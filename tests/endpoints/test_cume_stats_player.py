"""Tests for CumeStatsPlayer endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints.cume_stats_player import CumeStatsPlayer
from fastbreak.models.cume_stats_player import CumeStatsPlayerResponse


class TestCumeStatsPlayer:
    """Tests for CumeStatsPlayer endpoint."""

    def test_init_with_defaults(self):
        """CumeStatsPlayer uses sensible defaults."""
        endpoint = CumeStatsPlayer(player_id=2544)

        assert endpoint.league_id == "00"
        assert endpoint.season == "2025"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.player_id == 2544
        assert endpoint.game_ids == ""

    def test_init_with_custom_params(self):
        """CumeStatsPlayer accepts custom parameters."""
        endpoint = CumeStatsPlayer(
            league_id="10",
            season="2026",
            season_type="Playoffs",
            player_id=2544,
            game_ids="0022500617,0022500618",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2026"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.player_id == 2544
        assert endpoint.game_ids == "0022500617,0022500618"

    def test_init_with_single_game(self):
        """CumeStatsPlayer works with a single game ID."""
        endpoint = CumeStatsPlayer(
            player_id=2544,
            game_ids="0022500617",
        )

        assert endpoint.player_id == 2544
        assert endpoint.game_ids == "0022500617"

    def test_params_returns_all_parameters(self):
        """params() returns all parameters with correct API names."""
        endpoint = CumeStatsPlayer(
            league_id="00",
            season="2026",
            season_type="Regular Season",
            player_id=2544,
            game_ids="0022500617",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2026",
            "SeasonType": "Regular Season",
            "PlayerID": "2544",
            "GameIDs": "0022500617",
        }

    def test_params_converts_player_id_to_string(self):
        """params() converts player_id integer to string."""
        endpoint = CumeStatsPlayer(player_id=2544)

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert isinstance(params["PlayerID"], str)

    def test_path_is_correct(self):
        """CumeStatsPlayer has correct API path."""
        endpoint = CumeStatsPlayer(player_id=2544)

        assert endpoint.path == "cumestatsplayer"

    def test_response_model_is_correct(self):
        """CumeStatsPlayer uses CumeStatsPlayerResponse model."""
        endpoint = CumeStatsPlayer(player_id=2544)

        assert endpoint.response_model is CumeStatsPlayerResponse

    def test_endpoint_is_frozen(self):
        """CumeStatsPlayer is immutable (frozen dataclass)."""
        endpoint = CumeStatsPlayer(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023"  # type: ignore[misc]

    def test_params_with_multiple_game_ids(self):
        """params() handles multiple comma-separated game IDs."""
        endpoint = CumeStatsPlayer(
            player_id=2544,
            game_ids="0022500617,0022500618,0022500619",
        )

        params = endpoint.params()

        assert params["GameIDs"] == "0022500617,0022500618,0022500619"
