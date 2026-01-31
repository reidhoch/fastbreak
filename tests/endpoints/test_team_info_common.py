import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamInfoCommon
from fastbreak.models import TeamInfoCommonResponse


class TestTeamInfoCommon:
    """Tests for TeamInfoCommon endpoint."""

    def test_init_with_defaults(self):
        """TeamInfoCommon uses sensible defaults."""
        endpoint = TeamInfoCommon(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamInfoCommon accepts team_id."""
        endpoint = TeamInfoCommon(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_league_id(self):
        """TeamInfoCommon accepts custom league_id."""
        endpoint = TeamInfoCommon(team_id=1610612747, league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamInfoCommon(team_id=1610612743)

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["LeagueID"] == "00"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamInfoCommon(team_id=1610612747)

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """TeamInfoCommon has correct API path."""
        endpoint = TeamInfoCommon(team_id=1610612747)

        assert endpoint.path == "teaminfocommon"

    def test_response_model_is_correct(self):
        """TeamInfoCommon uses TeamInfoCommonResponse model."""
        endpoint = TeamInfoCommon(team_id=1610612747)

        assert endpoint.response_model is TeamInfoCommonResponse

    def test_endpoint_is_frozen(self):
        """TeamInfoCommon is immutable (frozen dataclass)."""
        endpoint = TeamInfoCommon(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = 1610612743  # type: ignore[misc]
