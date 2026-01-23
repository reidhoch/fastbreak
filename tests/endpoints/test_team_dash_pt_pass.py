from fastbreak.endpoints import TeamDashPtPass
from fastbreak.models import TeamDashPtPassResponse


class TestTeamDashPtPass:
    """Tests for TeamDashPtPass endpoint."""

    def test_init_with_defaults(self):
        """TeamDashPtPass uses sensible defaults."""
        endpoint = TeamDashPtPass()

        assert endpoint.team_id == 0
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.last_n_games == 0

    def test_init_with_team_id(self):
        """TeamDashPtPass accepts team_id."""
        endpoint = TeamDashPtPass(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_custom_season(self):
        """TeamDashPtPass accepts custom season."""
        endpoint = TeamDashPtPass(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamDashPtPass accepts custom season_type."""
        endpoint = TeamDashPtPass(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """TeamDashPtPass accepts custom per_mode."""
        endpoint = TeamDashPtPass(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_last_n_games(self):
        """TeamDashPtPass accepts last_n_games filter."""
        endpoint = TeamDashPtPass(last_n_games=10)

        assert endpoint.last_n_games == 10

    def test_init_with_all_optional_params(self):
        """TeamDashPtPass accepts all optional parameters."""
        endpoint = TeamDashPtPass(
            outcome="W",
            location="Home",
            season_segment="Post All-Star",
            date_from="01/01/2024",
            date_to="03/31/2024",
            vs_conference="West",
            vs_division="Pacific",
        )

        assert endpoint.outcome == "W"
        assert endpoint.location == "Home"
        assert endpoint.season_segment == "Post All-Star"
        assert endpoint.date_from == "01/01/2024"
        assert endpoint.date_to == "03/31/2024"
        assert endpoint.vs_conference == "West"
        assert endpoint.vs_division == "Pacific"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamDashPtPass(
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

    def test_params_includes_optional_params(self):
        """params() includes optional parameters when set."""
        endpoint = TeamDashPtPass(
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_params_excludes_none_values(self):
        """params() excludes None optional parameters."""
        endpoint = TeamDashPtPass()

        params = endpoint.params()

        assert "Outcome" not in params
        assert "Location" not in params
        assert "SeasonSegment" not in params

    def test_params_includes_empty_date_strings(self):
        """params() includes empty strings for date params when not set."""
        endpoint = TeamDashPtPass()

        params = endpoint.params()

        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""

    def test_params_includes_date_values(self):
        """params() includes date values when set."""
        endpoint = TeamDashPtPass(
            date_from="01/01/2024",
            date_to="03/31/2024",
        )

        params = endpoint.params()

        assert params["DateFrom"] == "01/01/2024"
        assert params["DateTo"] == "03/31/2024"

    def test_path_is_correct(self):
        """TeamDashPtPass has correct API path."""
        endpoint = TeamDashPtPass()

        assert endpoint.path == "teamdashptpass"

    def test_response_model_is_correct(self):
        """TeamDashPtPass uses TeamDashPtPassResponse model."""
        endpoint = TeamDashPtPass()

        assert endpoint.response_model is TeamDashPtPassResponse

    def test_endpoint_is_frozen(self):
        """TeamDashPtPass is immutable (frozen dataclass)."""
        endpoint = TeamDashPtPass()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
