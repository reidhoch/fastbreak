# fastbreak.compare

High-level helpers for comparing two NBA players side-by-side across box score stats, derived efficiency metrics (TS%, eFG%, A/TO, game score), and estimated advanced metrics (net rating, usage, pace).

All async functions take an `NBAClient` instance as the first argument. The `season` parameter defaults to the current season when omitted. Pure computation helpers (`build_compared_player`, `compare_players`, `comparison_deltas`, `comparison_edges`, `stat_leader`) do not require a client.

```python
from fastbreak.compare import (
    ComparedPlayer,
    ComparisonResult,
    EdgeSummary,
    COMPARISON_METRICS,
    HIGHER_IS_WORSE,
    build_compared_player,
    compare_players,
    comparison_deltas,
    comparison_edges,
    stat_leader,
    get_player_comparison,
)
```

---

## Data Classes

### `ComparedPlayer`

```python
@dataclass(frozen=True)
class ComparedPlayer:
    player_id: int
    name: str
    # Box score
    min: float
    pts: float
    reb: float
    oreb: float
    dreb: float
    ast: float
    stl: float
    blk: float
    tov: float
    pf: float
    plus_minus: float
    fgm: float
    fga: float
    fg_pct: float
    fg3m: float
    fg3a: float
    fg3_pct: float
    ftm: float
    fta: float
    ft_pct: float
    # Derived
    ts_pct: float | None
    efg_pct: float | None
    ast_tov: float | None
    game_score: float
    ft_rate: float | None
    three_pt_rate: float | None
    # Estimated advanced
    e_off_rating: float | None
    e_def_rating: float | None
    e_net_rating: float | None
    e_usg_pct: float | None
    e_pace: float | None
```

A frozen dataclass holding all stats for one player in a comparison. Box score fields come from the `PlayerCompare` endpoint. Derived metrics are computed via `fastbreak.metrics`. Estimated fields come from `PlayerEstimatedMetrics` (may be `None` if the player is not found in league-wide data).

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `player_id` | `int` | caller | NBA player ID |
| `name` | `str` | `description` field | Player name from API |
| `pts` | `float` | box score | Points |
| `reb` | `float` | box score | Total rebounds |
| `ast` | `float` | box score | Assists |
| `stl` / `blk` | `float` | box score | Steals / blocks |
| `tov` | `float` | box score | Turnovers |
| `fg_pct` / `fg3_pct` / `ft_pct` | `float` | box score | Shooting percentages |
| `plus_minus` | `float` | box score | Plus/minus |
| `ts_pct` | `float \| None` | `true_shooting()` | True shooting % |
| `efg_pct` | `float \| None` | `effective_fg_pct()` | Effective FG% |
| `ast_tov` | `float \| None` | `ast_to_tov()` | Assist-to-turnover ratio |
| `game_score` | `float` | `game_score()` | Hollinger's Game Score |
| `ft_rate` | `float \| None` | `free_throw_rate()` | Free throw rate |
| `three_pt_rate` | `float \| None` | `three_point_rate()` | Three-point attempt rate |
| `e_off_rating` | `float \| None` | estimated | Estimated offensive rating |
| `e_def_rating` | `float \| None` | estimated | Estimated defensive rating |
| `e_net_rating` | `float \| None` | estimated | Estimated net rating |
| `e_usg_pct` | `float \| None` | estimated | Estimated usage % |
| `e_pace` | `float \| None` | estimated | Estimated pace |

---

### `EdgeSummary`

```python
@dataclass(frozen=True)
class EdgeSummary:
    a_leads: int
    b_leads: int
    ties: int
    unavailable: int
    total: int
```

Counts how many comparison metrics each player leads in. `total == a_leads + b_leads + ties + unavailable` always. Metrics with `None` deltas (missing data) are counted as `unavailable`, not as ties. Metrics in `HIGHER_IS_WORSE` (turnovers, personal fouls, defensive rating) have inverted polarity — the player with the *lower* value leads.

---

### `ComparisonResult`

```python
@dataclass(frozen=True)
class ComparisonResult:
    player_a: ComparedPlayer
    player_b: ComparedPlayer
    deltas: dict[str, float | None]
    edges: EdgeSummary
```

The complete comparison. `deltas` maps each metric name to `player_a - player_b` (positive means A's raw value is higher). `None` deltas indicate one or both values are unavailable. Who actually *leads* on a metric depends on polarity — use `HIGHER_IS_WORSE` (and helpers like `stat_leader` / `comparison_edges`) rather than the sign of the delta alone.

---

## Constants

### `COMPARISON_METRICS`

Tuple of all metric names included in the comparison: 20 box score fields + 6 derived + 5 estimated = 31 total.

### `HIGHER_IS_WORSE`

`frozenset({"tov", "pf", "e_def_rating"})` — metrics where a lower value is better. Used by `comparison_edges` to invert polarity.

---

## Function Reference

### `build_compared_player`

```python
def build_compared_player(
    player_id: int,
    stats: _CompareStatsLike,
    estimated: PlayerEstimatedMetric | None = None,
) -> ComparedPlayer
```

Pure computation helper. Builds a `ComparedPlayer` from a stats object (matching the `PlayerCompareStats` fields) and optional estimated metrics.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player ID |
| `stats` | `_CompareStatsLike` | required | Box score stats object |
| `estimated` | `PlayerEstimatedMetric \| None` | `None` | Estimated advanced metrics |

**Returns** `ComparedPlayer`

---

### `comparison_deltas`

```python
def comparison_deltas(
    a: ComparedPlayer,
    b: ComparedPlayer,
) -> dict[str, float | None]
```

Compute `a - b` for every metric in `COMPARISON_METRICS`. Returns `None` for any metric where either value is `None`.

**Mathematical properties:**
- **Antisymmetry**: `deltas(a, b)[m] == -deltas(b, a)[m]`
- **Identity**: `deltas(a, a)[m] == 0` for all non-None metrics

---

### `comparison_edges`

```python
def comparison_edges(
    deltas: dict[str, float | None],
    *,
    higher_is_worse: frozenset[str] = HIGHER_IS_WORSE,
) -> EdgeSummary
```

Count leads/trails/ties from a deltas dict. `None` deltas are counted as `unavailable`. For metrics in `higher_is_worse`, the polarity is inverted (lower is better).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deltas` | `dict[str, float \| None]` | required | Output of `comparison_deltas` |
| `higher_is_worse` | `frozenset[str]` | `HIGHER_IS_WORSE` | Metrics where lower is better |

**Returns** `EdgeSummary` — `total == a_leads + b_leads + ties + unavailable` always

---

### `stat_leader`

```python
def stat_leader(
    a: ComparedPlayer,
    b: ComparedPlayer,
    metric: str,
    *,
    higher_is_worse: bool = False,
) -> int | None
```

Return the `player_id` of whichever player leads in a metric. Returns `None` if tied or either value is unavailable.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `a` | `ComparedPlayer` | required | First player |
| `b` | `ComparedPlayer` | required | Second player |
| `metric` | `str` | required | Attribute name to compare |
| `higher_is_worse` | `bool` | `False` | If `True`, lower value wins |

**Returns** `int | None` — player_id of the leader, or `None`

**Example**

```python
leader = stat_leader(result.player_a, result.player_b, "pts")
if leader == result.player_a.player_id:
    print(f"{result.player_a.name} scores more")
```

---

### `compare_players`

```python
def compare_players(
    player_a_id: int,
    player_a_stats: _CompareStatsLike,
    player_b_id: int,
    player_b_stats: _CompareStatsLike,
    *,
    estimated_a: PlayerEstimatedMetric | None = None,
    estimated_b: PlayerEstimatedMetric | None = None,
) -> ComparisonResult
```

Pure orchestrator. Builds both `ComparedPlayer` instances, computes deltas and edges. Use this when you already have raw stats objects.

---

### `get_player_comparison`

```python
async def get_player_comparison(
    client: NBAClient,
    player_a_id: int,
    player_b_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> ComparisonResult
```

Fetch and build a full comparison between two players. Makes 2 concurrent API calls: `PlayerCompare` (box score) and `PlayerEstimatedMetrics` (advanced). Returns a complete `ComparisonResult`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_a_id` | `int` | required | First player's NBA ID |
| `player_b_id` | `int` | required | Second player's NBA ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | Season type |
| `per_mode` | `PerMode` | `"PerGame"` | Stat mode |

**Returns** `ComparisonResult`

**Raises** `ValueError` if the endpoint returns fewer than 2 individual rows

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.compare import get_player_comparison

async def main():
    async with NBAClient() as client:
        result = await get_player_comparison(client, 2544, 203999)

    a, b = result.player_a, result.player_b
    a_ts = f"{a.ts_pct:.3f}" if a.ts_pct is not None else "N/A"
    b_ts = f"{b.ts_pct:.3f}" if b.ts_pct is not None else "N/A"
    print(f"{a.name}: {a.pts} pts, TS% {a_ts}")
    print(f"{b.name}: {b.pts} pts, TS% {b_ts}")

    for metric, delta in result.deltas.items():
        if delta is not None and abs(delta) > 1.0:
            print(f"  {metric}: {delta:+.1f}")

    e = result.edges
    print(f"Edge: {a.name} {e.a_leads} - {b.name} {e.b_leads} (ties {e.ties})")

asyncio.run(main())
```

---

## Complete Examples

### Side-by-side comparison with stat categories

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.compare import HIGHER_IS_WORSE, get_player_comparison, stat_leader
from fastbreak.players import get_player_id

async def main():
    async with NBAClient() as client:
        pid_a = await get_player_id(client, "Jayson Tatum")
        pid_b = await get_player_id(client, "Luka Dončić")
        if pid_a is None or pid_b is None:
            raise ValueError("Could not resolve one or both player IDs")
        result = await get_player_comparison(client, pid_a, pid_b)

    a, b = result.player_a, result.player_b
    print(f"{a.name} vs {b.name}")

    for label, metric in [("PTS", "pts"), ("REB", "reb"), ("AST", "ast"),
                           ("TS%", "ts_pct"), ("NET", "e_net_rating")]:
        hiw = metric in HIGHER_IS_WORSE
        lid = stat_leader(a, b, metric, higher_is_worse=hiw)
        arrow = "←" if lid == a.player_id else ("→" if lid == b.player_id else "=")
        delta = result.deltas[metric]
        d_str = f"{delta:+.1f}" if delta is not None else "N/A"
        print(f"  {label:<5} {getattr(a, metric):>8} {arrow} {getattr(b, metric):>8}  ({d_str})")

    e = result.edges
    print(f"\nEdge: {a.name} {e.a_leads} - {b.name} {e.b_leads} (ties {e.ties})")

asyncio.run(main())
```

---

## Helpers vs. Raw Endpoints

| Need | Use helper | Use raw endpoint |
|------|-----------|-----------------|
| Full comparison with derived metrics | `get_player_comparison` | `PlayerCompare` + manual computation |
| Custom comparison metrics | `compare_players` with own stats | `PlayerCompare` endpoint directly |
| Specific metric delta | `stat_leader` or `comparison_deltas` | `stat_delta` from `fastbreak.metrics` |
| Edge count with custom polarity | `comparison_edges(deltas, higher_is_worse=...)` | Manual counting |
