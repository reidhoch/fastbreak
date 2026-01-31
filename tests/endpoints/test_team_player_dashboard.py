import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamPlayerDashboard
from fastbreak.models import TeamPlayerDashboardResponse


class TestTeamPlayerDashboard:
    """Tests for TeamPlayerDashboard endpoint."""

    def test_init_with_defaults(self):
        """TeamPlayerDashboard uses sensible defaults."""
        endpoint = TeamPlayerDashboard(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamPlayerDashboard accepts team_id."""
        endpoint = TeamPlayerDashboard(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamPlayerDashboard accepts custom season."""
        endpoint = TeamPlayerDashboard(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_per_mode(self):
        """TeamPlayerDashboard accepts custom per_mode."""
        endpoint = TeamPlayerDashboard(team_id=1610612747, per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamPlayerDashboard(
            team_id=1610612743,
            season="2023-24",
            season_type="Playoffs",
            per_mode="Per36",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Playoffs"
        assert params["PerMode"] == "Per36"
        assert params["LeagueID"] == "00"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamPlayerDashboard(team_id=1610612747)

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["Month"] == "0"
        assert params["OpponentTeamID"] == "0"
        assert params["Period"] == "0"
        assert params["LastNGames"] == "0"

    def test_path_is_correct(self):
        """TeamPlayerDashboard has correct API path."""
        endpoint = TeamPlayerDashboard(team_id=1610612747)

        assert endpoint.path == "teamplayerdashboard"

    def test_response_model_is_correct(self):
        """TeamPlayerDashboard uses TeamPlayerDashboardResponse model."""
        endpoint = TeamPlayerDashboard(team_id=1610612747)

        assert endpoint.response_model is TeamPlayerDashboardResponse

    def test_endpoint_is_frozen(self):
        """TeamPlayerDashboard is immutable (frozen dataclass)."""
        endpoint = TeamPlayerDashboard(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = 1610612743  # type: ignore[misc]
