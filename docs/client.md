# NBAClient Reference

`NBAClient` is the async context manager you use for every NBA Stats API request. It manages an `aiohttp` session, response caching, automatic retries with exponential backoff, rate-limit header handling, and optional signal-based graceful shutdown.

## Overview

Every request flows through `NBAClient`. You construct an `Endpoint` instance describing what you want, pass it to `client.get()` or `client.get_many()`, and receive a fully-validated Pydantic model back.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints.scoreboard import ScoreboardV2

async def main() -> None:
    async with NBAClient() as client:
        scoreboard = await client.get(ScoreboardV2(game_date="02/27/2026"))
        for game in scoreboard.game_header:
            print(game.game_id, game.home_team_id, game.visitor_team_id)

asyncio.run(main())
```

Under the hood `NBAClient`:

- Creates and owns an `aiohttp.ClientSession` with browser-like headers required by the NBA Stats API.
- Lazily initializes the session on first request (thread-safe via `anyio.Lock`).
- Checks a `TTLCache` before hitting the network when caching is enabled.
- Retries transient failures (429, 5xx, timeouts, connection errors) with exponential backoff and jitter.
- Respects the `Retry-After` header from 429 responses.
- Validates every response against the endpoint's Pydantic model.
- Installs `SIGINT`/`SIGTERM` handlers for graceful shutdown (can be disabled).

---

## Constructor Reference

```python
NBAClient(
    session: ClientSession | None = None,
    timeout: ClientTimeout | None = None,
    max_retries: int = 3,
    retry_wait_min: float = 1.0,
    retry_wait_max: float = 10.0,
    request_delay: float = 0.0,
    cache_ttl: int = 0,
    cache_maxsize: int = 256,
    *,
    handle_signals: bool = True,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session` | `ClientSession \| None` | `None` | Bring your own `aiohttp` session. When provided the client will **not** close it on exit. Useful for connection reuse or testing. |
| `timeout` | `ClientTimeout \| None` | `None` | Request timeout configuration. Defaults to `ClientTimeout(total=60)` (60-second total timeout). |
| `max_retries` | `int` | `3` | Maximum number of retry attempts for transient failures. The first attempt counts; `max_retries=3` means up to 4 total attempts. |
| `retry_wait_min` | `float` | `1.0` | Minimum wait in seconds between retries (lower bound for exponential backoff). |
| `retry_wait_max` | `float` | `10.0` | Maximum wait in seconds between retries (upper bound for exponential backoff, also caps `Retry-After` values). |
| `request_delay` | `float` | `0.0` | Seconds to sleep before each request inside `get_many()`. Use for proactive rate limiting. Has no effect on `get()`. |
| `cache_ttl` | `int` | `0` | TTL in seconds for the response cache. `0` disables caching entirely. |
| `cache_maxsize` | `int` | `256` | Maximum number of responses to keep in the cache. Oldest entries are evicted when full. |
| `handle_signals` | `bool` | `True` | Register `SIGINT`/`SIGTERM` handlers for graceful shutdown. Set to `False` when the process already manages signal handling (e.g., FastAPI, aiohttp app server). |

---

## Usage Patterns

### Standard usage

The recommended pattern is the async context manager. The session is opened lazily and closed automatically on exit.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints.player_game_log import PlayerGameLog

async def main() -> None:
    async with NBAClient() as client:
        log = await client.get(PlayerGameLog(player_id=2544, season="2025-26"))
        for row in log.games:
            print(row.game_date, row.pts)

asyncio.run(main())
```

### Custom timeout

```python
from aiohttp import ClientTimeout
from fastbreak.clients import NBAClient

async def main() -> None:
    timeout = ClientTimeout(total=30, connect=5)
    async with NBAClient(timeout=timeout) as client:
        ...
```

### Bringing your own session

Pass an existing `ClientSession` when you want to manage connection pooling yourself. The client will not close a session it did not create.

```python
import aiohttp
from fastbreak.clients import NBAClient

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        async with NBAClient(session=session) as client:
            ...
```

### Manual lifecycle (no context manager)

Call `close()` explicitly when you cannot use `async with`. The `__del__` method emits a `ResourceWarning` if the client is garbage-collected without being closed.

```python
from fastbreak.clients import NBAClient

client = NBAClient(handle_signals=False)
try:
    result = await client.get(some_endpoint)
finally:
    await client.close()
```

### Web server embedding

Web servers (FastAPI, aiohttp, Starlette) manage their own signal handlers. Disable fastbreak's built-in handlers to avoid conflicts.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastbreak.clients import NBAClient

client: NBAClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = NBAClient(handle_signals=False)
    yield
    if client is not None:
        await client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/leaders")
async def leaders():
    from fastbreak.endpoints.league_leaders import LeagueLeaders
    assert client is not None
    result = await client.get(LeagueLeaders())
    return result.leaders
```

---

## `get()` — Fetch a Single Endpoint

```python
async def get(
    endpoint: Endpoint[T],
    *,
    request_id: str | None = None,
) -> T
```

Fetches one endpoint and returns the parsed, validated response model.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `endpoint` | `Endpoint[T]` | Any frozen Pydantic endpoint model. Defines the API path and query parameters. |
| `request_id` | `str \| None` | Optional correlation ID for log tracing. A UUID is generated automatically if not provided. |

**Returns** `T` — the endpoint's associated response model, fully validated.

**Behavior**

1. Checks the TTL cache. Returns the cached response immediately if found.
2. Acquires the session (creates it on first call).
3. Executes an HTTP GET with retry logic.
4. On a 429 response, reads the `Retry-After` header and uses it as the wait duration.
5. Validates the JSON body against the endpoint's Pydantic model.
6. Stores the result in the cache on success.

**Example**

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints.box_scores_v3 import BoxScoreTraditionalV3

async def fetch_box_score(game_id: str) -> None:
    async with NBAClient() as client:
        box = await client.get(BoxScoreTraditionalV3(game_id=game_id))
        for player in box.box_score_traditional.home_team.players:
            print(player.name_i, player.statistics.points)
```

**With request_id for distributed tracing**

```python
import uuid
from fastbreak.clients import NBAClient

async def fetch_with_trace(game_id: str, trace_id: str) -> None:
    async with NBAClient() as client:
        result = await client.get(
            BoxScoreTraditionalV3(game_id=game_id),
            request_id=trace_id,
        )
```

---

## `get_many()` — Fetch Multiple Endpoints Concurrently

```python
async def get_many(
    endpoints: Sequence[Endpoint[T]],
    *,
    max_concurrency: int | None = None,
) -> list[T]
```

Fetches multiple endpoints using `anyio` task groups. Results are returned in the same order as the input list, regardless of completion order.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `endpoints` | `Sequence[Endpoint[T]]` | — | The endpoints to fetch. May be empty (returns `[]`). |
| `max_concurrency` | `int \| None` | `3` | Maximum number of requests to run simultaneously. |

**Returns** `list[T]` — responses in the same order as `endpoints`.

**Raises**

- `TypeError` — if any element is not an `Endpoint` instance (checked before any requests are made).
- `ExceptionGroup` — if any request fails. All in-flight requests are cancelled immediately. The group contains the exceptions from every failed request.

**Behavior**

- Each request runs inside `get()`, so caching and retries apply to each individual request.
- When `request_delay > 0`, each task sleeps for that duration before issuing its HTTP request, spreading load over time.
- A batch correlation ID is generated and prepended to each request's `request_id` (`"<batch_id>:<index>"`), making individual requests traceable back to the batch in logs.
- Progress is logged at DEBUG level every ~10% of completion when `len(endpoints) >= 10`.

**Examples**

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints.box_scores_v3 import BoxScoreTraditionalV3

async def fetch_multiple_box_scores(game_ids: list[str]) -> None:
    endpoints = [BoxScoreTraditionalV3(game_id=gid) for gid in game_ids]

    async with NBAClient(request_delay=0.5) as client:
        box_scores = await client.get_many(endpoints, max_concurrency=5)

    for gid, box in zip(game_ids, box_scores):
        print(gid, len(box.box_score_traditional.home_team.players), "players")
```

**Handling partial failures**

```python
from fastbreak.clients import NBAClient

async def safe_fetch_many(endpoints):
    async with NBAClient() as client:
        try:
            return await client.get_many(endpoints)
        except* Exception as eg:
            print(f"{len(eg.exceptions)} request(s) failed:")
            for exc in eg.exceptions:
                print(f"  {type(exc).__name__}: {exc}")
            raise
```

---

## Caching

Response caching is disabled by default. Enable it by setting `cache_ttl` to a positive integer.

### Enabling the cache

```python
async with NBAClient(cache_ttl=300, cache_maxsize=256) as client:
    # First call hits the API
    result1 = await client.get(some_endpoint)
    # Second call with identical params returns cached result instantly
    result2 = await client.get(some_endpoint)
    assert result1 == result2
```

### `cache_info` property

Returns a snapshot of cache statistics, or `None` if caching is disabled.

```python
info = client.cache_info
# With caching enabled:
# {'size': 12, 'maxsize': 256, 'ttl': 300}

# With caching disabled (cache_ttl=0):
# None
```

| Key | Type | Description |
|---|---|---|
| `size` | `int` | Current number of cached entries. |
| `maxsize` | `int` | Maximum number of entries the cache can hold. |
| `ttl` | `int` | Time-to-live per entry in seconds. |

### `clear_cache()` method

Immediately evicts all cached responses. Useful after mutations or when you know data has changed.

```python
client.clear_cache()
```

### Cache key generation

The cache key is a SHA-256 hash of `"{endpoint.path}:{json.dumps(endpoint.params(), sort_keys=True)}"`. Two `Endpoint` instances with the same class and the same params will always share a cache entry. The cache is type-safe — if a key were ever to collide across different response types, `CacheTypeMismatchError` is raised rather than returning a silently wrong model.

---

## Retry Behavior

Retries are powered by [tenacity](https://tenacity.readthedocs.io/) and run per request (not shared across concurrent `get_many()` calls).

### What triggers a retry

| Condition | Retried |
|---|---|
| HTTP 429 Too Many Requests | Yes |
| HTTP 5xx Server Error | Yes |
| `aiohttp` connection errors (`OSError`) | Yes |
| `TimeoutError` | Yes |
| HTTP 4xx (other than 429) | No |
| `pydantic.ValidationError` | No |

### Backoff strategy

Between retries, fastbreak waits using **exponential backoff with jitter** bounded by `retry_wait_min` and `retry_wait_max`. When a 429 response includes a `Retry-After: <seconds>` header, that value is used instead (capped at `retry_wait_max`).

```
attempt 1 → fail → wait ~1–2s
attempt 2 → fail → wait ~2–5s
attempt 3 → fail → wait up to 10s
attempt 4 → reraise
```

### Configuration example

```python
async with NBAClient(
    max_retries=5,
    retry_wait_min=2.0,
    retry_wait_max=30.0,
) as client:
    ...
```

### Disabling retries

Set `max_retries=0` to make every request a single attempt with no retry.

```python
async with NBAClient(max_retries=0) as client:
    ...
```

---

## Error Handling

### `aiohttp.ClientResponseError`

Raised for non-retryable HTTP errors (4xx except 429) or after all retry attempts are exhausted. Contains `status`, `message`, and `request_info`.

```python
import aiohttp
from fastbreak.clients import NBAClient

async def main() -> None:
    async with NBAClient() as client:
        try:
            result = await client.get(some_endpoint)
        except aiohttp.ClientResponseError as e:
            print(f"HTTP {e.status}: {e.message}")
            print(f"URL: {e.request_info.url}")
```

### `pydantic.ValidationError`

Raised when the API response does not match the expected schema. This usually means the NBA Stats API changed its response format.

```python
from pydantic import ValidationError
from fastbreak.clients import NBAClient

async def main() -> None:
    async with NBAClient() as client:
        try:
            result = await client.get(some_endpoint)
        except ValidationError as e:
            print(f"Schema mismatch — {e.error_count()} error(s):")
            for err in e.errors():
                print(f"  {err['loc']}: {err['msg']}")
```

### `ExceptionGroup` (from `get_many()`)

Python 3.11+ exception groups are used when any request in a `get_many()` batch fails. Use `except*` to handle them.

```python
from fastbreak.clients import NBAClient
import aiohttp

async def main() -> None:
    async with NBAClient() as client:
        try:
            results = await client.get_many(endpoints)
        except* aiohttp.ClientResponseError as eg:
            for exc in eg.exceptions:
                print(f"HTTP {exc.status} for one of the batch requests")
        except* Exception as eg:
            for exc in eg.exceptions:
                print(f"Unexpected: {type(exc).__name__}: {exc}")
```

### `TypeError` (from `get_many()`)

Raised synchronously before any network requests are made if any element in the input sequence is not an `Endpoint` instance.

```python
try:
    await client.get_many(["not_an_endpoint"])
except TypeError as e:
    print(e)  # Item at index 0 is not an Endpoint instance: str
```

### `CacheTypeMismatchError`

An internal error that indicates a bug in cache key generation (a collision between two different endpoint types producing the same key). This should never occur in normal use. If you see it, please file a bug.

---

## Rate Limiting

The NBA Stats API enforces rate limits. fastbreak provides two complementary mechanisms.

### Reactive: `Retry-After` header

When the server returns `HTTP 429` with a `Retry-After: <seconds>` header, fastbreak automatically waits exactly that many seconds (capped at `retry_wait_max`) before retrying. No configuration needed.

### Proactive: `request_delay`

Set `request_delay` to introduce a fixed sleep before each request in a `get_many()` batch. This prevents bursting and reduces the chance of triggering rate limits in the first place.

```python
# ~60 requests per minute maximum
async with NBAClient(request_delay=1.0) as client:
    results = await client.get_many(endpoints)

# ~100 requests per minute maximum
async with NBAClient(request_delay=0.6) as client:
    results = await client.get_many(endpoints)
```

`request_delay` only applies to `get_many()`. Direct `get()` calls are not throttled.

### Combining both

For large batches where you want both proactive throttling and safe recovery from occasional 429s:

```python
async with NBAClient(
    request_delay=0.5,      # ~120 req/min proactively
    max_retries=5,          # retry up to 5 times
    retry_wait_max=60.0,    # honour long Retry-After values
) as client:
    results = await client.get_many(large_endpoint_list)
```

---

## Signal Handling

By default, `NBAClient` registers handlers for `SIGINT` (Ctrl-C) and `SIGTERM` when used as an async context manager. When a signal is received:

1. Signal handlers are removed immediately (prevents re-entrancy on double Ctrl-C).
2. The aiohttp session is closed cleanly.
3. All pending asyncio tasks are cancelled.

This ensures open connections are flushed and resources are freed before the process exits.

### Disabling signal handling

Signal handling must be disabled when the host framework already installs its own handlers (FastAPI, aiohttp app server, Celery, Gunicorn, etc.). Registering multiple handlers for the same signal leads to unpredictable behavior.

```python
# FastAPI — lifespan controls startup/shutdown
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastbreak.clients import NBAClient

_client: NBAClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _client
    _client = NBAClient(handle_signals=False)
    yield
    if _client:
        await _client.close()

app = FastAPI(lifespan=lifespan)
```

```python
# aiohttp web app
from aiohttp import web
from fastbreak.clients import NBAClient

async def on_startup(app: web.Application) -> None:
    app["nba"] = NBAClient(handle_signals=False)

async def on_cleanup(app: web.Application) -> None:
    await app["nba"].close()

app = web.Application()
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)
```

### Platform notes

Signal handler installation may silently fail on Windows and when the event loop runs inside a non-main thread. fastbreak logs these failures at DEBUG level and continues without signal handling rather than raising an exception.

---

## Bringing Your Own Session

Pass an `aiohttp.ClientSession` you created yourself. fastbreak will use it for all requests but will **not** close it when the client exits — you remain responsible for the session lifecycle.

```python
import aiohttp
from fastbreak.clients import NBAClient

async def main() -> None:
    connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Both clients share the same connection pool
        async with NBAClient(session=session, handle_signals=False) as client:
            result = await client.get(some_endpoint)
```

**Common use case: testing with `aiohttp.test_utils`**

```python
from aiohttp.test_utils import TestClient, TestServer
from fastbreak.clients import NBAClient

async def test_with_mock_server(aiohttp_client, app) -> None:
    test_client = await aiohttp_client(app)
    nba = NBAClient(session=test_client.session, handle_signals=False)
    try:
        result = await nba.get(some_endpoint)
        assert result is not None
    finally:
        await nba.close()
```

---

## Logging

`NBAClient` emits structured log events via [structlog](https://www.structlog.org/). All events include a `request_id` (or `batch_id` for `get_many()`) for correlation.

| Event | Level | When |
|---|---|---|
| `request_attempt` | DEBUG | Before each HTTP request (includes attempt number) |
| `cache_hit` | DEBUG | When a cached response is returned |
| `request_success` | DEBUG | After a successful response is parsed |
| `rate_limited` | DEBUG | When a 429 response is received |
| `validation_failed` | WARNING | When Pydantic validation fails |
| `batch_start` | DEBUG | At the start of a `get_many()` call |
| `batch_progress` | DEBUG | Every ~10% through a large batch |
| `batch_complete` | DEBUG | When all batch requests finish |
| `session_close_timeout` | WARNING | If the session takes too long to close |

Control log verbosity via the `FASTBREAK_LOG_LEVEL` environment variable:

```bash
FASTBREAK_LOG_LEVEL=DEBUG python my_script.py
FASTBREAK_LOG_FORMAT=json python my_script.py   # structured JSON output
```

---

## Complete Example

The following example demonstrates caching, concurrency, error handling, and rate limiting together.

```python
import asyncio
import aiohttp
from pydantic import ValidationError

from fastbreak.clients import NBAClient
from fastbreak.endpoints.box_scores_v3 import BoxScoreTraditionalV3
from fastbreak.games import get_game_ids


async def main() -> None:
    game_ids: list[str] = []

    async with NBAClient(
        cache_ttl=600,       # cache responses for 10 minutes
        cache_maxsize=512,
        request_delay=0.5,   # ~120 req/min in batches
        max_retries=4,
        retry_wait_min=1.0,
        retry_wait_max=30.0,
    ) as client:

        # Fetch all regular-season game IDs for one team this season
        game_ids = await get_game_ids(client, "2025-26", team_id=1610612747)
        # Filter to regular season only (game IDs starting with "002")
        regular_season = [gid for gid in game_ids if gid[:3] == "002"]

        print(f"Fetching {len(regular_season)} box scores...")
        print(f"Cache before: {client.cache_info}")

        endpoints = [BoxScoreTraditionalV3(game_id=gid) for gid in regular_season]

        try:
            box_scores = await client.get_many(endpoints, max_concurrency=5)
        except* aiohttp.ClientResponseError as eg:
            print(f"{len(eg.exceptions)} HTTP error(s) — aborting")
            return
        except* ValidationError as eg:
            print(f"{len(eg.exceptions)} schema error(s) — check for API changes")
            return

        print(f"Cache after: {client.cache_info}")

        for gid, box in zip(regular_season, box_scores):
            top_scorer = max(box.box_score_traditional.home_team.players, key=lambda p: p.statistics.points or 0, default=None)
            if top_scorer:
                print(f"{gid}: {top_scorer.name_i} — {top_scorer.statistics.points} pts")

        # Invalidate cache before the next run if needed
        client.clear_cache()


asyncio.run(main())
```
