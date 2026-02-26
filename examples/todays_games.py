"""Example: Fetching today's games with fastbreak.games."""

import asyncio
from datetime import datetime

from fastbreak.clients import NBAClient
from fastbreak.games import get_todays_games


async def main() -> None:
    async with NBAClient() as client:
        games = await get_todays_games(client)

        if not games:
            print("No games scheduled today.")
            return

        print(f"{len(games)} game(s) today\n")
        for game in games:
            if not game.game_time_utc:
                print("Game time not available.")
                continue
            local_time = datetime.fromisoformat(game.game_time_utc).astimezone(tz=None)
            away = game.away_team.team_tricode if game.away_team else "N/A"
            home = game.home_team.team_tricode if game.home_team else "N/A"
            print(f"  {away} @ {home}  {local_time.strftime('%I:%M %p %Z')}")


if __name__ == "__main__":
    asyncio.run(main())
