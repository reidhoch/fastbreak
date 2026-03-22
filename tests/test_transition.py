"""Tests for the transition classification module."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st
from pytest_mock import MockerFixture

from fastbreak.models.play_by_play import PlayByPlayAction
from fastbreak.transition import (
    Classification,
    TransitionAnalysis,
    TransitionPossession,
    Trigger,
    classify_possessions,
    get_transition_stats,
    transition_efficiency,
    transition_frequency,
)
from tests.strategies import XDIST_SUPPRESS as _XDIST

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_SHOT_ACTION_TYPES = frozenset(
    ("2pt", "3pt", "Made Shot", "Missed Shot", "Free Throw", "Heave")
)


def _make_action(
    *,
    action_type: str = "2pt",
    sub_type: str = "",
    shot_result: str = "",
    is_field_goal: int | None = None,
    team_id: int = 100,
    period: int = 1,
    clock: str = "PT10M00.00S",
    shot_value: int = 0,
    description: str = "",
    action_number: int = 1,
) -> PlayByPlayAction:
    """Build a minimal PlayByPlayAction for transition tests."""
    if is_field_goal is None:
        is_field_goal = 1 if action_type in _SHOT_ACTION_TYPES else 0

    return PlayByPlayAction(
        actionNumber=action_number,
        clock=clock,
        period=period,
        teamId=team_id,
        teamTricode="TST",
        personId=0,
        playerName="Test Player",
        playerNameI="T. Player",
        xLegacy=0,
        yLegacy=0,
        shotDistance=0,
        shotResult=shot_result,
        isFieldGoal=is_field_goal,
        scoreHome="0",
        scoreAway="0",
        pointsTotal=0,
        location="h",
        description=description,
        actionType=action_type,
        subType=sub_type,
        videoAvailable=0,
        shotValue=shot_value,
        actionId=action_number,
    )


def _make_possession(
    *,
    classification: Classification = "transition",
    trigger: Trigger = "turnover",
    points_scored: int = 0,
    team_id: int = 100,
    period: int = 1,
) -> TransitionPossession:
    """Build a TransitionPossession for frequency/efficiency tests."""
    return TransitionPossession(
        team_id=team_id,
        period=period,
        game_clock=600.0,
        elapsed=5.0,
        classification=classification,
        trigger=trigger,
        actions=(),
        points_scored=points_scored,
    )


# ---------------------------------------------------------------------------
# TestDataclassFrozenSlots
# ---------------------------------------------------------------------------


class TestDataclassFrozenSlots:
    """Verify that all transition dataclasses are frozen and use slots."""

    def test_transition_possession_frozen(self):
        poss = _make_possession()
        with pytest.raises(AttributeError):
            poss.team_id = 999  # type: ignore[misc]

    def test_transition_possession_slots(self):
        poss = _make_possession()
        assert not hasattr(poss, "__dict__")

    def test_transition_summary_frozen(self):
        summary = transition_frequency([_make_possession()])
        with pytest.raises(AttributeError):
            summary.total_possessions = 99  # type: ignore[misc]

    def test_transition_summary_slots(self):
        summary = transition_frequency([_make_possession()])
        assert not hasattr(summary, "__dict__")

    def test_transition_efficiency_frozen(self):
        eff = transition_efficiency([_make_possession()])
        with pytest.raises(AttributeError):
            eff.transition_points = 99  # type: ignore[misc]

    def test_transition_efficiency_slots(self):
        eff = transition_efficiency([_make_possession()])
        assert not hasattr(eff, "__dict__")

    def test_transition_analysis_frozen(self):
        analysis = TransitionAnalysis(
            game_id="0022500571",
            possessions=(),
            summary=transition_frequency([]),
            efficiency=transition_efficiency([]),
        )
        with pytest.raises(AttributeError):
            analysis.game_id = "other"  # type: ignore[misc]

    def test_transition_analysis_slots(self):
        analysis = TransitionAnalysis(
            game_id="0022500571",
            possessions=(),
            summary=transition_frequency([]),
            efficiency=transition_efficiency([]),
        )
        assert not hasattr(analysis, "__dict__")


# ---------------------------------------------------------------------------
# TestClassifyPossessions
# ---------------------------------------------------------------------------


class TestClassifyPossessions:
    """Tests for classify_possessions()."""

    def test_empty_actions(self):
        """Empty action list returns empty possession list."""
        assert classify_possessions([]) == []

    def test_single_made_fg(self):
        """A single made 2pt creates exactly one possession."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 1

    def test_fast_shot_is_transition(self):
        """A shot 3s after a turnover is classified as transition."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M57.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert result[-1].classification == "transition"

    def test_slow_shot_is_halfcourt(self):
        """A shot 12s after a turnover is classified as halfcourt."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M48.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert result[-1].classification == "halfcourt"

    def test_exactly_at_window_is_transition(self):
        """A shot at exactly 8.0s is transition (boundary is <=)."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M52.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert result[-1].classification == "transition"
        assert result[-1].elapsed == pytest.approx(8.0)

    def test_just_over_window_is_halfcourt(self):
        """A shot at 8.01s is halfcourt (just past the boundary)."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M51.99S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert result[-1].classification == "halfcourt"
        assert result[-1].elapsed == pytest.approx(8.01)

    def test_custom_window(self):
        """Custom window=5.0 classifies a 6s possession as halfcourt."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M54.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions, transition_window=5.0)
        assert result[-1].classification == "halfcourt"

    def test_default_window_is_8(self):
        """Default window is 8s: a 7.9s possession is transition."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M52.10S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert result[-1].classification == "transition"
        assert result[-1].elapsed == pytest.approx(7.9)

    def test_made_fg_triggers_new_possession(self):
        """A made field goal triggers a new possession."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M50.00S",
                shot_result="Missed",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2

    def test_three_pointer_triggers_new_possession(self):
        """A made 3pt triggers a new possession with trigger='made_fg'."""
        actions = [
            _make_action(
                action_type="3pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=3,
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M50.00S",
                shot_result="Missed",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2
        assert result[1].trigger == "made_fg"

    def test_turnover_triggers_new_possession(self):
        """A turnover triggers a new possession."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M50.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2

    def test_defensive_rebound_triggers_new_possession(self):
        """A defensive rebound (team change) triggers a new possession."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
            _make_action(
                action_type="rebound",
                sub_type="",
                team_id=200,
                clock="PT09M58.00S",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2

    def test_offensive_rebound_no_new_possession(self):
        """An offensive rebound (same team) does NOT trigger a new possession."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
            _make_action(
                action_type="rebound",
                sub_type="offensive",
                team_id=100,
                clock="PT09M58.00S",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 1

    def test_missed_fg_no_trigger(self):
        """A missed shot alone does not trigger a possession change."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 1

    def test_trigger_field_made_fg(self):
        """Second possession's trigger is 'made_fg' after a made basket."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M50.00S",
                shot_result="Missed",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert result[1].trigger == "made_fg"

    def test_trigger_field_turnover(self):
        """Second possession's trigger is 'turnover' after a turnover."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M50.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert result[1].trigger == "turnover"

    def test_trigger_field_defensive_rebound(self):
        """Second possession's trigger is 'defensive_rebound' after a def reb."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
            _make_action(
                action_type="rebound",
                sub_type="",
                team_id=200,
                clock="PT09M58.00S",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert result[1].trigger == "defensive_rebound"

    def test_start_of_period_trigger(self):
        """First possession of a period has trigger='start_of_period'."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert result[0].trigger == "start_of_period"

    def test_period_boundary_new_possession(self):
        """Actions in a new period create a new possession with start_of_period."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                period=1,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                period=2,
                clock="PT12M00.00S",
                shot_result="Missed",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2
        assert result[1].trigger == "start_of_period"

    def test_team_id_preserved(self):
        """Possession team_id matches the offensive team."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert result[0].team_id == 100

    def test_period_preserved(self):
        """Possession period matches the action period."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                period=2,
                clock="PT10M00.00S",
                shot_result="Missed",
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert result[0].period == 2

    def test_points_scored_2pt(self):
        """A made 2pt gives points_scored=2."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert result[0].points_scored == 2

    def test_points_scored_3pt(self):
        """A made 3pt gives points_scored=3."""
        actions = [
            _make_action(
                action_type="3pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=3,
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert result[0].points_scored == 3

    def test_points_scored_zero_on_miss(self):
        """A missed shot gives points_scored=0."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Missed",
                shot_value=2,
                action_number=1,
            ),
        ]
        result = classify_possessions(actions)
        assert result[0].points_scored == 0

    def test_actions_tuple_correct(self):
        """Each possession contains exactly the right actions."""
        actions = [
            _make_action(
                action_type="Jump Ball",
                team_id=100,
                clock="PT12M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=2,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M57.00S",
                shot_result="Missed",
                action_number=3,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result[0].actions) == 2  # Jump Ball + turnover
        assert len(result[1].actions) == 1  # shot

    def test_team_id_zero_skipped(self):
        """Actions with teamId=0 (game events) are skipped entirely."""
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
            _make_action(
                action_type="period",
                team_id=0,
                clock="PT10M00.00S",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        for poss in result:
            assert all(a.teamId != 0 for a in poss.actions)

    def test_back_to_back_made_fgs_team_id_set(self):
        """Back-to-back made FGs with no intervening action: team_id is correct.

        After the first FG, current_team_id resets to 0.  The second FG must
        correctly set team_id via the ``== 0`` guard before finalize.
        """
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M50.00S",
                shot_result="Made",
                shot_value=2,
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2
        assert result[0].team_id == 100
        assert result[1].team_id == 200

    def test_turnover_then_immediate_made_fg_team_id_set(self):
        """Turnover followed immediately by made FG: team_id is correct.

        After the turnover, current_team_id resets to 0.  The made FG must
        correctly set team_id via the ``== 0`` guard.
        """
        actions = [
            _make_action(
                action_type="turnover",
                team_id=100,
                clock="PT10M00.00S",
                action_number=1,
            ),
            _make_action(
                action_type="2pt",
                team_id=200,
                clock="PT09M55.00S",
                shot_result="Made",
                shot_value=2,
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2
        assert result[0].team_id == 100
        assert result[1].team_id == 200

    def test_made_fg_then_immediate_turnover_team_id_set(self):
        """Made FG followed immediately by turnover: team_id is correct.

        After the made FG, current_team_id resets to 0.  The turnover must
        correctly set team_id via the ``== 0`` guard before finalizing.
        """
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
            _make_action(
                action_type="turnover",
                team_id=200,
                clock="PT09M55.00S",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2
        assert result[0].team_id == 100
        assert result[1].team_id == 200

    def test_made_fg_then_foul_team_id_set(self):
        """Made FG followed by a foul (regular action): team_id is correct.

        After the made FG, current_team_id resets to 0.  The foul (which is
        a regular action, not a possession-ending event) must correctly set
        team_id via the ``== 0`` guard.
        """
        actions = [
            _make_action(
                action_type="2pt",
                team_id=100,
                clock="PT10M00.00S",
                shot_result="Made",
                shot_value=2,
                action_number=1,
            ),
            _make_action(
                action_type="foul",
                team_id=200,
                clock="PT09M55.00S",
                action_number=2,
            ),
        ]
        result = classify_possessions(actions)
        assert len(result) == 2
        assert result[1].team_id == 200


# ---------------------------------------------------------------------------
# TestTransitionFrequency
# ---------------------------------------------------------------------------


class TestTransitionFrequency:
    """Tests for transition_frequency()."""

    def test_empty_returns_none_pcts(self):
        """Zero possessions gives None for both percentages."""
        summary = transition_frequency([])
        assert summary.total_possessions == 0
        assert summary.transition_pct is None
        assert summary.halfcourt_pct is None

    def test_all_transition(self):
        """All transition → pct=1.0, hc_pct=0.0."""
        poss = [_make_possession(classification="transition") for _ in range(3)]
        summary = transition_frequency(poss)
        assert summary.transition_pct == pytest.approx(1.0)
        assert summary.halfcourt_pct == pytest.approx(0.0)

    def test_all_halfcourt(self):
        """All halfcourt → trans_pct=0.0, hc_pct=1.0."""
        poss = [_make_possession(classification="halfcourt") for _ in range(3)]
        summary = transition_frequency(poss)
        assert summary.transition_pct == pytest.approx(0.0)
        assert summary.halfcourt_pct == pytest.approx(1.0)

    def test_mixed_exact(self):
        """2 transition + 3 halfcourt → 0.4 and 0.6."""
        poss = [
            _make_possession(classification="transition"),
            _make_possession(classification="transition"),
            _make_possession(classification="halfcourt"),
            _make_possession(classification="halfcourt"),
            _make_possession(classification="halfcourt"),
        ]
        summary = transition_frequency(poss)
        assert summary.transition_pct == pytest.approx(0.4)
        assert summary.halfcourt_pct == pytest.approx(0.6)

    def test_total_equals_sum(self):
        """total_possessions always equals transition + halfcourt count."""
        poss = [
            _make_possession(classification="transition"),
            _make_possession(classification="halfcourt"),
            _make_possession(classification="halfcourt"),
        ]
        summary = transition_frequency(poss)
        assert (
            summary.total_possessions
            == summary.transition_possessions + summary.halfcourt_possessions
        )


# ---------------------------------------------------------------------------
# TestTransitionEfficiency
# ---------------------------------------------------------------------------


class TestTransitionEfficiency:
    """Tests for transition_efficiency()."""

    def test_empty_returns_none_ppp(self):
        """No possessions → both PPP are None."""
        eff = transition_efficiency([])
        assert eff.transition_ppp is None
        assert eff.halfcourt_ppp is None

    def test_transition_ppp_exact(self):
        """4 points / 2 transition possessions → PPP 2.0."""
        poss = [
            _make_possession(classification="transition", points_scored=2),
            _make_possession(classification="transition", points_scored=2),
        ]
        eff = transition_efficiency(poss)
        assert eff.transition_ppp == pytest.approx(2.0)

    def test_halfcourt_ppp_exact(self):
        """6 points / 3 halfcourt possessions → PPP 2.0."""
        poss = [
            _make_possession(classification="halfcourt", points_scored=2),
            _make_possession(classification="halfcourt", points_scored=2),
            _make_possession(classification="halfcourt", points_scored=2),
        ]
        eff = transition_efficiency(poss)
        assert eff.halfcourt_ppp == pytest.approx(2.0)

    def test_zero_points_is_zero_not_none(self):
        """0 points / 2 possessions → PPP 0.0, not None."""
        poss = [
            _make_possession(classification="transition", points_scored=0),
            _make_possession(classification="transition", points_scored=0),
        ]
        eff = transition_efficiency(poss)
        assert eff.transition_ppp == pytest.approx(0.0)

    def test_no_transition_gives_none_ppp(self):
        """0 transition possessions → transition_ppp is None."""
        poss = [_make_possession(classification="halfcourt", points_scored=2)]
        eff = transition_efficiency(poss)
        assert eff.transition_ppp is None

    def test_no_halfcourt_gives_none_ppp(self):
        """0 halfcourt possessions → halfcourt_ppp is None."""
        poss = [_make_possession(classification="transition", points_scored=2)]
        eff = transition_efficiency(poss)
        assert eff.halfcourt_ppp is None

    def test_points_fields_correct(self):
        """Point totals are summed correctly per classification."""
        poss = [
            _make_possession(classification="transition", points_scored=3),
            _make_possession(classification="transition", points_scored=2),
            _make_possession(classification="halfcourt", points_scored=2),
        ]
        eff = transition_efficiency(poss)
        assert eff.transition_points == 5
        assert eff.halfcourt_points == 2
        assert eff.transition_possessions == 2
        assert eff.halfcourt_possessions == 1

    def test_single_transition_possession_ppp(self):
        """Exactly 1 transition possession still computes PPP (not None).

        Kills boundary mutant where ``trans_count > 0`` is mutated to ``> 1``.
        """
        poss = [_make_possession(classification="transition", points_scored=3)]
        eff = transition_efficiency(poss)
        assert eff.transition_ppp == pytest.approx(3.0)

    def test_single_halfcourt_possession_ppp(self):
        """Exactly 1 halfcourt possession still computes PPP (not None).

        Kills boundary mutant where ``half_count > 0`` is mutated to ``> 1``.
        """
        poss = [_make_possession(classification="halfcourt", points_scored=2)]
        eff = transition_efficiency(poss)
        assert eff.halfcourt_ppp == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# TestGetTransitionStats
# ---------------------------------------------------------------------------


class TestGetTransitionStats:
    """Tests for get_transition_stats() async wrapper."""

    async def test_calls_get_play_by_play(self, make_pbp_client):
        """get_transition_stats calls the API with the correct game_id."""
        client = make_pbp_client([])
        await get_transition_stats(client, "0022500571")
        client.get.assert_called_once()
        endpoint = client.get.call_args[0][0]
        assert endpoint.game_id == "0022500571"

    async def test_returns_transition_analysis(self, make_pbp_client):
        """get_transition_stats returns a TransitionAnalysis."""
        client = make_pbp_client([])
        result = await get_transition_stats(client, "0022500571")
        assert isinstance(result, TransitionAnalysis)

    async def test_game_id_preserved(self, make_pbp_client):
        """The game_id is stored on the result."""
        client = make_pbp_client([])
        result = await get_transition_stats(client, "0022500571")
        assert result.game_id == "0022500571"

    async def test_custom_window_forwarded(
        self, mocker: MockerFixture, make_pbp_client
    ):
        """transition_window kwarg is forwarded to classify_possessions."""
        mock_classify = mocker.patch(
            "fastbreak.transition.classify_possessions",
            return_value=[],
        )
        client = make_pbp_client([])
        await get_transition_stats(client, "0022500571", transition_window=5.0)
        mock_classify.assert_called_once()
        assert mock_classify.call_args.kwargs["transition_window"] == 5.0


# ---------------------------------------------------------------------------
# Hypothesis property-based tests
# ---------------------------------------------------------------------------


_action_st = st.builds(
    _make_action,
    action_type=st.sampled_from(["2pt", "3pt", "turnover", "rebound", "foul"]),
    sub_type=st.sampled_from(["", "offensive"]),
    shot_result=st.sampled_from(["", "Made", "Missed"]),
    team_id=st.sampled_from([100, 200]),
    period=st.integers(min_value=1, max_value=4),
    clock=st.integers(min_value=0, max_value=720).map(
        lambda s: f"PT{s // 60:02d}M{s % 60:02d}.00S"
    ),
    shot_value=st.sampled_from([0, 2, 3]),
    action_number=st.integers(min_value=1, max_value=10000),
)


class TestClassifyPossessionsProperties:
    """Hypothesis property-based tests for classify_possessions."""

    @given(st.lists(_action_st, max_size=30))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_classification_always_valid(self, actions):
        """Every classification is 'transition' or 'halfcourt'."""
        result = classify_possessions(actions)
        for poss in result:
            assert poss.classification in {"transition", "halfcourt"}

    @given(st.lists(_action_st, max_size=30))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_total_equals_transition_plus_halfcourt(self, actions):
        """total always equals transition + halfcourt count."""
        possessions = classify_possessions(actions)
        summary = transition_frequency(possessions)
        assert (
            summary.total_possessions
            == summary.transition_possessions + summary.halfcourt_possessions
        )

    @given(st.lists(_action_st, min_size=1, max_size=30))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_pcts_sum_to_one_when_nonempty(self, actions):
        """transition_pct + halfcourt_pct = 1.0 when possessions exist."""
        possessions = classify_possessions(actions)
        assume(len(possessions) > 0)
        summary = transition_frequency(possessions)
        assert summary.transition_pct is not None
        assert summary.halfcourt_pct is not None
        assert summary.transition_pct + summary.halfcourt_pct == pytest.approx(1.0)

    @given(st.lists(_action_st, max_size=30))
    @settings(suppress_health_check=[HealthCheck.too_slow, *_XDIST], max_examples=50)
    def test_window_zero_all_halfcourt(self, actions):
        """With window=0, no possession with positive elapsed is transition."""
        result = classify_possessions(actions, transition_window=0.0)
        for poss in result:
            # elapsed <= 0 can occur when the FGA coincides with (or, in
            # non-chronological hypothesis data, precedes) possession start.
            assert poss.classification == "halfcourt" or poss.elapsed <= 0.0
