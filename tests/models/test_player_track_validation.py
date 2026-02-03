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
