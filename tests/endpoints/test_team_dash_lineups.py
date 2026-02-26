import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamDashLineups
from fastbreak.models import TeamDashLineupsResponse
from fastbreak.seasons import get_season_from_date


class TestTeamDashLineups:
    """Tests for TeamDashLineups endpoint."""

    def test_init_with_defaults(self):
        """TeamDashLineups uses sensible defaults."""
        endpoint = TeamDashLineups(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.group_quantity == 5
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_init_with_team_id(self):
        """TeamDashLineups accepts team_id."""
        endpoint = TeamDashLineups(team_id=1610612743)

        assert endpoint.team_id == 1610612743

    def test_init_with_group_quantity(self):
        """TeamDashLineups accepts group_quantity."""
        endpoint = TeamDashLineups(team_id=1610612747, group_quantity=2)

        assert endpoint.group_quantity == 2

    def test_init_with_custom_season(self):
        """TeamDashLineups accepts custom season."""
        endpoint = TeamDashLineups(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamDashLineups accepts custom season_type."""
        endpoint = TeamDashLineups(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """TeamDashLineups accepts custom per_mode."""
        endpoint = TeamDashLineups(team_id=1610612747, per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_custom_measure_type(self):
        """TeamDashLineups accepts custom measure_type."""
        endpoint = TeamDashLineups(team_id=1610612747, measure_type="Advanced")

        assert endpoint.measure_type == "Advanced"

    def test_init_with_last_n_games(self):
        """TeamDashLineups accepts last_n_games filter."""
        endpoint = TeamDashLineups(team_id=1610612747, last_n_games=10)

        assert endpoint.last_n_games == 10

    def test_init_with_pace_plus_rank(self):
        """TeamDashLineups accepts pace/plus/rank settings."""
        endpoint = TeamDashLineups(
            team_id=1610612747,
            pace_adjust="Y",
            plus_minus="Y",
            rank="Y",
        )

        assert endpoint.pace_adjust == "Y"
        assert endpoint.plus_minus == "Y"
        assert endpoint.rank == "Y"

    def test_init_with_all_optional_params(self):
        """TeamDashLineups accepts all optional parameters."""
        endpoint = TeamDashLineups(
            team_id=1610612747,
            outcome="W",
            location="Home",
            season_segment="Post All-Star",
            date_from="01/01/2024",
            date_to="03/31/2024",
            vs_conference="West",
            vs_division="Pacific",
            game_segment="First Half",
            shot_clock_range="24-22",
        )

        assert endpoint.outcome == "W"
        assert endpoint.location == "Home"
        assert endpoint.season_segment == "Post All-Star"
        assert endpoint.date_from == "01/01/2024"
        assert endpoint.date_to == "03/31/2024"
        assert endpoint.vs_conference == "West"
        assert endpoint.vs_division == "Pacific"
        assert endpoint.game_segment == "First Half"
        assert endpoint.shot_clock_range == "24-22"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamDashLineups(
            team_id=1610612743,
            group_quantity=5,
            season="2023-24",
            last_n_games=10,
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["GroupQuantity"] == "5"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["LastNGames"] == "10"

    def test_params_with_two_man_lineups(self):
        """params() correctly handles 2-man lineup groupings."""
        endpoint = TeamDashLineups(
            team_id=1610612743,
            group_quantity=2,
        )

        params = endpoint.params()

        assert params["GroupQuantity"] == "2"

    def test_params_includes_optional_params(self):
        """params() includes optional parameters when set."""
        endpoint = TeamDashLineups(
            team_id=1610612747,
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_params_excludes_none_values(self):
        """params() excludes None optional parameters."""
        endpoint = TeamDashLineups(team_id=1610612747)

        params = endpoint.params()

        assert "Outcome" not in params
        assert "Location" not in params
        assert "SeasonSegment" not in params

    def test_path_is_correct(self):
        """TeamDashLineups has correct API path."""
        endpoint = TeamDashLineups(team_id=1610612747)

        assert endpoint.path == "teamdashlineups"

    def test_response_model_is_correct(self):
        """TeamDashLineups uses TeamDashLineupsResponse model."""
        endpoint = TeamDashLineups(team_id=1610612747)

        assert endpoint.response_model is TeamDashLineupsResponse

    def test_endpoint_is_frozen(self):
        """TeamDashLineups is immutable (frozen dataclass)."""
        endpoint = TeamDashLineups(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
