from fastbreak.endpoints import CommonPlayerInfo
from fastbreak.models import CommonPlayerInfoResponse


class TestCommonPlayerInfo:
    """Tests for CommonPlayerInfo endpoint."""

    def test_init_with_required_player_id(self):
        """CommonPlayerInfo requires player_id."""
        endpoint = CommonPlayerInfo(player_id=203500)

        assert endpoint.player_id == 203500

    def test_init_with_default_league_id(self):
        """CommonPlayerInfo uses NBA league_id by default."""
        endpoint = CommonPlayerInfo(player_id=203500)

        assert endpoint.league_id == "00"

    def test_init_with_custom_league_id(self):
        """CommonPlayerInfo accepts custom league_id."""
        endpoint = CommonPlayerInfo(player_id=203500, league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_all_params(self):
        """CommonPlayerInfo accepts all parameters."""
        endpoint = CommonPlayerInfo(player_id=201939, league_id="00")

        assert endpoint.player_id == 201939
        assert endpoint.league_id == "00"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = CommonPlayerInfo(player_id=203500, league_id="00")

        params = endpoint.params()

        assert params == {
            "PlayerID": "203500",
            "LeagueID": "00",
        }

    def test_params_converts_player_id_to_string(self):
        """params() converts player_id int to string."""
        endpoint = CommonPlayerInfo(player_id=2544)

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert isinstance(params["PlayerID"], str)

    def test_path_is_correct(self):
        """CommonPlayerInfo has correct API path."""
        endpoint = CommonPlayerInfo(player_id=203500)

        assert endpoint.path == "commonplayerinfo"

    def test_response_model_is_correct(self):
        """CommonPlayerInfo uses CommonPlayerInfoResponse model."""
        endpoint = CommonPlayerInfo(player_id=203500)

        assert endpoint.response_model is CommonPlayerInfoResponse

    def test_endpoint_is_frozen(self):
        """CommonPlayerInfo is immutable (frozen dataclass)."""
        endpoint = CommonPlayerInfo(player_id=203500)

        try:
            endpoint.player_id = 2544  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
