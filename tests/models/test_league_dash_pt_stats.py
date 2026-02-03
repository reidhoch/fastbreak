"""Tests for league dash pt stats models."""

from fastbreak.models.league_dash_pt_stats import (
    LeagueDashPtStatsResponse,
    PlayerPtStats,
    TeamPtStats,
)


class TestTeamPtStats:
    """Tests for TeamPtStats model."""

    def test_parse_team_data(self):
        """TeamPtStats parses API data correctly."""
        data = {
            "TEAM_ID": 1610612747,
            "TEAM_NAME": "Los Angeles Lakers",
            "TEAM_ABBREVIATION": "LAL",
            "GP": 50,
            "W": 30,
            "L": 20,
            "MIN": 2400.0,
        }

        team = TeamPtStats.model_validate(data)

        assert team.team_name == "Los Angeles Lakers"
        assert team.gp == 50


class TestPlayerPtStats:
    """Tests for PlayerPtStats model."""

    def test_parse_player_data(self):
        """PlayerPtStats parses API data correctly."""
        data = {
            "PLAYER_ID": 2544,
            "PLAYER_NAME": "LeBron James",
            "TEAM_ID": 1610612747,
            "TEAM_ABBREVIATION": "LAL",
            "GP": 50,
            "W": 30,
            "L": 20,
            "MIN": 1800.0,
            "DIST_FEET": 10000.0,
            "DIST_MILES": 1.89,
            "DIST_MILES_OFF": 1.0,
            "DIST_MILES_DEF": 0.89,
            "AVG_SPEED": 4.3,
            "AVG_SPEED_OFF": 4.6,
            "AVG_SPEED_DEF": 4.0,
        }

        player = PlayerPtStats.model_validate(data)

        assert player.player_name == "LeBron James"
        assert player.gp == 50


class TestLeagueDashPtStatsResponse:
    """Tests for LeagueDashPtStatsResponse model."""

    def test_parse_team_tabular_response(self):
        """Response parses team tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPtStats",
                    "headers": [
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "GP",
                        "W",
                        "L",
                        "MIN",
                    ],
                    "rowSet": [
                        [1610612747, "Lakers", "LAL", 50, 30, 20, 2400.0],
                    ],
                }
            ]
        }

        response = LeagueDashPtStatsResponse.model_validate(data)

        assert len(response.teams) == 1
        assert response.teams[0].team_name == "Lakers"
        assert response.players == []

    def test_parse_player_tabular_response(self):
        """Response parses player tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPtStats",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "GP",
                        "W",
                        "L",
                        "MIN",
                        "DIST_FEET",
                        "DIST_MILES",
                        "DIST_MILES_OFF",
                        "DIST_MILES_DEF",
                        "AVG_SPEED",
                        "AVG_SPEED_OFF",
                        "AVG_SPEED_DEF",
                    ],
                    "rowSet": [
                        [
                            2544,
                            "LeBron James",
                            1610612747,
                            "LAL",
                            50,
                            30,
                            20,
                            1800.0,
                            10000.0,
                            1.89,
                            1.0,
                            0.89,
                            4.3,
                            4.6,
                            4.0,
                        ],
                    ],
                }
            ]
        }

        response = LeagueDashPtStatsResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].player_name == "LeBron James"
        assert response.teams == []

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPtStats",
                    "headers": ["TEAM_ID"],
                    "rowSet": [],
                }
            ]
        }

        response = LeagueDashPtStatsResponse.model_validate(data)

        # Empty response defaults to team stats
        assert response.teams == []
        assert response.players == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"teams": [], "players": []}

        response = LeagueDashPtStatsResponse.model_validate(data)

        assert response.teams == []
        assert response.players == []
