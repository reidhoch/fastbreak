"""Example: project LeBron James for the Lakers' game today.

Run with:
    uv run python examples/projections.py
"""

from __future__ import annotations

import asyncio
from datetime import date

from fastbreak import NBAClient, project_player
from fastbreak.schedule import days_rest_before_game, game_dates_from_schedule, get_team_schedule
from fastbreak.teams import get_team

LAKERS_TEAM_ID = 1610612747
LEBRON_PLAYER_ID = 2544


async def main() -> None:
    today = date.today()

    async with NBAClient() as client:
        schedule = await get_team_schedule(client, team_id=LAKERS_TEAM_ID)

        todays_game = next(
            (
                g
                for g in schedule
                if g.game_date_est and g.game_date_est[:10] == today.isoformat()
            ),
            None,
        )
        if todays_game is None:
            print(f"Lakers are not scheduled to play on {today}.")
            return
        if todays_game.home_team is None or todays_game.away_team is None:
            print(f"Lakers game on {today} has no confirmed opponent yet.")
            return

        is_home = todays_game.home_team.team_id == LAKERS_TEAM_ID
        opponent_team_id = (
            todays_game.away_team.team_id if is_home else todays_game.home_team.team_id
        )
        if opponent_team_id is None:
            print(f"Lakers game on {today} has no confirmed opponent yet.")
            return

        prior_dates = [d for d in game_dates_from_schedule(schedule) if d < today]
        synthetic = [*prior_dates, today]
        days_rest = days_rest_before_game(synthetic, len(synthetic) - 1) or 0

        proj = await project_player(
            client,
            player_id=LEBRON_PLAYER_ID,
            player_name="LeBron James",
            opponent_team_id=opponent_team_id,
            is_home=is_home,
            game_date=today,
            season="2025-26",
            days_rest=days_rest,
            rolling_n=10,
        )

    opponent = get_team(proj.opponent_team_id)
    opponent_name = opponent.full_name if opponent else f"team {proj.opponent_team_id}"
    location = "vs." if proj.is_home else "@"
    print(f"Projection for {proj.player_name} {location} {opponent_name} on {proj.game_date}")
    print(f"  days rest: {days_rest}")
    for name, sp in proj.stats.items():
        print(
            f"  {name:5s}: mean={sp.mean:5.2f}  stdev={sp.stdev:4.2f}  "
            f"rolling={sp.rolling_mean:5.2f}  season={sp.season_mean:5.2f}  "
            f"dist={sp.distribution}"
        )
        for line in (sp.mean - sp.stdev, sp.mean, sp.mean + sp.stdev):
            print(f"    P(over {line:5.2f}) = {sp.prob_over(line):.3f}")


if __name__ == "__main__":
    asyncio.run(main())
