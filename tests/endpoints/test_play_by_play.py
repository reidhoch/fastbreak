import pytest

from fastbreak.endpoints import PlayByPlay
from fastbreak.models import PlayByPlayResponse


class TestPlayByPlay:
    """Tests for PlayByPlay endpoint."""

    def test_endpoint_path(self):
        """Endpoint has correct path."""
        endpoint = PlayByPlay(game_id="0022500571")
        assert endpoint.path == "playbyplayv3"

    def test_endpoint_response_model(self):
        """Endpoint has correct response model."""
        endpoint = PlayByPlay(game_id="0022500571")
        assert endpoint.response_model is PlayByPlayResponse

    @pytest.mark.parametrize("game_id", ["0022500571", "0022500100"])
    def test_params_returns_correct_game_id(self, game_id):
        """params() returns correct GameID parameter."""
        endpoint = PlayByPlay(game_id=game_id)
        assert endpoint.params() == {"GameID": game_id}

    def test_parse_response(self, sample_response_data):
        """parse_response() returns correct model type."""
        endpoint = PlayByPlay(game_id="0022500571")
        response = endpoint.parse_response(sample_response_data)
        assert isinstance(response, PlayByPlayResponse)
        assert response.game.gameId == "0022500571"
