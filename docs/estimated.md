# estimated — Estimated Advanced Metrics

The `fastbreak.estimated` module provides league-wide estimated advanced metrics for players and teams. Unlike box-score-derived stats, estimated metrics use a Bayesian/regression framework that incorporates league-wide context to produce reliable values even for players with limited sample sizes — making them particularly useful early in a season or for players who have missed significant time.

## Table of Contents

- [Quick Start](#quick-start)
- [Functions](#functions)
  - [get_player_estimated_metrics](#get_player_estimated_metrics)
  - [get_team_estimated_metrics](#get_team_estimated_metrics)
  - [get_estimated_leaders](#get_estimated_leaders)
  - [find_player](#find_player)
  - [find_team](#find_team)
  - [rank_estimated_metrics](#rank_estimated_metrics)
- [Data Types](#data-types)
- [Gotchas](#gotchas)

---

## Quick Start

```python
from fastbreak.clients import NBAClient
from fastbreak.estimated import (
    get_player_estimated_metrics,
    get_team_estimated_metrics,
    get_estimated_leaders,
    find_player,
    find_team,
    rank_estimated_metrics,
)

async with NBAClient() as client:
    # Top 10 players by estimated net rating (2025-26 season)
    leaders = await get_estimated_leaders(client, metric="e_net_rating", top_n=10, min_gp=20)
    for rank, p in enumerate(leaders, 1):
        print(f"{rank}. {p.player_name}: {p.e_net_rating:+.1f}")

    # Single player lookup
    players = await get_player_estimated_metrics(client, season="2025-26")
    hali = find_player(players, player_id=1641705)
    if hali:
        print(f"{hali.player_name}: OFF {hali.e_off_rating:.1f} / DEF {hali.e_def_rating:.1f}")

    # Team metrics
    teams = await get_team_estimated_metrics(client, season="2025-26")
    pacers = find_team(teams, team_id=1610612754)
    if pacers:
        print(f"{pacers.team_name}: pace {pacers.e_pace:.1f}")
```

---

## Functions

### get_player_estimated_metrics

```python
async def get_player_estimated_metrics(
    client: NBAClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerEstimatedMetric]
```

Fetch estimated advanced metrics for all players in the league. Wraps `PlayerEstimatedMetrics`. Returns one row per player; there is no way to request a single player from this endpoint.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |

Returns `list[PlayerEstimatedMetric]` with one entry per player (league-wide). Use `find_player()` or `rank_estimated_metrics()` to filter client-side.

```python
players = await get_player_estimated_metrics(client, season="2025-26")
# [{player_id: 1641705, player_name: "Tyrese Haliburton", e_net_rating: 4.2, ...}, ...]
```

---

### get_team_estimated_metrics

```python
async def get_team_estimated_metrics(
    client: NBAClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[TeamEstimatedMetric]
```

Fetch estimated advanced metrics for all 30 teams. Wraps `TeamEstimatedMetrics`. Returns one row per team; there is no way to request a single team from this endpoint.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |

Returns `list[TeamEstimatedMetric]` with one entry per team. Use `find_team()` to look up a specific team client-side.

```python
teams = await get_team_estimated_metrics(client, season="2025-26")
# [{team_id: 1610612754, team_name: "Indiana Pacers", e_pace: 101.3, ...}, ...]

# Sort teams by estimated net rating
ranked = sorted(
    teams,
    key=lambda t: t.e_net_rating if t.e_net_rating is not None else float("-inf"),
    reverse=True,
)
for t in ranked[:5]:
    net = f"{t.e_net_rating:+.1f}" if t.e_net_rating is not None else "N/A"
    print(f"{t.team_name}: {net}")
```

---

### get_estimated_leaders

```python
async def get_estimated_leaders(
    client: NBAClient,
    *,
    metric: _PlayerMetricField = "e_net_rating",
    top_n: int = 10,
    min_gp: int = 0,
    min_minutes: float = 0.0,
    ascending: bool = False,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerEstimatedMetric]
```

Convenience wrapper: fetches all players via `get_player_estimated_metrics()`, applies `rank_estimated_metrics()`, and returns the top `top_n` results. Raises `ValueError` if `top_n < 1`.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `metric` | `"e_net_rating"` | Metric field to rank by (see `_PlayerMetricField`) |
| `top_n` | `10` | Number of results to return |
| `min_gp` | `0` | Minimum games played (inclusive) |
| `min_minutes` | `0.0` | Minimum minutes (inclusive). Per-game avg for players. |
| `ascending` | `False` | If `True`, return lowest values first |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |

`_PlayerMetricField` is a `Literal` of: `"e_off_rating"`, `"e_def_rating"`, `"e_net_rating"`, `"e_pace"`, `"e_usg_pct"`, `"e_ast_ratio"`, `"e_oreb_pct"`, `"e_dreb_pct"`, `"e_reb_pct"`, `"e_tov_pct"`.

```python
# Top 10 by net rating (min 20 games)
leaders = await get_estimated_leaders(client, metric="e_net_rating", top_n=10, min_gp=20)

# Top 5 by offensive rating (min 30 min/g)
off_leaders = await get_estimated_leaders(
    client, metric="e_off_rating", top_n=5, min_minutes=30.0
)

# Most efficient ball-handlers by AST ratio
ast_leaders = await get_estimated_leaders(client, metric="e_ast_ratio", top_n=10, min_gp=15)

# Worst turnover rate (highest e_tov_pct)
worst_tov = await get_estimated_leaders(
    client, metric="e_tov_pct", top_n=5, ascending=False, min_gp=20
)
```

---

### find_player

```python
def find_player(
    players: list[PlayerEstimatedMetric],
    player_id: int,
) -> PlayerEstimatedMetric | None
```

Return the first `PlayerEstimatedMetric` matching `player_id`, or `None` if not found. Pure function — no client required.

| Parameter | Default | Description |
|---|---|---|
| `players` | required | Full list from `get_player_estimated_metrics()` |
| `player_id` | required | NBA player ID |

```python
players = await get_player_estimated_metrics(client, season="2025-26")

# Tyrese Haliburton
hali = find_player(players, player_id=1641705)
if hali:
    print(f"{hali.player_name}: e_net={hali.e_net_rating:+.1f}, rank #{hali.e_net_rating_rank}")
```

---

### find_team

```python
def find_team(
    teams: list[TeamEstimatedMetric],
    team_id: int,
) -> TeamEstimatedMetric | None
```

Return the first `TeamEstimatedMetric` matching `team_id`, or `None` if not found. Pure function — no client required.

| Parameter | Default | Description |
|---|---|---|
| `teams` | required | Full list from `get_team_estimated_metrics()` |
| `team_id` | required | NBA team ID |

```python
teams = await get_team_estimated_metrics(client, season="2025-26")

# Indiana Pacers
pacers = find_team(teams, team_id=1610612754)
if pacers:
    print(f"{pacers.team_name}: pace={pacers.e_pace:.1f}, net={pacers.e_net_rating:+.1f}")
```

---

### rank_estimated_metrics

```python
def rank_estimated_metrics(
    players: list[PlayerEstimatedMetric],
    *,
    by: _PlayerMetricField = "e_net_rating",
    ascending: bool = False,
    min_gp: int = 0,
    min_minutes: float = 0.0,
) -> list[PlayerEstimatedMetric]
```

Filter and sort a player list by any estimated metric field. Players below the minimum games played or minutes threshold are excluded, as are players with `None` for the sort field. Raises `ValueError` if `min_gp` or `min_minutes` is negative.

| Parameter | Default | Description |
|---|---|---|
| `players` | required | List of player estimated metrics |
| `by` | `"e_net_rating"` | Metric field to sort by |
| `ascending` | `False` | If `True`, sort ascending (lowest first) |
| `min_gp` | `0` | Minimum games played (inclusive) |
| `min_minutes` | `0.0` | Minimum per-game average minutes (inclusive). E.g. `30.0` for 30+ min/g. |

```python
players = await get_player_estimated_metrics(client, season="2025-26")

# Top players by net rating (min 20 GP, min 30 min/g)
top = rank_estimated_metrics(players, by="e_net_rating", min_gp=20, min_minutes=30.0)
for p in top[:10]:
    print(f"{p.player_name}: {p.e_net_rating:+.1f}")

# Best offensive rebounders
oreb_leaders = rank_estimated_metrics(players, by="e_oreb_pct", min_gp=10)

# Highest usage among qualified players
usage = rank_estimated_metrics(players, by="e_usg_pct", min_gp=20, min_minutes=28.0)
```

---

## Data Types

### PlayerEstimatedMetric

Key fields on the `PlayerEstimatedMetric` Pydantic model returned by `get_player_estimated_metrics()`:

| Field | Type | Description |
|---|---|---|
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Player full name |
| `gp` | `int` | Games played |
| `wins` | `int` | Team wins while player appeared |
| `losses` | `int` | Team losses while player appeared |
| `win_pct` | `float \| None` | Win percentage |
| `minutes` | `float` | Per-game average minutes (not total season minutes) |
| `e_off_rating` | `float \| None` | Estimated offensive rating (points per 100 possessions on court) |
| `e_def_rating` | `float \| None` | Estimated defensive rating (points allowed per 100 possessions on court) |
| `e_net_rating` | `float \| None` | Estimated net rating (`e_off_rating - e_def_rating`) |
| `e_pace` | `float \| None` | Estimated pace (possessions per 48 minutes) |
| `e_usg_pct` | `float \| None` | Estimated usage percentage (0–1 scale) |
| `e_ast_ratio` | `float \| None` | Estimated assist ratio (assists per 100 plays) |
| `e_oreb_pct` | `float \| None` | Estimated offensive rebound percentage |
| `e_dreb_pct` | `float \| None` | Estimated defensive rebound percentage |
| `e_reb_pct` | `float \| None` | Estimated total rebound percentage |
| `e_tov_pct` | `float \| None` | Estimated turnover percentage (turnovers per 100 plays) |
| `e_off_rating_rank` | `int \| None` | League rank for `e_off_rating` (1 = best) |
| `e_def_rating_rank` | `int \| None` | League rank for `e_def_rating` (1 = best, i.e., lowest) |
| `e_net_rating_rank` | `int \| None` | League rank for `e_net_rating` (1 = best) |
| `gp_rank` | `int \| None` | League rank for games played |
| `min_rank` | `int \| None` | League rank for total minutes |

All `*_rank` fields are provided by the NBA API — no client-side computation needed.

---

### TeamEstimatedMetric

Key fields on the `TeamEstimatedMetric` Pydantic model returned by `get_team_estimated_metrics()`:

| Field | Type | Description |
|---|---|---|
| `team_id` | `int` | NBA team ID |
| `team_name` | `str` | Full team name (e.g., `"Indiana Pacers"`) |
| `gp` | `int` | Games played |
| `wins` | `int` | Wins |
| `losses` | `int` | Losses |
| `win_pct` | `float \| None` | Win percentage |
| `minutes` | `float` | Total team minutes |
| `e_off_rating` | `float \| None` | Estimated offensive rating |
| `e_def_rating` | `float \| None` | Estimated defensive rating |
| `e_net_rating` | `float \| None` | Estimated net rating |
| `e_pace` | `float \| None` | Estimated pace |
| `e_ast_ratio` | `float \| None` | Estimated assist ratio |
| `e_oreb_pct` | `float \| None` | Estimated offensive rebound percentage |
| `e_dreb_pct` | `float \| None` | Estimated defensive rebound percentage |
| `e_reb_pct` | `float \| None` | Estimated total rebound percentage |
| `e_tm_tov_pct` | `float \| None` | Estimated team turnover percentage (note: `e_tm_tov_pct`, not `e_tov_pct`) |
| `e_off_rating_rank` | `int \| None` | League rank for `e_off_rating` |
| `e_def_rating_rank` | `int \| None` | League rank for `e_def_rating` |
| `e_net_rating_rank` | `int \| None` | League rank for `e_net_rating` |

> **Note:** `TeamEstimatedMetric` uses `e_tm_tov_pct` (not `e_tov_pct`) and does not have an `e_usg_pct` field. These two differences from `PlayerEstimatedMetric` reflect the original API schema.

---

## Gotchas

- **League-wide endpoints only** — neither `PlayerEstimatedMetrics` nor `TeamEstimatedMetrics` accepts a player or team ID. The API always returns all players / all 30 teams. Use `find_player()`, `find_team()`, or `rank_estimated_metrics()` to filter client-side.

- **Singular `resultSet`** — both endpoints use `resultSet` (singular) instead of the `resultSets` (plural) key used by virtually every other NBA Stats API endpoint. The response models handle this transparently; you will not notice it in normal usage, but it matters if you write custom validators or inspect the raw API response.

- **`e_tm_tov_pct` vs `e_tov_pct`** — the team model uses `e_tm_tov_pct` while the player model uses `e_tov_pct`. This mirrors the raw API field names (`E_TM_TOV_PCT` vs `E_TOV_PCT`).

- **Team model lacks `e_usg_pct`** — usage percentage is a player-level concept and is not present on `TeamEstimatedMetric`.

- **Rankings are pre-computed by the API** — every estimated metric field has a corresponding `*_rank` field (e.g., `e_net_rating_rank`). There is no need to compute rankings client-side. Rank 1 = best for most metrics; for `e_def_rating`, rank 1 = lowest (best defense).

- **`minutes` means different things** — on `PlayerEstimatedMetric`, the `minutes` field is a **per-game average** (e.g., 38.3). On `TeamEstimatedMetric`, it is **total season minutes** (e.g., 3496.0). This inconsistency mirrors the raw API. When using `rank_estimated_metrics(min_minutes=...)`, use per-game values (e.g., `min_minutes=30.0` for 30+ min/g).
