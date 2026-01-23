from fastbreak.endpoints import PlayerAwards
from fastbreak.models import PlayerAwardsResponse


class TestPlayerAwards:
    """Tests for PlayerAwards endpoint."""

    def test_init_with_player_id(self):
        """PlayerAwards requires player_id."""
        endpoint = PlayerAwards(player_id=2544)

        assert endpoint.player_id == 2544

    def test_init_with_different_player_id(self):
        """PlayerAwards accepts different player IDs."""
        endpoint = PlayerAwards(player_id=201566)

        assert endpoint.player_id == 201566

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = PlayerAwards(player_id=2544)

        params = endpoint.params()

        assert params == {
            "PlayerID": "2544",
        }

    def test_path_is_correct(self):
        """PlayerAwards has correct API path."""
        endpoint = PlayerAwards(player_id=2544)

        assert endpoint.path == "playerawards"

    def test_response_model_is_correct(self):
        """PlayerAwards uses PlayerAwardsResponse model."""
        endpoint = PlayerAwards(player_id=2544)

        assert endpoint.response_model is PlayerAwardsResponse

    def test_endpoint_is_frozen(self):
        """PlayerAwards is immutable (frozen dataclass)."""
        endpoint = PlayerAwards(player_id=2544)

        try:
            endpoint.player_id = 201566  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
