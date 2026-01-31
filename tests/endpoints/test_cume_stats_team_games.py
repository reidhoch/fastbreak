"""Tests for CumeStatsTeamGames endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints.cume_stats_team_games import CumeStatsTeamGames
from fastbreak.models.cume_stats_team_games import CumeStatsTeamGamesResponse


class TestCumeStatsTeamGames:
    """Tests for CumeStatsTeamGames endpoint."""

    def test_init_with_defaults(self):
        """CumeStatsTeamGames uses sensible defaults."""
        endpoint = CumeStatsTeamGames(team_id=1610612747)

        assert endpoint.league_id == "00"
        assert endpoint.season == "2025"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.team_id == 1610612747

    def test_init_optional_params_default_to_none_or_zero(self):
        """CumeStatsTeamGames optional params default appropriately."""
        endpoint = CumeStatsTeamGames(team_id=1610612747)

        assert endpoint.location is None
        assert endpoint.outcome is None
        assert endpoint.vs_team_id == 0  # vs_team_id defaults to 0
        assert endpoint.vs_division is None
        assert endpoint.vs_conference is None

    def test_init_with_custom_required_params(self):
        """CumeStatsTeamGames accepts custom required parameters."""
        endpoint = CumeStatsTeamGames(
            league_id="10",
            season="2026",
            season_type="Playoffs",
            team_id=1610612745,
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2026"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.team_id == 1610612745

    def test_init_with_optional_filters(self):
        """CumeStatsTeamGames accepts optional filter parameters."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
            location="Home",
            outcome="W",
            vs_team_id=1610612744,
            vs_division="Pacific",
            vs_conference="West",
        )

        assert endpoint.location == "Home"
        assert endpoint.outcome == "W"
        assert endpoint.vs_team_id == 1610612744
        assert endpoint.vs_division == "Pacific"
        assert endpoint.vs_conference == "West"

    def test_params_returns_required_and_vs_team_id(self):
        """params() returns required params plus VsTeamID (always included)."""
        endpoint = CumeStatsTeamGames(team_id=1610612745)

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2025",
            "SeasonType": "Regular Season",
            "TeamID": "1610612745",
            "VsTeamID": "0",
        }
        assert "Location" not in params
        assert "Outcome" not in params

    def test_params_uses_season_not_season_id(self):
        """params() uses Season parameter (not SeasonID)."""
        endpoint = CumeStatsTeamGames(team_id=1610612747, season="2026")

        params = endpoint.params()

        assert "Season" in params
        assert "SeasonID" not in params
        assert params["Season"] == "2026"

    def test_params_includes_optional_when_set(self):
        """params() includes optional params when they are set."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
            location="Road",
            outcome="L",
        )

        params = endpoint.params()

        assert params["Location"] == "Road"
        assert params["Outcome"] == "L"

    def test_params_includes_all_optional_params_when_set(self):
        """params() includes all optional params when set."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
            location="Home",
            outcome="W",
            vs_team_id=1610612744,
            vs_division="Pacific",
            vs_conference="West",
        )

        params = endpoint.params()

        assert params["Location"] == "Home"
        assert params["Outcome"] == "W"
        assert params["VsTeamID"] == "1610612744"
        assert params["VsDivision"] == "Pacific"
        assert params["VsConference"] == "West"

    def test_params_converts_ids_to_strings(self):
        """params() converts integer IDs to strings."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
            vs_team_id=1610612744,
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612745"
        assert params["VsTeamID"] == "1610612744"
        assert isinstance(params["TeamID"], str)
        assert isinstance(params["VsTeamID"], str)

    def test_path_is_correct(self):
        """CumeStatsTeamGames has correct API path."""
        endpoint = CumeStatsTeamGames(team_id=1610612747)

        assert endpoint.path == "cumestatsteamgames"

    def test_response_model_is_correct(self):
        """CumeStatsTeamGames uses CumeStatsTeamGamesResponse model."""
        endpoint = CumeStatsTeamGames(team_id=1610612747)

        assert endpoint.response_model is CumeStatsTeamGamesResponse

    def test_endpoint_is_frozen(self):
        """CumeStatsTeamGames is immutable (frozen dataclass)."""
        endpoint = CumeStatsTeamGames(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023"  # type: ignore[misc]
