# fastbreak.games

Async helpers for the most common game-related workflows: finding games by date or season, fetching live and final scores, retrieving box scores for multiple games concurrently, and pulling full play-by-play logs.

All functions in this module are async and require an `NBAClient` instance. The module imports from `fastbreak.games`:

```python
from fastbreak.games import (
    get_game_ids,
    get_games_on_date,
    get_todays_games,
    get_yesterdays_games,
    get_game_summary,
    get_box_scores,
    get_play_by_play,
)
```

---

## Understanding game IDs

Every NBA game has a 10-character string ID such as `"0022500571"`. The first three characters encode the game type:

| Prefix | Game type         |
|--------|-------------------|
| `001`  | Preseason         |
| `002`  | Regular season    |
| `003`  | All-Star game     |
| `004`  | Playoffs          |

This matters because `get_game_ids()` returns raw IDs from the NBA Stats API, which can include preseason and All-Star games alongside regular season games depending on what the API returns for a given season and date range. All-Star games are particularly problematic because they produce non-standard team tricodes (`"WLD"`, `"STP"`, `"STR"`) that will break any logic expecting real team abbreviations.

**Always filter by prefix when you only want regular season games:**

```python
all_ids = await get_game_ids(client, "2025-26")
regular_season_ids = [gid for gid in all_ids if gid[:3] == "002"]
```

The same filter also excludes All-Star games, since those use the `"003"` prefix. Playoff IDs use `"004"` and are only present when `season_type="Playoffs"` is passed to `get_game_ids()`.

---

## Function reference

### `get_game_ids`

```python
async def get_game_ids(
    client: NBAClient,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
    team_id: int | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
) -> list[str]
```

Returns a sorted, deduplicated list of game ID strings for a season.

Internally uses the `LeagueGameLog` endpoint (team-level), which contains one row per team per game. Deduplication is applied before returning so each game appears exactly once. The NBA API's `TeamID` parameter on this endpoint is silently ignored server-side; team filtering is therefore applied client-side after fetching all rows.

**Parameters:**

| Parameter     | Type              | Default             | Description |
|---------------|-------------------|---------------------|-------------|
| `client`      | `NBAClient`       | required            | Active NBA client |
| `season`      | `Season \| None`  | current season      | Season in `YYYY-YY` format (e.g., `"2025-26"`). Defaults to the current season. |
| `season_type` | `SeasonType`      | `"Regular Season"`  | `"Regular Season"`, `"Playoffs"`, `"Pre Season"`, `"All-Star"` |
| `team_id`     | `int \| None`     | `None`              | Restrict to one team's games. Pass the integer team ID. |
| `date_from`   | `Date \| None`    | `None`              | Lower bound, inclusive. Format: `"MM/DD/YYYY"` |
| `date_to`     | `Date \| None`    | `None`              | Upper bound, inclusive. Format: `"MM/DD/YYYY"` |

**Returns:** `list[str]` — sorted list of 10-character game ID strings.

```python
# All regular-season game IDs for 2025-26
ids = await get_game_ids(client, "2025-26")

# Playoff games only
playoff_ids = await get_game_ids(client, "2025-26", season_type="Playoffs")

# One team's games
pacers_ids = await get_game_ids(client, "2025-26", team_id=1610612754)

# Date-range filter — January 2026 only
jan_ids = await get_game_ids(
    client,
    "2025-26",
    date_from="01/01/2026",
    date_to="01/31/2026",
)

# Combine team + date range
pacers_jan = await get_game_ids(
    client,
    "2025-26",
    team_id=1610612754,
    date_from="01/01/2026",
    date_to="01/31/2026",
)
```

---

### `get_games_on_date`

```python
async def get_games_on_date(
    client: NBAClient,
    game_date: ISODate,
) -> list[ScoreboardGame]
```

Returns all games scheduled on a specific date.

Uses the `ScoreboardV3` endpoint, which returns a nested JSON structure with live score data, period breakdowns, broadcaster information, and team/game leaders.

**Parameters:**

| Parameter   | Type        | Description |
|-------------|-------------|-------------|
| `client`    | `NBAClient` | Active NBA client |
| `game_date` | `str`       | Date in `YYYY-MM-DD` format (e.g., `"2025-01-15"`) |

**Returns:** `list[ScoreboardGame]` — one entry per game. Returns an empty list on off-days or if the API returns no scoreboard.

**Raises:** `ValueError` if `game_date` is not a valid `YYYY-MM-DD` date string.

```python
games = await get_games_on_date(client, "2025-01-15")
for game in games:
    away = game.away_team.team_tricode if game.away_team else "N/A"
    home = game.home_team.team_tricode if game.home_team else "N/A"
    print(f"{away} @ {home}  {game.game_status_text}")
```

---

### `get_todays_games`

```python
async def get_todays_games(client: NBAClient) -> list[ScoreboardGame]
```

Convenience wrapper that calls `get_games_on_date` with today's date. Equivalent to:

```python
await get_games_on_date(client, date.today().isoformat())
```

```python
games = await get_todays_games(client)
```

---

### `get_yesterdays_games`

```python
async def get_yesterdays_games(client: NBAClient) -> list[ScoreboardGame]
```

Convenience wrapper that calls `get_games_on_date` with yesterday's date.

```python
games = await get_yesterdays_games(client)
```

---

### `get_game_summary`

```python
async def get_game_summary(
    client: NBAClient,
    game_id: str,
) -> BoxScoreSummaryData
```

Returns full metadata for a single completed or in-progress game: arena, officials, attendance, broadcasters, last five meetings, and per-team summary statistics.

Uses the `BoxScoreSummary` endpoint.

**Parameters:**

| Parameter | Type        | Description |
|-----------|-------------|-------------|
| `client`  | `NBAClient` | Active NBA client |
| `game_id` | `str`       | 10-character NBA game ID string |

**Returns:** `BoxScoreSummaryData`

Key fields on `BoxScoreSummaryData`:

| Field              | Type              | Description |
|--------------------|-------------------|-------------|
| `gameId`           | `str`             | Game ID |
| `gameCode`         | `str`             | Human-readable code, e.g. `"20250115/BOSLAL"` |
| `gameStatus`       | `int`             | `1` = scheduled, `2` = in progress, `3` = final |
| `gameStatusText`   | `str`             | `"Final"`, `"Q3 4:32"`, etc. |
| `period`           | `int`             | Current period |
| `gameClock`        | `str`             | Remaining time in current period |
| `gameTimeUTC`      | `str`             | ISO 8601 tip-off time in UTC |
| `gameEt`           | `str`             | Tip-off time in Eastern Time |
| `awayTeamId`       | `int`             | Away team ID |
| `homeTeamId`       | `int`             | Home team ID |
| `duration`         | `str`             | Game duration string |
| `attendance`       | `int`             | Attendance count |
| `sellout`          | `int`             | `1` if sold out |
| `arena`            | `Arena`           | Arena name, city, state, country |
| `officials`        | `list[Official]`  | Referee roster |
| `broadcasters`     | `Broadcasters`    | National and local broadcaster info |
| `homeTeam`         | `SummaryTeam`     | Home team summary with record and score |
| `awayTeam`         | `SummaryTeam`     | Away team summary with record and score |
| `lastFiveMeetings` | `LastFiveMeetings`| Results of the last 5 head-to-head matchups |

```python
summary = await get_game_summary(client, "0022500571")
print(f"Arena:      {summary.arena.arenaName}, {summary.arena.arenaCity}")
print(f"Attendance: {summary.attendance:,}")
officials = ", ".join(o.name for o in summary.officials)
print(f"Officials:  {officials}")
```

---

### `get_box_scores`

```python
async def get_box_scores(
    client: NBAClient,
    game_ids: list[str],
) -> dict[str, BoxScoreTraditionalData]
```

Fetches traditional box scores for multiple games concurrently using `client.get_many()`. Returns a dict mapping each game ID to its `BoxScoreTraditionalData`.

**Parameters:**

| Parameter  | Type        | Description |
|------------|-------------|-------------|
| `client`   | `NBAClient` | Active NBA client |
| `game_ids` | `list[str]` | List of 10-character game ID strings |

**Returns:** `dict[str, BoxScoreTraditionalData]` — keys are game IDs in the same order as `game_ids`. Returns an empty dict if `game_ids` is empty.

**Note:** Raises `ExceptionGroup` if any individual request fails (this is propagated from `get_many()`).

Key fields on `BoxScoreTraditionalData`:

| Field        | Type                  | Description |
|--------------|-----------------------|-------------|
| `gameId`     | `str`                 | Game ID |
| `homeTeamId` | `int`                 | Home team ID |
| `awayTeamId` | `int`                 | Away team ID |
| `homeTeam`   | `TraditionalTeam`     | Home team with players and statistics |
| `awayTeam`   | `TraditionalTeam`     | Away team with players and statistics |

Key fields on `TraditionalTeam`:

| Field         | Type                         | Description |
|---------------|------------------------------|-------------|
| `teamId`      | `int`                        | Team ID |
| `teamCity`    | `str \| None`                | City name |
| `teamName`    | `str \| None`                | Franchise name |
| `teamTricode` | `str \| None`                | 3-letter abbreviation |
| `players`     | `list[TraditionalPlayer]`    | All rostered players |
| `statistics`  | `TraditionalStatistics`      | Aggregated team stats |
| `starters`    | `TraditionalGroupStatistics \| None` | Starters-only aggregate |
| `bench`       | `TraditionalGroupStatistics \| None` | Bench-only aggregate |

Key fields on `TraditionalStatistics` — `TraditionalGroupStatistics` (`starters`/`bench`) has all fields below except `plusMinusPoints`:

| Field                     | Type    | Description |
|---------------------------|---------|-------------|
| `points`                  | `int`   | Total points |
| `fieldGoalsMade`          | `int`   | FGM |
| `fieldGoalsAttempted`     | `int`   | FGA |
| `fieldGoalsPercentage`    | `float` | FG% (0.0–1.0) |
| `threePointersMade`       | `int`   | 3PM |
| `threePointersAttempted`  | `int`   | 3PA |
| `threePointersPercentage` | `float` | 3P% (0.0–1.0) |
| `freeThrowsMade`          | `int`   | FTM |
| `freeThrowsAttempted`     | `int`   | FTA |
| `freeThrowsPercentage`    | `float` | FT% (0.0–1.0) |
| `reboundsOffensive`       | `int`   | Offensive rebounds |
| `reboundsDefensive`       | `int`   | Defensive rebounds |
| `reboundsTotal`           | `int`   | Total rebounds |
| `assists`                 | `int`   | Assists |
| `steals`                  | `int`   | Steals |
| `blocks`                  | `int`   | Blocks |
| `turnovers`               | `int`   | Turnovers |
| `foulsPersonal`           | `int`   | Personal fouls |
| `plusMinusPoints`         | `float` | Plus/minus (player or team) |
| `minutes`                 | `str`   | Minutes played as a duration string |

```python
box_scores = await get_box_scores(client, ["0022500571", "0022500572"])
for game_id, bs in box_scores.items():
    away = bs.awayTeam
    home = bs.homeTeam
    print(
        f"{away.teamTricode} @ {home.teamTricode}: "
        f"{away.statistics.points} - {home.statistics.points}"
    )
```

---

### `get_play_by_play`

```python
async def get_play_by_play(
    client: NBAClient,
    game_id: str,
) -> list[PlayByPlayAction]
```

Returns all play-by-play actions for a game in chronological order (by `actionNumber`).

Uses the `PlayByPlay` endpoint. Returns the `actions` list directly from the response's `game` object.

**Parameters:**

| Parameter | Type        | Description |
|-----------|-------------|-------------|
| `client`  | `NBAClient` | Active NBA client |
| `game_id` | `str`       | 10-character NBA game ID string |

**Returns:** `list[PlayByPlayAction]`

Key fields on `PlayByPlayAction`:

| Field          | Type    | Description |
|----------------|---------|-------------|
| `actionNumber` | `int`   | Sequential action index (chronological) |
| `actionId`     | `int`   | Unique action identifier |
| `actionType`   | `str`   | Category: `"2pt"`, `"3pt"`, `"freethrow"`, `"turnover"`, `"foul"`, `"rebound"`, `"substitution"`, etc. |
| `subType`      | `str`   | Sub-category: `"jump shot"`, `"layup"`, `"dunk"`, `"offensive"`, etc. |
| `period`       | `int`   | Period number (`1`–`4`, then `5`+ for overtime) |
| `clock`        | `str`   | Remaining time in period as ISO 8601 duration, e.g. `"PT04M32.00S"` |
| `description`  | `str`   | Human-readable play description |
| `teamId`       | `int`   | Team ID of the player involved |
| `teamTricode`  | `str`   | 3-letter team abbreviation |
| `personId`     | `int`   | Player ID (`0` for team events) |
| `playerName`   | `str`   | Full player name |
| `playerNameI`  | `str`   | Abbreviated name, e.g. `"L. James"` |
| `shotResult`   | `str`   | `"Made"`, `"Missed"`, or `""` for non-shot actions |
| `isFieldGoal`  | `int`   | `1` if this action is a field goal attempt, otherwise `0` |
| `shotDistance` | `int`   | Distance in feet from the basket |
| `shotValue`    | `int`   | Point value of the shot (`2`, `3`, or `0`) |
| `xLegacy`      | `int`   | X coordinate on the court (shot location) |
| `yLegacy`      | `int`   | Y coordinate on the court (shot location) |
| `scoreHome`    | `str`   | Home team score after this action |
| `scoreAway`    | `str`   | Away team score after this action |
| `pointsTotal`  | `int`   | Total points scored on this action |
| `location`     | `str`   | `"H"` (home), `"A"` (away), or `""` |
| `videoAvailable` | `int` | `1` if video footage is available |

```python
actions = await get_play_by_play(client, "0022500571")

# All fourth-quarter actions
fourth_quarter = [a for a in actions if a.period == 4]

# Made field goals only
made_shots = [a for a in actions if a.shotResult == "Made"]

# Three-point attempts
threes = [a for a in actions if a.actionType == "3pt"]

# Last 5 scoring plays of the game
scoring = [a for a in actions if a.shotResult == "Made"]
for action in scoring[-5:]:
    print(f"Q{action.period} {action.clock}  {action.description}")
```

---

## ScoreboardGame fields

`ScoreboardGame` is returned by `get_games_on_date()`, `get_todays_games()`, and `get_yesterdays_games()`. All fields are optional (`... | None`) because the API may omit values for games that have not yet started or for which data is unavailable.

| Field                | Type                       | Description |
|----------------------|----------------------------|-------------|
| `game_id`            | `str \| None`              | 10-character game ID |
| `game_code`          | `str \| None`              | Human-readable code, e.g. `"20250115/BOSLAL"` |
| `game_status`        | `int \| None`              | `1` = scheduled, `2` = in progress, `3` = final |
| `game_status_text`   | `str \| None`              | `"7:30 pm ET"`, `"Q3 4:32"`, `"Final"`, etc. |
| `period`             | `int \| None`              | Current period (0 if not started) |
| `game_clock`         | `str \| None`              | Remaining time in current period |
| `game_time_utc`      | `str \| None`              | ISO 8601 tip-off time in UTC |
| `game_et`            | `str \| None`              | Tip-off time in Eastern Time |
| `regulation_periods` | `int \| None`              | Number of regulation periods (typically `4`) |
| `home_team`          | `ScoreboardTeam \| None`   | Home team info and current score |
| `away_team`          | `ScoreboardTeam \| None`   | Away team info and current score |
| `game_leaders`       | `GameLeaders \| None`      | Top performers in this game (pts/reb/ast) |
| `team_leaders`       | `TeamLeaders \| None`      | Season scoring/rebounding/assist leaders for each team |
| `broadcasters`       | `ScoreboardBroadcasters \| None` | National and local broadcast info |
| `series_game_number` | `str \| None`              | Playoff series game number, e.g. `"Game 3"` |
| `series_text`        | `str \| None`              | Playoff series record, e.g. `"LAL leads 2-1"` |
| `game_label`         | `str \| None`              | Special label (e.g., `"Christmas"`) |
| `if_necessary`       | `bool \| None`             | `True` for a playoff game that may not be played |
| `is_neutral`         | `bool \| None`             | `True` for neutral-site games |

`ScoreboardTeam` (accessed via `game.home_team` or `game.away_team`):

| Field               | Type              | Description |
|---------------------|-------------------|-------------|
| `team_id`           | `int \| None`     | Team ID |
| `team_name`         | `str \| None`     | Franchise name, e.g. `"Lakers"` |
| `team_city`         | `str \| None`     | City, e.g. `"Los Angeles"` |
| `team_tricode`      | `str \| None`     | 3-letter abbreviation, e.g. `"LAL"` |
| `team_slug`         | `str \| None`     | URL slug, e.g. `"lakers"` |
| `wins`              | `int \| None`     | Season wins at time of game |
| `losses`            | `int \| None`     | Season losses at time of game |
| `score`             | `int \| None`     | Current or final score |
| `seed`              | `int \| None`     | Playoff seed |
| `in_bonus`          | `str \| None`     | Whether team is in the bonus |
| `timeouts_remaining`| `int \| None`     | Remaining timeouts |
| `periods`           | `list[PeriodScore]` | Per-period scoring breakdown |

---

## Common patterns

### Scoreboard to box scores

Fetch yesterday's final scores and then pull full box scores for all games:

```python
from fastbreak.clients import NBAClient
from fastbreak.games import get_box_scores, get_yesterdays_games

async def main() -> None:
    async with NBAClient() as client:
        games = await get_yesterdays_games(client)
        game_ids = [g.game_id for g in games if g.game_id]
        box_scores = await get_box_scores(client, game_ids)

        for game_id, bs in box_scores.items():
            away = bs.awayTeam
            home = bs.homeTeam
            print(
                f"{away.teamTricode} @ {home.teamTricode}: "
                f"{away.statistics.points} - {home.statistics.points}"
            )
```

### Filter to regular season only

`get_game_ids()` may include All-Star games (`003`) if they fall within the date range for a regular season request. Always filter by prefix:

```python
all_ids = await get_game_ids(client, "2025-26")
regular_season_ids = [gid for gid in all_ids if gid[:3] == "002"]
```

### Play-by-play analysis

```python
actions = await get_play_by_play(client, "0022500571")

# Filter to a specific period
fourth_quarter = [a for a in actions if a.period == 4]

# All made shots
made_shots = [a for a in actions if a.shotResult == "Made"]

# All three-point attempts
threes = [a for a in actions if a.actionType == "3pt"]
made_threes = [a for a in threes if a.shotResult == "Made"]
print(f"3PT: {len(made_threes)}/{len(threes)}")
```

### Display today's schedule with tip-off times

```python
from datetime import datetime
from fastbreak.games import get_todays_games

games = await get_todays_games(client)
for game in games:
    away = game.away_team.team_tricode if game.away_team else "N/A"
    home = game.home_team.team_tricode if game.home_team else "N/A"
    if game.game_time_utc:
        local = datetime.fromisoformat(game.game_time_utc).astimezone(tz=None)
        tip = local.strftime("%I:%M %p %Z")
    else:
        tip = game.game_status_text or "TBD"
    print(f"{away} @ {home}  {tip}")
```

---

## Complete examples

### Example 1: Today's and yesterday's scores with a game summary

```python
"""Display today's schedule, yesterday's results, and one game summary."""

import asyncio
from datetime import datetime

from fastbreak.clients import NBAClient
from fastbreak.games import get_game_summary, get_todays_games, get_yesterdays_games


async def main() -> None:
    async with NBAClient() as client:
        # ── Today's schedule ────────────────────────────────────────
        print("Today's games")
        print("-" * 40)
        games = await get_todays_games(client)
        if not games:
            print("  No games scheduled today.")
        else:
            for game in games:
                away = game.away_team.team_tricode if game.away_team else "N/A"
                home = game.home_team.team_tricode if game.home_team else "N/A"
                if game.game_time_utc:
                    local = datetime.fromisoformat(game.game_time_utc).astimezone(tz=None)
                    tip = local.strftime("%I:%M %p %Z")
                else:
                    tip = game.game_status_text or "TBD"
                print(f"  {away} @ {home}  {tip}")
        print()

        # ── Yesterday's results ──────────────────────────────────────
        print("Yesterday's results")
        print("-" * 40)
        yesterday = await get_yesterdays_games(client)
        if not yesterday:
            print("  No games yesterday.")
        else:
            for game in yesterday:
                away = game.away_team.team_tricode if game.away_team else "N/A"
                home = game.home_team.team_tricode if game.home_team else "N/A"
                away_score = game.away_team.score if game.away_team else None
                home_score = game.home_team.score if game.home_team else None
                status = game.game_status_text or "Final"
                if away_score is not None and home_score is not None:
                    print(f"  {away} {away_score}  {home} {home_score}  [{status}]")
                else:
                    print(f"  {away} @ {home}  {status}")
        print()

        # ── Game summary (arena, officials, attendance) ──────────────
        game_ids = [g.game_id for g in yesterday if g.game_id]
        if game_ids:
            print("Game summary — first game from yesterday")
            print("-" * 40)
            summary = await get_game_summary(client, game_ids[0])
            away = summary.awayTeam.teamTricode if summary.awayTeam else "N/A"
            home = summary.homeTeam.teamTricode if summary.homeTeam else "N/A"
            print(f"  Matchup:    {away} @ {home}")
            print(f"  Status:     {summary.gameStatusText}")
            print(f"  Arena:      {summary.arena.arenaName}, {summary.arena.arenaCity}")
            print(f"  Attendance: {summary.attendance:,}")
            names = ", ".join(o.name for o in summary.officials)
            print(f"  Officials:  {names}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Season game IDs and batch box scores

```python
"""Fetch all regular-season game IDs and retrieve box scores in batch."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import get_box_scores, get_game_ids


async def main() -> None:
    async with NBAClient(request_delay=0.6) as client:
        # Fetch all regular-season IDs for 2025-26
        all_ids = await get_game_ids(client, "2025-26")
        regular = [gid for gid in all_ids if gid[:3] == "002"]
        print(f"Total regular season games: {len(regular)}")

        # Pull box scores for the first 10 games
        sample_ids = regular[:10]
        print(f"\nFetching box scores for {len(sample_ids)} games...")
        box_scores = await get_box_scores(client, sample_ids)

        print()
        for game_id, bs in box_scores.items():
            away = bs.awayTeam
            home = bs.homeTeam
            a_pts = away.statistics.points
            h_pts = home.statistics.points
            winner = away.teamTricode if a_pts > h_pts else home.teamTricode
            print(
                f"  [{game_id}]  "
                f"{away.teamTricode} {a_pts} @ {home.teamTricode} {h_pts}"
                f"  ({winner} wins)"
            )


if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Play-by-play breakdown

```python
"""Analyze play-by-play data for yesterday's first game."""

import asyncio
from collections import Counter
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.games import get_games_on_date, get_play_by_play


async def main() -> None:
    async with NBAClient() as client:
        yesterday = (
            datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
        ).isoformat()

        games = await get_games_on_date(client, yesterday)
        if not games:
            print(f"No games on {yesterday}.")
            return

        game = games[0]
        if not game.game_id:
            print("Game ID unavailable.")
            return

        away = game.away_team.team_tricode if game.away_team else "AWY"
        home = game.home_team.team_tricode if game.home_team else "HME"
        print(f"Play-by-play: {away} @ {home}  ({yesterday})")
        print("-" * 50)

        actions = await get_play_by_play(client, game.game_id)
        print(f"Total actions: {len(actions)}")

        # Action type breakdown
        type_counts: Counter[str] = Counter(
            a.actionType for a in actions if a.actionType
        )
        print("\nTop action types:")
        for action_type, count in type_counts.most_common(8):
            print(f"  {action_type:<22} {count:4}")

        # Three-point shooting
        threes = [a for a in actions if a.actionType == "3pt"]
        made_threes = [a for a in threes if a.shotResult == "Made"]
        print(f"\n3PT: {len(made_threes)}/{len(threes)}")

        # Fourth-quarter scoring plays
        q4_made = [
            a for a in actions if a.period == 4 and a.shotResult == "Made"
        ]
        print(f"\n4th-quarter made shots: {len(q4_made)}")
        print("\nLast 5 scoring plays:")
        scoring = [a for a in actions if a.shotResult == "Made"]
        for action in scoring[-5:]:
            print(
                f"  Q{action.period} {action.clock:<18} "
                f"{action.teamTricode}  {action.description}"
            )


if __name__ == "__main__":
    asyncio.run(main())
```

### Example 4: Team schedule with date filtering

```python
"""List a team's games within a specific month using get_game_ids."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import get_game_ids, get_game_summary
from fastbreak.teams import get_team_id


async def main() -> None:
    team_id = get_team_id("BOS")
    if team_id is None:
        print("Team not found.")
        return

    async with NBAClient() as client:
        ids = await get_game_ids(
            client,
            "2025-26",
            team_id=team_id,
            date_from="01/01/2026",
            date_to="01/31/2026",
        )

        print(f"Celtics games in January 2026: {len(ids)}")
        for game_id in ids:
            summary = await get_game_summary(client, game_id)
            away = summary.awayTeam.teamTricode if summary.awayTeam else "N/A"
            home = summary.homeTeam.teamTricode if summary.homeTeam else "N/A"
            away_score = summary.awayTeam.score if summary.awayTeam else "?"
            home_score = summary.homeTeam.score if summary.homeTeam else "?"
            print(
                f"  [{game_id}]  {away} {away_score} @ {home} {home_score}"
                f"  {summary.gameStatusText}"
            )


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Notes and gotchas

**All-Star game tricodes.** All-Star games (`003` prefix) use non-standard team tricodes such as `"WLD"`, `"STP"`, and `"STR"`. Any code that maps tricodes to real teams will fail on these IDs. Filter them out with `gid[:3] == "002"` before processing.

**`get_game_ids` default season.** When `season=None`, the current season is derived from today's date using `get_season_from_date()`. This means the result changes automatically as the season progresses, which is useful for always-current dashboards but can cause unexpected results in scripts that run across a season boundary.

**`get_box_scores` returns a dict, not a list.** Unlike a hypothetical list return, the dict makes it straightforward to look up a specific game's data by ID without iterating.

**`get_play_by_play` returns actions directly.** The function returns `list[PlayByPlayAction]`, not the full `PlayByPlayResponse`. If you need the `gameId` or `videoAvailable` flag from the response envelope, use the endpoint directly:

```python
from fastbreak.endpoints import PlayByPlay

response = await client.get(PlayByPlay(game_id="0022500571"))
game = response.game       # PlayByPlayGame
actions = game.actions     # list[PlayByPlayAction]
```

**`game_status` integer values.** On `ScoreboardGame`, `game_status` uses integer codes: `1` = scheduled, `2` = in progress, `3` = final. On `BoxScoreSummaryData`, the equivalent field is `gameStatus` (camelCase, no alias). `game_status_text` / `gameStatusText` provides a human-readable equivalent.

**Period clock format.** `PlayByPlayAction.clock` is an ISO 8601 duration string (e.g., `"PT04M32.00S"`), not a plain `"4:32"` string. Parse it with the standard library if you need arithmetic:

```python
import re

def parse_clock(clock: str) -> float:
    """Return remaining seconds from an ISO 8601 clock string."""
    m = re.match(r"PT(\d+)M([\d.]+)S", clock)
    if not m:
        return 0.0
    return int(m.group(1)) * 60 + float(m.group(2))
```

**Empty lists on off-days.** `get_games_on_date()` returns `[]` when there are no games, including during the off-season. Always guard against empty lists before indexing.
