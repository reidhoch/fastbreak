from fastbreak.endpoints import TeamEstimatedMetrics
from fastbreak.models import TeamEstimatedMetricsResponse


class TestTeamEstimatedMetrics:
    """Tests for TeamEstimatedMetrics endpoint."""

    def test_init_with_defaults(self):
        """TeamEstimatedMetrics uses sensible defaults."""
        endpoint = TeamEstimatedMetrics()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"

    def test_init_with_custom_season(self):
        """TeamEstimatedMetrics accepts custom season."""
        endpoint = TeamEstimatedMetrics(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamEstimatedMetrics accepts custom season_type."""
        endpoint = TeamEstimatedMetrics(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_league_id(self):
        """TeamEstimatedMetrics accepts custom league_id."""
        endpoint = TeamEstimatedMetrics(league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamEstimatedMetrics(
            season="2023-24",
            season_type="Playoffs",
        )

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Playoffs"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamEstimatedMetrics()

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"

    def test_path_is_correct(self):
        """TeamEstimatedMetrics has correct API path."""
        endpoint = TeamEstimatedMetrics()

        assert endpoint.path == "teamestimatedmetrics"

    def test_response_model_is_correct(self):
        """TeamEstimatedMetrics uses TeamEstimatedMetricsResponse model."""
        endpoint = TeamEstimatedMetrics()

        assert endpoint.response_model is TeamEstimatedMetricsResponse

    def test_endpoint_is_frozen(self):
        """TeamEstimatedMetrics is immutable (frozen dataclass)."""
        endpoint = TeamEstimatedMetrics()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
