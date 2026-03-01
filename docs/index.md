# fastbreak Documentation

## Table of Contents

| File | What's in it |
|------|-------------|
| [getting-started.md](getting-started.md) | Installation, first async request, basic patterns |
| [client.md](client.md) | `NBAClient` reference: caching, retries, `get()`, `get_many()`, signal handling |
| [seasons.md](seasons.md) | Season string utilities: `get_season_from_date`, `season_start_year`, `season_to_season_id` |
| [standings.md](standings.md) | Standings helpers: `get_standings`, `get_conference_standings`, `TeamStanding` fields |
| [players.md](players.md) | Player helpers: search, game logs, stats, leaders, hustle, on/off splits, playtypes |
| [teams.md](teams.md) | Team helpers: lookup, game logs, stats, lineups, net ratings, playtypes, roster, coaches |
| [games.md](games.md) | Game helpers: scoreboard, box scores (traditional, advanced, hustle, scoring), play-by-play, game summary |
| [schedule.md](schedule.md) | Schedule helper: full season schedule, back-to-back detection, rest day utilities |
| [metrics.md](metrics.md) | Pure-computation metrics: true shooting, PER, net rating, pace-adjusted stats |
| [endpoints.md](endpoints.md) | All 100+ endpoint classes: params, response models, type aliases |
| [models.md](models.md) | Response model patterns: `FrozenResponse`, result set validators, v3 models, DataFrame mixins |
| [types.md](types.md) | Type aliases: `Season`, `SeasonType`, `PerMode`, `MeasureType`, `LeagueID`, and more |
| [gotchas.md](gotchas.md) | Known quirks: All-Star game IDs, `SynergyPlaytypes` returning 0 rows, lineup `min` field, and more |
