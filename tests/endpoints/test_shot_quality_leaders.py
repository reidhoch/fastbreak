import pytest
from pydantic import ValidationError

from fastbreak.endpoints import ShotQualityLeaders
from fastbreak.models import ShotQualityLeadersResponse


class TestShotQualityLeaders:
    """Tests for ShotQualityLeaders endpoint."""

    def test_init_with_defaults(self):
        """ShotQualityLeaders uses sensible defaults."""
        endpoint = ShotQualityLeaders()

        assert endpoint.league_id == "00"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.season_year == "2024-25"

    def test_init_with_custom_league_id(self):
        """ShotQualityLeaders accepts custom league_id."""
        endpoint = ShotQualityLeaders(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_type(self):
        """ShotQualityLeaders accepts custom season_type."""
        endpoint = ShotQualityLeaders(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_season_year(self):
        """ShotQualityLeaders accepts custom season_year."""
        endpoint = ShotQualityLeaders(season_year="2024-25")

        assert endpoint.season_year == "2024-25"

    def test_init_with_all_custom_params(self):
        """ShotQualityLeaders accepts all custom parameters."""
        endpoint = ShotQualityLeaders(
            league_id="10",
            season_type="Playoffs",
            season_year="2024-25",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.season_year == "2024-25"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = ShotQualityLeaders(
            league_id="00",
            season_type="Regular Season",
            season_year="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonType": "Regular Season",
            "Season": "2024-25",
        }

    def test_path_is_correct(self):
        """ShotQualityLeaders has correct API path."""
        endpoint = ShotQualityLeaders()

        assert endpoint.path == "shotqualityleaders"

    def test_response_model_is_correct(self):
        """ShotQualityLeaders uses ShotQualityLeadersResponse model."""
        endpoint = ShotQualityLeaders()

        assert endpoint.response_model is ShotQualityLeadersResponse

    def test_endpoint_is_frozen(self):
        """ShotQualityLeaders is immutable (frozen dataclass)."""
        endpoint = ShotQualityLeaders()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season_year = "2024-25"  # type: ignore[misc]
