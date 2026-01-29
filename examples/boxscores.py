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
        game_ids = [
            BoxScoreTraditional(game.game_id)
            for game in scoreboard.games
            if game.game_id
        ]
        # Retrieve multiple box scores in a single request
        scores = await client.get_many(game_ids)
        if not scores:
            print("No box scores found.")
            return
        for score in scores:
            boxscore = score.boxScoreTraditional
            away_team = boxscore.awayTeam.teamTricode
            home_team = boxscore.homeTeam.teamTricode
            away_points = boxscore.awayTeam.statistics.points
            home_points = boxscore.homeTeam.statistics.points
            print(f"{away_team} @ {home_team}: {away_points} - {home_points}")


asyncio.run(get_box_scores())
