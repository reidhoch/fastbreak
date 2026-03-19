"""Tests for PlayerTrackStatistics validation branches."""

import pytest
from pydantic import ValidationError

from fastbreak.models.common.player_track_statistics import (
    PlayerTrackStatistics,
    TeamPlayerTrackStatistics,
)


class TestPlayerTrackStatisticsValidation:
    """Tests for made > attempted validation."""

    def test_valid_statistics(self):
        """Valid stats where made <= attempted pass validation."""
        stats = PlayerTrackStatistics(
            minutes="30:00",
            speed=5.0,
            distance=2.5,
            reboundChancesOffensive=5,
            reboundChancesDefensive=10,
            reboundChancesTotal=15,
            touches=40,
            secondaryAssists=2,
            freeThrowAssists=3,
            passes=15,
            assists=5,
            contestedFieldGoalsMade=8,
            contestedFieldGoalsAttempted=20,
            contestedFieldGoalPercentage=0.4,
            uncontestedFieldGoalsMade=10,
            uncontestedFieldGoalsAttempted=15,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=3,
            defendedAtRimFieldGoalsAttempted=8,
            defendedAtRimFieldGoalPercentage=0.375,
        )
        assert stats.contestedFieldGoalsMade == 8

    def test_contested_made_exceeds_attempted_raises(self):
        """Raises when contestedFieldGoalsMade > contestedFieldGoalsAttempted."""
        with pytest.raises(ValidationError, match="contestedFieldGoalsMade"):
            PlayerTrackStatistics(
                minutes="30:00",
                speed=5.0,
                distance=2.5,
                reboundChancesOffensive=5,
                reboundChancesDefensive=10,
                reboundChancesTotal=15,
                touches=40,
                secondaryAssists=2,
                freeThrowAssists=3,
                passes=15,
                assists=5,
                contestedFieldGoalsMade=25,  # More than attempted
                contestedFieldGoalsAttempted=20,
                contestedFieldGoalPercentage=0.4,
                uncontestedFieldGoalsMade=10,
                uncontestedFieldGoalsAttempted=15,
                uncontestedFieldGoalsPercentage=0.667,
                fieldGoalPercentage=0.5,
                defendedAtRimFieldGoalsMade=3,
                defendedAtRimFieldGoalsAttempted=8,
                defendedAtRimFieldGoalPercentage=0.375,
            )

    def test_uncontested_made_exceeds_attempted_raises(self):
        """Raises when uncontestedFieldGoalsMade > uncontestedFieldGoalsAttempted."""
        with pytest.raises(ValidationError, match="uncontestedFieldGoalsMade"):
            PlayerTrackStatistics(
                minutes="30:00",
                speed=5.0,
                distance=2.5,
                reboundChancesOffensive=5,
                reboundChancesDefensive=10,
                reboundChancesTotal=15,
                touches=40,
                secondaryAssists=2,
                freeThrowAssists=3,
                passes=15,
                assists=5,
                contestedFieldGoalsMade=8,
                contestedFieldGoalsAttempted=20,
                contestedFieldGoalPercentage=0.4,
                uncontestedFieldGoalsMade=20,  # More than attempted
                uncontestedFieldGoalsAttempted=15,
                uncontestedFieldGoalsPercentage=0.667,
                fieldGoalPercentage=0.5,
                defendedAtRimFieldGoalsMade=3,
                defendedAtRimFieldGoalsAttempted=8,
                defendedAtRimFieldGoalPercentage=0.375,
            )

    def test_defended_at_rim_made_exceeds_attempted_raises(self):
        """Raises when defendedAtRimFieldGoalsMade > defendedAtRimFieldGoalsAttempted."""
        with pytest.raises(ValidationError, match="defendedAtRimFieldGoalsMade"):
            PlayerTrackStatistics(
                minutes="30:00",
                speed=5.0,
                distance=2.5,
                reboundChancesOffensive=5,
                reboundChancesDefensive=10,
                reboundChancesTotal=15,
                touches=40,
                secondaryAssists=2,
                freeThrowAssists=3,
                passes=15,
                assists=5,
                contestedFieldGoalsMade=8,
                contestedFieldGoalsAttempted=20,
                contestedFieldGoalPercentage=0.4,
                uncontestedFieldGoalsMade=10,
                uncontestedFieldGoalsAttempted=15,
                uncontestedFieldGoalsPercentage=0.667,
                fieldGoalPercentage=0.5,
                defendedAtRimFieldGoalsMade=15,  # More than attempted
                defendedAtRimFieldGoalsAttempted=8,
                defendedAtRimFieldGoalPercentage=0.375,
            )


class TestTeamPlayerTrackStatisticsValidation:
    """Tests for TeamPlayerTrackStatistics made > attempted validation."""

    def test_valid_team_statistics(self):
        """Valid team stats where made <= attempted pass validation."""
        stats = TeamPlayerTrackStatistics(
            minutes="240:00",
            distance=25.0,
            reboundChancesOffensive=20,
            reboundChancesDefensive=40,
            reboundChancesTotal=60,
            touches=200,
            secondaryAssists=10,
            freeThrowAssists=15,
            passes=75,
            assists=25,
            contestedFieldGoalsMade=30,
            contestedFieldGoalsAttempted=80,
            contestedFieldGoalPercentage=0.375,
            uncontestedFieldGoalsMade=40,
            uncontestedFieldGoalsAttempted=60,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=12,
            defendedAtRimFieldGoalsAttempted=30,
            defendedAtRimFieldGoalPercentage=0.4,
        )
        assert stats.contestedFieldGoalsMade == 30

    def test_team_contested_made_exceeds_attempted_raises(self):
        """Raises when team contestedFieldGoalsMade > contestedFieldGoalsAttempted."""
        with pytest.raises(ValidationError, match="contestedFieldGoalsMade"):
            TeamPlayerTrackStatistics(
                minutes="240:00",
                distance=25.0,
                reboundChancesOffensive=20,
                reboundChancesDefensive=40,
                reboundChancesTotal=60,
                touches=200,
                secondaryAssists=10,
                freeThrowAssists=15,
                passes=75,
                assists=25,
                contestedFieldGoalsMade=100,  # More than attempted
                contestedFieldGoalsAttempted=80,
                contestedFieldGoalPercentage=0.375,
                uncontestedFieldGoalsMade=40,
                uncontestedFieldGoalsAttempted=60,
                uncontestedFieldGoalsPercentage=0.667,
                fieldGoalPercentage=0.5,
                defendedAtRimFieldGoalsMade=12,
                defendedAtRimFieldGoalsAttempted=30,
                defendedAtRimFieldGoalPercentage=0.4,
            )

    def test_team_uncontested_made_exceeds_attempted_raises(self):
        """Raises when team uncontestedFieldGoalsMade > uncontestedFieldGoalsAttempted."""
        with pytest.raises(ValidationError, match="uncontestedFieldGoalsMade"):
            TeamPlayerTrackStatistics(
                minutes="240:00",
                distance=25.0,
                reboundChancesOffensive=20,
                reboundChancesDefensive=40,
                reboundChancesTotal=60,
                touches=200,
                secondaryAssists=10,
                freeThrowAssists=15,
                passes=75,
                assists=25,
                contestedFieldGoalsMade=30,
                contestedFieldGoalsAttempted=80,
                contestedFieldGoalPercentage=0.375,
                uncontestedFieldGoalsMade=80,  # More than attempted
                uncontestedFieldGoalsAttempted=60,
                uncontestedFieldGoalsPercentage=0.667,
                fieldGoalPercentage=0.5,
                defendedAtRimFieldGoalsMade=12,
                defendedAtRimFieldGoalsAttempted=30,
                defendedAtRimFieldGoalPercentage=0.4,
            )

    def test_team_defended_at_rim_made_exceeds_attempted_raises(self):
        """Raises when team defendedAtRimFieldGoalsMade > defendedAtRimFieldGoalsAttempted."""
        with pytest.raises(ValidationError, match="defendedAtRimFieldGoalsMade"):
            TeamPlayerTrackStatistics(
                minutes="240:00",
                distance=25.0,
                reboundChancesOffensive=20,
                reboundChancesDefensive=40,
                reboundChancesTotal=60,
                touches=200,
                secondaryAssists=10,
                freeThrowAssists=15,
                passes=75,
                assists=25,
                contestedFieldGoalsMade=30,
                contestedFieldGoalsAttempted=80,
                contestedFieldGoalPercentage=0.375,
                uncontestedFieldGoalsMade=40,
                uncontestedFieldGoalsAttempted=60,
                uncontestedFieldGoalsPercentage=0.667,
                fieldGoalPercentage=0.5,
                defendedAtRimFieldGoalsMade=50,  # More than attempted
                defendedAtRimFieldGoalsAttempted=30,
                defendedAtRimFieldGoalPercentage=0.4,
            )


class TestPlayerTrackBoundaryMadeEqualsAttempted:
    """Boundary tests where made == attempted (kills > to >= gremlins)."""

    def test_contested_made_equals_attempted_is_valid(self):
        """made == attempted should pass validation (not raise)."""
        stats = PlayerTrackStatistics(
            minutes="30:00",
            speed=5.0,
            distance=2.5,
            reboundChancesOffensive=5,
            reboundChancesDefensive=10,
            reboundChancesTotal=15,
            touches=40,
            secondaryAssists=2,
            freeThrowAssists=3,
            passes=15,
            assists=5,
            contestedFieldGoalsMade=10,  # Equal to attempted
            contestedFieldGoalsAttempted=10,
            contestedFieldGoalPercentage=1.0,
            uncontestedFieldGoalsMade=5,
            uncontestedFieldGoalsAttempted=15,
            uncontestedFieldGoalsPercentage=0.333,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=3,
            defendedAtRimFieldGoalsAttempted=8,
            defendedAtRimFieldGoalPercentage=0.375,
        )
        assert stats.contestedFieldGoalsMade == stats.contestedFieldGoalsAttempted

    def test_uncontested_made_equals_attempted_is_valid(self):
        """made == attempted should pass validation (not raise)."""
        stats = PlayerTrackStatistics(
            minutes="30:00",
            speed=5.0,
            distance=2.5,
            reboundChancesOffensive=5,
            reboundChancesDefensive=10,
            reboundChancesTotal=15,
            touches=40,
            secondaryAssists=2,
            freeThrowAssists=3,
            passes=15,
            assists=5,
            contestedFieldGoalsMade=8,
            contestedFieldGoalsAttempted=20,
            contestedFieldGoalPercentage=0.4,
            uncontestedFieldGoalsMade=15,  # Equal to attempted
            uncontestedFieldGoalsAttempted=15,
            uncontestedFieldGoalsPercentage=1.0,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=3,
            defendedAtRimFieldGoalsAttempted=8,
            defendedAtRimFieldGoalPercentage=0.375,
        )
        assert stats.uncontestedFieldGoalsMade == stats.uncontestedFieldGoalsAttempted

    def test_defended_at_rim_made_equals_attempted_is_valid(self):
        """made == attempted should pass validation (not raise)."""
        stats = PlayerTrackStatistics(
            minutes="30:00",
            speed=5.0,
            distance=2.5,
            reboundChancesOffensive=5,
            reboundChancesDefensive=10,
            reboundChancesTotal=15,
            touches=40,
            secondaryAssists=2,
            freeThrowAssists=3,
            passes=15,
            assists=5,
            contestedFieldGoalsMade=8,
            contestedFieldGoalsAttempted=20,
            contestedFieldGoalPercentage=0.4,
            uncontestedFieldGoalsMade=10,
            uncontestedFieldGoalsAttempted=15,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=8,  # Equal to attempted
            defendedAtRimFieldGoalsAttempted=8,
            defendedAtRimFieldGoalPercentage=1.0,
        )
        assert (
            stats.defendedAtRimFieldGoalsMade == stats.defendedAtRimFieldGoalsAttempted
        )

    def test_all_made_equals_attempted_is_valid(self):
        """All three pairs at boundary should pass validation."""
        stats = PlayerTrackStatistics(
            minutes="30:00",
            speed=5.0,
            distance=2.5,
            reboundChancesOffensive=5,
            reboundChancesDefensive=10,
            reboundChancesTotal=15,
            touches=40,
            secondaryAssists=2,
            freeThrowAssists=3,
            passes=15,
            assists=5,
            contestedFieldGoalsMade=20,
            contestedFieldGoalsAttempted=20,
            contestedFieldGoalPercentage=1.0,
            uncontestedFieldGoalsMade=15,
            uncontestedFieldGoalsAttempted=15,
            uncontestedFieldGoalsPercentage=1.0,
            fieldGoalPercentage=1.0,
            defendedAtRimFieldGoalsMade=8,
            defendedAtRimFieldGoalsAttempted=8,
            defendedAtRimFieldGoalPercentage=1.0,
        )
        assert stats.contestedFieldGoalsMade == stats.contestedFieldGoalsAttempted
        assert stats.uncontestedFieldGoalsMade == stats.uncontestedFieldGoalsAttempted
        assert (
            stats.defendedAtRimFieldGoalsMade == stats.defendedAtRimFieldGoalsAttempted
        )


class TestTeamPlayerTrackBoundaryMadeEqualsAttempted:
    """Boundary tests for TeamPlayerTrackStatistics where made == attempted."""

    def test_team_contested_made_equals_attempted_is_valid(self):
        """made == attempted should pass validation (not raise)."""
        stats = TeamPlayerTrackStatistics(
            minutes="240:00",
            distance=25.0,
            reboundChancesOffensive=20,
            reboundChancesDefensive=40,
            reboundChancesTotal=60,
            touches=200,
            secondaryAssists=10,
            freeThrowAssists=15,
            passes=75,
            assists=25,
            contestedFieldGoalsMade=80,  # Equal to attempted
            contestedFieldGoalsAttempted=80,
            contestedFieldGoalPercentage=1.0,
            uncontestedFieldGoalsMade=40,
            uncontestedFieldGoalsAttempted=60,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=12,
            defendedAtRimFieldGoalsAttempted=30,
            defendedAtRimFieldGoalPercentage=0.4,
        )
        assert stats.contestedFieldGoalsMade == stats.contestedFieldGoalsAttempted

    def test_team_uncontested_made_equals_attempted_is_valid(self):
        """made == attempted should pass validation (not raise)."""
        stats = TeamPlayerTrackStatistics(
            minutes="240:00",
            distance=25.0,
            reboundChancesOffensive=20,
            reboundChancesDefensive=40,
            reboundChancesTotal=60,
            touches=200,
            secondaryAssists=10,
            freeThrowAssists=15,
            passes=75,
            assists=25,
            contestedFieldGoalsMade=30,
            contestedFieldGoalsAttempted=80,
            contestedFieldGoalPercentage=0.375,
            uncontestedFieldGoalsMade=60,  # Equal to attempted
            uncontestedFieldGoalsAttempted=60,
            uncontestedFieldGoalsPercentage=1.0,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=12,
            defendedAtRimFieldGoalsAttempted=30,
            defendedAtRimFieldGoalPercentage=0.4,
        )
        assert stats.uncontestedFieldGoalsMade == stats.uncontestedFieldGoalsAttempted

    def test_team_defended_at_rim_made_equals_attempted_is_valid(self):
        """made == attempted should pass validation (not raise)."""
        stats = TeamPlayerTrackStatistics(
            minutes="240:00",
            distance=25.0,
            reboundChancesOffensive=20,
            reboundChancesDefensive=40,
            reboundChancesTotal=60,
            touches=200,
            secondaryAssists=10,
            freeThrowAssists=15,
            passes=75,
            assists=25,
            contestedFieldGoalsMade=30,
            contestedFieldGoalsAttempted=80,
            contestedFieldGoalPercentage=0.375,
            uncontestedFieldGoalsMade=40,
            uncontestedFieldGoalsAttempted=60,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=30,  # Equal to attempted
            defendedAtRimFieldGoalsAttempted=30,
            defendedAtRimFieldGoalPercentage=1.0,
        )
        assert (
            stats.defendedAtRimFieldGoalsMade == stats.defendedAtRimFieldGoalsAttempted
        )


class TestPlayerTrackValidatorReturnsSelf:
    """Test that the model validator returns self (kills return → None gremlin)."""

    def test_validator_returns_self_for_player(self):
        """check_made_not_exceeding_attempted must return self, not None."""
        stats = PlayerTrackStatistics(
            minutes="30:00",
            speed=5.0,
            distance=2.5,
            reboundChancesOffensive=5,
            reboundChancesDefensive=10,
            reboundChancesTotal=15,
            touches=40,
            secondaryAssists=2,
            freeThrowAssists=3,
            passes=15,
            assists=5,
            contestedFieldGoalsMade=8,
            contestedFieldGoalsAttempted=20,
            contestedFieldGoalPercentage=0.4,
            uncontestedFieldGoalsMade=10,
            uncontestedFieldGoalsAttempted=15,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=3,
            defendedAtRimFieldGoalsAttempted=8,
            defendedAtRimFieldGoalPercentage=0.375,
        )
        # If the validator returned None instead of self, construction would fail
        assert stats is not None
        assert isinstance(stats, PlayerTrackStatistics)
        assert stats.minutes == "30:00"

    def test_validator_returns_self_for_team(self):
        """check_made_not_exceeding_attempted must return self, not None."""
        stats = TeamPlayerTrackStatistics(
            minutes="240:00",
            distance=25.0,
            reboundChancesOffensive=20,
            reboundChancesDefensive=40,
            reboundChancesTotal=60,
            touches=200,
            secondaryAssists=10,
            freeThrowAssists=15,
            passes=75,
            assists=25,
            contestedFieldGoalsMade=30,
            contestedFieldGoalsAttempted=80,
            contestedFieldGoalPercentage=0.375,
            uncontestedFieldGoalsMade=40,
            uncontestedFieldGoalsAttempted=60,
            uncontestedFieldGoalsPercentage=0.667,
            fieldGoalPercentage=0.5,
            defendedAtRimFieldGoalsMade=12,
            defendedAtRimFieldGoalsAttempted=30,
            defendedAtRimFieldGoalPercentage=0.4,
        )
        # If the validator returned None instead of self, construction would fail
        assert stats is not None
        assert isinstance(stats, TeamPlayerTrackStatistics)
        assert stats.minutes == "240:00"
