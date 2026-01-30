from pydantic import ValidationError

from fastbreak.endpoints import TeamPlayerOnOffDetails
from fastbreak.models import TeamPlayerOnOffDetailsResponse


class TestTeamPlayerOnOffDetails:
    """Tests for TeamPlayerOnOffDetails endpoint."""

    def test_init_with_defaults(self):
        """TeamPlayerOnOffDetails uses sensible defaults."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamPlayerOnOffDetails accepts team_id."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamPlayerOnOffDetails accepts custom season."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_per_mode(self):
        """TeamPlayerOnOffDetails accepts custom per_mode."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747, per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamPlayerOnOffDetails(
            team_id=1610612743,
            season="2023-24",
            season_type="Playoffs",
            per_mode="Per36",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Playoffs"
        assert params["PerMode"] == "Per36"
        assert params["LeagueID"] == "00"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747)

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["Month"] == "0"
        assert params["OpponentTeamID"] == "0"

    def test_path_is_correct(self):
        """TeamPlayerOnOffDetails has correct API path."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747)

        assert endpoint.path == "teamplayeronoffdetails"

    def test_response_model_is_correct(self):
        """TeamPlayerOnOffDetails uses TeamPlayerOnOffDetailsResponse model."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747)

        assert endpoint.response_model is TeamPlayerOnOffDetailsResponse

    def test_endpoint_is_frozen(self):
        """TeamPlayerOnOffDetails is immutable (frozen dataclass)."""
        endpoint = TeamPlayerOnOffDetails(team_id=1610612747)

        try:
            endpoint.team_id = 1610612743  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
