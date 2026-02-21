"""Tests for GravityLeaders endpoint."""

import pytest

from fastbreak.endpoints import GravityLeaders
from fastbreak.utils import get_season_from_date


class TestGravityLeaders:
    """Tests for GravityLeaders endpoint."""

    def test_init_with_defaults(self):
        """Endpoint initializes with default values."""
        endpoint = GravityLeaders()
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.league_id == "00"

    def test_init_with_custom_season(self):
        """Endpoint accepts custom season."""
        endpoint = GravityLeaders(season="2023-24")
        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """Endpoint accepts custom season type."""
        endpoint = GravityLeaders(season_type="Playoffs")
        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_league_id(self):
        """Endpoint accepts custom league ID."""
        endpoint = GravityLeaders(league_id="10")
        assert endpoint.league_id == "10"

    def test_init_with_all_custom_params(self):
        """Endpoint accepts all custom parameters."""
        endpoint = GravityLeaders(
            season="2022-23",
            season_type="Playoffs",
            league_id="10",
        )
        assert endpoint.season == "2022-23"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns dictionary with all parameters."""
        endpoint = GravityLeaders(
            season="2023-24",
            season_type="Playoffs",
            league_id="00",
        )
        params = endpoint.params()
        assert params == {
            "LeagueID": "00",
            "Season": "2023-24",
            "SeasonType": "Playoffs",
        }

    def test_params_with_defaults(self):
        """params() returns correct defaults."""
        endpoint = GravityLeaders()
        params = endpoint.params()
        assert params == {
            "LeagueID": "00",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
        }

    def test_path_is_correct(self):
        """Endpoint has correct path."""
        endpoint = GravityLeaders()
        assert endpoint.path == "gravityleaders"
