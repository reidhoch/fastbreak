import asyncio

from fastbreak.clients import NBAClient
from fastbreak.endpoints import GravityLeaders


async def get_gravity_leaders() -> None:
    async with NBAClient() as client:
        response = await client.get(GravityLeaders(season="2025-26"))
        leaders = response.leaders
        print("Top 10 Gravity Leaders for Season 2025-26")
        for player in leaders[:10]:
            print(f"{player.FirstName} {player.LastName}: {player.AvgGravityScore}")


asyncio.run(get_gravity_leaders())
