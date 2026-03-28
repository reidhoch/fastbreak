"""Example: Searching for games and analyzing results with fastbreak.game_finder.

Covers:
  - find_team_games     — search team games with filters
  - find_player_games   — search player games with stat thresholds
  - aggregate_games     — average stats across a set of games
  - streak_games        — find consecutive win/loss streaks
  - summarize_record    — compute W-L record

Run:
    uv run python examples/game_finder.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.game_finder import (
    aggregate_games,
    find_player_games,
    find_team_games,
    streak_games,
    summarize_record,
)


async def team_analysis(client: NBAClient) -> None:
    """Demonstrate team game search, record, averages, and streaks."""
    print("=" * 64)
    print("Team Analysis  (find_team_games)")
    print("=" * 64)

    team_id = 1610612754  # Pacers
    games = await find_team_games(
        client, team_id=team_id, season="2025-26", season_type="Regular Season"
    )
    if not games:
        print("  No games found for this team/season.")
        return

    # Record
    record = summarize_record(games)
    print(f"\n  Pacers 2025-26: {record.wins}-{record.losses} ({record.win_pct:.3f})")

    # Averages
    avgs = aggregate_games(games)
    print(f"  PPG: {avgs.pts:.1f}  RPG: {avgs.reb:.1f}  APG: {avgs.ast:.1f}")
    if avgs.fg_pct is not None:
        print(f"  FG%: {avgs.fg_pct:.3f}  3P%: {avgs.fg3_pct or 0:.3f}  FT%: {avgs.ft_pct or 0:.3f}")

    # Streaks
    streaks = streak_games(games)
    if streaks:
        longest = max(streaks, key=len)
        current = streaks[-1]
        print(f"  Current streak: {current[0].wl} {len(current)}")
        print(f"  Longest streak: {longest[0].wl} {len(longest)}")

    # Home vs road split (Location filter is non-functional on leaguegamefinder,
    # so filter client-side via the matchup string: "vs." = home, "@" = road)
    home = [g for g in games if g.matchup and "vs." in g.matchup]
    road = [g for g in games if g.matchup and "@" in g.matchup]
    home_rec = summarize_record(home)
    road_rec = summarize_record(road)
    print(f"  Home: {home_rec.wins}-{home_rec.losses}  Road: {road_rec.wins}-{road_rec.losses}")


async def player_analysis(client: NBAClient) -> None:
    """Demonstrate player game search with stat thresholds."""
    print("\n" + "=" * 64)
    print("Player Analysis  (find_player_games)")
    print("=" * 64)

    # Find Nembhard's 5+ assist games
    player_id = 1630174  # Andrew Nembhard
    big_games = await find_player_games(
        client, player_id=player_id, season="2025-26", gt_ast=5
    )
    print(f"\n  Nembhard 5+ assist games: {len(big_games)}")
    for g in big_games[:5]:
        print(f"    {g.game_date}  {g.matchup or ''}  {g.pts}pts  {g.reb}reb  {g.ast}ast  {g.wl or '?'}")

    if big_games:
        avgs = aggregate_games(big_games)
        print(f"  Avg in 5+ ast games: {avgs.pts:.1f}pts  {avgs.reb:.1f}reb  {avgs.ast:.1f}ast")

    # Record in those games
    if big_games:
        rec = summarize_record(big_games)
        print(f"  Record when Nembhard has 5+ ast: {rec.wins}-{rec.losses} ({rec.win_pct:.3f})")


async def main() -> None:
    async with NBAClient() as client:
        await team_analysis(client)
        await player_analysis(client)


if __name__ == "__main__":
    asyncio.run(main())
