from pydantic import ValidationError

from fastbreak.endpoints import DraftCombineStats
from fastbreak.models import DraftCombineStatsResponse


class TestDraftCombineStats:
    """Tests for DraftCombineStats endpoint."""

    def test_init_with_defaults(self):
        """DraftCombineStats uses sensible defaults."""
        endpoint = DraftCombineStats()

        assert endpoint.league_id == "00"
        assert endpoint.season_year == "2024-25"

    def test_init_with_custom_league_id(self):
        """DraftCombineStats accepts custom league_id."""
        endpoint = DraftCombineStats(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_year(self):
        """DraftCombineStats accepts custom season_year."""
        endpoint = DraftCombineStats(season_year="2023-24")

        assert endpoint.season_year == "2023-24"

    def test_init_with_all_custom_params(self):
        """DraftCombineStats accepts all custom parameters."""
        endpoint = DraftCombineStats(
            league_id="10",
            season_year="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_year == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = DraftCombineStats(
            league_id="00",
            season_year="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonYear": "2024-25",
        }

    def test_path_is_correct(self):
        """DraftCombineStats has correct API path."""
        endpoint = DraftCombineStats()

        assert endpoint.path == "draftcombinestats"

    def test_response_model_is_correct(self):
        """DraftCombineStats uses DraftCombineStatsResponse model."""
        endpoint = DraftCombineStats()

        assert endpoint.response_model is DraftCombineStatsResponse

    def test_endpoint_is_frozen(self):
        """DraftCombineStats is immutable (frozen dataclass)."""
        endpoint = DraftCombineStats()

        try:
            endpoint.season_year = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
