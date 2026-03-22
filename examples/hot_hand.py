"""Hot hand analysis examples.

Demonstrates single-game hot hand detection with Miller-Sanjurjo bias
correction, season-level analysis across multiple games, and step-by-step
usage of the pure computation functions.

Run:
    uv run python examples/hot_hand.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import get_game_ids, get_play_by_play
from fastbreak.hot_hand import (
    HotHandResult,
    extract_shot_sequences,
    get_hot_hand_stats,
    hot_hand_result,
    merge_sequences,
)


def print_result_table(results: list[HotHandResult], title: str) -> None:
    """Print a formatted table of hot hand results."""
    scorable = [r for r in results if r.score is not None]
    scorable.sort(key=lambda r: (r.score or 0.0), reverse=True)

    if not scorable:
        print(f"\n{title}")
        print("  No players with enough streak opportunities to score.")
        return

    print(f"\n{title}")
    print(
        f"  {'Player':<22} {'FGA':>4} {'Base%':>6} "
        f"{'Naive':>6} {'Corr':>6} {'Delta':>7} {'Score':>7}"
    )
    print("  " + "-" * 62)
    for r in scorable:
        # score is not None implies baseline_p, naive_p, corrected_p, delta are not None
        assert r.baseline_p is not None and r.naive_p is not None
        assert r.corrected_p is not None and r.delta is not None and r.score is not None
        print(
            f"  {r.player_name:<22} {r.n:>4} {r.baseline_p:>6.1%} "
            f"{r.naive_p:>6.1%} {r.corrected_p:>6.1%} "
            f"{r.delta:>+7.3f} {r.score:>+7.1f}"
        )


async def single_game_analysis(game_id: str = "0022500571") -> None:
    """Analyze hot hand effects for all players in a single game."""
    async with NBAClient() as client:
        analysis = await get_hot_hand_stats(client, game_id)

    print(f"Game {analysis.game_id}: {len(analysis.sequences)} players shot FGs")
    print_result_table(list(analysis.results), "Hot Hand Results (sorted by score)")


async def step_by_step_analysis(game_id: str = "0022500571") -> None:
    """Show how to use the pure functions individually after fetching PBP."""
    async with NBAClient() as client:
        actions = await get_play_by_play(client, game_id)

    sequences = extract_shot_sequences(actions)

    print(f"\nStep-by-Step Analysis  game_id={game_id}")
    print("=" * 55)
    print(f"  Actions in game:     {len(actions)}")
    print(f"  Players with FGAs:   {len(sequences)}")

    # Show shot sequences for first 5 players
    print("\n  Shot sequences (first 5 players):")
    for seq in sequences[:5]:
        streak = "".join("M" if s else "x" for s in seq.shots)
        print(f"    {seq.player_name:<22} {streak}")

    # Compute results manually
    results = [
        hot_hand_result(seq.player_id, seq.player_name, seq.shots) for seq in sequences
    ]
    print_result_table(results, "Results from manual computation")


async def season_analysis(
    season: str = "2025-26",
    team_id: int = 1610612744,
    n_games: int = 5,
) -> None:
    """Merge shot sequences across multiple games for season-level analysis."""
    async with NBAClient() as client:
        game_ids = await get_game_ids(client, season, team_id=team_id)
        if not game_ids:
            print(f"No games found for team {team_id} in {season}")
            return

        # First N regular-season games
        game_ids = [g for g in game_ids if g[:3] == "002"][:n_games]

        game_seqs = []
        for gid in game_ids:
            actions = await get_play_by_play(client, gid)
            game_seqs.append(extract_shot_sequences(actions))

    merged = merge_sequences(game_seqs)

    print(f"\nSeason Hot Hand — {len(game_ids)} games (team_id={team_id})")
    print("=" * 55)

    results = [
        hot_hand_result(seq.player_id, seq.player_name, seq.shots) for seq in merged
    ]
    print_result_table(results, f"Season-Level Hot Hand ({n_games} games merged)")


async def compare_streak_lengths(game_id: str = "0022500571") -> None:
    """Compare results at different streak lengths (k values)."""
    async with NBAClient() as client:
        actions = await get_play_by_play(client, game_id)

    sequences = extract_shot_sequences(actions)

    print(f"\nStreak Length Comparison  game_id={game_id}")
    print("=" * 55)
    print(f"  {'k':>2} {'Players w/ score':>17} {'Avg delta':>10} {'Max score':>10}")
    print("  " + "-" * 42)

    for k in [1, 2, 3, 4, 5]:
        results = [
            hot_hand_result(seq.player_id, seq.player_name, seq.shots, k=k)
            for seq in sequences
        ]
        scorable = [r for r in results if r.score is not None and r.delta is not None]
        if scorable:
            avg_delta = sum(r.delta for r in scorable if r.delta is not None) / len(scorable)
            max_score = max(r.score for r in scorable if r.score is not None)
            print(
                f"  {k:>2} {len(scorable):>17} {avg_delta:>+10.3f} {max_score:>+10.1f}"
            )
        else:
            print(f"  {k:>2} {'0':>17} {'N/A':>10} {'N/A':>10}")


async def main() -> None:
    game_id = "0022500571"

    # Single-game analysis using the async wrapper
    await single_game_analysis(game_id)

    # Step-by-step pure function usage
    await step_by_step_analysis(game_id)

    # Compare different streak lengths
    await compare_streak_lengths(game_id)

    # Uncomment to run season-level analysis (makes several API calls):
    # await season_analysis()


if __name__ == "__main__":
    asyncio.run(main())
