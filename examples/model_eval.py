"""Example: Scoring probabilistic forecasts with fastbreak.model_eval.

Every part is pure computation — no network access required.

Part 1 — proper scoring rules: Brier score and log loss for three forecasters.
Part 2 — calibration curve: are predicted probabilities reliable in aggregate?
Part 3 — realized ROI: turning a sequence of staked bets into a return figure.
Part 4 — end-to-end: score a model's win probabilities, then its betting ROI.
"""

from fastbreak.betting import bet_ev, kelly_fraction
from fastbreak.model_eval import (
    brier_score,
    calibration_curve,
    log_loss,
    roi,
)

# ---------------------------------------------------------------------------
# Part 1: proper scoring rules
# ---------------------------------------------------------------------------


def demo_scoring_rules() -> None:
    """Compare Brier score and log loss across three contrasting forecasters."""
    print("=" * 60)
    print("Part 1 — Proper scoring rules: Brier score & log loss")
    print("=" * 60)
    print(
        "  Both reward confident, correct probabilities and punish confident,\n"
        "  wrong ones. Lower is better for each. Log loss is harsher on\n"
        "  confidently-wrong calls (it clips p to avoid an infinite penalty).\n"
    )

    # Shared ground truth: 8 events, half occurred (1) and half did not (0).
    outcomes = [1, 0, 1, 1, 0, 1, 0, 0]

    forecasters = {
        "Sharp (confident+right)": [0.8, 0.2, 0.9, 0.7, 0.1, 0.85, 0.25, 0.15],
        "Coin flip (all 0.5)": [0.5] * len(outcomes),
        "Overconfident & wrong": [0.2, 0.8, 0.1, 0.3, 0.9, 0.15, 0.75, 0.85],
    }

    print(f"  {'Forecaster':<26}  {'Brier':>7}  {'Log loss':>9}")
    print("  " + "-" * 46)
    for name, probs in forecasters.items():
        bs = brier_score(probs, outcomes)
        ll = log_loss(probs, outcomes)
        print(f"  {name:<26}  {bs:>7.3f}  {ll:>9.3f}")

    print()
    print("  Benchmarks:")
    print("    A constant-0.5 forecaster always scores Brier = 0.250.")
    print("    The sharp forecaster beats it; the overconfident-wrong one")
    print("    is punished hardest by log loss for backing the wrong side.")
    print()


# ---------------------------------------------------------------------------
# Part 2: calibration curve
# ---------------------------------------------------------------------------


def demo_calibration() -> None:
    """Bucket predictions into reliability bins and compare pred vs. observed."""
    print("=" * 60)
    print("Part 2 — Calibration curve (reliability)")
    print("=" * 60)
    print(
        "  A well-calibrated model's predicted probability matches the\n"
        "  observed hit rate within each bin: when it says 70%, the event\n"
        "  should happen ~70% of the time. Empty bins are omitted.\n"
    )

    # 20 predictions paired with outcomes. The model is roughly calibrated:
    # high-probability picks hit more often than low-probability ones.
    probs = [
        0.05,
        0.12,
        0.18,
        0.22,
        0.28,
        0.35,
        0.42,
        0.48,
        0.55,
        0.58,
        0.62,
        0.68,
        0.72,
        0.78,
        0.82,
        0.85,
        0.88,
        0.91,
        0.94,
        0.97,
    ]
    outcomes = [
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
    ]

    bins = calibration_curve(probs, outcomes, n_bins=5)

    print(f"  {'Bin':>11}  {'N':>3}  {'Mean pred':>9}  {'Observed':>8}  {'Gap':>7}")
    print("  " + "-" * 48)
    for b in bins:
        gap = b.mean_pred - b.mean_outcome
        print(
            f"  [{b.lower:.2f},{b.upper:.2f})  {b.count:>3}"
            f"  {b.mean_pred:>9.3f}  {b.mean_outcome:>8.3f}  {gap:>+7.3f}"
        )

    total = sum(b.count for b in bins)
    print("  " + "-" * 48)
    print(f"  {len(bins)} populated bin(s), {total} predictions total")
    print()
    print(
        "  A positive gap means the model is over-confident in that band\n"
        "  (predicted higher than reality); negative means under-confident.\n"
    )


# ---------------------------------------------------------------------------
# Part 3: realized ROI
# ---------------------------------------------------------------------------


def demo_roi() -> None:
    """Compute realized return across a few staking scenarios."""
    print("=" * 60)
    print("Part 3 — Realized ROI")
    print("=" * 60)
    print(
        "  roi = sum(profits) / sum(stakes). Profits are net: positive for a\n"
        "  win, negative (the stake lost) for a loss. ROI is a per-unit-risked\n"
        "  return, independent of how many bets were placed.\n"
    )

    # Each scenario: equal 1-unit stakes, with the net profit of each bet.
    # A winning -110 bet nets +0.91; a loss nets -1.00.
    scenarios = {
        "Winning season": ([1.0] * 5, [0.91, -1.0, 0.91, 0.91, -1.0]),
        "Break-even-ish": ([1.0] * 4, [0.91, -1.0, 0.91, -1.0]),
        "Losing season": ([1.0] * 5, [-1.0, 0.91, -1.0, -1.0, 0.91]),
    }

    print(f"  {'Scenario':<18}  {'Bets':>4}  {'Staked':>7}  {'Profit':>7}  {'ROI':>8}")
    print("  " + "-" * 52)
    for name, (stakes, profits) in scenarios.items():
        r = roi(stakes=stakes, profits=profits)
        print(
            f"  {name:<18}  {len(stakes):>4}  {sum(stakes):>7.1f}"
            f"  {sum(profits):>+7.2f}  {r:>+8.1%}"
        )

    print()
    print(
        "  At standard -110 juice you need to win ~52.4% just to break even,\n"
        "  so a 3-2 record (the 'winning season' row) is already profitable.\n"
    )


# ---------------------------------------------------------------------------
# Part 4: end-to-end — score a model, then evaluate its betting record
# ---------------------------------------------------------------------------


def demo_end_to_end() -> None:
    """Tie betting + model_eval together: probabilities → bets → scored results."""
    print("=" * 60)
    print("Part 4 — End-to-end: forecast quality → betting outcome")
    print("=" * 60)
    print(
        "  A model emits win probabilities. We bet (quarter-Kelly) only the\n"
        "  +EV games at the offered price, watch them resolve, then score\n"
        "  both the forecasts (Brier/log loss) and the realized ROI.\n"
    )

    # (model win prob, offered decimal odds, actual outcome 1=win/0=loss)
    games = [
        (0.62, 1.91, 1),  # +EV favorite, hit
        (0.55, 2.10, 0),  # +EV dog price, missed
        (0.48, 1.91, 0),  # NOT +EV — skipped
        (0.70, 1.80, 1),  # +EV favorite, hit
        (0.58, 2.00, 1),  # +EV, hit
        (0.45, 2.50, 0),  # +EV dog, missed
    ]

    probs = [g[0] for g in games]
    outcomes = [g[2] for g in games]

    stakes: list[float] = []
    profits: list[float] = []
    bankroll_unit = 100.0  # express Kelly fraction as a dollar stake

    print(
        f"  {'P(win)':>6}  {'Odds':>5}  {'EV':>7}  {'Stake':>7}  {'Result':>7}  {'P/L':>8}"
    )
    print("  " + "-" * 52)
    for win_prob, decimal, outcome in games:
        ev = bet_ev(win_prob=win_prob, decimal_odds=decimal)
        kelly = kelly_fraction(win_prob=win_prob, decimal_odds=decimal, fraction=0.25)
        stake = kelly * bankroll_unit

        if stake <= 0.0:
            print(
                f"  {win_prob:>6.2f}  {decimal:>5.2f}  {ev:>+7.3f}"
                f"  {'—':>7}  {'skip':>7}  {'—':>8}"
            )
            continue

        # Net profit: win pays (decimal - 1) * stake; loss forfeits the stake.
        pl = stake * (decimal - 1.0) if outcome == 1 else -stake
        stakes.append(stake)
        profits.append(pl)
        result = "win" if outcome == 1 else "loss"
        print(
            f"  {win_prob:>6.2f}  {decimal:>5.2f}  {ev:>+7.3f}"
            f"  {stake:>7.2f}  {result:>7}  {pl:>+8.2f}"
        )

    print()
    print("  Forecast quality (all games, including skipped bets):")
    print(f"    Brier score: {brier_score(probs, outcomes):.3f}")
    print(f"    Log loss:    {log_loss(probs, outcomes):.3f}")
    print()
    print("  Betting outcome (only the games we actually bet):")
    print(f"    Bets placed:  {len(stakes)}")
    print(f"    Total staked: {sum(stakes):.2f}")
    print(f"    Net profit:   {sum(profits):+.2f}")
    print(f"    ROI:          {roi(stakes=stakes, profits=profits):+.1%}")
    print()
    print(
        "  Forecast quality and ROI can diverge over a small sample — a\n"
        "  well-calibrated model still loses some +EV bets to variance.\n"
        "  Track CLV (see examples/betting.py) for a faster signal.\n"
    )


def main() -> None:
    demo_scoring_rules()
    demo_calibration()
    demo_roi()
    demo_end_to_end()


if __name__ == "__main__":
    main()
