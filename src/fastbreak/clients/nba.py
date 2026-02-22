import asyncio
import hashlib
import json
import ssl
import uuid
import warnings
from collections.abc import Callable, Sequence
from types import TracebackType
from typing import TYPE_CHECKING, ClassVar, Self, cast

import anyio
import certifi
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, TCPConnector
from anyio import CapacityLimiter, Lock
from cachetools import TTLCache
from pydantic import BaseModel, ValidationError
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from fastbreak import __version__
from fastbreak.endpoints.base import Endpoint
from fastbreak.logging import logger

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from structlog import BoundLogger

    from fastbreak.models import JSON

HTTP_TOO_MANY_REQUESTS = 429
HTTP_SERVER_ERROR_MIN = 500
BATCH_PROGRESS_THRESHOLD = 10
DEFAULT_CACHE_MAXSIZE = 256
SESSION_CLOSE_TIMEOUT = 5.0


class CacheTypeMismatchError(Exception):
    """Raised when a cached response has an unexpected type.

    This indicates a cache key collision or bug in the caching logic.
    """

    def __init__(self, key: str, expected: str, actual: str) -> None:
        self.key = key
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Cache type mismatch for key '{key[:16]}...': "
            f"expected {expected}, got {actual}"
        )


class _TypedResponseCache:
    """Type-safe wrapper around TTLCache for endpoint responses.

    This wrapper encapsulates the type relationship between cache keys
    (derived from endpoints) and their stored response types, providing
    type-safe get/set operations without requiring cast() at call sites.

    Stores response type alongside value to enable reliable type checking,
    since isinstance() alone cannot distinguish between Pydantic model types.
    """

    def __init__(self, maxsize: int, ttl: int) -> None:
        self._cache: TTLCache[str, tuple[type[BaseModel], BaseModel]] = TTLCache(
            maxsize=maxsize, ttl=ttl
        )

    def get[T: BaseModel](self, key: str, response_type: type[T]) -> T | None:
        """Retrieve a cached response with proper type narrowing.

        Args:
            key: The cache key (generated from endpoint path and params)
            response_type: The expected response model type for validation

        Returns:
            The cached response cast to T, or None if not found

        Raises:
            CacheTypeMismatchError: If cached value has wrong type (indicates bug)

        """
        cached = self._cache.get(key)
        if cached is None:
            return None
        cached_type, value = cached
        if cached_type is response_type:
            return cast("T", value)
        # Type mismatch indicates a bug - raise instead of silently returning None
        logger.error(
            "cache_type_mismatch_bug",
            key=key[:16] + "...",
            expected=response_type.__name__,
            actual=cached_type.__name__,
            hint="This indicates a cache key collision or bug",
        )
        raise CacheTypeMismatchError(key, response_type.__name__, cached_type.__name__)

    def set[T: BaseModel](self, key: str, value: T) -> None:
        """Store a response in the cache with its type."""
        self._cache[key] = (type(value), value)

    def __contains__(self, key: str) -> bool:
        return key in self._cache

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)

    @property
    def maxsize(self) -> float:
        """Return the maximum cache size."""
        return self._cache.maxsize

    @property
    def ttl(self) -> float:
        """Return the cache TTL in seconds."""
        return self._cache.ttl


def _is_retryable_error(exc: BaseException) -> bool:
    """Check if an exception should trigger a retry."""
    if isinstance(exc, ClientResponseError):
        return (
            exc.status == HTTP_TOO_MANY_REQUESTS or exc.status >= HTTP_SERVER_ERROR_MIN
        )
    return isinstance(exc, (TimeoutError, OSError))


class _RetryAfterState:
    """State container to track Retry-After header values between request and retry."""

    def __init__(self) -> None:
        self.retry_after: float | None = None

    def set_retry_after(self, value: float | None) -> None:
        """Store the Retry-After value from a 429 response."""
        self.retry_after = value

    def get_and_clear(self) -> float | None:
        """Get and clear the stored Retry-After value."""
        value = self.retry_after
        self.retry_after = None
        return value


def _make_wait_with_retry_after(
    retry_after_state: _RetryAfterState,
    initial: float,
    max_wait: float,
) -> Callable[[RetryCallState], float]:
    """Create a wait strategy that respects Retry-After headers.

    Falls back to exponential backoff with jitter if no Retry-After is present.
    """
    base_wait = wait_exponential_jitter(initial=initial, max=max_wait)

    def wait_func(retry_state: RetryCallState) -> float:
        retry_after = retry_after_state.get_and_clear()
        if retry_after is not None:
            # Respect the server's Retry-After, but cap it at max_wait
            return min(retry_after, max_wait)
        # Fall back to exponential backoff with jitter
        return base_wait(retry_state)

    return wait_func


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
        "User-Agent": f"Fastbreak/{__version__} (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
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
        cache_ttl: int = 0,
        cache_maxsize: int = DEFAULT_CACHE_MAXSIZE,
    ) -> None:
        """Initialize the NBA API client.

        Args:
            session: Optional aiohttp ClientSession to use (for connection reuse)
            timeout: Request timeout configuration (default: 60s total)
            max_retries: Maximum retry attempts for transient failures (default: 3)
            retry_wait_min: Minimum wait time between retries in seconds (default: 1.0)
            retry_wait_max: Maximum wait time between retries in seconds (default: 10.0)
            request_delay: Delay between requests in get_many() for rate limiting
            cache_ttl: TTL in seconds for response caching (0 = disabled, default)
            cache_maxsize: Maximum number of cached responses (default: 256)

        """
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout or ClientTimeout(total=60)
        self._session_lock = Lock()
        self._request_delay = request_delay

        # Retry configuration (stored for per-request retry instances)
        self._max_retries = max_retries
        self._retry_wait_min = retry_wait_min
        self._retry_wait_max = retry_wait_max

        # Response caching
        self._cache: _TypedResponseCache | None = None
        if cache_ttl > 0:
            self._cache = _TypedResponseCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self._cache_lock = Lock()

    def _make_cache_key[T: BaseModel](self, endpoint: Endpoint[T]) -> str:
        """Generate a cache key from endpoint path and parameters."""
        params_json = json.dumps(endpoint.params(), sort_keys=True)
        key_data = f"{endpoint.path}:{params_json}"
        return hashlib.sha256(key_data.encode()).hexdigest()

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
        """Close the client session if we own it.

        Uses a timeout to prevent hanging on stuck connections.
        """
        async with self._session_lock:
            if self._owns_session and self._session is not None:
                try:
                    await asyncio.wait_for(
                        self._session.close(), timeout=SESSION_CLOSE_TIMEOUT
                    )
                except TimeoutError:
                    logger.warning(
                        "session_close_timeout",
                        timeout=SESSION_CLOSE_TIMEOUT,
                        hint="Session close timed out, forcing cleanup",
                    )
                finally:
                    self._session = None

    def __del__(self) -> None:
        """Warn if client was not properly closed."""
        if self._owns_session and self._session is not None:
            warnings.warn(
                "NBAClient was not properly closed. Use 'async with NBAClient() as client:'",
                ResourceWarning,
                stacklevel=2,
            )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    def _parse_retry_after(self, value: str | None) -> float | None:
        """Parse Retry-After header value to seconds.

        Supports both delta-seconds (e.g., "120") and HTTP-date formats.
        Returns None if parsing fails.
        """
        if not value:
            return None
        try:
            # Try parsing as integer seconds first (most common)
            return float(value)
        except ValueError:
            logger.debug(
                "retry_after_parse_failed",
                raw_value=value,
                hint="Falling back to exponential backoff",
            )
            return None

    async def _check_cache[T: BaseModel](
        self, endpoint: Endpoint[T], request_id: str
    ) -> tuple[str | None, T | None]:
        """Check cache for a cached response.

        Returns:
            Tuple of (cache_key, cached_response). cache_key is None if caching
            is disabled. cached_response is None if not found in cache.

        """
        if self._cache is None:
            return None, None

        cache_key = self._make_cache_key(endpoint)
        async with self._cache_lock:
            cached = self._cache.get(cache_key, endpoint.response_model)
            if cached is not None:
                await logger.bind(request_id=request_id, endpoint=endpoint.path).adebug(
                    "cache_hit"
                )
            return cache_key, cached

    async def _store_in_cache[T: BaseModel](
        self, cache_key: str | None, result: T
    ) -> None:
        """Store a response in the cache if caching is enabled."""
        if self._cache is not None and cache_key is not None:
            async with self._cache_lock:
                self._cache.set(cache_key, result)

    async def get[T: BaseModel](
        self, endpoint: Endpoint[T], *, request_id: str | None = None
    ) -> T:
        """Fetch data from an endpoint and return the parsed response.

        Args:
            endpoint: An Endpoint instance defining the request
            request_id: Optional correlation ID for distributed tracing

        Returns:
            The parsed response model

        """
        req_id = request_id or str(uuid.uuid4())

        cache_key, cached = await self._check_cache(endpoint, req_id)
        if cached is not None:
            return cached

        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint.path}"
        log = logger.bind(request_id=req_id, endpoint=endpoint.path)

        # Create per-request retry state to avoid race conditions
        retry_after_state = _RetryAfterState()
        retry = AsyncRetrying(
            stop=stop_after_attempt(self._max_retries + 1),
            wait=_make_wait_with_retry_after(
                retry_after_state, self._retry_wait_min, self._retry_wait_max
            ),
            retry=retry_if_exception(_is_retryable_error),
            reraise=True,
        )

        async for attempt in retry:
            with attempt:
                attempt_num = attempt.retry_state.attempt_number
                await log.adebug(
                    "request_attempt",
                    attempt=attempt_num,
                    url=url,
                    params=endpoint.params(),
                )

                async with session.get(url, params=endpoint.params()) as resp:
                    await self._handle_rate_limit(
                        resp, log, attempt_num, retry_after_state
                    )
                    resp.raise_for_status()
                    data = await resp.json()

                    result = await self._parse_and_validate(endpoint, data, log)
                    await log.adebug("request_success", attempt=attempt_num)
                    await self._store_in_cache(cache_key, result)
                    return result

        # Unreachable due to reraise=True, but satisfies the type checker
        msg = "Retry loop exited unexpectedly"
        raise RuntimeError(msg)

    async def _handle_rate_limit(
        self,
        resp: "ClientResponse",
        log: "BoundLogger",
        attempt_num: int,
        retry_after_state: _RetryAfterState,
    ) -> None:
        """Handle rate limit response by storing Retry-After for the wait strategy."""
        if resp.status != HTTP_TOO_MANY_REQUESTS:
            return

        retry_after_raw = resp.headers.get("Retry-After")
        retry_after = self._parse_retry_after(retry_after_raw)
        retry_after_state.set_retry_after(retry_after)
        await log.adebug(
            "rate_limited",
            status=resp.status,
            retry_after=retry_after,
            retry_after_raw=retry_after_raw,
            attempt=attempt_num,
        )

    async def _parse_and_validate[T: BaseModel](
        self,
        endpoint: Endpoint[T],
        data: "JSON",
        log: "BoundLogger",
    ) -> T:
        """Parse and validate the API response."""
        try:
            return endpoint.parse_response(data)
        except ValidationError as e:
            await log.awarning(
                "validation_failed",
                error=str(e),
                endpoint=endpoint.path,
                response_keys=list(data.keys()) if isinstance(data, dict) else None,
            )
            raise

    async def get_many[T: BaseModel](
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
            TypeError: If any item in endpoints is not an Endpoint instance.
            ExceptionGroup: If any request fails, contains all exceptions.

        Example:
            endpoints = [BoxScoreTraditional(gid) for gid in game_ids]
            results = await client.get_many(endpoints)

        """
        if not endpoints:
            return []

        # Validate all items are Endpoint instances
        for i, ep in enumerate(endpoints):
            if not isinstance(ep, Endpoint):
                msg = f"Item at index {i} is not an Endpoint instance: {type(ep).__name__}"
                raise TypeError(msg)

        # Generate batch correlation ID
        batch_id = str(uuid.uuid4())

        total = len(endpoints)
        concurrency = max_concurrency or 3
        limiter = CapacityLimiter(concurrency)
        results: dict[int, T] = {}
        completed = 0

        log = logger.bind(batch_id=batch_id, total=total, concurrency=concurrency)
        await log.adebug("batch_start")

        async def _fetch_with_limiter(index: int, endpoint: Endpoint[T]) -> None:
            nonlocal completed
            async with limiter:
                if self._request_delay > 0:
                    await anyio.sleep(self._request_delay)
                # Use batch_id as prefix for individual request IDs
                request_id = f"{batch_id}:{index}"
                results[index] = await self.get(endpoint, request_id=request_id)
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
        return [results[i] for i in range(total)]

    def clear_cache(self) -> None:
        """Clear the response cache."""
        if self._cache is not None:
            self._cache.clear()

    @property
    def cache_info(self) -> dict[str, int] | None:
        """Return cache statistics, or None if caching is disabled.

        Returns:
            Dictionary with 'size', 'maxsize', and 'ttl' keys, or None.

        """
        if self._cache is None:
            return None
        return {
            "size": len(self._cache),
            "maxsize": int(self._cache.maxsize),
            "ttl": int(self._cache.ttl),
        }
