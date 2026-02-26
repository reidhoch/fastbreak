import pytest
from pydantic import ValidationError

from fastbreak.endpoints import CommonAllPlayers
from fastbreak.models import CommonAllPlayersResponse
from fastbreak.seasons import get_season_from_date


class TestCommonAllPlayers:
    """Tests for CommonAllPlayers endpoint."""

    def test_init_with_defaults(self):
        """CommonAllPlayers uses sensible defaults."""
        endpoint = CommonAllPlayers()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.is_only_current_season == 1

    def test_init_with_custom_league_id(self):
        """CommonAllPlayers accepts custom league_id."""
        endpoint = CommonAllPlayers(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """CommonAllPlayers accepts custom season."""
        endpoint = CommonAllPlayers(season="2025-26")

        assert endpoint.season == "2025-26"

    def test_init_with_historical_players(self):
        """CommonAllPlayers accepts is_only_current_season=0 for historical data."""
        endpoint = CommonAllPlayers(is_only_current_season=0)

        assert endpoint.is_only_current_season == 0

    def test_init_with_all_custom_params(self):
        """CommonAllPlayers accepts all custom parameters."""
        endpoint = CommonAllPlayers(
            league_id="10",
            season="2023-24",
            is_only_current_season=0,
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2023-24"
        assert endpoint.is_only_current_season == 0

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = CommonAllPlayers(
            league_id="00",
            season="2024-25",
            is_only_current_season=1,
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "IsOnlyCurrentSeason": "1",
        }

    def test_params_converts_int_to_string(self):
        """params() converts is_only_current_season int to string."""
        endpoint = CommonAllPlayers(is_only_current_season=0)

        params = endpoint.params()

        assert params["IsOnlyCurrentSeason"] == "0"
        assert isinstance(params["IsOnlyCurrentSeason"], str)

    def test_path_is_correct(self):
        """CommonAllPlayers has correct API path."""
        endpoint = CommonAllPlayers()

        assert endpoint.path == "commonallplayers"

    def test_response_model_is_correct(self):
        """CommonAllPlayers uses CommonAllPlayersResponse model."""
        endpoint = CommonAllPlayers()

        assert endpoint.response_model is CommonAllPlayersResponse

    def test_endpoint_is_frozen(self):
        """CommonAllPlayers is immutable (frozen dataclass)."""
        endpoint = CommonAllPlayers()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
