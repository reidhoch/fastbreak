# fastbreak.tracking

High-level helpers for NBA player-tracking data. These functions wrap the seven NBA Stats player-tracking endpoints (4 player, 3 team) and expose two profile dataclasses that fetch all sub-endpoints for a given player or team concurrently.

All async functions take an `NBAClient` instance as the first argument. The `season` parameter defaults to the current season when omitted.

```python
from fastbreak.tracking import (
    get_player_shots,
    get_player_passes,
    get_player_rebounds,
    get_player_shot_defense,
    get_team_shots,
    get_team_passes,
    get_team_rebounds,
    get_player_tracking_profile,
    get_team_tracking_profile,
    PlayerTrackingProfile,
    TeamTrackingProfile,
)
```

---

## Data Classes

### `PlayerTrackingProfile`

```python
@dataclass(frozen=True)
class PlayerTrackingProfile:
    player_id: int
    shots: PlayerDashPtShotsResponse
    passes: PlayerDashPtPassResponse
    rebounds: PlayerDashPtRebResponse
    shot_defense: PlayerDashPtShotDefendResponse
```

A frozen dataclass holding all four player tracking responses. Built by `get_player_tracking_profile`, which fetches all four endpoints concurrently.

| Field | Description |
|-------|-------------|
| `player_id` | NBA player ID |
| `shots` | Shot type, clock, dribbles, defender distance, touch time breakdowns |
| `passes` | Passes made to / received from each teammate, with AST rate and FG% |
| `rebounds` | Contested/uncontested boards by shot type, distance, number contesting |
| `shot_defense` | Opponent FG% when defended vs. normal FG% by category |

---

### `TeamTrackingProfile`

```python
@dataclass(frozen=True)
class TeamTrackingProfile:
    team_id: int
    shots: TeamDashPtShotsResponse
    passes: TeamDashPtPassResponse
    rebounds: TeamDashPtRebResponse
```

A frozen dataclass holding all three team tracking responses. Built by `get_team_tracking_profile`, which fetches all three endpoints concurrently.

| Field | Description |
|-------|-------------|
| `team_id` | NBA team ID |
| `shots` | Team shot breakdowns by type, clock, dribbles, defender distance, touch time |
| `passes` | Pass flow for every player on the team |
| `rebounds` | Team rebounding with contested/uncontested breakdown |

---

## Player Helpers

### `get_player_shots`

```python
async def get_player_shots(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtShotsResponse
```

Fetch player shot tracking data broken down by shot type, shot clock, dribbles, closest defender distance, and touch time.

**`PlayerDashPtShotsResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `overall` | `list[ShotTypeStats]` | Aggregate FGM/FGA/FG%/eFG% by shot type |
| `general_shooting` | `list[ShotTypeStats]` | General breakdown (catch & shoot, pull-up, less-than-10ft) |
| `shot_clock_shooting` | `list[ShotClockStats]` | Breakdown by shot clock range |
| `dribble_shooting` | `list[DribbleStats]` | Breakdown by number of dribbles before shot |
| `closest_defender_shooting` | `list[ClosestDefenderStats]` | Breakdown by closest defender distance |
| `closest_defender_10ft_plus_shooting` | `list[ClosestDefenderStats]` | Shots with defender 10 ft+ away |
| `touch_time_shooting` | `list[TouchTimeStats]` | Breakdown by time the player held the ball |

Each row exposes: `fgm`, `fga`, `fg_pct`, `efg_pct`, `fga_frequency`, `gp`, `games`.

---

### `get_player_passes`

```python
async def get_player_passes(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtPassResponse
```

Fetch player passing data — passes made to each teammate and passes received from each teammate, including assist rate and FG% generated.

**`PlayerDashPtPassResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `passes_made` | `list[PassMade]` | Passes the player made to each teammate |
| `passes_received` | `list[PassReceived]` | Passes the player received from each teammate |

Each `PassMade` row: `pass_to`, `pass_teammate_player_id`, `passes`, `ast`, `fgm`, `fga`, `fg_pct`, `frequency`.

Each `PassReceived` row: `pass_from`, `pass_teammate_player_id`, `passes`, `ast`, `fgm`, `fga`, `fg_pct`, `frequency`.

---

### `get_player_rebounds`

```python
async def get_player_rebounds(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtRebResponse
```

Fetch player rebounding data with contested vs. uncontested breakdowns.

**`PlayerDashPtRebResponse` fields**

| Field | Description |
|-------|-------------|
| `overall` | `OverallRebounding | None` — total `oreb`, `dreb`, `reb`, `c_reb`, `uc_reb`, `c_reb_pct`, `uc_reb_pct` |
| `by_shot_type` | Breakdown by 2FG vs. 3FG misses |
| `by_num_contested` | Breakdown by number of players contesting the rebound |
| `by_shot_distance` | Breakdown by original shot distance |
| `by_reb_distance` | Breakdown by rebound distance from the basket |

---

### `get_player_shot_defense`

```python
async def get_player_shot_defense(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtShotDefendResponse
```

Fetch shot defense data — opponent FG% when the player is the closest defender vs. league-normal FG% for each shot category.

**`PlayerDashPtShotDefendResponse` fields**

| Field | Description |
|-------|-------------|
| `defending_shots` | `list[DefendingShots]` — one row per `defense_category` |

Each `DefendingShots` row: `defense_category`, `d_fgm`, `d_fga`, `d_fg_pct`, `normal_fg_pct`, `pct_plusminus`, `freq`.

`pct_plusminus` is `d_fg_pct - normal_fg_pct` — **negative values are better** (opponent shoots below normal when this player defends).

---

## Team Helpers

### `get_team_shots`

```python
async def get_team_shots(
    client: NBAClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamDashPtShotsResponse
```

Team-level equivalent of `get_player_shots`. Same shot breakdowns aggregated at the team level.

**`TeamDashPtShotsResponse` fields**: `general_shooting`, `shot_clock_shooting`, `dribble_shooting`, `closest_defender_shooting`, `touch_time_shooting`.

---

### `get_team_passes`

```python
async def get_team_passes(
    client: NBAClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamDashPtPassResponse
```

Fetch pass flow for every player on the team — both passes made from and received by each player.

**`TeamDashPtPassResponse` fields**

| Field | Row type | Description |
|-------|----------|-------------|
| `passes_made` | `list[TeamPassMade]` | Passes made by each player (`pass_from`, `passes`, `ast`, `fgm`, `fga`, `fg_pct`) |
| `passes_received` | `list[TeamPassReceived]` | Passes received by each player |

---

### `get_team_rebounds`

```python
async def get_team_rebounds(
    client: NBAClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamDashPtRebResponse
```

Team rebounding breakdown with contested/uncontested splits.

**`TeamDashPtRebResponse` fields**: `overall`, `by_shot_type`, `by_num_contested`, `by_shot_distance`, `by_reb_distance` — same structure as `PlayerDashPtRebResponse` but keyed by team.

---

## Profile Functions

Profile functions fetch all sub-endpoints **concurrently** and return a single frozen dataclass. If any request fails, an `ExceptionGroup` is raised and in-flight requests are cancelled. For partial results, call the thin helpers individually.

### `get_player_tracking_profile`

```python
async def get_player_tracking_profile(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerTrackingProfile
```

Fetch all four player tracking endpoints concurrently and return a `PlayerTrackingProfile`.

**Example**

```python
from fastbreak.clients import NBAClient
from fastbreak.tracking import get_player_tracking_profile

async with NBAClient() as client:
    profile = await get_player_tracking_profile(client, player_id=201939)

# Shot efficiency by closest defender distance
for row in profile.shots.closest_defender_shooting:
    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"{row.close_def_dist_range:<20} {fg_str}")

# Top pass targets (by assists generated)
top_targets = sorted(profile.passes.passes_made, key=lambda r: -r.ast)[:5]
for row in top_targets:
    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"  → {row.pass_to:<22} {row.ast:.1f} AST  {fg_str} FG%")
```

---

### `get_team_tracking_profile`

```python
async def get_team_tracking_profile(
    client: NBAClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamTrackingProfile
```

Fetch all three team tracking endpoints concurrently and return a `TeamTrackingProfile`.

**Example**

```python
from fastbreak.clients import NBAClient
from fastbreak.teams import get_team_id
from fastbreak.tracking import get_team_tracking_profile

async with NBAClient() as client:
    team_id = get_team_id("Golden State Warriors")
    profile = await get_team_tracking_profile(client, team_id=team_id)

# Best passers on the team by assists generated
top_passers = sorted(profile.passes.passes_made, key=lambda r: -r.ast)[:5]
for row in top_passers:
    print(f"  {row.pass_from:<22} {row.ast:.1f} AST/g")
```

---

## Common Patterns

### Shot profile: where does a player score efficiently?

```python
from fastbreak.tracking import get_player_shots

async with NBAClient() as client:
    shots = await get_player_shots(client, player_id=201939, season="2025-26")

print("Shot type breakdown:")
for row in shots.general_shooting:
    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"  {row.shot_type:<25} {row.fga:>5.1f} FGA  {fg_str}")

print("\nShot clock urgency:")
for row in shots.shot_clock_shooting:
    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"  {row.shot_clock_range:<20} {fg_str}")
```

### Defense: does this player deter opponent shooting?

```python
from fastbreak.tracking import get_player_shot_defense

async with NBAClient() as client:
    defense = await get_player_shot_defense(client, player_id=203954)

for row in defense.defending_shots:
    if row.pct_plusminus is not None:
        label = "✓ below normal" if row.pct_plusminus < 0 else "✗ above normal"
        print(f"  {row.defense_category:<20} {row.pct_plusminus:+.3f}  {label}")
```

### Rebounding: contested vs. uncontested rate

```python
from fastbreak.tracking import get_player_rebounds

async with NBAClient() as client:
    reb = await get_player_rebounds(client, player_id=203999)

if reb.overall is not None:
    overall = reb.overall
    print(f"  Total reb:       {overall.reb:.1f}")
    print(f"  Contested:       {overall.c_reb:.1f}  ({overall.c_reb_pct:.1%})")
    print(f"  Uncontested:     {overall.uc_reb:.1f}  ({overall.uc_reb_pct:.1%})")
```

### Passing: who are a player's top assist targets?

```python
from fastbreak.tracking import get_player_passes

async with NBAClient() as client:
    passes = await get_player_passes(client, player_id=201939)

top = sorted(passes.passes_made, key=lambda r: -r.ast)[:5]
print("Top assist targets:")
for row in top:
    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"  → {row.pass_to:<22} {row.ast:.1f} AST/g  {fg_str} FG% on passes")
```

---

## Gotchas

- **`PlayerDashPtShots` uses `str` fields internally.** `player_id` and `last_n_games` are stored as strings in the `PlayerDashPtShots` endpoint (unlike all other tracking endpoints which use `int`). The helper `get_player_shots` accepts `int` from callers and converts internally — this is transparent to users.
- **`pct_plusminus` in shot defense is opponent-centric.** A negative value means the opponent shoots *below* their normal FG% with this player defending — which is good. Don't invert the sign.
- **Tracking data requires sufficient sample.** Players with limited minutes in a given segment may return empty result sets (not HTTP errors) rather than partial data. Check `response.overall is not None` before processing.
- **`per_mode="Totals"` vs. `"PerGame"`.** Passing stats scale differently under totals vs. per-game. For most comparisons use `"PerGame"` (the default).
