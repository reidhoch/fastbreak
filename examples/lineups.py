"""Lineup analysis examples.

Demonstrates lineup statistics, efficiency ratings, two-man combos,
and top lineups using fastbreak.lineups.

Run:
    uv run python examples/lineups.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.lineups import (
    get_league_lineup_ratings,
    get_lineup_efficiency,
    get_top_lineups,
    get_two_man_combos,
    lineup_net_rating,
    rank_lineups,
)
from fastbreak.seasons import get_season_from_date
from fastbreak.teams import get_team_id


async def top_team_lineups(team_name: str, season: str | None = None) -> None:
    """Print the top 10 five-man lineups for a team by plus/minus."""
    season = season or get_season_from_date()
    team_id = get_team_id(team_name)
    if team_id is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        top = await get_top_lineups(
            client,
            team_id,
            top_n=10,
            min_minutes=5.0,
            by="plus_minus",
            season=season,
        )

    if not top:
        print(f"No lineup data for {team_name} ({season})")
        return

    print(f"\n{team_name} — Top 10 Five-Man Lineups by +/- ({season})")
    print(f"{'Lineup':<45} {'GP':>4} {'Min':>6} {'+/-':>6}")
    print("-" * 66)
    for lu in top:
        name = lu.group_name[:43]
        print(f"  {name:<43} {lu.gp:>4} {lu.min:>6.1f} {lu.plus_minus:>+6.1f}")


async def team_lineup_efficiency(team_name: str, season: str | None = None) -> None:
    """Print a team's lineups sorted by net rating."""
    season = season or get_season_from_date()
    team_id = get_team_id(team_name)
    if team_id is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        best = await get_lineup_efficiency(
            client, team_id=team_id, top_n=5, season=season
        )

    if not best:
        print(f"No lineup efficiency data for {team_name} ({season})")
        return

    print(f"\n{team_name} — Top 5 Lineups by Net Rating ({season})")
    print(f"{'Lineup':<45} {'Off':>6} {'Def':>6} {'Net':>6} {'Pace':>6}")
    print("-" * 74)
    for lu in best:
        name = lu.group_name[:43]
        print(
            f"  {name:<43} {lu.off_rating:>6.1f} "
            f"{lu.def_rating:>6.1f} {lu.net_rating:>+6.1f} {lu.pace:>6.1f}"
        )


async def two_man_combos(team_name: str, season: str | None = None) -> None:
    """Print the top two-man combos for a team by plus/minus."""
    season = season or get_season_from_date()
    team_id = get_team_id(team_name)
    if team_id is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        combos = await get_two_man_combos(client, team_id=team_id, season=season)

    ranked = rank_lineups(combos, min_minutes=5.0, by="plus_minus")
    if not ranked:
        print(f"No two-man combo data for {team_name} ({season})")
        return

    print(f"\n{team_name} — Top 10 Two-Man Combos by +/- ({season})")
    print(f"{'Combo':<35} {'GP':>4} {'Min':>6} {'FG%':>6} {'+/-':>6}")
    print("-" * 62)
    for lu in ranked[:10]:
        name = lu.group_name[:33]
        fg_str = f"{lu.fg_pct:.1%}" if lu.fg_pct is not None else " N/A"
        print(
            f"  {name:<33} {lu.gp:>4} {lu.min:>6.1f} {fg_str:>6} {lu.plus_minus:>+6.1f}"
        )


async def league_efficiency_leaders(season: str | None = None) -> None:
    """Print the best and worst lineups league-wide by net rating."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        lineups = await get_league_lineup_ratings(client, minutes_min=50, season=season)

    if not lineups:
        print(f"No lineup efficiency data ({season})")
        return

    by_net = sorted(lineups, key=lambda lu: lu.net_rating, reverse=True)

    print(f"\nLeague Efficiency Leaders (50+ min, {season})")
    print(f"{'Lineup':<40} {'Team':>4} {'Off':>6} {'Def':>6} {'Net':>6}")
    print("-" * 67)

    print("  Best:")
    for lu in by_net[:5]:
        name = lu.group_name[:38]
        net = lineup_net_rating(lu.off_rating, lu.def_rating)
        print(
            f"    {name:<38} {lu.team_abbreviation:>4} "
            f"{lu.off_rating:>6.1f} {lu.def_rating:>6.1f} {net:>+6.1f}"
        )

    print("  Worst:")
    for lu in by_net[-5:]:
        name = lu.group_name[:38]
        net = lineup_net_rating(lu.off_rating, lu.def_rating)
        print(
            f"    {name:<38} {lu.team_abbreviation:>4} "
            f"{lu.off_rating:>6.1f} {lu.def_rating:>6.1f} {net:>+6.1f}"
        )


async def main() -> None:
    season = "2025-26"

    # 1. Top Lakers five-man lineups by +/-
    await top_team_lineups("Lakers", season)

    # 2. Lakers lineup efficiency ratings
    await team_lineup_efficiency("Lakers", season)

    # 3. Lakers two-man combos
    await two_man_combos("Lakers", season)

    # 4. League-wide best/worst lineups by net rating
    await league_efficiency_leaders(season)


if __name__ == "__main__":
    asyncio.run(main())
