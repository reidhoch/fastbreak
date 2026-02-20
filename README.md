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

## Features

- **Async-first** - Built on aiohttp for high-performance concurrent requests
- **Fully typed** - Complete type hints with strict mypy compliance
- **Pydantic models** - Validated response parsing with IDE autocomplete
- **DataFrame support** - Optional conversion to pandas or polars
- **Automatic retries** - Handles rate limiting and transient errors

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

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Stargazers

[![Stargazers](https://api.star-history.com/svg?repos=reidhoch/fastbreak&type=date&legend=top-left)](https://www.star-history.com/#reidhoch/fastbreak&type=date&legend=top-left)
