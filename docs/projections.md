# fastbreak.projections

Per-game statistical projections for a single player against a specified upcoming opponent. Each stat is produced by blending the player's recent form against their season mean via **Empirical Bayes shrinkage**, then applying small heuristic adjustments for opponent defense, rest, and home/away. The result carries enough information to answer sportsbook-style questions via `prob_over(line)`.

The module has no ML training step and no scipy dependency — survival functions are computed from stdlib `math.erfc` (Normal) and iterative CDF summation (Poisson). The only tunable inputs are the Empirical Bayes priors in `fastbreak.projections_priors`, which are regenerated offline from league-wide game log data.

```python
from fastbreak.projections import (
    # Data classes
    StatProjection,
    PlayerProjection,
    # Type aliases + constants
    ProjectionStat,
    DistributionFamily,
    STATS,
    # Pure math helpers
    empirical_bayes_blend,
    normal_sf,
    poisson_sf,
    adjust_for_opponent,
    adjust_for_rest,
    adjust_for_home,
    # Async orchestrator
    project_player,
)
from fastbreak.projections_priors import StatPrior, STAT_PRIORS
```

---

## Data Classes

### `StatProjection`

```python
@dataclass(frozen=True, slots=True)
class StatProjection:
    stat: ProjectionStat
    mean: float
    stdev: float
    distribution: DistributionFamily
    rolling_n: int
    season_mean: float
    rolling_mean: float
    adjustments: dict[str, float]
```

A frozen dataclass holding one stat's projection for a single upcoming game.

| Field | Type | Description |
|-------|------|-------------|
| `stat` | `ProjectionStat` | Stat key: one of `"pts"`, `"reb"`, `"ast"`, `"fg3m"` |
| `mean` | `float` | Final projected mean after blending + all adjustments (floored at 0) |
| `stdev` | `float` | Spread parameter. For Normal: residual stdev of recent games (floored). For Poisson: `sqrt(mean)` |
| `distribution` | `DistributionFamily` | `"normal"` (pts, reb, ast) or `"poisson"` (fg3m) |
| `rolling_n` | `int` | Actual number of recent games averaged (may be < requested `rolling_n` early in season) |
| `season_mean` | `float` | Unblended mean across all season games (the prior anchor) |
| `rolling_mean` | `float` | Unblended mean across the last `rolling_n` games |
| `adjustments` | `dict[str, float]` | Additive deltas applied on top of the blend: keys `"opponent"`, `"rest"`, `"home"` |

**Method**

```python
def prob_over(self, line: float) -> float
```

Returns `P(X > line)` under the stat's distribution. Dispatches to `normal_sf` for Normal stats and `poisson_sf` for Poisson stats. Useful for sportsbook-style totals (e.g. `proj.stats["pts"].prob_over(24.5)`).

---

### `PlayerProjection`

```python
@dataclass(frozen=True, slots=True)
class PlayerProjection:
    player_id: int
    player_name: str
    opponent_team_id: int
    game_date: date
    is_home: bool
    stats: dict[ProjectionStat, StatProjection]
```

The full per-game projection for a single player against a single opponent.

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Display name (pass-through — not looked up) |
| `opponent_team_id` | `int` | NBA team ID of the upcoming opponent |
| `game_date` | `date` | Date of the projected game |
| `is_home` | `bool` | `True` if the player's team is the home team |
| `stats` | `dict[ProjectionStat, StatProjection]` | One `StatProjection` per requested stat |

---

## Type Aliases and Constants

```python
ProjectionStat = Literal["pts", "reb", "ast", "fg3m"]
DistributionFamily = Literal["normal", "poisson"]
STATS: tuple[ProjectionStat, ...] = ("pts", "reb", "ast", "fg3m")
```

`STATS` is the canonical tuple of stats the module supports. `project_player` defaults to projecting all four. Pass a subset (e.g. `stats=("pts", "fg3m")`) to skip the others.

Distribution family by stat:

| Stat | Distribution | Rationale |
|------|--------------|-----------|
| `pts` | Normal | Sum of many independent contributions — roughly Gaussian |
| `reb` | Normal | Same logic at lower mean, but still well-approximated by Normal |
| `ast` | Normal | Less volatile than scoring; Normal is fine |
| `fg3m` | Poisson | Low integer counts with right skew; Normal would assign mass to negatives |

For Normal stats, `stdev = max(sqrt(residual_variance_of_recent_games), floor)`. Floors are `pts=3.0`, `reb=1.5`, `ast=1.5` — set to prevent over-confident projections when a short rolling window happens to be stable. For Poisson, `stdev = sqrt(max(mean, 1e-6))` (Poisson's λ=mean=variance property).

---

## Function Reference

### `empirical_bayes_blend`

```python
def empirical_bayes_blend(
    rolling_mean: float,
    season_mean: float,
    *,
    n: int,
    tau_sq: float,
    sigma_sq: float,
) -> float
```

James–Stein shrinkage toward the season mean.

```
w = tau_sq / (tau_sq + sigma_sq / n)
blended = w * rolling_mean + (1 - w) * season_mean
```

Where `tau_sq` (τ²) is **between-player variance** of season means — the prior width — and `sigma_sq` (σ²) is **within-player** game-to-game variance — observation noise.

- As `n` grows, `sigma_sq / n` shrinks, so `w → 1` (trust recent form).
- When `sigma_sq` dominates `tau_sq`, `w → 0` (regress to season anchor).
- If `sigma_sq == 0`: the MLE is trusted completely (returns `rolling_mean`).
- If `tau_sq == 0`: no prior strength; returns `season_mean`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rolling_mean` | `float` | required | Mean of the player's last `n` games |
| `season_mean` | `float` | required | Mean across the player's season (prior anchor) |
| `n` | `int` | required | Number of recent games averaged; must be > 0 |
| `tau_sq` | `float` | required | Between-player variance of season means |
| `sigma_sq` | `float` | required | Within-player game-to-game variance |

**Returns** `float` — blended mean, always between `rolling_mean` and `season_mean`.

**Raises** `ValueError` if `n <= 0` or either variance is negative.

---

### `normal_sf`

```python
def normal_sf(*, x: float, mean: float, stdev: float) -> float
```

Survival function `P(X > x)` for `X ~ Normal(mean, stdev²)`. Uses `math.erfc` from stdlib; no scipy dependency.

**Raises** `ValueError` if `stdev <= 0`.

```python
normal_sf(x=24.5, mean=26.1, stdev=5.0)  # → 0.625
```

---

### `poisson_sf`

```python
def poisson_sf(*, line: float, lam: float) -> float
```

Survival function `P(X > floor(line))` for `X ~ Poisson(lam)`. `line` may be fractional — the result equals `P(X >= ceil(line))` for non-integer lines, matching sportsbook convention where 2.5 threes means "at least 3".

Computed by summing the Poisson CDF iteratively (stable for typical NBA stat lines where `k < ~30`).

**Raises** `ValueError` if `lam < 0`.

```python
poisson_sf(line=2.5, lam=3.1)  # P(X >= 3) under Poisson(3.1) → 0.598
poisson_sf(line=2,   lam=3.1)  # P(X > 2)  under Poisson(3.1) → 0.598 (same bucket)
poisson_sf(line=-1,  lam=3.1)  # → 1.0
poisson_sf(line=5,   lam=0)    # → 0.0 (all mass at 0)
```

---

### `adjust_for_opponent`

```python
def adjust_for_opponent(
    *,
    blended_mean: float,
    stat: ProjectionStat,
    opp_def_rating: float,
    league_avg_def_rating: float,
) -> float
```

Additive delta for opposing defense strength. **Only applied to scoring stats (`pts`, `fg3m`)** — rebounds and assists are driven more by pace and role than defensive rating.

Formula: `delta = blended_mean * clamp((opp_def_rating - league_avg) / league_avg, -0.15, 0.15)`.

Higher opponent defensive rating (worse defense) produces a positive delta; the clamp prevents any single matchup from swinging the projection more than ±15%. Returns `0.0` for `reb` and `ast`, or when `league_avg_def_rating == 0`.

---

### `adjust_for_rest`

```python
def adjust_for_rest(
    *, blended_mean: float, stat: ProjectionStat, days_rest: int
) -> float
```

Additive delta for days of rest.

| `days_rest` | Fraction of blended mean |
|-------------|--------------------------|
| 0 (back-to-back) | −4% |
| 1 or 2 (normal) | 0% |
| 3+ (extended) | +1.5% |

Assists are halved (fatigue affects decision-making less than scoring and rebounding).

---

### `adjust_for_home`

```python
def adjust_for_home(
    *, blended_mean: float, stat: ProjectionStat, is_home: bool
) -> float
```

Additive delta of ±2% of the blended mean (`+2%` at home, `−2%` on the road). The `stat` parameter is reserved for future per-stat scaling but is currently unused.

---

### `project_player`

```python
async def project_player(
    client: NBAClient,
    *,
    player_id: int,
    player_name: str,
    opponent_team_id: int,
    is_home: bool,
    game_date: date,
    season: str,
    days_rest: int,
    rolling_n: int = 10,
    stats: Sequence[ProjectionStat] = STATS,
) -> PlayerProjection
```

The main entry point. Concurrently fetches the player's season game log and league-wide team estimated metrics, then builds one `StatProjection` per requested stat.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `player_name` | `str` | required | Display name (pass-through) |
| `opponent_team_id` | `int` | required | NBA team ID of the upcoming opponent |
| `is_home` | `bool` | required | `True` if the player's team is home |
| `game_date` | `date` | required | Date of the projected game |
| `season` | `str` | required | Season in `YYYY-YY` format (e.g. `"2025-26"`) |
| `days_rest` | `int` | required | Days of rest before the game (0 = back-to-back) |
| `rolling_n` | `int` | `10` | Number of most-recent games for the rolling mean |
| `stats` | `Sequence[ProjectionStat]` | `STATS` | Stats to project |

**Returns** `PlayerProjection` populated with one `StatProjection` per stat.

**Raises** `ValueError` when the player has no logged games for the season, or when the opponent team is missing from `TeamEstimatedMetrics` or lacks an `e_def_rating`.

The caller is responsible for supplying the matchup context — this module does not consult the schedule or infer the next game. This keeps the core layer pure and composable; see the "tonight's game" example below for how to derive `days_rest` and `is_home` from `fastbreak.schedule`.

---

## Empirical Bayes Explained

Projections blend two signals: **recent form** (the last `rolling_n` games) and the **season anchor** (the player's full season mean). Trusting recent form too eagerly overreacts to a two-game hot streak; trusting the season mean too rigidly ignores real adjustments in role or shot selection. Empirical Bayes solves this with a shrinkage weight that depends on sample size and the ratio of signal to noise:

```
w = tau_sq / (tau_sq + sigma_sq / n)
blended = w * rolling_mean + (1 - w) * season_mean
```

- **τ²** (`tau_sq`) is the between-player variance of season means — how much players in the league differ from each other in their season averages. Large τ² means there's a lot of "signal" to distinguish players by, so we should listen to individual data.
- **σ²** (`sigma_sq`) is the within-player game-to-game variance — the noise floor for any one player's per-game output. Large σ² means any `n`-game sample is unreliable.

As `n → ∞`, `sigma_sq / n → 0`, so `w → 1` and the blended mean tracks `rolling_mean` exactly. When `n` is small relative to `σ²/τ²`, `w` is small and the blended mean regresses most of the way to `season_mean`.

### Current priors (2025-26 regular season)

From `src/fastbreak/projections_priors.py`:

| stat | τ² | σ² | season | n_players | n_games |
|------|------|------|---------|-----------|---------|
| pts  | 36.1156 | 39.8224 | 2025-26 | 335 | 20785 |
| reb  | 4.6643  | 6.3483  | 2025-26 | 335 | 20785 |
| ast  | 3.2403  | 3.7092  | 2025-26 | 335 | 20785 |
| fg3m | 0.7310  | 1.6802  | 2025-26 | 335 | 20785 |

The ratio `τ²/σ²` controls how quickly each stat's blend trusts recent form. For `pts` it's ≈0.91 (signal and noise are close, so `w ≈ 0.91` at `n=10`); for `fg3m` it's ≈0.44, so the blend regresses harder toward the season mean.

### Regenerating priors

Priors live in `src/fastbreak/projections_priors.py` and are regenerated by `scripts/compute_projection_priors.py`:

```bash
uv run python scripts/compute_projection_priors.py
```

The script:

1. Queries `LeagueDashPlayerStats` and filters qualifying players (GP ≥ 30, MIN ≥ 15 per game).
2. Fetches each qualifying player's `PlayerGameLog` concurrently.
3. Computes per-stat **σ²** as the pool-averaged within-player variance across all games.
4. Computes per-stat **τ²** as the variance of season means across all qualifying players.
5. Overwrites `projections_priors.py` with the fresh values.

It takes 1–3 minutes due to rate-limited concurrent fetches (`request_delay=1.0` pacing). Run it at the start of a new season, and periodically mid-season if the player pool has shifted (injuries, trades, rotation changes).

---

## Complete Examples

### Direct call with a known matchup

Use this pattern when you already know the opponent, venue, and days of rest — for example, in a nightly batch job that iterates over a pre-loaded schedule.

```python
import asyncio
from datetime import date

from fastbreak import NBAClient, project_player


async def main() -> None:
    async with NBAClient() as client:
        proj = await project_player(
            client,
            player_id=2544,            # LeBron James
            player_name="LeBron James",
            opponent_team_id=1610612744,  # Golden State Warriors
            is_home=True,
            game_date=date(2026, 5, 6),
            season="2025-26",
            days_rest=1,
            rolling_n=10,
        )

    print(f"{proj.player_name} vs. team {proj.opponent_team_id} on {proj.game_date}")
    for name, sp in proj.stats.items():
        print(f"  {name:5s}: mean={sp.mean:5.2f}  stdev={sp.stdev:4.2f}  dist={sp.distribution}")
        # Sportsbook-style P(over) for three lines around the mean.
        for line in (sp.mean - sp.stdev, sp.mean, sp.mean + sp.stdev):
            print(f"    P(over {line:5.2f}) = {sp.prob_over(line):.3f}")


asyncio.run(main())
```

### Tonight's game (derive context from schedule)

A real use case rarely knows the opponent in advance. This pattern uses `fastbreak.schedule` helpers to find the next game, then derives `is_home` and `days_rest` from the schedule.

```python
import asyncio
from datetime import date

from fastbreak import NBAClient, project_player
from fastbreak.schedule import (
    days_rest_before_game,
    game_dates_from_schedule,
    get_team_schedule,
)

LAKERS_TEAM_ID = 1610612747
LEBRON_PLAYER_ID = 2544


async def main() -> None:
    today = date.today()

    async with NBAClient() as client:
        schedule = await get_team_schedule(client, team_id=LAKERS_TEAM_ID)

        todays_game = next(
            (g for g in schedule
             if g.game_date_est and g.game_date_est[:10] == today.isoformat()),
            None,
        )
        if todays_game is None or todays_game.home_team is None or todays_game.away_team is None:
            print(f"Lakers have no confirmed opponent on {today}.")
            return

        is_home = todays_game.home_team.team_id == LAKERS_TEAM_ID
        opponent_team_id = (
            todays_game.away_team.team_id if is_home else todays_game.home_team.team_id
        )

        # Derive days of rest by appending today's game to prior game dates.
        prior_dates = [d for d in game_dates_from_schedule(schedule) if d < today]
        synthetic = [*prior_dates, today]
        days_rest = days_rest_before_game(synthetic, len(synthetic) - 1) or 0

        proj = await project_player(
            client,
            player_id=LEBRON_PLAYER_ID,
            player_name="LeBron James",
            opponent_team_id=opponent_team_id,
            is_home=is_home,
            game_date=today,
            season="2025-26",
            days_rest=days_rest,
        )

    for name, sp in proj.stats.items():
        print(f"  {name:5s}: mean={sp.mean:5.2f}  rolling={sp.rolling_mean:5.2f}  season={sp.season_mean:5.2f}")


asyncio.run(main())
```

---

## Known Limitations

- **Heuristic, not ML.** The ±15% opponent clamp, −4% b2b, +1.5% extended-rest, and ±2% home fractions are hand-picked, not learned. They nudge the blend in the right direction without overwhelming it, but a proper model would learn these interactions from historical data.
- **Caller supplies the matchup.** `project_player` does not consult the schedule; `opponent_team_id`, `is_home`, `game_date`, and `days_rest` are all explicit. This keeps the core pure; see the second example above for how to derive them from `fastbreak.schedule`.
- **Opponent defense only affects scoring stats.** `adjust_for_opponent` returns `0` for `reb` and `ast` — those stats are more pace- and role-driven than defensive rating explains.
- **No injury or DNP handling.** Game logs are taken as-is; a three-game absence does not discount the rolling window.
- **Minutes are not modeled.** An 18-minute blowout and a 36-minute game contribute equally to `rolling_mean`. Inspect `rolling_mean` vs `season_mean` when players have volatile minutes.
- **Priors are league-wide, not positional.** `τ²` and `σ²` pool across all qualifying players — a guard-vs-big split for `reb` and `ast` would be an obvious v2 improvement.

---

## Related

- `fastbreak.projections_priors` — the `StatPrior` dataclass and the `STAT_PRIORS` dict. Data-only module, regenerated by `scripts/compute_projection_priors.py`.
- `fastbreak.schedule` — helpers for deriving `game_date`, `is_home`, and `days_rest` from the league schedule.
- `fastbreak.estimated` — the `TeamEstimatedMetrics` endpoint fetched internally for opponent defensive rating.
- `fastbreak.players` — for looking up `player_id` from a name string before projecting.
