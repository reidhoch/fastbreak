from pydantic import ValidationError

from fastbreak.endpoints import LeagueSeasonMatchups
from fastbreak.models import LeagueSeasonMatchupsResponse


class TestLeagueSeasonMatchups:
    """Tests for LeagueSeasonMatchups endpoint."""

    def test_init_with_defaults(self):
        """LeagueSeasonMatchups uses sensible defaults."""
        endpoint = LeagueSeasonMatchups()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.off_team_id is None
        assert endpoint.def_team_id is None
        assert endpoint.off_player_id is None
        assert endpoint.def_player_id is None

    def test_init_with_custom_season(self):
        """LeagueSeasonMatchups accepts custom season."""
        endpoint = LeagueSeasonMatchups(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """LeagueSeasonMatchups accepts custom season_type."""
        endpoint = LeagueSeasonMatchups(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_team_filters(self):
        """LeagueSeasonMatchups accepts team ID filters."""
        endpoint = LeagueSeasonMatchups(
            off_team_id="1610612754",
            def_team_id="1610612765",
        )

        assert endpoint.off_team_id == "1610612754"
        assert endpoint.def_team_id == "1610612765"

    def test_init_with_player_filters(self):
        """LeagueSeasonMatchups accepts player ID filters."""
        endpoint = LeagueSeasonMatchups(
            off_player_id="201566",
            def_player_id="203507",
        )

        assert endpoint.off_player_id == "201566"
        assert endpoint.def_player_id == "203507"

    def test_init_with_all_custom_params(self):
        """LeagueSeasonMatchups accepts all custom parameters."""
        endpoint = LeagueSeasonMatchups(
            league_id="00",
            season="2023-24",
            season_type="Playoffs",
            per_mode="Totals",
            off_team_id="1610612754",
            def_team_id="1610612765",
            off_player_id="201566",
            def_player_id="203507",
        )

        assert endpoint.league_id == "00"
        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.off_team_id == "1610612754"
        assert endpoint.def_team_id == "1610612765"
        assert endpoint.off_player_id == "201566"
        assert endpoint.def_player_id == "203507"

    def test_params_returns_correct_dict_minimal(self):
        """params() returns correctly formatted parameters without optional filters."""
        endpoint = LeagueSeasonMatchups()

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
        }

    def test_params_includes_team_filters(self):
        """params() includes team filters when set."""
        endpoint = LeagueSeasonMatchups(
            off_team_id="1610612754",
            def_team_id="1610612765",
        )

        params = endpoint.params()

        assert params["OffTeamID"] == "1610612754"
        assert params["DefTeamID"] == "1610612765"

    def test_params_includes_player_filters(self):
        """params() includes player filters when set."""
        endpoint = LeagueSeasonMatchups(
            off_player_id="201566",
            def_player_id="203507",
        )

        params = endpoint.params()

        assert params["OffPlayerID"] == "201566"
        assert params["DefPlayerID"] == "203507"

    def test_path_is_correct(self):
        """LeagueSeasonMatchups has correct API path."""
        endpoint = LeagueSeasonMatchups()

        assert endpoint.path == "leagueseasonmatchups"

    def test_response_model_is_correct(self):
        """LeagueSeasonMatchups uses LeagueSeasonMatchupsResponse model."""
        endpoint = LeagueSeasonMatchups()

        assert endpoint.response_model is LeagueSeasonMatchupsResponse

    def test_endpoint_is_frozen(self):
        """LeagueSeasonMatchups is immutable (frozen dataclass)."""
        endpoint = LeagueSeasonMatchups()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
