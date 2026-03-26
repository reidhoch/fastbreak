# fastbreak

[![PyPI](https://img.shields.io/pypi/v/fastbreak)](https://pypi.org/project/fastbreak/)
[![Python](https://img.shields.io/pypi/pyversions/fastbreak)](https://pypi.org/project/fastbreak/)
[![License](https://img.shields.io/github/license/reidhoch/fastbreak)](https://github.com/reidhoch/fastbreak/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/reidhoch/fastbreak/ci.yaml?label=CI)](https://github.com/reidhoch/fastbreak/actions)

Async Python client for the NBA Stats API, fully typed with Pydantic. Pandas and polars exports are optional.

## Installation

Requires Python 3.12+.

```bash
pip install fastbreak
```

With DataFrame support:

```bash
pip install fastbreak pandas   # or polars
```

## Quick Start

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async def main():
    async with NBAClient() as client:
        standings = await client.get(LeagueStandings(season="2025-26"))

        for team in standings.standings[:5]:
            print(f"{team.team_name}: {team.wins}-{team.losses}")

asyncio.run(main())
```

### Convert to DataFrame

```python
from fastbreak.models import TeamStanding

# To pandas
df = TeamStanding.to_pandas(standings.standings)

# To polars
df = TeamStanding.to_polars(standings.standings)
```

### Batch Requests

Fetch multiple endpoints concurrently with `get_many()`:

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import BoxScoreTraditional

game_ids = ["0022500001", "0022500002", "0022500003"]

async with NBAClient() as client:
    results = await client.get_many(
        [BoxScoreTraditional(game_id=gid) for gid in game_ids],
        max_concurrency=5,
    )
```

Results come back in the same order as the input. If any request fails, all in-flight requests are cancelled and an `ExceptionGroup` is raised.

### Caching

Pass `cache_ttl` to avoid hitting the API twice for the same response:

```python
from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings

async with NBAClient(cache_ttl=300, cache_maxsize=256) as client:
    result = await client.get(LeagueStandings(season="2025-26"))  # cached for 5 min
    print(client.cache_info)  # {'size': 1, 'maxsize': 256, 'ttl': 300}
    client.clear_cache()
```

## Features

- Async I/O via aiohttp (asyncio only)
- Strict mypy typing
- Pydantic models for all responses, with pandas/polars export
- Retries and rate-limit handling built in
- `get_many()` for concurrent batch requests
- Optional TTL response caching
- Pure-computation analytics: BPM, VORP, PER, true shooting, win shares, Pythagorean wins

## Utility Modules

Skip the endpoint boilerplate for common operations. Import directly and pass `client` as the first argument.

### Data Access

| Module | Key Functions |
|--------|---------------|
| `fastbreak.players` | `search_players`, `get_player_game_log`, `get_player_stats`, `get_league_leaders` |
| `fastbreak.teams` | `search_teams`, `get_team_stats`, `get_team_game_log`, `get_lineup_stats` |
| `fastbreak.games` | `get_todays_games`, `get_games_on_date`, `get_box_scores`, `get_play_by_play` |
| `fastbreak.standings` | `get_standings`, `get_conference_standings`, `magic_number` |
| `fastbreak.schedule` | `get_team_schedule`, `is_back_to_back`, `travel_distance`, `schedule_density` |
| `fastbreak.seasons` | `get_season_from_date`, `season_start_year` — sync, no client needed |

### Shooting & Defense

| Module | Key Functions |
|--------|---------------|
| `fastbreak.shots` | `get_shot_chart`, `zone_breakdown`, `shot_quality_vs_league`, `xfg_pct` |
| `fastbreak.defense` | `get_team_defense_zones`, `get_team_opponent_stats`, `defensive_shot_quality_vs_league` |
| `fastbreak.tracking` | `get_player_tracking_profile`, `get_team_tracking_profile`, `get_player_shot_defense` |

### Matchups, Lineups & Rotations

| Module | Key Functions |
|--------|---------------|
| `fastbreak.matchups` | `get_primary_defenders`, `get_defensive_assignments`, `get_team_matchup_summary` |
| `fastbreak.lineups` | `get_league_lineups`, `get_top_lineups`, `get_two_man_combos`, `get_lineup_efficiency` |
| `fastbreak.rotations` | `get_game_rotations`, `get_rotation_summary`, `lineup_stints`, `minutes_distribution` |

### Analytics & Comparison

| Module | Key Functions |
|--------|---------------|
| `fastbreak.metrics` | `bpm`, `vorp`, `per`, `true_shooting`, `usage_pct`, `pythagorean_win_pct` |
| `fastbreak.compare` | `get_player_comparison`, `comparison_deltas`, `comparison_edges`, `stat_leader` |
| `fastbreak.clutch` | `get_player_clutch_profile`, `get_league_clutch_leaders`, `clutch_score` |
| `fastbreak.estimated` | `get_player_estimated_metrics`, `get_team_estimated_metrics`, `get_estimated_leaders` |
| `fastbreak.splits` | `get_player_splits_profile`, `get_team_splits_profile` |
| `fastbreak.hot_hand` | `get_hot_hand_stats`, `hot_hand_result`, `miller_sanjurjo_bias`, `extract_shot_sequences` |
| `fastbreak.transition` | `get_transition_stats`, `classify_possessions`, `transition_frequency`, `transition_efficiency` |

```python
from fastbreak.players import search_players, get_player_game_log
from fastbreak.games import get_todays_games

async with NBAClient() as client:
    players = await search_players(client, "Jokić")
    log     = await get_player_game_log(client, player_id=players[0].person_id)
    games   = await get_todays_games(client)
```

## Available Endpoints

Over 115 endpoints covering:

| Category | Examples |
|----------|----------|
| **Box Scores** | `BoxScoreTraditional`, `BoxScoreAdvanced`, `BoxScorePlayerTrack`, `BoxScoreHustle`, `BoxScoreMatchups` |
| **Players** | `PlayerCareerStats`, `PlayerGameLogs`, `PlayerDashboardByClutch`, `PlayerEstimatedMetrics` |
| **Teams** | `TeamDetails`, `TeamGameLog`, `TeamPlayerDashboard`, `TeamEstimatedMetrics` |
| **League** | `LeagueStandings`, `LeagueLeaders`, `LeagueGameLog`, `LeagueDashLineups` |
| **Tracking** | `PlayerDashPtShots`, `PlayerDashPtPass`, `PlayerDashPtReb`, `PlayerDashPtShotDefend` |
| **Matchups** | `BoxScoreMatchupsV3`, `LeagueSeasonMatchups`, `MatchupsRollup`, `PlayerVsPlayer` |
| **Shooting** | `ShotChartDetail`, `ShotChartLeaguewide`, `LeagueDashTeamShotLocations` |
| **Play-by-Play** | `PlayByPlay`, `GameRotation` |
| **Hustle** | `HustleStatsBoxscore`, `LeagueHustleStatsPlayer`, `LeagueHustleStatsTeam` |
| **Splits** | `PlayerDashboardByGeneralSplits`, `PlayerDashboardByShootingSplits`, `TeamDashboardByGeneralSplits` |
| **Draft** | `DraftHistory`, `DraftCombineStats`, `DraftCombineDrillResults` |

See [`fastbreak.endpoints`](https://github.com/reidhoch/fastbreak/tree/main/src/fastbreak/endpoints) for the full list.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Stargazers

[![Stargazers](https://api.star-history.com/svg?repos=reidhoch/fastbreak&type=date&legend=top-left)](https://www.star-history.com/#reidhoch/fastbreak&type=date&legend=top-left)
