# fastbreak.metrics

Pure computation functions for derived basketball metrics. No async, no client, no network
calls — every function takes plain Python floats and returns a float (or None when the
denominator is zero). The module is designed to work naturally with data returned by the
fastbreak API helpers, but it has no dependency on them and can be used with any data source.

## Overview

```python
from fastbreak.metrics import (
    # Efficiency
    true_shooting, effective_fg_pct, game_score, relative_ts, relative_efg,
    # Rate stats
    per_36, per_100, free_throw_rate, three_point_rate, ast_to_tov, assist_ratio,
    # Counting / thresholds
    is_double_double, is_triple_double,
    # On-floor impact
    usage_pct, ast_pct, oreb_pct, dreb_pct, stl_pct, blk_pct,
    # PER
    pace_adjusted_per, per,
    # Team ratings
    ortg, drtg, net_rtg,
    # Win metrics
    offensive_win_shares,
    # Possession estimate
    possessions,
    # Rolling / windowed
    rolling_avg,
    # League context
    LeagueAverages,
)
```

A few things to know before using:

- Every function is a pure computation — same inputs, same output, no side effects.
- Functions that divide return `None` when the denominator is zero. Exceptions: `game_score`, `is_double_double`, and `is_triple_double` never return `None`.
- `nan` and `inf` inputs produce unspecified results — sanitize before passing in.
- Scale doesn't matter as long as all inputs for one call are on the same scale (per-game, per-36, season totals, etc.).

---

## LeagueAverages

`LeagueAverages` is the league context object required by relative and normalised metrics
(`relative_ts`, `relative_efg`, and the PER pipeline). It is a frozen dataclass with
`slots=True`.

```python
from fastbreak.metrics import LeagueAverages

lg = LeagueAverages(
    lg_pts=114.0,
    lg_fga=88.5,
    lg_fta=22.0,
    lg_ftm=17.5,
    lg_oreb=10.5,
    lg_treb=44.0,
    lg_ast=26.0,
    lg_fgm=42.0,
    lg_fg3m=13.0,
    lg_tov=13.5,
    lg_pf=19.5,
)
```

### Fields

All fields are `float`. Pass per-team-per-game averages (the scale used by
`get_league_averages()`), or whole-league totals — as long as the scale is consistent
across all fields.

| Field | Description |
|---|---|
| `lg_pts` | League average points per team per game |
| `lg_fga` | League average field goal attempts |
| `lg_fta` | League average free throw attempts |
| `lg_ftm` | League average free throws made |
| `lg_oreb` | League average offensive rebounds |
| `lg_treb` | League average total rebounds |
| `lg_ast` | League average assists |
| `lg_fgm` | League average field goals made |
| `lg_fg3m` | League average 3-pointers made |
| `lg_tov` | League average turnovers |
| `lg_pf` | League average personal fouls |

### Computed properties

These are recalculated on each property access from the stored fields. They are used
internally by metric functions but are also available to callers.

| Property | Formula | Description |
|---|---|---|
| `lg_pace` | `lg_fga - lg_oreb + lg_tov + 0.44·lg_fta` | Possession estimate (Dean Oliver formula) used as the league pace proxy in PER. Numerically equivalent to possessions per game (~95–105 for modern NBA). Pass `team_pace` using the same formula applied to team totals. |
| `vop` | `lg_pts / (lg_fga - lg_oreb + lg_tov + 0.44·lg_fta)` | Value of a Possession |
| `drb_pct` | `(lg_treb - lg_oreb) / lg_treb` | League defensive rebound rate |
| `factor` | `2/3 - (0.5·(lg_ast/lg_fgm)) / (2·(lg_fgm/lg_ftm))` | Assist factor used in PER |
| `ts` | `lg_pts / (2·(lg_fga + 0.44·lg_fta))` | League average True Shooting% |
| `efg` | `(lg_fgm + 0.5·lg_fg3m) / lg_fga` | League average eFG% |

### Validation

`__post_init__` raises `ValueError` under the following conditions:

- Any field is negative.
- Any of the denominator fields (`lg_fga`, `lg_treb`, `lg_fgm`, `lg_ftm`, `lg_pf`) is zero.
- `lg_oreb > lg_treb` (offensive rebounds exceed total rebounds).
- The `vop` compound denominator (`lg_fga - lg_oreb + lg_tov + 0.44·lg_fta`) is not
  positive.

---

## Getting league averages from the API

The recommended way to populate `LeagueAverages` is via `get_league_averages()` from
`fastbreak.teams`. It fetches per-game stats for all 30 teams using `LeagueDashTeamStats`
and computes means across all teams.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.teams import get_league_averages

async def main():
    async with NBAClient() as client:
        # Current season
        lg = await get_league_averages(client)

        # Specific season
        lg_2024 = await get_league_averages(client, season="2024-25")

    print(f"League TS%: {lg.ts:.3f}")
    print(f"League eFG%: {lg.efg:.3f}")
    print(f"League pace: {lg.lg_pace:.1f}")

asyncio.run(main())
```

Pace is estimated using the Dean Oliver possession formula:
`poss = fga - oreb + tov + 0.44 * fta`.

---

## FourFactors

```python
@dataclass(frozen=True, slots=True)
class FourFactors:
    efg_pct: float | None
    tov_pct: float | None
    oreb_pct: float | None
    ftr: float | None
```

Immutable result type returned by `four_factors()`.

### four_factors

```python
def four_factors(fgm: float, fg3m: float, fga: float, tov: float, fta: float, oreb: float, opp_dreb: float) -> FourFactors
```

Compute Dean Oliver's Four Factors for a single team performance.

| Factor | Field | Formula |
|---|---|---|
| Shooting efficiency | `efg_pct` | `(FGM + 0.5×FG3M) / FGA` |
| Ball security | `tov_pct` | `TOV / (FGA + 0.44×FTA + TOV)` |
| Second chances | `oreb_pct` | `OREB / (OREB + opp_DREB)` |
| Getting to the line | `ftr` | `FTA / FGA` |

Note: `oreb_pct` here is the **team-level** formula (no per-minute correction) — different from the player-level `oreb_pct()` function also in this module.

```python
ff = four_factors(fgm=40, fg3m=12, fga=88, tov=14, fta=20, oreb=10, opp_dreb=32)
print(ff.efg_pct)   # 0.523
print(ff.tov_pct)   # 0.126
```

---

## Function Reference

### Return value conventions

All functions that perform division return `float | None`. A `None` return means the
computation was not possible due to a zero denominator — most commonly because a player
did not attempt any shots, play any minutes, or face any opponent possessions in the
relevant sample. Always check for `None` before using a return value in downstream
calculations:

```python
ts = true_shooting(pts=0, fga=0, fta=0)
if ts is not None:
    rel = relative_ts(ts, lg)
```

`game_score`, `is_double_double`, and `is_triple_double` always return a value and never
return `None`.

---

### Efficiency Metrics

#### `true_shooting`

```python
def true_shooting(pts: float, fga: float, fta: float) -> float | None
```

True Shooting percentage — shooting efficiency that accounts for all three shot types
(2-pointers, 3-pointers, and free throws).

**Formula:** `TS% = pts / (2 * (fga + 0.44 * fta))`

The 0.44 multiplier on FTA reflects that not every free-throw trip consumes a full
possession (e.g., an and-one trip costs roughly 0.44 possessions rather than 1.0).

Values above 1.0 are valid in rare edge cases (player draws many and-one free throws
on a very small FGA sample). Always check before clamping.

Returns `None` when both `fga` and `fta` are zero.

```python
ts = true_shooting(pts=28, fga=18, fta=6)   # → 0.678
ts = true_shooting(pts=0,  fga=0,  fta=0)   # → None
```

---

#### `effective_fg_pct`

```python
def effective_fg_pct(fgm: float, fg3m: float, fga: float) -> float | None
```

Effective Field Goal percentage — adjusts FG% to give proper credit for 3-pointers,
which are worth 1.5× a made 2-pointer.

**Formula:** `eFG% = (fgm + 0.5 * fg3m) / fga`

Values above 1.0 are valid on small samples where a player makes many 3-pointers
relative to their total attempts (e.g., 3-for-3 from three with 0 two-point attempts).

Returns `None` when `fga` is zero.

```python
efg = effective_fg_pct(fgm=11, fg3m=4, fga=20)  # → 0.65
```

---

#### `game_score`

```python
def game_score(
    pts: float, fgm: float, fga: float, ftm: float, fta: float,
    oreb: float, dreb: float, stl: float, ast: float, blk: float,
    pf: float, tov: float,
) -> float
```

Hollinger's Game Score — a single number summarising a box score line. Roughly calibrated
so that 10 is an average game and 40+ is exceptional. Can be negative for very poor
shooting lines.

**Formula:**
```
GmSc = PTS + 0.4*FGM - 0.7*FGA - 0.4*(FTA - FTM)
       + 0.7*OREB + 0.3*DREB + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV
```

Never returns `None`.

```python
gs = game_score(
    pts=28, fgm=11, fga=19, ftm=7, fta=9,
    oreb=1, dreb=8, stl=2, ast=8, blk=1, pf=3, tov=4,
)
# → 24.5
```

---

#### `relative_ts`

```python
def relative_ts(player_ts: float | None, lg: LeagueAverages) -> float | None
```

Player True Shooting% minus the league average TS% (`lg.ts`). A positive value means
the player is more efficient than league average.

Returns `None` when `player_ts` is `None` (no shot attempts).

```python
ts  = true_shooting(pts=30, fga=20, fta=5)
rel = relative_ts(ts, lg)   # positive → above-average shooter
```

---

#### `relative_efg`

```python
def relative_efg(player_efg: float | None, lg: LeagueAverages) -> float | None
```

Player Effective Field Goal% minus the league average eFG% (`lg.efg`). A positive value
means the player generates more value per field goal attempt than the league average.

Returns `None` when `player_efg` is `None` (no field goal attempts).

---

### Rate Stats

#### `per_36`

```python
def per_36(stat: float, minutes: float) -> float | None
```

Normalise a counting stat to a per-36-minute pace. 36 minutes is the conventional
baseline, roughly equivalent to a starter's workload.

**Formula:** `per_36 = stat * 36 / minutes`

Returns `None` when `minutes` is zero.

```python
pts_per_36 = per_36(stat=20, minutes=30)  # → 24.0
reb_per_36 = per_36(stat=8,  minutes=30)  # → 9.6
```

---

#### `per_100`

```python
def per_100(stat: float, poss: float) -> float | None
```

Normalize a counting stat to a per-100-possessions rate.

`per_100 = stat × 100 / poss`

Prefer per-100 over per-36 when comparing players across eras with different league paces (e.g., 1970s ~105 poss/game vs. 2020s ~100 poss/game).

To get team-level possessions: `possessions(fga, oreb, tov, fta)` from this module.

Returns `None` when possessions are zero.

```python
pts_per_100 = per_100(stat=25, poss=96.4)  # → 25.934
reb_per_100 = per_100(stat=10, poss=100)   # → 10.0
```

---

#### `free_throw_rate`

```python
def free_throw_rate(fta: float, fga: float) -> float | None
```

Free Throw Rate — how aggressively a player attacks the foul line relative to their
volume of field goal attempts.

**Formula:** `FTr = fta / fga`

Values above 1.0 are valid for elite attackers who draw more free throw trips than
field goal attempts. Returns `None` when `fga` is zero.

```python
ftr = free_throw_rate(fta=8, fga=15)  # → 0.533
```

---

#### `three_point_rate`

```python
def three_point_rate(fg3a: float, fga: float) -> float | None
```

Three-Point Attempt Rate — the share of a player's field goal attempts that come from
beyond the arc.

**Formula:** `3PAr = fg3a / fga`

Returns `None` when `fga` is zero.

```python
tpar = three_point_rate(fg3a=9, fga=18)  # → 0.5
```

---

#### `tov_pct`

```python
def tov_pct(fga: float, fta: float, tov: float) -> float | None
```

Turnover percentage — share of possessions ending in a turnover.

`TOV% = TOV / (FGA + 0.44 × FTA + TOV)`

The denominator is Dean Oliver's possession estimate (same 0.44 FTA multiplier as `true_shooting` and `usage_pct`). Together with `effective_fg_pct`, `free_throw_rate`, and the team offensive rebound rate, this completes the Four Factors framework.

Returns a **0–1 fraction** (e.g. `0.126` for 12.6%). This matches the scale used by `FourFactorsStatistics.teamTurnoverPercentage` (from the box score four-factors endpoint). It does **not** match `AdvancedTeamStatistics.estimatedTeamTurnoverPercentage`, which the NBA advanced box-score endpoint returns on a **0–100 scale** (e.g. `12.6`). Multiply by 100 before comparing against that field.

Returns `None` when all three inputs are zero.

---

#### `ast_to_tov`

```python
def ast_to_tov(ast: float, tov: float) -> float | None
```

Assist-to-Turnover ratio — a measure of playmaking efficiency. Higher is better; elite
playmakers typically sustain values above 3.0 for a full season.

**Formula:** `AST/TOV = ast / tov`

Returns `None` when `tov` is zero to avoid division by zero.

```python
ratio = ast_to_tov(ast=9, tov=3)  # → 3.0
```

---

#### `assist_ratio`

```python
def assist_ratio(ast: float, fga: float, fta: float, tov: float) -> float | None
```

Assist Ratio — the percentage of a player's total possessions used that end in an assist.
Unlike `ast_to_tov`, this accounts for volume by normalising against all possession-ending
events, not just turnovers.

**Formula:** `AST Ratio = AST / (FGA + 0.44×FTA + AST + TOV) × 100`

The denominator includes field goal attempts, the FTA possession estimate, assists, and
turnovers — everything that "uses" a possession for or by the player.

Returns `None` when the denominator is zero (no activity at all).

```python
ratio = assist_ratio(ast=8, fga=0, fta=0, tov=3)   # pure passer: → 72.7
ratio = assist_ratio(ast=8, fga=18, fta=6, tov=2)  # typical guard
```

---

### Counting / Thresholds

Both functions operate on the five traditional counting categories and never return `None`.

#### `is_double_double`

```python
def is_double_double(pts: float, reb: float, ast: float, stl: float, blk: float) -> bool
```

Returns `True` if at least **two** of the five counting categories (points, rebounds,
assists, steals, blocks) are at 10 or above.

```python
is_double_double(pts=22, reb=11, ast=4, stl=1, blk=0)  # → True
is_double_double(pts=18, reb=9,  ast=4, stl=1, blk=0)  # → False
```

---

#### `is_triple_double`

```python
def is_triple_double(pts: float, reb: float, ast: float, stl: float, blk: float) -> bool
```

Returns `True` if at least **three** of the five counting categories are at 10 or above.

```python
is_triple_double(pts=22, reb=11, ast=10, stl=1, blk=0)  # → True
```

---

### On-Floor Impact

These functions measure what a player contributes while on the court, expressed as a
percentage of team or opponent opportunities. All use the same scaling pattern:
`stat * (team_mp / 5) / (mp * opportunity)`, which puts individual and team counts on a
per-person scale by dividing team minutes by 5.

All return `None` when `mp` (player minutes) is zero or when the relevant opportunity
count is zero.

---

#### `usage_pct`

```python
def usage_pct(
    fga: float, fta: float, tov: float, mp: float,
    team_fga: float, team_fta: float, team_tov: float, team_mp: float,
) -> float | None
```

Usage Percentage — the share of team possessions that end with the player taking a shot,
getting to the line, or turning the ball over while they are on the floor.

**Formula:**
```
Usage% = (fga + 0.44*fta + tov) * (team_mp/5) / (mp * (team_fga + 0.44*team_fta + team_tov))
```

A usage rate of approximately 0.20 is league-average; 0.30+ is a primary scoring option.
Returns `None` when `mp` or team possessions are zero.

```python
usg = usage_pct(
    fga=18, fta=6, tov=3, mp=34,
    team_fga=88, team_fta=22, team_tov=13, team_mp=240,
)
```

---

#### `ast_pct`

```python
def ast_pct(
    ast: float, fgm: float, mp: float, team_fgm: float, team_mp: float,
) -> float | None
```

Assist Percentage — the share of teammate field goals that the player assisted while on
the floor.

**Formula:**
```
AST% = ast / ((mp / (team_mp / 5)) * team_fgm - fgm)
```

The denominator estimates how many teammate baskets the player could have assisted:
team FGM scaled to the player's on-court time, minus the player's own makes.

Returns `None` when `mp` or `team_mp` is zero, or when the denominator is non-positive
(degenerate data, e.g. a player who made every basket their team made).

---

#### `oreb_pct`

```python
def oreb_pct(
    oreb: float, mp: float, team_oreb: float, opp_dreb: float, team_mp: float,
) -> float | None
```

Offensive Rebound Percentage — the share of available offensive boards the player
grabbed while on the floor.

**Formula:** `OREB% = oreb * (team_mp/5) / (mp * (team_oreb + opp_dreb))`

The denominator is total offensive rebounds available: every offensive missed shot that
was either grabbed by the player's team or conceded to the opponent's defense.

Returns `None` when `mp` or available rebounds are zero.

---

#### `dreb_pct`

```python
def dreb_pct(
    dreb: float, mp: float, team_dreb: float, opp_oreb: float, team_mp: float,
) -> float | None
```

Defensive Rebound Percentage — the share of available defensive boards the player
grabbed while on the floor.

**Formula:** `DREB% = dreb * (team_mp/5) / (mp * (team_dreb + opp_oreb))`

The denominator is total defensive rebounds available: every opponent miss that was
either secured defensively or retrieved by the opponent.

Returns `None` when `mp` or available rebounds are zero.

---

#### `stl_pct`

```python
def stl_pct(stl: float, mp: float, team_mp: float, opp_poss: float) -> float | None
```

Steal Percentage — the share of opponent possessions that ended in a steal by the player
while on the floor.

**Formula:** `STL% = stl * (team_mp/5) / (mp * opp_poss)`

`opp_poss` is typically estimated as: `opp_fga + 0.44*opp_fta + opp_tov - opp_oreb`.

Returns `None` when `mp` or `opp_poss` is zero.

---

#### `blk_pct`

```python
def blk_pct(blk: float, mp: float, team_mp: float, opp_fg2a: float) -> float | None
```

Block Percentage — the share of opponent 2-point field goal attempts that the player
blocked while on the floor.

**Formula:** `BLK% = blk * (team_mp/5) / (mp * opp_fg2a)`

Only 2-point attempts are used because 3-pointers are almost never blocked; including
them would dilute the signal. `opp_fg2a = opp_fga - opp_fg3a`.

Returns `None` when `mp` or `opp_fg2a` is zero.

---

### PER (Player Efficiency Rating)

PER is computed in two steps. First, `pace_adjusted_per` produces an unadjusted,
pace-normalised value (aPER) for a single player. After computing aPER for all players
in the league, you calculate a minutes-weighted league average aPER (`lg_aper`), then
call `per` to normalise to the conventional 15.0 baseline.

The league average PER is exactly 15.0 by construction. A borderline All-Star typically
registers around 25; values above 30 are rare.

---

#### `pace_adjusted_per`

```python
def pace_adjusted_per(
    fgm: float, fga: float, fg3m: float, ftm: float, fta: float,
    oreb: float, treb: float, ast: float, stl: float, blk: float,
    pf: float, tov: float, mp: float,
    team_ast: float, team_fgm: float, team_pace: float,
    lg: LeagueAverages,
) -> float | None
```

Pace-adjusted PER (aPER) — the first of two steps toward a full PER. Implements
Hollinger's unadjusted PER formula then scales by `lg_pace / team_pace` to put
fast-paced and slow-paced teams on equal footing.

**Arguments:**

| Argument | Description |
|---|---|
| `fgm` | Field goals made |
| `fga` | Field goals attempted |
| `fg3m` | Three-pointers made |
| `ftm` | Free throws made |
| `fta` | Free throws attempted |
| `oreb` | Offensive rebounds |
| `treb` | Total rebounds |
| `ast` | Assists |
| `stl` | Steals |
| `blk` | Blocks |
| `pf` | Personal fouls |
| `tov` | Turnovers |
| `mp` | Minutes played |
| `team_ast` | Team assists (same game or period as the player stats) |
| `team_fgm` | Team field goals made |
| `team_pace` | Team pace using the same possession formula as `lg.lg_pace`: `fga - oreb + tov + 0.44·fta` applied to team totals |
| `lg` | `LeagueAverages` for the season |

Returns `None` when `mp`, `team_fgm`, or `team_pace` is zero.

---

#### `per`

```python
def per(aper: float, lg_aper: float) -> float | None
```

Normalise a pace-adjusted PER to the conventional 15.0 league-average baseline.

**Formula:** `PER = aper * (15 / lg_aper)`

`lg_aper` is the minutes-weighted mean of all players' aPER values for the season.

Returns `None` when `lg_aper` is zero.

| PER range | Context |
|---|---|
| < 0 | Very poor game / season |
| ~10 | Below average |
| ~15 | League average (by definition) |
| ~20 | Good starter |
| ~25 | Borderline All-Star |
| 30+ | Elite / MVP-caliber |

---

### Team Ratings

Team ratings use the Dean Oliver possession estimate:
`possessions = fga - oreb + tov + 0.44 * fta`.

#### `possessions`

```python
def possessions(fga: float, oreb: float, tov: float, fta: float) -> float
```

Estimate the number of possessions using Dean Oliver's formula. Accounts for offensive
rebounds (which extend a possession rather than ending it) and the fractional FTA
multiplier (not all free-throw trips are standalone possessions).

**Formula:** `poss = fga - oreb + tov + 0.44 × fta`

This function never returns `None` — zero inputs simply produce zero possessions. Use
the result as the denominator for `per_100`, or pass it to `ortg`/`drtg` implicitly by
passing the raw counting stats.

```python
poss = possessions(fga=88, oreb=10, tov=13, fta=22)  # → 103.68
```

---

#### `ortg`

```python
def ortg(pts: float, fga: float, oreb: float, tov: float, fta: float) -> float | None
```

Offensive Rating — points scored per 100 possessions. Accounts for possession-ending
events (shots, turnovers, and free-throw trips) to remove the effect of pace.

Returns `None` when estimated possessions are zero.

```python
off_rtg = ortg(pts=112, fga=85, oreb=9, tov=13, fta=20)
```

---

#### `drtg`

```python
def drtg(opp_pts: float, opp_fga: float, opp_oreb: float, opp_tov: float, opp_fta: float) -> float | None
```

Defensive Rating — opponent points allowed per 100 opponent possessions. Lower is better.

The possession estimate uses the opponent's own counting stats (`opp_fga`, `opp_oreb`,
`opp_tov`, `opp_fta`), mirroring the way `ortg` uses the team's own counting stats for
the offensive possession estimate.

Returns `None` when estimated possessions are zero.

---

#### `net_rtg`

```python
def net_rtg(ortg_val: float | None, drtg_val: float | None) -> float | None
```

Net Rating — offensive rating minus defensive rating. The gold-standard summary of team
quality: positive means the team outscores opponents per possession, negative means the
reverse.

Returns `None` when either input is `None`.

```python
nr = net_rtg(ortg_val=114.2, drtg_val=110.8)  # → 3.4
```

---

#### `offensive_win_shares`

```python
def offensive_win_shares(
    pts: float, fga: float, fta: float, tov: float, lg: LeagueAverages,
) -> float | None
```

Offensive Win Shares — the player's estimated contribution to team wins through offense,
following the Basketball-Reference method.

**Formula:**
```
player_poss        = 0.96 × (fga + tov + 0.44 × fta)
marginal_offense   = pts − 0.92 × lg.vop × player_poss
marginal_pts_per_win = 0.32 × lg.lg_pts
OWS = marginal_offense / marginal_pts_per_win
```

The `0.96` factor strips out team offensive rebound extensions (which belong to the team,
not the individual). `0.92 × vop` is the replacement-level threshold — a player must
generate 8% more value than average replacement level to produce positive win shares.

Returns `None` when `lg.lg_pts` is zero.

```python
ows = offensive_win_shares(pts=28, fga=18, fta=6, tov=3, lg=lg)  # positive → above replacement
```

---

#### `pythagorean_win_pct`

```python
def pythagorean_win_pct(pts: float, opp_pts: float, exp: float = 13.91) -> float | None
```

Expected win% from point differential (Pythagorean win expectation).

`win% = pts^exp / (pts^exp + opp_pts^exp)`

The default exponent (13.91) is the basketball-specific correction; the original Pythagorean formula uses `exp=2`.

Pairs naturally with `TeamStanding.points_pg` and `TeamStanding.opp_points_pg`:

```python
expected = pythagorean_win_pct(s.points_pg, s.opp_points_pg)
luck = s.win_pct - expected   # positive = "lucky", negative = "unlucky"
```

Returns `None` when both inputs are zero.

---

### Rolling / Windowed

#### `rolling_avg`

```python
def rolling_avg(
    values: Sequence[float | None],
    window: int,
) -> list[float | None]
```

Returns a sliding-window average over a sequence of per-game stat values. This is a
pure function — no API call is needed.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `values` | `Sequence[float \| None]` | Per-game stat values in chronological order. Pass `None` for games where the stat is unavailable (DNP, injury, missing data). |
| `window` | `int` | Number of consecutive games in each window. Must be ≥ 1. |

**Returns:** `list[float | None]` — same length as `values`. Each position holds the
mean of the `window` values ending at that position, or `None` in two cases:

| Cause | Description |
|---|---|
| Warm-up | Fewer than `window` games have elapsed (positions 0 through `window - 2`) |
| Propagation | At least one `None` falls within the window |

**Raises:** `ValueError` if `window < 1`.

```python
from fastbreak.metrics import rolling_avg

pts = [22.0, 18.0, 30.0, None, 25.0, 28.0, 15.0, 24.0]
avgs_3 = rolling_avg(pts, window=3)
# [None, None, 23.33, None, None, None, 22.67, 22.33]
#  ^warm ^warm  ^ok   ^DNP  ^prop ^prop  ^ok    ^ok

avgs_5 = rolling_avg(pts, window=5)
# [None, None, None, None, None, None, None, None]
# All None — the DNP at index 3 is inside every 5-game window until index 7
```

**Common pattern — rolling average from a player game log:**

```python
from fastbreak.clients import NBAClient
from fastbreak.metrics import rolling_avg
from fastbreak.players import get_player_game_log

async def main() -> None:
    async with NBAClient() as client:
        games = await get_player_game_log(client, player_id=201939)  # Curry

    # Game log is reverse-chronological; reverse for plotting
    pts = [float(g.pts) for g in reversed(games)]
    avgs = rolling_avg(pts, window=5)

    print(f"{'Game':>5}  {'Pts':>5}  {'5-game avg':>10}")
    for i, (raw, avg) in enumerate(zip(pts, avgs, strict=True), start=1):
        avg_str = f"{avg:.2f}" if avg is not None else "    warm"
        print(f"  {i:>5}  {raw:>5.1f}  {avg_str:>10}")
```

---

## Practical Examples

### Example 1: TS% for a game log, compared to league average

This example uses hardcoded numbers to show the pure-computation workflow.

```python
from fastbreak.metrics import true_shooting, relative_ts, LeagueAverages

# Approximate 2024-25 league averages
lg = LeagueAverages(
    lg_pts=113.7,
    lg_fga=88.2,
    lg_fta=21.5,
    lg_ftm=17.0,
    lg_oreb=10.3,
    lg_treb=43.5,
    lg_ast=26.1,
    lg_fgm=42.1,
    lg_fg3m=13.1,
    lg_tov=13.3,
    lg_pf=19.2,
)

# Hypothetical game log: (pts, fga, fta)
game_log = [
    (32, 22, 8),
    (18, 14, 4),
    (27, 17, 6),
    (15, 16, 2),
    (40, 25, 10),
]

print(f"League TS%: {lg.ts:.3f}")
print()

for i, (pts, fga, fta) in enumerate(game_log, 1):
    ts = true_shooting(pts=pts, fga=fga, fta=fta)
    rel = relative_ts(ts, lg)
    if ts is not None and rel is not None:
        direction = "above" if rel > 0 else "below"
        print(f"Game {i}: TS%={ts:.3f}  ({rel:+.3f} {direction} league avg)")
    else:
        print(f"Game {i}: no shot attempts")
```

### Example 2: Full PER pipeline with live API data

PER is a two-step calculation:

1. Call `pace_adjusted_per()` for **every** qualifying player in the league to produce an
   aPER value per player.
2. Compute the minutes-weighted league-average aPER (`lg_aper`), then call `per()` to
   normalise each player's aPER to the 15.0 baseline.

Using a single player's own games to compute `lg_aper` is incorrect — it normalises the
player against themselves, pushing every game's PER toward 15 regardless of quality.
`lg_aper` must be derived from **all players** for the result to be meaningful.

The example below shows step 1 (computing aPER) for one player. Step 2 requires
repeating the same loop across all qualified players.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.teams import get_league_averages
from fastbreak.players import get_player_game_log
from fastbreak.metrics import pace_adjusted_per, per

PLAYER_ID = 2544   # LeBron James
TEAM_PACE = 100.0  # replace with actual team pace from box scores

async def main():
    async with NBAClient() as client:
        lg = await get_league_averages(client)
        log = await get_player_game_log(client, player_id=PLAYER_ID)

    apers: list[tuple[float, float]] = []

    for game in log:
        # For aPER we also need team_ast, team_fgm, team_pace.
        # Here we use league-average proxies; in production, join against team box scores.
        aper = pace_adjusted_per(
            fgm=game.fgm,
            fga=game.fga,
            fg3m=game.fg3m,
            ftm=game.ftm,
            fta=game.fta,
            oreb=game.oreb,
            treb=game.reb,
            ast=game.ast,
            stl=game.stl,
            blk=game.blk,
            pf=game.pf,
            tov=game.tov,
            mp=game.minutes,
            team_ast=26.0,    # league-average proxy; use actual team box score data
            team_fgm=42.0,    # league-average proxy
            team_pace=TEAM_PACE,
            lg=lg,
        )
        if aper is not None and game.minutes is not None and game.minutes > 0:
            apers.append((aper, game.minutes))

    if not apers:
        print("Insufficient data")
        return

    # Step 1 complete: print aPER per game.
    print(f"{'Min':>4}  {'aPER':>7}")
    for aper_val, minutes in apers[:5]:
        print(f"  {minutes:>4.0f}  {aper_val:>7.3f}")

    # Step 2: to convert aPER → PER you need lg_aper computed across all players:
    #
    #   all_apers = [(aper_val, minutes), ...]   # repeat above for every player
    #   total_mp  = sum(m for _, m in all_apers)
    #   lg_aper   = sum(a * m for a, m in all_apers) / total_mp
    #
    #   player_per = per(aper=aper_val, lg_aper=lg_aper)

asyncio.run(main())
```

### Example 3: Team net rating from a game's box score

This example shows how to compute ORTG, DRTG, and net rating from a single game's
counting stats, using only hardcoded numbers.

```python
from fastbreak.metrics import ortg, drtg, net_rtg

# Team's box score
team_pts  = 115
team_fga  = 87
team_oreb = 8
team_tov  = 12
team_fta  = 24

# Opponent's box score (needed for the opponent possession estimate in drtg)
opp_pts  = 108
opp_fga  = 85
opp_oreb = 9
opp_tov  = 14
opp_fta  = 20

off_rtg = ortg(pts=team_pts, fga=team_fga, oreb=team_oreb, tov=team_tov, fta=team_fta)
def_rtg = drtg(opp_pts=opp_pts, opp_fga=opp_fga, opp_oreb=opp_oreb, opp_tov=opp_tov, opp_fta=opp_fta)
net     = net_rtg(off_rtg, def_rtg)

if off_rtg and def_rtg and net:
    print(f"ORTG: {off_rtg:.1f}")
    print(f"DRTG: {def_rtg:.1f}")
    print(f"Net:  {net:+.1f}")
```

### Example 4: Double-double and triple-double detection across a season

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_game_log
from fastbreak.metrics import is_double_double, is_triple_double

PLAYER_ID = 203999  # Nikola Jokic

async def main():
    async with NBAClient() as client:
        log = await get_player_game_log(client, player_id=PLAYER_ID)

    double_doubles = 0
    triple_doubles = 0
    games_played   = 0

    for game in log:
        # game_id[:3] == "002" filters out All-Star games
        if game.game_id[:3] != "002":
            continue

        games_played += 1
        pts, reb, ast, stl, blk = (
            game.pts, game.reb, game.ast, game.stl, game.blk
        )

        if is_triple_double(pts=pts, reb=reb, ast=ast, stl=stl, blk=blk):
            triple_doubles += 1
        elif is_double_double(pts=pts, reb=reb, ast=ast, stl=stl, blk=blk):
            double_doubles += 1

    print(f"Games played:   {games_played}")
    print(f"Double-doubles: {double_doubles}")
    print(f"Triple-doubles: {triple_doubles}")
    print(f"DD/TD rate:     {(double_doubles + triple_doubles) / games_played:.1%}")

asyncio.run(main())
```

---

## Adding New Metrics

Because all functions are pure Python with no hidden state, adding a new metric requires
only adding a function to `src/fastbreak/metrics.py`. Follow the existing conventions:

1. Accept raw `float` inputs, not Pydantic models.
2. Return `float | None`, with `None` reserved for zero-denominator cases.
3. Document the formula in the docstring.
4. Use a guard at the top of the function (`if denominator == 0: return None`) rather
   than relying on Python's `ZeroDivisionError`.
