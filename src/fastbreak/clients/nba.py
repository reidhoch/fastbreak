import asyncio
from asyncio import Lock, Semaphore
from collections.abc import Sequence
from types import TracebackType
from typing import ClassVar, Self, TypeVar

from aiohttp import ClientResponseError, ClientSession, ClientTimeout, TCPConnector
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from fastbreak.endpoints.base import Endpoint

T = TypeVar("T", bound=BaseModel)

HTTP_TOO_MANY_REQUESTS = 429
HTTP_SERVER_ERROR_MIN = 500


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
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Firefox";v="114"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Fetch-Dest": "empty",
    }

    def __init__(
        self,
        session: ClientSession | None = None,
        timeout: ClientTimeout | None = None,
        max_retries: int = 3,
        retry_wait_min: float = 1.0,
        retry_wait_max: float = 10.0,
    ) -> None:
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout or ClientTimeout(total=30)
        self._session_lock = Lock()
        self._retry = AsyncRetrying(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_exponential_jitter(initial=retry_wait_min, max=retry_wait_max),
            retry=retry_if_exception(_is_retryable_error),
            reraise=True,
        )

    async def _get_session(self) -> ClientSession:
        async with self._session_lock:
            if self._session is None:
                connector = TCPConnector(
                    limit_per_host=10,
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

        async for attempt in self._retry:
            with attempt:
                async with session.get(url, params=endpoint.params()) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return endpoint.parse_response(data)

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

        Uses asyncio.TaskGroup for structured concurrency. If any request fails,
        all other requests are cancelled and an ExceptionGroup is raised.

        Args:
            endpoints: A sequence of Endpoint instances to fetch
            max_concurrency: Maximum concurrent requests (defaults to 10)

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

        concurrency = max_concurrency or 10
        semaphore = Semaphore(concurrency)
        results: list[T] = [None] * len(endpoints)  # type: ignore[list-item]

        async def _fetch_with_semaphore(index: int, endpoint: Endpoint[T]) -> None:
            async with semaphore:
                results[index] = await self.get(endpoint)

        async with asyncio.TaskGroup() as tg:
            for i, endpoint in enumerate(endpoints):
                tg.create_task(_fetch_with_semaphore(i, endpoint))

        return results
