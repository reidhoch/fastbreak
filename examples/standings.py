"""Example: League standings from fastbreak.standings."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.standings import get_conference_standings, get_standings


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Full league standings ──────────────────────────────────────
        print("=" * 60)
        print("Full league standings (current season)")
        print("=" * 60)
        standings = await get_standings(client)
        print(f"  {len(standings)} teams\n")
        print(
            f"  {'#':>3}  {'Team':<24} {'W':>3} {'L':>3}  {'W%':>6}  {'Conf GB':>7}  {'Streak':>7}"
        )
        print("  " + "-" * 60)
        for s in standings:
            print(
                f"  {s.playoff_rank:>3}  {s.team_name:<24}"
                f" {s.wins:>3} {s.losses:>3}"
                f"  {s.win_pct:>6.3f}"
                f"  {s.conference_games_back:>7.1f}"
                f"  {s.str_current_streak:>7}"
            )

        # ── 2. East conference standings ──────────────────────────────────
        print()
        print("=" * 60)
        print("Eastern Conference (by playoff rank)")
        print("=" * 60)
        east = await get_conference_standings(client, "East")
        for s in east:
            print(
                f"  {s.playoff_rank:>2}. {s.team_city} {s.team_name:<18}"
                f"  {s.wins}-{s.losses}"
                f"  ({s.home} home, {s.road} road)"
            )

        # ── 3. West conference standings ──────────────────────────────────
        print()
        print("=" * 60)
        print("Western Conference (by playoff rank)")
        print("=" * 60)
        west = await get_conference_standings(client, "West")
        for s in west:
            print(
                f"  {s.playoff_rank:>2}. {s.team_city} {s.team_name:<18}"
                f"  {s.wins}-{s.losses}"
                f"  ({s.home} home, {s.road} road)"
            )


if __name__ == "__main__":
    asyncio.run(main())
