"""Example: Odds and bankroll math with fastbreak.betting.

Every part is pure computation — no network access required.

Part 1 — odds format conversions: American ↔ decimal ↔ implied probability.
Part 2 — removing the vig: turn a posted two-way market into fair probabilities.
Part 3 — bet sizing: expected value and (fractional) Kelly stakes.
Part 4 — closing-line value: did your price beat the close?
Part 5 — spreads ↔ win probabilities (Normal margin model).
Part 6 — log5: head-to-head win probability from two season win rates.
"""

from fastbreak.betting import (
    american_to_decimal,
    american_to_prob,
    bet_ev,
    closing_line_value,
    decimal_to_american,
    decimal_to_prob,
    kelly_fraction,
    log5,
    remove_vig,
    spread_to_win_prob,
    win_prob_to_spread,
)

# ---------------------------------------------------------------------------
# Part 1: odds format conversions
# ---------------------------------------------------------------------------


def demo_odds_conversions() -> None:
    """Round-trip a few moneylines through decimal and implied-probability form."""
    print("=" * 60)
    print("Part 1 — Odds conversions: American ↔ decimal ↔ probability")
    print("=" * 60)
    print(
        "  American odds are the sportsbook's native format; decimal odds\n"
        "  are the payout multiplier (stake included); implied probability\n"
        "  is 1 / decimal — what the price says your win chance must exceed.\n"
    )

    moneylines = [-300, -150, -110, 100, 130, 250]

    print(f"  {'American':>9}  {'Decimal':>8}  {'Implied P':>9}  {'Round-trip':>11}")
    print("  " + "-" * 44)
    for american in moneylines:
        decimal = american_to_decimal(american)
        prob = american_to_prob(american)
        # Round-trip back to American to show the conversions are inverses.
        back = decimal_to_american(decimal)
        back_str = f"{back:+d}"
        print(f"  {american:>+9d}  {decimal:>8.3f}  {prob:>9.3f}  {back_str:>11}")

    print()
    print("  Notes:")
    print("    -110 (a standard 'juiced' line) implies 52.4% — the 2.4% over")
    print("    50% is the book's cut on a coin-flip market.")
    print("    +100 (even money) is decimal 2.0 and implies exactly 50%.")
    print(
        f"    decimal_to_prob(2.50) = {decimal_to_prob(2.50):.3f}  "
        "(direct decimal → probability)"
    )
    print()


# ---------------------------------------------------------------------------
# Part 2: removing the vig
# ---------------------------------------------------------------------------


def demo_remove_vig() -> None:
    """Strip the bookmaker margin from a posted two-way moneyline market."""
    print("=" * 60)
    print("Part 2 — Removing the vig: posted prices → fair probabilities")
    print("=" * 60)
    print(
        "  A book's two implied probabilities sum to MORE than 1.0 — the\n"
        "  excess (the 'overround') is the vig. remove_vig normalizes them\n"
        "  back to a fair distribution that sums to exactly 1.0.\n"
    )

    # A typical NBA moneyline: favorite -150, underdog +130.
    fav_american, dog_american = -150, 130
    fav_implied = american_to_prob(fav_american)
    dog_implied = american_to_prob(dog_american)
    overround = fav_implied + dog_implied

    fair = remove_vig([fav_implied, dog_implied])

    print(f"  Market: favorite {fav_american:+d} / underdog {dog_american:+d}")
    print()
    print(f"  {'Side':<11}  {'Implied':>8}  {'Fair':>7}")
    print("  " + "-" * 30)
    print(f"  {'Favorite':<11}  {fav_implied:>8.3f}  {fair[0]:>7.3f}")
    print(f"  {'Underdog':<11}  {dog_implied:>8.3f}  {fair[1]:>7.3f}")
    print("  " + "-" * 30)
    print(f"  {'Sum':<11}  {overround:>8.3f}  {sum(fair):>7.3f}")
    print()
    print(f"  Overround (book's edge): {(overround - 1.0) * 100:.1f}%")
    print(
        "  The fair probabilities are your no-vig baseline — compare your\n"
        "  model against these, not the raw posted prices.\n"
    )


# ---------------------------------------------------------------------------
# Part 3: expected value and Kelly sizing
# ---------------------------------------------------------------------------


def demo_ev_and_kelly() -> None:
    """Compute EV and Kelly stakes for several model-vs-market edges."""
    print("=" * 60)
    print("Part 3 — Bet sizing: expected value and (fractional) Kelly")
    print("=" * 60)
    print(
        "  bet_ev is profit per unit staked (0 = fair, >0 = +EV).\n"
        "  kelly_fraction is the bankroll share that maximizes long-run\n"
        "  log-growth. Negative-edge bets clamp to 0.0 (never bet against\n"
        "  yourself); quarter-Kelly (fraction=0.25) tames variance.\n"
    )

    # Each scenario: a price (decimal odds) and YOUR model's win probability.
    scenarios = [
        ("Model edge", 1.91, 0.58),  # -110 price, model says 58%
        ("Fair bet", 2.00, 0.50),  # even money, no edge
        ("Underdog value", 2.60, 0.45),  # +160 dog you make 45%
        ("Negative edge", 1.91, 0.48),  # -110 price, model says only 48%
    ]

    print(
        f"  {'Scenario':<16}  {'Decimal':>7}  {'Model P':>7}"
        f"  {'EV/unit':>8}  {'Full K':>7}  {'¼ K':>6}"
    )
    print("  " + "-" * 60)
    for label, decimal, win_prob in scenarios:
        ev = bet_ev(win_prob=win_prob, decimal_odds=decimal)
        full_k = kelly_fraction(win_prob=win_prob, decimal_odds=decimal)
        quarter_k = kelly_fraction(
            win_prob=win_prob, decimal_odds=decimal, fraction=0.25
        )
        print(
            f"  {label:<16}  {decimal:>7.2f}  {win_prob:>7.2f}"
            f"  {ev:>+8.3f}  {full_k:>7.3f}  {quarter_k:>6.3f}"
        )

    print()
    print(
        "  The negative-edge row shows EV < 0 and a Kelly stake of 0.000 —\n"
        "  the clamp refuses to size a bet the model doesn't favor.\n"
    )


# ---------------------------------------------------------------------------
# Part 4: closing-line value
# ---------------------------------------------------------------------------


def demo_closing_line_value() -> None:
    """Measure how your entry price compares to the closing line."""
    print("=" * 60)
    print("Part 4 — Closing-line value (CLV)")
    print("=" * 60)
    print(
        "  CLV = bet_decimal / closing_decimal - 1. Beating the close\n"
        "  (positive CLV) is the single best leading indicator that your\n"
        "  process is +EV, even before results come in.\n"
    )

    # Each row: the decimal price you took vs. where the line closed.
    bets = [
        ("Beat the close", 2.10, 2.00),  # bet +110, closed +100
        ("Matched close", 1.95, 1.95),
        ("Beaten by close", 1.85, 1.95),  # you took a worse price than the close
    ]

    print(f"  {'Outcome':<17}  {'Your odds':>9}  {'Close':>7}  {'CLV':>8}")
    print("  " + "-" * 46)
    for label, bet_decimal, closing_decimal in bets:
        clv = closing_line_value(
            bet_decimal=bet_decimal, closing_decimal=closing_decimal
        )
        print(
            f"  {label:<17}  {bet_decimal:>9.2f}  {closing_decimal:>7.2f}  {clv:>+8.3f}"
        )

    print()
    print(
        "  Consistently positive CLV over a large sample is what separates\n"
        "  sustainable edges from variance.\n"
    )


# ---------------------------------------------------------------------------
# Part 5: spreads ↔ win probabilities
# ---------------------------------------------------------------------------


def demo_spread_win_prob() -> None:
    """Translate point spreads to win probabilities and back."""
    print("=" * 60)
    print("Part 5 — Spreads ↔ win probabilities")
    print("=" * 60)
    print(
        "  spread_to_win_prob models the final margin as Normal(-spread, sigma)\n"
        "  and returns P(margin > 0). sigma defaults to 12.0 — roughly the\n"
        "  standard deviation of NBA game margins. Spread is from the\n"
        "  team's perspective: negative = favored.\n"
    )

    spreads = [-12.0, -6.0, -3.0, 0.0, 3.0, 6.0]

    print(f"  {'Spread':>7}  {'Win P':>7}  {'Recovered spread':>17}")
    print("  " + "-" * 36)
    for spread in spreads:
        win_prob = spread_to_win_prob(spread)
        # Invert (skip the degenerate 50/50 pick'em, which maps to exactly 0).
        recovered = win_prob_to_spread(win_prob)
        print(f"  {spread:>+7.1f}  {win_prob:>7.3f}  {recovered:>+17.2f}")

    print()
    print("  sigma sensitivity for a 6-point favorite (-6.0):")
    for sigma in (10.0, 12.0, 14.0):
        wp = spread_to_win_prob(-6.0, sigma=sigma)
        print(f"    sigma={sigma:>4.1f}:  win P = {wp:.3f}")
    print(
        "\n  Higher sigma (more game-to-game variance) pulls win probabilities\n"
        "  toward 50% — a big favorite is less 'safe' in a high-variance world.\n"
    )


# ---------------------------------------------------------------------------
# Part 6: log5 head-to-head
# ---------------------------------------------------------------------------


def demo_log5() -> None:
    """Estimate head-to-head win probability from two season win rates."""
    print("=" * 60)
    print("Part 6 — log5: head-to-head from season win rates")
    print("=" * 60)
    print(
        "  Bill James's log5 estimates P(A beats B) from each team's win\n"
        "  rate vs. a league of average opponents. A .732 team (60-22) vs.\n"
        "  a .500 team should win more than its raw rate suggests.\n"
    )

    # (label, team A win pct, team B win pct)
    matchups = [
        ("Contender vs avg", 0.732, 0.500),
        ("Contender vs tank", 0.732, 0.280),
        ("Even matchup", 0.550, 0.550),
        ("Avg vs contender", 0.500, 0.732),
    ]

    print(f"  {'Matchup':<18}  {'P(A)':>5}  {'P(B)':>5}  {'P(A beats B)':>13}")
    print("  " + "-" * 48)
    for label, p_a, p_b in matchups:
        p = log5(p_a, p_b)
        print(f"  {label:<18}  {p_a:>5.3f}  {p_b:>5.3f}  {p:>13.3f}")

    print()
    print(
        "  Note: log5 ignores home court, rest, and injuries — it's a pure\n"
        "  strength-vs-strength prior. Blend it with situational adjustments\n"
        "  (see fastbreak.schedule) before betting a specific game.\n"
    )


def main() -> None:
    demo_odds_conversions()
    demo_remove_vig()
    demo_ev_and_kelly()
    demo_closing_line_value()
    demo_spread_win_prob()
    demo_log5()


if __name__ == "__main__":
    main()
