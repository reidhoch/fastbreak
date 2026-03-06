# fastbreak.splits

High-level helpers for NBA player situational split data. These functions wrap five `PlayerDashboardBy*` endpoints and expose a `PlayerSplitsProfile` dataclass that fetches all sub-endpoints for a player concurrently.

All async functions take an `NBAClient` instance as the first argument. The `season` parameter defaults to the current season when omitted.

```python
from fastbreak.splits import (
    get_player_game_splits,
    get_player_general_splits,
    get_player_shooting_splits,
    get_player_last_n_games,
    get_player_team_performance_splits,
    get_player_splits_profile,
    PlayerSplitsProfile,
    stat_delta,
)
```

---

## Data Class

### `PlayerSplitsProfile`

```python
@dataclass(frozen=True)
class PlayerSplitsProfile:
    player_id: int
    game_splits: PlayerDashboardByGameSplitsResponse
    general_splits: PlayerDashboardByGeneralSplitsResponse
    shooting_splits: PlayerDashboardByShootingSplitsResponse
    last_n_games: PlayerDashboardByLastNGamesResponse
    team_performance: PlayerDashboardByTeamPerformanceResponse
```

A frozen dataclass holding all five player split responses. Built by `get_player_splits_profile`, which fetches all five endpoints concurrently via `client.get_many()`.

| Field | Description |
|-------|-------------|
| `player_id` | NBA player ID |
| `game_splits` | Stats by half, period, score margin, and actual margin |
| `general_splits` | Stats by location, W/L, month, All-Star break, starter/bench, and days rest |
| `shooting_splits` | Stats by shot distance, court area, shot type, and assist type |
| `last_n_games` | Rolling averages for last 5/10/15/20 games and by game-number range |
| `team_performance` | Stats split by score differential and team points scored/against ranges |

---

## Player Helpers

All helpers accept the same keyword arguments:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `season` | `Season \| None` | current season | Season in YYYY-YY format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `PerMode` | `"PerGame"` | `"PerGame"` or `"Totals"` |
| `last_n_games` | `int` | `0` | Restrict to last N games (0 = full season) |

---

### `get_player_game_splits`

```python
async def get_player_game_splits(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashboardByGameSplitsResponse
```

Fetch player stats broken down by game segment: half, period, score margin, and actual score margin.

**`PlayerDashboardByGameSplitsResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `overall` | `GameSplitStats \| None` | Full-season aggregate |
| `by_half` | `list[GameSplitStats]` | Stats by half (First Half, Second Half, Overtime) |
| `by_period` | `list[GameSplitStats]` | Stats by period (Q1, Q2, Q3, Q4, OT1, …) |
| `by_score_margin` | `list[GameSplitStats]` | Stats by general margin (Tied, Behind, Ahead) |
| `by_actual_margin` | `list[GameSplitStats]` | Stats by specific margin range (e.g., "Within 5") |

---

### `get_player_general_splits`

```python
async def get_player_general_splits(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    ...
) -> PlayerDashboardByGeneralSplitsResponse
```

Fetch player situational splits by location, game outcome, month, All-Star break, starting position, and days of rest.

**`PlayerDashboardByGeneralSplitsResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `overall` | `GameSplitStats \| None` | Full-season aggregate |
| `by_location` | `list[GameSplitStats]` | Home vs. Road (`group_value`: `"Home"`, `"Road"`) |
| `by_wins_losses` | `list[GameSplitStats]` | Wins vs. Losses |
| `by_month` | `list[GameSplitStats]` | Per calendar month |
| `by_pre_post_all_star` | `list[GameSplitStats]` | Pre All-Star vs. Post All-Star |
| `by_starting_position` | `list[GameSplitStats]` | Starters vs. Bench |
| `by_days_rest` | `list[GameSplitStats]` | 0/1/2/3+ days rest |

---

### `get_player_shooting_splits`

```python
async def get_player_shooting_splits(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    ...
) -> PlayerDashboardByShootingSplitsResponse
```

Fetch detailed shooting stats broken down by shot distance, court area, shot type, and whether the shot was assisted.

**`PlayerDashboardByShootingSplitsResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `overall` | `ShootingSplitStatsWithRank \| None` | Full-season aggregate with league ranks |
| `by_shot_distance_5ft` | `list[ShootingSplitStatsWithRank]` | Shot distance in 5-foot buckets |
| `by_shot_distance_8ft` | `list[ShootingSplitStatsWithRank]` | Shot distance in 8-foot buckets |
| `by_shot_area` | `list[ShootingSplitStatsWithRank]` | By court zone (Restricted Area, In The Paint, Mid-Range, Corner 3, Above the Break 3) |
| `by_assisted` | `list[ShootingSplitStatsWithRank]` | Assisted vs. Unassisted shots |
| `by_shot_type_summary` | `list[ShootingSplitStats]` | Summary by shot type category (no rank columns) |
| `by_shot_type_detail` | `list[ShootingSplitStatsWithRank]` | Detailed shot types (40+ categories) |
| `assisted_by` | `list[AssistedByStats]` | FG% on shots assisted by each teammate |

Each `ShootingSplitStats` row exposes: `group_value`, `fgm`, `fga`, `fg_pct`, `fg3m`, `fg3a`, `fg3_pct`, `efg_pct`, `pct_ast_fgm`, `pct_uast_fgm`.

---

### `get_player_last_n_games`

```python
async def get_player_last_n_games(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    ...
) -> PlayerDashboardByLastNGamesResponse
```

Fetch rolling-average stats at multiple lookback windows to identify recent form.

**`PlayerDashboardByLastNGamesResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `overall` | `GameSplitStats \| None` | Full-season baseline |
| `last_5` | `GameSplitStats \| None` | Stats from the last 5 games |
| `last_10` | `GameSplitStats \| None` | Stats from the last 10 games |
| `last_15` | `GameSplitStats \| None` | Stats from the last 15 games |
| `last_20` | `GameSplitStats \| None` | Stats from the last 20 games |
| `by_game_number` | `list[GameSplitStats]` | Stats by game-number ranges (Games 1–10, 11–20, …) |

---

### `get_player_team_performance_splits`

```python
async def get_player_team_performance_splits(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    ...
) -> PlayerDashboardByTeamPerformanceResponse
```

Fetch player stats split by the team's score differential and by points-scored/against ranges.

**`PlayerDashboardByTeamPerformanceResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `overall` | `GameSplitStats \| None` | Full-season aggregate |
| `by_score_differential` | `list[TeamPerformanceStats]` | Split by W/L and score margin (e.g., "W 10+", "L 1–5") |
| `by_points_scored` | `list[TeamPerformanceStats]` | Split by team points scored ranges |
| `by_points_against` | `list[TeamPerformanceStats]` | Split by opponent points scored ranges |

`TeamPerformanceStats` extends `GameSplitStats` with `group_value_2` (secondary grouping label, e.g., "W" or "L") and `group_value_order` (sort key).

---

## Profile Function

### `get_player_splits_profile`

```python
async def get_player_splits_profile(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerSplitsProfile
```

Fetch all five player split endpoints concurrently and return a `PlayerSplitsProfile`.

Uses `client.get_many()` so the client's `request_delay` and `max_concurrency` settings are respected. Raises `ExceptionGroup` if any request fails. Callers that need partial results should call the thin helpers individually.

**Example**

```python
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_id
from fastbreak.splits import get_player_splits_profile, stat_delta

async with NBAClient() as client:
    player_id = await get_player_id(client, "Victor Wembanyama")
    profile = await get_player_splits_profile(client, player_id=player_id)

# Home vs road FG% delta
home = next((s for s in profile.general_splits.by_location if s.group_value == "Home"), None)
road = next((s for s in profile.general_splits.by_location if s.group_value == "Road"), None)
delta = stat_delta(home.fg_pct if home else None, road.fg_pct if road else None)
if delta is not None:
    print(f"Home/road FG% edge: {delta:+.3f}")

# Recent form vs season baseline
if profile.last_n_games.last_5 and profile.last_n_games.overall:
    pts_trend = stat_delta(profile.last_n_games.last_5.pts, profile.last_n_games.overall.pts)
    print(f"L5 vs season: {pts_trend:+.1f} PTS")
```

---

## Pure Helper

### `stat_delta`

```python
def stat_delta(a: float | None, b: float | None) -> float | None
```

Compute `a - b`. Returns `None` if either argument is `None`. Useful for comparing the same stat across any two splits without manually handling the None-guard each time.

```python
from fastbreak.splits import stat_delta

# Home vs road FG% edge
stat_delta(home.fg_pct, road.fg_pct)    # e.g., 0.027 (home 2.7pp better)

# None-safe: returns None if data is missing for either window
stat_delta(last_5.pts, None)            # → None
```

**Properties** (verified by property-based tests):
- **Antisymmetry**: `stat_delta(a, b) == -stat_delta(b, a)` for all finite floats
- **Identity**: `stat_delta(a, a) == 0.0` for all finite floats
- **None propagation**: if either argument is `None`, result is `None`

---

## Common Patterns

### Home/road performance gap

```python
from fastbreak.splits import get_player_general_splits, stat_delta

async with NBAClient() as client:
    splits = await get_player_general_splits(client, player_id=1641705, season="2025-26")

home = next((s for s in splits.by_location if s.group_value == "Home"), None)
road = next((s for s in splits.by_location if s.group_value == "Road"), None)

fg_delta = stat_delta(home.fg_pct if home else None, road.fg_pct if road else None)
pts_delta = stat_delta(home.pts if home else None, road.pts if road else None)
fg_delta_str = f"{fg_delta:+.3f}" if fg_delta is not None else "N/A"
pts_delta_str = f"{pts_delta:+.1f}" if pts_delta is not None else "N/A"
print(f"FG% home/road edge: {fg_delta_str}")
print(f"PTS home/road edge: {pts_delta_str}")
```

### Is the player heating up or cooling off?

```python
from fastbreak.splits import get_player_last_n_games, stat_delta

async with NBAClient() as client:
    last_n = await get_player_last_n_games(client, player_id=2544, season="2025-26")

if last_n.last_5 and last_n.overall:
    pts_trend = stat_delta(last_n.last_5.pts, last_n.overall.pts)
    fg_trend = stat_delta(last_n.last_5.fg_pct, last_n.overall.fg_pct)
    pts_trend_str = f"{pts_trend:+.1f} PTS" if pts_trend is not None else "N/A PTS"
    fg_trend_str = f"{fg_trend:+.3f} FG%" if fg_trend is not None else "N/A FG%"
    print(f"L5 vs season:  {pts_trend_str}  {fg_trend_str}")
```

### Shot area efficiency

```python
from fastbreak.splits import get_player_shooting_splits

async with NBAClient() as client:
    shooting = await get_player_shooting_splits(client, player_id=201939, season="2025-26")

print("FG% by court area:")
for row in shooting.by_shot_area:
    print(f"  {row.group_value:<30} {row.fg_pct:.1%}  eFG% {row.efg_pct:.1%}")
```

### Score-margin context

```python
from fastbreak.splits import get_player_game_splits

async with NBAClient() as client:
    game_splits = await get_player_game_splits(client, player_id=203999, season="2025-26")

print("Stats by score margin:")
for row in game_splits.by_score_margin:
    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"  {str(row.group_value):<20} {row.gp:>3} GP  {fg_str} FG%  {row.pts:.1f} PTS")
```

---

## Gotchas

- **`overall` is a single object, not a list.** All five response types have `overall: GameSplitStats | None`. Check `if response.overall is not None:` before accessing it; don't iterate over it.
- **Empty lists vs. None.** When a player has no data for a specific window (e.g., `last_n_games.last_20` early in the season), the field is `None`. The list fields (e.g., `by_location`, `by_period`) return an empty list `[]` rather than `None` — always guard with `if response.by_location:` before iterating if the season may be early.
- **`group_value` is `str | int`.** `GameSplitStats.group_value` is typed `str | int` (some NBA endpoints return numeric labels for period numbers). Use `str(row.group_value)` in f-strings or comparisons to be safe.
- **`stat_delta` is not for ranked fields.** Rank columns in `GameSplitStats` (e.g., `fg_pct_rank`) represent league rank — smaller is better. Applying `stat_delta` to ranks gives a meaningful difference only if you remember the direction is inverted.
- **`by_score_differential` uses two grouping fields.** `TeamPerformanceStats.group_value` holds the margin range (e.g., `"W 10+"`) and `group_value_2` holds the win/loss indicator (`"W"` or `"L"`). Use both for full context.
- **`per_mode="Totals"` vs. `"PerGame"`.** All helpers default to `"PerGame"`. For raw counting stats (e.g., total FGM on catch-and-shoot attempts), pass `per_mode="Totals"`.
