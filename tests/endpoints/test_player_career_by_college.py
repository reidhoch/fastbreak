from fastbreak.endpoints import PlayerCareerByCollege
from fastbreak.models import PlayerCareerByCollegeResponse


class TestPlayerCareerByCollege:
    """Tests for PlayerCareerByCollege endpoint."""

    def test_init_with_college(self):
        """PlayerCareerByCollege requires college."""
        endpoint = PlayerCareerByCollege(college="Duke")

        assert endpoint.college == "Duke"

    def test_init_with_defaults(self):
        """PlayerCareerByCollege uses sensible defaults."""
        endpoint = PlayerCareerByCollege(college="Duke")

        assert endpoint.league_id == "00"
        assert endpoint.per_mode == "Totals"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.season is None

    def test_init_with_custom_league_id(self):
        """PlayerCareerByCollege accepts custom league_id."""
        endpoint = PlayerCareerByCollege(college="Duke", league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_per_mode(self):
        """PlayerCareerByCollege accepts custom per_mode."""
        endpoint = PlayerCareerByCollege(college="Duke", per_mode="PerGame")

        assert endpoint.per_mode == "PerGame"

    def test_init_with_custom_season_type(self):
        """PlayerCareerByCollege accepts custom season_type."""
        endpoint = PlayerCareerByCollege(college="Duke", season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_season(self):
        """PlayerCareerByCollege accepts optional season."""
        endpoint = PlayerCareerByCollege(college="Duke", season="2024-25")

        assert endpoint.season == "2024-25"

    def test_init_with_all_custom_params(self):
        """PlayerCareerByCollege accepts all custom parameters."""
        endpoint = PlayerCareerByCollege(
            college="Kentucky",
            league_id="10",
            per_mode="PerGame",
            season_type="Playoffs",
            season="2023-24",
        )

        assert endpoint.college == "Kentucky"
        assert endpoint.league_id == "10"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.season == "2023-24"

    def test_params_returns_correct_dict_without_season(self):
        """params() returns correctly formatted parameters without season."""
        endpoint = PlayerCareerByCollege(college="Duke")

        params = endpoint.params()

        assert params == {
            "College": "Duke",
            "LeagueID": "00",
            "PerMode": "Totals",
            "SeasonType": "Regular Season",
        }

    def test_params_returns_correct_dict_with_season(self):
        """params() returns correctly formatted parameters with season."""
        endpoint = PlayerCareerByCollege(college="Duke", season="2024-25")

        params = endpoint.params()

        assert params == {
            "College": "Duke",
            "LeagueID": "00",
            "PerMode": "Totals",
            "SeasonType": "Regular Season",
            "Season": "2024-25",
        }

    def test_path_is_correct(self):
        """PlayerCareerByCollege has correct API path."""
        endpoint = PlayerCareerByCollege(college="Duke")

        assert endpoint.path == "playercareerbycollege"

    def test_response_model_is_correct(self):
        """PlayerCareerByCollege uses PlayerCareerByCollegeResponse model."""
        endpoint = PlayerCareerByCollege(college="Duke")

        assert endpoint.response_model is PlayerCareerByCollegeResponse

    def test_endpoint_is_frozen(self):
        """PlayerCareerByCollege is immutable (frozen dataclass)."""
        endpoint = PlayerCareerByCollege(college="Duke")

        try:
            endpoint.college = "Kentucky"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
