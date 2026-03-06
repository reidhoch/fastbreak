"""Clutch performance analysis examples.

Demonstrates league-wide clutch leaders and a per-player clutch profile
using the standard NBA clutch definition: last 5 minutes, score within 5.

Run:
    uv run python examples/clutch.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.clutch import get_league_clutch_leaders, get_player_clutch_profile
from fastbreak.players import get_player_id

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
        print(f"{rank:<3} {row.player_name:<25} {row.team_abbreviation:<5} {row.min:>5.1f} {pm_str:>6}")


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


async def main() -> None:
    season = "2025-26"

    await league_clutch_leaders(season)

    # Profile a handful of notable players
    # Note: player names must match exactly as stored in the NBA API,
    # including diacritics (e.g. "Nikola Jokić", not "Nikola Jokic")
    for name in ["LeBron James", "Victor Wembanyama", "Nikola Jokić"]:
        await player_clutch_profile(name, season)


if __name__ == "__main__":
    asyncio.run(main())
