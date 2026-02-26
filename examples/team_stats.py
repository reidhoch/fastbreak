"""Example: Team stats and lineup analysis from fastbreak.teams."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.teams import get_lineup_stats, get_team_stats, search_teams


async def main() -> None:
    async with NBAClient() as client:
        ind = search_teams("IND")[0]

        # 1. Indiana Pacers season stats
        print("=" * 60)
        print(f"{ind.full_name} — season stats")
        print("=" * 60)
        teams = await get_team_stats(client)
        pacers = next((t for t in teams if t.team_id == ind.id), None)
        if pacers:
            print(f"  PPG:  {pacers.pts:5.1f}")
            print(f"  RPG:  {pacers.reb:5.1f}")
            print(f"  APG:  {pacers.ast:5.1f}")
            print(f"  FG%:  {pacers.fg_pct:.3f}")
            print(f"  3P%:  {pacers.fg3_pct:.3f}")
        print()

        # 2. Pacers 5-man lineup stats — top 5 by plus/minus
        print("=" * 60)
        print(f"{ind.full_name} — top 5 lineups by +/- per game")
        print("=" * 60)
        lineups = await get_lineup_stats(client, team_id=ind.id)
        top_lineups = sorted(lineups, key=lambda ln: ln.plus_minus, reverse=True)[:5]
        for lineup in top_lineups:
            print(
                f"  {lineup.group_name}"
                f"  {lineup.gp} GP  +/- {lineup.plus_minus:+.1f}"
            )
        print()

        # 3. Two-man combinations — which pair logs the most minutes?
        print("=" * 60)
        print(f"{ind.full_name} — top 3 two-man combos by minutes")
        print("=" * 60)
        pairs = await get_lineup_stats(client, team_id=ind.id, group_quantity=2)
        top_pairs = sorted(pairs, key=lambda ln: ln.min, reverse=True)[:3]
        for pair in top_pairs:
            print(f"  {pair.group_name}  {pair.min:.0f} min  +/- {pair.plus_minus:+.1f}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
