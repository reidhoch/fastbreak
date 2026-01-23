from fastbreak.endpoints import TeamDetails
from fastbreak.models import TeamDetailsResponse


class TestTeamDetails:
    """Tests for TeamDetails endpoint."""

    def test_init_with_defaults(self):
        """TeamDetails uses sensible defaults."""
        endpoint = TeamDetails()

        assert endpoint.team_id == 0

    def test_init_with_team_id(self):
        """TeamDetails accepts team_id."""
        endpoint = TeamDetails(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamDetails(team_id=1610612743)

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"

    def test_params_with_default_team_id(self):
        """params() returns TeamID as string even when 0."""
        endpoint = TeamDetails()

        params = endpoint.params()

        assert params["TeamID"] == "0"

    def test_path_is_correct(self):
        """TeamDetails has correct API path."""
        endpoint = TeamDetails()

        assert endpoint.path == "teamdetails"

    def test_response_model_is_correct(self):
        """TeamDetails uses TeamDetailsResponse model."""
        endpoint = TeamDetails()

        assert endpoint.response_model is TeamDetailsResponse

    def test_endpoint_is_frozen(self):
        """TeamDetails is immutable (frozen dataclass)."""
        endpoint = TeamDetails()

        try:
            endpoint.team_id = 123  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
