"""Property-based tests for fastbreak.metrics using Hypothesis.

Covers mathematical invariants that hold for *all* valid inputs:
bounds, scale invariance, symmetry, identity values, and composition.
These complement the example-based tests in test_metrics.py.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from fastbreak.metrics import (
    LeagueAverages,
    assist_ratio,
    ast_to_tov,
    drtg,
    effective_fg_pct,
    four_factors,
    free_throw_rate,
    net_rtg,
    ortg,
    per_100,
    per_36,
    possessions,
    pythagorean_win_pct,
    relative_efg,
    relative_ts,
    rolling_avg,
    three_point_rate,
    tov_pct,
    true_shooting,
)

# ─── Shared strategies ────────────────────────────────────────────────────────

# Non-negative float (including zero) — for counting stats.
# allow_subnormal=False excludes denormalized values (below 2^-1022) where
# expressions like 0.44 * 5e-324 underflow to 0.0, breaking scale invariance.
nn = st.floats(
    min_value=0.0,
    max_value=200.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

# Strictly positive float — for required-positive denominators and scale factors
pos = st.floats(min_value=0.01, max_value=200.0, allow_nan=False, allow_infinity=False)

# Scale factor for scale-invariance tests
scale = st.floats(min_value=0.01, max_value=50.0, allow_nan=False, allow_infinity=False)

_XDIST = [HealthCheck.differing_executors]


@st.composite
def league_averages_st(draw: st.DrawFn) -> LeagueAverages:
    """Build a valid LeagueAverages satisfying all __post_init__ constraints."""
    lg_pts = draw(pos)
    lg_fga = draw(pos)
    lg_fta = draw(pos)
    lg_ftm = draw(pos)
    lg_oreb = draw(nn)
    lg_treb = draw(pos)
    lg_ast = draw(nn)
    lg_fgm = draw(pos)
    lg_fg3m = draw(nn)
    lg_tov = draw(nn)
    lg_pf = draw(pos)
    # Cross-field: offensive rebounds cannot exceed total rebounds
    assume(lg_oreb <= lg_treb)
    # vop denominator must be positive (validated in __post_init__)
    assume(lg_fga - lg_oreb + lg_tov + 0.44 * lg_fta > 0)
    return LeagueAverages(
        lg_pts=lg_pts,
        lg_fga=lg_fga,
        lg_fta=lg_fta,
        lg_ftm=lg_ftm,
        lg_oreb=lg_oreb,
        lg_treb=lg_treb,
        lg_ast=lg_ast,
        lg_fgm=lg_fgm,
        lg_fg3m=lg_fg3m,
        lg_tov=lg_tov,
        lg_pf=lg_pf,
    )


# ─── LeagueAverages derived properties ────────────────────────────────────────


class TestLeagueAveragesDerivedProperties:
    """lg_pace is a computed property — test that it matches its own formula."""

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_lg_pace_matches_formula(self, lg: LeagueAverages) -> None:
        """lg_pace == lg_fga - lg_oreb + lg_tov + 0.44 * lg_fta."""
        expected = lg.lg_fga - lg.lg_oreb + lg.lg_tov + 0.44 * lg.lg_fta
        assert lg.lg_pace == pytest.approx(expected, rel=1e-9)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_vop_matches_formula(self, lg: LeagueAverages) -> None:
        """vop == lg_pts / lg_pace."""
        assert lg.vop == pytest.approx(lg.lg_pts / lg.lg_pace, rel=1e-9)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_efg_matches_formula(self, lg: LeagueAverages) -> None:
        """efg == (lg_fgm + 0.5 * lg_fg3m) / lg_fga."""
        expected = (lg.lg_fgm + 0.5 * lg.lg_fg3m) / lg.lg_fga
        assert lg.efg == pytest.approx(expected, rel=1e-9)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_ts_matches_formula(self, lg: LeagueAverages) -> None:
        """ts == lg_pts / (2 * (lg_fga + 0.44 * lg_fta))."""
        expected = lg.lg_pts / (2 * (lg.lg_fga + 0.44 * lg.lg_fta))
        assert lg.ts == pytest.approx(expected, rel=1e-9)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_lg_pace_positive(self, lg: LeagueAverages) -> None:
        """lg_pace is always positive (validated by __post_init__)."""
        assert lg.lg_pace > 0


# ─── true_shooting ────────────────────────────────────────────────────────────


class TestTrueShootingProperties:
    @given(pts=nn, fga=pos, fta=nn)
    @settings(suppress_health_check=_XDIST)
    def test_non_negative(self, pts: float, fga: float, fta: float) -> None:
        """TS% is non-negative when pts >= 0."""
        result = true_shooting(pts=pts, fga=fga, fta=fta)
        assert result is not None
        assert result >= 0.0

    @given(pts=nn, fga=pos, fta=nn, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_scale_invariance(
        self, pts: float, fga: float, fta: float, k: float
    ) -> None:
        """TS%(k·pts, k·fga, k·fta) == TS%(pts, fga, fta) — the k cancels."""
        original = true_shooting(pts=pts, fga=fga, fta=fta)
        scaled = true_shooting(pts=k * pts, fga=k * fga, fta=k * fta)
        assert scaled == pytest.approx(original, rel=1e-9)

    def test_none_when_zero_attempts(self) -> None:
        """Returns None only when both fga and fta are zero."""
        assert true_shooting(pts=0.0, fga=0.0, fta=0.0) is None


# ─── effective_fg_pct ─────────────────────────────────────────────────────────


class TestEffectiveFgPctProperties:
    @given(fgm=nn, fga=pos)
    @settings(suppress_health_check=_XDIST)
    def test_no_threes_equals_fg_pct(self, fgm: float, fga: float) -> None:
        """eFG% == FG% when fg3m = 0."""
        result = effective_fg_pct(fgm=fgm, fg3m=0.0, fga=fga)
        assert result == pytest.approx(fgm / fga, rel=1e-9)

    @given(fgm=nn, fg3m=nn, fga=pos, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_scale_invariance(
        self, fgm: float, fg3m: float, fga: float, k: float
    ) -> None:
        """eFG%(k·fgm, k·fg3m, k·fga) == eFG%(fgm, fg3m, fga)."""
        original = effective_fg_pct(fgm=fgm, fg3m=fg3m, fga=fga)
        scaled = effective_fg_pct(fgm=k * fgm, fg3m=k * fg3m, fga=k * fga)
        assert scaled == pytest.approx(original, rel=1e-9)

    @given(fgm=nn, fg3m=nn, fga=pos)
    @settings(suppress_health_check=_XDIST)
    def test_at_least_plain_fg_pct(self, fgm: float, fg3m: float, fga: float) -> None:
        """eFG% >= FG% — 3-pointers can only raise or hold the percentage."""
        efg = effective_fg_pct(fgm=fgm, fg3m=fg3m, fga=fga)
        fg = fgm / fga
        assert efg is not None
        assert efg >= fg - 1e-12  # small tolerance for float comparison


# ─── free_throw_rate ──────────────────────────────────────────────────────────


class TestFreeThrowRateProperties:
    @given(fta=nn, fga=pos)
    @settings(suppress_health_check=_XDIST)
    def test_non_negative(self, fta: float, fga: float) -> None:
        """FTR >= 0 for non-negative inputs."""
        result = free_throw_rate(fta=fta, fga=fga)
        assert result is not None
        assert result >= 0.0

    @given(fta=nn, fga=pos, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_scale_invariance(self, fta: float, fga: float, k: float) -> None:
        """FTR(k·fta, k·fga) == FTR(fta, fga)."""
        assert free_throw_rate(fta=k * fta, fga=k * fga) == pytest.approx(
            free_throw_rate(fta=fta, fga=fga), rel=1e-9
        )


# ─── three_point_rate ─────────────────────────────────────────────────────────


class TestThreePointRateProperties:
    @given(fg3a=nn, fga=pos)
    @settings(suppress_health_check=_XDIST)
    def test_bounded_when_fg3a_le_fga(self, fg3a: float, fga: float) -> None:
        """3PR in [0, 1] when fg3a <= fga (physically valid)."""
        assume(fg3a <= fga)
        result = three_point_rate(fg3a=fg3a, fga=fga)
        assert result is not None
        assert 0.0 <= result <= 1.0

    @given(fg3a=nn, fga=pos, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_scale_invariance(self, fg3a: float, fga: float, k: float) -> None:
        """3PR(k·fg3a, k·fga) == 3PR(fg3a, fga)."""
        assert three_point_rate(fg3a=k * fg3a, fga=k * fga) == pytest.approx(
            three_point_rate(fg3a=fg3a, fga=fga), rel=1e-9
        )


# ─── tov_pct ──────────────────────────────────────────────────────────────────


class TestTovPctProperties:
    @given(fga=nn, fta=nn, tov=nn)
    @settings(suppress_health_check=_XDIST)
    def test_bounded_in_zero_to_one(self, fga: float, fta: float, tov: float) -> None:
        """TOV% is always in [0, 1] — tov can never exceed its own denominator."""
        result = tov_pct(fga=fga, fta=fta, tov=tov)
        if result is not None:
            assert 0.0 <= result <= 1.0

    @given(fga=nn, fta=nn, tov=pos)
    @settings(suppress_health_check=_XDIST)
    def test_non_none_when_tov_positive(
        self, fga: float, fta: float, tov: float
    ) -> None:
        """Result is non-None whenever tov > 0 (denominator is at least tov)."""
        result = tov_pct(fga=fga, fta=fta, tov=tov)
        assert result is not None

    @given(fga=nn, fta=nn, tov=nn, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_scale_invariance(
        self, fga: float, fta: float, tov: float, k: float
    ) -> None:
        """TOV%(k·fga, k·fta, k·tov) == TOV%(fga, fta, tov)."""
        denom = fga + 0.44 * fta + tov
        # Skip inputs where IEEE 754 underflow would collapse a subnormal
        # denominator to 0 after scaling, producing a spurious None result.
        assume(denom == 0.0 or k * denom > 0)
        original = tov_pct(fga=fga, fta=fta, tov=tov)
        scaled = tov_pct(fga=k * fga, fta=k * fta, tov=k * tov)
        if original is None:
            assert scaled is None
        else:
            assert scaled == pytest.approx(original, rel=1e-9)

    def test_none_when_all_zero(self) -> None:
        """Returns None only when fga=fta=tov=0."""
        assert tov_pct(fga=0.0, fta=0.0, tov=0.0) is None


# ─── possessions ──────────────────────────────────────────────────────────────


class TestPossessionsProperties:
    @given(fga=nn, oreb=nn, tov=nn, fta=nn, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_scale_invariance(
        self, fga: float, oreb: float, tov: float, fta: float, k: float
    ) -> None:
        """possessions(k·a, k·b, k·c, k·d) == k · possessions(a, b, c, d)."""
        original = possessions(fga=fga, oreb=oreb, tov=tov, fta=fta)
        scaled = possessions(fga=k * fga, oreb=k * oreb, tov=k * tov, fta=k * fta)
        assert scaled == pytest.approx(k * original, rel=1e-9)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_matches_lg_pace(self, lg: LeagueAverages) -> None:
        """possessions() with lg fields == lg.lg_pace (same formula)."""
        result = possessions(
            fga=lg.lg_fga, oreb=lg.lg_oreb, tov=lg.lg_tov, fta=lg.lg_fta
        )
        assert result == pytest.approx(lg.lg_pace, rel=1e-9)


# ─── ortg / drtg / net_rtg ────────────────────────────────────────────────────


class TestOrtgDrtgNetRtgProperties:
    @given(pts=nn, fga=pos, oreb=nn, tov=nn, fta=nn)
    @settings(suppress_health_check=_XDIST)
    def test_ortg_non_negative(
        self, pts: float, fga: float, oreb: float, tov: float, fta: float
    ) -> None:
        """ORTG >= 0 for non-negative pts with a valid (positive) possession count.

        oreb > fga is physically impossible (can't rebound more than you shot)
        and produces a negative possession denominator, so we exclude it.
        """
        assume(fga - oreb + tov + 0.44 * fta > 0)
        result = ortg(pts=pts, fga=fga, oreb=oreb, tov=tov, fta=fta)
        assert result is not None
        assert result >= 0.0

    @given(pts=nn, fga=pos, oreb=nn, tov=nn, fta=nn, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_ortg_scale_invariance(
        self, pts: float, fga: float, oreb: float, tov: float, fta: float, k: float
    ) -> None:
        """ORTG(k·pts, k·fga, k·oreb, k·tov, k·fta) == ORTG(pts, fga, oreb, tov, fta)."""
        assume(fga - oreb + tov + 0.44 * fta > 0)
        original = ortg(pts=pts, fga=fga, oreb=oreb, tov=tov, fta=fta)
        scaled = ortg(pts=k * pts, fga=k * fga, oreb=k * oreb, tov=k * tov, fta=k * fta)
        assert scaled == pytest.approx(original, rel=1e-9)

    @given(opp_pts=nn, opp_fga=pos, opp_oreb=nn, opp_tov=nn, opp_fta=nn, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_drtg_scale_invariance(
        self,
        opp_pts: float,
        opp_fga: float,
        opp_oreb: float,
        opp_tov: float,
        opp_fta: float,
        k: float,
    ) -> None:
        """DRTG scales the same way as ORTG — uses opponent possession estimate."""
        assume(opp_fga - opp_oreb + opp_tov + 0.44 * opp_fta > 0)
        original = drtg(
            opp_pts=opp_pts,
            opp_fga=opp_fga,
            opp_oreb=opp_oreb,
            opp_tov=opp_tov,
            opp_fta=opp_fta,
        )
        scaled = drtg(
            opp_pts=k * opp_pts,
            opp_fga=k * opp_fga,
            opp_oreb=k * opp_oreb,
            opp_tov=k * opp_tov,
            opp_fta=k * opp_fta,
        )
        assert scaled == pytest.approx(original, rel=1e-9)

    @given(a=pos, b=pos)
    @settings(suppress_health_check=_XDIST)
    def test_net_rtg_antisymmetry(self, a: float, b: float) -> None:
        """net_rtg(a, b) == -net_rtg(b, a)."""
        assert net_rtg(a, b) == pytest.approx(-net_rtg(b, a), rel=1e-9)  # type: ignore[operator]

    @given(a=pos)
    @settings(suppress_health_check=_XDIST)
    def test_net_rtg_zero_when_equal(self, a: float) -> None:
        """net_rtg(a, a) == 0 — equal ORTG and DRTG cancel out."""
        assert net_rtg(a, a) == pytest.approx(0.0, abs=1e-12)

    @given(a=pos, b=pos)
    @settings(suppress_health_check=_XDIST)
    def test_net_rtg_is_difference(self, a: float, b: float) -> None:
        """net_rtg(a, b) == a - b by definition."""
        assert net_rtg(a, b) == pytest.approx(a - b, rel=1e-9)


# ─── pythagorean_win_pct ──────────────────────────────────────────────────────


class TestPythagoreanWinPctProperties:
    @given(
        pts=pos,
        opp_pts=pos,
        exp=st.floats(
            min_value=1.0, max_value=20.0, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(suppress_health_check=_XDIST)
    def test_bounded_in_zero_to_one(
        self, pts: float, opp_pts: float, exp: float
    ) -> None:
        """Pythagorean win% is always in [0, 1] for positive inputs."""
        result = pythagorean_win_pct(pts=pts, opp_pts=opp_pts, exp=exp)
        assert result is not None
        assert 0.0 <= result <= 1.0

    @given(
        pts=pos,
        opp_pts=pos,
        exp=st.floats(
            min_value=1.0, max_value=20.0, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(suppress_health_check=_XDIST)
    def test_complement_symmetry(self, pts: float, opp_pts: float, exp: float) -> None:
        """win_pct(a, b) + win_pct(b, a) == 1.0 for any positive inputs."""
        forward = pythagorean_win_pct(pts=pts, opp_pts=opp_pts, exp=exp)
        reverse = pythagorean_win_pct(pts=opp_pts, opp_pts=pts, exp=exp)
        assert forward is not None
        assert reverse is not None
        assert forward + reverse == pytest.approx(1.0, rel=1e-9)

    @given(
        pts=pos,
        exp=st.floats(
            min_value=1.0, max_value=20.0, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(suppress_health_check=_XDIST)
    def test_equal_scoring_gives_fifty_pct(self, pts: float, exp: float) -> None:
        """win_pct(a, a) == 0.5 — equal offenses → even odds."""
        result = pythagorean_win_pct(pts=pts, opp_pts=pts, exp=exp)
        assert result == pytest.approx(0.5, rel=1e-9)

    @given(pts=pos, opp_pts=pos)
    @settings(suppress_health_check=_XDIST)
    def test_more_points_means_higher_win_pct(self, pts: float, opp_pts: float) -> None:
        """Scoring more points than the opponent → win% > 0.5."""
        assume(pts > opp_pts)
        result = pythagorean_win_pct(pts=pts, opp_pts=opp_pts)
        assert result is not None
        assert result > 0.5


# ─── per_36 / per_100 normalization ───────────────────────────────────────────


class TestPerNormalizationProperties:
    @given(stat=nn)
    @settings(suppress_health_check=_XDIST)
    def test_per_36_identity_at_36_minutes(self, stat: float) -> None:
        """per_36(stat, 36) == stat — 36 minutes is the normalization unit."""
        assert per_36(stat=stat, minutes=36.0) == pytest.approx(stat, rel=1e-9)

    @given(stat=nn)
    @settings(suppress_health_check=_XDIST)
    def test_per_100_identity_at_100_possessions(self, stat: float) -> None:
        """per_100(stat, 100) == stat — 100 possessions is the normalization unit."""
        assert per_100(stat=stat, poss=100.0) == pytest.approx(stat, rel=1e-9)

    @given(a=nn, b=nn, minutes=pos)
    @settings(suppress_health_check=_XDIST)
    def test_per_36_linearity(self, a: float, b: float, minutes: float) -> None:
        """per_36 is linear in stat: per_36(a+b, m) == per_36(a, m) + per_36(b, m)."""
        combined = per_36(stat=a + b, minutes=minutes)
        separate = per_36(stat=a, minutes=minutes) + per_36(stat=b, minutes=minutes)  # type: ignore[operator]
        assert combined == pytest.approx(separate, rel=1e-9)

    @given(a=nn, b=nn, poss=pos)
    @settings(suppress_health_check=_XDIST)
    def test_per_100_linearity(self, a: float, b: float, poss: float) -> None:
        """per_100 is linear in stat: per_100(a+b, p) == per_100(a, p) + per_100(b, p)."""
        combined = per_100(stat=a + b, poss=poss)
        separate = per_100(stat=a, poss=poss) + per_100(stat=b, poss=poss)  # type: ignore[operator]
        assert combined == pytest.approx(separate, rel=1e-9)

    def test_per_36_none_at_zero_minutes(self) -> None:
        assert per_36(stat=10.0, minutes=0.0) is None

    def test_per_100_none_at_zero_possessions(self) -> None:
        assert per_100(stat=10.0, poss=0.0) is None


# ─── relative_ts / relative_efg ───────────────────────────────────────────────


class TestRelativeMetricsProperties:
    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_relative_ts_zero_at_league_average(self, lg: LeagueAverages) -> None:
        """A player matching the league TS% has relative_ts == 0."""
        assert relative_ts(player_ts=lg.ts, lg=lg) == pytest.approx(0.0, abs=1e-12)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_relative_efg_zero_at_league_average(self, lg: LeagueAverages) -> None:
        """A player matching the league eFG% has relative_efg == 0."""
        assert relative_efg(player_efg=lg.efg, lg=lg) == pytest.approx(0.0, abs=1e-12)

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_relative_ts_none_propagates(self, lg: LeagueAverages) -> None:
        """relative_ts(None, lg) is None."""
        assert relative_ts(player_ts=None, lg=lg) is None

    @given(lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_relative_efg_none_propagates(self, lg: LeagueAverages) -> None:
        """relative_efg(None, lg) is None."""
        assert relative_efg(player_efg=None, lg=lg) is None

    @given(player_ts=pos, lg=league_averages_st())
    @settings(suppress_health_check=_XDIST)
    def test_relative_ts_above_league_when_better(
        self, player_ts: float, lg: LeagueAverages
    ) -> None:
        """A player with TS% > league average has positive relative_ts."""
        assume(player_ts > lg.ts)
        result = relative_ts(player_ts=player_ts, lg=lg)
        assert result is not None
        assert result > 0.0


# ─── rolling_avg ──────────────────────────────────────────────────────────────


class TestRollingAvgProperties:
    @given(
        values=st.lists(st.one_of(st.none(), nn), min_size=0, max_size=50),
        window=st.integers(min_value=1, max_value=10),
    )
    @settings(suppress_health_check=_XDIST)
    def test_length_preserved(self, values: list[float | None], window: int) -> None:
        """Output length always equals input length."""
        result = rolling_avg(values, window)
        assert len(result) == len(values)

    @given(
        values=st.lists(nn, min_size=1, max_size=50),
        window=st.integers(min_value=1, max_value=10),
    )
    @settings(suppress_health_check=_XDIST)
    def test_warmup_positions_are_none(self, values: list[float], window: int) -> None:
        """First (window - 1) positions are always None (warm-up period)."""
        result = rolling_avg(values, window)
        for i in range(min(window - 1, len(values))):
            assert result[i] is None

    @given(
        v=pos,
        n=st.integers(min_value=1, max_value=30),
        window=st.integers(min_value=1, max_value=10),
    )
    @settings(suppress_health_check=_XDIST)
    def test_constant_sequence_gives_constant_output(
        self, v: float, n: int, window: int
    ) -> None:
        """A constant-value sequence: every non-warm-up output equals v."""
        values = [v] * n
        result = rolling_avg(values, window)
        for i, out in enumerate(result):
            if i >= window - 1:
                assert out == pytest.approx(v, rel=1e-9)

    @given(
        values=st.lists(nn, min_size=2, max_size=20),
        window=st.integers(min_value=1, max_value=5),
    )
    @settings(suppress_health_check=_XDIST)
    def test_all_outputs_are_float_or_none(
        self, values: list[float], window: int
    ) -> None:
        """Every element of the output is either float or None."""
        for out in rolling_avg(values, window):
            assert out is None or isinstance(out, float)


# ─── four_factors composition ─────────────────────────────────────────────────


class TestFourFactorsCompositionProperties:
    @given(
        fgm=nn,
        fg3m=nn,
        fga=pos,
        tov=nn,
        fta=nn,
        oreb=nn,
        opp_dreb=nn,
    )
    @settings(suppress_health_check=_XDIST)
    def test_efg_matches_direct_call(
        self,
        fgm: float,
        fg3m: float,
        fga: float,
        tov: float,
        fta: float,
        oreb: float,
        opp_dreb: float,
    ) -> None:
        """four_factors().efg_pct == effective_fg_pct(fgm, fg3m, fga)."""
        ff = four_factors(
            fgm=fgm, fg3m=fg3m, fga=fga, tov=tov, fta=fta, oreb=oreb, opp_dreb=opp_dreb
        )
        assert ff.efg_pct == effective_fg_pct(fgm=fgm, fg3m=fg3m, fga=fga)

    @given(
        fgm=nn,
        fg3m=nn,
        fga=pos,
        tov=nn,
        fta=nn,
        oreb=nn,
        opp_dreb=nn,
    )
    @settings(suppress_health_check=_XDIST)
    def test_tov_pct_matches_direct_call(
        self,
        fgm: float,
        fg3m: float,
        fga: float,
        tov: float,
        fta: float,
        oreb: float,
        opp_dreb: float,
    ) -> None:
        """four_factors().tov_pct == tov_pct(fga, fta, tov)."""
        ff = four_factors(
            fgm=fgm, fg3m=fg3m, fga=fga, tov=tov, fta=fta, oreb=oreb, opp_dreb=opp_dreb
        )
        assert ff.tov_pct == tov_pct(fga=fga, fta=fta, tov=tov)

    @given(
        fgm=nn,
        fg3m=nn,
        fga=pos,
        tov=nn,
        fta=nn,
        oreb=nn,
        opp_dreb=nn,
    )
    @settings(suppress_health_check=_XDIST)
    def test_ftr_matches_direct_call(
        self,
        fgm: float,
        fg3m: float,
        fga: float,
        tov: float,
        fta: float,
        oreb: float,
        opp_dreb: float,
    ) -> None:
        """four_factors().ftr == free_throw_rate(fta, fga)."""
        ff = four_factors(
            fgm=fgm, fg3m=fg3m, fga=fga, tov=tov, fta=fta, oreb=oreb, opp_dreb=opp_dreb
        )
        assert ff.ftr == free_throw_rate(fta=fta, fga=fga)

    @given(
        fgm=nn,
        fg3m=nn,
        fga=pos,
        tov=nn,
        fta=nn,
        oreb=pos,
        opp_dreb=pos,
    )
    @settings(suppress_health_check=_XDIST)
    def test_oreb_pct_in_zero_to_one(
        self,
        fgm: float,
        fg3m: float,
        fga: float,
        tov: float,
        fta: float,
        oreb: float,
        opp_dreb: float,
    ) -> None:
        """four_factors().oreb_pct is in [0, 1] when both rebound counts are positive."""
        ff = four_factors(
            fgm=fgm, fg3m=fg3m, fga=fga, tov=tov, fta=fta, oreb=oreb, opp_dreb=opp_dreb
        )
        assert ff.oreb_pct is not None
        assert 0.0 <= ff.oreb_pct <= 1.0


# ─── ast_to_tov / assist_ratio ────────────────────────────────────────────────


class TestAstProperties:
    @given(ast=nn, tov=pos)
    @settings(suppress_health_check=_XDIST)
    def test_ast_to_tov_non_negative(self, ast: float, tov: float) -> None:
        """AST/TOV >= 0 for non-negative ast."""
        result = ast_to_tov(ast=ast, tov=tov)
        assert result is not None
        assert result >= 0.0

    @given(ast=nn, tov=pos, k=scale)
    @settings(suppress_health_check=_XDIST)
    def test_ast_to_tov_scale_invariance(
        self, ast: float, tov: float, k: float
    ) -> None:
        """AST/TOV(k·ast, k·tov) == AST/TOV(ast, tov)."""
        assert ast_to_tov(ast=k * ast, tov=k * tov) == pytest.approx(
            ast_to_tov(ast=ast, tov=tov), rel=1e-9
        )

    @given(ast=nn, fga=nn, fta=nn, tov=nn)
    @settings(suppress_health_check=_XDIST)
    def test_assist_ratio_non_negative(
        self, ast: float, fga: float, fta: float, tov: float
    ) -> None:
        """Assist ratio >= 0 for non-negative inputs."""
        result = assist_ratio(ast=ast, fga=fga, fta=fta, tov=tov)
        if result is not None:
            assert result >= 0.0
