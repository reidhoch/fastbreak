from pydantic import ValidationError

from fastbreak.endpoints import TeamGameLogs
from fastbreak.models import TeamGameLogsResponse


class TestTeamGameLogs:
    """Tests for TeamGameLogs endpoint."""

    def test_init_with_defaults(self):
        """TeamGameLogs uses sensible defaults."""
        endpoint = TeamGameLogs(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamGameLogs accepts team_id."""
        endpoint = TeamGameLogs(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamGameLogs accepts custom season."""
        endpoint = TeamGameLogs(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamGameLogs accepts custom season_type."""
        endpoint = TeamGameLogs(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_league_id(self):
        """TeamGameLogs accepts custom league_id."""
        endpoint = TeamGameLogs(team_id=1610612747, league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamGameLogs(
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
        endpoint = TeamGameLogs(team_id=1610612747)

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """TeamGameLogs has correct API path."""
        endpoint = TeamGameLogs(team_id=1610612747)

        assert endpoint.path == "teamgamelogs"

    def test_response_model_is_correct(self):
        """TeamGameLogs uses TeamGameLogsResponse model."""
        endpoint = TeamGameLogs(team_id=1610612747)

        assert endpoint.response_model is TeamGameLogsResponse

    def test_endpoint_is_frozen(self):
        """TeamGameLogs is immutable (frozen dataclass)."""
        endpoint = TeamGameLogs(team_id=1610612747)

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
