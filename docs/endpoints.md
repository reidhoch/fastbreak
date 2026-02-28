# Endpoints Reference

In fastbreak, each endpoint is a frozen Pydantic model that holds the URL path and query parameters for a single NBA Stats API call.

## What Is an Endpoint?

An endpoint is a **frozen Pydantic model** (`ConfigDict(frozen=True)`) — not a dataclass, not a decorated function. Frozen by design: once constructed, endpoints can't be mutated. That makes them safe to cache, share between tasks, and use as dict keys.

Endpoints are **generic over their response type** `T`. The `response_model` class variable tells the client how to parse the API response:

```python
class BoxScoreTraditional(GameIdEndpoint[BoxScoreTraditionalResponse]):
    path: ClassVar[str] = "boxscoretraditionalv3"
    response_model: ClassVar[type[BoxScoreTraditionalResponse]] = BoxScoreTraditionalResponse
```

Every endpoint must define:
- `path` — the URL path segment appended to the NBA Stats base URL
- `response_model` — the Pydantic model class used to parse the JSON response
- `params()` — method returning `dict[str, str]` of query parameters

Because endpoints are frozen, attempting to modify a field after construction raises a `ValidationError`:

```python
ep = PlayerGameLog(player_id=2544, season="2024-25")
ep.season = "2023-24"  # raises pydantic_core.ValidationError
```

---

## How to Use Endpoints

Construct an endpoint by passing keyword arguments, then pass it to `client.get()` or `client.get_many()`:

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import PlayerGameLog, PlayerCareerStats, BoxScoreTraditionalV3

async with NBAClient() as client:
    # Single request
    log = await client.get(PlayerGameLog(player_id=2544, season="2024-25"))

    # Multiple requests concurrently — all endpoints must return the same response type
    log1, log2 = await client.get_many([
        PlayerGameLog(player_id=2544, season="2024-25"),
        PlayerGameLog(player_id=201939, season="2024-25"),
    ])
```

All parameters have defaults where possible. Season defaults to the current season (computed at construction time). `league_id` defaults to `"00"` (NBA).

**Key format rules:**
- Season: `"YYYY-YY"` (e.g., `"2024-25"`)
- Date: `"MM/DD/YYYY"` (e.g., `"12/25/2024"`) — most endpoints; scoreboard and video endpoints use `"YYYY-MM-DD"` as noted per-endpoint
- `game_id`: 10-character string (e.g., `"0022500571"`)
  - First 3 chars encode game type: `001`=preseason, `002`=regular season, `003`=All-Star, `004`=playoffs
- `player_id` and `team_id` are integers

---

## Base Endpoint Classes

These base classes eliminate boilerplate `params()` implementations. Your concrete endpoint only needs to define `path` and `response_model`.

### `Endpoint[T]`

Abstract base class. All endpoints ultimately inherit from this. Defines `parse_response()` and enforces that `path` and `response_model` are set. Subclasses must implement `params()`.

### `GameIdEndpoint[T]`

For endpoints requiring only a `game_id`. Covers all box score endpoints and other single-game queries.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `game_id` | `str` | required | 10-char NBA game identifier |

```python
class BoxScoreTraditional(GameIdEndpoint[BoxScoreTraditionalResponse]):
    path: ClassVar[str] = "boxscoretraditionalv3"
    response_model: ClassVar[type[BoxScoreTraditionalResponse]] = BoxScoreTraditionalResponse
```

### `PlayerIdEndpoint[T]`

Simplest player endpoint — only `player_id`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player identifier |

### `SimplePlayerEndpoint[T]`

Extends `PlayerIdEndpoint` with `league_id`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player identifier |
| `league_id` | `LeagueID` | `"00"` | `"00"` for NBA |

### `PlayerPerModeEndpoint[T]`

Extends `SimplePlayerEndpoint` with `per_mode`. Used for career stat endpoints that aggregate across seasons without a season filter.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player identifier |
| `league_id` | `LeagueID` | `"00"` | `"00"` for NBA |
| `per_mode` | `PerMode` | `"PerGame"` | `"PerGame"`, `"Totals"`, `"Per36"`, etc. |

### `PlayerSeasonEndpoint[T]`

Extends `SimplePlayerEndpoint` with `season` and `season_type`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player identifier |
| `league_id` | `LeagueID` | `"00"` | `"00"` for NBA |
| `season` | `Season` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, `"Pre Season"` |

### `TeamSeasonEndpoint[T]`

Team equivalent of `PlayerSeasonEndpoint`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `team_id` | `int` | required | NBA team identifier |
| `season` | `Season` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, etc. |
| `league_id` | `LeagueID` | `"00"` | `"00"` for NBA |

### `PlayerDashboardEndpoint[T]`

Full dashboard parameter set for player-based dashboards. Use when you need fine-grained filtering by location, opponent, date range, etc.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player identifier |
| `league_id` | `LeagueID` | `"00"` | `"00"` for NBA |
| `season` | `Season` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | Season type |
| `per_mode` | `PerMode` | `"PerGame"` | Stat aggregation mode |
| `measure_type` | `MeasureType` | `"Base"` | `"Base"`, `"Advanced"`, `"Misc"`, `"Scoring"`, etc. |
| `pace_adjust` | `YesNo` | `"N"` | Pace-adjust stats |
| `plus_minus` | `YesNo` | `"N"` | Include plus/minus |
| `rank` | `YesNo` | `"N"` | Include rank columns |
| `po_round` | `int` | `0` | Playoff round (0=all) |
| `month` | `int` | `0` | Calendar month (0=all) |
| `opponent_team_id` | `int` | `0` | Filter by opponent (0=all) |
| `period` | `Period` | `0` | Game period (0=all) |
| `last_n_games` | `int` | `0` | Last N games (0=all) |
| `ist_round` | `str \| None` | `None` | In-Season Tournament round |
| `outcome` | `Outcome \| None` | `None` | `"W"` or `"L"` |
| `location` | `Location \| None` | `None` | `"Home"` or `"Road"` |
| `season_segment` | `SeasonSegment \| None` | `None` | `"Pre All-Star"` or `"Post All-Star"` |
| `date_from` | `Date \| None` | `None` | Start date `MM/DD/YYYY` |
| `date_to` | `Date \| None` | `None` | End date `MM/DD/YYYY` |
| `vs_conference` | `Conference \| None` | `None` | `"East"` or `"West"` |
| `vs_division` | `Division \| None` | `None` | Division name |
| `game_segment` | `GameSegment \| None` | `None` | `"First Half"`, `"Second Half"`, `"Overtime"` |
| `shot_clock_range` | `ShotClockRange \| None` | `None` | Shot clock filter |

### `TeamDashboardEndpoint[T]`

Same as `PlayerDashboardEndpoint` but uses `team_id` instead of `player_id`. No `ist_round` parameter.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `team_id` | `int` | required | NBA team identifier |
| *(all other params same as `PlayerDashboardEndpoint`)* | | | |

### `DraftCombineEndpoint[T]`

For draft combine endpoints. Uses `season_year` instead of `season`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `league_id` | `LeagueID` | `"00"` | `"00"` for NBA |
| `season_year` | `str` | current season | Season in `YYYY-YY` format |

---

## Complete Endpoint Catalog

### Box Scores (V2 Format)

V2 box score endpoints use the older tabular `resultSets` JSON format. They accept only `game_id`.

| Class | Description | Base Class | Response Model |
|-------|-------------|------------|----------------|
| `BoxScoreTraditional` | Standard stats: FG, 3P, FT, REB, AST, STL, BLK, TOV, PF, PTS, +/- | `GameIdEndpoint` | `BoxScoreTraditionalResponse` |
| `BoxScoreAdvanced` | Advanced metrics: OffRtg, DefRtg, NetRtg, AST%, REB%, TOV%, USG%, PACE, PIE | `GameIdEndpoint` | `BoxScoreAdvancedResponse` |
| `BoxScoreScoring` | Scoring breakdown by shot type, assisted vs unassisted, paint/fastbreak/2nd-chance points | `GameIdEndpoint` | `BoxScoreScoringResponse` |
| `BoxScoreUsage` | Usage shares: % of team FGA, FTA, REB, AST, TOV, PTS while on court | `GameIdEndpoint` | `BoxScoreUsageResponse` |
| `BoxScoreMisc` | Miscellaneous: points off turnovers, 2nd-chance points, fastbreak points, blocks against | `GameIdEndpoint` | `BoxScoreMiscResponse` |
| `BoxScoreFourFactors` | Dean Oliver's four factors: eFG%, TOV rate, ORB rate, FT/FGA | `GameIdEndpoint` | `BoxScoreFourFactorsResponse` |
| `BoxScoreDefensive` | Defensive stats: matchup data, contests, deflections | `GameIdEndpoint` | `BoxScoreDefensiveResponse` |
| `BoxScorePlayerTrack` | SportVU tracking: speed, distance, touches, passes, contested shots | `GameIdEndpoint` | `BoxScorePlayerTrackResponse` |
| `BoxScoreHustle` | Hustle stats: contested shots, screen assists, deflections, loose balls, charges | `GameIdEndpoint` | `BoxScoreHustleResponse` |
| `BoxScoreMatchups` | Player matchup data: who guarded whom with stats | `GameIdEndpoint` | `BoxScoreMatchupsResponse` |
| `BoxScoreSummary` | Game summary: status, arena, officials, line score, series record | `GameIdEndpoint` | `BoxScoreSummaryResponse` |
| `HustleStatsBoxscore` | Alternate hustle stats endpoint | `GameIdEndpoint` | `HustleStatsBoxscoreResponse` |

### Box Scores (V3 Format)

V3 box score endpoints use modern nested JSON. They also accept only `game_id` and are defined in `endpoints/box_scores_v3.py`.

| Class | Description | Response Model |
|-------|-------------|----------------|
| `BoxScoreTraditionalV3` | Traditional stats in V3 nested format | `BoxScoreTraditionalV3Response` |
| `BoxScoreAdvancedV3` | Advanced metrics in V3 nested format | `BoxScoreAdvancedV3Response` |
| `BoxScoreScoringV3` | Scoring breakdown in V3 nested format | `BoxScoreScoringV3Response` |
| `BoxScoreUsageV3` | Usage stats in V3 nested format | `BoxScoreUsageV3Response` |
| `BoxScoreMiscV3` | Miscellaneous stats in V3 nested format | `BoxScoreMiscV3Response` |
| `BoxScoreFourFactorsV3` | Four factors in V3 nested format | `BoxScoreFourFactorsV3Response` |
| `BoxScorePlayerTrackV3` | Player tracking in V3 nested format | `BoxScorePlayerTrackV3Response` |
| `BoxScoreMatchupsV3` | Matchup data in V3 nested format | `BoxScoreMatchupsV3Response` |
| `BoxScoreSummaryV3` | Game summary in V3 nested format: status, arena, attendance, officials, broadcasters | `BoxScoreSummaryV3Response` |

**When to use V2 vs V3:** V3 endpoints use a nested JSON structure where players are grouped under their team. V2 endpoints return flat tabular rows. Use V3 for new code; V2 may be needed if you depend on existing parsers that expect tabular format.

---

### Player Stats and Profiles

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `PlayerIndex` | `season`, `league_id` | Directory of all players in a season with biographical, team, draft, and basic stat info | `PlayerIndexResponse` |
| `CommonPlayerInfo` | `player_id`, `league_id` | Detailed biographical info: birthdate, height, weight, country, team, draft info, career stats | `CommonPlayerInfoResponse` |
| `PlayerCareerStats` | `player_id`, `per_mode` | Season-by-season career stats, totals, rankings, and career highs across all leagues | `PlayerCareerStatsResponse` |
| `PlayerGameLog` | `player_id`, `season`, `season_type` | Game-by-game box score stats for a single season | `PlayerGameLogResponse` |
| `PlayerGameLogs` | `player_id`, `season`, `season_type` | Same as `PlayerGameLog` but includes stat rankings and fantasy points | `PlayerGameLogsResponse` |
| `PlayerProfileV2` | `player_id`, `per_mode`, `league_id` | Full player profile: season stats, career rankings, next game info | `PlayerProfileV2Response` |
| `PlayerCompare` | `player_id_list`, `vs_player_id_list`, `season` | Side-by-side stat comparison between two groups of players | `PlayerCompareResponse` |
| `PlayerVsPlayer` | `player_id` (str), `vs_player_id` (str), `season` | Head-to-head stats when a player faces a specific opponent. Note: both ID params are typed `str`, not `int` | `PlayerVsPlayerResponse` |
| `PlayerAwards` | `player_id` | All NBA awards, All-Star selections, and achievements for a player | `PlayerAwardsResponse` |
| `PlayerEstimatedMetrics` | `season`, `season_type`, `league_id` | Estimated OffRtg, DefRtg, NetRtg, and pace for all players league-wide | `PlayerEstimatedMetricsResponse` |
| `PlayerNextNGames` | `player_id`, `number_of_games`, `league_id`, `season` | Upcoming schedule for a player | `PlayerNextNGamesResponse` |
| `PlayerCareerByCollegeRollup` | `league_id`, `per_mode`, `season_type`, `season` | NBA career stats aggregated by players' college NCAA tournament region/seed | `PlayerCareerByCollegeRollupResponse` |
| `PlayerGameStreakFinder` | `player_id`, `league_id` | Find game streaks matching stat criteria | `PlayerGameStreakFinderResponse` |

---

### Player Dashboards

All inherit from `PlayerDashboardEndpoint[T]`. They require `player_id` and support the full suite of dashboard filters (location, date range, opponent, etc.).

| Class | Description | Response Model |
|-------|-------------|----------------|
| `PlayerDashboardByGeneralSplits` | Stats split by location, W/L, month, pre/post All-Star, starting position, days of rest | `PlayerDashboardByGeneralSplitsResponse` |
| `PlayerDashboardByShootingSplits` | Stats split by shot distance, shot type, assisted vs unassisted | `PlayerDashboardByShootingSplitsResponse` |
| `PlayerDashboardByGameSplits` | Stats split by score margin, game number, days off between games | `PlayerDashboardByGameSplitsResponse` |
| `PlayerDashboardByLastNGames` | Rolling stats over the last N games | `PlayerDashboardByLastNGamesResponse` |
| `PlayerDashboardByTeamPerformance` | Stats filtered by team wins/losses by margin | `PlayerDashboardByTeamPerformanceResponse` |
| `PlayerDashboardByClutch` | Stats in clutch situations (last 5 min, within 5 pts, etc.) | `PlayerDashboardByClutchResponse` |
| `PlayerDashboardByYearOverYear` | Year-over-year stat progression | `PlayerDashboardByYearOverYearResponse` |

---

### Player Tracking

These endpoints return SportVU and second-spectrum tracking data for a player in a season.

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `PlayerDashPtShots` | `player_id` (str), `season`, `season_type`, `per_mode` | Shot stats by type, shot clock range, dribbles before shot, defender distance, touch time. Note: `player_id` is typed `str`, not `int` | `PlayerDashPtShotsResponse` |
| `PlayerDashPtPass` | `player_id`, `season`, `per_mode` | Pass tracking: passes made/received, assists, potential assists, by zone | `PlayerDashPtPassResponse` |
| `PlayerDashPtReb` | `player_id`, `season`, `per_mode` | Rebound tracking: contested vs uncontested, distance from basket, time to retrieve | `PlayerDashPtRebResponse` |
| `PlayerDashPtShotDefend` | `player_id`, `season`, `per_mode` | Defensive shot contesting stats: shots defended by distance and zone | `PlayerDashPtShotDefendResponse` |
| `PlayerFantasyProfileBarGraph` | `player_id`, `league_id`, `season`, `season_type` | Fantasy-relevant stat breakdown for bar chart visualization | `PlayerFantasyProfileBarGraphResponse` |

---

### Team Stats and Profiles

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `TeamDetails` | `team_id` | Team background: arena, coach, GM, owner, championships, retired jerseys, Hall of Famers | `TeamDetailsResponse` |
| `TeamInfoCommon` | `team_id`, `season`, `league_id` | Common team info: record, conference standing, division standing | `TeamInfoCommonResponse` |
| `CommonTeamRoster` | `team_id`, `season`, `league_id` | Current season roster with player biographical info and contract details | `CommonTeamRosterResponse` |
| `CommonTeamYears` | `league_id` | All seasons each franchise has existed | `CommonTeamYearsResponse` |
| `TeamGameLog` | `team_id`, `season`, `season_type` | Game-by-game results and box score stats for a team | `TeamGameLogResponse` |
| `TeamGameLogs` | `team_id`, `season`, `season_type` | Extended game log with stat rankings | `TeamGameLogsResponse` |
| `TeamYearByYearStats` | `team_id`, `season_type`, `per_mode`, `league_id` | Season-by-season historical stats and records for a franchise | `TeamYearByYearStatsResponse` |
| `FranchiseHistory` | `league_id` | All active and defunct NBA franchises with years active and win totals | `FranchiseHistoryResponse` |
| `FranchisePlayers` | `team_id`, `league_id` | All players who have played for a franchise | `FranchisePlayersResponse` |
| `FranchiseLeaders` | `team_id`, `league_id` | All-time franchise leaders in points, rebounds, assists, steals, blocks | `FranchiseLeadersResponse` |

---

### Team Dashboards

`TeamDashboardByGeneralSplits` and `TeamDashboardByShootingSplits` inherit from `TeamDashboardEndpoint[T]` and support the full suite of dashboard filters. The remaining endpoints in this section inherit directly from `Endpoint[T]`.

| Class | Description | Response Model |
|-------|-------------|----------------|
| `TeamDashboardByGeneralSplits` | Team stats split by location, W/L, month, pre/post All-Star, days of rest | `TeamDashboardByGeneralSplitsResponse` |
| `TeamDashboardByShootingSplits` | Team stats split by shot distance and type | `TeamDashboardByShootingSplitsResponse` |
| `TeamPlayerDashboard` | Per-player breakdown of contributions while on the team | `TeamPlayerDashboardResponse` |
| `TeamVsPlayer` | Team stats when a specific player is on vs off court | `TeamVsPlayerResponse` |
| `TeamPlayerOnOffSummary` | On/off summary: team stats when each player is on court vs on the bench | `TeamPlayerOnOffSummaryResponse` |
| `TeamPlayerOnOffDetails` | On/off details with individual game-by-game splits | `TeamPlayerOnOffDetailsResponse` |

**Note:** The `pts` field in on/off data represents team points per game while that player is on court, not the player's individual scoring.

---

### Team Tracking and Lineups

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `TeamDashPtShots` | `team_id`, `season`, `per_mode` | Team shot tracking by type, shot clock, dribbles, defender distance, touch time | `TeamDashPtShotsResponse` |
| `TeamDashPtPass` | `team_id`, `season`, `per_mode` | Team pass tracking: passes made/received by zone | `TeamDashPtPassResponse` |
| `TeamDashPtReb` | `team_id`, `season`, `per_mode` | Team rebound tracking: contested vs uncontested, by zone | `TeamDashPtRebResponse` |
| `TeamDashLineups` | `team_id`, `group_quantity`, `season`, `per_mode`, `measure_type` | Stats for all lineup combinations of a given size (2–5 players). `group_quantity` defaults to `5` for 5-man lineups | `TeamDashLineupsResponse` |
| `LeagueLineupViz` | `season`, `per_mode`, `measure_type` | League-wide lineup visualization data for all teams | `LeagueLineupVizResponse` |

**Note:** `lineup.min` is a per-game average, not a total. The field name is misleading.

---

### League Stats

#### Standing and Game Logs

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `LeagueStandings` | `season`, `season_type`, `league_id` | Current standings for all 30 teams | `LeagueStandingsResponse` |
| `LeagueGameLog` | `season`, `season_type`, `player_or_team`, `sorter`, `direction` | Browse all game logs league-wide, sorted by a stat. `player_or_team="T"` for team games, `"P"` for player games | `LeagueGameLogResponse` |
| `LeagueGameFinder` | Various filters | Advanced game search: find games matching specific stat criteria | `LeagueGameFinderResponse` |

#### Player Dashboards

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `LeagueLeaders` | `season`, `season_type`, `per_mode`, `stat_category`, `scope` | League leaders ranked by a stat. `stat_category` is `"PTS"`, `"REB"`, `"AST"`, etc. | `LeagueLeadersResponse` |
| `LeagueDashPlayerStats` | `season`, `season_type`, `per_mode`, `measure_type` | Stats for all players in the league with extended filter support | `LeagueDashPlayerStatsResponse` |
| `LeagueDashPlayerBioStats` | `season`, `season_type`, `per_mode` | Player bio data (height, weight, age, experience) combined with stats | `LeagueDashPlayerBioStatsResponse` |
| `LeagueDashPlayerClutch` | `season`, `season_type`, `per_mode`, `measure_type` | Player stats specifically in clutch situations | `LeagueDashPlayerClutchResponse` |
| `CommonAllPlayers` | `league_id`, `season`, `is_only_current_season` | Directory of all players (active and historical) | `CommonAllPlayersResponse` |
| `LeaguePlayerOnDetails` | `season`, `season_type`, `per_mode` | On/off impact stats for players league-wide | `LeaguePlayerOnDetailsResponse` |

#### Team Dashboards

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `LeagueDashTeamStats` | `season`, `season_type`, `per_mode`, `measure_type` | Stats for all teams in the league with extended filter support | `LeagueDashTeamStatsResponse` |
| `LeagueDashTeamClutch` | `season`, `season_type`, `per_mode`, `measure_type` | Team stats in clutch situations | `LeagueDashTeamClutchResponse` |
| `LeagueDashTeamShotLocations` | `season`, `season_type`, `per_mode`, `measure_type` | Team shooting percentages broken down by court zone | `LeagueDashTeamShotLocationsResponse` |
| `LeagueDashTeamPtShot` | `season`, `season_type`, `per_mode` | Team-level player-tracking shot stats | `LeagueDashTeamPtShotResponse` |
| `LeagueDashOppPtShot` | `season`, `season_type`, `per_mode` | Opponent player-tracking shot stats (defensive tracking) | `LeagueDashOppPtShotResponse` |
| `LeagueDashLineups` | `season`, `season_type`, `per_mode`, `measure_type`, `group_quantity` | League-wide lineup stats for all teams | `LeagueDashLineupsResponse` |
| `LeagueDashPtStats` | `season`, `season_type`, `per_mode`, `player_or_team` | League-wide player-tracking summary stats | `LeagueDashPtStatsResponse` |
| `LeagueDashPtTeamDefend` | `season`, `season_type`, `per_mode` | Team defensive player-tracking stats | `LeagueDashPtTeamDefendResponse` |

#### Hustle, Assists, and Matchups

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `LeagueHustleStatsPlayer` | `season`, `season_type`, `per_mode` | League-wide hustle stats (contested shots, deflections, charges) for all players | `LeagueHustleStatsPlayerResponse` |
| `LeagueHustleStatsTeam` | `season`, `season_type`, `per_mode` | League-wide hustle stats aggregated per team | `LeagueHustleStatsTeamResponse` |
| `AssistTracker` | `season`, `season_type`, `per_mode` | Assist breakdown: assists by shot type and zone, points created | `AssistTrackerResponse` |
| `AssistLeaders` | `season`, `season_type`, `per_mode` | Ranked list of league assist leaders | `AssistLeadersResponse` |
| `LeagueSeasonMatchups` | `season`, `season_type`, `per_mode` | Season-long matchup data across the league | `LeagueSeasonMatchupsResponse` |
| `MatchupsRollup` | `season`, `season_type`, `per_mode` | Rollup summary of matchup data | `MatchupsRollupResponse` |

---

### Scoreboard and Video

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `ScoreboardV2` | `game_date`, `league_id`, `day_offset` | Daily scoreboard in V2 tabular format: game status, line scores, series records, team leaders. `game_date` is `"YYYY-MM-DD"` | `ScoreboardV2Response` |
| `ScoreboardV3` | `game_date`, `league_id` | Daily scoreboard in V3 nested format: live scores, period breakdowns, game leaders, broadcaster info. `game_date` is `"YYYY-MM-DD"` | `ScoreboardV3Response` |
| `HomepageLeaders` | `league_id`, `season`, `season_type`, `stat_category` | League leaders for homepage display | `HomepageLeadersResponse` |
| `HomepageV2` | `league_id`, `season`, `season_type` | Homepage data: leaders across multiple categories | `HomepageV2Response` |
| `LeadersTiles` | `league_id`, `season`, `season_type` | Tile-format leader data for UI display | `LeadersTilesResponse` |
| `VideoStatus` | `game_date`, `league_id` | Video availability status for games on a date | `VideoStatusResponse` |
| `VideoEvents` | `game_id` | Video event data for individual game plays | `VideoEventsResponse` |

---

### Shooting and Shot Charts

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `ShotChartDetail` | `team_id`, `player_id`, `season`, `season_type`, `context_measure` | Individual shot attempts with x/y coordinates for visualization. `player_id=0` for team-level. `context_measure` can be `"FGA"`, `"FGM"`, `"FG3A"`, etc. Also returns league average percentages by zone | `ShotChartDetailResponse` |
| `ShotChartLeaguewide` | `season`, `season_type`, `per_mode`, `league_id` | League-average shooting by zone, used as background in shot chart visualizations | `ShotChartLeaguewideResponse` |
| `ShotChartLineupDetail` | `group_id`, `season`, `season_type`, `context_measure` | Shot chart data for a specific lineup combination | `ShotChartLineupDetailResponse` |
| `ShotQualityLeaders` | `season`, `season_type`, `league_id` | Leaders in shot quality metrics (expected vs actual shooting efficiency) | `ShotQualityLeadersResponse` |
| `GravityLeaders` | `season`, `season_type`, `league_id` | Players ranked by gravity — how much defensive attention they attract based on defender proximity | `GravityLeadersResponse` |
| `DunkScoreLeaders` | `season`, `season_type`, `league_id` | Players ranked by dunk score | `DunkScoreLeadersResponse` |
| `LeverageLeaders` | `season`, `season_type`, `league_id` | Players ranked by leverage — impact in high-leverage game situations | `LeverageLeadersResponse` |

---

### Play-by-Play

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `PlayByPlay` | `game_id`, `start_period`, `end_period` | All actions/events for a game: shots, turnovers, fouls, substitutions, timeouts. `start_period=0`, `end_period=0` returns the full game | `PlayByPlayResponse` |
| `GameRotation` | `game_id`, `league_id` | Player rotation data: when each player checked in/out and per-stint stats | `GameRotationResponse` |

---

### Schedule

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `ScheduleLeagueV2` | `league_id`, `season` | Complete season schedule: all games by date with team, venue, broadcaster, and leader information | `ScheduleLeagueV2Response` |
| `ScheduleLeagueV2Int` | `league_id`, `season` | International version of the V2 schedule | `ScheduleLeagueV2IntResponse` |

---

### Draft

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `DraftHistory` | `league_id`, `season`, `team_id`, `round_num`, `round_pick`, `overall_pick`, `college` | NBA draft history with flexible filtering by year, team, pick position, or college | `DraftHistoryResponse` |
| `DraftCombineStats` | `season_year`, `league_id` | Aggregate combine stats: agility, strength, vertical jump, shooting | `DraftCombineStatsResponse` |
| `DraftCombinePlayerAnthro` | `season_year`, `league_id` | Player anthropometric data: height, wingspan, weight, hand length/width | `DraftCombinePlayerAnthroResponse` |
| `DraftCombineSpotShooting` | `season_year`, `league_id` | Spot-shooting drill results by position on court | `DraftCombineSpotShootingResponse` |
| `DraftCombineNonstationaryShooting` | `season_year`, `league_id` | Non-stationary shooting drill results | `DraftCombineNonstationaryShootingResponse` |
| `DraftCombineDrillResults` | `season_year`, `league_id` | Athletic drill results: sprint, agility, vertical jump | `DraftCombineDrillResultsResponse` |

Draft combine endpoints inherit from `DraftCombineEndpoint` and use `season_year` (not `season`) in `YYYY-YY` format.

---

### Historical and Special

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `AllTimeLeadersGrids` | `league_id`, `season_type`, `per_mode`, `top_x` | All-time NBA statistical leaders across multiple categories. `top_x` controls how many leaders to return per category (default 10) | `AllTimeLeadersResponse` |
| `CommonPlayoffSeries` | `league_id`, `season`, `series_id` | Playoff series matchup data | `CommonPlayoffSeriesResponse` |
| `IstStandings` | `league_id`, `season` | In-Season Tournament standings | `IstStandingsResponse` |
| `PlayoffPicture` | `league_id`, `season` | Current playoff picture: seedings, elimination/clinch scenarios | `PlayoffPictureResponse` |
| `CumeStatsPlayer` | `player_id`, `game_ids`, `league_id`, `season` | Cumulative stats for a player across a list of specific games. Note: `season` uses 4-digit year format (`"2025"`), not `"YYYY-YY"` | `CumeStatsPlayerResponse` |
| `CumeStatsPlayerGames` | `player_id`, `vs_team_id`, `season`, `league_id` | Games played by a player against a specific opponent | `CumeStatsPlayerGamesResponse` |
| `CumeStatsTeam` | `team_id`, `game_ids`, `league_id` | Cumulative team stats across a list of specific games | `CumeStatsTeamResponse` |
| `CumeStatsTeamGames` | `team_id`, `vs_team_id`, `season`, `league_id` | Games between two teams in a season | `CumeStatsTeamGamesResponse` |
| `InfographicFanDuelPlayer` | `game_id` | Per-game FanDuel-style fantasy stats for players in a specific game | `InfographicFanDuelPlayerResponse` |

---

### Advanced Analytics

| Class | Key Params | Description | Response Model |
|-------|------------|-------------|----------------|
| `PlayerEstimatedMetrics` | `season`, `season_type`, `league_id` | Estimated OffRtg, DefRtg, NetRtg, and pace for all players | `PlayerEstimatedMetricsResponse` |
| `TeamEstimatedMetrics` | `season`, `season_type`, `league_id` | Estimated OffRtg, DefRtg, NetRtg, and pace for all 30 teams | `TeamEstimatedMetricsResponse` |
| `SynergyPlaytypes` | `season_year`, `season_type`, `per_mode`, `player_or_team`, `play_type`, `type_grouping` | Synergy play-type stats (`"Isolation"`, `"Transition"`, `"Postup"`, `"PRBallHandler"`, `"PRRollman"`, `"Spotup"`, `"Handoff"`, `"Cut"`, `"OffScreen"`, `"OffRebound"`, `"Misc"`). Note: `season_year` defaults to a hardcoded `"2024-25"` (not the current season). **Always returns 0 rows on the public NBA Stats API** — play-type data is restricted and not available without a licensed data subscription | `SynergyPlaytypesResponse` |

---

## Code Examples

### Basic Single Request

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import PlayerGameLog

async with NBAClient() as client:
    log = await client.get(
        PlayerGameLog(
            player_id=2544,          # LeBron James
            season="2024-25",
            season_type="Regular Season",
        )
    )
    for game in log.games:
        print(f"{game.game_date}: {game.pts} pts, {game.reb} reb, {game.ast} ast")
```

### Batch Requests with `get_many()`

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import (
    BoxScoreTraditionalV3,
    BoxScoreAdvancedV3,
    BoxScoreSummaryV3,
)

game_id = "0022500571"

async with NBAClient() as client:
    traditional, advanced, summary = await client.get_many([
        BoxScoreTraditionalV3(game_id=game_id),
        BoxScoreAdvancedV3(game_id=game_id),
        BoxScoreSummaryV3(game_id=game_id),
    ])

    game = summary.box_score_summary
    print(f"{game.game_status_text} — {game.arena.arena_name}")

    for player in traditional.box_score_traditional.home_team.players:
        stats = player.statistics
        print(f"{player.name_i}: {stats.points} pts, {stats.rebounds_total} reb")
```

### Dashboard Endpoint with Filters

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import PlayerDashboardByGeneralSplits

async with NBAClient() as client:
    splits = await client.get(
        PlayerDashboardByGeneralSplits(
            player_id=201939,           # Stephen Curry
            season="2024-25",
            per_mode="PerGame",
            measure_type="Base",
            location="Home",            # Home games only
            date_from="11/01/2024",
            date_to="02/28/2025",
        )
    )
```

### Shot Chart

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import ShotChartDetail

async with NBAClient() as client:
    chart = await client.get(
        ShotChartDetail(
            player_id=203954,           # Joel Embiid
            team_id=1610612755,         # 76ers
            season="2024-25",
            season_type="Regular Season",
            context_measure="FGA",
        )
    )
    for shot in chart.shots:
        result = "Made" if shot.shot_made_flag else "Missed"
        print(f"{result}: ({shot.loc_x}, {shot.loc_y}) — {shot.action_type}")
```

---

## Writing a Custom Endpoint

Follow these steps to add a new endpoint to fastbreak.

### Step 1 — Create the endpoint file

Create `src/fastbreak/endpoints/my_endpoint.py`:

```python
from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.my_endpoint import MyEndpointResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season, SeasonType


class MyEndpoint(Endpoint[MyEndpointResponse]):
    """Fetch data from my endpoint.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        league_id: League identifier ("00" for NBA)
        my_param: Custom parameter description

    """

    path: ClassVar[str] = "myendpointpath"
    response_model: ClassVar[type[MyEndpointResponse]] = MyEndpointResponse

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"
    my_param: str = "default"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "Season": self.season,
            "SeasonType": self.season_type,
            "LeagueID": self.league_id,
            "MyParam": self.my_param,
        }
```

If your endpoint fits one of the existing base classes, use it to eliminate boilerplate:

```python
# Only needs game_id:
class MyBoxScore(GameIdEndpoint[MyBoxScoreResponse]):
    path: ClassVar[str] = "myboxscore"
    response_model: ClassVar[type[MyBoxScoreResponse]] = MyBoxScoreResponse

# Only needs player_id + season:
class MyPlayerLog(PlayerSeasonEndpoint[MyPlayerLogResponse]):
    path: ClassVar[str] = "myplayerlog"
    response_model: ClassVar[type[MyPlayerLogResponse]] = MyPlayerLogResponse
```

### Step 2 — Create the response model

Create `src/fastbreak/models/my_endpoint.py`:

```python
from pydantic import BaseModel, Field

from fastbreak.models.common import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator
from pydantic import model_validator


class MyRow(BaseModel):
    game_id: str = Field(alias="GAME_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    points: int = Field(alias="PTS")


class MyEndpointResponse(FrozenResponse):
    rows: list[MyRow] = Field(default_factory=list)

    # Parses the first resultSet in the tabular response
    from_result_sets = model_validator(mode="before")(tabular_validator("rows"))
```

For multiple named result sets:

```python
from fastbreak.models.common.result_set import named_result_sets_validator
from pydantic import model_validator

class MyEndpointResponse(FrozenResponse):
    stats: list[StatsRow] = Field(default_factory=list)
    summary: SummaryRow | None = None

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({
            "stats": "StatsResultSet",
            "summary": ("SummaryResultSet", True),  # True = single row, not a list
        })
    )
```

### Step 3 — Register in `__init__.py` files

Add a `TYPE_CHECKING` import to `src/fastbreak/endpoints/__init__.py`:

```python
if TYPE_CHECKING:
    from fastbreak.endpoints.my_endpoint import MyEndpoint as MyEndpoint
```

Add a `TYPE_CHECKING` import to `src/fastbreak/models/__init__.py`:

```python
if TYPE_CHECKING:
    from fastbreak.models.my_endpoint import MyEndpointResponse as MyEndpointResponse
```

Both modules auto-discover all submodules at runtime; the `TYPE_CHECKING` blocks exist only to support static type checkers (mypy, pyright) and IDE autocomplete.

### Step 4 — Write tests

Create `tests/endpoints/test_my_endpoint.py`:

```python
from fastbreak.endpoints import MyEndpoint


def test_my_endpoint_default_params() -> None:
    ep = MyEndpoint()
    params = ep.params()
    assert params["LeagueID"] == "00"
    assert params["MyParam"] == "default"


def test_my_endpoint_custom_params() -> None:
    ep = MyEndpoint(season="2023-24", my_param="custom")
    params = ep.params()
    assert params["Season"] == "2023-24"
    assert params["MyParam"] == "custom"


def test_my_endpoint_is_frozen() -> None:
    ep = MyEndpoint()
    try:
        ep.my_param = "mutated"  # type: ignore[misc]
        assert False, "Should have raised"
    except Exception:
        pass
```

Create `tests/models/test_my_endpoint.py` to test response parsing against a fixture.

---

## Type Aliases

Common type aliases used in endpoint parameters, imported from `fastbreak.types`:

| Alias | Valid Values |
|-------|-------------|
| `Season` | `"YYYY-YY"` (e.g., `"2024-25"`) |
| `Date` | `"MM/DD/YYYY"` (e.g., `"12/25/2024"`) |
| `SeasonType` | `"Regular Season"`, `"Pre Season"`, `"Playoffs"`, `"All Star"`, `"PlayIn"` |
| `PerMode` | `"PerGame"`, `"Totals"`, `"Per36"`, `"Per100Possessions"`, `"PerMinute"`, `"Per48"`, etc. |
| `MeasureType` | `"Base"`, `"Advanced"`, `"Misc"`, `"Scoring"`, `"Defense"`, `"Usage"`, `"Opponent"` |
| `Conference` | `"East"`, `"West"` |
| `Division` | `"Atlantic"`, `"Central"`, `"Southeast"`, `"Northwest"`, `"Pacific"`, `"Southwest"` |
| `Location` | `"Home"`, `"Road"` |
| `Outcome` | `"W"`, `"L"` |
| `GameSegment` | `"First Half"`, `"Second Half"`, `"Overtime"` |
| `SeasonSegment` | `"Pre All-Star"`, `"Post All-Star"` |
| `Period` | `Literal[0, 1, 2, 3, 4]` — 0=all, 1–4=quarters. For OT, use `GameSegment = "Overtime"` |
| `LeagueID` | `"00"` (NBA), `"01"` (ABA historical), `"10"` (WNBA), `"15"` (G-League), `"20"` (Summer League) |
| `YesNo` | `"Y"`, `"N"` |
| `PlayerOrTeamAbbreviation` | `"P"`, `"T"` |
| `ContextMeasure` | `"FGA"`, `"FGM"`, `"FG3A"`, `"FG3M"`, `"PTS"`, `"EFG_PCT"`, etc. |
