# defense — Defensive Analysis

The `fastbreak.defense` module provides zone-based aggregate defensive stats, opponent shooting breakdowns, and per-game defensive box scores. It mirrors the structure of `fastbreak.shots` but from the defensive side: given that true per-shot x/y defensive coordinate data is unavailable from the NBA Stats API (`ShotChartDetail` has no defense context measure), this module uses zone-based aggregate data from `LeagueDashPtTeamDefend` and `LeagueDashOppPtShot` instead of individual shot records.

## Table of Contents

- [Quick Start](#quick-start)
- [Functions](#functions)
  - [get_team_defense_zones](#get_team_defense_zones)
  - [get_team_opponent_stats](#get_team_opponent_stats)
  - [get_box_scores_defensive](#get_box_scores_defensive)
  - [get_player_shot_defense](#get_player_shot_defense)
  - [defensive_shot_quality_vs_league](#defensive_shot_quality_vs_league)
- [Data Types](#data-types)

---

## Quick Start

```python
from fastbreak.clients import NBAClient
from fastbreak.defense import (
    get_team_defense_zones,
    get_team_opponent_stats,
    get_box_scores_defensive,
    defensive_shot_quality_vs_league,
)

async with NBAClient() as client:
    # FG% allowed vs league average for all 30 teams (2025-26 season)
    zones = await get_team_defense_zones(client, season="2025-26")

    # Delta vs. league average for one team (Boston Celtics)
    deltas = defensive_shot_quality_vs_league(zones, team_id=1610612738)
    for abbr, delta in deltas.items():
        if delta is not None:
            print(f"{abbr}: {delta:+.3f} vs league avg (negative = better defense)")

    # Opponent 2PT/3PT shooting breakdown for all teams
    opp_stats = await get_team_opponent_stats(client, season="2025-26")
    bos = next(t for t in opp_stats if t.team_abbreviation == "BOS")
    print(f"BOS opp FG%: {bos.fg_pct:.1%}  opp 3PT%: {bos.fg3_pct:.1%}")

    # Defensive box scores for specific games
    game_ids = ["0022500001", "0022500002"]
    boxes = await get_box_scores_defensive(client, game_ids)
    for gid, box in boxes.items():
        home = box.box_score_defensive.home_team
        if home:
            print(f"{gid}: home team {home.team_tricode}")
```

---

## Functions

### get_team_defense_zones

```python
async def get_team_defense_zones(
    client: NBAClient,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    defense_category: DefenseCategory = "Overall",
) -> list[TeamDefendStats]
```

Fetch defensive breakdown for all 30 teams by shot category. Wraps `LeagueDashPtTeamDefend`. Returns opponent FGA frequency and FG% allowed vs. league average per team.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `defense_category` | `"Overall"` | Shot category: `"Overall"`, `"3 Pointers"`, `"2 Pointers"`, `"Less Than 6Ft"`, `"Less Than 10Ft"`, `"Greater Than 15Ft"` |

Returns `list[TeamDefendStats]` with one entry per team (all 30 teams). Filter by `team_id` to isolate a specific team, or pass the full list to `defensive_shot_quality_vs_league()`.

```python
zones = await get_team_defense_zones(client)
# [{team_id: 1610612738, team_abbreviation: "BOS", d_fg_pct: 0.461, pct_plusminus: -0.021, ...}, ...]
```

---

### get_team_opponent_stats

```python
async def get_team_opponent_stats(
    client: NBAClient,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[OppPtShotStats]
```

Fetch league-wide opponent shooting stats for all 30 teams. Wraps `LeagueDashOppPtShot`. Returns FGA frequency, FG%, eFG%, and 2PT/3PT splits allowed by each team.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |

Returns `list[OppPtShotStats]` with one entry per team (all 30 teams). Lower `fg_pct` indicates better overall defense.

```python
opp_stats = await get_team_opponent_stats(client)
# [{team_id: 1610612738, fg_pct: 0.452, efg_pct: 0.531, fg3_pct: 0.341, ...}, ...]

# Filter to one team
bos = next(t for t in opp_stats if t.team_abbreviation == "BOS")
print(f"opp 2PT%: {bos.fg2_pct:.1%}  opp 3PT%: {bos.fg3_pct:.1%}")
```

---

### get_box_scores_defensive

```python
async def get_box_scores_defensive(
    client: NBAClient,
    game_ids: list[str],
    max_concurrency: int = 5,
) -> dict[str, BoxScoreDefensiveResponse]
```

Fetch defensive box scores for multiple games concurrently. Mirrors `get_box_scores()` from `fastbreak.games` — returns `{game_id: response}` in input order.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `game_ids` | required | List of NBA game IDs (e.g., `["0022500001", "0022500002"]`) |
| `max_concurrency` | `5` | Maximum concurrent requests |

Returns a `dict` mapping each `game_id` to a `BoxScoreDefensiveResponse`. Raises `ExceptionGroup` if any request fails (all in-flight requests are cancelled). Returns `{}` immediately for an empty `game_ids` list.

Each `BoxScoreDefensiveResponse` contains matchup-based per-player stats: `matchup_field_goals_attempted`, `matchup_field_goal_percentage`, `partial_possessions`, `switches_on`, `steals`, `blocks`, and more.

```python
boxes = await get_box_scores_defensive(client, game_ids=["0022500001", "0022500002"])
box = boxes["0022500001"]
home = box.box_score_defensive.home_team
if home:
    for player in home.players:
        stats = player.statistics
        print(
            f"{player.name_i}: {stats.matchup_field_goals_made}/"
            f"{stats.matchup_field_goals_attempted} "
            f"({stats.matchup_field_goal_percentage:.1%})"
        )
```

---

### get_player_shot_defense

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

Fetch player-level shot defense tracking data. Re-exported from `fastbreak.tracking` for convenience — opponent FG% when guarded by this player vs. normal FG% by shot category.

| Parameter | Default | Description |
|---|---|---|
| `client` | required | NBA API client |
| `player_id` | required | NBA player ID |
| `season` | current | Season in YYYY-YY format |
| `season_type` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |
| `per_mode` | `"PerGame"` | `"PerGame"` or `"Totals"` |
| `last_n_games` | `0` | Restrict to last N games (0 = full season) |

```python
from fastbreak.defense import get_player_shot_defense

# Rudy Gobert's shot defense profile
defense = await get_player_shot_defense(client, player_id=203497, season="2025-26")
```

> **Note:** This function is a re-export of `fastbreak.tracking.get_player_shot_defense`. Import from either module — the function is identical.

---

### defensive_shot_quality_vs_league

```python
def defensive_shot_quality_vs_league(
    zones: list[TeamDefendStats],
    team_id: int,
) -> dict[str, float | None]
```

Compute per-zone FG% delta that a team *allows* vs. league average. Extracts `pct_plusminus` from `TeamDefendStats` rows for the given `team_id`. Mirrors `shot_quality_vs_league()` from `fastbreak.shots` — but the sign convention is inverted: **negative is better** (opponents shoot worse than the league average against this team).

| Parameter | Default | Description |
|---|---|---|
| `zones` | required | All teams' defend stats from `get_team_defense_zones()` |
| `team_id` | required | NBA team ID to extract stats for |

Returns a `dict` mapping `team_abbreviation` to `pct_plusminus`. Returns `{}` if `team_id` is not found in `zones`.

> **Sign convention:** `pct_plusminus` is negative when opponents shoot *below* league average (better defense), and positive when opponents shoot *above* league average (worse defense). This is the opposite of `shot_quality_vs_league()` in `fastbreak.shots`, where positive means the player outperforms.

```python
zones = await get_team_defense_zones(client)

# Boston Celtics (team_id 1610612738)
deltas = defensive_shot_quality_vs_league(zones, team_id=1610612738)
# {"BOS": -0.021}  — opponents shoot 2.1pp below league average (elite defense)

# Sort all teams by zone defense quality (best first)
all_deltas = [
    (stats.team_abbreviation, stats.pct_plusminus)
    for stats in zones
]
ranked = sorted(all_deltas, key=lambda x: x[1])  # most negative = best
for abbr, delta in ranked[:5]:
    print(f"{abbr}: {delta:+.3f}")
```

---

## Data Types

### TeamDefendStats

Key fields on the `TeamDefendStats` Pydantic model returned in `get_team_defense_zones()`:

| Field | Type | Description |
|---|---|---|
| `team_id` | `int` | NBA team ID |
| `team_name` | `str` | Full team name |
| `team_abbreviation` | `str` | Three-letter team code (e.g., `"BOS"`) |
| `gp` | `int` | Games played |
| `freq` | `float` | Frequency of shots in this zone vs. total opponent FGA |
| `d_fgm` | `int` | Opponent field goals made against this team |
| `d_fga` | `int` | Opponent field goals attempted against this team |
| `d_fg_pct` | `float` | Opponent FG% allowed (lower = better defense) |
| `normal_fg_pct` | `float` | League-average FG% from this zone (the baseline) |
| `pct_plusminus` | `float` | `d_fg_pct - normal_fg_pct` (negative = better than average) |

### OppPtShotStats

Key fields on the `OppPtShotStats` Pydantic model returned in `get_team_opponent_stats()`:

| Field | Type | Description |
|---|---|---|
| `team_id` | `int` | NBA team ID |
| `team_name` | `str` | Full team name |
| `team_abbreviation` | `str` | Three-letter team code |
| `gp` | `int` | Games played |
| `fga_frequency` | `float` | Fraction of opponent FGA from this shot type |
| `fgm` | `int` | Opponent field goals made (total) |
| `fga` | `int` | Opponent field goals attempted (total) |
| `fg_pct` | `float` | Overall opponent FG% allowed |
| `efg_pct` | `float` | Opponent effective FG% allowed (accounts for 3PT value) |
| `fg2a_frequency` | `float` | Fraction of opponent FGA that are 2-pointers |
| `fg2m` | `int` | Opponent 2PT field goals made |
| `fg2a` | `int` | Opponent 2PT field goals attempted |
| `fg2_pct` | `float` | Opponent 2PT FG% allowed |
| `fg3a_frequency` | `float` | Fraction of opponent FGA that are 3-pointers |
| `fg3m` | `int` | Opponent 3PT field goals made |
| `fg3a` | `int` | Opponent 3PT field goals attempted |
| `fg3_pct` | `float` | Opponent 3PT FG% allowed |

### BoxScoreDefensiveResponse

Key structure of the `BoxScoreDefensiveResponse` Pydantic model returned in `get_box_scores_defensive()`:

| Field | Type | Description |
|---|---|---|
| `box_score_defensive.game_id` | `str` | NBA game ID |
| `box_score_defensive.home_team` | `DefensiveTeam \| None` | Home team with per-player defensive stats |
| `box_score_defensive.away_team` | `DefensiveTeam \| None` | Away team with per-player defensive stats |
| `box_score_defensive.home_team.players` | `list[DefensivePlayer]` | Each player's matchup stats |
| `player.statistics.matchup_field_goals_attempted` | `int` | FGA while this player was the primary defender |
| `player.statistics.matchup_field_goal_percentage` | `float` | Opponent FG% when guarded by this player |
| `player.statistics.matchup_three_pointer_percentage` | `float` | Opponent 3PT% when guarded by this player |
| `player.statistics.partial_possessions` | `float` | Partial possessions defended |
| `player.statistics.switches_on` | `int` | Times this player was switched onto an opponent |
| `player.statistics.steals` | `int` | Steals in matchup situations |
| `player.statistics.blocks` | `int` | Blocks in matchup situations |
