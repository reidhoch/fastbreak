# Gotchas and Known Quirks

Common unexpected behaviors and non-obvious API quirks. Each entry: what you observe, why it happens, what to do.

---

## Table of Contents

1. [Game ID encoding and All-Star filtering](#1-game-id-encoding-and-all-star-filtering)
2. [SynergyPlaytypes always returns 0 rows](#2-synergyplaytypes-always-returns-0-rows)
3. [lineup.min is per-game average minutes, not total](#3-lineupmin-is-per-game-average-minutes-not-total)
4. [On/off split pts is team points, not player points](#4-onoff-split-pts-is-team-points-not-player-points)
5. [asyncio only — trio is not supported](#5-asyncio-only--trio-is-not-supported)
6. [NBAClient(handle_signals=False) for web servers](#6-nbaclienthandle_signalsfalse-for-web-servers)
7. [FrozenResponse.strict() for catching API schema drift](#7-frozenresponsestrictfor-catching-api-schema-drift)
8. [Endpoints are frozen Pydantic models, not dataclasses](#8-endpoints-are-frozen-pydantic-models-not-dataclasses)
9. [get_many() raises ExceptionGroup, not a plain exception](#9-get_many-raises-exceptiongroup-not-a-plain-exception)
10. [Season boundary: October 1st, not the first game](#10-season-boundary-october-1st-not-the-first-game)
11. [Date format differences by context](#11-date-format-differences-by-context)
12. [PlayerProfileV2 vs CommonPlayerInfo](#12-playerprofilev2-vs-commonplayerinfo)

---

## 1. Game ID encoding and All-Star filtering

**Symptom**

You fetch a full list of game IDs for a season and encounter unexpected team abbreviations like `"WLD"`, `"STP"`, or `"STR"` in box scores or scoreboard data. Code that maps tricodes to team names, looks up team stats, or validates abbreviations breaks silently or raises a `KeyError`.

**Root cause**

NBA game IDs are 10-character strings, and the first three characters encode the game type:

| Prefix | Game type       |
|--------|-----------------|
| `001`  | Preseason       |
| `002`  | Regular season  |
| `003`  | All-Star        |
| `004`  | Playoffs        |

All-Star games (`003`) use non-standard team abbreviations that do not correspond to any real NBA franchise. The abbreviations vary by year and format — for example, World vs. USA games used `"WLD"` and `"USA"`, while the current East vs. West format uses `"EAS"` and `"WES"`, and celebrity/alumni games introduce entirely arbitrary codes. None of these appear in the `TEAMS` registry in `fastbreak.teams`.

**Solution**

Filter by game ID prefix before processing results. Use `gid[:3]` to select only the game types you care about:

```python
from fastbreak.games import get_game_ids

# Regular season only — eliminates All-Star, preseason, and playoff games
all_ids = await get_game_ids(client, "2025-26", team_id=1610612747)
regular_season_ids = [gid for gid in all_ids if gid[:3] == "002"]

# Playoffs only
playoff_ids = [gid for gid in all_ids if gid[:3] == "004"]

# Both regular season and playoffs (e.g., for full-season analysis)
real_game_ids = [gid for gid in all_ids if gid[:3] in ("002", "004")]
```

If you are iterating over box scores and validating tricodes, always apply the prefix filter upstream. Letting All-Star game IDs reach team-lookup code will cause failures that are difficult to diagnose.

---

## 2. SynergyPlaytypes always returns 0 rows

**Symptom**

Calling `get_player_playtypes()` or `get_team_playtypes()` returns an empty list — no error, no warning, just `[]`.

**Root cause**

The Synergy play-type data (pick-and-roll ball handler frequency, post-up efficiency, spot-up PPP, etc.) is commercially licensed and **not available on the public NBA Stats API**. The `SynergyPlaytypes` endpoint accepts requests and returns a valid HTTP 200 response — it simply contains zero rows. This is not a parsing bug in fastbreak; it is an intentional access restriction on the API server.

**Workaround**

There is no workaround for the public API. The data is behind a Synergy Sports subscription.

If you need play-type data, the options are:

- Purchase a Synergy Sports or NBA Advanced Media subscription with an API key that grants access to this endpoint.
- Use a third-party data provider that has licensed the data (e.g., cleaning the glass, pbpstats.com).
- Approximate play types manually from play-by-play data using `get_play_by_play()`.

Do not confuse a missing data subscription with a broken endpoint. If you add retry logic or error handling around `get_player_playtypes()` expecting it to eventually succeed, it will spin indefinitely — the endpoint is functioning correctly.

---

## 3. lineup.min is per-game average minutes, not total

**Symptom**

You call `get_lineup_stats()` and see a five-man lineup with `min = 24.5` that has only appeared in 3 games together. Your intuition says the lineup has played a combined 24.5 minutes total, but that seems plausible — until you notice a different lineup with 2 games played showing `min = 31.2`. Total minutes cannot exceed game length, so something is off.

**Root cause**

The `min` field on `LineupStats` is the **per-game average minutes** the lineup played together, not the cumulative total across all appearances. The NBA Stats API reports it this way, and the field name is genuinely misleading. A lineup with `min = 24.5` and `gp = 3` has played an average of 24.5 minutes per game they appeared together — a total of roughly 73.5 minutes.

This also affects `get_lineup_net_ratings()`. The `min_minutes` threshold parameter (default `10.0`) filters out lineups that average fewer than 10 minutes per game together — it is **not** a minimum total minutes threshold.

```python
# get_lineup_net_ratings filters by per-game average, not total minutes
lineups = await get_lineup_net_ratings(
    client,
    team_id=1610612747,
    min_minutes=10.0,  # excludes lineups averaging <10 min/game together
)
```

**Solution**

If you need total lineup minutes, multiply `min` by `gp` (games played):

```python
lineups = await get_lineup_stats(client, team_id=1610612747)

for lineup in lineups:
    total_minutes = lineup.min * lineup.gp
    print(f"{lineup.group_name}: {total_minutes:.1f} total min ({lineup.gp} games)")
```

Use `get_lineup_stats()` directly when you need access to `gp` for this calculation. The higher-level `get_lineup_net_ratings()` helper returns `(LineupStats, net_rating)` tuples, so `gp` is still accessible from the `LineupStats` object.

---

## 4. On/off split pts is team points, not player points

**Symptom**

You call `get_on_off_splits()` for a player and inspect the `pts` field on the returned rows. You see values like `114.2` and `109.8` — far higher than any individual player's per-game scoring average. The numbers look like team scoring rates, not player scoring.

**Root cause**

In on/off split data from the `LeaguePlayerOnDetails` endpoint, `pts` represents **team points per game while the player is on the court** (or per 100 possessions, depending on `per_mode`). It measures how many points the team scores with this player on the floor — a team context metric, not the individual player's personal scoring output.

This is correct NBA Stats API behavior. The on/off framework is designed to evaluate a player's impact on team performance, so all offensive and defensive stats in these rows reflect team-level outcomes, not the player's individual box score line.

**Solution**

Interpret `pts` as a team scoring rate, not player scoring:

```python
splits = await get_on_off_splits(
    client,
    player_id=2544,
    team_id=1610612747,
    per_mode="PerGame",
)

on_pts  = splits["on"][0].pts   # team points per game with player on court
off_pts = splits["off"][0].pts  # team points per game with player off court

# A positive difference means the team scores more with the player on the floor
impact = on_pts - off_pts
print(f"Scoring impact: {impact:+.1f} pts/game")
```

If you need the player's individual scoring, use `get_player_stats()` or `get_player_game_log()` instead.

---

## 5. asyncio only — trio is not supported

**Symptom**

You attempt to use fastbreak inside a trio-based application and receive errors about the event loop, incompatible backends, or missing asyncio APIs.

**Root cause**

fastbreak uses [aiohttp](https://docs.aiohttp.org/) as its HTTP transport layer. aiohttp is built on asyncio and does not support trio. While fastbreak uses anyio internally for concurrency primitives (`Lock`, `CapacityLimiter`, `create_task_group`), the underlying `ClientSession` from aiohttp requires an asyncio event loop.

**Solution**

Run fastbreak under asyncio. If your application uses trio, you have two options:

- Switch the top-level runner to asyncio: `asyncio.run(main())` instead of `trio.run(main)`.
- Use a subprocess or worker process boundary to isolate fastbreak from the trio event loop.

There is no supported way to use fastbreak directly within a trio task.

---

## 6. NBAClient(handle_signals=False) for web servers

**Symptom**

When you embed `NBAClient` inside a FastAPI application, an aiohttp web server, or Django with async support, you see warnings about signal handlers being registered or overwritten. In some cases, `SIGINT` or `SIGTERM` does not cleanly shut down your application — either it shuts down too early, ignores the signal, or raises a `RuntimeError` about signal handlers in threads.

**Root cause**

By default, `NBAClient` installs `SIGINT` and `SIGTERM` handlers on the running asyncio event loop when it enters the `async with` block (`__aenter__`). These handlers close the HTTP session and cancel all pending tasks on signal receipt — the right behaviour for a standalone script.

Web frameworks manage their own signal handling and lifecycle. When NBAClient installs its own handlers, it replaces or interferes with the framework's handlers. On shutdown, the framework may lose its SIGTERM handler entirely, leaving it unable to perform its own graceful shutdown (draining in-flight requests, closing database connections, etc.).

`loop.add_signal_handler()` also raises `NotImplementedError` on Windows and `RuntimeError` if called from a non-main thread — both common in web server workers.

**Solution**

Pass `handle_signals=False` and manage the client lifecycle yourself using your framework's startup/shutdown hooks.

FastAPI lifespan example:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastbreak.clients import NBAClient

client: NBAClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    # Startup — disable signal handling; FastAPI manages its own
    client = NBAClient(cache_ttl=300, handle_signals=False)
    await client.__aenter__()
    yield
    # Shutdown
    await client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/players/{player_id}/stats")
async def player_stats(player_id: int):
    from fastbreak.players import get_player_stats
    return await get_player_stats(client, player_id=player_id)
```

For standalone scripts where NBAClient is used as an `async with` context manager directly, the default `handle_signals=True` is appropriate and provides clean Ctrl-C behaviour.

---

## 7. FrozenResponse.strict() for catching API schema drift

**Symptom**

The NBA Stats API adds a new field to a response — for example, a new `tracking_zone` key appears on player stats rows. Your code runs without errors and your tests pass. You only discover the change weeks later when a colleague mentions the new field. Alternatively, a field is renamed and the old name stops appearing, but your Pydantic model silently falls back to its default value instead of raising an error.

**Root cause**

All fastbreak response models inherit from `FrozenResponse`, which is configured with `extra="ignore"`. This is intentional — it makes the library forward-compatible with NBA Stats API changes that add new fields. The downside is that extra fields are silently discarded rather than surfaced.

`FrozenResponse` does log a `WARNING`-level structured log event (`unknown_fields_received`) when it receives fields that are not in the model, but this only helps if you are watching logs.

**Solution**

Use `MyResponse.strict()` in your tests to create a version of the model that raises a `ValidationError` on any extra field:

```python
from fastbreak.models import PlayerGameLogResponse

def test_player_game_log_schema(fixture_data: dict):
    # This raises ValidationError if the API fixture contains fields
    # that are not mapped in PlayerGameLogResponse
    StrictPlayerGameLog = PlayerGameLogResponse.strict()
    result = StrictPlayerGameLog.model_validate(fixture_data)
    assert len(result.games) > 0
```

`strict()` creates a new subclass with `extra="forbid"` using `ConfigDict`. It does not mutate the original model class, so it is safe to use in tests alongside normal usage.

Recommended practice:

- Keep fixture JSON files checked into your test suite alongside model tests.
- Run `uv run pytest -m live_api` periodically and watch for `unknown_fields_received` log warnings — these indicate the API has added fields that your models do not yet handle.
- When a new field appears in live API responses, add it to the model and regenerate the fixture.

---

## 8. Endpoints are frozen Pydantic models, not dataclasses

**Symptom**

You try to reuse an endpoint object by updating one of its parameters after construction:

```python
endpoint = BoxScoreTraditional(game_id="0022500571")
endpoint.game_id = "0022500572"  # Trying to reuse for a different game
```

This raises a `ValidationError` or `TypeError` rather than updating the field.

**Root cause**

All endpoint classes inherit from `Endpoint[T]`, which uses `ConfigDict(frozen=True)`. Frozen Pydantic models raise a `ValidationError` if you attempt attribute assignment after construction — they are immutable by design. This prevents accidental mutation of an endpoint that may already be in flight or cached.

Endpoints are not Python `@dataclass(frozen=True)` instances either — they are Pydantic models, so the error message comes from Pydantic's validation machinery rather than a standard `FrozenInstanceError`.

**Solution**

Construct a new endpoint with the desired parameters. Endpoint objects are lightweight (just a few string fields) — creating many of them is cheap:

```python
# Correct approach: create a new endpoint per game
game_ids = ["0022500571", "0022500572", "0022500573"]
endpoints = [BoxScoreTraditional(game_id=gid) for gid in game_ids]

# Fetch all concurrently
results = await client.get_many(endpoints)
```

For parametric sweeps (e.g., fetching player stats for multiple `per_mode` values), use a list comprehension:

```python
from fastbreak.endpoints import PlayerGameLog

endpoints = [
    PlayerGameLog(player_id=2544, season=season)
    for season in ["2023-24", "2024-25", "2025-26"]
]
logs = await client.get_many(endpoints)
```

---

## 9. get_many() raises ExceptionGroup, not a plain exception

**Symptom**

You wrap `get_many()` in a `try/except Exception` block expecting to catch request failures, but the exception is not caught:

```python
try:
    results = await client.get_many(endpoints)
except Exception as e:
    print(f"Failed: {e}")  # This block is never entered despite failures
```

Or you see an unhandled `ExceptionGroup` traceback that looks different from a normal exception.

**Root cause**

`get_many()` uses `anyio.create_task_group()` for structured concurrency. When any task within a task group raises an exception, anyio cancels all sibling tasks and wraps all collected exceptions in an `ExceptionGroup` (Python 3.11+). An `ExceptionGroup` is a subclass of `BaseException`, not `Exception` — so `except Exception` does not catch it.

By design: when one request fails, all others are cancelled. `get_many()` never partially succeeds silently.

**Solution**

Use Python 3.11+ `except*` syntax to handle `ExceptionGroup`:

```python
from aiohttp import ClientResponseError

try:
    results = await client.get_many(endpoints)
except* ClientResponseError as eg:
    for exc in eg.exceptions:
        print(f"HTTP error {exc.status}: {exc.message}")
except* TimeoutError as eg:
    print(f"Timed out on {len(eg.exceptions)} requests")
```

If you are on a framework or pattern that cannot use `except*`, you can catch `BaseException` or `ExceptionGroup` directly:

```python
import builtins

try:
    results = await client.get_many(endpoints)
except BaseException as e:
    if isinstance(e, ExceptionGroup):
        for exc in e.exceptions:
            handle_exception(exc)
    else:
        raise
```

For batch requests where partial failure is acceptable, consider splitting `endpoints` into individual `client.get()` calls wrapped in `asyncio.gather(..., return_exceptions=True)` instead of using `get_many()`.

---

## 10. Season boundary: October 1st, not the first game of the season

**Symptom**

You call `get_season_from_date()` in mid-September and get the previous season string (e.g., `"2024-25"`) even though NBA training camp has already started and the league has officially announced the new season's schedule.

**Root cause**

`get_season_from_date()` uses **October 1st** as the hard-coded season boundary. Any date with `month < 10` is treated as belonging to the previous season's year. October 1 is hardcoded as a safe cutoff — the exact preseason start shifts each year, but the first regular-season game is always after it.

```python
# From fastbreak/seasons.py:
start_year = ref.year if ref.month >= _SEASON_START_MONTH else ref.year - 1
# where _SEASON_START_MONTH = 10
```

In practice:
- Preseason typically starts in early October.
- Regular season typically starts mid-to-late October.
- The September gap (training camp and preseason scheduling) returns the prior season.

**Solution**

If you are working with preseason data in September or early October, pass the date explicitly rather than relying on the default:

```python
from datetime import date
from fastbreak.seasons import get_season_from_date

# September: still returns "2024-25"
get_season_from_date(date(2025, 9, 15))   # → "2024-25"

# October 1st onward: returns new season
get_season_from_date(date(2025, 10, 1))   # → "2025-26"
get_season_from_date(date(2025, 10, 15))  # → "2025-26"
```

If you need to work with preseason games in late September, construct the season string manually (`"2025-26"`) rather than deriving it from the date.

---

## 11. Date format differences by context

**Symptom**

You pass a date string to an endpoint parameter and either get a `ValidationError` immediately, or the request succeeds but returns zero results. Switching between different helper functions in the same session, you find that the format that worked in one call fails in another.

**Root cause**

fastbreak uses two different date formats depending on the context, reflecting the underlying NBA Stats API's own inconsistency:

| Context | Format | Example |
|---------|--------|---------|
| `Date` type alias (most endpoint params) | `MM/DD/YYYY` | `"01/15/2026"` |
| `get_games_on_date()` / scoreboard helpers | `YYYY-MM-DD` (ISO 8601) | `"2026-01-15"` |

The `Date` type alias is defined in `fastbreak.types` as `MM/DD/YYYY` to match the format the NBA Stats API expects in query parameters. The `get_games_on_date()` helper accepts ISO format as a developer convenience and converts it internally before sending the request.

Mixing these up produces one of two failure modes:

- **Typed endpoint param**: Pydantic validates the `Date` alias at construction time and raises a `ValidationError` if the format does not match.
- **Untyped or string param**: The API receives the malformed date, ignores it or treats it as a missing param, and returns an empty result set with no error.

**Solution**

Follow the format expected by each interface:

```python
from fastbreak.games import get_games_on_date
from fastbreak.endpoints import ScoreboardV2
from fastbreak.types import Date

# Helper function — use ISO format (YYYY-MM-DD)
games = await get_games_on_date(client, "2026-01-15")

# Direct endpoint construction — use MM/DD/YYYY (the Date type alias)
endpoint = ScoreboardV2(game_date=Date("01/15/2026"))
result = await client.get(endpoint)
```

If you are constructing dates dynamically from Python `datetime` objects, use the appropriate `strftime` format for each context:

```python
from datetime import date

d = date(2026, 1, 15)

iso_format = d.strftime("%Y-%m-%d")     # "2026-01-15"  → for get_games_on_date()
nba_format = d.strftime("%m/%d/%Y")     # "01/15/2026"  → for Date type params
```

---

## 12. PlayerProfileV2 vs CommonPlayerInfo

**Symptom**

You need basic player details (name, team, position, jersey number) and are unsure which endpoint to use. You try `PlayerProfileV2` and find it is noticeably slower than you expected and returns a large payload with many result sets you do not need.

**Root cause**

These are two separate endpoints that overlap in player biographical data but serve different purposes:

- **`CommonPlayerInfo`** — a lightweight endpoint returning a single result set with the player's current biographical details: name, team, position, height, weight, draft info, and a handful of career milestones. Fast and minimal. Use this for lookups.

- **`PlayerProfileV2`** — a heavier endpoint that returns multiple result sets including career totals by season, career per-game averages, career highs, and awards. It is significantly larger and slower because it aggregates a player's entire career history in one call.

**Solution**

Use `CommonPlayerInfo` (via `get_player()` or `get_player_id()`) for player lookups and biographical details:

```python
from fastbreak.players import get_player, get_player_id

# Fast — uses CommonPlayerInfo internally
player = await get_player(client, "Nikola Jokic")
print(player.team_abbreviation, player.position)

pid = await get_player_id(client, "Nikola Jokic")
```

Reserve `PlayerProfileV2` for situations where you specifically need career totals or career highs — it returns more complete historical data but at the cost of a larger response and slower parse time:

```python
from fastbreak.endpoints import PlayerProfileV2

endpoint = PlayerProfileV2(player_id=203999)
profile = await client.get(endpoint)
career_totals = profile.career_totals_regular_season
```

Do not use `PlayerProfileV2` in a loop over many players — the response size and API latency will multiply quickly. For bulk season stats, use `get_player_stats()` with `get_many()` instead.
