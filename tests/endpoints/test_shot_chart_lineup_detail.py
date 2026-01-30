from pydantic import ValidationError

from fastbreak.endpoints import ShotChartLineupDetail
from fastbreak.models import ShotChartLineupDetailResponse


class TestShotChartLineupDetail:
    """Tests for ShotChartLineupDetail endpoint."""

    def test_init_with_defaults(self):
        """ShotChartLineupDetail uses sensible defaults."""
        endpoint = ShotChartLineupDetail(team_id=1610612747)

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.team_id == 1610612747
        assert endpoint.context_measure == "FGA"

    def test_init_with_custom_league_id(self):
        """ShotChartLineupDetail accepts custom league_id."""
        endpoint = ShotChartLineupDetail(team_id=1610612747, league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """ShotChartLineupDetail accepts custom season."""
        endpoint = ShotChartLineupDetail(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """ShotChartLineupDetail accepts custom season_type."""
        endpoint = ShotChartLineupDetail(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_team_id(self):
        """ShotChartLineupDetail accepts custom team_id."""
        endpoint = ShotChartLineupDetail(team_id=1610612747)

        assert endpoint.team_id == 1610612747

    def test_init_with_custom_context_measure(self):
        """ShotChartLineupDetail accepts custom context_measure."""
        endpoint = ShotChartLineupDetail(team_id=1610612747, context_measure="FG3A")

        assert endpoint.context_measure == "FG3A"

    def test_init_with_game_id(self):
        """ShotChartLineupDetail accepts game_id filter."""
        endpoint = ShotChartLineupDetail(team_id=1610612747, game_id="0022400001")

        assert endpoint.game_id == "0022400001"

    def test_init_with_group_id(self):
        """ShotChartLineupDetail accepts group_id filter."""
        endpoint = ShotChartLineupDetail(team_id=1610612747, group_id="123-456-789")

        assert endpoint.group_id == "123-456-789"

    def test_init_with_all_optional_params(self):
        """ShotChartLineupDetail accepts all optional parameters."""
        endpoint = ShotChartLineupDetail(
            team_id=1610612747,
            game_id="0022400001",
            group_id="123-456-789",
            opponent_team_id=1610612744,
            period=1,
            last_n_games=10,
            month=12,
            location="Home",
            outcome="W",
            date_from="01/01/2024",
            date_to="03/31/2024",
            vs_conference="West",
            vs_division="Pacific",
            game_segment="First Half",
            season_segment="Post All-Star",
            context_filter="TEAM_ID",
        )

        assert endpoint.game_id == "0022400001"
        assert endpoint.group_id == "123-456-789"
        assert endpoint.opponent_team_id == 1610612744
        assert endpoint.period == 1
        assert endpoint.last_n_games == 10
        assert endpoint.month == 12
        assert endpoint.location == "Home"
        assert endpoint.outcome == "W"
        assert endpoint.date_from == "01/01/2024"
        assert endpoint.date_to == "03/31/2024"
        assert endpoint.vs_conference == "West"
        assert endpoint.vs_division == "Pacific"
        assert endpoint.game_segment == "First Half"
        assert endpoint.season_segment == "Post All-Star"
        assert endpoint.context_filter == "TEAM_ID"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = ShotChartLineupDetail(
            league_id="00",
            season="2024-25",
            season_type="Regular Season",
            team_id=1610612747,
            context_measure="FGA",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "TeamID": "1610612747",
            "ContextMeasure": "FGA",
        }

    def test_params_includes_optional_params(self):
        """params() includes optional parameters when set."""
        endpoint = ShotChartLineupDetail(
            team_id=1610612747,
            game_id="0022400001",
            group_id="123-456",
            period=2,
        )

        params = endpoint.params()

        assert params["GameID"] == "0022400001"
        assert params["GROUP_ID"] == "123-456"
        assert params["Period"] == "2"

    def test_params_excludes_none_values(self):
        """params() excludes None optional parameters."""
        endpoint = ShotChartLineupDetail(team_id=1610612747)

        params = endpoint.params()

        assert "GameID" not in params
        assert "GROUP_ID" not in params
        assert "OpponentTeamID" not in params

    def test_path_is_correct(self):
        """ShotChartLineupDetail has correct API path."""
        endpoint = ShotChartLineupDetail(team_id=1610612747)

        assert endpoint.path == "shotchartlineupdetail"

    def test_response_model_is_correct(self):
        """ShotChartLineupDetail uses ShotChartLineupDetailResponse model."""
        endpoint = ShotChartLineupDetail(team_id=1610612747)

        assert endpoint.response_model is ShotChartLineupDetailResponse

    def test_endpoint_is_frozen(self):
        """ShotChartLineupDetail is immutable (frozen dataclass)."""
        endpoint = ShotChartLineupDetail(team_id=1610612747)

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
