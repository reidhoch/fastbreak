"""Tests for LeagueDashPlayerStats endpoint."""

from fastbreak.endpoints import LeagueDashPlayerStats
from fastbreak.models import LeagueDashPlayerStatsResponse


class TestLeagueDashPlayerStats:
    """Tests for LeagueDashPlayerStats endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashPlayerStats uses sensible defaults."""
        endpoint = LeagueDashPlayerStats()

        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.league_id == "00"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueDashPlayerStats()
        params = endpoint.params()

        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """LeagueDashPlayerStats has correct API path."""
        endpoint = LeagueDashPlayerStats()

        assert endpoint.path == "leaguedashplayerstats"

    def test_response_model_is_correct(self):
        """LeagueDashPlayerStats uses LeagueDashPlayerStatsResponse model."""
        endpoint = LeagueDashPlayerStats()

        assert endpoint.response_model is LeagueDashPlayerStatsResponse
