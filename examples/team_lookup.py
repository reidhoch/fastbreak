"""Example: Team search and game log utilities from fastbreak.teams."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.teams import get_team_game_log, search_teams


async def main() -> None:
    # search_teams is synchronous — no client needed
    print("=" * 60)
    print("Searching for 'IND'...")
    print("=" * 60)
    results = search_teams("IND")
    for team in results:
        print(f"  {team.full_name}  (id={team.id}, abbr={team.abbreviation})")
        print(f"    {team.conference} / {team.division}")
    print()

    print("=" * 60)
    print("Searching for 'New'...")
    print("=" * 60)
    for team in search_teams("New"):
        print(f"  {team.full_name}  ({team.abbreviation})")
    print()

    async with NBAClient() as client:
        # Fetch the Pacers' game log and show the last 5 games
        ind = search_teams("IND")[0]
        print("=" * 60)
        print(f"{ind.full_name} — last 5 games this season")
        print("=" * 60)
        log = await get_team_game_log(client, team_id=ind.id)
        for entry in log[-5:]:
            print(
                f"  {entry.game_date}  {entry.matchup}"
                f"  {entry.pts} pts  {'W' if entry.wl == 'W' else 'L'}"
                f"  ({entry.wins}-{entry.losses})"
            )
        print()


if __name__ == "__main__":
    asyncio.run(main())
