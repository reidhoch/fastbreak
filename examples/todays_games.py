import asyncio
from datetime import UTC, datetime

from fastbreak.clients import NBAClient
from fastbreak.endpoints import ScoreboardV3


async def get_games() -> None:
    async with NBAClient() as client:
        today = datetime.now(tz=UTC).astimezone().date()
        response = await client.get(ScoreboardV3(game_date=today.isoformat()))
        if response.scoreboard:
            for game in response.scoreboard.games:
                if not game.game_time_utc:
                    print("Game time not available.")
                    continue
                local_time = datetime.fromisoformat(game.game_time_utc).astimezone(tz=None)
                away_team = game.away_team.team_tricode if game.away_team else "N/A"
                home_team = game.home_team.team_tricode if game.home_team else "N/A"
                print(f"{away_team} @ {home_team} at {local_time.time()}")


asyncio.run(get_games())
