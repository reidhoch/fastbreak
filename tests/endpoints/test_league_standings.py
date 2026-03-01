from fastbreak.endpoints import LeagueStandings
from fastbreak.models import LeagueStandingsResponse


class TestLeagueStandings:
    """Tests for LeagueStandings endpoint.

    Construction, params(), and frozen-immutability are covered by property
    tests in tests/test_models_properties.py. Only ClassVar checks remain here.
    """

    def test_path_is_correct(self):
        assert LeagueStandings.path == "leaguestandingsv3"

    def test_response_model_is_correct(self):
        assert LeagueStandings.response_model is LeagueStandingsResponse
