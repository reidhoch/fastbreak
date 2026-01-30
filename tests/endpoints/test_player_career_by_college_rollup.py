from pydantic import ValidationError

from fastbreak.endpoints import PlayerCareerByCollegeRollup
from fastbreak.models import PlayerCareerByCollegeRollupResponse


class TestPlayerCareerByCollegeRollup:
    """Tests for PlayerCareerByCollegeRollup endpoint."""

    def test_init_with_defaults(self):
        """PlayerCareerByCollegeRollup uses sensible defaults."""
        endpoint = PlayerCareerByCollegeRollup()

        assert endpoint.league_id == "00"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.season is None

    def test_init_with_custom_league_id(self):
        """PlayerCareerByCollegeRollup accepts custom league_id."""
        endpoint = PlayerCareerByCollegeRollup(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_per_mode(self):
        """PlayerCareerByCollegeRollup accepts custom per_mode."""
        endpoint = PlayerCareerByCollegeRollup(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_custom_season_type(self):
        """PlayerCareerByCollegeRollup accepts custom season_type."""
        endpoint = PlayerCareerByCollegeRollup(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_season(self):
        """PlayerCareerByCollegeRollup accepts optional season."""
        endpoint = PlayerCareerByCollegeRollup(season="2024-25")

        assert endpoint.season == "2024-25"

    def test_init_with_all_custom_params(self):
        """PlayerCareerByCollegeRollup accepts all custom parameters."""
        endpoint = PlayerCareerByCollegeRollup(
            league_id="10",
            per_mode="Totals",
            season_type="Playoffs",
            season="2023-24",
        )

        assert endpoint.league_id == "10"
        assert endpoint.per_mode == "Totals"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.season == "2023-24"

    def test_params_returns_correct_dict_without_season(self):
        """params() returns correctly formatted parameters without season."""
        endpoint = PlayerCareerByCollegeRollup()

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "PerMode": "PerGame",
            "SeasonType": "Regular Season",
        }

    def test_params_returns_correct_dict_with_season(self):
        """params() returns correctly formatted parameters with season."""
        endpoint = PlayerCareerByCollegeRollup(season="2024-25")

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "PerMode": "PerGame",
            "SeasonType": "Regular Season",
            "Season": "2024-25",
        }

    def test_path_is_correct(self):
        """PlayerCareerByCollegeRollup has correct API path."""
        endpoint = PlayerCareerByCollegeRollup()

        assert endpoint.path == "playercareerbycollegerollup"

    def test_response_model_is_correct(self):
        """PlayerCareerByCollegeRollup uses correct response model."""
        endpoint = PlayerCareerByCollegeRollup()

        assert endpoint.response_model is PlayerCareerByCollegeRollupResponse

    def test_endpoint_is_frozen(self):
        """PlayerCareerByCollegeRollup is immutable (frozen dataclass)."""
        endpoint = PlayerCareerByCollegeRollup()

        try:
            endpoint.per_mode = "Totals"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
