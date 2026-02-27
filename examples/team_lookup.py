"""Example: Team search and game log utilities from fastbreak.teams."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.teams import (
    TEAMS,
    TeamID,
    TeamInfo,
    get_team,
    get_team_game_log,
    get_team_id,
    search_teams,
    teams_by_conference,
    teams_by_division,
)


async def main() -> None:  # noqa: PLR0915
    # ── TEAMS — full 30-team registry ───────────────────────────────
    print("=" * 60)
    print("TEAMS — 30-team registry (first 5 alphabetically)")
    print("=" * 60)
    for team in sorted(TEAMS.values(), key=lambda t: t.full_name)[:5]:
        print(f"  {team.full_name:<28}  {team.abbreviation}  id={team.id.value}")
    print(f"\n  Total teams: {len(TEAMS)}")
    print()

    # ── get_team — look up by abbreviation, full name, city, or ID ──
    print("=" * 60)
    print("get_team — look up by abbreviation, name, or numeric ID")
    print("=" * 60)
    identifiers: list[str | int] = [
        "LAL",
        "Golden State Warriors",
        "Chicago",
        1610612754,
    ]
    for identifier in identifiers:
        team: TeamInfo | None = get_team(identifier)
        if team:
            print(f"  {identifier!s:<30}  →  {team.full_name} ({team.abbreviation})")
        else:
            print(f"  {identifier!s:<30}  →  not found")
    print()

    # ── get_team_id — returns the TeamID enum value ──────────────────
    print("=" * 60)
    print("get_team_id — resolve identifier to numeric TeamID")
    print("=" * 60)
    for query in ["BOS", "Lakers", "Unknown FC"]:
        tid: TeamID | None = get_team_id(query)
        print(f"  {query:<20}  →  {tid.value if tid else 'None'}")
    print()

    # ── teams_by_conference / teams_by_division ──────────────────────
    print("=" * 60)
    print("teams_by_conference / teams_by_division")
    print("=" * 60)
    east = teams_by_conference("East")
    west = teams_by_conference("West")
    print(f"  East: {len(east)} teams  |  West: {len(west)} teams")

    atlantic = teams_by_division("Atlantic")
    northwest = teams_by_division("Northwest")
    print(f"  Atlantic: {', '.join(t.abbreviation for t in atlantic)}")
    print(f"  Northwest: {', '.join(t.abbreviation for t in northwest)}")
    print()

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
