"""Example: Player lookup utilities in fastbreak."""

import asyncio

from fastbreak.clients import NBAClient


async def main() -> None:
    """Demonstrate player lookup functionality."""
    async with NBAClient() as client:
        # 1. Search for players by partial name
        print("=" * 60)
        print("Searching for 'Curry'...")
        print("=" * 60)
        currys = await client.search_players("Curry")
        for player in currys:
            print(f"  {player.player_first_name} {player.player_last_name}")
            print(f"    ID: {player.person_id}")
            print(f"    Team: {player.team_name} ({player.team_abbreviation})")
            print(f"    Position: {player.position}")
            print()

        # 2. Get player by ID
        print("=" * 60)
        print("Looking up player ID 2544 (LeBron James)...")
        print("=" * 60)
        lebron = await client.get_player(2544)
        if lebron:
            print(f"  {lebron.player_first_name} {lebron.player_last_name}")
            print(f"    Team: {lebron.team_city} {lebron.team_name}")
            print(f"    Position: {lebron.position}")
            print(f"    Height: {lebron.height}, Weight: {lebron.weight}")
            print(f"    College: {lebron.college or 'N/A'}")
            print(f"    Draft: {lebron.draft_year} Round {lebron.draft_round} Pick {lebron.draft_number}")
            print(f"    Stats: {lebron.pts} PPG, {lebron.reb} RPG, {lebron.ast} APG")
        print()

        # 3. Get player by exact name
        print("=" * 60)
        print("Looking up 'Anthony Edwards' by name...")
        print("=" * 60)
        ant = await client.get_player("Anthony Edwards")
        if ant:
            print(f"  {ant.player_first_name} {ant.player_last_name}")
            print(f"    ID: {ant.person_id}")
            print(f"    Team: {ant.team_city} {ant.team_name}")
            print(f"    Stats: {ant.pts} PPG, {ant.reb} RPG, {ant.ast} APG")
        print()

        # 4. Get just the player ID
        print("=" * 60)
        print("Getting player ID for 'Nikola Jokić'...")
        print("=" * 60)
        jokic_id = await client.get_player_id("Nikola Jokić")
        print(f"  Nikola Jokić's player ID: {jokic_id}")
        print()

        # 5. Search with limit
        print("=" * 60)
        print("Top 5 players matching 'James'...")
        print("=" * 60)
        james_players = await client.search_players("James", limit=5)
        for i, player in enumerate(james_players, 1):
            print(f"  {i}. {player.player_first_name} {player.player_last_name} ({player.team_abbreviation})")


if __name__ == "__main__":
    asyncio.run(main())
