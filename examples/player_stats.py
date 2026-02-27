"""Example: Player career stats and league leaders from fastbreak.players."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.players import get_hustle_stats, get_league_leaders, get_player_stats


async def main() -> None:
    async with NBAClient() as client:
        # 1. Career stats for Tyrese Haliburton (season-by-season)
        print("=" * 60)
        print("Tyrese Haliburton — career season averages")
        print("=" * 60)
        stats = await get_player_stats(client, player_id=1630169)
        for season in stats.season_totals_regular_season[-5:]:
            print(
                f"  {season.season_id}  {season.team_abbreviation}"
                f"  {season.gp} GP"
                f"  {season.pts} / {season.reb} / {season.ast}"
            )
        career = (
            stats.career_totals_regular_season[0]
            if stats.career_totals_regular_season
            else None
        )
        if career:
            print(f"  Career: {career.pts} pts  {career.reb} reb  {career.ast} ast")
        print()

        # 2. Hustle stats for Aaron Nesmith
        print("=" * 60)
        print("Aaron Nesmith — hustle stats")
        print("=" * 60)
        hustle = await get_hustle_stats(client, player_id=1630174)
        if hustle:
            print(f"  Deflections:       {hustle.deflections:.1f}")
            print(f"  Screen assists:    {hustle.screen_assists:.1f}")
            print(f"  Charges drawn:     {hustle.charges_drawn:.1f}")
            print(f"  Contested shots:   {hustle.contested_shots:.1f}")
            print(f"  Box outs:          {hustle.box_outs:.1f}")
        else:
            print("  Not found.")
        print()

        # 3. Top 10 scorers this season
        print("=" * 60)
        print("Top 10 scorers this season")
        print("=" * 60)
        scorers = await get_league_leaders(client, stat_category="PTS", limit=10)
        for i, leader in enumerate(scorers, 1):
            print(f"  {i:2}. {leader.player:<25} {leader.pts:5.1f} PPG")
        print()

        # 4. Top 5 assist leaders
        print("=" * 60)
        print("Top 5 assist leaders this season")
        print("=" * 60)
        assisters = await get_league_leaders(client, stat_category="AST", limit=5)
        for i, leader in enumerate(assisters, 1):
            print(f"  {i}. {leader.player:<25} {leader.ast:4.1f} APG")
        print()


if __name__ == "__main__":
    asyncio.run(main())
