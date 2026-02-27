import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.endpoints import BoxScoreTraditional, ScoreboardV3


@dataclass(frozen=True)
class PlayerGame:
    name: str
    team: str
    date: str
    pts: int
    reb: int
    ast: int
    min: int


@dataclass(frozen=True)
class PlayerTrend:
    player_id: int
    name: str
    team: str
    games: int
    ppg_early: float
    ppg_recent: float
    trend: float
    total_ppg: float


async def analyze_player_trends(  # noqa: C901
    start_date: date, end_date: date, min_games: int = 2
) -> list[PlayerTrend]:
    """
    Analyze player performance trends across a date range.

    Returns players sorted by scoring trend (recent vs early performance).
    """
    async with NBAClient(request_delay=1.0) as client:
        # Step 1: Get all game IDs in the date range
        print(f"Fetching games from {start_date} to {end_date}...")
        game_ids: list[str] = []
        current = start_date

        while current <= end_date:
            response = await client.get(ScoreboardV3(game_date=current.isoformat()))
            if response.scoreboard:
                game_ids.extend(
                    game.game_id
                    for game in response.scoreboard.games
                    if game.game_status == 3  # noqa: PLR2004
                    and game.game_id is not None
                    and game.game_id[:3] == "002"  # regular season only (skip All-Star/preseason)
                )
            current += timedelta(days=1)

        print(f"Found {len(game_ids)} completed games")

        if not game_ids:
            return []

        # Step 2: Fetch box scores with limited concurrency to avoid rate limits
        print("Fetching box scores...")
        endpoints = [BoxScoreTraditional(game_id=gid) for gid in game_ids]
        box_scores = await client.get_many(endpoints, max_concurrency=2)

        # Step 3: Aggregate player stats
        player_games: dict[int, list[PlayerGame]] = defaultdict(list)

        for box_score in box_scores:
            game_date = box_score.boxScoreTraditional.gameId[:8]  # YYYYMMDD prefix

            for team in [
                box_score.boxScoreTraditional.homeTeam,
                box_score.boxScoreTraditional.awayTeam,
            ]:
                for player in team.players:
                    if (
                        not player.statistics.minutes
                        or ":" not in player.statistics.minutes
                    ):
                        continue
                    mins = int(player.statistics.minutes.split(":")[0])
                    if mins < 10:  # noqa: PLR2004 — only players with 10+ minutes
                        continue
                    player_games[player.personId].append(
                        PlayerGame(
                            name=f"{player.firstName} {player.familyName}",
                            team=team.teamTricode,
                            date=game_date,
                            pts=player.statistics.points,
                            reb=player.statistics.reboundsTotal,
                            ast=player.statistics.assists,
                            min=mins,
                        )
                    )

        # Step 4: Calculate trends for players with enough games
        trends: list[PlayerTrend] = []

        for player_id, games in player_games.items():
            if len(games) < min_games:
                continue

            # Sort by date
            sorted_games = sorted(games, key=lambda g: g.date)

            # Split into first half and second half
            mid = len(sorted_games) // 2
            first_half = sorted_games[:mid]
            second_half = sorted_games[mid:]

            avg_first = sum(g.pts for g in first_half) / len(first_half)
            avg_second = sum(g.pts for g in second_half) / len(second_half)
            trend = avg_second - avg_first

            trends.append(
                PlayerTrend(
                    player_id=player_id,
                    name=sorted_games[0].name,
                    team=sorted_games[-1].team,
                    games=len(sorted_games),
                    ppg_early=round(avg_first, 1),
                    ppg_recent=round(avg_second, 1),
                    trend=round(trend, 1),
                    total_ppg=round(
                        sum(g.pts for g in sorted_games) / len(sorted_games), 1
                    ),
                )
            )

        # Sort by trend (hottest players first)
        trends.sort(key=lambda x: x.trend, reverse=True)
        return trends


async def main() -> None:
    # Analyze the last 2 weeks
    end = datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
    start = end - timedelta(days=14)

    trends = await analyze_player_trends(start, end, min_games=3)

    if not trends:
        print("No data found")
        return

    def print_players(title: str, players: list[PlayerTrend]) -> None:
        print(f"\n{title}")
        print("-" * 60)
        print(
            f"{'Player':<25} {'Team':<5} {'GP':<4} {'Early':<7} {'Recent':<7} {'Trend':<7}"
        )
        print("-" * 60)
        for p in players:
            trend_str = f"+{p.trend}" if p.trend >= 0 else str(p.trend)
            print(
                f"{p.name:<25} {p.team:<5} {p.games:<4} "
                f"{p.ppg_early:<7} {p.ppg_recent:<7} {trend_str:<7}"
            )

    # Print hottest and cooling players
    print_players("🔥 HEATING UP (Biggest Scoring Increase)", trends[:10])
    print_players("❄️ COOLING DOWN (Biggest Scoring Decrease)", trends[-10:])


if __name__ == "__main__":
    asyncio.run(main())
