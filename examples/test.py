from cachetools.func import ttl_cache

from fastbreak.clients import NBAClient
import asyncio
from pprint import pprint
from fastbreak.games import get_game_summary
from fastbreak.players import get_player


async def main() -> None:
    async with NBAClient(cache_ttl=30) as client:
        game_id = "0022501039"  # Example game ID
        summary = await get_game_summary(client, game_id)
        for player in summary.awayTeam.players:
            plyr = await get_player(client, identifier=player.personId)
            pprint(f"{plyr.player_first_name} {plyr.player_last_name}")


if __name__ == "__main__":
    asyncio.run(main())
