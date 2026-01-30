from pydantic import ValidationError

from fastbreak.endpoints import FranchisePlayers
from fastbreak.models import FranchisePlayersResponse


class TestFranchisePlayers:
    """Tests for FranchisePlayers endpoint."""

    def test_init_with_defaults(self):
        """FranchisePlayers uses sensible defaults."""
        endpoint = FranchisePlayers(team_id="1610612747")

        assert endpoint.league_id == "00"
        assert endpoint.team_id == "1610612747"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"

    def test_init_with_custom_league_id(self):
        """FranchisePlayers accepts custom league_id."""
        endpoint = FranchisePlayers(team_id="1610612747", league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_team_id(self):
        """FranchisePlayers accepts custom team_id."""
        endpoint = FranchisePlayers(team_id="1610612745")

        assert endpoint.team_id == "1610612745"

    def test_init_with_custom_season_type(self):
        """FranchisePlayers accepts custom season_type."""
        endpoint = FranchisePlayers(team_id="1610612747", season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """FranchisePlayers accepts custom per_mode."""
        endpoint = FranchisePlayers(team_id="1610612747", per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_all_custom_params(self):
        """FranchisePlayers accepts all custom parameters."""
        endpoint = FranchisePlayers(
            league_id="10",
            team_id="1610612745",
            season_type="Playoffs",
            per_mode="Totals",
        )

        assert endpoint.league_id == "10"
        assert endpoint.team_id == "1610612745"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = FranchisePlayers(
            league_id="00",
            team_id="1610612747",
            season_type="Regular Season",
            per_mode="PerGame",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "TeamID": "1610612747",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
        }

    def test_path_is_correct(self):
        """FranchisePlayers has correct API path."""
        endpoint = FranchisePlayers(team_id="1610612747")

        assert endpoint.path == "franchiseplayers"

    def test_response_model_is_correct(self):
        """FranchisePlayers uses FranchisePlayersResponse model."""
        endpoint = FranchisePlayers(team_id="1610612747")

        assert endpoint.response_model is FranchisePlayersResponse

    def test_endpoint_is_frozen(self):
        """FranchisePlayers is immutable (frozen dataclass)."""
        endpoint = FranchisePlayers(team_id="1610612747")

        try:
            endpoint.team_id = "1610612745"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
