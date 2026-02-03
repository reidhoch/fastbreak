"""Tests for game rotation models."""

from fastbreak.models.game_rotation import (
    GameRotationResponse,
    RotationEntry,
)


class TestRotationEntry:
    """Tests for RotationEntry model."""

    def test_parse_rotation_entry(self):
        """RotationEntry parses API data correctly."""
        data = {
            "GAME_ID": "0022400001",
            "TEAM_ID": 1610612747,
            "TEAM_CITY": "Los Angeles",
            "TEAM_NAME": "Lakers",
            "PERSON_ID": 2544,
            "PLAYER_FIRST": "LeBron",
            "PLAYER_LAST": "James",
            "IN_TIME_REAL": 0.0,
            "OUT_TIME_REAL": 720.0,
            "PLAYER_PTS": 12,
            "PT_DIFF": 5,
            "USG_PCT": 0.285,
        }

        entry = RotationEntry.model_validate(data)

        assert entry.game_id == "0022400001"
        assert entry.team_id == 1610612747
        assert entry.person_id == 2544
        assert entry.player_first == "LeBron"
        assert entry.player_last == "James"
        assert entry.player_pts == 12
        assert entry.pt_diff == 5


class TestGameRotationResponse:
    """Tests for GameRotationResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "AwayTeam",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "PERSON_ID",
                        "PLAYER_FIRST",
                        "PLAYER_LAST",
                        "IN_TIME_REAL",
                        "OUT_TIME_REAL",
                        "PLAYER_PTS",
                        "PT_DIFF",
                        "USG_PCT",
                    ],
                    "rowSet": [
                        [
                            "0022400001",
                            1610612750,
                            "Minnesota",
                            "Timberwolves",
                            201566,
                            "Anthony",
                            "Davis",
                            0.0,
                            600.0,
                            10,
                            3,
                            0.25,
                        ],
                    ],
                },
                {
                    "name": "HomeTeam",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "PERSON_ID",
                        "PLAYER_FIRST",
                        "PLAYER_LAST",
                        "IN_TIME_REAL",
                        "OUT_TIME_REAL",
                        "PLAYER_PTS",
                        "PT_DIFF",
                        "USG_PCT",
                    ],
                    "rowSet": [
                        [
                            "0022400001",
                            1610612747,
                            "Los Angeles",
                            "Lakers",
                            2544,
                            "LeBron",
                            "James",
                            0.0,
                            720.0,
                            12,
                            5,
                            0.285,
                        ],
                    ],
                },
            ]
        }

        response = GameRotationResponse.model_validate(data)

        assert len(response.away_team) == 1
        assert len(response.home_team) == 1
        assert response.away_team[0].team_name == "Timberwolves"
        assert response.home_team[0].player_first == "LeBron"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "AwayTeam",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
                {
                    "name": "HomeTeam",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = GameRotationResponse.model_validate(data)

        assert response.away_team == []
        assert response.home_team == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"away_team": [], "home_team": []}

        response = GameRotationResponse.model_validate(data)

        assert response.away_team == []
        assert response.home_team == []
