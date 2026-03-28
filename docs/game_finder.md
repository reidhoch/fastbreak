# fastbreak.game_finder

Search for games by team or player with rich filtering, then analyze results with pure computation helpers. Wraps the `LeagueGameFinder` endpoint.

The module provides two async search functions (`find_team_games`, `find_player_games`) and three pure helpers (`aggregate_games`, `streak_games`, `summarize_record`):

```python
from fastbreak.game_finder import (
    find_team_games,
    find_player_games,
    aggregate_games,
    streak_games,
    summarize_record,
    GameAverages,
    Record,
)
```

---

## Function reference

### `find_team_games`

```python
async def find_team_games(
    client: NBAClient,
    team_id: int,
    *,
    vs_team_id: int | None = None,
    season: Season | None = None,
    season_type: SeasonType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    outcome: Outcome | None = None,
    location: Location | None = None,
    gt_pts: int | None = None,
    gt_reb: int | None = None,
    gt_ast: int | None = None,
    gt_stl: int | None = None,
    gt_blk: int | None = None,
) -> list[GameFinderResult]
```

Find games for a team matching the given filters. All ID and threshold parameters accept `int` and are converted to `str` internally.

**Parameters:**

| Parameter     | Type                | Default    | Description |
|---------------|---------------------|------------|-------------|
| `client`      | `NBAClient`         | required   | Active NBA client |
| `team_id`     | `int`               | required   | Team ID to search for |
| `vs_team_id`  | `int \| None`       | `None`     | Filter by opponent team ID |
| `season`      | `Season \| None`    | `None`     | Season in `YYYY-YY` format |
| `season_type` | `SeasonType \| None`| `None`     | `"Regular Season"`, `"Playoffs"`, etc. |
| `date_from`   | `Date \| None`      | `None`     | Start date `"MM/DD/YYYY"` |
| `date_to`     | `Date \| None`      | `None`     | End date `"MM/DD/YYYY"` |
| `outcome`     | `Outcome \| None`   | `None`     | `"W"` or `"L"` |
| `location`    | `Location \| None`  | `None`     | `"Home"` or `"Road"` |
| `gt_pts`      | `int \| None`       | `None`     | Minimum points threshold |
| `gt_reb`      | `int \| None`       | `None`     | Minimum rebounds threshold |
| `gt_ast`      | `int \| None`       | `None`     | Minimum assists threshold |
| `gt_stl`      | `int \| None`       | `None`     | Minimum steals threshold |
| `gt_blk`      | `int \| None`       | `None`     | Minimum blocks threshold |

**Returns:** `list[GameFinderResult]` — games matching the criteria, each with full box score stats.

**Examples:**

```python
# All Celtics home wins this season
games = await find_team_games(
    client, team_id=1610612738, season="2025-26", outcome="W", location="Home"
)

# Celtics vs Lakers games where they scored 110+
games = await find_team_games(
    client, team_id=1610612738, vs_team_id=1610612747, gt_pts=110
)
```

---

### `find_player_games`

```python
async def find_player_games(
    client: NBAClient,
    player_id: int,
    *,
    team_id: int | None = None,
    vs_team_id: int | None = None,
    season: Season | None = None,
    season_type: SeasonType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    outcome: Outcome | None = None,
    location: Location | None = None,
    gt_pts: int | None = None,
    gt_reb: int | None = None,
    gt_ast: int | None = None,
    gt_stl: int | None = None,
    gt_blk: int | None = None,
) -> list[GameFinderResult]
```

Find games for a player matching the given filters. Same parameters as `find_team_games` but with `player_id` as the required positional argument and `team_id` as an optional keyword filter.

**Parameters:**

| Parameter     | Type                | Default    | Description |
|---------------|---------------------|------------|-------------|
| `client`      | `NBAClient`         | required   | Active NBA client |
| `player_id`   | `int`               | required   | Player ID to search for |
| `team_id`     | `int \| None`       | `None`     | Filter by team ID |
| `vs_team_id`  | `int \| None`       | `None`     | Filter by opponent team ID |
| `season`      | `Season \| None`    | `None`     | Season in `YYYY-YY` format |
| `season_type` | `SeasonType \| None`| `None`     | `"Regular Season"`, `"Playoffs"`, etc. |
| `date_from`   | `Date \| None`      | `None`     | Start date `"MM/DD/YYYY"` |
| `date_to`     | `Date \| None`      | `None`     | End date `"MM/DD/YYYY"` |
| `outcome`     | `Outcome \| None`   | `None`     | `"W"` or `"L"` |
| `location`    | `Location \| None`  | `None`     | `"Home"` or `"Road"` |
| `gt_pts`      | `int \| None`       | `None`     | Minimum points threshold |
| `gt_reb`      | `int \| None`       | `None`     | Minimum rebounds threshold |
| `gt_ast`      | `int \| None`       | `None`     | Minimum assists threshold |
| `gt_stl`      | `int \| None`       | `None`     | Minimum steals threshold |
| `gt_blk`      | `int \| None`       | `None`     | Minimum blocks threshold |

**Returns:** `list[GameFinderResult]` — player-level game results matching the criteria.

**Examples:**

```python
# Curry's 30+ point games this season
games = await find_player_games(
    client, player_id=201939, season="2025-26", gt_pts=30
)

# Tatum's road games vs the Heat
games = await find_player_games(
    client, player_id=1628369, vs_team_id=1610612748, location="Road"
)
```

---

### `aggregate_games`

```python
def aggregate_games(games: list[GameFinderResult]) -> GameAverages
```

Compute average stats across a list of games. Counting stats are always averaged. Percentage fields and `plus_minus` are averaged from non-None values only — if all values are `None`, the result is `None`.

**Parameters:**

| Parameter | Type                     | Description |
|-----------|--------------------------|-------------|
| `games`   | `list[GameFinderResult]` | Games to aggregate |

**Returns:** `GameAverages` — frozen dataclass with averaged stats.

**Examples:**

```python
games = await find_team_games(client, team_id=1610612738, season="2025-26")
avgs = aggregate_games(games)
print(f"PPG: {avgs.pts:.1f}, RPG: {avgs.reb:.1f}, APG: {avgs.ast:.1f}")
```

---

### `streak_games`

```python
def streak_games(games: list[GameFinderResult]) -> list[list[GameFinderResult]]
```

Group consecutive games into win/loss streaks. Games with `wl=None` are excluded and break the current streak. Adjacent streaks always have different `wl` values.

**Parameters:**

| Parameter | Type                     | Description |
|-----------|--------------------------|-------------|
| `games`   | `list[GameFinderResult]` | Games in chronological order |

**Returns:** `list[list[GameFinderResult]]` — list of streaks, each a list of consecutive same-`wl` games.

**Examples:**

```python
games = await find_team_games(client, team_id=1610612747, season="2025-26")
streaks = streak_games(games)
for streak in streaks:
    print(f"{'W' if streak[0].wl == 'W' else 'L'} streak: {len(streak)} games")
```

---

### `summarize_record`

```python
def summarize_record(games: list[GameFinderResult]) -> Record
```

Compute the win-loss record from a list of games. Games with `wl=None` are excluded.

**Parameters:**

| Parameter | Type                     | Description |
|-----------|--------------------------|-------------|
| `games`   | `list[GameFinderResult]` | Games to summarize |

**Returns:** `Record` — frozen dataclass with `wins`, `losses`, and `win_pct`.

**Examples:**

```python
games = await find_team_games(
    client, team_id=1610612738, season="2025-26", location="Road"
)
record = summarize_record(games)
print(f"Road record: {record.wins}-{record.losses} ({record.win_pct:.3f})")
```

---

## Dataclass reference

### `GameAverages`

Frozen dataclass returned by `aggregate_games()`.

| Field        | Type            | Description |
|--------------|-----------------|-------------|
| `pts`        | `float`         | Average points |
| `reb`        | `float`         | Average rebounds |
| `ast`        | `float`         | Average assists |
| `stl`        | `float`         | Average steals |
| `blk`        | `float`         | Average blocks |
| `tov`        | `float`         | Average turnovers |
| `fg_pct`     | `float \| None` | Average FG%, None if all games have None |
| `fg3_pct`    | `float \| None` | Average 3P%, None if all games have None |
| `ft_pct`     | `float \| None` | Average FT%, None if all games have None |
| `plus_minus` | `float \| None` | Average plus/minus, None if all games have None |

### `Record`

Frozen dataclass returned by `summarize_record()`.

| Field     | Type    | Description |
|-----------|---------|-------------|
| `wins`    | `int`   | Number of wins |
| `losses`  | `int`   | Number of losses |
| `win_pct` | `float` | Win percentage (0.0–1.0), 0.0 for empty input |

---

## `GameFinderResult` field reference

Each result in the list returned by `find_team_games` / `find_player_games` has these fields:

| Field                | Type            | Description |
|----------------------|-----------------|-------------|
| `season_id`          | `str`           | Season identifier (e.g., `"22025"`) |
| `team_id`            | `int \| None`   | Team ID |
| `team_abbreviation`  | `str \| None`   | Team abbreviation (e.g., `"BOS"`) |
| `team_name`          | `str \| None`   | Team name (e.g., `"Boston Celtics"`) |
| `game_id`            | `str`           | 10-character game ID |
| `game_date`          | `str`           | Game date string |
| `matchup`            | `str \| None`   | Matchup string (e.g., `"BOS vs. LAL"`) |
| `wl`                 | `str \| None`   | `"W"` or `"L"`, None for in-progress |
| `min`                | `int`           | Minutes played |
| `pts`                | `int`           | Points |
| `fgm`                | `int`           | Field goals made |
| `fga`                | `int`           | Field goals attempted |
| `fg_pct`             | `float \| None` | Field goal percentage |
| `fg3m`               | `int`           | Three-pointers made |
| `fg3a`               | `int`           | Three-pointers attempted |
| `fg3_pct`            | `float \| None` | Three-point percentage |
| `ftm`                | `int`           | Free throws made |
| `fta`                | `int`           | Free throws attempted |
| `ft_pct`             | `float \| None` | Free throw percentage |
| `oreb`               | `int`           | Offensive rebounds |
| `dreb`               | `int`           | Defensive rebounds |
| `reb`                | `int`           | Total rebounds |
| `ast`                | `int`           | Assists |
| `stl`                | `int`           | Steals |
| `blk`                | `int`           | Blocks |
| `tov`                | `int`           | Turnovers |
| `pf`                 | `int`           | Personal fouls |
| `plus_minus`         | `float \| None` | Plus/minus rating |

`GameFinderResult` includes `PandasMixin` and `PolarsMixin` — call `GameFinderResult.to_pandas(games)` or `GameFinderResult.to_polars(games)` to convert a list to a DataFrame.

---

## Common patterns

**Build a training dataset for a matchup model:**

```python
# All Celtics vs top Eastern rivals
rivals = [1610612748, 1610612749, 1610612755]  # MIA, MIL, PHI
from fastbreak.game_finder import find_team_games

games = []
for rival_id in rivals:
    rival_games = await find_team_games(
        client, team_id=1610612738, vs_team_id=rival_id, season="2025-26"
    )
    games.extend(rival_games)
```

**Compare home vs road performance:**

```python
home = await find_team_games(client, team_id=1610612747, season="2025-26", location="Home")
road = await find_team_games(client, team_id=1610612747, season="2025-26", location="Road")
home_avgs = aggregate_games(home)
road_avgs = aggregate_games(road)
print(f"Home PPG: {home_avgs.pts:.1f} vs Road PPG: {road_avgs.pts:.1f}")
```

**Find a player's longest win streak:**

```python
games = await find_player_games(client, player_id=1628369, season="2025-26")
streaks = streak_games(games)
win_streaks = [s for s in streaks if s[0].wl == "W"]
if win_streaks:
    longest = max(win_streaks, key=len)
    print(f"Longest W streak: {len(longest)} games")
```

---

## Complete example

```python
"""Team season analysis with game finder."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.game_finder import (
    aggregate_games,
    find_team_games,
    streak_games,
    summarize_record,
)


async def main() -> None:
    async with NBAClient() as client:
        team_id = 1610612738  # Celtics

        # Fetch all games this season
        games = await find_team_games(client, team_id=team_id, season="2025-26")
        if not games:
            print("No games found.")
            return

        # Record
        record = summarize_record(games)
        print(f"Record: {record.wins}-{record.losses} ({record.win_pct:.3f})")

        # Averages
        avgs = aggregate_games(games)
        print(f"PPG: {avgs.pts:.1f}  RPG: {avgs.reb:.1f}  APG: {avgs.ast:.1f}")

        # Streaks
        streaks = streak_games(games)
        if streaks:
            longest = max(streaks, key=len)
            print(f"Current: {streaks[-1][0].wl} streak ({len(streaks[-1])} games)")
            print(f"Longest: {longest[0].wl} streak ({len(longest)} games)")


if __name__ == "__main__":
    asyncio.run(main())
```
