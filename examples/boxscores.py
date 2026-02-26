"""Example: Fetching box scores with fastbreak.games."""

import asyncio
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.games import get_box_scores, get_games_on_date


async def main() -> None:
    async with NBAClient() as client:
        yesterday = (
            datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
        ).isoformat()

        games = await get_games_on_date(client, yesterday)
        if not games:
            print(f"No games on {yesterday}.")
            return

        print(f"{len(games)} game(s) on {yesterday}\n")

        game_ids = [g.game_id for g in games if g.game_id]
        box_scores = await get_box_scores(client, game_ids)

        for game_id, boxscore in box_scores.items():
            away = boxscore.awayTeam
            home = boxscore.homeTeam
            print(
                f"  {away.teamTricode} @ {home.teamTricode}:"
                f"  {away.statistics.points} - {home.statistics.points}"
                f"  [{game_id}]"
            )


if __name__ == "__main__":
    asyncio.run(main())
