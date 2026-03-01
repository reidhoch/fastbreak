# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.0.8] — 2026-03-01

### ✨ Features

**`fastbreak.standings`** — new module for league standings:
- `get_standings()` — all 30 teams for a season/season type
- `get_conference_standings()` — single conference, sorted by playoff rank
- `magic_number()` — clinching magic number for a leading team over a specific opponent

**`fastbreak.metrics`** — expanded analytics:
- `tov_pct()` — turnover percentage (returns 0–1 fraction, consistent with four-factors endpoint)
- `FourFactors` dataclass and `four_factors()` — Dean Oliver's four factors in one call
- `assist_ratio()` — assists per 100 offensive plays (matches NBA v3 box score field)
- `per_100()` — normalize any counting stat to a per-100-possessions rate
- `possessions()` — Dean Oliver possession estimate, now public (renamed from `_possessions`)
- `offensive_win_shares()` — player offensive win shares (Basketball-Reference method)
- `pythagorean_win_pct()` — Pythagorean win expectation (default exponent: 13.91)

**`fastbreak.games`** — new batch box score helpers:
- `get_box_scores_advanced()`, `get_box_scores_hustle()`, `get_box_scores_scoring()`

**`fastbreak.teams`** — new roster helpers:
- `get_team_roster()` — current roster players for a team
- `get_team_coaches()` — full coaching staff (head coach and assistants)

### 🐛 Bug Fixes

- **`drtg()`**: Fixed to use opponent stats (`opp_fga`, `opp_oreb`, `opp_tov`, `opp_fta`) for the possession estimate — previously used team stats, producing an incorrect denominator
- **`MatchupStatistics`**: Removed `le=1.0` constraint on `percentageDefenderTotalTime`, `percentageOffensiveTotalTime`, and `percentageTotalTimeBothOn` — the NBA API returns values above 1.0 due to rounding in clock-segment arithmetic

### 🔧 Improvements

- **`LeagueAverages.lg_pace`**: Converted from a constructor parameter to a computed property derived from `lg_fga - lg_oreb + lg_tov + 0.44*lg_fta`, ensuring it stays consistent with the `vop` denominator and other possession estimates
- **`get_player_playtypes()` / `get_team_playtypes()`**: Now emit a `UserWarning` explaining that the `SynergyPlaytypes` endpoint always returns empty on the public NBA Stats API

## [v0.0.7] — 2026-02-27

### 📖 Documentation

- Added full API reference docs covering all public modules: `NBAClient`, 100+ endpoint classes, Pydantic response models, and all helper modules (`players`, `teams`, `games`, `schedule`, `seasons`, `metrics`)
- Added type alias reference, known gotchas, and `docs/index.md` table of contents
- Added `context7.json` for Context7 MCP integration

## [v0.0.6] — 2026-02-27

### 🐛 Bug Fixes

- **`FranchiseLeaders` / `FranchisePlayers`**: `team_id` parameter type corrected from `str` to `int`, consistent with `TeamID` usage across the library
- **`BoxScoreHustle`**: Removed incorrect partition validator that required `offensive_box_outs + defensive_box_outs == box_outs` — the NBA API does not guarantee this invariant

### 🔧 Improvements

Schema sync — response models updated to match current NBA Stats API fields:

- **`LeagueDashPlayerStats`**: Added `wnba_fantasy_pts` and full set of per-stat rank columns
- **`LeagueDashPlayerClutch`**: Added `group_set`, `nickname`, `nba_fantasy_pts`, `dd2`, `td3`, `wnba_fantasy_pts`, and full rank column set
- **`LeagueDashTeamStats`**: Added full set of per-stat rank columns
- **`HomepageV2`**: Added `fg_pct`
- **`LeagueDashLineups`**: Added `sum_time_played`

### ⚙️ Tooling

- Pre-commit: added `check-yaml`, `validate-pyproject`, `actionlint`, `no-commit-to-branch`; removed standalone `isort` (consolidated into Ruff)
- Updated `ruff` to v0.15.4, `validate-pyproject` to v0.25, `actionlint` to v1.7.11

## [v0.0.5] — 2026-02-27

### ✨ Features

**`fastbreak.metrics`** — new pure-Python analytics module for computing advanced statistics from existing model data (no extra API calls):
- Shooting efficiency: `true_shooting()`, `effective_fg_pct()`, `free_throw_rate()`, `three_point_rate()`
- Playmaking: `ast_to_tov()`, `ast_pct()`
- Rebounding: `oreb_pct()`, `dreb_pct()`
- Defense: `stl_pct()`, `blk_pct()`
- Composite: `game_score()`, `per_36()`, `usage_pct()`, `per()`, `pace_adjusted_per()`
- Team ratings: `ortg()`, `drtg()`, `net_rtg()`
- Relative metrics: `relative_ts()`, `relative_efg()` (vs. league average via `LeagueAverages`)
- Milestone detection: `is_double_double()`, `is_triple_double()`

**`fastbreak.schedule`** — new schedule helpers:
- `get_team_schedule()` — fetch a team's full season schedule
- `days_rest_before_game()` — compute rest days between games
- `is_back_to_back()` — detect back-to-back games

**`fastbreak.players`** — expanded async helpers for advanced player stat queries

**`fastbreak.teams`** — `get_lineup_net_ratings()` now accepts `int | TeamID` for the `team_id` parameter

**New examples:** `metrics.py`, `player_advanced.py`, `team_advanced.py`, `schedule.py`, `seasons.py`

### 🐛 Bug Fixes

- Corrected inaccuracies in example scripts and cleaned up inline comments

### 🔩 Dependencies

- `ruff` bumped `0.15.2` → `0.15.4` (dev)

### ⚙️ CI

- Publish workflow updated to use `uv`'s native trusted publishing (removes manual OIDC token minting)

## [v0.0.4] — 2026-02-26

### ✨ Features

**Utility Modules** — High-level async helpers for common NBA Stats workflows:
- `fastbreak.players` — `search_players()`, `get_player()`, `get_player_id()`, `get_player_game_log()`, `get_player_stats()`, `get_league_leaders()`, `get_hustle_stats()`
- `fastbreak.teams` — `get_team()`, `get_team_id()`, `search_teams()`, `teams_by_conference()`, `teams_by_division()`, `get_team_stats()`, `get_team_game_log()`, `get_lineup_stats()`
- `fastbreak.games` — `get_game_ids()`, `get_game_summary()`, `get_games_on_date()`, `get_todays_games()`, `get_box_scores()`, `get_play_by_play()`
- `fastbreak.seasons` — sync helpers: `get_season_from_date()`, `season_start_year()`, `season_to_season_id()`

**Signal Handling** — `NBAClient(handle_signals=False)` for embedding in web servers that manage their own signal handlers (SIGINT/SIGTERM)

**Structured Logging** — `structlog`-based logging via `FASTBREAK_LOG_LEVEL` / `FASTBREAK_LOG_FORMAT` environment variables

**New Endpoints (70):**

*Player:*
`AssistLeaders`, `AssistTracker`, `CommonAllPlayers`, `CommonPlayerInfo`, `DunkScoreLeaders`, `GravityLeaders`, `LeagueLeaders`, `LeaguePlayerOnDetails`, `PlayerAwards`, `PlayerCareerStats`, `PlayerCompare`, `PlayerDashPtPass`, `PlayerDashPtReb`, `PlayerDashPtShotDefend`, `PlayerDashPtShots`, `PlayerEstimatedMetrics`, `PlayerFantasyProfileBarGraph`, `PlayerGameLog`, `PlayerGameLogs`, `PlayerGameStreakFinder`, `PlayerIndex`, `PlayerNextNGames`, `PlayerProfileV2`, `PlayerVsPlayer`

*Team:*
`CommonTeamRoster`, `TeamDashLineups`, `TeamDashPtPass`, `TeamDashPtReb`, `TeamDashPtShots`, `TeamEstimatedMetrics`, `TeamGameLog`, `TeamGameLogs`, `TeamPlayerDashboard`, `TeamPlayerOnOffDetails`, `TeamPlayerOnOffSummary`, `TeamVsPlayer`

*League:*
`LeagueDashLineups`, `LeagueDashOppPtShot`, `LeagueDashPlayerBioStats`, `LeagueDashPlayerClutch`, `LeagueDashPlayerStats`, `LeagueDashPtStats`, `LeagueDashPtTeamDefend`, `LeagueDashTeamPtShot`, `LeagueDashTeamShotLocations`, `LeagueDashTeamStats`, `LeagueGameLog`, `LeagueHustleStatsPlayer`, `LeagueHustleStatsTeam`, `LeagueLineupViz`, `LeagueSeasonMatchups`, `LeagueStandings`, `MatchupsRollup`

*Game / Box Score:*
`BoxScoreDefensive`, `BoxScoreHustle`, `BoxScoresV3`, `HomepageLeaders`, `HomepageV2`, `IstStandings`, `LeadersTiles`, `ScoreboardV2`, `ScheduleLeagueV2`, `ScheduleLeagueV2Int`, `ShotChartLeaguewide`, `ShotChartLineupDetail`, `VideoEvents`

*Other:*
`CommonPlayoffSeries`, `LeagueSeasonMatchups`

### 🔧 Improvements

- **Type safety** — stricter typing across endpoint and model definitions
- **`tabular_validator` adoption** — result set parsing consolidated to shared validators
- **`base.py` endpoint base classes** — new typed subclasses (`GameIdEndpoint`, `PlayerDashboardEndpoint`, `DraftCombineEndpoint`, etc.) reduce boilerplate across endpoints

### 🐛 Bug Fixes

- Fixed potential silent failures in async request handling
- Fixed team abbreviation: Indiana Pacers now correctly uses `IND` (was `GSW`)

### 🔩 Dependencies

- `certifi` bumped `2026.1.4` → `2026.2.25`
- `mutmut` bumped `3.4.0` → `3.5.0` (dev)
- pre-commit hooks updated

## [v0.0.3]

✨ Features

- New Endpoint: LeagueDashTeamClutch — Team clutch performance statistics with configurable clutch time parameters
- Response Caching — TTL-based caching via cache_ttl parameter, with clear_cache() and cache_info support
- Live API Testing — New CI workflow for integration tests against NBA Stats API
- Examples — Added examples/ directory with practical usage patterns (box scores, player trends, gravity metrics, shot analysis)

🔧 Improvements

- AnyIO Migration — Replaced asyncio primitives with AnyIO for backend-agnostic structured concurrency
- Structured Logging — Consistent structlog usage throughout
- Dashboard Endpoint Hierarchy — New DashboardEndpoint base class for cleaner inheritance
- Enhanced Type Safety — Expanded Annotated[Literal, Field] type aliases
- Error Visibility — Logging distinguishes parse failures from empty responses

🗑️  Breaking Changes

- Removed PlayerCareerByCollege endpoint (non-functional upstream)
- Removed TeamAndPlayersVsPlayers endpoint (non-functional upstream)

🧪 Testing

- Major test coverage expansion
- Client test reorganization

📝 Documentation

- Updated endpoint count (80+ → 100+)
- Added Stargazers chart to README
