"""Shot chart analysis examples.

Demonstrates per-shot coordinate data, zone efficiency breakdowns,
delta vs. league-average shooting by zone, expected FG% (xFG%),
and team shot locations by distance range.

Run:
    uv run python examples/shots.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.players import get_player_id
from fastbreak.seasons import get_season_from_date
from fastbreak.shots import (
    get_league_shot_zones,
    get_shot_chart,
    get_team_shot_locations,
    shot_quality_vs_league,
    team_distance_breakdown,
    xfg_pct,
    zone_breakdown,
    zone_fg_pct,
)
from fastbreak.teams import get_team_id


async def player_shot_zones(player_name: str, season: str | None = None) -> None:
    """Print zone-by-zone FG%, delta vs. league average, and xFG% for a player."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        response = await get_shot_chart(client, player_id=player_id, season=season)
        lg_zones = await get_league_shot_zones(client, season=season)

    shots = response.shots
    if not shots:
        print(f"{player_name} has no shot data for {season}.")
        return

    breakdown = zone_breakdown(shots)
    deltas = shot_quality_vs_league(shots, lg_zones, player_zones=breakdown)

    # xFG%: expected FG% given shot selection — "what would a league-average
    # player shoot from the same locations?"
    expected = xfg_pct(shots, lg_zones, player_zones=breakdown)
    actual = zone_fg_pct(shots)
    making_delta = (
        (actual - expected) if actual is not None and expected is not None else None
    )

    print(f"\nShot Zone Breakdown — {player_name} ({season})")
    print(f"Total shots: {len(shots)}")
    if expected is not None and actual is not None:
        print(
            f"Overall FG%: {actual:.1%}  |  xFG%: {expected:.1%}  |  "
            f"Shot-making: {making_delta:+.1%}",
        )
        print(
            "  (xFG% = expected FG% from shot locations; positive shot-making = above average)",
        )
    print("-" * 62)
    print(f"{'Zone':<28} {'FGM':>4} {'FGA':>4} {'FG%':>6}  {'vs Lg':>7}")
    print("-" * 62)

    for zone, stats in sorted(breakdown.items(), key=lambda x: -x[1].fga):
        fg_pct_str = f"{stats.fg_pct:.1%}" if stats.fg_pct is not None else "N/A"
        delta = deltas.get(zone)
        delta_str = f"{delta:+.1%}" if delta is not None else "  N/A"
        print(
            f"{zone:<28} {stats.fgm:>4.0f} {stats.fga:>4.0f} {fg_pct_str:>6}  {delta_str:>7}",
        )


async def compare_shot_zones(
    player_names: list[str],
    season: str | None = None,
) -> None:
    """Compare zone FG% for multiple players side by side."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_ids: dict[str, int] = {}
        for name in player_names:
            pid = await get_player_id(client, name)
            if pid is None:
                print(f"Player not found: {name!r}")
                continue
            player_ids[name] = pid

        if not player_ids:
            return

        responses = {}
        for name, pid in player_ids.items():
            responses[name] = await get_shot_chart(client, player_id=pid, season=season)
        lg_zones = await get_league_shot_zones(client, season=season)

    lg_totals: dict[str, tuple[int, int]] = {}
    for z in lg_zones:
        fga, fgm = lg_totals.get(z.shot_zone_basic, (0, 0))
        lg_totals[z.shot_zone_basic] = (fga + z.fga, fgm + z.fgm)
    zone_lookup = {zone: fgm / fga for zone, (fga, fgm) in lg_totals.items() if fga > 0}

    # Collect all zones present across any player, sorted by combined volume
    names = list(player_ids.keys())
    all_breakdowns = {name: zone_breakdown(responses[name].shots) for name in names}
    zone_volumes: dict[str, float] = {}
    for bd in all_breakdowns.values():
        for zone, zstats in bd.items():
            zone_volumes[zone] = zone_volumes.get(zone, 0) + zstats.fga
    all_zones = sorted(zone_volumes, key=lambda z: -zone_volumes[z])

    # Print header
    print(f"\nZone FG% Comparison — {season}")
    print(f"{'Zone':<28}", end="")
    for name in names:
        short = name.split()[-1][:10]  # Last name, max 10 chars
        print(f"  {short:>10}", end="")
    print(f"  {'Lg Avg':>7}")
    print("-" * (28 + len(names) * 12 + 9))

    for zone in all_zones:
        print(f"{zone:<28}", end="")
        for name in names:
            stats = all_breakdowns[name].get(zone)
            val = (
                f"{stats.fg_pct:.1%}" if stats and stats.fg_pct is not None else " ---"
            )
            print(f"  {val:>10}", end="")
        lg_avg = zone_lookup.get(zone)
        lg_str = f"{lg_avg:.1%}" if lg_avg is not None else "  N/A"
        print(f"  {lg_str:>7}")


async def team_shot_distances(team_name: str, season: str | None = None) -> None:
    """Print shot FG% by distance range for a single team."""
    season = season or get_season_from_date()
    team_id_val = get_team_id(team_name)
    if team_id_val is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        locations = await get_team_shot_locations(
            client,
            team_id=int(team_id_val),
            season=season,
        )

    if not locations:
        print(f"No shot location data for {team_name}.")
        return

    breakdown = team_distance_breakdown(locations[0])

    print(f"\nShot Locations by Distance — {locations[0].team_name} ({season})")
    print("-" * 48)
    print(f"{'Distance':<20} {'FGM':>5} {'FGA':>5} {'FG%':>7}")
    print("-" * 48)
    for label, stats in breakdown.items():
        fg_str = f"{stats.fg_pct:.1%}" if stats.fg_pct is not None else "  N/A"
        print(f"{label:<20} {stats.fgm:>5.1f} {stats.fga:>5.1f} {fg_str:>7}")


async def compare_team_distances(season: str | None = None) -> None:
    """Compare shot distance profiles across all 30 teams (top 5 by close-range %)."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        all_teams = await get_team_shot_locations(client, season=season)

    if not all_teams:
        print("No team shot data found.")
        return

    # Rank teams by FG% at the rim (Less Than 5ft)
    rim_data = []
    for team in all_teams:
        bd = team_distance_breakdown(team)
        rim = bd.get("Less Than 5ft")
        if rim and rim.fg_pct is not None:
            rim_data.append((team.team_name, rim.fg_pct, rim.fga))

    rim_data.sort(key=lambda x: x[1], reverse=True)

    print(f"\nTop 5 Teams by Rim FG% (Less Than 5ft) — {season}")
    print("-" * 45)
    print(f"{'#':<3} {'Team':<25} {'FG%':>6} {'FGA':>5}")
    print("-" * 45)
    for rank, (name, pct, fga) in enumerate(rim_data[:5], 1):
        print(f"{rank:<3} {name:<25} {pct:.1%} {fga:>5.0f}")


async def main() -> None:
    season = "2025-26"

    # Player shot zone analysis
    await player_shot_zones("Pascal Siakam", season)
    await compare_shot_zones(["LeBron James", "Kevin Durant", "Nikola Jokić"], season)

    # Team shot distance breakdown
    await team_shot_distances("Thunder", season)
    await compare_team_distances(season)


if __name__ == "__main__":
    asyncio.run(main())
