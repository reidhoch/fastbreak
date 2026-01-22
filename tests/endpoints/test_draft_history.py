from fastbreak.endpoints import DraftHistory
from fastbreak.models import DraftHistoryResponse


class TestDraftHistory:
    """Tests for DraftHistory endpoint."""

    def test_init_with_defaults(self):
        """DraftHistory uses sensible defaults."""
        endpoint = DraftHistory()

        assert endpoint.league_id == "00"
        assert endpoint.season is None
        assert endpoint.team_id is None
        assert endpoint.round_num is None
        assert endpoint.round_pick is None
        assert endpoint.overall_pick is None
        assert endpoint.college is None

    def test_init_with_custom_league_id(self):
        """DraftHistory accepts custom league_id."""
        endpoint = DraftHistory(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """DraftHistory accepts custom season."""
        endpoint = DraftHistory(season="2024")

        assert endpoint.season == "2024"

    def test_init_with_custom_team_id(self):
        """DraftHistory accepts custom team_id."""
        endpoint = DraftHistory(team_id="1610612747")

        assert endpoint.team_id == "1610612747"

    def test_init_with_custom_round_num(self):
        """DraftHistory accepts custom round_num."""
        endpoint = DraftHistory(round_num="1")

        assert endpoint.round_num == "1"

    def test_init_with_custom_college(self):
        """DraftHistory accepts custom college."""
        endpoint = DraftHistory(college="Duke")

        assert endpoint.college == "Duke"

    def test_init_with_all_custom_params(self):
        """DraftHistory accepts all custom parameters."""
        endpoint = DraftHistory(
            league_id="00",
            season="2024",
            team_id="1610612747",
            round_num="1",
            round_pick="5",
            overall_pick="5",
            college="Duke",
        )

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024"
        assert endpoint.team_id == "1610612747"
        assert endpoint.round_num == "1"
        assert endpoint.round_pick == "5"
        assert endpoint.overall_pick == "5"
        assert endpoint.college == "Duke"

    def test_params_returns_minimal_dict(self):
        """params() returns only LeagueID when no filters set."""
        endpoint = DraftHistory()

        params = endpoint.params()

        assert params == {"LeagueID": "00"}

    def test_params_includes_optional_filters(self):
        """params() includes optional parameters when set."""
        endpoint = DraftHistory(
            season="2024",
            team_id="1610612747",
            round_num="1",
            college="Duke",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024",
            "TeamID": "1610612747",
            "RoundNum": "1",
            "College": "Duke",
        }

    def test_path_is_correct(self):
        """DraftHistory has correct API path."""
        endpoint = DraftHistory()

        assert endpoint.path == "drafthistory"

    def test_response_model_is_correct(self):
        """DraftHistory uses DraftHistoryResponse model."""
        endpoint = DraftHistory()

        assert endpoint.response_model is DraftHistoryResponse

    def test_endpoint_is_frozen(self):
        """DraftHistory is immutable (frozen dataclass)."""
        endpoint = DraftHistory()

        try:
            endpoint.season = "2024"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
