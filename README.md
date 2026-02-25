# fastbreak

[![PyPI](https://img.shields.io/pypi/v/fastbreak)](https://pypi.org/project/fastbreak/)
[![Python](https://img.shields.io/pypi/pyversions/fastbreak)](https://pypi.org/project/fastbreak/)
[![License](https://img.shields.io/github/license/reidhoch/fastbreak)](https://github.com/reidhoch/fastbreak/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/reidhoch/fastbreak/ci.yaml?label=CI)](https://github.com/reidhoch/fastbreak/actions)

Async Python client for the NBA Stats API. Fully typed, with Pydantic models and optional DataFrame conversion.

## Installation

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
from fastbreak.endpoints import BoxScoreTraditional

game_ids = ["0022401001", "0022401002", "0022401003"]

async with NBAClient() as client:
    results = await client.get_many(
        [BoxScoreTraditional(game_id=gid) for gid in game_ids],
        max_concurrency=5,
    )
```

Results are returned in the same order as the input. If any request fails, all in-flight requests are cancelled and an `ExceptionGroup` is raised.

### Caching

Enable TTL-based response caching to avoid redundant API calls:

```python
async with NBAClient(cache_ttl=300, cache_maxsize=256) as client:
    result = await client.get(LeagueStandings(season="2025-26"))  # cached for 5 min
    print(client.cache_info)  # {'size': 1, 'maxsize': 256, 'ttl': 300}
    client.clear_cache()
```

## Features

- Async I/O via aiohttp
- Strict mypy typing throughout
- Pydantic models for all responses, with pandas/polars export
- Retries and rate-limit handling built in
- `get_many()` for concurrent batch requests
- Optional TTL response caching

## Available Endpoints

100+ endpoints covering:

| Category | Examples |
|----------|----------|
| **Box Scores** | `BoxScoreTraditional`, `BoxScoreAdvanced`, `BoxScorePlayerTrack` |
| **Players** | `PlayerCareerStats`, `PlayerGameLogs`, `PlayerDashboardByClutch` |
| **Teams** | `TeamDetails`, `TeamGameLog`, `TeamPlayerDashboard` |
| **League** | `LeagueStandings`, `LeagueLeaders`, `LeagueGameLog` |
| **Play-by-Play** | `PlayByPlay`, `GameRotation` |
| **Shooting** | `ShotChartDetail`, `ShotChartLeaguewide` |
| **Draft** | `DraftHistory`, `DraftCombineStats` |

See [`fastbreak.endpoints`](https://github.com/reidhoch/fastbreak/tree/main/src/fastbreak/endpoints) for the full list.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Stargazers

[![Stargazers](https://api.star-history.com/svg?repos=reidhoch/fastbreak&type=date&legend=top-left)](https://www.star-history.com/#reidhoch/fastbreak&type=date&legend=top-left)
