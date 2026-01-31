import pytest
from pydantic import ValidationError

from fastbreak.endpoints import GameRotation
from fastbreak.models import GameRotationResponse


class TestGameRotation:
    """Tests for GameRotation endpoint."""

    def test_init_with_required_params(self):
        """GameRotation requires game_id."""
        endpoint = GameRotation(game_id="0022500571")

        assert endpoint.game_id == "0022500571"
        assert endpoint.league_id == "00"

    def test_init_with_custom_league_id(self):
        """GameRotation accepts custom league_id."""
        endpoint = GameRotation(game_id="0022500571", league_id="10")

        assert endpoint.game_id == "0022500571"
        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = GameRotation(game_id="0022500571", league_id="00")

        params = endpoint.params()

        assert params == {
            "GameID": "0022500571",
            "LeagueID": "00",
        }

    def test_path_is_correct(self):
        """GameRotation has correct API path."""
        endpoint = GameRotation(game_id="0022500571")

        assert endpoint.path == "gamerotation"

    def test_response_model_is_correct(self):
        """GameRotation uses GameRotationResponse model."""
        endpoint = GameRotation(game_id="0022500571")

        assert endpoint.response_model is GameRotationResponse

    def test_endpoint_is_frozen(self):
        """GameRotation is immutable (frozen dataclass)."""
        endpoint = GameRotation(game_id="0022500571")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_id = "0022500572"  # type: ignore[misc]
