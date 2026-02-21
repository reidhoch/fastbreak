import pytest
from pydantic import ValidationError

from fastbreak.endpoints import DraftCombineSpotShooting
from fastbreak.models import DraftCombineSpotShootingResponse
from fastbreak.utils import get_season_from_date


class TestDraftCombineSpotShooting:
    """Tests for DraftCombineSpotShooting endpoint."""

    def test_init_with_defaults(self):
        """DraftCombineSpotShooting uses sensible defaults."""
        endpoint = DraftCombineSpotShooting()

        assert endpoint.league_id == "00"
        assert endpoint.season_year == get_season_from_date()

    def test_init_with_custom_league_id(self):
        """DraftCombineSpotShooting accepts custom league_id."""
        endpoint = DraftCombineSpotShooting(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_year(self):
        """DraftCombineSpotShooting accepts custom season_year."""
        endpoint = DraftCombineSpotShooting(season_year="2023-24")

        assert endpoint.season_year == "2023-24"

    def test_init_with_all_custom_params(self):
        """DraftCombineSpotShooting accepts all custom parameters."""
        endpoint = DraftCombineSpotShooting(
            league_id="10",
            season_year="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_year == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = DraftCombineSpotShooting(
            league_id="00",
            season_year="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonYear": "2024-25",
        }

    def test_path_is_correct(self):
        """DraftCombineSpotShooting has correct API path."""
        endpoint = DraftCombineSpotShooting()

        assert endpoint.path == "draftcombinespotshooting"

    def test_response_model_is_correct(self):
        """DraftCombineSpotShooting uses DraftCombineSpotShootingResponse model."""
        endpoint = DraftCombineSpotShooting()

        assert endpoint.response_model is DraftCombineSpotShootingResponse

    def test_endpoint_is_frozen(self):
        """DraftCombineSpotShooting is immutable (frozen dataclass)."""
        endpoint = DraftCombineSpotShooting()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season_year = "2023-24"  # type: ignore[misc]
