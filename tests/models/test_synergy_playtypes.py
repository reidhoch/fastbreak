"""Tests for synergy playtypes models."""

from fastbreak.models.synergy_playtypes import (
    PlayerSynergyPlaytype,
    SynergyPlaytypesResponse,
    TeamSynergyPlaytype,
)


class TestPlayerSynergyPlaytype:
    """Tests for PlayerSynergyPlaytype model."""

    def test_parse_player_data(self):
        """PlayerSynergyPlaytype parses API data correctly."""
        data = {
            "SEASON_ID": "22024",
            "PLAYER_ID": 2544,
            "PLAYER_NAME": "LeBron James",
            "TEAM_ID": 1610612747,
            "TEAM_ABBREVIATION": "LAL",
            "TEAM_NAME": "Los Angeles Lakers",
            "PLAY_TYPE": "Isolation",
            "TYPE_GROUPING": "Offensive",
            "PERCENTILE": 0.85,
            "GP": 50,
            "POSS_PCT": 0.12,
            "PPP": 1.05,
            "FG_PCT": 0.48,
            "FT_POSS_PCT": 0.08,
            "TOV_POSS_PCT": 0.10,
            "SF_POSS_PCT": 0.05,
            "PLUSONE_POSS_PCT": 0.02,
            "SCORE_POSS_PCT": 0.45,
            "EFG_PCT": 0.52,
            "POSS": 150.5,
            "PTS": 158.0,
            "FGM": 72.0,
            "FGA": 150.0,
            "FGMX": 78.0,
        }

        playtype = PlayerSynergyPlaytype.model_validate(data)

        assert playtype.player_name == "LeBron James"
        assert playtype.play_type == "Isolation"
        assert playtype.ppp == 1.05


class TestTeamSynergyPlaytype:
    """Tests for TeamSynergyPlaytype model."""

    def test_parse_team_data(self):
        """TeamSynergyPlaytype parses API data correctly."""
        data = {
            "SEASON_ID": "22024",
            "TEAM_ID": 1610612747,
            "TEAM_ABBREVIATION": "LAL",
            "TEAM_NAME": "Los Angeles Lakers",
            "PLAY_TYPE": "Transition",
            "TYPE_GROUPING": "Offensive",
            "PERCENTILE": 0.75,
            "GP": 60,
            "POSS_PCT": 0.18,
            "PPP": 1.15,
            "FG_PCT": 0.55,
            "FT_POSS_PCT": 0.06,
            "TOV_POSS_PCT": 0.12,
            "SF_POSS_PCT": 0.04,
            "PLUSONE_POSS_PCT": 0.03,
            "SCORE_POSS_PCT": 0.50,
            "EFG_PCT": 0.58,
            "POSS": 800.0,
            "PTS": 920.0,
            "FGM": 440.0,
            "FGA": 800.0,
            "FGMX": 360.0,
        }

        playtype = TeamSynergyPlaytype.model_validate(data)

        assert playtype.team_name == "Los Angeles Lakers"
        assert playtype.play_type == "Transition"


class TestSynergyPlaytypesResponse:
    """Tests for SynergyPlaytypesResponse model."""

    def test_parse_player_tabular_response(self):
        """Response parses player tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "SynergyPlayType",
                    "headers": [
                        "SEASON_ID",
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "PLAY_TYPE",
                        "TYPE_GROUPING",
                        "PERCENTILE",
                        "GP",
                        "POSS_PCT",
                        "PPP",
                        "FG_PCT",
                        "FT_POSS_PCT",
                        "TOV_POSS_PCT",
                        "SF_POSS_PCT",
                        "PLUSONE_POSS_PCT",
                        "SCORE_POSS_PCT",
                        "EFG_PCT",
                        "POSS",
                        "PTS",
                        "FGM",
                        "FGA",
                        "FGMX",
                    ],
                    "rowSet": [
                        [
                            "22024",
                            2544,
                            "LeBron James",
                            1610612747,
                            "LAL",
                            "Lakers",
                            "Isolation",
                            "Offensive",
                            0.85,
                            50,
                            0.12,
                            1.05,
                            0.48,
                            0.08,
                            0.10,
                            0.05,
                            0.02,
                            0.45,
                            0.52,
                            150.5,
                            158.0,
                            72.0,
                            150.0,
                            78.0,
                        ],
                    ],
                }
            ]
        }

        response = SynergyPlaytypesResponse.model_validate(data)

        assert len(response.player_stats) == 1
        assert response.player_stats[0].player_name == "LeBron James"
        assert response.team_stats == []

    def test_parse_team_tabular_response(self):
        """Response parses team tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "SynergyPlayType",
                    "headers": [
                        "SEASON_ID",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "PLAY_TYPE",
                        "TYPE_GROUPING",
                        "PERCENTILE",
                        "GP",
                        "POSS_PCT",
                        "PPP",
                        "FG_PCT",
                        "FT_POSS_PCT",
                        "TOV_POSS_PCT",
                        "SF_POSS_PCT",
                        "PLUSONE_POSS_PCT",
                        "SCORE_POSS_PCT",
                        "EFG_PCT",
                        "POSS",
                        "PTS",
                        "FGM",
                        "FGA",
                        "FGMX",
                    ],
                    "rowSet": [
                        [
                            "22024",
                            1610612747,
                            "LAL",
                            "Lakers",
                            "Transition",
                            "Offensive",
                            0.75,
                            60,
                            0.18,
                            1.15,
                            0.55,
                            0.06,
                            0.12,
                            0.04,
                            0.03,
                            0.50,
                            0.58,
                            800.0,
                            920.0,
                            440.0,
                            800.0,
                            360.0,
                        ],
                    ],
                }
            ]
        }

        response = SynergyPlaytypesResponse.model_validate(data)

        assert len(response.team_stats) == 1
        assert response.team_stats[0].team_name == "Lakers"
        assert response.player_stats == []

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "SynergyPlayType",
                    "headers": ["SEASON_ID"],
                    "rowSet": [],
                }
            ]
        }

        response = SynergyPlaytypesResponse.model_validate(data)

        assert response.player_stats == []
        assert response.team_stats == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"player_stats": [], "team_stats": []}

        response = SynergyPlaytypesResponse.model_validate(data)

        assert response.player_stats == []
        assert response.team_stats == []
