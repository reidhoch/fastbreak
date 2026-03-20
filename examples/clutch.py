"""Clutch performance analysis examples.

Demonstrates league-wide clutch leaders (player and team), a per-player clutch
profile, and single-team clutch stats using the standard NBA clutch definition:
last 5 minutes, score within 5.

Run:
    uv run python examples/clutch.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.clutch import (
    get_league_clutch_leaders,
    get_league_team_clutch_leaders,
    get_player_clutch_profile,
    get_team_clutch_stats,
)
from fastbreak.players import get_player_id
from fastbreak.teams import get_team_id

_MIN_CLUTCH_MINUTES = 5.0  # minimum total clutch minutes for a meaningful sample


async def league_clutch_leaders(season: str = "2025-26") -> None:
    """Print top-10 clutch performers league-wide, sorted by plus/minus."""
    async with NBAClient() as client:
        leaders = await get_league_clutch_leaders(
            client,
            season=season,
            min_minutes=_MIN_CLUTCH_MINUTES,
            top_n=10,
        )

    if not leaders:
        print("No qualified clutch performers found.")
        return

    print(f"\nTop Clutch Performers — {season} Regular Season")
    print(f"(min {_MIN_CLUTCH_MINUTES:.0f} clutch minutes, last 5 min ≤5 pts)")
    print("-" * 55)
    print(f"{'#':<3} {'Player':<25} {'Team':<5} {'Min':>5} {'±':>6}")
    print("-" * 55)
    for rank, row in enumerate(leaders, 1):
        pm_str = f"{row.plus_minus:+.1f}"
        print(
            f"{rank:<3} {row.player_name:<25} {row.team_abbreviation:<5} {row.min:>5.1f} {pm_str:>6}",
        )


async def player_clutch_profile(player_name: str, season: str = "2025-26") -> None:
    """Print a detailed clutch profile for a single player."""
    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        profile = await get_player_clutch_profile(
            client,
            player_id=player_id,
            name=player_name,
            season=season,
            min_threshold=_MIN_CLUTCH_MINUTES,
        )

    if profile is None:
        print(f"{player_name} has no clutch minutes recorded this season.")
        return

    def fmt(val: float | None, fmt_spec: str = ".3f") -> str:
        return f"{val:{fmt_spec}}" if val is not None else "N/A"

    def fmt_delta(val: float | None) -> str:
        return f"{val:+.3f}" if val is not None else "N/A"

    print(f"\nClutch Profile — {profile.name or player_name} ({season})")
    print("-" * 45)
    print(f"  Clutch minutes:   {profile.clutch_min:.1f}")
    print(f"  Clutch +/-:       {profile.clutch_plus_minus:+.1f}")
    print()
    print(f"  TS%  (regular):   {fmt(profile.regular_ts)}")
    print(f"  TS%  (clutch):    {fmt(profile.clutch_ts)}")
    print(f"  TS%  delta:       {fmt_delta(profile.ts_delta)}")
    print()
    print(f"  A/TO (regular):   {fmt(profile.regular_ato)}")
    print(f"  A/TO (clutch):    {fmt(profile.clutch_ato)}")
    print(f"  A/TO delta:       {fmt_delta(profile.ato_delta)}")
    print()
    if profile.score is not None:
        label = "clutch performer" if profile.score > 0 else "struggles in clutch"
        print(f"  Composite score:  {profile.score:+.2f}  ({label})")
    else:
        print(f"  Composite score:  N/A (< {_MIN_CLUTCH_MINUTES:.0f} clutch minutes)")


async def team_clutch_leaders(season: str = "2025-26") -> None:
    """Print the top 10 teams in clutch situations, sorted by plus/minus."""
    async with NBAClient() as client:
        leaders = await get_league_team_clutch_leaders(
            client,
            season=season,
            top_n=10,
        )

    if not leaders:
        print("No team clutch data found.")
        return

    print(f"\nTop Team Clutch Performers — {season} Regular Season")
    print("(last 5 min ≤5 pts)")
    print("-" * 60)
    print(f"{'#':<3} {'Team':<28} {'W-L':>6} {'PTS':>5} {'±':>7}")
    print("-" * 60)
    for rank, row in enumerate(leaders, 1):
        pm_str = f"{row.plus_minus:+.1f}"
        print(
            f"{rank:<3} {row.team_name:<28} "
            f"{row.w}-{row.losses:>2} {row.pts:>5.1f} {pm_str:>7}",
        )


async def single_team_clutch(team_name: str, season: str = "2025-26") -> None:
    """Print clutch stats for a single team."""
    team_id = get_team_id(team_name)
    if team_id is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        stats = await get_team_clutch_stats(
            client,
            int(team_id),
            season=season,
        )

    if stats is None:
        print(f"No clutch data for {team_name}.")
        return

    print(f"\nClutch Stats — {stats.team_name} ({season})")
    print("-" * 40)
    print(f"  Record:     {stats.w}-{stats.losses} ({stats.w_pct:.3f})")
    print(f"  Points:     {stats.pts:.1f}")
    fg_str = f"{stats.fg_pct:.1%}" if stats.fga > 0 else "N/A"
    fg3_str = f"{stats.fg3_pct:.1%}" if stats.fg3a > 0 else "N/A"
    print(f"  FG%:        {fg_str}")
    print(f"  3P%:        {fg3_str}")
    print(f"  +/-:        {stats.plus_minus:+.1f}")
    print(f"  AST:        {stats.ast:.1f}")
    print(f"  TOV:        {stats.tov:.1f}")


async def main() -> None:
    season = "2025-26"

    # Player clutch leaders and profiles
    await league_clutch_leaders(season)
    for name in ["LeBron James", "Victor Wembanyama", "Nikola Jokić"]:
        await player_clutch_profile(name, season)

    # Team clutch leaders and single-team deep dive
    await team_clutch_leaders(season)
    await single_team_clutch("Celtics", season)


if __name__ == "__main__":
    asyncio.run(main())
