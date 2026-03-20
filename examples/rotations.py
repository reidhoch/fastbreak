"""Rotation analysis examples.

Demonstrates player stint analysis, minutes aggregation, lineup reconstruction,
and substitution timeline from game rotation data.

Run:
    uv run python examples/rotations.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.rotations import (
    get_game_rotations,
    get_rotation_summary,
    lineup_stints,
    player_stints,
    player_total_minutes,
    rotation_timeline,
    stint_plus_minus,
)


async def main() -> None:
    game_id = "0022500571"
    team_id = 1610612754  # Indiana Pacers

    async with NBAClient() as client:
        # 1. Fetch rotations
        response = await get_game_rotations(client, game_id=game_id)
        print(f"Rotation Data  game_id={game_id}")
        print("=" * 55)
        print(f"  Home team entries: {len(response.home_team)}")
        print(f"  Away team entries: {len(response.away_team)}")

        # 2. Per-player minutes (sorted by total)
        entries = response.home_team
        minutes = player_total_minutes(entries)
        print(f"\nPer-Player Minutes (home team, sorted by total)")
        print("-" * 55)
        print(f"  {'Player':<25} {'Minutes':>8} {'Stints':>7} {'Avg':>6} {'Pts':>5} {'+/-':>6}")
        for m in minutes:
            print(
                f"  {m.player_name:<25} {m.total_minutes:>8.1f} {m.stint_count:>7} "
                f"{m.avg_stint_minutes:>6.1f} {m.total_points:>5} {m.total_pt_diff:>+6.0f}"
            )

        # 3. Stint plus/minus leaders
        pm = stint_plus_minus(entries)
        stints = player_stints(entries)
        name_map = {s.player_id: s.player_name for s in stints}
        sorted_pm = sorted(pm.items(), key=lambda x: x[1], reverse=True)
        print(f"\nPlus/Minus Leaders")
        print("-" * 35)
        for pid, diff in sorted_pm[:5]:
            print(f"  {name_map.get(pid, str(pid)):<25} {diff:>+6.1f}")

        # 4. Top 5 lineup stints by duration
        lineups = lineup_stints(entries)
        top_lineups = sorted(lineups, key=lambda l: l.duration_minutes, reverse=True)[:5]
        print(f"\nTop 5 Lineups by Duration")
        print("-" * 65)
        for ls in top_lineups:
            names = ", ".join(ls.player_names)
            print(f"  {ls.duration_minutes:>5.1f} min  {names}")

        # 5. Substitution timeline
        timeline = rotation_timeline(entries)
        print(f"\nSubstitution Timeline (first 10 events)")
        print("-" * 65)
        for ev in timeline[:10]:
            in_name = ev.player_in_name or "---"
            out_name = ev.player_out_name or "---"
            print(
                f"  Q{ev.period} {ev.time:>7.1f}s  IN: {in_name:<20} OUT: {out_name:<20}"
            )

        # 6. Full summary via convenience wrapper
        summary = await get_rotation_summary(client, game_id, team_id=team_id)
        print(f"\nRotation Summary")
        print("-" * 40)
        print(f"  Game: {summary.game_id}")
        print(f"  Team: {summary.team_id}")
        print(f"  Total game minutes: {summary.total_game_minutes:.1f}")
        print(f"  Player stints: {len(summary.player_stints)}")
        print(f"  Unique lineups: {len(summary.lineup_stints)}")
        print(f"  Substitution events: {len(summary.substitution_events)}")


if __name__ == "__main__":
    asyncio.run(main())
