"""Tests for statistics model validators.

These tests verify that the model validators correctly enforce:
- made shots <= attempted shots
- reboundsTotal == reboundsOffensive + reboundsDefensive
"""

import pytest
from pydantic import ValidationError

from fastbreak.models.common.matchup_statistics import MatchupStatistics
from fastbreak.models.common.player_track_statistics import (
    PlayerTrackStatistics,
    TeamPlayerTrackStatistics,
)
from fastbreak.models.common.traditional_statistics import (
    TraditionalGroupStatistics,
    TraditionalStatistics,
)


class TestTraditionalGroupStatisticsValidation:
    """Tests for TraditionalGroupStatistics model validators."""

    @pytest.fixture
    def valid_data(self):
        """Return valid traditional statistics data."""
        return {
            "minutes": "32:45",
            "fieldGoalsMade": 8,
            "fieldGoalsAttempted": 15,
            "fieldGoalsPercentage": 0.533,
            "threePointersMade": 2,
            "threePointersAttempted": 5,
            "threePointersPercentage": 0.4,
            "freeThrowsMade": 4,
            "freeThrowsAttempted": 5,
            "freeThrowsPercentage": 0.8,
            "reboundsOffensive": 2,
            "reboundsDefensive": 6,
            "reboundsTotal": 8,
            "assists": 5,
            "steals": 1,
            "blocks": 0,
            "turnovers": 2,
            "foulsPersonal": 3,
            "points": 22,
        }

    def test_valid_data_passes(self, valid_data):
        """Valid statistics data should pass validation."""
        stats = TraditionalGroupStatistics.model_validate(valid_data)
        assert stats.fieldGoalsMade == 8
        assert stats.reboundsTotal == 8

    def test_field_goals_made_exceeds_attempted_raises(self, valid_data):
        """fieldGoalsMade > fieldGoalsAttempted should raise ValidationError."""
        valid_data["fieldGoalsMade"] = 20
        valid_data["fieldGoalsAttempted"] = 15

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "fieldGoalsMade (20) > fieldGoalsAttempted (15)" in str(errors[0]["msg"])

    def test_three_pointers_made_exceeds_attempted_raises(self, valid_data):
        """threePointersMade > threePointersAttempted should raise ValidationError."""
        valid_data["threePointersMade"] = 10
        valid_data["threePointersAttempted"] = 5

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "threePointersMade (10) > threePointersAttempted (5)" in str(
            errors[0]["msg"]
        )

    def test_free_throws_made_exceeds_attempted_raises(self, valid_data):
        """freeThrowsMade > freeThrowsAttempted should raise ValidationError."""
        valid_data["freeThrowsMade"] = 8
        valid_data["freeThrowsAttempted"] = 5

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "freeThrowsMade (8) > freeThrowsAttempted (5)" in str(errors[0]["msg"])

    def test_rebounds_total_mismatch_raises(self, valid_data):
        """reboundsTotal != offensive + defensive should raise ValidationError."""
        valid_data["reboundsOffensive"] = 2
        valid_data["reboundsDefensive"] = 6
        valid_data["reboundsTotal"] = 10  # Should be 8

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "reboundsTotal (10) != reboundsOffensive + reboundsDefensive (8)" in str(
            errors[0]["msg"]
        )

    def test_zero_attempts_with_zero_made_valid(self, valid_data):
        """Zero made with zero attempted is valid."""
        valid_data["fieldGoalsMade"] = 0
        valid_data["fieldGoalsAttempted"] = 0
        valid_data["fieldGoalsPercentage"] = 0.0

        stats = TraditionalGroupStatistics.model_validate(valid_data)
        assert stats.fieldGoalsMade == 0
        assert stats.fieldGoalsAttempted == 0

    def test_all_made_equals_attempted_valid(self, valid_data):
        """Made == attempted (perfect shooting) is valid."""
        valid_data["freeThrowsMade"] = 5
        valid_data["freeThrowsAttempted"] = 5
        valid_data["freeThrowsPercentage"] = 1.0

        stats = TraditionalGroupStatistics.model_validate(valid_data)
        assert stats.freeThrowsMade == 5
        assert stats.freeThrowsAttempted == 5


class TestTraditionalStatisticsValidation:
    """Tests for TraditionalStatistics (inherits from TraditionalGroupStatistics)."""

    @pytest.fixture
    def valid_data(self):
        """Return valid traditional statistics data with plusMinusPoints."""
        return {
            "minutes": "32:45",
            "fieldGoalsMade": 8,
            "fieldGoalsAttempted": 15,
            "fieldGoalsPercentage": 0.533,
            "threePointersMade": 2,
            "threePointersAttempted": 5,
            "threePointersPercentage": 0.4,
            "freeThrowsMade": 4,
            "freeThrowsAttempted": 5,
            "freeThrowsPercentage": 0.8,
            "reboundsOffensive": 2,
            "reboundsDefensive": 6,
            "reboundsTotal": 8,
            "assists": 5,
            "steals": 1,
            "blocks": 0,
            "turnovers": 2,
            "foulsPersonal": 3,
            "points": 22,
            "plusMinusPoints": 12.5,
        }

    def test_inherits_validators(self, valid_data):
        """TraditionalStatistics should inherit validators from parent."""
        valid_data["fieldGoalsMade"] = 20  # Invalid: exceeds attempted

        with pytest.raises(ValidationError) as exc_info:
            TraditionalStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "fieldGoalsMade (20) > fieldGoalsAttempted (15)" in str(errors[0]["msg"])

    def test_negative_plus_minus_valid(self, valid_data):
        """Negative plusMinusPoints is valid."""
        valid_data["plusMinusPoints"] = -15.0

        stats = TraditionalStatistics.model_validate(valid_data)
        assert stats.plusMinusPoints == -15.0


class TestPlayerTrackStatisticsValidation:
    """Tests for PlayerTrackStatistics model validators."""

    @pytest.fixture
    def valid_data(self):
        """Return valid player track statistics data."""
        return {
            "minutes": "28:30",
            "speed": 4.5,
            "distance": 2.3,
            "reboundChancesOffensive": 3,
            "reboundChancesDefensive": 8,
            "reboundChancesTotal": 11,
            "touches": 45,
            "secondaryAssists": 2,
            "freeThrowAssists": 1,
            "passes": 30,
            "assists": 5,
            "contestedFieldGoalsMade": 3,
            "contestedFieldGoalsAttempted": 8,
            "contestedFieldGoalPercentage": 0.375,
            "uncontestedFieldGoalsMade": 5,
            "uncontestedFieldGoalsAttempted": 7,
            "uncontestedFieldGoalsPercentage": 0.714,
            "fieldGoalPercentage": 0.533,
            "defendedAtRimFieldGoalsMade": 2,
            "defendedAtRimFieldGoalsAttempted": 4,
            "defendedAtRimFieldGoalPercentage": 0.5,
        }

    def test_valid_data_passes(self, valid_data):
        """Valid player track statistics should pass validation."""
        stats = PlayerTrackStatistics.model_validate(valid_data)
        assert stats.contestedFieldGoalsMade == 3
        assert stats.speed == 4.5

    def test_contested_fg_made_exceeds_attempted_raises(self, valid_data):
        """contestedFieldGoalsMade > attempted should raise ValidationError."""
        valid_data["contestedFieldGoalsMade"] = 10
        valid_data["contestedFieldGoalsAttempted"] = 8

        with pytest.raises(ValidationError) as exc_info:
            PlayerTrackStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "contestedFieldGoalsMade (10) > contestedFieldGoalsAttempted (8)" in str(
            errors[0]["msg"]
        )

    def test_uncontested_fg_made_exceeds_attempted_raises(self, valid_data):
        """uncontestedFieldGoalsMade > attempted should raise ValidationError."""
        valid_data["uncontestedFieldGoalsMade"] = 10
        valid_data["uncontestedFieldGoalsAttempted"] = 7

        with pytest.raises(ValidationError) as exc_info:
            PlayerTrackStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "uncontestedFieldGoalsMade (10) > uncontestedFieldGoalsAttempted (7)"
            in str(errors[0]["msg"])
        )

    def test_defended_at_rim_fg_made_exceeds_attempted_raises(self, valid_data):
        """defendedAtRimFieldGoalsMade > attempted should raise ValidationError."""
        valid_data["defendedAtRimFieldGoalsMade"] = 6
        valid_data["defendedAtRimFieldGoalsAttempted"] = 4

        with pytest.raises(ValidationError) as exc_info:
            PlayerTrackStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "defendedAtRimFieldGoalsMade (6) > defendedAtRimFieldGoalsAttempted (4)"
            in str(errors[0]["msg"])
        )

    def test_rebound_chances_total_mismatch_allowed(self, valid_data):
        """reboundChancesTotal mismatch is allowed (API data quality issue)."""
        # This reflects real NBA API behavior where total != offensive + defensive
        valid_data["reboundChancesOffensive"] = 3
        valid_data["reboundChancesDefensive"] = 8
        valid_data["reboundChancesTotal"] = 10  # Should be 11, but API is inconsistent

        # Should NOT raise - we don't validate this due to API data issues
        stats = PlayerTrackStatistics.model_validate(valid_data)
        assert stats.reboundChancesTotal == 10


class TestTeamPlayerTrackStatisticsValidation:
    """Tests for TeamPlayerTrackStatistics model validators."""

    @pytest.fixture
    def valid_data(self):
        """Return valid team player track statistics data."""
        return {
            "minutes": "240:00",
            "distance": 45.6,
            "reboundChancesOffensive": 15,
            "reboundChancesDefensive": 40,
            "reboundChancesTotal": 55,
            "touches": 350,
            "secondaryAssists": 12,
            "freeThrowAssists": 5,
            "passes": 280,
            "assists": 25,
            "contestedFieldGoalsMade": 20,
            "contestedFieldGoalsAttempted": 50,
            "contestedFieldGoalPercentage": 0.4,
            "uncontestedFieldGoalsMade": 30,
            "uncontestedFieldGoalsAttempted": 40,
            "uncontestedFieldGoalsPercentage": 0.75,
            "fieldGoalPercentage": 0.556,
            "defendedAtRimFieldGoalsMade": 15,
            "defendedAtRimFieldGoalsAttempted": 25,
            "defendedAtRimFieldGoalPercentage": 0.6,
        }

    def test_valid_data_passes(self, valid_data):
        """Valid team player track statistics should pass validation."""
        stats = TeamPlayerTrackStatistics.model_validate(valid_data)
        assert stats.contestedFieldGoalsMade == 20

    def test_contested_fg_made_exceeds_attempted_raises(self, valid_data):
        """contestedFieldGoalsMade > attempted should raise ValidationError."""
        valid_data["contestedFieldGoalsMade"] = 60
        valid_data["contestedFieldGoalsAttempted"] = 50

        with pytest.raises(ValidationError) as exc_info:
            TeamPlayerTrackStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "contestedFieldGoalsMade (60) > contestedFieldGoalsAttempted (50)"
            in str(errors[0]["msg"])
        )


class TestMatchupStatisticsValidation:
    """Tests for MatchupStatistics model validators."""

    @pytest.fixture
    def valid_data(self):
        """Return valid matchup statistics data."""
        return {
            "matchupMinutes": "8:30",
            "matchupMinutesSort": 8.5,
            "partialPossessions": 12.5,
            "percentageDefenderTotalTime": 0.25,
            "percentageOffensiveTotalTime": 0.3,
            "percentageTotalTimeBothOn": 0.2,
            "switchesOn": 3,
            "playerPoints": 6,
            "teamPoints": 10,
            "matchupAssists": 1,
            "matchupPotentialAssists": 2,
            "matchupTurnovers": 0,
            "matchupBlocks": 1,
            "matchupFieldGoalsMade": 2,
            "matchupFieldGoalsAttempted": 5,
            "matchupFieldGoalsPercentage": 0.4,
            "matchupThreePointersMade": 1,
            "matchupThreePointersAttempted": 2,
            "matchupThreePointersPercentage": 0.5,
            "helpBlocks": 0,
            "helpFieldGoalsMade": 1,
            "helpFieldGoalsAttempted": 3,
            "helpFieldGoalsPercentage": 0.333,
            "matchupFreeThrowsMade": 2,
            "matchupFreeThrowsAttempted": 2,
            "shootingFouls": 1,
        }

    def test_valid_data_passes(self, valid_data):
        """Valid matchup statistics should pass validation."""
        stats = MatchupStatistics.model_validate(valid_data)
        assert stats.matchup_field_goals_made == 2
        assert stats.player_points == 6

    def test_matchup_fg_made_exceeds_attempted_raises(self, valid_data):
        """matchup_field_goals_made > attempted should raise ValidationError."""
        valid_data["matchupFieldGoalsMade"] = 8
        valid_data["matchupFieldGoalsAttempted"] = 5

        with pytest.raises(ValidationError) as exc_info:
            MatchupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "matchup_field_goals_made (8) > matchup_field_goals_attempted (5)"
            in str(errors[0]["msg"])
        )

    def test_matchup_three_pointers_made_exceeds_attempted_raises(self, valid_data):
        """matchup_three_pointers_made > attempted should raise ValidationError."""
        valid_data["matchupThreePointersMade"] = 5
        valid_data["matchupThreePointersAttempted"] = 2

        with pytest.raises(ValidationError) as exc_info:
            MatchupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "matchup_three_pointers_made (5) > matchup_three_pointers_attempted (2)"
            in str(errors[0]["msg"])
        )

    def test_help_fg_made_exceeds_attempted_raises(self, valid_data):
        """help_field_goals_made > attempted should raise ValidationError."""
        valid_data["helpFieldGoalsMade"] = 5
        valid_data["helpFieldGoalsAttempted"] = 3

        with pytest.raises(ValidationError) as exc_info:
            MatchupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "help_field_goals_made (5) > help_field_goals_attempted (3)" in str(
            errors[0]["msg"]
        )

    def test_matchup_free_throws_made_exceeds_attempted_raises(self, valid_data):
        """matchup_free_throws_made > attempted should raise ValidationError."""
        valid_data["matchupFreeThrowsMade"] = 4
        valid_data["matchupFreeThrowsAttempted"] = 2

        with pytest.raises(ValidationError) as exc_info:
            MatchupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "matchup_free_throws_made (4) > matchup_free_throws_attempted (2)"
            in str(errors[0]["msg"])
        )

    def test_all_zero_stats_valid(self, valid_data):
        """All zeros for shooting stats is valid (no shots taken in matchup)."""
        valid_data["matchupFieldGoalsMade"] = 0
        valid_data["matchupFieldGoalsAttempted"] = 0
        valid_data["matchupFieldGoalsPercentage"] = 0.0
        valid_data["matchupThreePointersMade"] = 0
        valid_data["matchupThreePointersAttempted"] = 0
        valid_data["matchupThreePointersPercentage"] = 0.0

        stats = MatchupStatistics.model_validate(valid_data)
        assert stats.matchup_field_goals_made == 0
        assert stats.matchup_field_goals_attempted == 0

    def test_three_point_attempted_exceeds_fg_attempted_raises(self, valid_data):
        """matchup_three_pointers_attempted > matchup_field_goals_attempted should raise."""
        valid_data["matchupThreePointersAttempted"] = (
            8  # > matchupFieldGoalsAttempted=5
        )
        valid_data["matchupThreePointersMade"] = 2

        with pytest.raises(ValidationError) as exc_info:
            MatchupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert (
            "matchup_three_pointers_attempted (8) > matchup_field_goals_attempted (5)"
            in str(errors[0]["msg"])
        )

    def test_three_point_made_exceeds_fg_made_raises(self, valid_data):
        """matchup_three_pointers_made > matchup_field_goals_made should raise."""
        valid_data["matchupThreePointersMade"] = 5  # > matchupFieldGoalsMade=2
        valid_data["matchupThreePointersAttempted"] = 5

        with pytest.raises(ValidationError) as exc_info:
            MatchupStatistics.model_validate(valid_data)

        errors = exc_info.value.errors()
        assert "matchup_three_pointers_made (5) > matchup_field_goals_made (2)" in str(
            errors[0]["msg"]
        )


class TestFieldConstraints:
    """Tests for Field(ge=0) and Field(ge=0.0, le=1.0) constraints."""

    def test_negative_count_raises(self):
        """Negative count values should raise ValidationError."""
        data = {
            "minutes": "32:45",
            "fieldGoalsMade": -1,  # Invalid: negative
            "fieldGoalsAttempted": 15,
            "fieldGoalsPercentage": 0.5,
            "threePointersMade": 2,
            "threePointersAttempted": 5,
            "threePointersPercentage": 0.4,
            "freeThrowsMade": 4,
            "freeThrowsAttempted": 5,
            "freeThrowsPercentage": 0.8,
            "reboundsOffensive": 2,
            "reboundsDefensive": 6,
            "reboundsTotal": 8,
            "assists": 5,
            "steals": 1,
            "blocks": 0,
            "turnovers": 2,
            "foulsPersonal": 3,
            "points": 22,
        }

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(data)

        errors = exc_info.value.errors()
        assert any("greater than or equal to 0" in str(e) for e in errors)

    def test_percentage_above_one_raises(self):
        """Percentage > 1.0 should raise ValidationError."""
        data = {
            "minutes": "32:45",
            "fieldGoalsMade": 8,
            "fieldGoalsAttempted": 15,
            "fieldGoalsPercentage": 1.5,  # Invalid: > 1.0
            "threePointersMade": 2,
            "threePointersAttempted": 5,
            "threePointersPercentage": 0.4,
            "freeThrowsMade": 4,
            "freeThrowsAttempted": 5,
            "freeThrowsPercentage": 0.8,
            "reboundsOffensive": 2,
            "reboundsDefensive": 6,
            "reboundsTotal": 8,
            "assists": 5,
            "steals": 1,
            "blocks": 0,
            "turnovers": 2,
            "foulsPersonal": 3,
            "points": 22,
        }

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(data)

        errors = exc_info.value.errors()
        assert any("less than or equal to 1" in str(e) for e in errors)

    def test_negative_percentage_raises(self):
        """Percentage < 0.0 should raise ValidationError."""
        data = {
            "minutes": "32:45",
            "fieldGoalsMade": 8,
            "fieldGoalsAttempted": 15,
            "fieldGoalsPercentage": -0.1,  # Invalid: < 0.0
            "threePointersMade": 2,
            "threePointersAttempted": 5,
            "threePointersPercentage": 0.4,
            "freeThrowsMade": 4,
            "freeThrowsAttempted": 5,
            "freeThrowsPercentage": 0.8,
            "reboundsOffensive": 2,
            "reboundsDefensive": 6,
            "reboundsTotal": 8,
            "assists": 5,
            "steals": 1,
            "blocks": 0,
            "turnovers": 2,
            "foulsPersonal": 3,
            "points": 22,
        }

        with pytest.raises(ValidationError) as exc_info:
            TraditionalGroupStatistics.model_validate(data)

        errors = exc_info.value.errors()
        assert any("greater than or equal to 0" in str(e) for e in errors)


class TestHustleStatisticsValidation:
    """Tests for HustleStatistics.check_partitions model validator."""

    @pytest.fixture
    def valid_data(self):
        """Return valid hustle statistics data with correct partition sums."""
        return {
            "minutes": "28:15",
            "points": 12,
            "contestedShots": 5,
            "contestedShots2pt": 3,
            "contestedShots3pt": 2,
            "deflections": 2,
            "chargesDrawn": 0,
            "screenAssists": 4,
            "screenAssistPoints": 8,
            "looseBallsRecoveredOffensive": 1,
            "looseBallsRecoveredDefensive": 2,
            "looseBallsRecoveredTotal": 3,
            "offensiveBoxOuts": 2,
            "defensiveBoxOuts": 3,
            "boxOutPlayerTeamRebounds": 3,
            "boxOutPlayerRebounds": 2,
            "boxOuts": 5,
        }

    def test_valid_data_passes(self, valid_data):
        """Valid partition sums should pass validation without error."""
        from fastbreak.models.box_score_hustle import HustleStatistics  # noqa: PLC0415

        stats = HustleStatistics.model_validate(valid_data)
        assert stats.contested_shots == 5
        assert (
            stats.contested_shots_2pt + stats.contested_shots_3pt
            == stats.contested_shots
        )

    def test_contested_shots_partition_mismatch_raises(self, valid_data):
        """contested_shots_2pt + contested_shots_3pt != contested_shots should raise."""
        from fastbreak.models.box_score_hustle import HustleStatistics  # noqa: PLC0415

        valid_data["contestedShots2pt"] = 4  # 4 + 2 = 6 != contestedShots=5

        with pytest.raises(ValidationError) as exc_info:
            HustleStatistics.model_validate(valid_data)

        assert "contested_shots_2pt" in str(exc_info.value)
        assert "contested_shots" in str(exc_info.value)

    def test_loose_balls_partition_mismatch_raises(self, valid_data):
        """loose_balls_recovered_offensive + defensive != total should raise."""
        from fastbreak.models.box_score_hustle import HustleStatistics  # noqa: PLC0415

        valid_data["looseBallsRecoveredOffensive"] = 5  # 5 + 2 = 7 != total=3

        with pytest.raises(ValidationError) as exc_info:
            HustleStatistics.model_validate(valid_data)

        assert "loose_balls_recovered" in str(exc_info.value)

    def test_box_outs_partition_mismatch_raises(self, valid_data):
        """offensive_box_outs + defensive_box_outs != box_outs should raise."""
        from fastbreak.models.box_score_hustle import HustleStatistics  # noqa: PLC0415

        valid_data["offensiveBoxOuts"] = 10  # 10 + 3 = 13 != boxOuts=5

        with pytest.raises(ValidationError) as exc_info:
            HustleStatistics.model_validate(valid_data)

        assert "box_outs" in str(exc_info.value)
