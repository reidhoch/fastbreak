"""Player and team tracking data examples.

Demonstrates shot breakdowns, pass flow, rebounding splits, shot defense,
and concurrent profile fetching via PlayerTrackingProfile / TeamTrackingProfile.

Run:
    uv run python examples/tracking.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.players import get_player_id
from fastbreak.seasons import get_season_from_date
from fastbreak.teams import get_team_id
from fastbreak.tracking import (
    get_player_shot_defense,
    get_player_tracking_profile,
    get_team_tracking_profile,
)


async def player_shot_profile(player_name: str, season: str | None = None) -> None:
    """Print shot efficiency breakdowns by type, shot clock, and defender distance."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        profile = await get_player_tracking_profile(
            client, player_id=player_id, season=season
        )

    shots = profile.shots

    print(f"\nShot Profile — {player_name} ({season})")

    print("\n  General shooting (catch & shoot / pull-up / <10 ft):")
    print(f"  {'Type':<28} {'FGA':>5} {'FG%':>6}  {'eFG%':>6}")
    print("  " + "-" * 50)
    for row in sorted(shots.general_shooting, key=lambda r: -r.fga):
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        efg_str = f"{row.efg_pct:.1%}" if row.efg_pct is not None else "  N/A"
        print(f"  {row.shot_type:<28} {row.fga:>5.1f} {fg_str:>6}  {efg_str:>6}")

    print("\n  By shot clock range:")
    print(f"  {'Range':<22} {'FGA':>5} {'FG%':>6}")
    print("  " + "-" * 36)
    for clk in shots.shot_clock_shooting:
        fg_str = f"{clk.fg_pct:.1%}" if clk.fg_pct is not None else "  N/A"
        print(f"  {clk.shot_clock_range:<22} {clk.fga:>5.1f} {fg_str:>6}")

    print("\n  By closest defender distance:")
    print(f"  {'Distance':<22} {'FGA':>5} {'FG%':>6}")
    print("  " + "-" * 36)
    for def_row in shots.closest_defender_shooting:
        fg_str = f"{def_row.fg_pct:.1%}" if def_row.fg_pct is not None else "  N/A"
        print(f"  {def_row.close_def_dist_range:<22} {def_row.fga:>5.1f} {fg_str:>6}")


async def player_defense_profile(player_name: str, season: str | None = None) -> None:
    """Print shot defense: opponent FG% vs. normal FG% by category."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        defense = await get_player_shot_defense(
            client, player_id=player_id, season=season
        )

    if not defense.defending_shots:
        print(f"{player_name} has no shot defense data for {season}.")
        return

    print(f"\nShot Defense — {player_name} ({season})")
    print(f"  {'Category':<22} {'D FG%':>6}  {'Normal':>6}  {'Δ':>7}  Impact")
    print("  " + "-" * 58)
    for row in defense.defending_shots:
        if (
            row.d_fg_pct is None
            or row.normal_fg_pct is None
            or row.pct_plusminus is None
        ):
            continue
        impact = "✓ deters" if row.pct_plusminus < 0 else "✗ yields"
        print(
            f"  {row.defense_category:<22} {row.d_fg_pct:.1%}  "
            f"{row.normal_fg_pct:.1%}  {row.pct_plusminus:>+.3f}  {impact}"
        )


async def player_passing_profile(player_name: str, season: str | None = None) -> None:
    """Print top pass targets and pass sources."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        profile = await get_player_tracking_profile(
            client, player_id=player_id, season=season
        )

    passes = profile.passes

    print(f"\nPassing Profile — {player_name} ({season})")

    top_targets = sorted(passes.passes_made, key=lambda r: -r.ast)[:6]
    if top_targets:
        print("\n  Top assist targets (by assists generated):")
        print(f"  {'Teammate':<24} {'AST/g':>6}  {'FG%':>6}  {'Pass/g':>7}")
        print("  " + "-" * 48)
        for row in top_targets:
            fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
            print(
                f"  {row.pass_to:<24} {row.ast:>6.2f}  {fg_str:>6}  {row.passes:>7.1f}"
            )

    top_sources = sorted(passes.passes_received, key=lambda r: -r.ast)[:5]
    if top_sources:
        print("\n  Top pass sources (passes received leading to FGM):")
        print(f"  {'Teammate':<24} {'AST/g':>6}  {'FG%':>6}")
        print("  " + "-" * 40)
        for src in top_sources:
            fg_str = f"{src.fg_pct:.1%}" if src.fg_pct is not None else "  N/A"
            print(f"  {src.pass_from:<24} {src.ast:>6.2f}  {fg_str:>6}")


async def team_tracking_summary(team_name: str, season: str | None = None) -> None:
    """Print team shot efficiency and top passers."""
    season = season or get_season_from_date()

    team_id = get_team_id(team_name)
    if team_id is None:
        print(f"Team not found: {team_name!r}")
        return

    async with NBAClient() as client:
        profile = await get_team_tracking_profile(
            client, team_id=team_id, season=season
        )

    print(f"\nTeam Tracking Summary — {team_name} ({season})")

    print("\n  Shot clock shooting:")
    print(f"  {'Range':<22} {'FG%':>6}")
    print("  " + "-" * 30)
    for row in profile.shots.shot_clock_shooting:
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        print(f"  {row.shot_clock_range:<22} {fg_str:>6}")

    top_passers = sorted(profile.passes.passes_made, key=lambda r: -r.ast)[:6]
    if top_passers:
        print("\n  Top ball-movers (by assists generated):")
        print(f"  {'Player':<24} {'AST/g':>6}  {'Pass/g':>7}")
        print("  " + "-" * 42)
        for passer in top_passers:
            print(f"  {passer.pass_from:<24} {passer.ast:>6.2f}  {passer.passes:>7.1f}")

    overall = profile.rebounds.overall
    if overall is not None:
        print(
            f"\n  Rebounding:  {overall.reb:.1f} total  |  "
            f"{overall.c_reb:.1f} contested ({overall.c_reb_pct:.1%})  |  "
            f"{overall.uc_reb:.1f} uncontested ({overall.uc_reb_pct:.1%})"
        )


async def main() -> None:
    season = "2025-26"

    # Player shot and passing profile
    await player_shot_profile("Victor Wembanyama", season)
    await player_passing_profile("LeBron James", season)

    # Shot defense — who deters opponents?
    await player_defense_profile("Rudy Gobert", season)

    # Team summary
    await team_tracking_summary("Celtics", season)


if __name__ == "__main__":
    asyncio.run(main())
