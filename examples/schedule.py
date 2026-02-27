"""Example: Schedule utilities from fastbreak.schedule."""

import asyncio
from datetime import date

from fastbreak.clients import NBAClient
from fastbreak.schedule import days_rest_before_game, get_team_schedule, is_back_to_back
from fastbreak.teams import get_team_id

_ind_id = get_team_id("IND")
if _ind_id is None:
    msg = "IND team not found"
    raise ValueError(msg)
IND_TEAM_ID: int = int(_ind_id)


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Full team schedule ────────────────────────────────────
        print("=" * 60)
        print("Indiana Pacers — 2024-25 schedule (first 10 games)")
        print("=" * 60)
        games = await get_team_schedule(client, team_id=IND_TEAM_ID, season="2024-25")
        print(f"  {len(games)} total games scheduled\n")
        for game in games[:10]:
            if not game.game_date_est:
                continue
            game_date = game.game_date_est[:10]
            away = game.away_team.team_tricode if game.away_team else "???"
            home = game.home_team.team_tricode if game.home_team else "???"
            status = game.game_status_text or ""
            print(f"  {game_date}  {away} @ {home}  {status}")
        print()

        # ── 2. Back-to-back detection ────────────────────────────────
        print("=" * 60)
        print("Pacers — back-to-backs in 2024-25")
        print("=" * 60)
        # Keep (game, date) pairs together to avoid parallel-list index drift
        valid_games = [
            (g, date.fromisoformat(g.game_date_est[:10]))
            for g in games
            if g.game_date_est
        ]
        game_dates = [d for _, d in valid_games]

        back_to_backs = [
            (i, game_dates[i])
            for i in range(len(game_dates))
            if is_back_to_back(game_dates, i)
        ]
        print(f"  {len(back_to_backs)} back-to-back games")
        for i, d in back_to_backs[:5]:
            rest = days_rest_before_game(game_dates, i)
            game, _ = valid_games[i]
            away = game.away_team.team_tricode if game.away_team else "???"
            home = game.home_team.team_tricode if game.home_team else "???"
            print(f"  Game {i + 1:3d}  {d}  {away} @ {home}  ({rest} days rest)")
        print()

        # ── 3. days_rest_before_game — inspect rest around an example stretch ──
        print("=" * 60)
        print("Rest days before each of the first 5 games")
        print("=" * 60)
        for i in range(min(5, len(game_dates))):
            rest = days_rest_before_game(game_dates, i)
            game, d = valid_games[i]
            away = game.away_team.team_tricode if game.away_team else "???"
            home = game.home_team.team_tricode if game.home_team else "???"
            rest_str = str(rest) if rest is not None else "first game"
            print(f"  Game {i + 1}  {d}  {away} @ {home}  rest={rest_str}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
