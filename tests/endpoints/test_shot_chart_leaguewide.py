import pytest
from pydantic import ValidationError

from fastbreak.endpoints import ShotChartLeaguewide
from fastbreak.models import ShotChartLeaguewideResponse
from fastbreak.utils import get_season_from_date


class TestShotChartLeaguewide:
    """Tests for ShotChartLeaguewide endpoint."""

    def test_init_with_defaults(self):
        """ShotChartLeaguewide uses sensible defaults."""
        endpoint = ShotChartLeaguewide()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()

    def test_init_with_custom_league_id(self):
        """ShotChartLeaguewide accepts custom league_id."""
        endpoint = ShotChartLeaguewide(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """ShotChartLeaguewide accepts custom season."""
        endpoint = ShotChartLeaguewide(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_all_custom_params(self):
        """ShotChartLeaguewide accepts all custom parameters."""
        endpoint = ShotChartLeaguewide(
            league_id="10",
            season="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = ShotChartLeaguewide(
            league_id="00",
            season="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
        }

    def test_path_is_correct(self):
        """ShotChartLeaguewide has correct API path."""
        endpoint = ShotChartLeaguewide()

        assert endpoint.path == "shotchartleaguewide"

    def test_response_model_is_correct(self):
        """ShotChartLeaguewide uses ShotChartLeaguewideResponse model."""
        endpoint = ShotChartLeaguewide()

        assert endpoint.response_model is ShotChartLeaguewideResponse

    def test_endpoint_is_frozen(self):
        """ShotChartLeaguewide is immutable (frozen dataclass)."""
        endpoint = ShotChartLeaguewide()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
