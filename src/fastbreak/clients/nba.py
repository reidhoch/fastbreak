"""NBA client — async client configured for the NBA (league ID ``"00"``)."""

from typing import ClassVar

from fastbreak.clients.base import (
    BATCH_PROGRESS_THRESHOLD,
    DEFAULT_CACHE_MAXSIZE,
    HTTP_SERVER_ERROR_MIN,
    HTTP_TOO_MANY_REQUESTS,
    SESSION_CLOSE_TIMEOUT,
    BaseClient,
    CacheTypeMismatchError,
    _is_retryable_error,
    _make_wait_with_retry_after,
    _RetryAfterState,
    _TypedResponseCache,
)
from fastbreak.league import League

# Re-export base internals for backward compatibility — tests and external
# code may import these from ``fastbreak.clients.nba``.
__all__ = [
    "BATCH_PROGRESS_THRESHOLD",
    "DEFAULT_CACHE_MAXSIZE",
    "HTTP_SERVER_ERROR_MIN",
    "HTTP_TOO_MANY_REQUESTS",
    "SESSION_CLOSE_TIMEOUT",
    "CacheTypeMismatchError",
    "NBAClient",
    "_RetryAfterState",
    "_TypedResponseCache",
    "_is_retryable_error",
    "_make_wait_with_retry_after",
]


class NBAClient(BaseClient):
    """Async client for the NBA Stats API."""

    league: ClassVar[League] = League.NBA
