# lineups — League-Wide Lineup Analysis

Analyze lineup combinations across the entire NBA. Wraps `LeagueDashLineups` (box score
stats for lineup groups) and `LeagueLineupViz` (efficiency ratings, pace, shot distribution).

Complements the team-scoped helpers in `fastbreak.teams`:
- `teams.get_lineup_stats` → single team, wraps `TeamDashLineups`
- `teams.get_lineup_net_ratings` → single team net rating calc
- **`lineups.*`** → league-wide, supports team filtering, wraps different endpoints

## Quick Start

```python
from fastbreak.clients import NBAClient
from fastbreak.lineups import (
    get_league_lineups,
    get_lineup_efficiency,
    get_top_lineups,
    get_two_man_combos,
    lineup_net_rating,
    rank_lineups,
)

async with NBAClient() as client:
    # Top 10 five-man lineups for the Lakers by plus/minus
    top = await get_top_lineups(client, 1610612747, top_n=10, min_minutes=10.0)

    # Lakers lineup efficiency (sorted by net rating)
    best = await get_lineup_efficiency(client, team_id=1610612747, top_n=5)

    # Two-man combos for a specific team
    combos = await get_two_man_combos(client, team_id=1610612747)
    ranked = rank_lineups(combos, min_minutes=5.0, by="plus_minus")
```

## API Reference

### Raw Access

#### `get_league_lineups`

```python
async def get_league_lineups(
    client: NBAClient,
    team_id: int,                # required — API rejects team_id=0
    *,
    group_quantity: int = 5,     # 2-5 players per lineup
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    measure_type: MeasureType = "Base",
) -> list[LeagueLineup]
```

Lineup combination statistics for a team. Wraps `LeagueDashLineups`. A specific `team_id`
is required — the NBA API returns 500 if `team_id=0` is passed.

#### `get_league_lineup_ratings`

```python
async def get_league_lineup_ratings(
    client: NBAClient,
    *,
    team_id: int = 0,
    group_quantity: int = 5,
    minutes_min: int = 10,       # server-side minimum minutes filter
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "Totals",
) -> list[LineupViz]
```

Lineup efficiency ratings. Returns offensive/defensive ratings, pace, shot distribution,
and opponent defense stats. Wraps `LeagueLineupViz`.

### Profile Builders

#### `get_top_lineups`

```python
async def get_top_lineups(
    client: NBAClient,
    team_id: int,                # required — positional
    *,
    group_quantity: int = 5,
    min_minutes: float = 10.0,
    top_n: int = 10,
    by: Literal["min", "pts", "plus_minus", "w_pct", "fg_pct"] = "plus_minus",
    ascending: bool = False,
    season: Season | None = None,
    ...
) -> list[LeagueLineup]
```

Top N lineups for a team by any stat. Fetches, filters by minutes, sorts, and trims.

#### `get_two_man_combos`

```python
async def get_two_man_combos(
    client: NBAClient,
    team_id: int,                # required — positional
    *,
    season: Season | None = None,
    ...
) -> list[LeagueLineup]
```

Convenience wrapper: sets `group_quantity=2` and requires a `team_id`.

#### `get_lineup_efficiency`

```python
async def get_lineup_efficiency(
    client: NBAClient,
    *,
    team_id: int = 0,
    group_quantity: int = 5,
    minutes_min: int = 10,
    top_n: int | None = None,
    season: Season | None = None,
    ...
) -> list[LineupViz]
```

Lineups sorted by net rating (best first). Optionally caps at `top_n`.

### Computation Helpers

#### `lineup_net_rating`

```python
def lineup_net_rating(off_rating: float, def_rating: float) -> float
```

Returns `off_rating - def_rating`. Positive = outscoring opponents.

#### `rank_lineups`

```python
def rank_lineups(
    lineups: list[LeagueLineup],
    *,
    min_minutes: float = 10.0,
    by: Literal["min", "pts", "plus_minus", "w_pct", "fg_pct"] = "plus_minus",
    ascending: bool = False,
) -> list[LeagueLineup]
```

Filter by volume and sort. Lineups with `None` FG% are excluded when sorting by `fg_pct`.

## Data Types

### `LeagueLineup` (from `LeagueDashLineups`)

| Field | Type | Description |
|-------|------|-------------|
| `group_name` | `str` | Player names joined by " - " |
| `team_abbreviation` | `str` | Team tricode (e.g., "LAL") |
| `gp` | `int` | Games played together |
| `min` | `float` | Per-game average minutes |
| `pts` | `float` | Points (per mode dependent) |
| `plus_minus` | `float` | Plus/minus |
| `fg_pct` | `float \| None` | Field goal percentage |
| `w_pct` | `float` | Win percentage |
| `*_rank` | `int` | League rank for each stat (27 rank fields) |

### `LineupViz` (from `LeagueLineupViz`)

| Field | Type | Description |
|-------|------|-------------|
| `group_name` | `str` | Player names joined by " - " |
| `off_rating` | `float` | Offensive rating (pts per 100 poss) |
| `def_rating` | `float` | Defensive rating |
| `net_rating` | `float` | Net rating (off - def) |
| `pace` | `float` | Pace (possessions per 48 min) |
| `ts_pct` | `float` | True shooting percentage |
| `pct_fga_2pt` | `float` | Share of FGA that are 2-pointers |
| `pct_fga_3pt` | `float` | Share of FGA that are 3-pointers |
| `opp_efg_pct` | `float` | Opponent effective FG% |

## Integration with `teams.py`

The `lineups` module handles **league-wide** analysis; `teams` handles **single-team** analysis.
They wrap different endpoints and return different models:

| Function | Endpoint | Return Type | Scope |
|----------|----------|-------------|-------|
| `lineups.get_league_lineups` | `LeagueDashLineups` | `LeagueLineup` | League-wide |
| `lineups.get_league_lineup_ratings` | `LeagueLineupViz` | `LineupViz` | League-wide |
| `teams.get_lineup_stats` | `TeamDashLineups` | `LineupStats` | Single team |
| `teams.get_lineup_net_ratings` | `TeamDashLineups` | `(LineupStats, float)` | Single team |

Use `teams.get_lineup_stats` when you already know the team and want the `TeamDashLineups`
response model (which includes `sum_time_played` as a non-nullable `int`). Use
`lineups.get_league_lineups` when comparing across teams or exploring league-wide data.

## Gotchas

- **`lineup.min` is per-game average minutes**, not total minutes played. This field name
  is misleading — check `sum_time_played` for total minutes (nullable on `LeagueLineup`).
- **`LeagueDashLineups` requires a specific `team_id`** — the NBA API returns 500
  for `team_id=0`. That's why `get_league_lineups` and `get_top_lineups` take
  `team_id` as a required positional argument.
- **`LeagueLineupViz` ignores `team_id` entirely** — the API always returns
  league-wide data regardless of the value passed. `get_league_lineup_ratings`
  and `get_lineup_efficiency` filter client-side when `team_id` is non-zero.
- **`group_quantity` supports 2-5**. Pass `2` for two-man combos, `3` for three-man, etc.
  The `get_two_man_combos` convenience function sets this automatically.
- **`LeagueLineup` ≠ `LineupStats`**. These are different models from different endpoints.
  `LeagueLineup` has rank fields; `LineupStats` (from `TeamDashLineups`) does not.
