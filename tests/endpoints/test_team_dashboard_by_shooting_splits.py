import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamDashboardByShootingSplits
from fastbreak.models import TeamDashboardByShootingSplitsResponse


class TestTeamDashboardByShootingSplits:
    """Tests for TeamDashboardByShootingSplits endpoint."""

    def test_init_with_defaults(self):
        """TeamDashboardByShootingSplits uses sensible defaults."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_init_with_team_id(self):
        """TeamDashboardByShootingSplits accepts team_id."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamDashboardByShootingSplits accepts custom season."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamDashboardByShootingSplits accepts custom season_type."""
        endpoint = TeamDashboardByShootingSplits(
            team_id=1610612747, season_type="Playoffs"
        )

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """TeamDashboardByShootingSplits accepts custom per_mode."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747, per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_custom_measure_type(self):
        """TeamDashboardByShootingSplits accepts custom measure_type."""
        endpoint = TeamDashboardByShootingSplits(
            team_id=1610612747, measure_type="Advanced"
        )

        assert endpoint.measure_type == "Advanced"

    def test_init_with_last_n_games(self):
        """TeamDashboardByShootingSplits accepts last_n_games filter."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747, last_n_games=10)

        assert endpoint.last_n_games == 10

    def test_init_with_pace_plus_rank(self):
        """TeamDashboardByShootingSplits accepts pace/plus/rank settings."""
        endpoint = TeamDashboardByShootingSplits(
            team_id=1610612747,
            pace_adjust="Y",
            plus_minus="Y",
            rank="Y",
        )

        assert endpoint.pace_adjust == "Y"
        assert endpoint.plus_minus == "Y"
        assert endpoint.rank == "Y"

    def test_init_with_all_optional_params(self):
        """TeamDashboardByShootingSplits accepts all optional parameters."""
        endpoint = TeamDashboardByShootingSplits(
            team_id=1610612747,
            outcome="W",
            location="Home",
            season_segment="Post All-Star",
            date_from="01/01/2024",
            date_to="03/31/2024",
            vs_conference="West",
            vs_division="Pacific",
            game_segment="First Half",
            shot_clock_range="24-22",
        )

        assert endpoint.outcome == "W"
        assert endpoint.location == "Home"
        assert endpoint.season_segment == "Post All-Star"
        assert endpoint.date_from == "01/01/2024"
        assert endpoint.date_to == "03/31/2024"
        assert endpoint.vs_conference == "West"
        assert endpoint.vs_division == "Pacific"
        assert endpoint.game_segment == "First Half"
        assert endpoint.shot_clock_range == "24-22"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamDashboardByShootingSplits(
            team_id=1610612743,
            season="2023-24",
            last_n_games=10,
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["LastNGames"] == "10"

    def test_params_includes_optional_params(self):
        """params() includes optional parameters when set."""
        endpoint = TeamDashboardByShootingSplits(
            team_id=1610612747,
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_params_excludes_none_values(self):
        """params() excludes None optional parameters."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747)

        params = endpoint.params()

        assert "Outcome" not in params
        assert "Location" not in params
        assert "SeasonSegment" not in params

    def test_path_is_correct(self):
        """TeamDashboardByShootingSplits has correct API path."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747)

        assert endpoint.path == "teamdashboardbyshootingsplits"

    def test_response_model_is_correct(self):
        """TeamDashboardByShootingSplits uses TeamDashboardByShootingSplitsResponse model."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747)

        assert endpoint.response_model is TeamDashboardByShootingSplitsResponse

    def test_endpoint_is_frozen(self):
        """TeamDashboardByShootingSplits is immutable (frozen dataclass)."""
        endpoint = TeamDashboardByShootingSplits(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
