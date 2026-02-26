import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamVsPlayer
from fastbreak.models import TeamVsPlayerResponse
from fastbreak.seasons import get_season_from_date


class TestTeamVsPlayer:
    """Tests for TeamVsPlayer endpoint."""

    def test_init_with_defaults(self):
        """TeamVsPlayer uses sensible defaults."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544)

        assert endpoint.team_id == 1610612747
        assert endpoint.vs_player_id == 2544
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.league_id == "00"

    def test_init_with_team_id(self):
        """TeamVsPlayer accepts team_id."""
        endpoint = TeamVsPlayer(team_id=1610612743, vs_player_id=2544)

        assert endpoint.team_id == 1610612743

    def test_init_with_vs_player_id(self):
        """TeamVsPlayer accepts vs_player_id."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544)

        assert endpoint.vs_player_id == 2544

    def test_init_with_custom_season(self):
        """TeamVsPlayer accepts custom season."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = TeamVsPlayer(
            team_id=1610612743,
            vs_player_id=2544,
            season="2023-24",
            season_type="Playoffs",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612743"
        assert params["VsPlayerID"] == "2544"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Playoffs"
        assert params["LeagueID"] == "00"

    def test_params_with_defaults(self):
        """params() returns default parameters correctly."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544)

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["VsPlayerID"] == "2544"
        assert params["Season"] == get_season_from_date()
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"

    def test_path_is_correct(self):
        """TeamVsPlayer has correct API path."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544)

        assert endpoint.path == "teamvsplayer"

    def test_response_model_is_correct(self):
        """TeamVsPlayer uses TeamVsPlayerResponse model."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544)

        assert endpoint.response_model is TeamVsPlayerResponse

    def test_endpoint_is_frozen(self):
        """TeamVsPlayer is immutable (frozen dataclass)."""
        endpoint = TeamVsPlayer(team_id=1610612747, vs_player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = 1610612743  # type: ignore[misc]
