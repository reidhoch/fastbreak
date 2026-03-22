"""Tests for fastbreak.hot_hand -- hot hand analysis with Miller-Sanjurjo correction."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st

from fastbreak.hot_hand import (
    HotHandAnalysis,
    HotHandResult,
    ShotSequence,
    StreakCounts,
    count_streaks,
    extract_shot_sequences,
    get_hot_hand_stats,
    hot_hand_result,
    hot_hand_score,
    merge_sequences,
    miller_sanjurjo_bias,
)
from fastbreak.models.play_by_play import PlayByPlayAction
from tests.strategies import XDIST_SUPPRESS as _XDIST

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_SHOT_ACTION_TYPES = frozenset(("2pt", "3pt"))


def _make_action(
    *,
    action_type: str = "2pt",
    shot_result: str = "",
    is_field_goal: int | None = None,
    team_id: int = 100,
    person_id: int = 1,
    player_name: str = "Test Player",
    period: int = 1,
    clock: str = "PT10M00.00S",
    shot_value: int = 2,
    action_number: int = 1,
) -> PlayByPlayAction:
    """Build a minimal PlayByPlayAction for hot hand tests."""
    if is_field_goal is None:
        is_field_goal = 1 if action_type in _SHOT_ACTION_TYPES else 0

    return PlayByPlayAction(
        actionNumber=action_number,
        clock=clock,
        period=period,
        teamId=team_id,
        teamTricode="TST",
        personId=person_id,
        playerName=player_name,
        playerNameI=player_name[0] + ". Player",
        xLegacy=0,
        yLegacy=0,
        shotDistance=0,
        shotResult=shot_result,
        isFieldGoal=is_field_goal,
        scoreHome="0",
        scoreAway="0",
        pointsTotal=0,
        location="h",
        description="",
        actionType=action_type,
        subType="",
        videoAvailable=0,
        shotValue=shot_value,
        actionId=action_number,
    )


# =========================================================================
# Phase 1: Dataclass frozen/slots verification
# =========================================================================


class TestDataclassFrozenSlots:
    """Verify all hot hand dataclasses are frozen and use slots."""

    def test_shot_sequence_frozen(self):
        seq = ShotSequence(player_id=1, player_name="P", team_id=100, shots=())
        with pytest.raises(AttributeError):
            seq.player_id = 999  # type: ignore[misc]

    def test_shot_sequence_slots(self):
        seq = ShotSequence(player_id=1, player_name="P", team_id=100, shots=())
        assert not hasattr(seq, "__dict__")

    def test_streak_counts_frozen(self):
        sc = StreakCounts(
            k=3,
            n=10,
            streak_opportunities=0,
            makes_after_streak=0,
            misses_after_streak=0,
            naive_p=None,
        )
        with pytest.raises(AttributeError):
            sc.k = 5  # type: ignore[misc]

    def test_streak_counts_slots(self):
        sc = StreakCounts(
            k=3,
            n=10,
            streak_opportunities=0,
            makes_after_streak=0,
            misses_after_streak=0,
            naive_p=None,
        )
        assert not hasattr(sc, "__dict__")

    def test_hot_hand_result_frozen(self):
        r = HotHandResult(
            player_id=1,
            player_name="P",
            k=3,
            n=0,
            baseline_p=None,
            naive_p=None,
            bias_correction=None,
            corrected_p=None,
            delta=None,
            streak_opportunities=0,
            score=None,
        )
        with pytest.raises(AttributeError):
            r.k = 5  # type: ignore[misc]

    def test_hot_hand_result_slots(self):
        r = HotHandResult(
            player_id=1,
            player_name="P",
            k=3,
            n=0,
            baseline_p=None,
            naive_p=None,
            bias_correction=None,
            corrected_p=None,
            delta=None,
            streak_opportunities=0,
            score=None,
        )
        assert not hasattr(r, "__dict__")

    def test_hot_hand_analysis_frozen(self):
        a = HotHandAnalysis(game_id="001", sequences=(), results=())
        with pytest.raises(AttributeError):
            a.game_id = "999"  # type: ignore[misc]

    def test_hot_hand_analysis_slots(self):
        a = HotHandAnalysis(game_id="001", sequences=(), results=())
        assert not hasattr(a, "__dict__")


# =========================================================================
# Phase 1: miller_sanjurjo_bias()
# =========================================================================


class TestMillerSanjurjoBias:
    """Tests for the Miller-Sanjurjo bias correction function."""

    def test_returns_none_when_n_equals_k(self):
        """n == k means no post-streak shots exist."""
        assert miller_sanjurjo_bias(p=0.5, n=3, k=3) is None

    def test_returns_none_when_n_less_than_k(self):
        assert miller_sanjurjo_bias(p=0.5, n=2, k=3) is None

    def test_n_one_more_than_k_is_valid(self):
        """n = k + 1: exactly one post-streak position."""
        result = miller_sanjurjo_bias(p=0.5, n=4, k=3)
        assert result is not None
        assert result == pytest.approx(0.5 * 0.5 / 1)  # 0.25

    def test_bias_zero_when_p_zero(self):
        result = miller_sanjurjo_bias(p=0.0, n=20, k=3)
        assert result == pytest.approx(0.0)

    def test_bias_zero_when_p_one(self):
        result = miller_sanjurjo_bias(p=1.0, n=20, k=3)
        assert result == pytest.approx(0.0)

    def test_bias_positive_for_interior_p(self):
        result = miller_sanjurjo_bias(p=0.5, n=20, k=3)
        assert result is not None
        assert result > 0.0

    def test_exact_formula_k1(self):
        """p=0.4, n=21, k=1: 0.4 * 0.6 / 20 = 0.012"""
        result = miller_sanjurjo_bias(p=0.4, n=21, k=1)
        assert result == pytest.approx(0.012)

    def test_exact_formula_k3(self):
        """p=0.5, n=23, k=3: 0.25 / 20 = 0.0125"""
        result = miller_sanjurjo_bias(p=0.5, n=23, k=3)
        assert result == pytest.approx(0.0125)

    def test_bias_maximized_at_p_half(self):
        b_half = miller_sanjurjo_bias(p=0.5, n=20, k=3)
        b_low = miller_sanjurjo_bias(p=0.3, n=20, k=3)
        b_high = miller_sanjurjo_bias(p=0.7, n=20, k=3)
        assert b_half is not None and b_low is not None and b_high is not None
        assert b_half >= b_low
        assert b_half >= b_high


class TestMillerSanjurjoBiasProperties:
    """Hypothesis property-based tests for miller_sanjurjo_bias."""

    @given(
        p=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        n=st.integers(min_value=2, max_value=100),
        k=st.integers(min_value=1, max_value=10),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_bias_non_negative(self, p, n, k):
        result = miller_sanjurjo_bias(p, n, k)
        if result is not None:
            assert result >= 0.0

    @given(
        p=st.floats(min_value=0.01, max_value=0.99, allow_nan=False),
        n=st.integers(min_value=10, max_value=100),
        k=st.integers(min_value=1, max_value=5),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_bias_decreases_with_n(self, p, n, k):
        """Larger n → smaller bias."""
        assume(n > k + 1)
        b1 = miller_sanjurjo_bias(p, n, k)
        b2 = miller_sanjurjo_bias(p, n + 10, k)
        assert b1 is not None and b2 is not None
        assert b2 <= b1 + 1e-9

    @given(
        n=st.integers(min_value=10, max_value=100),
        k=st.integers(min_value=1, max_value=5),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_symmetric_in_p(self, n, k):
        """bias(p) == bias(1-p) because p*(1-p) is symmetric."""
        assume(n > k)
        b1 = miller_sanjurjo_bias(0.3, n, k)
        b2 = miller_sanjurjo_bias(0.7, n, k)
        assert b1 is not None and b2 is not None
        assert b1 == pytest.approx(b2)


# =========================================================================
# Phase 1: count_streaks()
# =========================================================================


class TestCountStreaks:
    """Tests for count_streaks()."""

    def test_k_zero_raises(self):
        with pytest.raises(ValueError, match="k must be >= 1"):
            count_streaks((True, False), k=0)

    def test_k_negative_raises(self):
        with pytest.raises(ValueError, match="k must be >= 1"):
            count_streaks((True, False), k=-1)

    def test_empty_sequence(self):
        result = count_streaks((), k=3)
        assert result.streak_opportunities == 0
        assert result.naive_p is None

    def test_all_makes_k3(self):
        """5 makes, k=3: positions 3 and 4 are opportunities, both makes."""
        shots = (True, True, True, True, True)
        result = count_streaks(shots, k=3)
        assert result.streak_opportunities == 2
        assert result.makes_after_streak == 2
        assert result.misses_after_streak == 0
        assert result.naive_p == pytest.approx(1.0)

    def test_all_misses(self):
        result = count_streaks((False,) * 10, k=3)
        assert result.streak_opportunities == 0
        assert result.naive_p is None

    def test_streak_then_miss(self):
        """TTTf: 1 opportunity, 0 makes."""
        shots = (True, True, True, False)
        result = count_streaks(shots, k=3)
        assert result.streak_opportunities == 1
        assert result.makes_after_streak == 0
        assert result.misses_after_streak == 1
        assert result.naive_p == pytest.approx(0.0)

    def test_streak_then_make(self):
        """TTTT: 1 opportunity, 1 make."""
        shots = (True, True, True, True)
        result = count_streaks(shots, k=3)
        assert result.streak_opportunities == 1
        assert result.makes_after_streak == 1
        assert result.naive_p == pytest.approx(1.0)

    def test_k_equals_1(self):
        """k=1: after every make, check the next shot."""
        shots = (True, False, True, True)
        result = count_streaks(shots, k=1)
        # pos 1: after T → F (miss)
        # pos 2: after F → skip
        # pos 3: after T → T (make)
        assert result.streak_opportunities == 2
        assert result.makes_after_streak == 1
        assert result.misses_after_streak == 1
        assert result.naive_p == pytest.approx(0.5)

    def test_sequence_shorter_than_k(self):
        shots = (True, True)
        result = count_streaks(shots, k=3)
        assert result.streak_opportunities == 0

    def test_exactly_k_shots_all_makes_no_opportunity(self):
        """Exactly k shots: no post-streak position exists."""
        shots = (True, True, True)
        result = count_streaks(shots, k=3)
        assert result.streak_opportunities == 0

    def test_n_field(self):
        shots = (True, False, True, True, False, True)
        result = count_streaks(shots, k=2)
        assert result.n == 6

    def test_k_field(self):
        result = count_streaks((True, True, True, False), k=2)
        assert result.k == 2

    def test_overlapping_streaks(self):
        """TTTFT with k=2: pos 2 (TT→T make), pos 3 (TT→F miss)."""
        shots = (True, True, True, False, True)
        result = count_streaks(shots, k=2)
        assert result.streak_opportunities == 2
        assert result.makes_after_streak == 1
        assert result.misses_after_streak == 1


class TestCountStreaksProperties:
    """Hypothesis property-based tests for count_streaks."""

    @given(shots=st.lists(st.booleans(), max_size=30).map(tuple))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_opportunities_equal_makes_plus_misses(self, shots):
        result = count_streaks(shots, k=3)
        assert (
            result.streak_opportunities
            == result.makes_after_streak + result.misses_after_streak
        )

    @given(shots=st.lists(st.booleans(), max_size=30).map(tuple))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_opportunities_bounded_by_n_minus_k(self, shots):
        k = 3
        result = count_streaks(shots, k=k)
        assert result.streak_opportunities <= max(0, len(shots) - k)

    @given(shots=st.lists(st.booleans(), min_size=4, max_size=30).map(tuple))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_naive_p_in_unit_interval_when_defined(self, shots):
        result = count_streaks(shots, k=3)
        if result.naive_p is not None:
            assert 0.0 <= result.naive_p <= 1.0

    @given(n=st.integers(min_value=1, max_value=30))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_all_false_no_opportunities(self, n):
        result = count_streaks((False,) * n, k=1)
        assert result.streak_opportunities == 0


# =========================================================================
# Phase 1: hot_hand_score()
# =========================================================================


class TestHotHandScore:
    """Tests for hot_hand_score()."""

    def test_below_min_opportunities_returns_none(self):
        assert hot_hand_score(delta=0.05, streak_opportunities=2) is None

    def test_exactly_at_min_opportunities_is_valid(self):
        """Kills < → <= mutation."""
        result = hot_hand_score(delta=0.05, streak_opportunities=3)
        assert result is not None

    def test_one_below_min_returns_none(self):
        """Kills < → <= mutation from the other side."""
        assert hot_hand_score(delta=0.05, streak_opportunities=2) is None

    def test_zero_delta_returns_zero_score(self):
        result = hot_hand_score(delta=0.0, streak_opportunities=10)
        assert result == pytest.approx(0.0)

    def test_positive_delta_positive_score(self):
        result = hot_hand_score(delta=0.05, streak_opportunities=10)
        assert result is not None
        assert result > 0.0

    def test_negative_delta_negative_score(self):
        result = hot_hand_score(delta=-0.05, streak_opportunities=10)
        assert result is not None
        assert result < 0.0

    def test_custom_min_opportunities(self):
        assert (
            hot_hand_score(delta=0.05, streak_opportunities=5, min_opportunities=10)
            is None
        )

    def test_exact_value(self):
        """Pin exact formula: 0.05 * 100 * log2(1 + 10) = 5.0 * log2(11)."""
        from math import log2

        result = hot_hand_score(delta=0.05, streak_opportunities=10)
        assert result == pytest.approx(5.0 * log2(11.0))


class TestHotHandScoreProperties:
    """Hypothesis property-based tests for hot_hand_score."""

    @given(
        delta=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False),
        opps=st.integers(min_value=3, max_value=100),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_antisymmetry(self, delta, opps):
        """Negating delta negates the score."""
        pos = hot_hand_score(delta, opps)
        neg = hot_hand_score(-delta, opps)
        assert pos is not None and neg is not None
        assert neg == pytest.approx(-pos)

    @given(
        delta=st.floats(min_value=0.01, max_value=0.5, allow_nan=False),
        opps1=st.integers(min_value=3, max_value=50),
        opps2=st.integers(min_value=3, max_value=50),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_monotone_in_opportunities(self, delta, opps1, opps2):
        """More opportunities → higher score for positive delta."""
        lo, hi = sorted((opps1, opps2))
        s_lo = hot_hand_score(delta, lo)
        s_hi = hot_hand_score(delta, hi)
        assert s_lo is not None and s_hi is not None
        assert s_hi >= s_lo - 1e-9


# =========================================================================
# Phase 1: hot_hand_result()
# =========================================================================


class TestHotHandResult:
    """Tests for the combined hot_hand_result()."""

    def test_empty_shots(self):
        result = hot_hand_result(1, "P", ())
        assert result.baseline_p is None
        assert result.naive_p is None
        assert result.corrected_p is None
        assert result.delta is None
        assert result.score is None

    def test_player_fields_preserved(self):
        result = hot_hand_result(42, "Stephen Curry", (True,) * 5)
        assert result.player_id == 42
        assert result.player_name == "Stephen Curry"

    def test_all_makes_bias_is_zero(self):
        """All makes: p=1.0, bias = 1*(1-1)/(n-k) = 0."""
        shots = (True,) * 10
        result = hot_hand_result(shots=shots, player_id=1, player_name="P", k=3)
        assert result.baseline_p == pytest.approx(1.0)
        assert result.bias_correction == pytest.approx(0.0)

    def test_mixed_sequence_fields_populated(self):
        shots = (True, True, True, False, True, True, True, True, False, True)
        result = hot_hand_result(1, "P", shots, k=3)
        assert result.n == 10
        assert result.k == 3
        assert result.baseline_p is not None
        assert result.naive_p is not None
        assert result.bias_correction is not None
        assert result.corrected_p is not None
        assert result.delta is not None

    def test_insufficient_opportunities_score_none(self):
        """k=3, 4 shots, 1 opportunity < min 3 → score is None."""
        shots = (True, True, True, False)
        result = hot_hand_result(1, "P", shots, k=3, min_opportunities=3)
        assert result.score is None

    def test_corrected_p_equals_naive_plus_bias(self):
        """Definitional identity: corrected_p == naive_p + bias_correction."""
        shots = (True, True, True, True, False, True, True, True, False, True)
        result = hot_hand_result(1, "P", shots, k=3)
        if result.naive_p is not None and result.bias_correction is not None:
            assert result.corrected_p == pytest.approx(
                result.naive_p + result.bias_correction
            )

    def test_delta_equals_corrected_minus_baseline(self):
        """Definitional identity: delta == corrected_p - baseline_p."""
        shots = (True, True, True, True, False, True, True, True, False, True)
        result = hot_hand_result(1, "P", shots, k=3)
        if result.corrected_p is not None and result.baseline_p is not None:
            assert result.delta == pytest.approx(result.corrected_p - result.baseline_p)


# =========================================================================
# Phase 2: extract_shot_sequences()
# =========================================================================


class TestExtractShotSequences:
    """Tests for extract_shot_sequences()."""

    def test_empty_actions(self):
        assert extract_shot_sequences([]) == []

    def test_single_made_shot(self):
        actions = [_make_action(action_type="2pt", shot_result="Made", person_id=42)]
        result = extract_shot_sequences(actions)
        assert len(result) == 1
        assert result[0].shots == (True,)
        assert result[0].player_id == 42

    def test_single_missed_shot(self):
        actions = [_make_action(action_type="2pt", shot_result="Missed", person_id=42)]
        result = extract_shot_sequences(actions)
        assert result[0].shots == (False,)

    def test_non_field_goal_excluded(self):
        actions = [_make_action(action_type="turnover", person_id=42)]
        assert extract_shot_sequences(actions) == []

    def test_team_id_zero_skipped(self):
        actions = [
            _make_action(
                action_type="2pt", shot_result="Made", team_id=0, person_id=42
            ),
        ]
        assert extract_shot_sequences(actions) == []

    def test_two_players_separate_sequences(self):
        actions = [
            _make_action(
                action_type="2pt",
                shot_result="Made",
                person_id=1,
                player_name="A",
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                shot_result="Missed",
                person_id=2,
                player_name="B",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                shot_result="Made",
                person_id=1,
                player_name="A",
                action_number=3,
            ),
        ]
        result = extract_shot_sequences(actions)
        assert len(result) == 2
        p1 = next(s for s in result if s.player_id == 1)
        p2 = next(s for s in result if s.player_id == 2)
        assert p1.shots == (True, True)
        assert p2.shots == (False,)

    def test_chronological_order_preserved(self):
        actions = [
            _make_action(
                action_type="2pt", shot_result="Made", person_id=1, action_number=1
            ),
            _make_action(
                action_type="2pt", shot_result="Missed", person_id=1, action_number=2
            ),
            _make_action(
                action_type="3pt", shot_result="Made", person_id=1, action_number=3
            ),
        ]
        result = extract_shot_sequences(actions)
        assert result[0].shots == (True, False, True)

    def test_sorted_by_player_id(self):
        actions = [
            _make_action(
                action_type="2pt", shot_result="Made", person_id=99, action_number=1
            ),
            _make_action(
                action_type="2pt", shot_result="Made", person_id=1, action_number=2
            ),
        ]
        result = extract_shot_sequences(actions)
        assert result[0].player_id == 1
        assert result[1].player_id == 99


# =========================================================================
# Phase 2: merge_sequences()
# =========================================================================


class TestMergeSequences:
    """Tests for merge_sequences()."""

    def test_empty_input(self):
        assert merge_sequences([]) == []

    def test_single_game_passthrough(self):
        seq = [
            ShotSequence(player_id=1, player_name="P", team_id=100, shots=(True, False))
        ]
        result = merge_sequences([seq])
        assert len(result) == 1
        assert result[0].shots == (True, False)

    def test_two_games_concatenated(self):
        g1 = [ShotSequence(player_id=1, player_name="P", team_id=100, shots=(True,))]
        g2 = [
            ShotSequence(player_id=1, player_name="P", team_id=100, shots=(False, True))
        ]
        result = merge_sequences([g1, g2])
        assert len(result) == 1
        assert result[0].shots == (True, False, True)

    def test_different_players_kept_separate(self):
        g1 = [
            ShotSequence(player_id=1, player_name="A", team_id=100, shots=(True,)),
            ShotSequence(player_id=2, player_name="B", team_id=100, shots=(False,)),
        ]
        result = merge_sequences([g1])
        assert len(result) == 2

    def test_sorted_by_player_id(self):
        g1 = [ShotSequence(player_id=99, player_name="Z", team_id=100, shots=(True,))]
        g2 = [ShotSequence(player_id=1, player_name="A", team_id=100, shots=(False,))]
        result = merge_sequences([g1, g2])
        assert result[0].player_id == 1
        assert result[1].player_id == 99

    def test_empty_games_ignored(self):
        g1: list[ShotSequence] = []
        g2 = [ShotSequence(player_id=1, player_name="P", team_id=100, shots=(True,))]
        result = merge_sequences([g1, g2])
        assert len(result) == 1


# =========================================================================
# Phase 3: get_hot_hand_stats() async wrapper
# =========================================================================


class TestGetHotHandStats:
    """Tests for get_hot_hand_stats() async wrapper."""

    async def test_calls_get_play_by_play(self, make_pbp_client):
        client = make_pbp_client([])
        await get_hot_hand_stats(client, "0022500571")
        client.get.assert_called_once()

    async def test_returns_hot_hand_analysis(self, make_pbp_client):
        client = make_pbp_client([])
        result = await get_hot_hand_stats(client, "0022500571")
        assert isinstance(result, HotHandAnalysis)

    async def test_game_id_preserved(self, make_pbp_client):
        client = make_pbp_client([])
        result = await get_hot_hand_stats(client, "0022500571")
        assert result.game_id == "0022500571"

    async def test_custom_k_forwarded(self, make_pbp_client):
        actions = [
            _make_action(
                action_type="2pt", shot_result="Made", person_id=1, action_number=i
            )
            for i in range(1, 6)
        ]
        client = make_pbp_client(actions)
        result = await get_hot_hand_stats(client, "0022500571", k=2)
        assert all(r.k == 2 for r in result.results)

    async def test_results_match_sequences(self, make_pbp_client):
        """One result per sequence (per player)."""
        actions = [
            _make_action(
                action_type="2pt", shot_result="Made", person_id=1, action_number=1
            ),
            _make_action(
                action_type="2pt", shot_result="Missed", person_id=2, action_number=2
            ),
        ]
        client = make_pbp_client(actions)
        result = await get_hot_hand_stats(client, "0022500571")
        assert len(result.results) == len(result.sequences)
