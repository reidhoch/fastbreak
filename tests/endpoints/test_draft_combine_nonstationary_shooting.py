from pydantic import ValidationError

from fastbreak.endpoints import DraftCombineNonstationaryShooting
from fastbreak.models import DraftCombineNonstationaryShootingResponse


class TestDraftCombineNonstationaryShooting:
    """Tests for DraftCombineNonstationaryShooting endpoint."""

    def test_init_with_defaults(self):
        """DraftCombineNonstationaryShooting uses sensible defaults."""
        endpoint = DraftCombineNonstationaryShooting()

        assert endpoint.league_id == "00"
        assert endpoint.season_year == "2024-25"

    def test_init_with_custom_league_id(self):
        """DraftCombineNonstationaryShooting accepts custom league_id."""
        endpoint = DraftCombineNonstationaryShooting(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_year(self):
        """DraftCombineNonstationaryShooting accepts custom season_year."""
        endpoint = DraftCombineNonstationaryShooting(season_year="2023-24")

        assert endpoint.season_year == "2023-24"

    def test_init_with_all_custom_params(self):
        """DraftCombineNonstationaryShooting accepts all custom parameters."""
        endpoint = DraftCombineNonstationaryShooting(
            league_id="10",
            season_year="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_year == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = DraftCombineNonstationaryShooting(
            league_id="00",
            season_year="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonYear": "2024-25",
        }

    def test_path_is_correct(self):
        """DraftCombineNonstationaryShooting has correct API path."""
        endpoint = DraftCombineNonstationaryShooting()

        assert endpoint.path == "draftcombinenonstationaryshooting"

    def test_response_model_is_correct(self):
        """DraftCombineNonstationaryShooting uses correct response model."""
        endpoint = DraftCombineNonstationaryShooting()

        assert endpoint.response_model is DraftCombineNonstationaryShootingResponse

    def test_endpoint_is_frozen(self):
        """DraftCombineNonstationaryShooting is immutable (frozen dataclass)."""
        endpoint = DraftCombineNonstationaryShooting()

        try:
            endpoint.season_year = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
