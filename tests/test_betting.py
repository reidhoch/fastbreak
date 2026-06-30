"""Tests for fastbreak.betting — odds, bankroll, and win-prob math."""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------- american_to_decimal ----------


class TestAmericanToDecimal:
    def test_positive_odds(self) -> None:
        from fastbreak.betting import american_to_decimal

        assert american_to_decimal(150) == pytest.approx(2.5)

    def test_negative_odds(self) -> None:
        from fastbreak.betting import american_to_decimal

        assert american_to_decimal(-200) == pytest.approx(1.5)

    def test_even_money_both_signs(self) -> None:
        from fastbreak.betting import american_to_decimal

        assert american_to_decimal(100) == pytest.approx(2.0)
        assert american_to_decimal(-100) == pytest.approx(2.0)

    def test_rejects_sub_100_magnitude(self) -> None:
        from fastbreak.betting import american_to_decimal

        with pytest.raises(ValueError, match="American odds"):
            american_to_decimal(50)

    def test_rejects_zero(self) -> None:
        from fastbreak.betting import american_to_decimal

        with pytest.raises(ValueError, match="American odds"):
            american_to_decimal(0)


# ---------- decimal_to_american ----------


class TestDecimalToAmerican:
    def test_above_even(self) -> None:
        from fastbreak.betting import decimal_to_american

        assert decimal_to_american(2.5) == 150

    def test_below_even(self) -> None:
        from fastbreak.betting import decimal_to_american

        assert decimal_to_american(1.5) == -200

    def test_even_money_is_positive_100(self) -> None:
        from fastbreak.betting import decimal_to_american

        assert decimal_to_american(2.0) == 100

    def test_rejects_decimal_at_or_below_one(self) -> None:
        from fastbreak.betting import decimal_to_american

        with pytest.raises(ValueError, match="decimal odds"):
            decimal_to_american(1.0)

    def test_rejects_nan(self) -> None:
        from fastbreak.betting import decimal_to_american

        # NaN slips past the <= 1.0 guard (all NaN comparisons are False) and
        # would fail deep inside round() with an opaque exception.
        with pytest.raises(ValueError, match="decimal odds"):
            decimal_to_american(math.nan)

    def test_rejects_infinity(self) -> None:
        from fastbreak.betting import decimal_to_american

        with pytest.raises(ValueError, match="decimal odds"):
            decimal_to_american(math.inf)


# ---------- american <-> decimal roundtrip (PBT) ----------


@given(
    odds=st.one_of(
        st.integers(min_value=100, max_value=100_000),
        st.integers(min_value=-100_000, max_value=-101),
    )
)
@settings(max_examples=300)
def test_american_decimal_roundtrip(odds: int) -> None:
    """decimal_to_american(american_to_decimal(o)) == o.

    Excludes -100 from the generator because both +100 and -100 map to
    decimal 2.0, so -100 normalizes to +100 on the return trip.
    """
    from fastbreak.betting import american_to_decimal, decimal_to_american

    assert decimal_to_american(american_to_decimal(odds)) == odds


# ---------- american_to_prob / decimal_to_prob ----------


class TestImpliedProbability:
    def test_american_positive(self) -> None:
        from fastbreak.betting import american_to_prob

        assert american_to_prob(150) == pytest.approx(0.4)

    def test_american_negative(self) -> None:
        from fastbreak.betting import american_to_prob

        assert american_to_prob(-200) == pytest.approx(2.0 / 3.0)

    def test_decimal(self) -> None:
        from fastbreak.betting import decimal_to_prob

        assert decimal_to_prob(2.5) == pytest.approx(0.4)

    def test_decimal_rejects_at_or_below_one(self) -> None:
        from fastbreak.betting import decimal_to_prob

        with pytest.raises(ValueError, match="decimal odds"):
            decimal_to_prob(0.9)

    def test_decimal_rejects_nan(self) -> None:
        from fastbreak.betting import decimal_to_prob

        # NaN slips past the <= 1.0 guard and would return NaN downstream.
        with pytest.raises(ValueError, match="decimal odds"):
            decimal_to_prob(math.nan)

    def test_decimal_rejects_infinity(self) -> None:
        from fastbreak.betting import decimal_to_prob

        with pytest.raises(ValueError, match="decimal odds"):
            decimal_to_prob(math.inf)


@given(
    odds=st.one_of(
        st.integers(min_value=100, max_value=100_000),
        st.integers(min_value=-100_000, max_value=-100),
    )
)
@settings(max_examples=300)
def test_american_prob_matches_decimal_prob(odds: int) -> None:
    """american_to_prob(o) == decimal_to_prob(american_to_decimal(o))."""
    from fastbreak.betting import american_to_decimal, american_to_prob, decimal_to_prob

    assert american_to_prob(odds) == pytest.approx(
        decimal_to_prob(american_to_decimal(odds))
    )


@given(
    odds=st.one_of(
        st.integers(min_value=100, max_value=100_000),
        st.integers(min_value=-100_000, max_value=-100),
    )
)
@settings(max_examples=300)
def test_implied_prob_in_unit_interval(odds: int) -> None:
    from fastbreak.betting import american_to_prob

    p = american_to_prob(odds)
    assert 0.0 < p < 1.0


# ---------- remove_vig ----------


class TestRemoveVig:
    def test_two_way_symmetric(self) -> None:
        from fastbreak.betting import remove_vig

        # Both sides priced at implied 0.6 (typical -150/-150 book).
        assert remove_vig([0.6, 0.6]) == pytest.approx([0.5, 0.5])

    def test_preserves_ratio(self) -> None:
        from fastbreak.betting import remove_vig

        result = remove_vig([0.6, 0.3])
        assert result == pytest.approx([2.0 / 3.0, 1.0 / 3.0])

    def test_rejects_empty(self) -> None:
        from fastbreak.betting import remove_vig

        with pytest.raises(ValueError, match="at least one"):
            remove_vig([])

    def test_rejects_nonpositive_sum(self) -> None:
        from fastbreak.betting import remove_vig

        with pytest.raises(ValueError, match="positive"):
            remove_vig([0.0, 0.0])

    def test_rejects_negative_input(self) -> None:
        from fastbreak.betting import remove_vig

        # A negative prob with a larger positive keeps the sum positive, so it
        # slips past the sum check and would emit a negative "probability".
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            remove_vig([-0.2, 0.9])

    def test_rejects_above_one_input(self) -> None:
        from fastbreak.betting import remove_vig

        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            remove_vig([1.5, 0.3])

    def test_rejects_nan_input(self) -> None:
        from fastbreak.betting import remove_vig

        with pytest.raises(ValueError, match="finite"):
            remove_vig([math.nan, 0.5])

    def test_rejects_infinite_input(self) -> None:
        from fastbreak.betting import remove_vig

        with pytest.raises(ValueError, match="finite"):
            remove_vig([math.inf, 0.5])


@given(
    probs=st.lists(
        st.floats(min_value=0.01, max_value=0.99, allow_nan=False),
        min_size=2,
        max_size=6,
    )
)
@settings(max_examples=300)
def test_remove_vig_sums_to_one(probs: list[float]) -> None:
    from fastbreak.betting import remove_vig

    assert sum(remove_vig(probs)) == pytest.approx(1.0)


# ---------- bet_ev ----------


class TestBetEv:
    def test_fair_bet_is_zero(self) -> None:
        from fastbreak.betting import bet_ev

        assert bet_ev(win_prob=0.5, decimal_odds=2.0) == pytest.approx(0.0)

    def test_positive_edge(self) -> None:
        from fastbreak.betting import bet_ev

        # p=0.6 at +100 (decimal 2.0): 0.6*1 - 0.4 = 0.2 per unit.
        assert bet_ev(win_prob=0.6, decimal_odds=2.0) == pytest.approx(0.2)

    def test_negative_edge(self) -> None:
        from fastbreak.betting import bet_ev

        assert bet_ev(win_prob=0.4, decimal_odds=2.0) == pytest.approx(-0.2)

    def test_rejects_prob_out_of_range(self) -> None:
        from fastbreak.betting import bet_ev

        with pytest.raises(ValueError, match="win_prob"):
            bet_ev(win_prob=1.5, decimal_odds=2.0)

    def test_rejects_nan_odds(self) -> None:
        from fastbreak.betting import bet_ev

        # NaN bypasses the <= 1.0 guard and would return NaN downstream.
        with pytest.raises(ValueError, match="decimal_odds"):
            bet_ev(win_prob=0.5, decimal_odds=math.nan)

    def test_rejects_infinite_odds(self) -> None:
        from fastbreak.betting import bet_ev

        with pytest.raises(ValueError, match="decimal_odds"):
            bet_ev(win_prob=0.5, decimal_odds=math.inf)


# ---------- kelly_fraction ----------


class TestKellyFraction:
    def test_positive_edge(self) -> None:
        from fastbreak.betting import kelly_fraction

        # p=0.6, d=2.0: edge=0.2, b=1.0 -> f*=0.2
        assert kelly_fraction(win_prob=0.6, decimal_odds=2.0) == pytest.approx(0.2)

    def test_negative_edge_clamps_to_zero(self) -> None:
        from fastbreak.betting import kelly_fraction

        assert kelly_fraction(win_prob=0.4, decimal_odds=2.0) == 0.0

    def test_fractional_kelly_scales(self) -> None:
        from fastbreak.betting import kelly_fraction

        full = kelly_fraction(win_prob=0.6, decimal_odds=2.0)
        half = kelly_fraction(win_prob=0.6, decimal_odds=2.0, fraction=0.5)
        assert half == pytest.approx(full * 0.5)

    def test_rejects_bad_fraction(self) -> None:
        from fastbreak.betting import kelly_fraction

        with pytest.raises(ValueError, match="fraction"):
            kelly_fraction(win_prob=0.6, decimal_odds=2.0, fraction=0.0)

    def test_rejects_nan_odds(self) -> None:
        from fastbreak.betting import kelly_fraction

        with pytest.raises(ValueError, match="decimal_odds"):
            kelly_fraction(win_prob=0.6, decimal_odds=math.nan)

    def test_rejects_infinite_odds(self) -> None:
        from fastbreak.betting import kelly_fraction

        with pytest.raises(ValueError, match="decimal_odds"):
            kelly_fraction(win_prob=0.6, decimal_odds=math.inf)


@given(
    win_prob=st.floats(min_value=0.0, max_value=1.0),
    decimal_odds=st.floats(min_value=1.01, max_value=50.0),
)
@settings(max_examples=300)
def test_kelly_never_negative(win_prob: float, decimal_odds: float) -> None:
    from fastbreak.betting import kelly_fraction

    assert kelly_fraction(win_prob=win_prob, decimal_odds=decimal_odds) >= 0.0


@given(
    win_prob=st.floats(min_value=0.0, max_value=1.0),
    decimal_odds=st.floats(min_value=1.01, max_value=50.0),
)
@settings(max_examples=300)
def test_kelly_positive_iff_positive_ev(win_prob: float, decimal_odds: float) -> None:
    """Kelly stake is > 0 exactly when the bet is +EV."""
    from fastbreak.betting import bet_ev, kelly_fraction

    ev = bet_ev(win_prob=win_prob, decimal_odds=decimal_odds)
    f = kelly_fraction(win_prob=win_prob, decimal_odds=decimal_odds)
    if ev > 1e-9:
        assert f > 0.0
    else:
        assert f == 0.0


# ---------- closing_line_value ----------


class TestClosingLineValue:
    def test_beat_the_close(self) -> None:
        from fastbreak.betting import closing_line_value

        # Bet at 2.1, line closed at 2.0 -> 5% CLV.
        assert closing_line_value(
            bet_decimal=2.1, closing_decimal=2.0
        ) == pytest.approx(0.05)

    def test_worse_than_close_is_negative(self) -> None:
        from fastbreak.betting import closing_line_value

        assert closing_line_value(bet_decimal=1.9, closing_decimal=2.0) < 0.0

    def test_rejects_nan_bet_decimal(self) -> None:
        from fastbreak.betting import closing_line_value

        with pytest.raises(ValueError, match="bet_decimal"):
            closing_line_value(bet_decimal=math.nan, closing_decimal=2.0)

    def test_rejects_infinite_closing_decimal(self) -> None:
        from fastbreak.betting import closing_line_value

        with pytest.raises(ValueError, match="closing_decimal"):
            closing_line_value(bet_decimal=2.0, closing_decimal=math.inf)


# ---------- spread <-> win_prob ----------


class TestSpreadWinProb:
    def test_pick_em_is_fifty_fifty(self) -> None:
        from fastbreak.betting import spread_to_win_prob

        assert spread_to_win_prob(0.0) == pytest.approx(0.5, abs=1e-9)

    def test_favorite_above_half(self) -> None:
        from fastbreak.betting import spread_to_win_prob

        # Favored by 7 (spread -7) -> win prob > 0.5.
        assert spread_to_win_prob(-7.0) > 0.5

    def test_underdog_below_half(self) -> None:
        from fastbreak.betting import spread_to_win_prob

        assert spread_to_win_prob(7.0) < 0.5

    def test_win_prob_to_spread_pick_em(self) -> None:
        from fastbreak.betting import win_prob_to_spread

        assert win_prob_to_spread(0.5) == pytest.approx(0.0, abs=1e-6)

    def test_rejects_sigma_nonpositive(self) -> None:
        from fastbreak.betting import spread_to_win_prob

        with pytest.raises(ValueError, match="sigma"):
            spread_to_win_prob(0.0, sigma=0.0)

    def test_rejects_nonfinite_spread_naming_spread(self) -> None:
        from fastbreak.betting import spread_to_win_prob

        # A non-finite spread already raises (via normal_sf's mean check), but
        # the error should name `spread` at this boundary, not the internal
        # `mean`, so the caller knows which argument was bad.
        for bad in (math.nan, math.inf, -math.inf):
            with pytest.raises(ValueError, match="spread"):
                spread_to_win_prob(bad)

    def test_win_prob_to_spread_rejects_degenerate(self) -> None:
        from fastbreak.betting import win_prob_to_spread

        with pytest.raises(ValueError, match="win_prob"):
            win_prob_to_spread(0.0)
        with pytest.raises(ValueError, match="win_prob"):
            win_prob_to_spread(1.0)


@given(spread=st.floats(min_value=-30.0, max_value=30.0))
@settings(max_examples=300)
def test_spread_winprob_roundtrip(spread: float) -> None:
    """win_prob_to_spread(spread_to_win_prob(s)) == s."""
    from fastbreak.betting import spread_to_win_prob, win_prob_to_spread

    p = spread_to_win_prob(spread)
    assert win_prob_to_spread(p) == pytest.approx(spread, abs=1e-4)


@given(spread=st.floats(min_value=-40.0, max_value=40.0))
@settings(max_examples=300)
def test_spread_to_win_prob_monotonic(spread: float) -> None:
    """A bigger favorite (more negative spread) wins more often."""
    from fastbreak.betting import spread_to_win_prob

    assert spread_to_win_prob(spread - 1.0) >= spread_to_win_prob(spread)


# ---------- log5 ----------


class TestLog5:
    def test_equal_strength_is_half(self) -> None:
        from fastbreak.betting import log5

        assert log5(0.5, 0.5) == pytest.approx(0.5)

    def test_league_average_opponent_returns_own_rate(self) -> None:
        from fastbreak.betting import log5

        # Against a .500 opponent, A's win prob equals its own rate.
        assert log5(0.7, 0.5) == pytest.approx(0.7)

    def test_known_value(self) -> None:
        from fastbreak.betting import log5

        assert log5(0.6, 0.4) == pytest.approx(0.36 / 0.52)

    def test_rejects_degenerate(self) -> None:
        from fastbreak.betting import log5

        with pytest.raises(ValueError, match="degenerate"):
            log5(0.0, 0.0)


@given(
    p_a=st.floats(min_value=0.01, max_value=0.99),
    p_b=st.floats(min_value=0.01, max_value=0.99),
)
@settings(max_examples=300)
def test_log5_complementary(p_a: float, p_b: float) -> None:
    """log5(a, b) + log5(b, a) == 1 (A beating B vs B beating A)."""
    from fastbreak.betting import log5

    assert log5(p_a, p_b) + log5(p_b, p_a) == pytest.approx(1.0)


@given(
    p_a=st.floats(min_value=0.01, max_value=0.99),
    p_b=st.floats(min_value=0.01, max_value=0.99),
)
@settings(max_examples=300)
def test_log5_in_unit_interval(p_a: float, p_b: float) -> None:
    from fastbreak.betting import log5

    assert 0.0 <= log5(p_a, p_b) <= 1.0


def test_module_has_no_scipy_dependency() -> None:
    """betting.py must rely only on stdlib math (house convention)."""
    import fastbreak.betting as betting_mod

    source = betting_mod.__file__
    assert source is not None
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    assert "import scipy" not in text
    assert "from scipy" not in text
    assert "import math" in text or "from math" in text
