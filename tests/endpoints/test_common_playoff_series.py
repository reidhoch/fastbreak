import pytest
from pydantic import ValidationError

from fastbreak.endpoints import CommonPlayoffSeries
from fastbreak.models import CommonPlayoffSeriesResponse


class TestCommonPlayoffSeries:
    """Tests for CommonPlayoffSeries endpoint."""

    def test_init_with_defaults(self):
        """CommonPlayoffSeries uses sensible defaults."""
        endpoint = CommonPlayoffSeries()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.series_id is None

    def test_init_with_custom_league_id(self):
        """CommonPlayoffSeries accepts custom league_id."""
        endpoint = CommonPlayoffSeries(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """CommonPlayoffSeries accepts custom season."""
        endpoint = CommonPlayoffSeries(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_series_id(self):
        """CommonPlayoffSeries accepts optional series_id."""
        endpoint = CommonPlayoffSeries(series_id="004240010")

        assert endpoint.series_id == "004240010"

    def test_init_with_all_custom_params(self):
        """CommonPlayoffSeries accepts all custom parameters."""
        endpoint = CommonPlayoffSeries(
            league_id="00",
            season="2023-24",
            series_id="004230040",
        )

        assert endpoint.league_id == "00"
        assert endpoint.season == "2023-24"
        assert endpoint.series_id == "004230040"

    def test_params_returns_correct_dict_without_series_id(self):
        """params() returns correctly formatted parameters without series_id."""
        endpoint = CommonPlayoffSeries(
            league_id="00",
            season="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
        }
        assert "SeriesID" not in params

    def test_params_includes_series_id_when_provided(self):
        """params() includes SeriesID when provided."""
        endpoint = CommonPlayoffSeries(series_id="004240010")

        params = endpoint.params()

        assert params["SeriesID"] == "004240010"

    def test_path_is_correct(self):
        """CommonPlayoffSeries has correct API path."""
        endpoint = CommonPlayoffSeries()

        assert endpoint.path == "commonplayoffseries"

    def test_response_model_is_correct(self):
        """CommonPlayoffSeries uses CommonPlayoffSeriesResponse model."""
        endpoint = CommonPlayoffSeries()

        assert endpoint.response_model is CommonPlayoffSeriesResponse

    def test_endpoint_is_frozen(self):
        """CommonPlayoffSeries is immutable (frozen dataclass)."""
        endpoint = CommonPlayoffSeries()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
