from fastbreak.endpoints import LeverageLeaders
from fastbreak.models import LeverageLeadersResponse


class TestLeverageLeaders:
    """Tests for LeverageLeaders endpoint."""

    def test_init_with_defaults(self):
        """LeverageLeaders uses sensible defaults."""
        endpoint = LeverageLeaders()

        assert endpoint.league_id == "00"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.season_year == "2025-26"

    def test_init_with_custom_league_id(self):
        """LeverageLeaders accepts custom league_id."""
        endpoint = LeverageLeaders(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_type(self):
        """LeverageLeaders accepts custom season_type."""
        endpoint = LeverageLeaders(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_season_year(self):
        """LeverageLeaders accepts custom season_year."""
        endpoint = LeverageLeaders(season_year="2024-25")

        assert endpoint.season_year == "2024-25"

    def test_init_with_all_custom_params(self):
        """LeverageLeaders accepts all custom parameters."""
        endpoint = LeverageLeaders(
            league_id="10",
            season_type="Playoffs",
            season_year="2024-25",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.season_year == "2024-25"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeverageLeaders(
            league_id="00",
            season_type="Regular Season",
            season_year="2025-26",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonType": "Regular Season",
            "Season": "2025-26",
        }

    def test_path_is_correct(self):
        """LeverageLeaders has correct API path."""
        endpoint = LeverageLeaders()

        assert endpoint.path == "leverageleaders"

    def test_response_model_is_correct(self):
        """LeverageLeaders uses LeverageLeadersResponse model."""
        endpoint = LeverageLeaders()

        assert endpoint.response_model is LeverageLeadersResponse

    def test_endpoint_is_frozen(self):
        """LeverageLeaders is immutable (frozen dataclass)."""
        endpoint = LeverageLeaders()

        try:
            endpoint.season_year = "2024-25"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
