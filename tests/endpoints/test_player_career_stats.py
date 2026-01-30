from pydantic import ValidationError

from fastbreak.endpoints import PlayerCareerStats
from fastbreak.models import PlayerCareerStatsResponse


class TestPlayerCareerStats:
    """Tests for PlayerCareerStats endpoint."""

    def test_init_with_player_id(self):
        """PlayerCareerStats requires player_id."""
        endpoint = PlayerCareerStats(player_id=2544)

        assert endpoint.player_id == 2544

    def test_init_with_defaults(self):
        """PlayerCareerStats uses sensible defaults."""
        endpoint = PlayerCareerStats(player_id=2544)

        assert endpoint.league_id == "00"
        assert endpoint.per_mode == "PerGame"

    def test_init_with_custom_league_id(self):
        """PlayerCareerStats accepts custom league_id."""
        endpoint = PlayerCareerStats(player_id=2544, league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_per_mode(self):
        """PlayerCareerStats accepts custom per_mode."""
        endpoint = PlayerCareerStats(player_id=2544, per_mode="Per36")

        assert endpoint.per_mode == "Per36"

    def test_init_with_totals_per_mode(self):
        """PlayerCareerStats accepts Totals per_mode."""
        endpoint = PlayerCareerStats(player_id=2544, per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_all_custom_params(self):
        """PlayerCareerStats accepts all custom parameters."""
        endpoint = PlayerCareerStats(
            player_id=201566,
            league_id="10",
            per_mode="Per36",
        )

        assert endpoint.player_id == 201566
        assert endpoint.league_id == "10"
        assert endpoint.per_mode == "Per36"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = PlayerCareerStats(
            player_id=2544,
            league_id="00",
            per_mode="PerGame",
        )

        params = endpoint.params()

        assert params == {
            "PlayerID": "2544",
            "LeagueID": "00",
            "PerMode": "PerGame",
        }

    def test_path_is_correct(self):
        """PlayerCareerStats has correct API path."""
        endpoint = PlayerCareerStats(player_id=2544)

        assert endpoint.path == "playercareerstats"

    def test_response_model_is_correct(self):
        """PlayerCareerStats uses PlayerCareerStatsResponse model."""
        endpoint = PlayerCareerStats(player_id=2544)

        assert endpoint.response_model is PlayerCareerStatsResponse

    def test_endpoint_is_frozen(self):
        """PlayerCareerStats is immutable (frozen dataclass)."""
        endpoint = PlayerCareerStats(player_id=2544)

        try:
            endpoint.player_id = 201566  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
