from pydantic import ValidationError

from fastbreak.endpoints import FranchiseHistory
from fastbreak.models import FranchiseHistoryResponse


class TestFranchiseHistory:
    """Tests for FranchiseHistory endpoint."""

    def test_init_with_defaults(self):
        """FranchiseHistory uses sensible defaults."""
        endpoint = FranchiseHistory()

        assert endpoint.league_id == "00"

    def test_init_with_custom_league_id(self):
        """FranchiseHistory accepts custom league_id."""
        endpoint = FranchiseHistory(league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = FranchiseHistory(league_id="00")

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
        }

    def test_path_is_correct(self):
        """FranchiseHistory has correct API path."""
        endpoint = FranchiseHistory()

        assert endpoint.path == "franchisehistory"

    def test_response_model_is_correct(self):
        """FranchiseHistory uses FranchiseHistoryResponse model."""
        endpoint = FranchiseHistory()

        assert endpoint.response_model is FranchiseHistoryResponse

    def test_endpoint_is_frozen(self):
        """FranchiseHistory is immutable (frozen dataclass)."""
        endpoint = FranchiseHistory()

        try:
            endpoint.league_id = "10"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
