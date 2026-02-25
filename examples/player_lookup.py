"""Example: Player lookup utilities from fastbreak.players."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.players import get_player, get_player_id, search_players


async def main() -> None:
    async with NBAClient() as client:
        # 1. Search by partial name — returns closest matches first
        print("=" * 60)
        print("Searching for 'Curry'...")
        print("=" * 60)
        currys = await search_players(client, "Curry")
        for player in currys:
            print(f"  {player.player_first_name} {player.player_last_name}")
            print(f"    ID: {player.person_id}")
            print(f"    Team: {player.team_name} ({player.team_abbreviation})")
            print(f"    Position: {player.position}")
            print()

        # 2. Get a player by numeric ID
        print("=" * 60)
        print("Looking up player ID 2544 (LeBron James)...")
        print("=" * 60)
        lebron = await get_player(client, 2544)
        if lebron:
            print(f"  {lebron.player_first_name} {lebron.player_last_name}")
            print(f"    Team: {lebron.team_city} {lebron.team_name}")
            print(f"    Position: {lebron.position}")
            print(f"    Height: {lebron.height}, Weight: {lebron.weight}")
            print(f"    College: {lebron.college or 'N/A'}")
            print(
                f"    Draft: {lebron.draft_year} Round {lebron.draft_round} Pick {lebron.draft_number}"
            )
            print(f"    Stats: {lebron.pts} PPG, {lebron.reb} RPG, {lebron.ast} APG")
        print()

        # 3. Get a player by exact full name
        print("=" * 60)
        print("Looking up 'Anthony Edwards' by name...")
        print("=" * 60)
        ant = await get_player(client, "Anthony Edwards")
        if ant:
            print(f"  {ant.player_first_name} {ant.player_last_name}")
            print(f"    ID: {ant.person_id}")
            print(f"    Team: {ant.team_city} {ant.team_name}")
            print(f"    Stats: {ant.pts} PPG, {ant.reb} RPG, {ant.ast} APG")
        print()

        # 4. Get just the player ID — useful before calling a player dashboard endpoint
        print("=" * 60)
        print("Getting player ID for 'Nikola Jokić'...")
        print("=" * 60)
        jokic_id = await get_player_id(client, "Nikola Jokić")
        print(f"  Nikola Jokić's player ID: {jokic_id}")
        print()

        # 5. Search with a limit — returns only the top N results
        print("=" * 60)
        print("Top 5 players matching 'James'...")
        print("=" * 60)
        james_players = await search_players(client, "James", limit=5)
        for i, player in enumerate(james_players, 1):
            print(
                f"  {i}. {player.player_first_name} {player.player_last_name}"
                f" ({player.team_abbreviation})"
            )


if __name__ == "__main__":
    asyncio.run(main())
