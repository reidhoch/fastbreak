from pydantic import ValidationError

from fastbreak.endpoints import TeamDashPtReb
from fastbreak.models import TeamDashPtRebResponse


class TestTeamDashPtReb:
    """Tests for TeamDashPtReb endpoint."""

    def test_init_with_defaults(self):
        """TeamDashPtReb uses sensible defaults."""
        endpoint = TeamDashPtReb(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.period == 0
        assert endpoint.last_n_games == 0

    def test_init_with_team_id(self):
        """TeamDashPtReb accepts team_id."""
        endpoint = TeamDashPtReb(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamDashPtReb accepts custom season."""
        endpoint = TeamDashPtReb(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamDashPtReb accepts custom season_type."""
        endpoint = TeamDashPtReb(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """TeamDashPtReb accepts custom per_mode."""
        endpoint = TeamDashPtReb(team_id=1610612747, per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_last_n_games(self):
        """TeamDashPtReb accepts last_n_games filter."""
        endpoint = TeamDashPtReb(team_id=1610612747, last_n_games=10)

        assert endpoint.last_n_games == 10

    def test_init_with_period(self):
        """TeamDashPtReb accepts period filter."""
        endpoint = TeamDashPtReb(team_id=1610612747, period=4)

        assert endpoint.period == 4

    def test_init_with_all_optional_params(self):
        """TeamDashPtReb accepts all optional parameters."""
        endpoint = TeamDashPtReb(
            team_id=1610612747,
            outcome="W",
            location="Home",
            season_segment="Post All-Star",
            date_from="01/01/2024",
            date_to="03/31/2024",
            vs_conference="West",
            vs_division="Pacific",
            game_segment="First Half",
        )

        assert endpoint.outcome == "W"
        assert endpoint.location == "Home"
        assert endpoint.season_segment == "Post All-Star"
        assert endpoint.date_from == "01/01/2024"
        assert endpoint.date_to == "03/31/2024"
        assert endpoint.vs_conference == "West"
        assert endpoint.vs_division == "Pacific"
        assert endpoint.game_segment == "First Half"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamDashPtReb(
            team_id=1610612743,
            season="2023-24",
            last_n_games=10,
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["LastNGames"] == "10"
        assert params["Month"] == "0"
        assert params["OpponentTeamID"] == "0"
        assert params["Period"] == "0"

    def test_params_includes_optional_params(self):
        """params() includes optional parameters when set."""
        endpoint = TeamDashPtReb(
            team_id=1610612747,
            outcome="W",
            location="Home",
            game_segment="First Half",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["GameSegment"] == "First Half"

    def test_params_includes_empty_strings_for_unset(self):
        """params() includes empty strings for certain params when not set."""
        endpoint = TeamDashPtReb(team_id=1610612747)

        params = endpoint.params()

        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""
        assert params["Outcome"] == ""
        assert params["Location"] == ""
        assert params["GameSegment"] == ""

    def test_params_excludes_none_values(self):
        """params() excludes None optional parameters."""
        endpoint = TeamDashPtReb(team_id=1610612747)

        params = endpoint.params()

        assert "SeasonSegment" not in params
        assert "VsConference" not in params
        assert "VsDivision" not in params

    def test_path_is_correct(self):
        """TeamDashPtReb has correct API path."""
        endpoint = TeamDashPtReb(team_id=1610612747)

        assert endpoint.path == "teamdashptreb"

    def test_response_model_is_correct(self):
        """TeamDashPtReb uses TeamDashPtRebResponse model."""
        endpoint = TeamDashPtReb(team_id=1610612747)

        assert endpoint.response_model is TeamDashPtRebResponse

    def test_endpoint_is_frozen(self):
        """TeamDashPtReb is immutable (frozen dataclass)."""
        endpoint = TeamDashPtReb(team_id=1610612747)

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
