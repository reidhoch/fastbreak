import asyncio
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.endpoints import BoxScoreTraditional, ScoreboardV3


async def get_box_scores() -> None:
    async with NBAClient() as client:
        yesterday = datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
        response = await client.get(ScoreboardV3(game_date=yesterday.isoformat()))
        scoreboard = response.scoreboard
        if not scoreboard:
            print("No games found for yesterday.")
            return
        # Retrieve multiple box scores in a single request
        game_ids = [BoxScoreTraditional(game.game_id) for game in scoreboard.games if game.game_id]
        scores = await client.get_many(game_ids)
        if not scores:
            print("No box scores found.")
            return
        for score in scores:
            boxscore = score.boxScoreTraditional
            away = boxscore.awayTeam
            home = boxscore.homeTeam
            print(f"{away.teamTricode} @ {home.teamTricode}: {away.statistics.points} - {home.statistics.points}")


asyncio.run(get_box_scores())
