"""Tests for team game models - non-tabular data paths."""

from fastbreak.models.team_game_log import TeamGameLogResponse
from fastbreak.models.team_game_logs import TeamGameLogsResponse


class TestTeamGameLogResponse:
    """Tests for TeamGameLogResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"games": []}

        response = TeamGameLogResponse.model_validate(data)

        assert response.games == []


class TestTeamGameLogsResponse:
    """Tests for TeamGameLogsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"games": []}

        response = TeamGameLogsResponse.model_validate(data)

        assert response.games == []
