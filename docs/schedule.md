# fastbreak.schedule

## Overview

`fastbreak.schedule` provides an async schedule fetcher and sync utility functions for rest-day analysis.

- `get_team_schedule` is **async** — it calls the NBA Stats API and requires an `NBAClient` instance.
- `is_back_to_back` and `days_rest_before_game` are **sync** — they operate on a plain `list[datetime.date]` and require no client or network access.

The async function fetches the full league schedule from the `ScheduleLeagueV2` endpoint and filters it down to the games that involve the requested team. The sync helpers accept the resulting list of dates so you can run rest-day analysis without additional API calls.

```python
from fastbreak.schedule import get_team_schedule, is_back_to_back, days_rest_before_game
```

---

## Function Reference

### `get_team_schedule(client, team_id, season=None) -> list[ScheduledGame]`

Returns all scheduled games for a team in a season, sorted by date (chronological order).

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `NBAClient` | An active `NBAClient` async context manager instance |
| `team_id` | `int` | NBA team ID (e.g., `1610612754` for the Indiana Pacers) |
| `season` | `str \| None` | Season in `YYYY-YY` format (e.g., `"2025-26"`). Defaults to the current season via `get_season_from_date()` |

**Returns**

`list[ScheduledGame]` — games sorted chronologically by `game_date_est`. Games with no date sort to the end of the list and a warning is logged.

**Behavior**

- Fetches the complete league schedule via the `ScheduleLeagueV2` endpoint for the given season.
- Filters to only games where the team appears as either the home or away team.
- Returns an empty list if the API response contains no `leagueSchedule` field (e.g., offseason or data unavailability), and logs a warning.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.schedule import get_team_schedule

async def main():
    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=1610612754)
        print(f"Found {len(games)} games")
        for g in games[:5]:
            print(g.game_date_est, g.away_team.team_tricode, "@", g.home_team.team_tricode)

asyncio.run(main())
```

---

### `days_rest_before_game(game_dates, game_index) -> int | None`

Returns the number of rest days before the game at `game_index` in a sorted list of game dates.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `game_dates` | `list[datetime.date]` | Sorted list of game dates for a single team |
| `game_index` | `int` | 0-based index of the game to examine |

**Returns**

| Value | Meaning |
|-------|---------|
| `None` | First game of the season — no prior game exists |
| `0` | Back-to-back — the team played the night before |
| `1` | One day off between games |
| `N` | N days off between games |

**Formula**

```
rest_days = (game_dates[game_index] - game_dates[game_index - 1]).days - 1
```

The result is clamped to a minimum of `0` so same-day entries (which should not occur in a valid schedule) do not return negative values.

**Examples**

```python
from datetime import date
from fastbreak.schedule import days_rest_before_game

dates = [
    date(2025, 1, 14),  # index 0 — season opener
    date(2025, 1, 15),  # index 1 — next day (back-to-back)
    date(2025, 1, 17),  # index 2 — one day off
    date(2025, 1, 20),  # index 3 — two days off
]

days_rest_before_game(dates, 0)  # None  — first game
days_rest_before_game(dates, 1)  # 0     — back-to-back (Jan 14 -> Jan 15)
days_rest_before_game(dates, 2)  # 1     — one day off  (Jan 15 -> Jan 17)
days_rest_before_game(dates, 3)  # 2     — two days off (Jan 17 -> Jan 20)
```

---

### `is_back_to_back(game_dates, game_index) -> bool`

Returns `True` if the game at `game_index` is the second leg of a back-to-back.

This is a convenience wrapper around `days_rest_before_game`. It returns `True` when `days_rest_before_game` returns `0`, and `False` for any other value (including `None` for the first game of the season).

**Parameters**

Same as `days_rest_before_game`.

**Returns**

`bool` — `True` only when `days_rest_before_game(game_dates, game_index) == 0`.

```python
from datetime import date
from fastbreak.schedule import is_back_to_back

dates = [date(2025, 1, 14), date(2025, 1, 15), date(2025, 1, 17)]

is_back_to_back(dates, 0)  # False — first game of season
is_back_to_back(dates, 1)  # True  — played Jan 14, playing again Jan 15
is_back_to_back(dates, 2)  # False — one day off
```

---

## ScheduledGame Fields

`ScheduledGame` is a Pydantic model with `extra="ignore"`, so forward-compatible with future API additions.

### Identifiers and Status

| Field | Type | Description |
|-------|------|-------------|
| `game_id` | `str \| None` | NBA game ID (e.g., `"0022500571"`). First 3 chars encode game type: `001`=preseason, `002`=regular season, `003`=All-Star, `004`=playoffs |
| `game_code` | `str \| None` | Short code combining date and teams (e.g., `"20250115/INDLAL"`) |
| `game_status` | `int \| None` | `1` = scheduled, `2` = in progress, `3` = final |
| `game_status_text` | `str \| None` | Human-readable status (e.g., `"Final"`, `"7:00 pm ET"`) |
| `game_sequence` | `int \| None` | Ordering within the game date |
| `postponed_status` | `str \| None` | Postponement indicator if applicable |
| `if_necessary` | `str \| None` | Playoff flag — present when the game is "if necessary" |

### Date and Time

| Field | Type | Description |
|-------|------|-------------|
| `game_date_est` | `str \| None` | Game date in Eastern Time, ISO format (`"YYYY-MM-DDT00:00:00"`) — used as sort key |
| `game_time_est` | `str \| None` | Tipoff time in Eastern Time |
| `game_date_time_est` | `str \| None` | Combined date and time in Eastern Time |
| `game_date_utc` | `str \| None` | Game date in UTC |
| `game_time_utc` | `str \| None` | Tipoff time in UTC |
| `game_date_time_utc` | `str \| None` | Combined date and time in UTC |
| `away_team_time` | `str \| None` | Tipoff time in the away team's local timezone |
| `home_team_time` | `str \| None` | Tipoff time in the home team's local timezone |
| `day` | `str \| None` | Day of week abbreviation (e.g., `"Wed"`) |
| `month_num` | `int \| None` | Month number (1–12) |
| `week_number` | `int \| None` | NBA schedule week number |
| `week_name` | `str \| None` | NBA schedule week label |

### Venue

| Field | Type | Description |
|-------|------|-------------|
| `arena_name` | `str \| None` | Arena name (e.g., `"Gainbridge Fieldhouse"`) |
| `arena_state` | `str \| None` | State abbreviation (e.g., `"IN"`) |
| `arena_city` | `str \| None` | City name (e.g., `"Indianapolis"`) |
| `is_neutral` | `bool \| None` | `True` if the game is played at a neutral site |

### Series / Playoff Labels

| Field | Type | Description |
|-------|------|-------------|
| `series_game_number` | `str \| None` | Game number within a playoff series (e.g., `"Game 3"`) |
| `series_text` | `str \| None` | Series standing text (e.g., `"IND leads series 2-1"`) |
| `game_label` | `str \| None` | Special event label (e.g., `"NBA Cup"`) |
| `game_sub_label` | `str \| None` | Additional label detail |
| `game_subtype` | `str \| None` | Game subtype code |

### Teams

| Field | Type | Description |
|-------|------|-------------|
| `home_team` | `ScheduleTeam \| None` | Home team details (see below) |
| `away_team` | `ScheduleTeam \| None` | Away team details (see below) |

`ScheduleTeam` fields:

| Field | Type | Description |
|-------|------|-------------|
| `team_id` | `int \| None` | NBA team ID |
| `team_name` | `str \| None` | Team nickname (e.g., `"Pacers"`) |
| `team_city` | `str \| None` | Team city (e.g., `"Indiana"`) |
| `team_tricode` | `str \| None` | Three-letter code (e.g., `"IND"`) |
| `team_slug` | `str \| None` | URL slug (e.g., `"pacers"`) |
| `wins` | `int \| None` | Current season wins (populated for completed games) |
| `losses` | `int \| None` | Current season losses (populated for completed games) |
| `score` | `int \| None` | Final or current score (populated during/after game) |
| `seed` | `int \| None` | Playoff seed (populated in postseason) |

### Broadcasters

| Field | Type | Description |
|-------|------|-------------|
| `broadcasters` | `GameBroadcasters \| None` | All broadcast information grouped by category |

`GameBroadcasters` groups `ScheduleBroadcaster` objects by distribution type:

| Field | Description |
|-------|-------------|
| `national_broadcasters` | National TV broadcasters |
| `national_radio_broadcasters` | National radio broadcasters |
| `national_ott_broadcasters` | National streaming/OTT broadcasters |
| `home_tv_broadcasters` | Home market TV broadcasters |
| `home_radio_broadcasters` | Home market radio broadcasters |
| `home_ott_broadcasters` | Home market streaming broadcasters |
| `away_tv_broadcasters` | Away market TV broadcasters |
| `away_radio_broadcasters` | Away market radio broadcasters |
| `away_ott_broadcasters` | Away market streaming broadcasters |

Each `ScheduleBroadcaster` includes: `broadcaster_id`, `broadcaster_display`, `broadcaster_abbreviation`, `broadcaster_scope`, `broadcaster_media`, `broadcaster_description`, `broadcaster_video_link`, `broadcaster_team_id`, `broadcaster_ranking`, `tape_delay_comments`, `localization_region`.

### Points Leaders

| Field | Type | Description |
|-------|------|-------------|
| `points_leaders` | `list[PointsLeader]` | Top scorers for completed games (empty list for future games) |

`PointsLeader` fields: `person_id`, `first_name`, `last_name`, `team_id`, `team_city`, `team_name`, `team_tricode`, `points`.

### Misc

| Field | Type | Description |
|-------|------|-------------|
| `branch_link` | `str \| None` | Deep-link URL for the game |

---

## Common Patterns

### Finding all back-to-backs in a season

Extract the game dates from the schedule, then use `days_rest_before_game` to find every instance where rest days equal zero.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.schedule import get_team_schedule, days_rest_before_game

async def main():
    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=1610612754)  # Pacers

    # Filter out games without a date, then build the dates list
    from datetime import date
    dated_games = [g for g in games if g.game_date_est is not None]
    dates = [date.fromisoformat(g.game_date_est[:10]) for g in dated_games]

    back_to_backs = [
        (dated_games[i], dates[i])
        for i in range(len(dated_games))
        if days_rest_before_game(dates, i) == 0
    ]

    print(f"Back-to-backs this season: {len(back_to_backs)}")
    for game, game_date in back_to_backs:
        opp = (
            game.away_team.team_tricode
            if game.home_team and game.home_team.team_id == 1610612754
            else game.home_team.team_tricode if game.home_team else "?"
        )
        print(f"  {game_date}  vs/@ {opp}")

asyncio.run(main())
```

### Rest days histogram

Compute the distribution of rest days across a full season to understand schedule density.

```python
import asyncio
from collections import Counter
from datetime import date
from fastbreak.clients import NBAClient
from fastbreak.schedule import get_team_schedule, days_rest_before_game

async def main():
    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=1610612754)  # Pacers

    dates = [
        date.fromisoformat(g.game_date_est[:10])
        for g in games
        if g.game_date_est is not None
    ]

    rest_counts: Counter[int] = Counter()
    for i in range(len(dates)):
        rest = days_rest_before_game(dates, i)
        if rest is not None:
            rest_counts[rest] += 1

    print("Rest days distribution:")
    for days in sorted(rest_counts):
        label = "back-to-back" if days == 0 else f"{days} day(s) rest"
        print(f"  {label}: {rest_counts[days]} games")

asyncio.run(main())
```

### Upcoming schedule

Filter to only future games using today's date.

```python
import asyncio
from datetime import date
from fastbreak.clients import NBAClient
from fastbreak.schedule import get_team_schedule

async def main():
    today = date.today()

    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=1610612754)  # Pacers

    upcoming = [
        g for g in games
        if g.game_date_est is not None
        and date.fromisoformat(g.game_date_est[:10]) >= today
    ]

    print(f"Upcoming games ({len(upcoming)} remaining):")
    for g in upcoming[:10]:
        home = g.home_team.team_tricode if g.home_team else "?"
        away = g.away_team.team_tricode if g.away_team else "?"
        location = "HOME" if g.home_team and g.home_team.team_id == 1610612754 else "AWAY"
        print(f"  {g.game_date_est[:10]}  {away} @ {home}  [{location}]  {g.game_status_text}")

asyncio.run(main())
```

---

## Full Examples

### Example 1: Season schedule summary

Print a formatted season schedule with rest-day annotations.

```python
"""Season schedule summary with rest-day annotations."""

import asyncio
from datetime import date

from fastbreak.clients import NBAClient
from fastbreak.schedule import days_rest_before_game, get_team_schedule

TEAM_ID = 1610612754  # Indiana Pacers
SEASON = "2025-26"


async def main() -> None:
    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=TEAM_ID, season=SEASON)

    dated_games = [g for g in games if g.game_date_est is not None]
    dates = [date.fromisoformat(g.game_date_est[:10]) for g in dated_games]

    print(f"Indiana Pacers — {SEASON} Schedule ({len(games)} games)\n")
    print(f"{'Date':<12} {'Matchup':<20} {'Location':<6} {'Rest'}")
    print("-" * 55)

    for i, game in enumerate(dated_games):
        game_date = date.fromisoformat(game.game_date_est[:10])
        home = game.home_team.team_tricode if game.home_team else "???"
        away = game.away_team.team_tricode if game.away_team else "???"
        matchup = f"{away} @ {home}"
        is_home = game.home_team is not None and game.home_team.team_id == TEAM_ID
        location = "HOME" if is_home else "AWAY"

        rest = days_rest_before_game(dates, i)
        if rest is None:
            rest_label = "opener"
        elif rest == 0:
            rest_label = "B2B"
        else:
            rest_label = f"{rest}d"

        print(f"{str(game_date):<12} {matchup:<20} {location:<6} {rest_label}")


asyncio.run(main())
```

### Example 2: Broadcaster lookup

Find all nationally televised games on a specific network.

```python
"""Find all games broadcast on a specific national network."""

import asyncio
from fastbreak.clients import NBAClient
from fastbreak.schedule import get_team_schedule

TEAM_ID = 1610612754  # Indiana Pacers
TARGET_NETWORK = "ESPN"


async def main() -> None:
    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=TEAM_ID)

    national_tv_games = []
    for game in games:
        if game.broadcasters is None:
            continue
        for bc in game.broadcasters.national_broadcasters:
            if bc.broadcaster_abbreviation == TARGET_NETWORK:
                national_tv_games.append(game)
                break

    print(f"Pacers games on {TARGET_NETWORK}: {len(national_tv_games)}")
    for game in national_tv_games:
        home = game.home_team.team_tricode if game.home_team else "???"
        away = game.away_team.team_tricode if game.away_team else "???"
        print(f"  {game.game_date_est[:10] if game.game_date_est else 'TBD'}  {away} @ {home}")


asyncio.run(main())
```

### Example 3: Back-to-back fatigue tracker

For each back-to-back, show the preceding game and the B2B game side by side.

```python
"""Back-to-back fatigue tracker — shows preceding game and B2B game pairs."""

import asyncio
from datetime import date

from fastbreak.clients import NBAClient
from fastbreak.schedule import days_rest_before_game, get_team_schedule

TEAM_ID = 1610612754  # Indiana Pacers


def _matchup(game) -> str:
    home = game.home_team.team_tricode if game.home_team else "???"
    away = game.away_team.team_tricode if game.away_team else "???"
    return f"{away} @ {home}"


async def main() -> None:
    async with NBAClient() as client:
        games = await get_team_schedule(client, team_id=TEAM_ID)

    dated_games = [g for g in games if g.game_date_est is not None]
    dates = [date.fromisoformat(g.game_date_est[:10]) for g in dated_games]

    b2b_pairs = [
        (dated_games[i - 1], dated_games[i])
        for i in range(1, len(dated_games))
        if days_rest_before_game(dates, i) == 0
    ]

    print(f"Indiana Pacers — Back-to-Backs ({len(b2b_pairs)} total)\n")
    for first, second in b2b_pairs:
        d1 = first.game_date_est[:10] if first.game_date_est else "?"
        d2 = second.game_date_est[:10] if second.game_date_est else "?"
        print(f"  Night 1: {d1}  {_matchup(first)}")
        print(f"  Night 2: {d2}  {_matchup(second)}")
        print()


asyncio.run(main())
```

---

## Note on Data Availability

Schedule data is sourced from the `ScheduleLeagueV2` endpoint (`scheduleleaguev2`). A few considerations:

- **Offseason**: Calling `get_team_schedule` before the upcoming season's schedule is released will return an empty list. A warning is logged with `league_schedule_missing_from_response`.
- **Future games**: The schedule for the full season is typically published before the season starts. Game times and broadcasters for games many weeks in advance may still be `None` or subject to change.
- **Game status**: Use `game_status` to differentiate scheduled (`1`), in-progress (`2`), and final (`3`) games. For future games, `score` and `points_leaders` will be `None` or empty.
- **Playoffs and All-Star**: All-Star games produce non-standard tricodes (e.g., `"WLD"`, `"STP"`, `"STR"`). Filter with `game_id[:3] == "002"` to keep only regular-season games. Playoff games use prefix `"004"`.
- **Neutral-site games**: Check `game.is_neutral` for games played at a neutral site (e.g., international games, NBA Cup finals) where `home_team` may not reflect the actual court advantage.
