"""Tests for team and players vs players models."""

from fastbreak.models.team_and_players_vs_players import (
    TeamAndPlayersVsPlayersResponse,
)


class TestTeamAndPlayersVsPlayersResponse:
    """Tests for TeamAndPlayersVsPlayersResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "players_vs_players": [],
            "team_players_vs_players_off": [],
            "team_players_vs_players_on": [],
            "team_vs_players": [],
            "team_vs_players_off": [],
        }

        response = TeamAndPlayersVsPlayersResponse.model_validate(data)

        assert response.players_vs_players == []
        assert response.team_vs_players == []
