import pytest
from pydantic import ValidationError

from fastbreak.endpoints import CommonTeamRoster
from fastbreak.models import CommonTeamRosterResponse
from fastbreak.utils import get_season_from_date


class TestCommonTeamRoster:
    """Tests for CommonTeamRoster endpoint."""

    def test_init_with_team_id(self):
        """CommonTeamRoster requires team_id."""
        endpoint = CommonTeamRoster(team_id=1610612745)

        assert endpoint.team_id == 1610612745
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()

    def test_init_with_custom_league_id(self):
        """CommonTeamRoster accepts custom league_id."""
        endpoint = CommonTeamRoster(team_id=1610612745, league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """CommonTeamRoster accepts custom season."""
        endpoint = CommonTeamRoster(team_id=1610612745, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_all_custom_params(self):
        """CommonTeamRoster accepts all custom parameters."""
        endpoint = CommonTeamRoster(
            team_id=1610612747,
            league_id="00",
            season="2023-24",
        )

        assert endpoint.team_id == 1610612747
        assert endpoint.league_id == "00"
        assert endpoint.season == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = CommonTeamRoster(
            team_id=1610612745,
            league_id="00",
            season="2024-25",
        )

        params = endpoint.params()

        assert params == {
            "TeamID": "1610612745",
            "LeagueID": "00",
            "Season": "2024-25",
        }

    def test_path_is_correct(self):
        """CommonTeamRoster has correct API path."""
        endpoint = CommonTeamRoster(team_id=1610612745)

        assert endpoint.path == "commonteamroster"

    def test_response_model_is_correct(self):
        """CommonTeamRoster uses CommonTeamRosterResponse model."""
        endpoint = CommonTeamRoster(team_id=1610612745)

        assert endpoint.response_model is CommonTeamRosterResponse

    def test_endpoint_is_frozen(self):
        """CommonTeamRoster is immutable (frozen dataclass)."""
        endpoint = CommonTeamRoster(team_id=1610612745)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
