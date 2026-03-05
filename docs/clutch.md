# fastbreak.clutch

High-level helpers for clutch performance analysis. These functions use the standard NBA clutch definition — **last 5 minutes of the game with the score within 5 points** — to compare a player's performance under pressure against their full-season baseline.

All async functions take an `NBAClient` instance as the first argument. The `season` parameter defaults to the current season when omitted. Pure computation helpers (`clutch_score`, `build_clutch_profile`) do not require a client.

```python
from fastbreak.clutch import (
    clutch_score,
    build_clutch_profile,
    get_player_clutch_stats,
    get_player_clutch_profile,
    get_league_clutch_leaders,
)
```

---

## Data Classes

### `ClutchProfile`

```python
@dataclass(frozen=True)
class ClutchProfile:
    player_id: int
    name: str
    team: str
    clutch_min: float
    regular_ts: float | None
    clutch_ts: float | None
    ts_delta: float | None
    regular_ato: float | None
    clutch_ato: float | None
    ato_delta: float | None
    clutch_plus_minus: float
    score: float | None
```

A frozen dataclass holding a player's computed clutch performance profile. Built by `build_clutch_profile` or returned directly by `get_player_clutch_profile`.

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | NBA player ID |
| `name` | `str` | Player's full name (display only) |
| `team` | `str` | Team abbreviation (display only) |
| `clutch_min` | `float` | Minutes played in clutch situations |
| `regular_ts` | `float \| None` | True shooting % for the full season baseline |
| `clutch_ts` | `float \| None` | True shooting % in clutch situations |
| `ts_delta` | `float \| None` | `clutch_ts - regular_ts` — positive means better under pressure |
| `regular_ato` | `float \| None` | Assist-to-turnover ratio for the full season |
| `clutch_ato` | `float \| None` | Assist-to-turnover ratio in clutch situations |
| `ato_delta` | `float \| None` | `clutch_ato - regular_ato` — positive means better decisions |
| `clutch_plus_minus` | `float` | Plus/minus in clutch situations |
| `score` | `float \| None` | Composite clutch rating; `None` if below the minutes threshold |

`score` is `None` when `clutch_min < min_threshold` (default 5 minutes) — the sample is considered too small to be reliable.

---

## Function Reference

### `clutch_score`

```python
def clutch_score(
    ts_delta: float,
    ato_delta: float,
    plus_minus: float,
    clutch_min: float,
    min_threshold: float = 5.0,
) -> float | None
```

Pure computation helper. Calculates a composite clutch performance score from pre-computed deltas.

The formula is a weighted linear combination:

```
score = ts_delta * 10 + ato_delta * 3 + plus_minus * 0.5
```

Weights reflect predictive value: shooting quality under pressure is the strongest signal, followed by decision-making, then team outcome context. The linear (no-constant) form means the score is antisymmetric — `score(-x) == -score(x)`.

Returns `None` when `clutch_min < min_threshold` (insufficient sample).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ts_delta` | `float` | required | Clutch TS% minus regular-season TS% |
| `ato_delta` | `float` | required | Clutch A/TO minus regular-season A/TO |
| `plus_minus` | `float` | required | Plus/minus in clutch situations |
| `clutch_min` | `float` | required | Minutes played in clutch situations |
| `min_threshold` | `float` | `5.0` | Minimum clutch minutes required to compute a score |

**Returns** `float | None` — composite score, or `None` if below the minutes threshold

**Example**

```python
from fastbreak.clutch import clutch_score

# Player improved TS% by 5pp and A/TO by 0.5, with +3 plus/minus
score = clutch_score(ts_delta=0.05, ato_delta=0.5, plus_minus=3.0, clutch_min=25.0)
# score = 0.05 * 10 + 0.5 * 3 + 3.0 * 0.5 = 0.5 + 1.5 + 1.5 = 3.5

# Player with fewer than 20 clutch minutes — score suppressed
score = clutch_score(ts_delta=0.10, ato_delta=1.0, plus_minus=5.0, clutch_min=10.0)
# score is None
```

---

### `build_clutch_profile`

```python
def build_clutch_profile(
    player_id: int,
    name: str,
    team: str,
    overall: _ClutchStatsLike | None,
    clutch: _ClutchStatsLike | None,
    *,
    min_threshold: float = 5.0,
) -> ClutchProfile
```

Pure computation helper. Builds a `ClutchProfile` from stats objects representing overall and clutch-situation performance. Either `overall` or `clutch` may be `None`.

Both stats objects must expose `.pts`, `.fga`, `.fta`, `.ast`, `.tov`, `.min`, and `.plus_minus` attributes (structural duck-typing via `_ClutchStatsLike` Protocol — any object with those fields works).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player ID |
| `name` | `str` | required | Player full name (stored for display) |
| `team` | `str` | required | Team abbreviation (stored for display) |
| `overall` | `_ClutchStatsLike \| None` | required | Full-season stats object, or `None` |
| `clutch` | `_ClutchStatsLike \| None` | required | Clutch-situation stats object, or `None` |
| `min_threshold` | `float` | `5.0` | Minimum clutch minutes required to compute a score |

**Returns** `ClutchProfile` with all computed delta and composite score fields

---

### `get_player_clutch_stats`

```python
async def get_player_clutch_stats(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> PlayerDashboardByClutchResponse
```

Fetch all clutch time-split variants for a single player. Returns stats for eleven clutch definitions (last 5/3/1 minutes at ≤5 points, last 30/10 seconds at ≤3 points, and the same definitions with ±5/±3 point spreads).

Use this when you need access to non-standard clutch definitions. For the common case (standard clutch definition), use `get_player_clutch_profile` instead.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, etc. |

**Returns** `PlayerDashboardByClutchResponse` — contains `overall` and eleven named clutch scenario attributes. Key attributes:

| Attribute | Clutch definition |
|-----------|------------------|
| `overall` | Full season (no clutch filter) |
| `last_5_min_lte_5_pts` | Last 5 min, score ≤5 pts (standard NBA clutch) |
| `last_3_min_lte_5_pts` | Last 3 min, score ≤5 pts |
| `last_1_min_lte_5_pts` | Last 1 min, score ≤5 pts |
| `last_30_sec_lte_3_pts` | Last 30 sec, score ≤3 pts |
| `last_10_sec_lte_3_pts` | Last 10 sec, score ≤3 pts |

---

### `get_player_clutch_profile`

```python
async def get_player_clutch_profile(
    client: NBAClient,
    player_id: int,
    *,
    name: str = "",
    team: str = "",
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    min_threshold: float = 5.0,
) -> ClutchProfile | None
```

Build a `ClutchProfile` comparing a player's clutch performance against their regular-season baseline. Uses the standard NBA clutch definition: last 5 minutes, score within 5 points.

Returns `None` if the player has no qualifying clutch minutes for the season.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `name` | `str` | `""` | Player's display name (stored on profile) |
| `team` | `str` | `""` | Team abbreviation (stored on profile) |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, etc. |
| `min_threshold` | `float` | `5.0` | Minimum clutch minutes to compute a composite score |

**Returns** `ClutchProfile | None` — the computed profile, or `None` if the player has no clutch data

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.clutch import get_player_clutch_profile

async def main():
    async with NBAClient() as client:
        profile = await get_player_clutch_profile(
            client,
            player_id=2544,
            name="LeBron James",
            team="LAL",
        )

        if profile is None:
            print("No clutch data recorded this season")
            return

        print(f"{profile.name} ({profile.team})")
        print(f"  Clutch minutes: {profile.clutch_min:.1f}")
        print(f"  Clutch +/-:     {profile.clutch_plus_minus:+.1f}")

        if profile.ts_delta is not None:
            label = "↑ better" if profile.ts_delta > 0 else "↓ worse"
            print(f"  TS% delta:      {profile.ts_delta:+.3f}  ({label} in clutch)")

        if profile.score is not None:
            print(f"  Composite score: {profile.score:+.2f}")
        else:
            print(f"  Composite score: N/A (< {20} clutch minutes)")

asyncio.run(main())
```

---

### `get_league_clutch_leaders`

```python
async def get_league_clutch_leaders(
    client: NBAClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    min_minutes: float = 20.0,
    top_n: int = 10,
) -> list[LeagueDashPlayerClutchRow]
```

Fetch league-wide clutch leaders sorted by plus/minus descending. Uses the standard clutch definition (last 5 min, ≤5 pts) across all players, filtered to those with sufficient clutch sample size.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, etc. |
| `min_minutes` | `float` | `20.0` | Minimum clutch minutes to qualify |
| `top_n` | `int` | `10` | Maximum number of players to return |

**Returns** `list[LeagueDashPlayerClutchRow]` — sorted by `plus_minus` descending, capped at `top_n`

**`LeagueDashPlayerClutchRow` fields (selected)**

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Player name |
| `team_id` | `int` | Team ID |
| `team_abbreviation` | `str` | Team abbreviation |
| `age` | `float \| None` | Player age |
| `gp` | `int` | Games played |
| `w` / `losses` | `int` | Wins / losses in clutch situations |
| `w_pct` | `float \| None` | Win percentage in clutch situations |
| `min` | `float` | Clutch minutes played |
| `pts` | `float` | Points per clutch appearance |
| `reb` / `ast` / `stl` / `blk` | `float` | Stats per clutch appearance |
| `fgm` / `fga` / `fg_pct` | `float / float / float \| None` | Field goal stats |
| `fg3m` / `fg3a` / `fg3_pct` | `float / float / float \| None` | Three-point stats |
| `ftm` / `fta` / `ft_pct` | `float / float / float \| None` | Free throw stats |
| `tov` | `float` | Turnovers per clutch appearance |
| `plus_minus` | `float` | Plus/minus in clutch situations |
| `dd2` / `td3` | `int \| None` | Double-doubles / triple-doubles |

Each stat also has a corresponding `*_rank` field (e.g. `plus_minus_rank`) giving that player's league rank for the stat.

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.clutch import get_league_clutch_leaders

async def main():
    async with NBAClient() as client:
        leaders = await get_league_clutch_leaders(
            client,
            min_minutes=20.0,
            top_n=10,
        )

    if not leaders:
        print("No qualified clutch performers found")
        return

    print("Top Clutch Performers (by plus/minus, min 20 clutch min)")
    print(f"{'#':<3} {'Player':<25} {'Team':<5} {'Min':>5} {'±':>6} {'TS%':>6}")
    print("-" * 55)
    for rank, row in enumerate(leaders, 1):
        # Compute TS% from raw clutch stats
        ts = row.pts / (2 * (row.fga + 0.44 * row.fta)) if row.fga or row.fta else None
        ts_str = f"{ts:.3f}" if ts is not None else "  N/A"
        pm_str = f"{row.plus_minus:+.1f}"
        print(f"{rank:<3} {row.player_name:<25} {row.team_abbreviation:<5} {row.min:>5.1f} {pm_str:>6} {ts_str:>6}")

asyncio.run(main())
```

---

## Complete Examples

### Clutch leaderboard with scoring efficiency

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.clutch import get_league_clutch_leaders

async def main():
    async with NBAClient() as client:
        # Top 15 by plus/minus, requiring 30+ clutch minutes
        leaders = await get_league_clutch_leaders(
            client,
            min_minutes=30.0,
            top_n=15,
        )

    print(f"{'Rank':<5} {'Player':<25} {'Team':<5} {'GP':>3} {'Min':>5} {'PTS':>5} {'+/-':>6} {'W%':>6}")
    print("-" * 65)
    for i, row in enumerate(leaders, 1):
        w_pct = f"{row.w_pct:.3f}" if row.w_pct is not None else "  N/A"
        print(
            f"{i:<5} {row.player_name:<25} {row.team_abbreviation:<5} "
            f"{row.gp:>3} {row.min:>5.1f} {row.pts:>5.1f} "
            f"{row.plus_minus:>+6.1f} {w_pct:>6}"
        )

asyncio.run(main())
```

### Per-player clutch profile with context

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.clutch import get_player_clutch_profile
from fastbreak.players import get_player_id

async def clutch_report(client, name: str, season: str) -> None:
    player_id = await get_player_id(client, name)
    if player_id is None:
        print(f"  {name}: not found")
        return

    profile = await get_player_clutch_profile(
        client,
        player_id=player_id,
        name=name,
        season=season,  # type: ignore[arg-type]
    )

    if profile is None:
        print(f"  {name}: no clutch data")
        return

    score_str = f"{profile.score:+.2f}" if profile.score is not None else "N/A (< 20 min)"
    ts_str = f"{profile.ts_delta:+.3f}" if profile.ts_delta is not None else "N/A"
    ato_str = f"{profile.ato_delta:+.2f}" if profile.ato_delta is not None else "N/A"
    print(
        f"  {name:<22} {profile.clutch_min:>5.1f} min  "
        f"TS%Δ {ts_str}  A/TOΔ {ato_str}  "
        f"+/- {profile.clutch_plus_minus:>+5.1f}  score {score_str}"
    )

async def main():
    season = "2024-25"
    players = [
        "LeBron James",
        "Stephen Curry",
        "Nikola Jokic",
        "Jayson Tatum",
        "Luka Doncic",
    ]

    print(f"Clutch Performance Report — {season}")
    print(f"  {'Player':<22} {'Min':>5}      TS%Δ    A/TOΔ    +/-     Score")
    print("  " + "-" * 72)

    async with NBAClient() as client:
        for name in players:
            await clutch_report(client, name, season)

asyncio.run(main())
```

### Comparing standard vs. tighter clutch definitions

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.clutch import build_clutch_profile, get_player_clutch_stats

async def main():
    async with NBAClient() as client:
        # Fetch all eleven clutch splits for Nikola Jokic (ID: 203999)
        response = await get_player_clutch_stats(client, player_id=203999)

    definitions = {
        "Last 5 min, ≤5 pts (standard)": response.last_5_min_lte_5_pts,
        "Last 3 min, ≤5 pts":            response.last_3_min_lte_5_pts,
        "Last 1 min, ≤5 pts":            response.last_1_min_lte_5_pts,
    }

    print("Nikola Jokic — clutch profile by time window")
    print(f"{'Definition':<30} {'Min':>6} {'Score':>8}")
    print("-" * 47)

    for label, clutch_stats in definitions.items():
        if clutch_stats is None:
            print(f"{label:<30} {'N/A':>6} {'N/A':>8}")
            continue

        profile = build_clutch_profile(
            203999, "Nikola Jokic", "DEN",
            response.overall,
            clutch_stats,
        )
        score_str = f"{profile.score:+.2f}" if profile.score is not None else "   N/A"
        print(f"{label:<30} {profile.clutch_min:>6.1f} {score_str:>8}")

asyncio.run(main())
```

---

## Helpers vs. Raw Endpoints

The helpers in `fastbreak.clutch` cover the most common clutch workflows. For advanced filtering or non-standard clutch windows, access the raw endpoints directly.

| Need | Use helper | Use raw endpoint |
|------|-----------|-----------------|
| Standard clutch profile (last 5 min ≤5 pts) | `get_player_clutch_profile` | `PlayerDashboardByClutch` (all eleven windows) |
| League-wide clutch ranking | `get_league_clutch_leaders` | `LeagueDashPlayerClutch` (position/conference filters) |
| Non-standard clutch window | `get_player_clutch_stats` + `build_clutch_profile` | `PlayerDashboardByClutch` (direct attribute access) |
| Composite score from custom stats | `build_clutch_profile` / `clutch_score` | n/a — pure Python |

Example — accessing a non-standard clutch window directly:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.clutch import build_clutch_profile, get_player_clutch_stats

async def main():
    async with NBAClient() as client:
        response = await get_player_clutch_stats(client, player_id=201939)

    # Last 30 seconds, score within 3 points — much tighter than standard
    if response.last_30_sec_lte_3_pts:
        profile = build_clutch_profile(
            201939, "Stephen Curry", "GSW",
            response.overall,
            response.last_30_sec_lte_3_pts,
            min_threshold=5.0,   # lower threshold for very tight window
        )
        print(f"Last 30 sec (≤3 pts): score = {profile.score}")

asyncio.run(main())
```

---

## Composite Score Formula

The `clutch_score` formula is designed to be interpretable:

| Component | Weight | Rationale |
|-----------|--------|-----------|
| `ts_delta * 10` | Largest | Shooting quality under pressure is the most repeatable signal |
| `ato_delta * 3` | Medium | Decision-making in pressure reflects composure |
| `plus_minus * 0.5` | Smallest | Team outcome has many confounders (teammates, matchups) |

A score near **0** is league-average clutch performance. Positive scores indicate better-than-baseline performance in clutch situations; negative scores indicate decline.

The **5-minute minimum** (`min_threshold`) exists because small samples produce noisy results — a player who hits one shot in 2 clutch minutes can have an extreme TS% delta that does not reflect their true ability.
