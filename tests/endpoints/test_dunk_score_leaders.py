"""Tests for DunkScoreLeaders endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import DunkScoreLeaders


class TestDunkScoreLeaders:
    """Tests for DunkScoreLeaders endpoint."""

    def test_init_with_defaults(self):
        """Endpoint initializes with default values."""
        endpoint = DunkScoreLeaders()
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.league_id == "00"
        assert endpoint.player_id is None
        assert endpoint.team_id is None
        assert endpoint.game_id is None

    def test_init_with_custom_season(self):
        """Endpoint accepts custom season."""
        endpoint = DunkScoreLeaders(season="2023-24")
        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """Endpoint accepts custom season type."""
        endpoint = DunkScoreLeaders(season_type="Playoffs")
        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_league_id(self):
        """Endpoint accepts custom league ID."""
        endpoint = DunkScoreLeaders(league_id="10")
        assert endpoint.league_id == "10"

    def test_init_with_player_id(self):
        """Endpoint accepts player ID filter."""
        endpoint = DunkScoreLeaders(player_id=2544)
        assert endpoint.player_id == 2544

    def test_init_with_team_id(self):
        """Endpoint accepts team ID filter."""
        endpoint = DunkScoreLeaders(team_id=1610612747)
        assert endpoint.team_id == 1610612747

    def test_init_with_game_id(self):
        """Endpoint accepts game ID filter."""
        endpoint = DunkScoreLeaders(game_id="0022400731")
        assert endpoint.game_id == "0022400731"

    def test_init_with_all_filters(self):
        """Endpoint accepts all filter parameters."""
        endpoint = DunkScoreLeaders(
            season="2023-24",
            season_type="Playoffs",
            league_id="00",
            player_id=2544,
            team_id=1610612747,
            game_id="0022400731",
        )
        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.league_id == "00"
        assert endpoint.player_id == 2544
        assert endpoint.team_id == 1610612747
        assert endpoint.game_id == "0022400731"

    def test_params_with_defaults(self):
        """params() returns correct defaults without optional filters."""
        endpoint = DunkScoreLeaders()
        params = endpoint.params()
        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
        }

    def test_params_excludes_none_values(self):
        """params() excludes None filter values."""
        endpoint = DunkScoreLeaders(player_id=None, team_id=None, game_id=None)
        params = endpoint.params()
        assert "PlayerId" not in params
        assert "TeamId" not in params
        assert "GameId" not in params

    def test_params_includes_player_id_when_set(self):
        """params() includes PlayerId when set."""
        endpoint = DunkScoreLeaders(player_id=2544)
        params = endpoint.params()
        assert params["PlayerId"] == "2544"

    def test_params_includes_team_id_when_set(self):
        """params() includes TeamId when set."""
        endpoint = DunkScoreLeaders(team_id=1610612747)
        params = endpoint.params()
        assert params["TeamId"] == "1610612747"

    def test_params_includes_game_id_when_set(self):
        """params() includes GameId when set."""
        endpoint = DunkScoreLeaders(game_id="0022400731")
        params = endpoint.params()
        assert params["GameId"] == "0022400731"

    def test_params_with_all_filters(self):
        """params() includes all filters when set."""
        endpoint = DunkScoreLeaders(
            season="2023-24",
            season_type="Playoffs",
            league_id="00",
            player_id=2544,
            team_id=1610612747,
            game_id="0022400731",
        )
        params = endpoint.params()
        assert params == {
            "LeagueID": "00",
            "Season": "2023-24",
            "SeasonType": "Playoffs",
            "PlayerId": "2544",
            "TeamId": "1610612747",
            "GameId": "0022400731",
        }

    def test_path_is_correct(self):
        """Endpoint has correct path."""
        endpoint = DunkScoreLeaders()
        assert endpoint.path == "dunkscoreleaders"

    def test_endpoint_is_frozen(self):
        """Endpoint is immutable (frozen Pydantic model)."""
        endpoint = DunkScoreLeaders()
        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"
