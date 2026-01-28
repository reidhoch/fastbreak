import asyncio
from collections import defaultdict
from datetime import date, timedelta

from aiohttp import ClientTimeout

from fastbreak.clients import NBAClient
from fastbreak.endpoints import BoxScoreTraditional, ScoreboardV3


async def analyze_player_trends(
    start_date: date, end_date: date, min_games: int = 2
) -> list[dict]:
    """
    Analyze player performance trends across a date range.

    Returns players sorted by scoring trend (recent vs early performance).
    """
    async with NBAClient(request_delay=0.6) as client:
        # Step 1: Get all game IDs in the date range
        print(f"Fetching games from {start_date} to {end_date}...")
        game_ids: list[str] = []
        current = start_date

        while current <= end_date:
            response = await client.get(ScoreboardV3(game_date=current.isoformat()))
            for game in response.scoreboard.games:
                if game.game_status == 3:  # Final
                    game_ids.append(game.game_id)
            current += timedelta(days=1)

        print(f"Found {len(game_ids)} completed games")

        if not game_ids:
            return []

        # Step 2: Fetch box scores with limited concurrency to avoid rate limits
        print("Fetching box scores...")
        endpoints = [BoxScoreTraditional(game_id=gid) for gid in game_ids]
        box_scores = await client.get_many(endpoints, max_concurrency=2)

        # Step 3: Aggregate player stats
        player_games: dict[int, list[dict]] = defaultdict(list)

        for box_score in box_scores:
            game_date = box_score.boxScoreTraditional.gameId[:8]  # YYYYMMDD prefix

            for team in [
                box_score.boxScoreTraditional.homeTeam,
                box_score.boxScoreTraditional.awayTeam,
            ]:
                for player in team.players:
                    if player.statistics.minutes and ":" in player.statistics.minutes:
                        mins = int(player.statistics.minutes.split(":")[0])
                        if mins >= 10:  # Only players with 10+ minutes
                            player_games[player.personId].append(
                                {
                                    "name": player.firstName + " " + player.familyName,
                                    "team": team.teamTricode,
                                    "date": game_date,
                                    "pts": player.statistics.points,
                                    "reb": player.statistics.reboundsTotal,
                                    "ast": player.statistics.assists,
                                    "min": mins,
                                }
                            )

        # Step 4: Calculate trends for players with enough games
        trends = []

        for player_id, games in player_games.items():
            if len(games) < min_games:
                continue

            # Sort by date
            games.sort(key=lambda g: g["date"])

            # Split into first half and second half
            mid = len(games) // 2
            first_half = games[:mid]
            second_half = games[mid:]

            avg_first = sum(g["pts"] for g in first_half) / len(first_half)
            avg_second = sum(g["pts"] for g in second_half) / len(second_half)
            trend = avg_second - avg_first

            trends.append(
                {
                    "player_id": player_id,
                    "name": games[0]["name"],
                    "team": games[-1]["team"],
                    "games": len(games),
                    "ppg_early": round(avg_first, 1),
                    "ppg_recent": round(avg_second, 1),
                    "trend": round(trend, 1),
                    "total_ppg": round(sum(g["pts"] for g in games) / len(games), 1),
                }
            )

        # Sort by trend (hottest players first)
        trends.sort(key=lambda x: x["trend"], reverse=True)
        return trends


async def main():
    # Analyze the last week
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=14)

    trends = await analyze_player_trends(start, end, min_games=3)

    if not trends:
        print("No data found")
        return

    # Print hottest players
    print("\n🔥 HEATING UP (Biggest Scoring Increase)")
    print("-" * 60)
    print(f"{'Player':<25} {'Team':<5} {'GP':<4} {'Early':<7} {'Recent':<7} {'Trend':<7}")
    print("-" * 60)
    for p in trends[:10]:
        trend_str = f"+{p['trend']}" if p["trend"] >= 0 else str(p["trend"])
        print(
            f"{p['name']:<25} {p['team']:<5} {p['games']:<4} "
            f"{p['ppg_early']:<7} {p['ppg_recent']:<7} {trend_str:<7}"
        )

    # Print cooling players
    print("\n❄️ COOLING DOWN (Biggest Scoring Decrease)")
    print("-" * 60)
    for p in trends[-10:]:
        trend_str = f"+{p['trend']}" if p["trend"] >= 0 else str(p["trend"])
        print(
            f"{p['name']:<25} {p['team']:<5} {p['games']:<4} "
            f"{p['ppg_early']:<7} {p['ppg_recent']:<7} {trend_str:<7}"
        )


if __name__ == "__main__":
    asyncio.run(main())
