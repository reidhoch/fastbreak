import pytest
from pydantic import ValidationError

from fastbreak.endpoints import DraftCombinePlayerAnthro
from fastbreak.models import DraftCombinePlayerAnthroResponse
from fastbreak.seasons import get_season_from_date


class TestDraftCombinePlayerAnthro:
    """Tests for DraftCombinePlayerAnthro endpoint."""

    def test_init_with_defaults(self):
        """DraftCombinePlayerAnthro uses sensible defaults."""
        endpoint = DraftCombinePlayerAnthro()

        assert endpoint.league_id == "00"
        assert endpoint.season_year == get_season_from_date()

    def test_init_with_custom_league_id(self):
        """DraftCombinePlayerAnthro accepts custom league_id."""
        endpoint = DraftCombinePlayerAnthro(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_year(self):
        """DraftCombinePlayerAnthro accepts custom season_year."""
        endpoint = DraftCombinePlayerAnthro(season_year="2023-24")

        assert endpoint.season_year == "2023-24"

    def test_init_with_all_custom_params(self):
        """DraftCombinePlayerAnthro accepts all custom parameters."""
        endpoint = DraftCombinePlayerAnthro(
            league_id="10",
            season_year="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_year == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = DraftCombinePlayerAnthro(
            league_id="00",
            season_year="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonYear": "2024-25",
        }

    def test_path_is_correct(self):
        """DraftCombinePlayerAnthro has correct API path."""
        endpoint = DraftCombinePlayerAnthro()

        assert endpoint.path == "draftcombineplayeranthro"

    def test_response_model_is_correct(self):
        """DraftCombinePlayerAnthro uses DraftCombinePlayerAnthroResponse model."""
        endpoint = DraftCombinePlayerAnthro()

        assert endpoint.response_model is DraftCombinePlayerAnthroResponse

    def test_endpoint_is_frozen(self):
        """DraftCombinePlayerAnthro is immutable (frozen dataclass)."""
        endpoint = DraftCombinePlayerAnthro()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season_year = "2023-24"  # type: ignore[misc]
