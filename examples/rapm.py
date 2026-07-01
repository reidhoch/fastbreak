"""Estimate RAPM from a small set of hand-built stints.

Run: uv run python examples/rapm.py
"""

from fastbreak.rapm import Stint, compute_rapm, rapm_leaders


def main() -> None:
    # Toy stints: player 10 consistently on winning lineups, player 20 on losing.
    stints = [
        Stint(
            home_player_ids=(10, 1, 2, 3, 4),
            away_player_ids=(20, 5, 6, 7, 8),
            possessions=20.0,
            point_diff=8,
        ),
        Stint(
            home_player_ids=(10, 5, 6, 7, 8),
            away_player_ids=(20, 1, 2, 3, 4),
            possessions=18.0,
            point_diff=6,
        ),
        Stint(
            home_player_ids=(20, 1, 2, 3, 4),
            away_player_ids=(10, 5, 6, 7, 8),
            possessions=22.0,
            point_diff=-7,
        ),
        Stint(
            home_player_ids=(1, 2, 3, 4, 5),
            away_player_ids=(6, 7, 8, 9, 11),
            possessions=15.0,
            point_diff=1,
        ),
    ]

    result = compute_rapm(stints, lambda_=50.0)
    print(
        f"Solved RAPM over {result.n_stints} stints, {result.n_players} players (alpha={result.alpha})."
    )
    print("\nTop 5 by RAPM (net pts / 100 poss):")
    for r in rapm_leaders(result, top_n=5):
        print(
            f"  player {r.player_id:>3}: {r.rapm:+6.2f}  ({r.possessions:.0f} poss, {r.stint_count} stints)"
        )


if __name__ == "__main__":
    main()
