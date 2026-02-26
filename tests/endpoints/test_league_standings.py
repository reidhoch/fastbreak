from fastbreak.endpoints import LeagueStandings
from fastbreak.models import LeagueStandingsResponse
from fastbreak.seasons import get_season_from_date


class TestLeagueStandings:
    """Tests for LeagueStandings endpoint."""

    def test_init_with_defaults(self):
        """LeagueStandings uses sensible defaults."""
        endpoint = LeagueStandings()

        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.league_id == "00"

    def test_init_with_custom_season(self):
        """LeagueStandings accepts custom season."""
        endpoint = LeagueStandings(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """LeagueStandings accepts custom season type."""
        endpoint = LeagueStandings(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueStandings(
            season="2024-25",
            season_type="Regular Season",
            league_id="00",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
        }

    def test_path_is_correct(self):
        """LeagueStandings has correct API path."""
        endpoint = LeagueStandings()

        assert endpoint.path == "leaguestandingsv3"

    def test_response_model_is_correct(self):
        """LeagueStandings uses LeagueStandingsResponse model."""
        endpoint = LeagueStandings()

        assert endpoint.response_model is LeagueStandingsResponse
