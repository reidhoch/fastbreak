"""Tests for CumeStatsTeam endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints.cume_stats_team import CumeStatsTeam
from fastbreak.models.cume_stats_team import CumeStatsTeamResponse


class TestCumeStatsTeam:
    """Tests for CumeStatsTeam endpoint."""

    def test_init_with_defaults(self):
        """CumeStatsTeam uses sensible defaults."""
        endpoint = CumeStatsTeam(team_id=1610612747)

        assert endpoint.league_id == "00"
        assert endpoint.season == "2025"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.team_id == 1610612747
        assert endpoint.game_ids == ""

    def test_init_with_custom_params(self):
        """CumeStatsTeam accepts custom parameters."""
        endpoint = CumeStatsTeam(
            league_id="10",
            season="2026",
            season_type="Playoffs",
            team_id=1610612745,
            game_ids="0022500617,0022500618",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2026"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.team_id == 1610612745
        assert endpoint.game_ids == "0022500617,0022500618"

    def test_init_with_single_game(self):
        """CumeStatsTeam works with a single game ID."""
        endpoint = CumeStatsTeam(
            team_id=1610612745,
            game_ids="0022500617",
        )

        assert endpoint.team_id == 1610612745
        assert endpoint.game_ids == "0022500617"

    def test_params_returns_all_parameters(self):
        """params() returns all parameters with correct API names."""
        endpoint = CumeStatsTeam(
            league_id="00",
            season="2026",
            season_type="Regular Season",
            team_id=1610612745,
            game_ids="0022500617",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2026",
            "SeasonType": "Regular Season",
            "TeamID": "1610612745",
            "GameIDs": "0022500617",
        }

    def test_params_converts_team_id_to_string(self):
        """params() converts team_id integer to string."""
        endpoint = CumeStatsTeam(team_id=1610612745)

        params = endpoint.params()

        assert params["TeamID"] == "1610612745"
        assert isinstance(params["TeamID"], str)

    def test_path_is_correct(self):
        """CumeStatsTeam has correct API path."""
        endpoint = CumeStatsTeam(team_id=1610612747)

        assert endpoint.path == "cumestatsteam"

    def test_response_model_is_correct(self):
        """CumeStatsTeam uses CumeStatsTeamResponse model."""
        endpoint = CumeStatsTeam(team_id=1610612747)

        assert endpoint.response_model is CumeStatsTeamResponse

    def test_endpoint_is_frozen(self):
        """CumeStatsTeam is immutable (frozen dataclass)."""
        endpoint = CumeStatsTeam(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023"  # type: ignore[misc]

    def test_params_with_multiple_game_ids(self):
        """params() handles multiple comma-separated game IDs."""
        endpoint = CumeStatsTeam(
            team_id=1610612745,
            game_ids="0022500617,0022500618,0022500619",
        )

        params = endpoint.params()

        assert params["GameIDs"] == "0022500617,0022500618,0022500619"
