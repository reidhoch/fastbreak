from fastbreak.endpoints import TeamYearByYearStats
from fastbreak.models import TeamYearByYearStatsResponse


class TestTeamYearByYearStats:
    """Tests for TeamYearByYearStats endpoint."""

    def test_init_with_defaults(self):
        """TeamYearByYearStats uses sensible defaults."""
        endpoint = TeamYearByYearStats()

        assert endpoint.team_id == 0
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamYearByYearStats accepts team_id."""
        endpoint = TeamYearByYearStats(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season_type(self):
        """TeamYearByYearStats accepts custom season_type."""
        endpoint = TeamYearByYearStats(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """TeamYearByYearStats accepts custom per_mode."""
        endpoint = TeamYearByYearStats(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamYearByYearStats(
            team_id=1610612743,
            season_type="Playoffs",
            per_mode="Totals",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["SeasonType"] == "Playoffs"
        assert params["PerMode"] == "Totals"
        assert params["LeagueID"] == "00"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamYearByYearStats()

        params = endpoint.params()

        assert params["TeamID"] == "0"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """TeamYearByYearStats has correct API path."""
        endpoint = TeamYearByYearStats()

        assert endpoint.path == "teamyearbyyearstats"

    def test_response_model_is_correct(self):
        """TeamYearByYearStats uses TeamYearByYearStatsResponse model."""
        endpoint = TeamYearByYearStats()

        assert endpoint.response_model is TeamYearByYearStatsResponse

    def test_endpoint_is_frozen(self):
        """TeamYearByYearStats is immutable (frozen dataclass)."""
        endpoint = TeamYearByYearStats()

        try:
            endpoint.team_id = 1610612743  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
