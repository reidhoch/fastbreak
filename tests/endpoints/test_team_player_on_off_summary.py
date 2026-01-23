from fastbreak.endpoints import TeamPlayerOnOffSummary
from fastbreak.models import TeamPlayerOnOffSummaryResponse


class TestTeamPlayerOnOffSummary:
    """Tests for TeamPlayerOnOffSummary endpoint."""

    def test_init_with_defaults(self):
        """TeamPlayerOnOffSummary uses sensible defaults."""
        endpoint = TeamPlayerOnOffSummary()

        assert endpoint.team_id == 0
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamPlayerOnOffSummary accepts team_id."""
        endpoint = TeamPlayerOnOffSummary(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamPlayerOnOffSummary accepts custom season."""
        endpoint = TeamPlayerOnOffSummary(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_per_mode(self):
        """TeamPlayerOnOffSummary accepts custom per_mode."""
        endpoint = TeamPlayerOnOffSummary(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamPlayerOnOffSummary(
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
        endpoint = TeamPlayerOnOffSummary()

        params = endpoint.params()

        assert params["TeamID"] == "0"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["Month"] == "0"
        assert params["OpponentTeamID"] == "0"

    def test_path_is_correct(self):
        """TeamPlayerOnOffSummary has correct API path."""
        endpoint = TeamPlayerOnOffSummary()

        assert endpoint.path == "teamplayeronoffsummary"

    def test_response_model_is_correct(self):
        """TeamPlayerOnOffSummary uses TeamPlayerOnOffSummaryResponse model."""
        endpoint = TeamPlayerOnOffSummary()

        assert endpoint.response_model is TeamPlayerOnOffSummaryResponse

    def test_endpoint_is_frozen(self):
        """TeamPlayerOnOffSummary is immutable (frozen dataclass)."""
        endpoint = TeamPlayerOnOffSummary()

        try:
            endpoint.team_id = 1610612743  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
