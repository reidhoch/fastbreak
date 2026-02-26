# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
