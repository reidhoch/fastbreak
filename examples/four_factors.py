"""Example: Fetching four factors box scores with fastbreak.games.

Covers:
  - get_yesterdays_games    — find recent game IDs
  - get_box_scores_four_factors — Dean Oliver's Four Factors per team
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import get_box_scores_four_factors, get_yesterdays_games


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Yesterday's games ────────────────────────────────────────
        print("=" * 72)
        print("Four Factors  (get_box_scores_four_factors)")
        print("=" * 72)
        games = await get_yesterdays_games(client)
        if not games:
            print("  No games yesterday.")
            return

        game_ids = [g.game_id for g in games if g.game_id]
        four = await get_box_scores_four_factors(client, game_ids)

        # ── 2. Print four factors for each game ─────────────────────────
        for game_id, data in four.items():
            away = data.awayTeam
            home = data.homeTeam
            tri_a = away.teamTricode or "AWY"
            tri_h = home.teamTricode or "HME"

            print(f"\n  {tri_a} @ {tri_h}  [{game_id}]")
            print(f"  {'':25} {'eFG%':>6}  {'TOV%':>6}  {'OREB%':>6}  {'FTR':>6}")
            print("  " + "-" * 55)

            for label, team in [(tri_a, away), (tri_h, home)]:
                s = team.statistics
                print(
                    f"  {label + ' (off)':25}"
                    f" {s.effectiveFieldGoalPercentage:>6.1%}"
                    f"  {s.teamTurnoverPercentage:>6.1%}"
                    f"  {s.offensiveReboundPercentage:>6.1%}"
                    f"  {s.freeThrowAttemptRate:>6.3f}"
                )
                print(
                    f"  {label + ' (opp def)':25}"
                    f" {s.oppEffectiveFieldGoalPercentage:>6.1%}"
                    f"  {s.oppTeamTurnoverPercentage:>6.1%}"
                    f"  {s.oppOffensiveReboundPercentage:>6.1%}"
                    f"  {s.oppFreeThrowAttemptRate:>6.3f}"
                )


if __name__ == "__main__":
    asyncio.run(main())
