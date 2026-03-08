"""Defensive analysis examples.

Demonstrates zone defense quality, opponent shooting stats, and per-player
shot defense. All three analyses available from fastbreak.defense.

Note: true per-shot x/y defensive coordinates are unavailable from the NBA
Stats API. This module provides zone-based aggregate data instead.

Run:
    uv run python examples/defense.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.defense import (
    defensive_shot_quality_vs_league,
    get_player_shot_defense,
    get_team_defense_zones,
    get_team_opponent_stats,
)
from fastbreak.seasons import get_season_from_date
from fastbreak.teams import get_team_id


async def team_zone_defense(team_name: str, season: str | None = None) -> None:
    """Print a team's defensive quality vs league average."""
    season = season or get_season_from_date()
    team_id = get_team_id(team_name)
    if team_id is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        zones = await get_team_defense_zones(client, season=season)

    deltas = defensive_shot_quality_vs_league(zones, team_id=team_id)
    if not deltas:
        print(f"No zone defense data for team_id={team_id}")
        return

    print(f"\nZone Defense Quality — {team_name} ({season})")
    print("  (negative = better than average; opponents shoot below normal FG%)")
    print("-" * 45)
    for abbr, delta in deltas.items():
        if delta is not None:
            marker = "<-- better" if delta < 0 else ""
            print(f"  {abbr}: {delta:+.3f}  {marker}")


async def league_opponent_shooting(season: str | None = None, top_n: int = 5) -> None:
    """Print the best and worst defensive teams by opponent FG%."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        teams = await get_team_opponent_stats(client, season=season)

    sorted_teams = sorted(teams, key=lambda t: t.fg_pct)
    print(f"\nLeague Opponent FG% — {season}")
    print(f"{'Rank':<5} {'Team':<6} {'Opp FG%':>8} {'Opp eFG%':>9} {'FG3A Freq':>10}")
    print("-" * 42)
    for i, team in enumerate(sorted_teams[:top_n], 1):
        print(
            f"  {i:<3} {team.team_abbreviation:<6} "
            f"{team.fg_pct:>8.1%} {team.efg_pct:>9.1%} "
            f"{team.fg3a_frequency:>9.1%}"
        )
    print("  ...")
    print(f"  (worst {top_n})")
    for i, team in enumerate(sorted_teams[-top_n:], len(sorted_teams) - top_n + 1):
        print(
            f"  {i:<3} {team.team_abbreviation:<6} "
            f"{team.fg_pct:>8.1%} {team.efg_pct:>9.1%} "
            f"{team.fg3a_frequency:>9.1%}"
        )


async def player_shot_defense_profile(
    player_id: int, player_name: str, season: str | None = None
) -> None:
    """Print a player's shot defense breakdown (opponent FG% when defended)."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        response = await get_player_shot_defense(
            client, player_id=player_id, season=season
        )

    shots = response.defending_shots
    if not shots:
        print(f"{player_name} has no shot defense data for {season}.")
        return

    print(f"\nShot Defense — {player_name} ({season})")
    print(
        f"{'Shot Type':<28} {'Opp FGA':>8} {'Opp FG%':>8} {'Normal FG%':>11} {'Delta':>7}"
    )
    print("-" * 66)
    for row in shots:
        delta = (
            row.d_fg_pct - row.normal_fg_pct
            if row.d_fg_pct is not None and row.normal_fg_pct is not None
            else None
        )
        delta_str = f"{delta:+.1%}" if delta is not None else "  N/A"
        fg_str = f"{row.d_fg_pct:.1%}" if row.d_fg_pct is not None else " N/A"
        norm_str = (
            f"{row.normal_fg_pct:.1%}" if row.normal_fg_pct is not None else " N/A"
        )
        fga_val = int(row.d_fga) if row.d_fga is not None else 0
        print(
            f"{row.defense_category:<28} {fga_val:>8} {fg_str:>8} {norm_str:>11} {delta_str:>7}"
        )


async def main() -> None:
    season = "2025-26"

    # Team zone defense quality
    await team_zone_defense("Celtics", season)

    # League-wide opponent shooting — best defenders
    await league_opponent_shooting(season, top_n=5)

    # Dyson Daniels per-shot defense breakdown (elite defender 2025-26)
    await player_shot_defense_profile(
        player_id=1630700, player_name="Dyson Daniels", season=season
    )


if __name__ == "__main__":
    asyncio.run(main())
