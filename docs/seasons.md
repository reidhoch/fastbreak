# fastbreak.seasons

## Overview

`fastbreak.seasons` provides three lightweight, synchronous utility functions for working with NBA season strings. No client, no async, no HTTP calls — just pure string manipulation and date arithmetic.

These utilities show up everywhere in fastbreak. Every helper in `fastbreak.players`, `fastbreak.teams`, `fastbreak.games`, and `fastbreak.schedule` defaults its `season` parameter to `get_season_from_date()`. Every endpoint that carries a `season` field uses `get_season_from_date` as its Pydantic field default. You can call these functions at any point in your code — at the module level, inside a sync function, or anywhere else — without an async context.

All three functions are also re-exported from the top-level `fastbreak` package:

```python
from fastbreak.seasons import get_season_from_date, season_start_year, season_to_season_id
# or equivalently:
from fastbreak import get_season_from_date, season_start_year, season_to_season_id
```

---

## Season Formats in fastbreak

The NBA Stats API accepts season identifiers in more than one format depending on which endpoint you are calling. fastbreak normalises everything to a single user-facing format and handles conversion internally.

### `Season` — "YYYY-YY" format

The primary format used throughout fastbreak. The `Season` type alias (defined in `fastbreak.types`) validates that the string is structurally correct and that the two-digit suffix is the correct continuation of the four-digit start year.

Examples: `"2024-25"`, `"2025-26"`, `"1999-00"`

This is what you pass to every endpoint and helper that takes a `season` argument, and it is what `get_season_from_date()` returns.

### SeasonID — "2YYYY" numeric format

Some low-level NBA Stats API endpoints use a numeric season identifier prefixed with `2` (indicating regular season). fastbreak generates this internally via `season_to_season_id()`. You will rarely need this format unless you are calling endpoints directly and inspecting raw parameters.

Examples: `"22024"` (for 2024-25), `"22025"` (for 2025-26)

### NBA season calendar

An NBA season spans two calendar years. The "2025-26" season begins in October 2025 (preseason) and runs through June 2026 (NBA Finals). The start year — 2025 in this example — is what anchors the season string. Dates in January through September of a given year belong to the season that started the previous October.

| Date | Season |
|------|--------|
| 2025-09-30 | "2024-25" (last day before boundary) |
| 2025-10-01 | "2025-26" (season boundary) |
| 2026-02-27 | "2025-26" (mid-season) |
| 2026-06-15 | "2025-26" (Finals) |

---

## Function Reference

### `get_season_from_date(reference_date=None) -> Season`

Returns the NBA season string for a given date. The season boundary is October 1: dates on or after October 1 belong to the season starting that year; dates before October 1 belong to the season that started the previous year.

**Signature:**

```python
def get_season_from_date(reference_date: date | None = None) -> Season
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reference_date` | `datetime.date \| None` | `None` | Date to resolve. When `None`, uses the current UTC date. |

**Returns:** `Season` — a validated season string in `"YYYY-YY"` format.

**Examples:**

```python
from datetime import date
from fastbreak.seasons import get_season_from_date

# Current season (as of 2026-02-27, this is "2025-26")
season = get_season_from_date()
print(season)  # "2025-26"

# Date in October — new season has started
print(get_season_from_date(date(2025, 10, 1)))   # "2025-26"
print(get_season_from_date(date(2025, 10, 22)))  # "2025-26"  (Opening Night)

# Date in September — still the previous season
print(get_season_from_date(date(2025, 9, 30)))   # "2024-25"
print(get_season_from_date(date(2025, 9, 15)))   # "2024-25"

# Mid-season and Finals
print(get_season_from_date(date(2025, 2, 27)))   # "2024-25"
print(get_season_from_date(date(2025, 6, 15)))   # "2024-25"

# Century-turn edge case
print(get_season_from_date(date(1999, 11, 1)))   # "1999-00"
```

---

### `season_start_year(season) -> int`

Extracts the four-digit start year from a season string as an integer. Useful when you need to do arithmetic with season years or construct a range of seasons programmatically.

**Signature:**

```python
def season_start_year(season: Season) -> int
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `season` | `Season` | Season string in `"YYYY-YY"` format. |

**Returns:** `int` — the start year (e.g., `2025` from `"2025-26"`).

**Raises:** `ValueError` if the leading four characters are not numeric. Well-typed callers validated through Pydantic will never hit this path.

**Examples:**

```python
from fastbreak.seasons import season_start_year

print(season_start_year("2025-26"))  # 2025
print(season_start_year("2024-25"))  # 2024
print(season_start_year("1999-00"))  # 1999

# Useful for arithmetic
year = season_start_year("2025-26")
previous_season_start = year - 1     # 2024
```

---

### `season_to_season_id(season) -> str`

Converts a `"YYYY-YY"` season string to the NBA Stats API's internal numeric season ID format. The ID is always prefixed with `"2"`, which designates the regular season. Preseason and playoff season IDs use different prefixes and are not supported by this function.

**Signature:**

```python
def season_to_season_id(season: Season) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `season` | `Season` | Season string in `"YYYY-YY"` format. |

**Returns:** `str` — the season ID in `"2YYYY"` format (e.g., `"22025"`).

**Examples:**

```python
from fastbreak.seasons import season_to_season_id

print(season_to_season_id("2025-26"))  # "22025"
print(season_to_season_id("2024-25"))  # "22024"
print(season_to_season_id("1999-00"))  # "21999"
```

This function is called internally by fastbreak whenever an endpoint requires the numeric season ID. You will not normally need to call it yourself unless you are constructing raw endpoint parameters or inspecting what gets sent to the API.

---

## Why These Utilities Exist

The NBA Stats API is not internally consistent about how it represents seasons. Depending on the endpoint:

- Most use `"2024-25"` — the `"YYYY-YY"` format
- Some use `"22024"` — the `"2YYYY"` numeric ID
- A few use only the four-digit start year as a plain string — `"2024"`

fastbreak standardises on `"YYYY-YY"` as the public interface and converts to other formats internally. The `Season` type alias enforces format validity through Pydantic's `AfterValidator` at model construction time, so malformed strings are caught before they ever reach the API.

---

## Usage in Context

### Default season in helpers

Every helper in `fastbreak.players`, `fastbreak.teams`, `fastbreak.games`, and `fastbreak.schedule` accepts an optional `season` parameter that defaults to `get_season_from_date()`. You never need to pass a season for current-season queries:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_game_log
from fastbreak.teams import get_team_stats

async def main():
    async with NBAClient() as client:
        # Both default to the current season automatically
        log = await get_player_game_log(client, player_id=2544)
        teams = await get_team_stats(client)

asyncio.run(main())
```

When querying a specific past season, pass the season string explicitly:

```python
log = await get_player_game_log(client, player_id=2544, season="2023-24")
```

### Endpoint field defaults

Endpoints use `get_season_from_date` as a Pydantic field default factory so that creating an endpoint without specifying a season automatically resolves to the current season at instantiation time:

```python
from fastbreak.endpoints import PlayerIndex

# Defaults to current season — get_season_from_date() is called at construction
endpoint = PlayerIndex()

# Explicit season
endpoint = PlayerIndex(season="2024-25")
```

### Iterating over multiple seasons

`season_start_year` and `get_season_from_date` make it straightforward to build season ranges:

```python
from fastbreak.seasons import get_season_from_date, season_start_year

def make_season(start_year: int) -> str:
    """Build a season string from a start year integer."""
    end_suffix = (start_year + 1) % 100
    return f"{start_year}-{end_suffix:02d}"

# Last five seasons ending at the current one
current = get_season_from_date()
current_year = season_start_year(current)
seasons = [make_season(current_year - i) for i in range(4, -1, -1)]
# e.g. ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
```

### Computing a season range for batch requests

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.seasons import get_season_from_date, season_start_year
from fastbreak.players import get_player_game_log

def make_season(start_year: int) -> str:
    end_suffix = (start_year + 1) % 100
    return f"{start_year}-{end_suffix:02d}"

async def main():
    current = get_season_from_date()
    current_year = season_start_year(current)
    # Build a three-season window: two prior seasons + current
    seasons = [make_season(current_year - i) for i in range(2, -1, -1)]

    async with NBAClient() as client:
        for season in seasons:
            log = await get_player_game_log(client, player_id=201939, season=season)
            print(f"{season}: {len(log)} games")

asyncio.run(main())
```

---

## Complete Runnable Examples

The following examples require no async context — import and call directly.

### All three functions

```python
from datetime import date
from fastbreak.seasons import (
    get_season_from_date,
    season_start_year,
    season_to_season_id,
)

# get_season_from_date
print(get_season_from_date())                        # "2025-26"  (today: 2026-02-27)
print(get_season_from_date(date(2025, 10, 22)))      # "2025-26"  (Opening Night)
print(get_season_from_date(date(2025, 9, 30)))       # "2024-25"  (day before boundary)
print(get_season_from_date(date(2025, 10, 1)))       # "2025-26"  (on the boundary)

# season_start_year
print(season_start_year("2025-26"))  # 2025
print(season_start_year("2024-25"))  # 2024
print(season_start_year("1999-00"))  # 1999

# season_to_season_id
print(season_to_season_id("2025-26"))  # "22025"
print(season_to_season_id("2024-25"))  # "22024"
print(season_to_season_id("1999-00"))  # "21999"
```

### Multi-season loop

```python
from fastbreak.seasons import get_season_from_date, season_start_year

def make_season(start_year: int) -> str:
    end_suffix = (start_year + 1) % 100
    return f"{start_year}-{end_suffix:02d}"

current = get_season_from_date()
current_year = season_start_year(current)

print("Recent seasons:")
for year in range(current_year - 4, current_year + 1):
    print(f"  {make_season(year)}")

# Recent seasons:
#   2021-22
#   2022-23
#   2023-24
#   2024-25
#   2025-26
```

### Season boundary edge cases

```python
from datetime import date
from fastbreak.seasons import get_season_from_date

boundary_cases = [
    date(2025, 9, 30),   # Last day of old season window
    date(2025, 10, 1),   # First day of new season window
    date(2025, 10, 31),  # Late October
    date(2026, 1, 1),    # New Year — still same season
    date(2026, 6, 30),   # End of Finals window
    date(2026, 9, 30),   # Late September — still same season
    date(2026, 10, 1),   # Season rolls over again
]

for d in boundary_cases:
    print(f"  {d}  ->  {get_season_from_date(d)}")

# 2025-09-30  ->  2024-25
# 2025-10-01  ->  2025-26
# 2025-10-31  ->  2025-26
# 2026-01-01  ->  2025-26
# 2026-06-30  ->  2025-26
# 2026-09-30  ->  2025-26
# 2026-10-01  ->  2026-27
```

The runnable version of these examples lives at `examples/seasons.py` in the repository.
