from fastbreak.endpoints import FranchiseLeaders
from fastbreak.models import FranchiseLeadersResponse


class TestFranchiseLeaders:
    """Tests for FranchiseLeaders endpoint."""

    def test_init_with_defaults(self):
        """FranchiseLeaders uses sensible defaults."""
        endpoint = FranchiseLeaders()

        assert endpoint.league_id == "00"
        assert endpoint.team_id == "1610612747"

    def test_init_with_custom_league_id(self):
        """FranchiseLeaders accepts custom league_id."""
        endpoint = FranchiseLeaders(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_team_id(self):
        """FranchiseLeaders accepts custom team_id."""
        endpoint = FranchiseLeaders(team_id="1610612744")

        assert endpoint.team_id == "1610612744"

    def test_init_with_all_custom_params(self):
        """FranchiseLeaders accepts all custom parameters."""
        endpoint = FranchiseLeaders(
            league_id="10",
            team_id="1610612744",
        )

        assert endpoint.league_id == "10"
        assert endpoint.team_id == "1610612744"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = FranchiseLeaders(
            league_id="00",
            team_id="1610612747",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "TeamID": "1610612747",
        }

    def test_path_is_correct(self):
        """FranchiseLeaders has correct API path."""
        endpoint = FranchiseLeaders()

        assert endpoint.path == "franchiseleaders"

    def test_response_model_is_correct(self):
        """FranchiseLeaders uses FranchiseLeadersResponse model."""
        endpoint = FranchiseLeaders()

        assert endpoint.response_model is FranchiseLeadersResponse

    def test_endpoint_is_frozen(self):
        """FranchiseLeaders is immutable (frozen dataclass)."""
        endpoint = FranchiseLeaders()

        try:
            endpoint.team_id = "1610612744"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
