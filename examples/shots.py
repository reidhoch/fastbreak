"""Shot chart analysis examples.

Demonstrates per-shot coordinate data, zone efficiency breakdowns,
delta vs. league-average shooting by zone, and expected FG% (xFG%).

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
    shot_quality_vs_league,
    xfg_pct,
    zone_breakdown,
    zone_fg_pct,
)


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
    making_delta = (actual - expected) if actual is not None and expected is not None else None

    print(f"\nShot Zone Breakdown — {player_name} ({season})")
    print(f"Total shots: {len(shots)}")
    if expected is not None and actual is not None:
        print(f"Overall FG%: {actual:.1%}  |  xFG%: {expected:.1%}  |  "
              f"Shot-making: {making_delta:+.1%}")
        print("  (xFG% = expected FG% from shot locations; positive shot-making = above average)")
    print("-" * 62)
    print(f"{'Zone':<28} {'FGM':>4} {'FGA':>4} {'FG%':>6}  {'vs Lg':>7}")
    print("-" * 62)

    for zone, stats in sorted(breakdown.items(), key=lambda x: -x[1].fga):
        fg_pct_str = f"{stats.fg_pct:.1%}" if stats.fg_pct is not None else "N/A"
        delta = deltas.get(zone)
        delta_str = f"{delta:+.1%}" if delta is not None else "  N/A"
        print(f"{zone:<28} {stats.fgm:>4} {stats.fga:>4} {fg_pct_str:>6}  {delta_str:>7}")


async def compare_shot_zones(
    player_names: list[str], season: str | None = None
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
    zone_volumes: dict[str, int] = {}
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
            val = f"{stats.fg_pct:.1%}" if stats and stats.fg_pct is not None else " ---"
            print(f"  {val:>10}", end="")
        lg_avg = zone_lookup.get(zone)
        lg_str = f"{lg_avg:.1%}" if lg_avg is not None else "  N/A"
        print(f"  {lg_str:>7}")


async def main() -> None:
    season = "2025-26"

    # Single player breakdown
    await player_shot_zones("Pascal Siakam", season)

    # Multi-player comparison
    await compare_shot_zones(["LeBron James", "Kevin Durant", "Nikola Jokić"], season)


if __name__ == "__main__":
    asyncio.run(main())
