"""Transition analysis examples.

Demonstrates possession classification (transition vs half-court) from
play-by-play data, including frequency breakdowns and points-per-possession
efficiency splits.

Run:
    uv run python examples/transition.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import get_game_ids, get_play_by_play
from fastbreak.models.play_by_play import PlayByPlayAction
from fastbreak.transition import (
    TransitionAnalysis,
    classify_possessions,
    get_transition_stats,
    transition_efficiency,
    transition_frequency,
)


def print_analysis(analysis: TransitionAnalysis) -> None:
    """Print a full transition breakdown for one game."""
    s = analysis.summary
    e = analysis.efficiency

    print(f"\nTransition Analysis  game_id={analysis.game_id}")
    print("=" * 55)

    print(f"  Total possessions:      {s.total_possessions}")
    print(f"  Transition possessions:  {s.transition_possessions}")
    print(f"  Half-court possessions:  {s.halfcourt_possessions}")

    if s.transition_pct is not None:
        print(f"  Transition %:            {s.transition_pct:.1%}")
        print(f"  Half-court %:            {s.halfcourt_pct:.1%}")

    print()
    if e.transition_ppp is not None:
        print(f"  Transition PPP:          {e.transition_ppp:.2f}")
    else:
        print("  Transition PPP:          N/A (no transition possessions)")

    if e.halfcourt_ppp is not None:
        print(f"  Half-court PPP:          {e.halfcourt_ppp:.2f}")
    else:
        print("  Half-court PPP:          N/A (no half-court possessions)")

    print(f"  Transition points:       {e.transition_points}")
    print(f"  Half-court points:       {e.halfcourt_points}")


def step_by_step_analysis(actions: list[PlayByPlayAction], game_id: str) -> None:
    """Show how to use the pure functions individually."""
    # Classify possessions with the default 8-second window
    possessions = classify_possessions(actions, transition_window=8.0)
    summary = transition_frequency(possessions)

    print(f"\nStep-by-Step Analysis  game_id={game_id}")
    print("=" * 55)
    print(f"  Actions in game:  {len(actions)}")
    print(f"  Possessions:      {len(possessions)}")

    if summary.transition_pct is not None:
        print(f"  Transition rate:  {summary.transition_pct:.1%}")

    # Show the first few transition possessions
    trans = [p for p in possessions if p.classification == "transition"]
    print(f"\n  First 5 transition possessions:")
    for p in trans[:5]:
        print(
            f"    Q{p.period} {p.game_clock:5.1f}s remaining  "
            f"elapsed={p.elapsed:.1f}s  trigger={p.trigger:<20s}  "
            f"pts={p.points_scored}"
        )


def compare_windows(actions: list[PlayByPlayAction], game_id: str) -> None:
    """Compare classification at different transition windows."""
    print(f"\nWindow Comparison  game_id={game_id}")
    print("=" * 55)
    print(
        f"  {'Window':>8} {'Trans':>6} {'HC':>6} {'Trans%':>8} {'Trans PPP':>10} {'HC PPP':>10}"
    )
    print("  " + "-" * 52)

    for window in [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
        poss = classify_possessions(actions, transition_window=window)
        s = transition_frequency(poss)
        e = transition_efficiency(poss)

        t_pct = f"{s.transition_pct:.1%}" if s.transition_pct is not None else "N/A"
        t_ppp = f"{e.transition_ppp:.2f}" if e.transition_ppp is not None else "N/A"
        h_ppp = f"{e.halfcourt_ppp:.2f}" if e.halfcourt_ppp is not None else "N/A"

        print(
            f"  {window:>6.1f}s {s.transition_possessions:>6} "
            f"{s.halfcourt_possessions:>6} {t_pct:>8} {t_ppp:>10} {h_ppp:>10}"
        )


async def multi_game_transition_rate(
    client: NBAClient,
    season: str = "2025-26",
    team_id: int = 1610612744,
    n_games: int = 5,
) -> None:
    """Compute transition rates across several games for a team."""
    game_ids = await get_game_ids(client, season, team_id=team_id)
    if not game_ids:
        print(f"No games found for team {team_id} in {season}")
        return

    # Limit to the first N regular-season games
    game_ids = [g for g in game_ids if g[:3] == "002"][:n_games]

    print(f"\nMulti-Game Transition Rates  (team_id={team_id}, {season})")
    print("=" * 65)
    print(
        f"  {'Game ID':<12} {'Total':>6} {'Trans':>6} {'HC':>6} {'Trans%':>8} {'Trans PPP':>10}"
    )
    print("  " + "-" * 52)

    for gid in game_ids:
        analysis = await get_transition_stats(client, gid)
        s = analysis.summary
        e = analysis.efficiency
        t_pct = f"{s.transition_pct:.1%}" if s.transition_pct is not None else "N/A"
        t_ppp = f"{e.transition_ppp:.2f}" if e.transition_ppp is not None else "N/A"
        print(
            f"  {gid:<12} {s.total_possessions:>6} "
            f"{s.transition_possessions:>6} {s.halfcourt_possessions:>6} "
            f"{t_pct:>8} {t_ppp:>10}"
        )


async def main() -> None:
    # Use a known game ID (regular season 2025-26)
    game_id = "0022500571"

    async with NBAClient() as client:
        # Fetch PBP once and reuse for all single-game examples.
        # get_transition_stats(client, game_id) is the one-liner
        # alternative when you don't need the raw actions.
        actions = await get_play_by_play(client, game_id)

    poss = classify_possessions(actions)
    analysis = TransitionAnalysis(
        game_id=game_id,
        possessions=tuple(poss),
        summary=transition_frequency(poss),
        efficiency=transition_efficiency(poss),
    )

    print_analysis(analysis)
    step_by_step_analysis(actions, game_id)
    compare_windows(actions, game_id)
    # Uncomment to run multi-game analysis (makes several API calls):
    # async with NBAClient() as client:
    #     await multi_game_transition_rate(client)


if __name__ == "__main__":
    asyncio.run(main())
