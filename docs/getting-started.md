# Getting Started with fastbreak

fastbreak is an async Python client for the NBA Stats API. It gives you typed access to 100+ endpoints — standings, box scores, player stats, play-by-play, shot charts, and more — with automatic retries, optional response caching, and DataFrame export for every response model.

This guide walks from installation to your first request, then covers the features you'll reach for most.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Understanding the Async Context Manager](#understanding-the-async-context-manager)
5. [Your First Real Request](#your-first-real-request)
6. [Batch Requests with get_many()](#batch-requests-with-get_many)
7. [DataFrame Conversion](#dataframe-conversion)
8. [Caching](#caching)
9. [Retries](#retries)
10. [Logging](#logging)
11. [What's Next](#whats-next)

---

## Overview

Built on aiohttp with asyncio (trio is not supported). All responses are validated, frozen Pydantic models with mypy strict typing throughout.

- Async I/O via aiohttp — asyncio only
- Every response field is typed; mypy strict mode
- `to_pandas()` and `to_polars()` on any response list
- Automatic retries on HTTP 429 and 5xx, respects `Retry-After` headers
- Optional TTL caching with configurable size
- `get_many()` for concurrent batch requests, results in input order
- Structured logging via structlog, controlled by environment variables

---

## Installation

Install from PyPI:

```bash
pip install fastbreak
```

fastbreak requires Python 3.12 or later.

**Optional DataFrame dependencies:**

```bash
pip install fastbreak pandas       # pandas support
pip install fastbreak polars       # polars support
pip install fastbreak pandas polars  # both
```

DataFrame methods (`to_pandas()`, `to_polars()`) raise `ImportError` at call time if the corresponding library is not installed — you only need to install what you use.

---

## Quick Start

Here is the minimal working example. It fetches the current league standings and prints the first five teams:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async def main():
    async with NBAClient() as client:
        standings = await client.get(LeagueStandings(season="2025-26"))

        for team in standings.standings[:5]:
            print(f"{team.team_name}: {team.wins}-{team.losses}")

asyncio.run(main())
```

That is the entire pattern: create the client inside `async with`, call `client.get()` with an endpoint instance, and access typed fields on the response.

---

## Understanding the Async Context Manager

### Why `async with NBAClient() as client:`

`NBAClient` manages an underlying `aiohttp.ClientSession`. The session holds an open TCP connection pool that must be explicitly closed when you are done — otherwise the event loop will warn about unclosed resources.

Using `async with` guarantees cleanup in all cases, including exceptions and keyboard interrupts:

```python
async with NBAClient() as client:
    # session is created lazily on first request
    result = await client.get(...)
# session is closed here, even if an exception was raised above
```

If you skip the context manager and just call `NBAClient()` directly, the client will emit a `ResourceWarning` when it is garbage collected:

```
ResourceWarning: NBAClient was not properly closed. Use 'async with NBAClient() as client:'
```

### Running from a script with `asyncio.run()`

All fastbreak calls are async, so they must run inside a coroutine. The standard pattern for scripts is to define a `main()` coroutine and call `asyncio.run(main())` at the bottom of the file:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async def main():
    async with NBAClient() as client:
        standings = await client.get(LeagueStandings(season="2025-26"))
        print(standings.standings[0].team_name)

asyncio.run(main())
```

`asyncio.run()` creates a new event loop, runs the coroutine to completion, and then closes the loop. It is the right entry point for standalone scripts.

### When embedding fastbreak in a web server

If your application (FastAPI, aiohttp server, etc.) manages its own event loop and signal handlers, pass `handle_signals=False` so fastbreak does not interfere:

```python
client = NBAClient(handle_signals=False)
```

You are then responsible for calling `await client.close()` when shutting down, or use it as an async context manager as normal.

---

## Your First Real Request

Here is a complete, annotated script that fetches LeBron James's career game log for the 2025-26 season and prints recent games:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_game_log

async def main():
    # NBAClient is the entry point for all API calls.
    # Use it as an async context manager to ensure the session is closed.
    async with NBAClient() as client:

        # get_player_game_log() is a convenience helper in fastbreak.players.
        # player_id=2544 is LeBron James. Season format is "YYYY-YY".
        log = await get_player_game_log(client, player_id=2544, season="2025-26")

        # log is a list of PlayerGameLogEntry objects — fully typed.
        print(f"Games fetched: {len(log)}")

        # Print the 5 most recent games
        for game in log[:5]:
            print(
                f"{game.game_date}  {game.matchup:<15}"
                f"  {game.pts} pts  {game.reb} reb  {game.ast} ast"
            )

asyncio.run(main())
```

**What happens under the hood:**

1. `async with NBAClient() as client:` enters the context manager. No HTTP connection is opened yet.
2. `get_player_game_log(client, ...)` builds a `PlayerGameLog` endpoint instance and calls `client.get()`.
3. `client.get()` opens an aiohttp session (lazily, on first call), sends the request to `stats.nba.com`, and parses the JSON response into a Pydantic model.
4. The response model is frozen (immutable), so all fields are read-only after construction.
5. Exiting the `async with` block closes the session.

### Accessing response fields

Response models use Python-style snake_case field names, regardless of how the NBA API names them. The mapping is handled by Pydantic field aliases. You access `game.pts`, not `game.PTS`.

```python
# All of these are typed str | int | float | None — no guessing
game.game_date    # "FEB 26, 2026"
game.matchup      # "LAL vs. MEM"
game.pts          # 28
game.reb          # 7
game.ast          # 10
game.fg_pct       # 0.537
game.wl           # "W"
```

### Calling endpoints directly

The helper functions in `fastbreak.players`, `fastbreak.teams`, and `fastbreak.games` cover common use cases. For any other endpoint, construct it directly and pass it to `client.get()`:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import PlayerCareerStats

async def main():
    async with NBAClient() as client:
        career = await client.get(
            PlayerCareerStats(player_id=2544, per_mode="PerGame")
        )

        for season in career.season_totals_regular_season[-5:]:
            print(
                f"{season.season_id}  {season.team_abbreviation}"
                f"  {season.gp} GP  {season.pts} / {season.reb} / {season.ast}"
            )

asyncio.run(main())
```

Endpoint constructors accept typed, snake_case parameters. Invalid values are caught at construction time by Pydantic validation, not at request time.

---

## Batch Requests with get_many()

`get_many()` fetches a list of endpoints concurrently and returns results in the same order as the input list. Use it when you need data from multiple endpoints and do not want to make requests sequentially.

### Basic usage

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import BoxScoreTraditional

async def main():
    game_ids = ["0022500571", "0022500572", "0022500573"]

    async with NBAClient() as client:
        results = await client.get_many(
            [BoxScoreTraditional(game_id=gid) for gid in game_ids],
            max_concurrency=5,
        )

    # results[0] corresponds to game_ids[0], results[1] to game_ids[1], etc.
    for game_id, box in zip(game_ids, results):
        home = box.boxScoreTraditional.homeTeam
        away = box.boxScoreTraditional.awayTeam
        print(f"{game_id}: {away.teamTricode} @ {home.teamTricode}")

asyncio.run(main())
```

### Order preservation

Results are always returned in the same order as the input endpoints, regardless of which requests finish first. If you pass `[endpoint_A, endpoint_B, endpoint_C]`, you get back `[result_A, result_B, result_C]`.

### Concurrency control

`max_concurrency` limits how many requests run at once (defaults to 3). Raise it for higher throughput, lower it to reduce the chance of rate limiting:

```python
# More conservative — avoids hammering the API
results = await client.get_many(endpoints, max_concurrency=2)

# More aggressive — fine for small batches
results = await client.get_many(endpoints, max_concurrency=10)
```

You can also add a delay between requests in a batch using `request_delay` on the client constructor. This is useful when fetching large batches where you want to stay well under any rate limit:

```python
async with NBAClient(request_delay=0.5) as client:
    results = await client.get_many(endpoints)
```

### Failure behavior

If any request in the batch fails, all in-flight requests are cancelled and an `ExceptionGroup` is raised. The group contains one exception per failed request. Either all results are returned, or none are:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import BoxScoreTraditional

async def main():
    game_ids = ["0022500571", "0022500572", "invalid-id"]

    async with NBAClient() as client:
        try:
            results = await client.get_many(
                [BoxScoreTraditional(game_id=gid) for gid in game_ids]
            )
        except* Exception as eg:
            # eg.exceptions is a list of the individual failures
            for exc in eg.exceptions:
                print(f"Request failed: {exc}")

asyncio.run(main())
```

The `except*` syntax (Python 3.11+) handles `ExceptionGroup`. Each exception in the group corresponds to one failed request.

---

## DataFrame Conversion

Many response models include `PandasMixin` and `PolarsMixin`. Call the class method `to_pandas()` or `to_polars()` with a list of model instances to get a DataFrame with one row per item.

### pandas

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings
from fastbreak.models import TeamStanding

async def main():
    async with NBAClient() as client:
        standings = await client.get(LeagueStandings(season="2025-26"))

    # Pass the list of model instances to the class method
    df = TeamStanding.to_pandas(standings.standings)

    print(df[["team_name", "wins", "losses", "win_pct"]].head(10))

asyncio.run(main())
```

### polars

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings
from fastbreak.models import TeamStanding

async def main():
    async with NBAClient() as client:
        standings = await client.get(LeagueStandings(season="2025-26"))

    df = TeamStanding.to_polars(standings.standings)

    print(df.select(["team_name", "wins", "losses", "win_pct"]).head(10))

asyncio.run(main())
```

### Nested models and flattening

By default, nested model fields are flattened into dot-separated column names. For example, a player's `statistics.points` field becomes the column `statistics.points` in the DataFrame. Pass `flatten=False` to keep nested objects as dict columns, or change the separator with `sep`:

```python
# Flat columns: "statistics.points", "statistics.rebounds", ...
df = TraditionalPlayer.to_pandas(players, flatten=True, sep=".")

# Dict columns: df["statistics"] is a dict
df = TraditionalPlayer.to_pandas(players, flatten=False)
```

### Checking support

Not every model has DataFrame mixins — only those that represent list-like rows (standings entries, game log rows, player stat lines, etc.). If you call `to_pandas()` on a model that does not have `PandasMixin`, Python will raise `AttributeError`. Check the model's class hierarchy or the `models` documentation to confirm mixin support.

---

## Caching

By default, caching is disabled (`cache_ttl=0`). Enable it by setting `cache_ttl` to a positive integer (seconds). Responses are cached in memory by a hash of the endpoint path and parameters.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async def main():
    # Cache responses for 5 minutes, hold up to 256 entries
    async with NBAClient(cache_ttl=300, cache_maxsize=256) as client:

        # First call hits the API
        s1 = await client.get(LeagueStandings(season="2025-26"))

        # Second call returns the cached response instantly
        s2 = await client.get(LeagueStandings(season="2025-26"))

        # s1 and s2 are the same object
        assert s1 is s2

        # Inspect cache state
        print(client.cache_info)
        # {'size': 1, 'maxsize': 256, 'ttl': 300}

        # Manually invalidate all cached entries
        client.clear_cache()
        print(client.cache_info)
        # {'size': 0, 'maxsize': 256, 'ttl': 300}

asyncio.run(main())
```

### When to use caching

Caching is useful in scripts or notebooks where you iterate on analysis and re-run the same requests repeatedly. It is also useful in long-running processes (dashboards, web apps) where the same data is requested by multiple concurrent callers within a short window.

**`cache_info` returns `None` when caching is disabled:**

```python
async with NBAClient() as client:  # cache_ttl=0, caching disabled
    print(client.cache_info)  # None
```

### Cache key

The cache key is a SHA-256 hash of the endpoint's URL path and its query parameters. Two `LeagueStandings(season="2025-26")` instances will hit the same cache entry. A `LeagueStandings(season="2024-25")` instance will produce a different key.

---

## Retries

fastbreak automatically retries requests on transient failures:

- **HTTP 429** (Too Many Requests) — respects the `Retry-After` response header if present; otherwise falls back to exponential backoff
- **HTTP 5xx** (Server errors) — retries with exponential backoff and jitter
- **Timeouts and OS-level connection errors** — retried with the same strategy

### Default behavior

With the default constructor, fastbreak makes up to 3 retry attempts (4 total attempts including the first) with exponential backoff between 1 and 10 seconds:

```python
# These are the defaults — no need to specify them explicitly
async with NBAClient(
    max_retries=3,
    retry_wait_min=1.0,
    retry_wait_max=10.0,
) as client:
    result = await client.get(...)
```

### Configuring retries

Increase `max_retries` when running batch jobs that can tolerate retries, or decrease it for interactive use where you want fast failure:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async def main():
    # More retries, tighter backoff window — good for rate-limited batch jobs
    async with NBAClient(
        max_retries=5,
        retry_wait_min=2.0,
        retry_wait_max=30.0,
    ) as client:
        standings = await client.get(LeagueStandings(season="2025-26"))
        print(f"Fetched {len(standings.standings)} teams")

asyncio.run(main())
```

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async def main():
    # Fewer retries — fail fast during development
    async with NBAClient(max_retries=1) as client:
        standings = await client.get(LeagueStandings(season="2025-26"))
        print(standings.standings[0].team_name)

asyncio.run(main())
```

### Disabling retries

Set `max_retries=0` to disable retries entirely. Failures will raise immediately:

```python
async with NBAClient(max_retries=0) as client:
    result = await client.get(...)  # raises on first failure, no retries
```

### What is not retried

Validation errors (`pydantic.ValidationError`) and client errors other than 429 (e.g., HTTP 400, 404) are not retried. They indicate a problem with the request itself, not a transient server issue.

---

## Logging

fastbreak uses [structlog](https://www.structlog.org/) for structured logging. Log output is controlled by two environment variables. fastbreak configures structlog automatically at import time, but only if structlog has not already been configured by your application.

### FASTBREAK_LOG_LEVEL

Controls which messages are emitted. Default is `WARNING`.

| Value     | What you see                                   |
|-----------|------------------------------------------------|
| `DEBUG`   | Every request attempt, cache hits, retry waits |
| `INFO`    | Request completions, batch progress            |
| `WARNING` | Validation warnings, slow retries (default)    |
| `ERROR`   | Hard failures only                             |
| `SILENT`  | Nothing                                        |

### FASTBREAK_LOG_FORMAT

Controls the output format. Default is `console`.

| Value     | Output format                                         |
|-----------|-------------------------------------------------------|
| `console` | Human-readable colored output, good for development   |
| `json`    | One JSON object per line, good for log aggregation    |

### Setting environment variables

**In your shell before running the script:**

```bash
export FASTBREAK_LOG_LEVEL=DEBUG
export FASTBREAK_LOG_FORMAT=console
python my_script.py
```

**Inline for a single run:**

```bash
FASTBREAK_LOG_LEVEL=DEBUG python my_script.py
```

**From Python before importing fastbreak:**

```python
import os
os.environ["FASTBREAK_LOG_LEVEL"] = "DEBUG"
os.environ["FASTBREAK_LOG_FORMAT"] = "json"

import fastbreak  # logging configured here
```

The environment variables must be set before fastbreak is first imported. After import, changing `os.environ` has no effect on logging behavior.

### Debug output example

With `FASTBREAK_LOG_LEVEL=DEBUG`, you will see output like:

```
2026-02-27T12:00:00.123Z [debug] request_attempt endpoint=leaguestandingsv3 attempt=1 url=https://stats.nba.com/stats/leaguestandingsv3
2026-02-27T12:00:00.891Z [debug] request_success endpoint=leaguestandingsv3 attempt=1
```

On a retry:

```
2026-02-27T12:00:00.123Z [debug] request_attempt endpoint=leaguestandingsv3 attempt=1
2026-02-27T12:00:01.200Z [debug] rate_limited status=429 retry_after=2.0 attempt=1
2026-02-27T12:00:03.300Z [debug] request_attempt endpoint=leaguestandingsv3 attempt=2
2026-02-27T12:00:04.100Z [debug] request_success endpoint=leaguestandingsv3 attempt=2
```

### Bringing your own structlog configuration

If your application configures structlog before importing fastbreak, fastbreak will not override it:

```python
import structlog

# Configure structlog your way first
structlog.configure(...)

# fastbreak respects the existing configuration
from fastbreak.clients import NBAClient
```

---

## What's Next

Now that you have the basics, the other docs cover each area in depth:

- **[client.md](client.md)** — Full `NBAClient` reference: constructor parameters, `get()`, `get_many()`, caching, signal handling, bringing your own session
- **[endpoints.md](endpoints.md)** — All 100+ endpoints organized by category, with parameter tables
- **[players.md](players.md)** — `fastbreak.players` helpers: `search_players`, `get_player_game_log`, `get_player_stats`, `get_league_leaders`, `get_hustle_stats`, and more
- **[teams.md](teams.md)** — `fastbreak.teams` helpers: `get_team`, `search_teams`, `get_team_stats`, `get_lineup_stats`, `teams_by_conference`, and more
- **[games.md](games.md)** — `fastbreak.games` helpers: `get_games_on_date`, `get_box_scores`, `get_play_by_play`, `get_todays_games`
- **[seasons.md](seasons.md)** — `fastbreak.seasons` sync utilities: `get_season_from_date`, `season_start_year`, `season_to_season_id`
- **[models.md](models.md)** — Response model reference, `FrozenResponse` base class, DataFrame mixins, result set parsing
- **[gotchas.md](gotchas.md)** — Known quirks of the NBA Stats API and fastbreak behavior worth knowing before you hit them
