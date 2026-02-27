"""Example: Fetching today's and yesterday's games with fastbreak.games."""

import asyncio
from datetime import datetime

from fastbreak.clients import NBAClient
from fastbreak.games import get_game_summary, get_todays_games, get_yesterdays_games


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Today's games ─────────────────────────────────────────
        print("=" * 60)
        print("Today's games")
        print("=" * 60)
        games = await get_todays_games(client)
        if not games:
            print("  No games scheduled today.")
        else:
            print(f"  {len(games)} game(s)\n")
            for game in games:
                if not game.game_time_utc:
                    continue
                local_time = datetime.fromisoformat(game.game_time_utc).astimezone(
                    tz=None
                )
                away = game.away_team.team_tricode if game.away_team else "N/A"
                home = game.home_team.team_tricode if game.home_team else "N/A"
                print(f"  {away} @ {home}  {local_time.strftime('%I:%M %p %Z')}")
        print()

        # ── 2. Yesterday's games ─────────────────────────────────────
        print("=" * 60)
        print("Yesterday's games")
        print("=" * 60)
        yesterday_games = await get_yesterdays_games(client)
        if not yesterday_games:
            print("  No games yesterday.")
        else:
            print(f"  {len(yesterday_games)} game(s)\n")
            for game in yesterday_games:
                away = game.away_team.team_tricode if game.away_team else "N/A"
                home = game.home_team.team_tricode if game.home_team else "N/A"
                status = game.game_status_text or "Final"
                print(f"  {away} @ {home}  {status}")
        print()

        # ── 3. Game summary (arena, officials, attendance) ──────────
        print("=" * 60)
        print("Game summary — first game from yesterday")
        print("=" * 60)
        game_ids = [g.game_id for g in yesterday_games if g.game_id is not None]
        if not game_ids:
            print("  No completed games to summarise.")
        else:
            game_id = game_ids[0]
            summary = await get_game_summary(client, game_id)
            away = summary.awayTeam.teamTricode if summary.awayTeam else "N/A"
            home = summary.homeTeam.teamTricode if summary.homeTeam else "N/A"
            print(f"  Game:       {away} @ {home}  [{game_id}]")
            print(f"  Status:     {summary.gameStatusText}")
            print(f"  Arena:      {summary.arena.arenaName}, {summary.arena.arenaCity}")
            print(f"  Attendance: {summary.attendance:,}")
            if summary.officials:
                names = ", ".join(o.name for o in summary.officials)
                print(f"  Officials:  {names}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
