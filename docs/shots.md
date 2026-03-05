# shots — Shot Chart Analysis

The `fastbreak.shots` module provides shot chart data with x/y court coordinates, zone efficiency breakdowns, and per-zone delta vs. league average.

## Table of Contents

- [Quick Start](#quick-start)
- [Functions](#functions)
  - [get_shot_chart](#get_shot_chart)
  - [get_league_shot_zones](#get_league_shot_zones)
  - [zone_fg_pct](#zone_fg_pct)
  - [zone_breakdown](#zone_breakdown)
  - [shot_quality_vs_league](#shot_quality_vs_league)
- [Data Types](#data-types)
  - [ZoneStats](#zonestats)
  - [Shot (model)](#shot-model)
  - [LeagueWideShotZone (model)](#leaguewideshot-zone-model)
- [Common Patterns](#common-patterns)

---

## Quick Start

```python
from fastbreak.clients import NBAClient
from fastbreak.shots import (
    get_shot_chart,
    get_league_shot_zones,
    zone_breakdown,
    shot_quality_vs_league,
)

async with NBAClient() as client:
    # Fetch Steph Curry's shot chart (2025-26 season)
    response = await get_shot_chart(client, player_id=201939, season="2025-26")
    print(f"Total shots: {len(response.shots)}")

    # Zone-level efficiency
    breakdown = zone_breakdown(response.shots)
    for zone, stats in breakdown.items():
        print(f"{zone}: {stats.fgm}/{stats.fga} ({stats.fg_pct:.1%})")

    # Delta vs. league average
    lg_zones = await get_league_shot_zones(client, season="2025-26")
    deltas = shot_quality_vs_league(response.shots, lg_zones)
    for zone, delta in deltas.items():
        if delta is not None:
            print(f"{zone}: {delta:+.1%} vs league")
```

---

## Functions

### get_shot_chart

```python
async def get_shot_chart(
    client: NBAClient,
    player_id: int,
    *,
    team_id: int = 0,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    context_measure: ContextMeasure = "FGA",
) -> ShotChartDetailResponse
```

Fetch per-shot coordinate data for a player. Returns individual `Shot` objects with
x/y court coordinates (`loc_x`, `loc_y`), zone classifications, and league average FG% by zone.

| Parameter | Default | Description |
|---|---|---|
| `player_id` | required | NBA player ID |
| `team_id` | `0` | Filter to a specific team (0 = all teams) |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, `"Pre Season"` |
| `context_measure` | `"FGA"` | `"FGA"` (all attempts), `"FG3A"` (3-pointers), `"FGM"` (makes only) |

The response includes:
- `response.shots` — `list[Shot]`: Individual shot records with coordinates and result
- `response.league_averages` — `list[LeagueAverage]`: League FG% by zone (from the same API call)

> **Note:** `response.league_averages` and `get_league_shot_zones()` both provide zone averages, but they use slightly different zone structures. `get_league_shot_zones()` returns the standalone `ShotChartLeaguewide` endpoint data which is the recommended source for `shot_quality_vs_league()`.

---

### get_league_shot_zones

```python
async def get_league_shot_zones(
    client: NBAClient,
    *,
    season: Season | None = None,
) -> list[LeagueWideShotZone]
```

Fetch league-wide FG% by shot zone. This is the denominator data for `shot_quality_vs_league()` — it tells you what an average NBA player shoots from each zone.

Zone keys match `Shot.shot_zone_basic` for direct comparison.

```python
lg_zones = await get_league_shot_zones(client, season="2025-26")
# [{zone: "Restricted Area", fg_pct: 0.648, fga: 243847, ...}, ...]
```

---

### zone_fg_pct

```python
def zone_fg_pct(shots: list[Shot]) -> float | None
```

Compute FG% for a list of `Shot` objects. Returns `None` for an empty list.

```python
rim_shots = [s for s in shots if s.shot_zone_basic == "Restricted Area"]
fg_pct = zone_fg_pct(rim_shots)
# 0.648 — or None if no shots in that zone
```

**Properties verified by tests:**
- Result is always in `[0.0, 1.0]` for any non-empty list
- Returns `None` for empty list
- Consistent with `zone_breakdown()` (composition property)

---

### zone_breakdown

```python
def zone_breakdown(shots: list[Shot]) -> dict[str, ZoneStats]
```

Group shots by `shot_zone_basic` and compute FGA, FGM, and FG% per zone.
Returns `{}` for an empty shot list.

```python
breakdown = zone_breakdown(response.shots)
# {
#   "Restricted Area": ZoneStats(zone="Restricted Area", fga=142, fgm=92, fg_pct=0.648),
#   "Mid-Range":       ZoneStats(zone="Mid-Range",       fga=57,  fgm=23, fg_pct=0.404),
#   "Above the Break 3": ZoneStats(...),
#   ...
# }
```

**Invariants verified by tests (property-based):**
- `sum(v.fga for v in result.values()) == len(shots)` — total FGA is conserved
- `sum(v.fgm for v in result.values()) == total_makes` — total FGM is conserved
- Every `fg_pct` is in `[0.0, 1.0]`
- `zone_fg_pct(filtered_shots) == breakdown[zone].fg_pct` for every zone

---

### shot_quality_vs_league

```python
def shot_quality_vs_league(
    player_shots: list[Shot],
    league_zones: list[LeagueWideShotZone],
) -> dict[str, float | None]
```

Compute per-zone FG% delta vs. league average.

- **Positive delta** → player shoots above league average in that zone
- **Negative delta** → player shoots below league average
- **`None`** → zone in player shots but not in `league_zones` data

Result keys match exactly the zones in `player_shots` — league zones with no player shots are not included.

```python
deltas = shot_quality_vs_league(response.shots, lg_zones)
# {
#   "Restricted Area":   +0.058,  # 7pp above league avg
#   "Mid-Range":         -0.015,  # 1.5pp below league avg
#   "Above the Break 3": +0.043,  # Curry effect
#   ...
# }
```

**Invariants verified by tests (property-based):**
- All non-`None` deltas are in `[-1.0, 1.0]`
- Result keys are exactly the zones present in `player_shots`

---

## Data Types

### ZoneStats

```python
@dataclass(frozen=True)
class ZoneStats:
    zone: str         # matches Shot.shot_zone_basic
    fga: int          # total field goal attempts
    fgm: int          # total field goals made
    fg_pct: float | None  # fgm / fga, or None if fga == 0
```

> **Note:** `zone_breakdown()` only emits a `ZoneStats` entry when at least one shot exists in that zone (`fga >= 1`), so `fg_pct` is always a `float` in results returned by `zone_breakdown()`. `None` is only possible on a manually-constructed `ZoneStats(fga=0, ...)`.

### Shot (model)

Key fields on the `Shot` Pydantic model returned in `ShotChartDetailResponse.shots`:

| Field | Type | Description |
|---|---|---|
| `loc_x` | `int` | X coordinate (tenths of a foot, origin = hoop) |
| `loc_y` | `int` | Y coordinate (tenths of a foot, origin = hoop) |
| `shot_made_flag` | `int` | 1 = made, 0 = missed |
| `shot_attempted_flag` | `int` | Always 1 (all records are attempts) |
| `shot_zone_basic` | `str` | Zone name: `"Restricted Area"`, `"Mid-Range"`, etc. |
| `shot_zone_area` | `str` | Sub-area: `"Left Side(L)"`, `"Center(C)"`, etc. |
| `shot_zone_range` | `str` | Distance band: `"Less Than 8 ft."`, `"16-24 ft."`, etc. |
| `shot_distance` | `int` | Shot distance in feet |
| `shot_type` | `str` | `"2PT Field Goal"` or `"3PT Field Goal"` |
| `action_type` | `str` | Shot type: `"Jump Shot"`, `"Driving Layup"`, etc. |
| `period` | `int` | Quarter (1–4) or OT period |
| `game_date` | `str` | Date string (YYYYMMDD format) |
| `player_id` | `int` | NBA player ID |
| `team_id` | `int` | NBA team ID |

**Court coordinate system:** The NBA coordinate origin is at the center of the basket. `loc_x` runs left/right (negative = left), `loc_y` runs baseline-to-halfcourt. Values are in tenths of feet — divide by 10 for feet. The three-point arc is approximately 237–238 units from center.

### LeagueWideShotZone (model)

| Field | Type | Description |
|---|---|---|
| `shot_zone_basic` | `str` | Zone name (matches `Shot.shot_zone_basic`) |
| `shot_zone_area` | `str` | Sub-area |
| `shot_zone_range` | `str` | Distance band |
| `fga` | `int` | League-wide total attempts from this zone |
| `fgm` | `int` | League-wide total makes |
| `fg_pct` | `float` | League FG% from this zone |

---

## Common Patterns

### Filter shots before breakdown

```python
# Only 4th quarter shots
q4_shots = [s for s in response.shots if s.period == 4]
q4_breakdown = zone_breakdown(q4_shots)

# Only 3-pointers
three_pt_shots = [s for s in response.shots if s.shot_type == "3PT Field Goal"]
three_pt_breakdown = zone_breakdown(three_pt_shots)

# Only corner 3s
corner_3s = [s for s in response.shots
             if s.shot_zone_basic in ("Left Corner 3", "Right Corner 3")]
corner_3_pct = zone_fg_pct(corner_3s)
```

### Build a simple shot chart (coordinate data)

```python
response = await get_shot_chart(client, player_id=201939)

# Separate made and missed shots
made  = [(s.loc_x, s.loc_y) for s in response.shots if s.shot_made_flag == 1]
missed = [(s.loc_x, s.loc_y) for s in response.shots if s.shot_made_flag == 0]

# Pass to matplotlib scatter or any visualization library
# Divide coordinates by 10 to convert tenths-of-feet → feet
```

### Zone efficiency heat ranking

```python
from fastbreak.shots import zone_breakdown, shot_quality_vs_league

breakdown = zone_breakdown(response.shots)
deltas = shot_quality_vs_league(response.shots, lg_zones)

# Sort zones by how much the player exceeds league average
ranked = sorted(
    [(z, d) for z, d in deltas.items() if d is not None],
    key=lambda x: -x[1],
)
for zone, delta in ranked:
    fga = breakdown[zone].fga
    print(f"{zone}: {delta:+.1%} ({fga} attempts)")
```

### Combine with season context (playoffs vs. regular season)

```python
regular = await get_shot_chart(client, player_id=2544, season_type="Regular Season")
playoffs = await get_shot_chart(client, player_id=2544, season_type="Playoffs")

reg_breakdown = zone_breakdown(regular.shots)
po_breakdown  = zone_breakdown(playoffs.shots)

# Compare rim FG% between regular season and playoffs
rim_reg = reg_breakdown.get("Restricted Area")
rim_po  = po_breakdown.get("Restricted Area")
if rim_reg and rim_po and rim_reg.fg_pct and rim_po.fg_pct:
    print(f"Rim FG%  reg: {rim_reg.fg_pct:.1%}  playoffs: {rim_po.fg_pct:.1%}")
```

---

## Gotchas

- **`loc_x` / `loc_y` are in tenths of feet.** Divide by 10 before converting to standard court diagrams (which use feet). The three-point line is at `~237–238` units, not ~23.8 feet.
- **`season` is required for `ShotChartDetail`.** Unlike most endpoints, leaving `season=None` will be resolved to the current season by the helper, but passing an invalid season string will return an empty result set silently.
- **`context_measure="FGA"` includes all field goal attempts** (2-point and 3-point). Use `"FG3A"` to isolate three-point attempts only. This changes what shots appear in `response.shots` but does **not** affect `response.league_averages`.
- **Zone names must match exactly** between `Shot.shot_zone_basic` and `LeagueWideShotZone.shot_zone_basic` for `shot_quality_vs_league()` to compute deltas. Both come from the same NBA API field name so they should always match, but unusual zone names (like `"Backcourt"`) may only appear in player data and not in league averages — those zones receive `delta=None`.
