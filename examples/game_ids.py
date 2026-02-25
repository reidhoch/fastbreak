"""Example: Fetching game IDs with fastbreak.games."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import get_game_ids

# Indiana Pacers team ID
IND_TEAM_ID = 1610612754


async def main() -> None:
    async with NBAClient() as client:
        # 1. All regular-season game IDs for the current season
        print("=" * 60)
        print("All 2024-25 regular season game IDs...")
        print("=" * 60)
        ids = await get_game_ids(client, "2024-25")
        print(f"  {len(ids)} games")
        print(f"  First: {ids[0]}")
        print(f"  Last:  {ids[-1]}")
        print()

        # 2. Playoff game IDs
        print("=" * 60)
        print("2024-25 playoff game IDs...")
        print("=" * 60)
        playoff_ids = await get_game_ids(client, "2024-25", season_type="Playoffs")
        print(f"  {len(playoff_ids)} playoff games")
        if playoff_ids:
            print(f"  First: {playoff_ids[0]}")
            print(f"  Last:  {playoff_ids[-1]}")
        print()

        # 3. Single team's games — one row per game (no deduplication needed)
        print("=" * 60)
        print(f"Pacers (team_id={IND_TEAM_ID}) game IDs for 2024-25...")
        print("=" * 60)
        ind_ids = await get_game_ids(client, "2024-25", team_id=IND_TEAM_ID)
        print(f"  {len(ind_ids)} games")
        if ind_ids:
            print(f"  First: {ind_ids[0]}")
            print(f"  Last:  {ind_ids[-1]}")
        print()

        # 4. Games within a date range
        print("=" * 60)
        print("Games played in January 2025...")
        print("=" * 60)
        jan_ids = await get_game_ids(
            client,
            "2024-25",
            date_from="01/01/2025",
            date_to="01/31/2025",
        )
        print(f"  {len(jan_ids)} games in January 2025")
        print()

        # 5. Team games within a date range — combine both filters
        print("=" * 60)
        print("Pacers games in January 2025...")
        print("=" * 60)
        ind_jan_ids = await get_game_ids(
            client,
            "2024-25",
            team_id=IND_TEAM_ID,
            date_from="01/01/2025",
            date_to="01/31/2025",
        )
        print(f"  {len(ind_jan_ids)} Pacers games in January 2025")
        for game_id in ind_jan_ids:
            print(f"    {game_id}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
