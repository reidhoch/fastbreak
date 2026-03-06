# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.1.0] - 2026-03-06

### ✨ New Modules

- **`fastbreak.shots`** — Shot chart analysis: `zone_breakdown()`, `zone_fg_pct()`, `shot_quality_vs_league()`, and `xfg_pct()` (expected FG% based on shot-zone selection vs. league averages). `Shot.loc_x` / `loc_y` are in tenths of feet.
- **`fastbreak.clutch`** — Clutch performance analysis: `get_player_clutch_profile()`, `get_league_clutch_leaders()`, `build_clutch_profile()`, and `clutch_score()`. Clutch defined as last 5 minutes with score within ±5 points.
- **`fastbreak.tracking`** — Tracking stats helpers covering shots, passes, rebounds, and shot defense from NBA Stats hustle/tracking endpoints.
- **`fastbreak.splits`** — Per-split stat analysis; `stat_delta()` centralized in `fastbreak.metrics`.

### 🔧 Improvements

**`fastbreak.metrics`:**

- **BPM 2.0** (`bpm()`) — Box Plus/Minus per Myers / Basketball Reference. Returns `BPMResult(total, offensive, defensive)`. All stats per-100 team possessions; raw output requires a team adjustment constant before comparing across players.
- **VORP** (`vorp()`) — Value Over Replacement Player scaled to an 82-game season. Multiply by 2.7 for approximate Wins Above Replacement.
- **Defensive Win Shares** (`defensive_win_shares()`)
- **10 distribution and trend analytics** — `stat_floor()`, `stat_ceiling()`, `stat_median()`, `prop_hit_rate()`, `hit_rate_last_n()`, `rolling_consistency()`, `expected_stat()`, `percentile_rank()`, `streak_count()`, `stat_consistency()`

**`fastbreak.games`:**

- **`game_flow()`** — Builds a `list[GameFlowPoint]` scoring timeline from play-by-play actions.

**`fastbreak.models.common.result_set`:**

- **`named_result_sets_validator`** and **`named_tabular_validator`** — new helpers for parsing named NBA Stats result sets without boilerplate `model_validator` logic.

**`fastbreak.clients.NBAClient`:**

- **`request_delay`** — now sleeps *inside* the `CapacityLimiter` slot in `get_many()`, correctly pacing completions at `max_concurrency / request_delay` req/s.

### 🐛 Bug Fixes

- **`request_delay`**: Previously slept *outside* the capacity limiter, causing all tasks to wake simultaneously and stampede the limiter.

### 📚 Documentation

- Expanded docs for `shots`, `metrics`, and `games` modules.
- Fixed `xfg_pct()` docstring: `None` return condition now correctly describes both empty zone breakdown and no matching league data cases.
- Fixed VORP inline example approximation in `docs/metrics.md` (`≈ 10.8` → `≈ 8.7`; WAR `≈ 29.2` → `≈ 23.5`).

## [v0.0.13] - 2026-03-03

### 🐛 Bug Fixes

- **`__asynccontextmanager__`**: Body exceptions were wrapped in `ExceptionGroup` by anyio's task group when `handle_signals=True` — any exception raised inside `async with NBAClient() as client:` (e.g. a request timeout) would escape as `ExceptionGroup` instead of the original exception; fixed by catching body exceptions inside the task group, cancelling the scope, and re-raising outside

## [v0.0.12] - 2026-03-03

### 🔧 Improvements

**`NBAClient` (clients/nba.py):**

- **Idiomatic anyio throughout** — removed the `asyncio` import; all concurrency primitives now use anyio directly
  - `NBAClient` inherits from `anyio.AsyncContextManagerMixin` and implements `__asynccontextmanager__()` instead of `__aenter__` / `__aexit__`
  - Signal handling uses `anyio.open_signal_receiver` in a dedicated task (`_signal_handler_loop`) inside `anyio.create_task_group`; the cancel scope is cancelled on context exit
  - Session close timeout uses `anyio.move_on_after()` + `cancel_scope.cancelled_caught` instead of `asyncio.wait_for()` + `TimeoutError`
- **`request_delay` sleeps before acquiring the concurrency slot** — previously ran inside `async with limiter:`, holding a slot during the wait
- **`DummyCookieJar`** — `ClientSession` is created with `cookie_jar=DummyCookieJar()`; fastbreak doesn't use cookies

### 🐛 Bug Fixes

- **`_signal_handler_loop`**: Added `OSError` to caught exceptions — CPython's `add_signal_handler` can propagate a raw `OSError` (errno ≠ `EINVAL`) from `siginterrupt()`, which previously crashed the client at startup
- **`close()`**: Exceptions from `session.close()` are now logged at WARNING (with traceback) before propagating; previously they escaped silently
- **`docs/client.md`**: Cache key was documented as SHA-256; the implementation uses MD5 (`usedforsecurity=False`)
- **`docs/gotchas.md`**: Removed `await client.__aenter__()` from lifespan example — calling `__aenter__` without `__aexit__` leaves the signal handler task group uncancelled

### 📚 Documentation

- **`docs/client.md`**: Updated signal handling section for anyio; removed asyncio-specific "event loop" terminology; clarified `request_delay` slot-ordering
- **`docs/gotchas.md`**: Updated root-cause and lifespan example for anyio-based signal handling
- **`docs/models.md`**: Fixed import path `fastbreak.models.common.frozen` → `fastbreak.models.common.response`

## [v0.0.11] - 2026-03-03

### 🐛 Bug Fixes

- **`BoxScoreHustleData`**: `home_team` and `away_team` are now `HustleTeam | None` — the NBA API returns `null` for both team objects on certain games (e.g. last game of a season) where hustle data was not tracked; previously this raised a `ValidationError` instead of parsing gracefully

## [v0.0.10] - 2026-03-03

- **`DefensiveTeam`**: `statistics` is now `DefensiveTeamStatistics | None` — the NBA API returns `null` for this field when no defensive stats are available for a team

## [v0.0.9] — 2026-03-02

### 🐛 Bug Fixes

- **`RotationEntry`**: `player_pts`, `pt_diff`, and `usg_pct` are now `int | None` / `float | None` — the NBA API returns `null` for these fields when a player logs no time on court
- **`get_on_off_splits()`**: Rows with an unrecognised `court_status` value are now explicitly ignored (previously the `"off"` bucket could accumulate non-`"Off"` rows)
- **`teams_by_conference()` / `teams_by_division()`**: Return a copy of the internal lookup list, preventing callers from accidentally mutating the module-level index

### 🔧 Improvements

**`NBAClient` (clients/nba.py):**

- Cache key generation switched from SHA-256 to MD5 (`usedforsecurity=False`) — faster for non-security hashing
- Cache-hit log is now emitted *outside* the cache lock, reducing lock hold time under concurrent load

**`LeagueAverages` (metrics.py):**

- Pace denominator (`lg_fga - lg_oreb + lg_tov + 0.44*lg_fta`) is computed once in `__post_init__` and stored as `_pace_denom`; `vop` and `lg_pace` properties read the cached value instead of re-evaluating on each access

**`rolling_avg()` (metrics.py):**

- Replaced O(n·w) slice-and-sum with an O(n) sliding window using running `window_sum` and `none_count` accumulators

**`seasons.py`:**

- Extracted `_season_from_date(d: date)` as a pure helper and decorated it with `@lru_cache(maxsize=32)`; `get_season_from_date()` delegates to it — season lookups for the same date are now free after the first call

**`players.py`:**

- `_season_id_to_season()` decorated with `@lru_cache(maxsize=32)`, avoiding repeated string parsing in `get_career_game_logs()`

**`teams.py`:**

- `teams_by_conference()` / `teams_by_division()` are now O(1) lookups backed by pre-built `_TEAMS_BY_CONFERENCE` / `_TEAMS_BY_DIVISION` module-level dicts, replacing O(30) linear scans on every call
- `get_league_averages()` aggregates all 11 fields in a single loop instead of 11 separate `fmean()` generator passes; removed `statistics.fmean` import

**`standings.py`:**

- `get_conference_standings()` sort uses `attrgetter("playoff_rank")` instead of a lambda

**`models/common/result_set.py`:**

- Extracted `_parse_result_set_rows()` helper, eliminating duplicated header/rowSet parsing logic shared by `parse_result_set()` and `parse_result_set_by_name()`

### 🧪 Testing

- **`tests/strategies.py`** — shared [Hypothesis](https://hypothesis.readthedocs.io/) strategy factories for NBA domain types (`Season`, `Date`, `PerMode`, stat values, etc.)
- **`tests/test_metrics_properties.py`** — property-based tests covering mathematical invariants and edge cases for all metrics functions (`true_shooting`, `rolling_avg`, `pace_adjusted_per`, `pythagorean_win_pct`, and more)
- **`tests/test_models_properties.py`** — property-based tests for Pydantic model validation and round-trip behaviour
- **`tests/test_players.py`** — unit tests for player utility functions (`search_players`, `get_player`, `get_on_off_splits`, etc.)
- **`tests/models/test_game_rotation.py`** — model tests for the game rotation endpoint, including nullable-field cases
- Extended `tests/endpoints/test_box_scores.py` and `tests/endpoints/test_homepage_endpoints.py`

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
