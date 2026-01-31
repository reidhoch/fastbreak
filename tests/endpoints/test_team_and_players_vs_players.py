import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamAndPlayersVsPlayers
from fastbreak.models import TeamAndPlayersVsPlayersResponse


class TestTeamAndPlayersVsPlayers:
    """Tests for TeamAndPlayersVsPlayers endpoint."""

    def test_init_with_defaults(self):
        """TeamAndPlayersVsPlayers uses sensible defaults."""
        endpoint = TeamAndPlayersVsPlayers(team_id=1610612747, vs_team_id=1610612744)

        assert endpoint.league_id == "00"
        assert endpoint.team_id == 1610612747
        assert endpoint.vs_team_id == 1610612744
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_init_with_team_ids(self):
        """TeamAndPlayersVsPlayers accepts team IDs."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612743,
            vs_team_id=1610612747,
        )

        assert endpoint.team_id == 1610612743
        assert endpoint.vs_team_id == 1610612747

    def test_init_with_custom_season(self):
        """TeamAndPlayersVsPlayers accepts custom season."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747, vs_team_id=1610612744, season="2023-24"
        )

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """TeamAndPlayersVsPlayers accepts custom season_type."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747, vs_team_id=1610612744, season_type="Playoffs"
        )

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """TeamAndPlayersVsPlayers accepts custom per_mode."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747, vs_team_id=1610612744, per_mode="Totals"
        )

        assert endpoint.per_mode == "Totals"

    def test_init_with_custom_measure_type(self):
        """TeamAndPlayersVsPlayers accepts custom measure_type."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747, vs_team_id=1610612744, measure_type="Advanced"
        )

        assert endpoint.measure_type == "Advanced"

    def test_init_with_player_ids(self):
        """TeamAndPlayersVsPlayers accepts player ID filters."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747,
            vs_team_id=1610612744,
            player_id1=203999,
            player_id2=1627750,
            vs_player_id1=2544,
            vs_player_id2=203076,
        )

        assert endpoint.player_id1 == 203999
        assert endpoint.player_id2 == 1627750
        assert endpoint.vs_player_id1 == 2544
        assert endpoint.vs_player_id2 == 203076

    def test_init_with_pace_plus_rank(self):
        """TeamAndPlayersVsPlayers accepts pace/plus/rank settings."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747,
            vs_team_id=1610612744,
            pace_adjust="Y",
            plus_minus="Y",
            rank="Y",
        )

        assert endpoint.pace_adjust == "Y"
        assert endpoint.plus_minus == "Y"
        assert endpoint.rank == "Y"

    def test_init_with_all_optional_params(self):
        """TeamAndPlayersVsPlayers accepts all optional parameters."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747,
            vs_team_id=1610612744,
            conference="West",
            division="Pacific",
            game_segment="First Half",
            last_n_games=10,
            location="Home",
            month=12,
            opponent_team_id=1610612744,
            outcome="W",
            period=1,
            date_from="01/01/2024",
            date_to="03/31/2024",
            vs_conference="East",
            vs_division="Atlantic",
        )

        assert endpoint.conference == "West"
        assert endpoint.division == "Pacific"
        assert endpoint.game_segment == "First Half"
        assert endpoint.last_n_games == 10
        assert endpoint.location == "Home"
        assert endpoint.month == 12
        assert endpoint.opponent_team_id == 1610612744
        assert endpoint.outcome == "W"
        assert endpoint.period == 1
        assert endpoint.date_from == "01/01/2024"
        assert endpoint.date_to == "03/31/2024"
        assert endpoint.vs_conference == "East"
        assert endpoint.vs_division == "Atlantic"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612743,
            vs_team_id=1610612747,
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["VsTeamID"] == "1610612747"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"

    def test_params_includes_player_ids(self):
        """params() includes player ID parameters."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747,
            vs_team_id=1610612744,
            player_id1=203999,
            vs_player_id1=2544,
        )

        params = endpoint.params()

        assert params["PlayerID1"] == "203999"
        assert params["VsPlayerID1"] == "2544"
        assert params["PlayerID2"] == "0"
        assert params["VsPlayerID2"] == "0"

    def test_params_includes_optional_filters(self):
        """params() includes optional filter parameters."""
        endpoint = TeamAndPlayersVsPlayers(
            team_id=1610612747,
            vs_team_id=1610612744,
            location="Home",
            outcome="W",
        )

        params = endpoint.params()

        assert params["Location"] == "Home"
        assert params["Outcome"] == "W"

    def test_path_is_correct(self):
        """TeamAndPlayersVsPlayers has correct API path."""
        endpoint = TeamAndPlayersVsPlayers(team_id=1610612747, vs_team_id=1610612744)

        assert endpoint.path == "teamandplayersvsplayers"

    def test_response_model_is_correct(self):
        """TeamAndPlayersVsPlayers uses TeamAndPlayersVsPlayersResponse model."""
        endpoint = TeamAndPlayersVsPlayers(team_id=1610612747, vs_team_id=1610612744)

        assert endpoint.response_model is TeamAndPlayersVsPlayersResponse

    def test_endpoint_is_frozen(self):
        """TeamAndPlayersVsPlayers is immutable (frozen dataclass)."""
        endpoint = TeamAndPlayersVsPlayers(team_id=1610612747, vs_team_id=1610612744)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
