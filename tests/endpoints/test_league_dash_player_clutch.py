"""Tests for LeagueDashPlayerClutch endpoint."""

from fastbreak.endpoints import LeagueDashPlayerClutch
from fastbreak.models import LeagueDashPlayerClutchResponse


class TestLeagueDashPlayerClutch:
    """Tests for LeagueDashPlayerClutch endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashPlayerClutch uses sensible defaults."""
        endpoint = LeagueDashPlayerClutch()

        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.clutch_time == "Last 5 Minutes"
        assert endpoint.point_diff == 5

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueDashPlayerClutch()
        params = endpoint.params()

        assert params["Season"] == "2024-25"
        assert params["ClutchTime"] == "Last 5 Minutes"
        assert params["PointDiff"] == "5"

    def test_path_is_correct(self):
        """LeagueDashPlayerClutch has correct API path."""
        endpoint = LeagueDashPlayerClutch()

        assert endpoint.path == "leaguedashplayerclutch"

    def test_response_model_is_correct(self):
        """LeagueDashPlayerClutch uses LeagueDashPlayerClutchResponse."""
        endpoint = LeagueDashPlayerClutch()

        assert endpoint.response_model is LeagueDashPlayerClutchResponse
