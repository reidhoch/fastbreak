import pytest
from pydantic import ValidationError

from fastbreak.endpoints import DraftCombineDrillResults
from fastbreak.models import DraftCombineDrillResultsResponse
from fastbreak.seasons import get_season_from_date


class TestDraftCombineDrillResults:
    """Tests for DraftCombineDrillResults endpoint."""

    def test_init_with_defaults(self):
        """DraftCombineDrillResults uses sensible defaults."""
        endpoint = DraftCombineDrillResults()

        assert endpoint.league_id == "00"
        assert endpoint.season_year == get_season_from_date()

    def test_init_with_custom_league_id(self):
        """DraftCombineDrillResults accepts custom league_id."""
        endpoint = DraftCombineDrillResults(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_year(self):
        """DraftCombineDrillResults accepts custom season_year."""
        endpoint = DraftCombineDrillResults(season_year="2023-24")

        assert endpoint.season_year == "2023-24"

    def test_init_with_all_custom_params(self):
        """DraftCombineDrillResults accepts all custom parameters."""
        endpoint = DraftCombineDrillResults(
            league_id="10",
            season_year="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_year == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = DraftCombineDrillResults(
            league_id="00",
            season_year="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonYear": "2024-25",
        }

    def test_path_is_correct(self):
        """DraftCombineDrillResults has correct API path."""
        endpoint = DraftCombineDrillResults()

        assert endpoint.path == "draftcombinedrillresults"

    def test_response_model_is_correct(self):
        """DraftCombineDrillResults uses DraftCombineDrillResultsResponse model."""
        endpoint = DraftCombineDrillResults()

        assert endpoint.response_model is DraftCombineDrillResultsResponse

    def test_endpoint_is_frozen(self):
        """DraftCombineDrillResults is immutable (frozen dataclass)."""
        endpoint = DraftCombineDrillResults()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season_year = "2023-24"  # type: ignore[misc]
