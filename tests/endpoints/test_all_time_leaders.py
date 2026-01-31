import pytest
from pydantic import ValidationError

from fastbreak.endpoints import AllTimeLeadersGrids
from fastbreak.models import AllTimeLeadersResponse


class TestAllTimeLeadersGrids:
    """Tests for AllTimeLeadersGrids endpoint."""

    def test_init_with_defaults(self):
        """AllTimeLeadersGrids uses sensible defaults."""
        endpoint = AllTimeLeadersGrids()

        assert endpoint.league_id == "00"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.top_x == 10

    def test_init_with_custom_league_id(self):
        """AllTimeLeadersGrids accepts custom league_id."""
        endpoint = AllTimeLeadersGrids(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_type(self):
        """AllTimeLeadersGrids accepts custom season_type."""
        endpoint = AllTimeLeadersGrids(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """AllTimeLeadersGrids accepts custom per_mode."""
        endpoint = AllTimeLeadersGrids(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_custom_top_x(self):
        """AllTimeLeadersGrids accepts custom top_x."""
        endpoint = AllTimeLeadersGrids(top_x=25)

        assert endpoint.top_x == 25

    def test_init_with_all_custom_params(self):
        """AllTimeLeadersGrids accepts all custom parameters."""
        endpoint = AllTimeLeadersGrids(
            league_id="10",
            season_type="Playoffs",
            per_mode="Totals",
            top_x=50,
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.top_x == 50

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = AllTimeLeadersGrids(
            league_id="00",
            season_type="Regular Season",
            per_mode="PerGame",
            top_x=10,
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "TopX": "10",
        }

    def test_params_converts_top_x_to_string(self):
        """params() converts top_x integer to string."""
        endpoint = AllTimeLeadersGrids(top_x=25)

        params = endpoint.params()

        assert params["TopX"] == "25"
        assert isinstance(params["TopX"], str)

    def test_path_is_correct(self):
        """AllTimeLeadersGrids has correct API path."""
        endpoint = AllTimeLeadersGrids()

        assert endpoint.path == "alltimeleadersgrids"

    def test_response_model_is_correct(self):
        """AllTimeLeadersGrids uses AllTimeLeadersResponse model."""
        endpoint = AllTimeLeadersGrids()

        assert endpoint.response_model is AllTimeLeadersResponse

    def test_endpoint_is_frozen(self):
        """AllTimeLeadersGrids is immutable (frozen dataclass)."""
        endpoint = AllTimeLeadersGrids()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.top_x = 50  # type: ignore[misc]
