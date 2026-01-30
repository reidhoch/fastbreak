from pydantic import ValidationError

from fastbreak.endpoints import TeamGameLog
from fastbreak.models import TeamGameLogResponse


class TestTeamGameLog:
    """Tests for TeamGameLog endpoint."""

    def test_init_with_defaults(self):
        """TeamGameLog uses sensible defaults."""
        endpoint = TeamGameLog(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamGameLog accepts team_id."""
        endpoint = TeamGameLog(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamGameLog accepts custom season."""
        endpoint = TeamGameLog(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamGameLog accepts custom season_type."""
        endpoint = TeamGameLog(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_league_id(self):
        """TeamGameLog accepts custom league_id."""
        endpoint = TeamGameLog(team_id=1610612747, league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamGameLog(
            team_id=1610612743,
            season="2023-24",
            season_type="Playoffs",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Playoffs"
        assert params["LeagueID"] == "00"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamGameLog(team_id=1610612747)

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """TeamGameLog has correct API path."""
        endpoint = TeamGameLog(team_id=1610612747)

        assert endpoint.path == "teamgamelog"

    def test_response_model_is_correct(self):
        """TeamGameLog uses TeamGameLogResponse model."""
        endpoint = TeamGameLog(team_id=1610612747)

        assert endpoint.response_model is TeamGameLogResponse

    def test_endpoint_is_frozen(self):
        """TeamGameLog is immutable (frozen dataclass)."""
        endpoint = TeamGameLog(team_id=1610612747)

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
