# matchups — Player-vs-Player Matchup Analysis

The `fastbreak.matchups` module provides player-vs-player matchup data, defensive assignment analysis, and team matchup summaries. It wraps four NBA Stats API endpoints — `LeagueSeasonMatchups`, `MatchupsRollup`, `BoxScoreMatchupsV3`, and `PlayerVsPlayer` — into a layered API: pure computation helpers, raw access wrappers, and higher-level profile builders that handle common queries like "who guards this player?" and "which matchups were most efficient?"

## Table of Contents

- [Quick Start](#quick-start)
- [Functions (raw access)](#functions-raw-access)
  - [get_season_matchups](#get_season_matchups)
  - [get_matchup_rollup](#get_matchup_rollup)
  - [get_game_matchups](#get_game_matchups)
  - [get_player_matchup_stats](#get_player_matchup_stats)
- [Functions (profile builders)](#functions-profile-builders)
  - [get_primary_defenders](#get_primary_defenders)
  - [get_defensive_assignments](#get_defensive_assignments)
  - [get_team_matchup_summary](#get_team_matchup_summary)
- [Computation Helpers](#computation-helpers)
  - [matchup_ppp](#matchup_ppp)
  - [help_defense_rate](#help_defense_rate)
  - [rank_matchups](#rank_matchups)
- [Data Types](#data-types)

---

## Quick Start

```python
from fastbreak.clients import NBAClient
from fastbreak.matchups import (
    get_primary_defenders,
    get_team_matchup_summary,
    matchup_ppp,
    rank_matchups,
)

async with NBAClient() as client:
    # Who guards Jayson Tatum the most? (top 5 by matchup minutes)
    defenders = await get_primary_defenders(
        client, player_id=1628369, season="2025-26", top_n=5
    )
    for d in defenders:
        print(f"{d.def_player_name}: {d.matchup_min:.1f} min, {d.partial_poss:.1f} poss")
```

```python
async with NBAClient() as client:
    # All Celtics-vs-Heat matchups, ranked by PPP
    summary = await get_team_matchup_summary(
        client,
        off_team_id=1610612738,  # BOS
        def_team_id=1610612748,  # MIA
        season="2025-26",
    )

ranked = rank_matchups(summary, min_poss=5.0, by="ppp", ascending=False)
for m in ranked[:5]:
    ppp = matchup_ppp(m.player_pts, m.partial_poss)
    print(f"{m.off_player_name} vs {m.def_player_name}: {ppp:.2f} PPP")
```

```python
from fastbreak.matchups import matchup_ppp, help_defense_rate

# Points per possession
ppp = matchup_ppp(player_pts=12.0, partial_poss=8.5)   # → 1.41

# Fraction of shots where help defense was involved
rate = help_defense_rate(matchup_fga=80.0, help_fga=20.0)  # → 0.2
```

---

## Functions (raw access)

### get_season_matchups

```python
async def get_season_matchups(
    client: NBAClient,
    *,
    off_player_id: int | None = None,
    def_player_id: int | None = None,
    off_team_id: int | None = None,
    def_team_id: int | None = None,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[SeasonMatchup]
```

Season-long player-vs-player matchup stats. Wraps `LeagueSeasonMatchups`. At least one filter (player or team ID) should be provided; passing no filters returns league-wide data (large response).

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `off_player_id` | `None` | Filter to one offensive player |
| `def_player_id` | `None` | Filter to one defensive player |
| `off_team_id` | `None` | Filter to one offensive team |
| `def_team_id` | `None` | Filter to one defensive team |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |

Returns `list[SeasonMatchup]`, one entry per player-pair combination that appeared together. Integer IDs are converted to strings internally (endpoint convention).

```python
# All matchups where Tatum was on offense
matchups = await get_season_matchups(client, off_player_id=1628369, season="2025-26")
# [{off_player_name: "Jayson Tatum", def_player_name: "...", matchup_min: ..., ...}, ...]
```

---

### get_matchup_rollup

```python
async def get_matchup_rollup(
    client: NBAClient,
    *,
    off_team_id: int = 0,
    def_team_id: int = 0,
    off_player_id: int = 0,
    def_player_id: int = 0,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[MatchupRollupEntry]
```

Defender-aggregated matchup stats. Wraps `MatchupsRollup`. Includes `percent_of_time` and `position` fields not available in `get_season_matchups`. Pass `0` for any ID parameter to mean "all" (endpoint convention).

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `off_team_id` | `0` | Offensive team ID (0 = all) |
| `def_team_id` | `0` | Defensive team ID (0 = all) |
| `off_player_id` | `0` | Offensive player ID (0 = all) |
| `def_player_id` | `0` | Defensive player ID (0 = all) |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |

Returns `list[MatchupRollupEntry]` with one entry per defender.

```python
# Rollup for defenders who guarded Tatum
rollup = await get_matchup_rollup(client, off_player_id=1628369, season="2025-26")
# [{def_player_name: "...", percent_of_time: 0.42, position: "F", matchup_min: ..., ...}, ...]
```

---

### get_game_matchups

```python
async def get_game_matchups(
    client: NBAClient,
    game_id: str,
) -> BoxScoreMatchupsV3Response
```

Per-game player-vs-player defensive matchup data. Wraps `BoxScoreMatchupsV3` (the preferred v3 endpoint, not the legacy `BoxScoreMatchups`).

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `game_id` | required | NBA game ID (e.g., `"0022500571"`) |

Returns a `BoxScoreMatchupsV3Response`. Access per-player matchup stats via `response.box_score_matchups.home_team.players` and `response.box_score_matchups.away_team.players`. Each player has a `matchups` list (not sorted — sort by `matchup_minutes_sort` to find the primary assignment).

```python
response = await get_game_matchups(client, game_id="0022500571")
data = response.box_score_matchups

for player in data.home_team.players[:3]:
    if player.matchups:
        top = player.matchups[0]
        stats = top.statistics
        print(
            f"{player.name_i} guarded {top.name_i}: "
            f"{stats.matchup_field_goals_made}/{stats.matchup_field_goals_attempted} "
            f"({stats.matchup_field_goals_percentage:.0%}), "
            f"{stats.partial_possessions:.1f} poss"
        )
```

---

### get_player_matchup_stats

```python
async def get_player_matchup_stats(
    client: NBAClient,
    player_id: int,
    vs_player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    measure_type: MeasureType = "Base",
) -> PlayerVsPlayerResponse
```

Detailed head-to-head comparison with on/off splits and shot area breakdowns. Wraps `PlayerVsPlayer`. Requires both player IDs.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `player_id` | required | Primary player ID |
| `vs_player_id` | required | Opposing player ID |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |
| `measure_type` | `"Base"` | `"Base"`, `"Advanced"`, `"Misc"`, `"Scoring"`, or `"Usage"` |

Returns a `PlayerVsPlayerResponse` with multiple result sets: `overall`, `on_off_court`, `shot_area_on_court`, `shot_area_off_court`, and more. Each result set contains per-player rows with standard box score stats.

```python
response = await get_player_matchup_stats(
    client, player_id=1628369, vs_player_id=1628389, season="2025-26"
)

# Overall stats
for row in response.overall:
    if row.player_name and row.pts is not None:
        print(f"{row.player_name}: {row.pts:.1f} pts, {row.fg_pct:.1%} FG")

# On/off splits
for row in response.on_off_court:
    if row.court_status:
        print(f"  ({row.court_status} court): {row.pts:.1f} pts")
```

---

## Functions (profile builders)

### get_primary_defenders

```python
async def get_primary_defenders(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    top_n: int = 5,
) -> list[SeasonMatchup]
```

Who guards this player? Calls `get_season_matchups` with `off_player_id=player_id` and sorts by matchup minutes descending.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `player_id` | required | Offensive player ID |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |
| `top_n` | `5` | Maximum defenders to return |

Returns `list[SeasonMatchup]` sorted by `matchup_min` descending, capped at `top_n`.

```python
# Top 5 defenders by time guarded against Jayson Tatum
defenders = await get_primary_defenders(
    client, player_id=1628369, season="2025-26", top_n=5
)
for d in defenders:
    fg_str = f"{d.matchup_fg_pct:.1%}" if d.matchup_fg_pct is not None else "N/A"
    print(f"{d.def_player_name}: {d.matchup_min:.1f} min, {fg_str} FG%")
```

---

### get_defensive_assignments

```python
async def get_defensive_assignments(
    client: NBAClient,
    defender_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    top_n: int = 5,
) -> list[SeasonMatchup]
```

Who does this defender guard? Calls `get_season_matchups` with `def_player_id=defender_id` and sorts by matchup minutes descending.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `defender_id` | required | Defensive player ID |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |
| `top_n` | `5` | Maximum offensive players to return |

Returns `list[SeasonMatchup]` sorted by `matchup_min` descending, capped at `top_n`.

```python
# Top assignments for Dyson Daniels
assignments = await get_defensive_assignments(
    client, defender_id=1630700, season="2025-26", top_n=5
)
for a in assignments:
    ppp = matchup_ppp(a.player_pts, a.partial_poss)
    ppp_str = f"{ppp:.2f}" if ppp is not None else "N/A"
    print(f"{a.off_player_name}: {a.matchup_min:.1f} min, {ppp_str} PPP")
```

---

### get_team_matchup_summary

```python
async def get_team_matchup_summary(
    client: NBAClient,
    off_team_id: int,
    def_team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[SeasonMatchup]
```

All player-vs-player matchups between two teams. Returns the full unfiltered list — apply `rank_matchups()` to filter by volume and sort by effectiveness.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `off_team_id` | required | Offensive team ID |
| `def_team_id` | required | Defensive team ID |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |

Returns `list[SeasonMatchup]` with all player combinations between the two teams.

```python
from fastbreak.matchups import get_team_matchup_summary, rank_matchups, matchup_ppp

# BOS (1610612738) offense vs MIA (1610612748) defense
summary = await get_team_matchup_summary(
    client, off_team_id=1610612738, def_team_id=1610612748, season="2025-26"
)

# Best offensive matchups by PPP (min 5 possessions)
ranked = rank_matchups(summary, min_poss=5.0, by="ppp", ascending=False)
for m in ranked[:5]:
    ppp = matchup_ppp(m.player_pts, m.partial_poss)
    print(f"{m.off_player_name} vs {m.def_player_name}: {ppp:.2f} PPP")
```

---

## Computation Helpers

### matchup_ppp

```python
def matchup_ppp(player_pts: float, partial_poss: float) -> float | None
```

Points per possession in matchup situations. Returns `None` if `partial_poss <= 0`.

| Parameter | Description |
|---|---|
| `player_pts` | Offensive player's points scored in this matchup |
| `partial_poss` | Partial possessions defended in this matchup |

```python
ppp = matchup_ppp(player_pts=12.0, partial_poss=8.5)  # → 1.41
ppp = matchup_ppp(player_pts=0.0, partial_poss=0.0)   # → None
```

---

### help_defense_rate

```python
def help_defense_rate(matchup_fga: float, help_fga: float) -> float | None
```

Fraction of opponent shots that involved help defense (0–1). Returns `None` if total FGA is 0.

| Parameter | Description |
|---|---|
| `matchup_fga` | FGA while the primary defender was guarding (from `SeasonMatchup.matchup_fga`) |
| `help_fga` | FGA where help defense was involved (from `SeasonMatchup.help_fga`) |

```python
rate = help_defense_rate(matchup_fga=80.0, help_fga=20.0)  # → 0.2 (20% help defense)
rate = help_defense_rate(matchup_fga=0.0, help_fga=0.0)    # → None
```

---

### rank_matchups

```python
def rank_matchups(
    matchups: list[SeasonMatchup],
    *,
    min_poss: float = 10.0,
    by: Literal["matchup_fg_pct", "ppp"] = "matchup_fg_pct",
    ascending: bool = True,
) -> list[SeasonMatchup]
```

Sort matchups by effectiveness, filtering out low-volume pairs below a possession threshold. Matchups with `None` for the sort key are excluded.

| Parameter | Default | Description |
|---|---|---|
| `matchups` | required | List of matchups (e.g., from `get_team_matchup_summary()`) |
| `min_poss` | `10.0` | Minimum partial possessions to include |
| `by` | `"matchup_fg_pct"` | Sort key: `"matchup_fg_pct"` or `"ppp"` |
| `ascending` | `True` | `True` = lowest first (best defense), `False` = highest first (best offense) |

Returns a filtered, sorted `list[SeasonMatchup]`.

```python
# Hardest matchups for the defense (highest offensive PPP, min 10 poss)
worst = rank_matchups(summary, min_poss=10.0, by="ppp", ascending=False)

# Best defended matchups (lowest FG% allowed, min 5 poss)
best = rank_matchups(summary, min_poss=5.0, by="matchup_fg_pct", ascending=True)
```

---

## Data Types

### SeasonMatchup

Key fields on the `SeasonMatchup` Pydantic model returned by `get_season_matchups()`, `get_primary_defenders()`, `get_defensive_assignments()`, and `get_team_matchup_summary()`:

| Field | Type | Description |
|---|---|---|
| `season_id` | `str` | Season identifier (e.g., `"22025"`) |
| `off_player_id` | `int` | Offensive player ID |
| `off_player_name` | `str` | Offensive player name |
| `def_player_id` | `int` | Defensive player ID |
| `def_player_name` | `str` | Defensive player name |
| `gp` | `int` | Games played in this matchup |
| `matchup_min` | `float` | Total matchup minutes |
| `partial_poss` | `float` | Partial possessions in this matchup |
| `player_pts` | `float` | Offensive player's points in this matchup |
| `team_pts` | `float` | Offensive team's points while this matchup was active |
| `matchup_ast` | `float` | Assists by the offensive player in this matchup |
| `matchup_tov` | `float` | Turnovers by the offensive player in this matchup |
| `matchup_blk` | `float` | Blocks by the defensive player in this matchup |
| `matchup_fgm` | `float` | Field goals made in this matchup |
| `matchup_fga` | `float` | Field goals attempted in this matchup |
| `matchup_fg_pct` | `float \| None` | FG% in this matchup (None if no attempts) |
| `matchup_fg3m` | `float` | Three-pointers made in this matchup |
| `matchup_fg3a` | `float` | Three-pointers attempted in this matchup |
| `matchup_fg3_pct` | `float \| None` | 3PT% in this matchup (None if no attempts) |
| `matchup_ftm` | `float` | Free throws made in this matchup |
| `matchup_fta` | `float` | Free throws attempted in this matchup |
| `help_blk` | `float` | Blocks by help defenders while this player had the ball |
| `help_fgm` | `float` | Field goals made against help defense |
| `help_fga` | `float` | Field goals attempted against help defense |
| `help_fg_pct` | `float \| None` | FG% against help defense (None if no attempts) |
| `sfl` | `float` | Shooting fouls drawn |

### MatchupRollupEntry

Key fields on the `MatchupRollupEntry` Pydantic model returned by `get_matchup_rollup()`:

| Field | Type | Description |
|---|---|---|
| `season_id` | `str` | Season identifier |
| `position` | `str` | Defender's position (e.g., `"F"`, `"G"`, `"C"`) |
| `percent_of_time` | `float` | Fraction of time this defender guarded the offensive player (0–1) |
| `def_player_id` | `int` | Defensive player ID |
| `def_player_name` | `str` | Defensive player name |
| `gp` | `int` | Games played in this matchup |
| `matchup_min` | `float` | Total matchup minutes |
| `partial_poss` | `float` | Partial possessions in this matchup |
| `player_pts` | `float` | Offensive player's points in this matchup |
| `team_pts` | `float` | Team points while this matchup was active |
| `matchup_ast` | `float` | Assists in this matchup |
| `matchup_tov` | `float` | Turnovers in this matchup |
| `matchup_blk` | `float` | Blocks in this matchup |
| `matchup_fgm` | `float` | Field goals made |
| `matchup_fga` | `float` | Field goals attempted |
| `matchup_fg_pct` | `float` | FG% in this matchup |
| `matchup_fg3m` | `float` | Three-pointers made |
| `matchup_fg3a` | `float` | Three-pointers attempted |
| `matchup_fg3_pct` | `float` | 3PT% in this matchup |
| `matchup_ftm` | `float` | Free throws made |
| `matchup_fta` | `float` | Free throws attempted |
| `sfl` | `float` | Shooting fouls drawn |
