"""Property-based tests for fastbreak.compare using Hypothesis.

Covers mathematical invariants that hold for *all* valid inputs:
antisymmetry, identity, sum invariant, derived correctness, and range constraint.
These complement the example-based tests in test_compare.py.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from fastbreak.compare import (
    COMPARISON_METRICS,
    ComparedPlayer,
    build_compared_player,
    comparison_deltas,
    comparison_edges,
    stat_leader,
)
from fastbreak.metrics import true_shooting
from tests.strategies import XDIST_SUPPRESS as _XDIST

# ─── Shared strategies ────────────────────────────────────────────────────────

# Non-negative float for counting stats (pts, fga, etc.)
nn = st.floats(
    min_value=0.0,
    max_value=200.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

# Strictly positive float for denominators
pos = st.floats(
    min_value=0.01,
    max_value=200.0,
    allow_nan=False,
    allow_infinity=False,
)

# Percentage float [0, 1]
pct = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Optional float (float or None)
opt = st.one_of(st.none(), nn)


@st.composite
def stats_stub_st(draw: st.DrawFn) -> object:
    """Build a lightweight stats stub satisfying _CompareStatsLike."""
    from dataclasses import dataclass

    @dataclass
    class _Stub:
        description: str = "Test"
        min: float = 0.0
        pts: float = 0.0
        reb: float = 0.0
        oreb: float = 0.0
        dreb: float = 0.0
        ast: float = 0.0
        stl: float = 0.0
        blk: float = 0.0
        tov: float = 0.0
        pf: float = 0.0
        plus_minus: float = 0.0
        fgm: float = 0.0
        fga: float = 0.0
        fg_pct: float = 0.0
        fg3m: float = 0.0
        fg3a: float = 0.0
        fg3_pct: float = 0.0
        ftm: float = 0.0
        fta: float = 0.0
        ft_pct: float = 0.0

    return _Stub(
        min=draw(nn),
        pts=draw(nn),
        reb=draw(nn),
        oreb=draw(nn),
        dreb=draw(nn),
        ast=draw(nn),
        stl=draw(nn),
        blk=draw(nn),
        tov=draw(nn),
        pf=draw(nn),
        plus_minus=draw(
            st.floats(
                min_value=-50.0,
                max_value=50.0,
                allow_nan=False,
                allow_infinity=False,
            )
        ),
        fgm=draw(nn),
        fga=draw(nn),
        fg_pct=draw(pct),
        fg3m=draw(nn),
        fg3a=draw(nn),
        fg3_pct=draw(pct),
        ftm=draw(nn),
        fta=draw(nn),
        ft_pct=draw(pct),
    )


@st.composite
def compared_player_st(draw: st.DrawFn) -> ComparedPlayer:
    """Build a valid ComparedPlayer with random stats."""
    pid = draw(st.integers(min_value=1, max_value=999999))
    stats = draw(stats_stub_st())
    return build_compared_player(pid, stats)


# ─── Derived metric correctness ──────────────────────────────────────────────


class TestDerivedCorrectness:
    """Selected build_compared_player derived metrics match direct computation."""

    @given(stats=stats_stub_st())
    @settings(suppress_health_check=_XDIST)
    def test_ts_pct_matches_true_shooting(self, stats: object) -> None:
        cp = build_compared_player(1, stats)  # type: ignore[arg-type]
        expected = true_shooting(
            pts=stats.pts,
            fga=stats.fga,
            fta=stats.fta,  # type: ignore[attr-defined]
        )
        if expected is None:
            assert cp.ts_pct is None
        else:
            assert cp.ts_pct == pytest.approx(expected, rel=1e-9)

    @given(stats=stats_stub_st())
    @settings(suppress_health_check=_XDIST)
    def test_game_score_always_float(self, stats: object) -> None:
        """game_score is always float (never None)."""
        cp = build_compared_player(1, stats)  # type: ignore[arg-type]
        assert isinstance(cp.game_score, float)


# ─── Antisymmetry of deltas ──────────────────────────────────────────────────


class TestDeltaAntisymmetry:
    """comparison_deltas(a, b)[m] == -comparison_deltas(b, a)[m]."""

    @given(a=compared_player_st(), b=compared_player_st())
    @settings(suppress_health_check=_XDIST)
    def test_antisymmetry(self, a: ComparedPlayer, b: ComparedPlayer) -> None:
        d_ab = comparison_deltas(a, b)
        d_ba = comparison_deltas(b, a)
        for metric in COMPARISON_METRICS:
            v_ab = d_ab[metric]
            v_ba = d_ba[metric]
            if v_ab is None:
                assert v_ba is None, f"{metric}: None mismatch"
            else:
                assert v_ab == pytest.approx(-v_ba, abs=1e-9), (  # type: ignore[arg-type]
                    f"{metric}: {v_ab} != -{v_ba}"
                )


# ─── Identity of deltas ──────────────────────────────────────────────────────


class TestDeltaIdentity:
    """comparison_deltas(a, a)[m] == 0 for all non-None metrics."""

    @given(a=compared_player_st())
    @settings(suppress_health_check=_XDIST)
    def test_self_comparison_all_zero(self, a: ComparedPlayer) -> None:
        deltas = comparison_deltas(a, a)
        for metric, val in deltas.items():
            if val is not None:
                assert val == pytest.approx(0.0, abs=1e-9), (
                    f"{metric}: expected 0, got {val}"
                )


# ─── Edge summary sum invariant ──────────────────────────────────────────────


class TestEdgeSumInvariant:
    """a_leads + b_leads + ties + unavailable == total always."""

    @given(a=compared_player_st(), b=compared_player_st())
    @settings(suppress_health_check=_XDIST)
    def test_sum_equals_total(self, a: ComparedPlayer, b: ComparedPlayer) -> None:
        deltas = comparison_deltas(a, b)
        edges = comparison_edges(deltas)
        assert (
            edges.a_leads + edges.b_leads + edges.ties + edges.unavailable
            == edges.total
        )

    @given(a=compared_player_st(), b=compared_player_st())
    @settings(suppress_health_check=_XDIST)
    def test_total_equals_metrics_count(
        self,
        a: ComparedPlayer,
        b: ComparedPlayer,
    ) -> None:
        deltas = comparison_deltas(a, b)
        edges = comparison_edges(deltas)
        assert edges.total == len(COMPARISON_METRICS)


# ─── stat_leader range constraint ────────────────────────────────────────────


class TestStatLeaderRange:
    """stat_leader returns only valid player_ids or None."""

    @given(a=compared_player_st(), b=compared_player_st())
    @settings(suppress_health_check=_XDIST)
    def test_leader_in_valid_set(self, a: ComparedPlayer, b: ComparedPlayer) -> None:
        valid = {a.player_id, b.player_id, None}
        for metric in COMPARISON_METRICS:
            result = stat_leader(a, b, metric)
            assert result in valid, f"{metric}: {result} not in {valid}"
