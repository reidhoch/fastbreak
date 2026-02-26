"""Example: Play-by-play analysis from fastbreak.games."""

import asyncio
from collections import Counter
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.games import get_games_on_date, get_play_by_play


async def main() -> None:
    async with NBAClient() as client:
        # Pick yesterday's first game as our example
        yesterday = (datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)).isoformat()
        games = await get_games_on_date(client, yesterday)

        if not games:
            print(f"No games on {yesterday}.")
            return

        game = games[0]
        if game.game_id is None:
            print("No game ID available.")
            return

        away = game.away_team.team_tricode if game.away_team else "AWY"
        home = game.home_team.team_tricode if game.home_team else "HME"
        print(f"Play-by-play: {away} @ {home}  ({yesterday})\n")

        actions = await get_play_by_play(client, game.game_id)
        print(f"  Total actions: {len(actions)}")

        # Action type breakdown
        type_counts: Counter[str] = Counter(
            a.actionType for a in actions if a.actionType
        )
        print("\n  Top action types:")
        for action_type, count in type_counts.most_common(8):
            print(f"    {action_type:<20} {count:4}")

        # Fourth-quarter actions only
        q4 = [a for a in actions if a.period == 4]  # noqa: PLR2004
        print(f"\n  4th-quarter actions: {len(q4)}")

        # Last 5 scoring plays
        scoring = [a for a in actions if a.shotResult == "Made"]
        print("\n  Last 5 made shots:")
        for action in scoring[-5:]:
            clock = getattr(action, "clock", "")
            desc = getattr(action, "description", "")
            print(f"    Q{action.period} {clock}  {desc}")


if __name__ == "__main__":
    asyncio.run(main())
