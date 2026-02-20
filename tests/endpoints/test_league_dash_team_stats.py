"""Tests for LeagueDashTeamStats endpoint."""

from fastbreak.endpoints import LeagueDashTeamStats
from fastbreak.models import LeagueDashTeamStatsResponse


class TestLeagueDashTeamStats:
    """Tests for LeagueDashTeamStats endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashTeamStats uses sensible defaults."""
        endpoint = LeagueDashTeamStats()

        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.league_id == "00"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueDashTeamStats()
        params = endpoint.params()

        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """LeagueDashTeamStats has correct API path."""
        endpoint = LeagueDashTeamStats()

        assert endpoint.path == "leaguedashteamstats"

    def test_response_model_is_correct(self):
        """LeagueDashTeamStats uses LeagueDashTeamStatsResponse model."""
        endpoint = LeagueDashTeamStats()

        assert endpoint.response_model is LeagueDashTeamStatsResponse
