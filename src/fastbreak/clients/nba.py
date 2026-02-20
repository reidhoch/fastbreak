import ssl
from collections.abc import Sequence
from types import TracebackType
from typing import ClassVar, Self, TypeVar

import anyio
import certifi
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, TCPConnector
from anyio import CapacityLimiter, Lock
from pydantic import BaseModel, ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from fastbreak.endpoints.base import Endpoint
from fastbreak.logging import logger

T = TypeVar("T", bound=BaseModel)

HTTP_TOO_MANY_REQUESTS = 429
HTTP_SERVER_ERROR_MIN = 500
BATCH_PROGRESS_THRESHOLD = 10


def _is_retryable_error(exc: BaseException) -> bool:
    """Check if an exception should trigger a retry."""
    if isinstance(exc, ClientResponseError):
        return (
            exc.status == HTTP_TOO_MANY_REQUESTS or exc.status >= HTTP_SERVER_ERROR_MIN
        )
    return isinstance(exc, (TimeoutError, OSError))


class NBAClient:
    """Async client for the NBA Stats API."""

    BASE_URL = "https://stats.nba.com/stats"

    DEFAULT_HEADERS: ClassVar[dict[str, str]] = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "DNT": "1",
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    def __init__(  # noqa: PLR0913
        self,
        session: ClientSession | None = None,
        timeout: ClientTimeout | None = None,
        max_retries: int = 3,
        retry_wait_min: float = 1.0,
        retry_wait_max: float = 10.0,
        request_delay: float = 0.0,
    ) -> None:
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout or ClientTimeout(total=60)
        self._session_lock = Lock()
        self._request_delay = request_delay
        self._retry = AsyncRetrying(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_exponential_jitter(initial=retry_wait_min, max=retry_wait_max),
            retry=retry_if_exception(_is_retryable_error),
            reraise=True,
        )

    async def _get_session(self) -> ClientSession:
        async with self._session_lock:
            if self._session is None:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = TCPConnector(
                    limit_per_host=10,
                    ssl=ssl_context,
                    ttl_dns_cache=300,
                )
                self._session = ClientSession(
                    connector=connector,
                    headers=self.DEFAULT_HEADERS,
                    timeout=self._timeout,
                )
        return self._session

    async def close(self) -> None:
        """Close the client session if we own it."""
        async with self._session_lock:
            if self._owns_session and self._session is not None:
                await self._session.close()
                self._session = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def get(self, endpoint: Endpoint[T]) -> T:
        """Fetch data from an endpoint and return the parsed response.

        Args:
            endpoint: An Endpoint instance defining the request

        Returns:
            The parsed response model

        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint.path}"
        log = logger.bind(endpoint=endpoint.path)

        async for attempt in self._retry:
            with attempt:
                attempt_num = attempt.retry_state.attempt_number
                await log.adebug(
                    "request_attempt",
                    attempt=attempt_num,
                    url=url,
                    params=endpoint.params(),
                )

                async with session.get(url, params=endpoint.params()) as resp:
                    if resp.status == HTTP_TOO_MANY_REQUESTS:
                        retry_after = resp.headers.get("Retry-After")
                        await log.adebug(
                            "rate_limited",
                            status=resp.status,
                            retry_after=retry_after,
                            attempt=attempt_num,
                        )
                    resp.raise_for_status()
                    data = await resp.json()

                    try:
                        result = endpoint.parse_response(data)
                    except ValidationError as e:
                        await log.awarning(
                            "validation_failed",
                            error=str(e),
                            endpoint=endpoint.path,
                            response_keys=list(data.keys())
                            if isinstance(data, dict)
                            else None,
                        )
                        raise
                    else:
                        await log.adebug("request_success", attempt=attempt_num)
                        return result

        # This line is unreachable due to reraise=True, but satisfies the type checker
        msg = "Retry loop exited unexpectedly"
        raise RuntimeError(msg)

    async def get_many(
        self,
        endpoints: Sequence[Endpoint[T]],
        *,
        max_concurrency: int | None = None,
    ) -> list[T]:
        """Fetch data from multiple endpoints concurrently.

        Uses anyio task groups for structured concurrency. If any request fails,
        all other requests are cancelled and an ExceptionGroup is raised.

        Args:
            endpoints: A sequence of Endpoint instances to fetch
            max_concurrency: Maximum concurrent requests (defaults to 3)

        Returns:
            A list of parsed responses in the same order as the input endpoints.

        Raises:
            ExceptionGroup: If any request fails, contains all exceptions.

        Example:
            endpoints = [BoxScoreTraditional(gid) for gid in game_ids]
            results = await client.get_many(endpoints)

        """
        if not endpoints:
            return []

        total = len(endpoints)
        concurrency = max_concurrency or 3
        limiter = CapacityLimiter(concurrency)
        results: list[T] = [None] * total  # type: ignore[list-item]
        completed = 0

        log = logger.bind(total=total, concurrency=concurrency)
        await log.adebug("batch_start")

        async def _fetch_with_limiter(index: int, endpoint: Endpoint[T]) -> None:
            nonlocal completed
            async with limiter:
                if self._request_delay > 0:
                    await anyio.sleep(self._request_delay)
                results[index] = await self.get(endpoint)
                completed += 1
                if (
                    total >= BATCH_PROGRESS_THRESHOLD
                    and completed % max(1, total // BATCH_PROGRESS_THRESHOLD) == 0
                ):
                    await log.adebug("batch_progress", completed=completed, total=total)

        async with anyio.create_task_group() as tg:
            for i, endpoint in enumerate(endpoints):
                tg.start_soon(_fetch_with_limiter, i, endpoint)

        await log.adebug("batch_complete", total=total)
        return results
