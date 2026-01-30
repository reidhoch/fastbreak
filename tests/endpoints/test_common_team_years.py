from pydantic import ValidationError

from fastbreak.endpoints import CommonTeamYears
from fastbreak.models import CommonTeamYearsResponse


class TestCommonTeamYears:
    """Tests for CommonTeamYears endpoint."""

    def test_init_with_defaults(self):
        """CommonTeamYears uses sensible defaults."""
        endpoint = CommonTeamYears()

        assert endpoint.league_id == "00"

    def test_init_with_custom_league_id(self):
        """CommonTeamYears accepts custom league_id."""
        endpoint = CommonTeamYears(league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = CommonTeamYears(league_id="00")

        params = endpoint.params()

        assert params == {"LeagueID": "00"}

    def test_path_is_correct(self):
        """CommonTeamYears has correct API path."""
        endpoint = CommonTeamYears()

        assert endpoint.path == "commonteamyears"

    def test_response_model_is_correct(self):
        """CommonTeamYears uses CommonTeamYearsResponse model."""
        endpoint = CommonTeamYears()

        assert endpoint.response_model is CommonTeamYearsResponse

    def test_endpoint_is_frozen(self):
        """CommonTeamYears is immutable (frozen dataclass)."""
        endpoint = CommonTeamYears()

        try:
            endpoint.league_id = "10"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
