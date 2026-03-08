"""Player situational splits examples.

Demonstrates home/road and win/loss splits, recent form (last-N rolling averages),
game-context splits by half and score margin, shot-area breakdowns, and concurrent
profile fetching via PlayerSplitsProfile.

Run:
    uv run python examples/splits.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.players import get_player_id
from fastbreak.seasons import get_season_from_date
from fastbreak.splits import (
    get_player_general_splits,
    get_player_last_n_games,
    get_player_shooting_splits,
    get_player_splits_profile,
    stat_delta,
)


async def player_situational_splits(
    player_name: str, season: str | None = None
) -> None:
    """Print home/road and win/loss splits: FG%, PTS, and +/- comparisons."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        splits = await get_player_general_splits(
            client, player_id=player_id, season=season
        )

    print(f"\nSituational Splits — {player_name} ({season})")

    # Home vs Road
    home = next((s for s in splits.by_location if s.group_value == "Home"), None)
    road = next((s for s in splits.by_location if s.group_value == "Road"), None)
    if home and road:
        fg_delta = stat_delta(home.fg_pct, road.fg_pct)
        pts_delta = stat_delta(home.pts, road.pts)
        pm_delta = stat_delta(home.plus_minus, road.plus_minus)
        print("\n  Home vs Road:")
        print(f"  {'Split':<8} {'GP':>4} {'FG%':>6} {'PTS':>6} {'±':>6}")
        print("  " + "-" * 35)
        for label, row in [("Home", home), ("Road", road)]:
            fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
            print(
                f"  {label:<8} {row.gp:>4} {fg_str:>6} {row.pts:>6.1f} {row.plus_minus:>+6.1f}"
            )
        fg_delta_str = f"{fg_delta:+.3f}" if fg_delta is not None else "  N/A"
        pts_delta_str = f"{pts_delta:>+6.1f}" if pts_delta is not None else "   N/A"
        pm_delta_str = f"{pm_delta:>+6.1f}" if pm_delta is not None else "   N/A"
        print(
            f"  {'Delta':<8} {'':>4} {fg_delta_str:>6}  {pts_delta_str}  {pm_delta_str}"
        )

    # Wins vs Losses
    wins = next((s for s in splits.by_wins_losses if "W" in str(s.group_value)), None)
    losses = next((s for s in splits.by_wins_losses if "L" in str(s.group_value)), None)
    if wins and losses:
        fg_delta = stat_delta(wins.fg_pct, losses.fg_pct)
        print("\n  Wins vs Losses:")
        print(f"  {'Split':<8} {'GP':>4} {'FG%':>6} {'PTS':>6} {'±':>6}")
        print("  " + "-" * 35)
        for label, row in [("Wins", wins), ("Losses", losses)]:
            fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
            print(
                f"  {label:<8} {row.gp:>4} {fg_str:>6} {row.pts:>6.1f} {row.plus_minus:>+6.1f}"
            )
        if fg_delta is not None:
            print(f"\n  FG% in wins vs losses: {fg_delta:+.3f}")

    # Starter vs Bench
    print("\n  Starter vs Bench:")
    for row in splits.by_starting_position:
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        print(
            f"  {row.group_value!s:<10} {row.gp:>3} GP  {fg_str} FG%  {row.pts:.1f} PTS"
        )


async def player_recent_form(player_name: str, season: str | None = None) -> None:
    """Print rolling-window stats to show whether a player is hot or cold."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        last_n = await get_player_last_n_games(
            client, player_id=player_id, season=season
        )

    windows = [
        ("Season", last_n.overall),
        ("L20", last_n.last_20),
        ("L15", last_n.last_15),
        ("L10", last_n.last_10),
        ("L5", last_n.last_5),
    ]

    print(f"\nRecent Form — {player_name} ({season})")
    print(f"  {'Window':<8} {'GP':>4} {'PTS':>6} {'FG%':>6} {'AST':>5} {'REB':>5}")
    print("  " + "-" * 38)
    for label, row in windows:
        if row is None:
            print(f"  {label:<8}  N/A")
            continue
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        print(
            f"  {label:<8} {row.gp:>4} {row.pts:>6.1f} {fg_str:>6} {row.ast:>5.1f} {row.reb:>5.1f}"
        )

    # Trend: compare L5 to season baseline
    if last_n.overall and last_n.last_5:
        pts_trend = stat_delta(last_n.last_5.pts, last_n.overall.pts)
        fg_trend = stat_delta(last_n.last_5.fg_pct, last_n.overall.fg_pct)
        if pts_trend is None and fg_trend is None:
            return
        direction = (
            "↑ heating up"
            if pts_trend is not None and pts_trend > 0
            else "↓ cooling off"
        )
        pts_trend_str = (
            f"{pts_trend:+.1f} PTS" if pts_trend is not None else "   N/A PTS"
        )
        fg_trend_str = f"{fg_trend:+.3f} FG%" if fg_trend is not None else "   N/A FG%"
        print(f"\n  L5 vs season: {pts_trend_str}  {fg_trend_str}  {direction}")


async def player_shooting_breakdown(
    player_name: str, season: str | None = None
) -> None:
    """Print FG% by court area: restricted area, paint, mid-range, 3PT."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        shooting = await get_player_shooting_splits(
            client, player_id=player_id, season=season
        )

    print(f"\nShooting by Court Area — {player_name} ({season})")
    print(f"  {'Area':<30} {'FGM':>4} {'FGA':>4} {'FG%':>6}  {'eFG%':>6}")
    print("  " + "-" * 55)
    for row in shooting.by_shot_area:
        print(
            f"  {row.group_value:<30} {row.fgm:>4} {row.fga:>4} "
            f"{row.fg_pct:.1%}  {row.efg_pct:.1%}"
        )

    if shooting.by_assisted:
        print(f"\n  {'Type':<30} {'FG%':>6}  {'% Assisted':>10}")
        print("  " + "-" * 50)
        for row in shooting.by_assisted:
            print(f"  {row.group_value:<30} {row.fg_pct:.1%}  {row.pct_ast_fgm:>9.1%}")


async def player_full_profile(player_name: str, season: str | None = None) -> None:
    """Fetch all five split endpoints in one concurrent round-trip."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        player_id = await get_player_id(client, player_name)
        if player_id is None:
            print(f"Player not found: {player_name!r}")
            return

        # Single get_many() call fetches all 5 endpoints concurrently
        profile = await get_player_splits_profile(
            client, player_id=player_id, season=season
        )

    print(f"\nFull Splits Profile — {player_name} ({season})")

    # Score margin context: how does the player perform when team is behind?
    print("\n  By score margin (game splits):")
    for row in profile.game_splits.by_score_margin:
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        print(
            f"  {row.group_value!s:<20} {row.gp:>3} GP  {fg_str} FG%  {row.pts:.1f} PTS"
        )

    # Team performance context
    print("\n  By team score differential:")
    for row in profile.team_performance.by_score_differential:
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        label = f"{row.group_value} ({row.group_value_2})"
        print(f"  {label:<28} {fg_str} FG%  {row.pts:.1f} PTS")

    # Days rest summary
    print("\n  By days of rest (general splits):")
    for row in profile.general_splits.by_days_rest:
        fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "  N/A"
        print(f"  {row.group_value!s:<22} {row.gp:>3} GP  {fg_str}")


async def main() -> None:
    season = "2025-26"

    # Individual split views
    await player_situational_splits("Victor Wembanyama", season)
    await player_recent_form("LeBron James", season)
    await player_shooting_breakdown("Stephen Curry", season)

    # Full concurrent profile
    await player_full_profile("Nikola Jokić", season)


if __name__ == "__main__":
    asyncio.run(main())
