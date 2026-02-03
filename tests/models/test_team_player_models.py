"""Tests for team player models - non-tabular data paths."""

from fastbreak.models.team_player_dashboard import TeamPlayerDashboardResponse
from fastbreak.models.team_player_on_off_details import TeamPlayerOnOffDetailsResponse
from fastbreak.models.team_player_on_off_summary import TeamPlayerOnOffSummaryResponse
from fastbreak.models.team_vs_player import TeamVsPlayerResponse


class TestTeamPlayerDashboardResponse:
    """Tests for TeamPlayerDashboardResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "team_overall": None,
            "players": [],
        }

        response = TeamPlayerDashboardResponse.model_validate(data)

        assert response.team_overall is None
        assert response.players == []


class TestTeamPlayerOnOffDetailsResponse:
    """Tests for TeamPlayerOnOffDetailsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "overall": None,
            "players_on_court": [],
            "players_off_court": [],
        }

        response = TeamPlayerOnOffDetailsResponse.model_validate(data)

        assert response.overall is None
        assert response.players_on_court == []
        assert response.players_off_court == []


class TestTeamPlayerOnOffSummaryResponse:
    """Tests for TeamPlayerOnOffSummaryResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "overall": None,
            "players_on_court": [],
            "players_off_court": [],
        }

        response = TeamPlayerOnOffSummaryResponse.model_validate(data)

        assert response.overall is None
        assert response.players_on_court == []
        assert response.players_off_court == []


class TestTeamVsPlayerResponse:
    """Tests for TeamVsPlayerResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "overall": [],
            "vs_player_overall": None,
            "on_off_court": [],
            "shot_distance_overall": [],
            "shot_area_overall": [],
        }

        response = TeamVsPlayerResponse.model_validate(data)

        assert response.overall == []
        assert response.vs_player_overall is None
