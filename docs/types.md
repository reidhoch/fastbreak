# Type Aliases

`fastbreak.types` provides a set of validated type aliases for NBA Stats API parameters. Each alias is built on the `Annotated[Literal[...], Field(...)]` pattern (or `Annotated[str, AfterValidator(...), Field(...)]` for free-form strings with format validation), giving Pydantic the information it needs to validate values at model construction time.

All aliases are importable directly from `fastbreak.types`:

```python
from fastbreak.types import Season, SeasonType, PerMode, Conference, ...
```

They are used throughout endpoint classes and utility module function signatures for both runtime validation and static type checking.

---

## Why Type Aliases Matter

Errors are caught when you construct an endpoint model, not when the HTTP request fires. This means you get a `ValidationError` immediately with a clear message instead of an opaque API error response (or silently wrong data) after a network round-trip.

```python
from fastbreak.endpoints import PlayerCareerStats

# Valid — constructing the model succeeds
ep = PlayerCareerStats(player_id=2544, per_mode="PerGame")

# Invalid — raises ValidationError immediately at construction time
ep = PlayerCareerStats(player_id=2544, per_mode="invalid")
# pydantic_core.ValidationError: 1 validation error for PlayerCareerStats
# per_mode
#   Input should be 'Totals', 'PerGame', 'Per36', ...
```

The same guarantee applies to all parameters typed with an alias. Passing `"East"` for `Conference` works; passing `"Eastern"` raises immediately.

---

## Complete Reference

### `Season`

Season in `YYYY-YY` format. Uses an `AfterValidator` that verifies both the format and the year continuity: the two-digit suffix must equal `(start_year + 1) % 100`.

| Format | Example | Notes |
|--------|---------|-------|
| `YYYY-YY` | `"2025-26"` | 2025 + 1 = 2026, suffix `26` |
| `YYYY-YY` | `"1999-00"` | 1999 + 1 = 2000, suffix `00` (special case) |

Invalid examples that raise `ValidationError`: `"2025-27"`, `"25-26"`, `"2025/26"`.

**Used by:** nearly every endpoint — `DashboardEndpoint` (base for all player/team dashboards), `PlayerSeasonEndpoint`, `TeamSeasonEndpoint`, `LeagueLeaders`, `SynergyPlaytypes`, `ShotChartDetail`, `LeagueDashPtStats`, `IstStandings`, and many others. Also used by standalone helpers `get_player_game_log`, `get_team_game_log`, `get_game_ids`.

---

### `Date`

A calendar date in `MM/DD/YYYY` format. The validator checks both the format (zero-padded, slash-delimited) and that the value represents a real calendar date.

| Format | Example |
|--------|---------|
| `MM/DD/YYYY` | `"01/15/2025"` |

**Used by:** `date_from` and `date_to` filter parameters on `DashboardEndpoint`, `ShotChartDetail`, `LeagueDashPtStats`, and other endpoints that accept a date range filter.

---

### `ISODate`

A calendar date in `YYYY-MM-DD` format. The validator checks both the format and that the value represents a real calendar date.

| Format | Example |
|--------|---------|
| `YYYY-MM-DD` | `"2025-01-15"` |

**Used by:** `get_games_on_date` and related helpers in `fastbreak.games`.

---

### `SeasonType`

The type of NBA season.

| Valid values |
|-------------|
| `"Regular Season"` |
| `"Playoffs"` |
| `"Pre Season"` |
| `"All Star"` |
| `"PlayIn"` |

**Used by:** virtually every endpoint with a season context — `DashboardEndpoint` (and all dashboard subclasses), `PlayerSeasonEndpoint`, `TeamSeasonEndpoint`, `LeagueLeaders`, `LeagueDashPtStats`, `SynergyPlaytypes`, `ShotChartDetail`, `LeagueDashPlayerClutch`, `LeagueDashTeamClutch`, and others.

---

### `PerMode`

Statistical aggregation mode controlling how raw counting stats are normalized.

| Valid values | Meaning |
|-------------|---------|
| `"Totals"` | Season totals (raw counts) |
| `"PerGame"` | Per-game averages |
| `"Per36"` | Per 36 minutes |
| `"Per40"` | Per 40 minutes |
| `"Per48"` | Per 48 minutes |
| `"PerMinute"` | Per minute |
| `"PerPossession"` | Per possession |
| `"PerPlay"` | Per play |
| `"Per100Possessions"` | Per 100 possessions |
| `"Per100Plays"` | Per 100 plays |
| `"MinutesPer"` | Minutes per (e.g., minutes per game) |

**Used by:** `DashboardEndpoint`, `PlayerPerModeEndpoint`, `LeagueLeaders`, `LeagueDashPtStats`, `SynergyPlaytypes`, `LeagueDashPlayerClutch`, `LeagueDashTeamClutch`, `LeagueDashTeamShotLocations`, and many others. Also used by `get_player_stats` and `get_team_stats` helpers.

---

### `MeasureType`

The category of statistics to return. Controls which columns appear in dashboard endpoint responses.

| Valid values | Meaning |
|-------------|---------|
| `"Base"` | Standard box score stats |
| `"Advanced"` | Advanced metrics (e.g., TS%, eFG%, ORTG, DRTG) |
| `"Misc"` | Miscellaneous stats (points off turnovers, fast-break points, etc.) |
| `"Scoring"` | Scoring breakdown by shot type and distance |
| `"Usage"` | Usage rates and frequency |
| `"Four Factors"` | Dean Oliver's four factors (eFG%, TOV%, OREB%, FT Rate) |
| `"Opponent"` | Opponent stats allowed |
| `"Defense"` | Defensive stats |

**Used by:** `DashboardEndpoint` (and all player/team dashboard subclasses).

---

### `Conference`

NBA conference.

| Valid values |
|-------------|
| `"East"` |
| `"West"` |

**Used by:** `vs_conference` and `conference` filter parameters on `DashboardEndpoint`, `LeagueDashPtStats`, `ShotChartDetail`, and others. Also used by `fastbreak.teams.teams_by_conference`.

---

### `Division`

NBA division.

| Valid values |
|-------------|
| `"Atlantic"` |
| `"Central"` |
| `"Southeast"` |
| `"Northwest"` |
| `"Pacific"` |
| `"Southwest"` |

**Used by:** `vs_division` and `division` filter parameters on `DashboardEndpoint`, `LeagueDashPtStats`, `ShotChartDetail`, and others. Also used by `fastbreak.teams.teams_by_division`.

---

### `LeagueID`

Identifies the league for endpoints that serve multiple leagues.

| Valid values | League |
|-------------|--------|
| `"00"` | NBA |
| `"01"` | ABA (historical) |
| `"10"` | WNBA |
| `"15"` | G League |
| `"20"` | Summer League |

The default across all endpoints is `"00"` (NBA).

**Used by:** nearly every endpoint — `DashboardEndpoint`, `PlayerPerModeEndpoint`, `SimplePlayerEndpoint`, `DraftCombineEndpoint`, `LeagueLeaders`, `ShotChartDetail`, `SynergyPlaytypes`, `IstStandings`, and many others.

---

### `Location`

Game location from the perspective of the team or player being queried.

| Valid values |
|-------------|
| `"Home"` |
| `"Road"` |

**Used by:** `location` optional filter on `DashboardEndpoint`, `ShotChartDetail`, `LeagueDashPtStats`, and others.

---

### `Outcome`

Game outcome filter.

| Valid values |
|-------------|
| `"W"` |
| `"L"` |

**Used by:** `outcome` optional filter on `DashboardEndpoint`, `ShotChartDetail`, `LeagueDashPtStats`, and others.

---

### `Period`

Quarter or period of the game to filter statistics. Note that this type uses integer literals, not strings.

| Valid values | Meaning |
|-------------|---------|
| `0` | All periods combined |
| `1` | 1st quarter |
| `2` | 2nd quarter |
| `3` | 3rd quarter |
| `4` | 4th quarter |

The default on all endpoints that accept `period` is `0` (all periods). Overtime periods are not represented; use `GameSegment = "Overtime"` to filter to OT.

**Used by:** `DashboardEndpoint`, `ShotChartDetail`, `LeagueDashPtStats`, and others.

---

### `PlayerPosition`

Player position abbreviation. Uses single-letter codes and hyphenated dual-position codes.

| Valid values | Meaning |
|-------------|---------|
| `"G"` | Guard |
| `"F"` | Forward |
| `"C"` | Center |
| `"G-F"` | Guard-Forward |
| `"F-G"` | Forward-Guard |
| `"F-C"` | Forward-Center |
| `"C-F"` | Center-Forward |

**Used by:** `player_position` optional filter on `LeagueDashPtStats`, `AssistTracker`, and others.

---

### `PlayerExperience`

Player experience level by years in the league.

| Valid values |
|-------------|
| `"Rookie"` |
| `"Sophomore"` |
| `"Veteran"` |

**Used by:** `player_experience` optional filter on `LeagueDashPtStats`, `LeagueDashPlayerStats`, `LeagueDashTeamStats`, `LeagueDashPlayerClutch`, `LeagueDashTeamClutch`, `AssistTracker`, and others.

---

### `GameSegment`

Half or overtime segment of a game.

| Valid values |
|-------------|
| `"First Half"` |
| `"Second Half"` |
| `"Overtime"` |

**Used by:** `game_segment` optional filter on `DashboardEndpoint` and `ShotChartDetail`.

---

### `SeasonSegment`

Half of the season relative to the All-Star break.

| Valid values |
|-------------|
| `"Pre All-Star"` |
| `"Post All-Star"` |

**Used by:** `season_segment` optional filter on `DashboardEndpoint` and `ShotChartDetail`.

---

### `StarterBench`

Whether to filter to starters or bench players.

| Valid values |
|-------------|
| `"Starter"` |
| `"Bench"` |

**Used by:** `starter_bench` optional filter on `LeagueDashPtStats`, `LeagueDashPlayerStats`, `LeagueDashTeamStats`, `LeagueDashPlayerClutch`, `LeagueDashTeamClutch`, `AssistTracker`, and others.

---

### `AheadBehind`

Score differential state for clutch situation filtering.

| Valid values | Meaning |
|-------------|---------|
| `"Ahead or Behind"` | Either team leads (excludes tie) |
| `"Ahead or Tied"` | Queried team leads or the game is tied |
| `"Behind or Tied"` | Queried team trails or the game is tied |

**Used by:** `ahead_behind` parameter on `LeagueDashPlayerClutch` and `LeagueDashTeamClutch`.

---

### `ClutchTime`

Amount of time remaining in clutch situation filtering. Typically combined with `AheadBehind`.

| Valid values |
|-------------|
| `"Last 5 Minutes"` |
| `"Last 4 Minutes"` |
| `"Last 3 Minutes"` |
| `"Last 2 Minutes"` |
| `"Last 1 Minute"` |
| `"Last 30 Seconds"` |
| `"Last 10 Seconds"` |

**Used by:** `clutch_time` parameter on `LeagueDashPlayerClutch` and `LeagueDashTeamClutch`.

---

### `ShotClockRange`

Shot clock time remaining range for filtering possessions.

| Valid values | Meaning |
|-------------|---------|
| `"24-22"` | 24 to 22 seconds remaining |
| `"22-18 Very Early"` | 22 to 18 seconds remaining |
| `"18-15 Early"` | 18 to 15 seconds remaining |
| `"15-7 Average"` | 15 to 7 seconds remaining |
| `"7-4 Late"` | 7 to 4 seconds remaining |
| `"4-0 Very Late"` | 4 to 0 seconds remaining |
| `"ShotClock Off"` | Shot clock not running |

**Used by:** `shot_clock_range` optional filter on `DashboardEndpoint`.

---

### `ContextMeasure`

Shot type or outcome context for shot chart data. Controls which shot attempts appear in `ShotChartDetail` results.

| Valid values | Meaning |
|-------------|---------|
| `"FGA"` | Field goal attempts |
| `"FGM"` | Field goal makes |
| `"FG3A"` | 3-point attempts |
| `"FG3M"` | 3-point makes |
| `"FTA"` | Free throw attempts |
| `"FTM"` | Free throw makes |
| `"PTS"` | Points |
| `"PTS_FB"` | Fast-break points |
| `"PTS_OFF_TOV"` | Points off turnovers |
| `"PTS_2ND_CHANCE"` | Second-chance points |
| `"PF"` | Personal fouls |
| `"EFG_PCT"` | Effective field goal percentage |
| `"TS_PCT"` | True shooting percentage |

**Used by:** `context_measure` parameter on `ShotChartDetail`.

---

### `DistanceRange`

How shot distances are grouped for shot location statistics.

| Valid values | Meaning |
|-------------|---------|
| `"5ft Range"` | Group shots into 5-foot distance bands |
| `"8ft Range"` | Group shots into 8-foot distance bands |
| `"By Zone"` | Group shots by court zone (paint, mid-range, corner 3, etc.) |

**Used by:** `distance_range` parameter on `LeagueDashTeamShotLocations`.

---

### `PlayType`

Synergy play type classification for offensive or defensive situations.

| Valid values | Meaning |
|-------------|---------|
| `"Isolation"` | Isolation plays |
| `"Transition"` | Transition offense |
| `"PRBallHandler"` | Pick-and-roll ball handler |
| `"PRRollman"` | Pick-and-roll roll man |
| `"Postup"` | Post-up plays |
| `"Spotup"` | Spot-up shooting |
| `"Handoff"` | Hand-off plays |
| `"Cut"` | Cutting plays |
| `"OffScreen"` | Off-screen plays |
| `"OffRebound"` | Putback/off-rebound plays |
| `"Misc"` | Miscellaneous play types |

**Used by:** `play_type` optional filter on `SynergyPlaytypes`.

Note: The `SynergyPlaytypes` endpoint always returns 0 rows. Play-type data is restricted on the public NBA Stats API. This is not a parsing bug — see [Gotchas](./gotchas.md).

---

### `PtMeasureType`

Player tracking stat category. Determines which set of tracking metrics is returned by `LeagueDashPtStats`.

| Valid values | Meaning |
|-------------|---------|
| `"Drives"` | Drive frequency and efficiency stats |
| `"Defense"` | Defensive tracking stats |
| `"CatchShoot"` | Catch-and-shoot shot stats |
| `"Passing"` | Passes made, potential assists, etc. |
| `"Possessions"` | Touches, front-court touches, time of possession |
| `"PullUpShot"` | Pull-up jump shot stats |
| `"Rebounding"` | Contested/uncontested rebounding, rebound chance % |
| `"Efficiency"` | Points produced, possessions used |
| `"SpeedDistance"` | Average speed and distance covered |
| `"ElbowTouch"` | Elbow-area touch stats |
| `"PostTouch"` | Post-area touch stats |
| `"PaintTouch"` | Paint-area touch stats |

**Used by:** `pt_measure_type` parameter on `LeagueDashPtStats`.

---

### `Scope`

Player scope filter for league leaders and similar leaderboard endpoints.

| Valid values | Meaning |
|-------------|---------|
| `"S"` | Full season (all eligible players) |
| `"RS"` | Rookies — season leaders among rookies |
| `"Rookies"` | Rookies (alternate value accepted by some endpoints) |

**Used by:** `scope` parameter on `LeagueLeaders` and `LeadersTiles`.

---

### `Section`

IST (In-Season Tournament / NBA Cup) standings section.

| Valid values | Meaning |
|-------------|---------|
| `"group"` | Group stage standings |
| `"wildcard"` | Wildcard standings |

**Used by:** `section` parameter on `IstStandings`.

---

### `StatCategoryAbbreviation`

Statistical category abbreviation for leaderboard sorting in `LeagueLeaders`.

| Valid values | Stat |
|-------------|------|
| `"PTS"` | Points |
| `"FGM"` | Field goals made |
| `"FGA"` | Field goal attempts |
| `"FG_PCT"` | Field goal percentage |
| `"FG3M"` | 3-pointers made |
| `"FG3A"` | 3-point attempts |
| `"FG3_PCT"` | 3-point percentage |
| `"FTM"` | Free throws made |
| `"FTA"` | Free throw attempts |
| `"OREB"` | Offensive rebounds |
| `"DREB"` | Defensive rebounds |
| `"AST"` | Assists |
| `"STL"` | Steals |
| `"BLK"` | Blocks |
| `"TOV"` | Turnovers |
| `"REB"` | Total rebounds |

**Used by:** `stat_category` parameter on `LeagueLeaders`. Also used by `get_league_leaders` in `fastbreak.players`.

---

### `PlayerOrTeam`

Whether a query should return player-level or team-level statistics.

| Valid values |
|-------------|
| `"Player"` |
| `"Team"` |

**Used by:** `player_or_team` parameter on `LeagueDashPtStats`, `AssistLeaders`, `LeadersTiles`, `HomepageLeaders`, `HomepageV2`.

---

### `PlayerOrTeamAbbreviation`

Single-character abbreviation form of the player-or-team switch. Used by endpoints that prefer the short form in their API parameter.

| Valid values | Meaning |
|-------------|---------|
| `"P"` | Player |
| `"T"` | Team |

**Used by:** `player_or_team` parameter on `SynergyPlaytypes`, `LeagueGameFinder`, `LeagueGameLog`.

---

### `YesNo`

Boolean flag represented as a single character string. Used for API parameters that the NBA Stats API expects as `"Y"` or `"N"` rather than a native boolean.

| Valid values |
|-------------|
| `"Y"` |
| `"N"` |

**Used by:** `pace_adjust`, `plus_minus`, and `rank` parameters on `DashboardEndpoint` (and all its subclasses — the largest set of endpoints), as well as `LeagueDashLineups`, `TeamDashLineups`, `LeagueDashTeamShotLocations`, `LeagueLineupViz`, `PlayerVsPlayer`, `TeamVsPlayer`, `PlayerCompare`, `TeamPlayerOnOffDetails`, `TeamPlayerOnOffSummary`, `TeamPlayerDashboard`, `LeaguePlayerOnDetails`, and others.

---

## Usage Examples

### Constructing endpoints with typed parameters

```python
from fastbreak.endpoints import PlayerCareerStats, LeagueLeaders, ShotChartDetail
from fastbreak.types import PerMode, SeasonType, StatCategoryAbbreviation

# Explicit type annotations help your editor and type checker
per_mode: PerMode = "PerGame"
season_type: SeasonType = "Playoffs"

ep = PlayerCareerStats(player_id=2544, per_mode=per_mode)

# ValidationError at construction — not at request time
ep = PlayerCareerStats(player_id=2544, per_mode="Per48")   # valid
ep = PlayerCareerStats(player_id=2544, per_mode="invalid") # raises ValidationError!

# League leaders for blocks, post All-Star, playoffs
leaders_ep = LeagueLeaders(
    season="2025-26",
    season_type="Playoffs",
    stat_category="BLK",
    per_mode="PerGame",
    scope="S",
)

# Shot chart filtered to first half, home games only
chart_ep = ShotChartDetail(
    team_id=1610612744,
    player_id=201939,
    season="2025-26",
    context_measure="FGA",
    game_segment="First Half",
    location="Home",
)
```

### Using types in function signatures

```python
from fastbreak.types import Season, SeasonType, PerMode

async def fetch_player_averages(
    client,
    player_id: int,
    season: Season,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> None:
    ...
```

The type aliases are transparent to the type checker — `Season` is `str`, `PerMode` is `str`, etc. The `Annotated` metadata is consumed only by Pydantic during model validation.

---

## Season Format Details

`Season` uses an `AfterValidator` (not a `Literal`), so any validly formatted string is accepted. The validation logic:

1. The string must match the pattern `^\d{4}-\d{2}$`.
2. The two-digit suffix must equal `(start_year + 1) % 100`.

Examples:

| Season string | Start year | Expected suffix | Valid? |
|--------------|-----------|----------------|--------|
| `"2025-26"` | 2025 | 26 | Yes |
| `"2024-25"` | 2024 | 25 | Yes |
| `"1999-00"` | 1999 | 00 | Yes (2000 % 100 = 0) |
| `"2025-27"` | 2025 | 26 | No — suffix mismatch |
| `"25-26"` | — | — | No — wrong format |

The `get_season_from_date()` utility from `fastbreak.seasons` always returns a correctly formatted season string for the current date and can be used as a `Field(default_factory=...)` in endpoint models.

---

## Importing Types

All type aliases are importable from the single `fastbreak.types` module:

```python
from fastbreak.types import (
    AheadBehind,
    ClutchTime,
    Conference,
    ContextMeasure,
    Date,
    DistanceRange,
    Division,
    GameSegment,
    ISODate,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    Period,
    PerMode,
    PlayerExperience,
    PlayerOrTeam,
    PlayerOrTeamAbbreviation,
    PlayerPosition,
    PlayType,
    PtMeasureType,
    Scope,
    Season,
    SeasonSegment,
    SeasonType,
    Section,
    ShotClockRange,
    StarterBench,
    StatCategoryAbbreviation,
    YesNo,
)
```
