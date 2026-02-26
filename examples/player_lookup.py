"""Example: Player lookup utilities from fastbreak.players."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.players import (
    get_player,
    get_player_game_log,
    get_player_id,
    search_players,
)


async def main() -> None:  # noqa: PLR0915
    async with NBAClient() as client:
        # 1. Search by partial name — returns closest matches first
        print("=" * 60)
        print("Searching for 'Tyrese'...")
        print("=" * 60)
        results = await search_players(client, "Tyrese")
        for player in results:
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

        # 6. Fetch a player's game log for the season
        print("=" * 60)
        print("Pascal Siakam's last 5 games this season...")
        print("=" * 60)
        siakam_id = await get_player_id(client, "Pascal Siakam")
        if siakam_id:
            log = await get_player_game_log(client, player_id=siakam_id)
            for entry in log[-5:]:
                print(
                    f"  {entry.game_date}  {entry.matchup}"
                    f"  {entry.pts} pts / {entry.reb} reb / {entry.ast} ast"
                    f"  {'W' if entry.wl == 'W' else 'L'}"
                )
        print()


if __name__ == "__main__":
    asyncio.run(main())
