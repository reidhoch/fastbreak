"""Tests for HustleStatsBoxscore endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import HustleStatsBoxscore
from fastbreak.models import HustleStatsBoxscoreResponse


class TestHustleStatsBoxscore:
    """Tests for HustleStatsBoxscore endpoint."""

    def test_init_with_game_id(self):
        """HustleStatsBoxscore requires game_id."""
        endpoint = HustleStatsBoxscore(game_id="0022500571")

        assert endpoint.game_id == "0022500571"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = HustleStatsBoxscore(game_id="0022500571")

        params = endpoint.params()

        assert params == {"GameID": "0022500571"}

    def test_path_is_correct(self):
        """HustleStatsBoxscore has correct API path."""
        endpoint = HustleStatsBoxscore(game_id="0022500571")

        assert endpoint.path == "hustlestatsboxscore"

    def test_response_model_is_correct(self):
        """HustleStatsBoxscore uses HustleStatsBoxscoreResponse model."""
        endpoint = HustleStatsBoxscore(game_id="0022500571")

        assert endpoint.response_model is HustleStatsBoxscoreResponse

    def test_endpoint_is_frozen(self):
        """HustleStatsBoxscore is immutable (frozen dataclass)."""
        endpoint = HustleStatsBoxscore(game_id="0022500571")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_id = "0022500000"  # type: ignore[misc]


class TestHustleStatsBoxscoreResponse:
    """Tests for HustleStatsBoxscoreResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HustleStatsAvailable",
                    "headers": ["GAME_ID", "HUSTLE_STATUS"],
                    "rowSet": [["0022500571", 1]],
                },
                {
                    "name": "PlayerStats",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_CITY",
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "START_POSITION",
                        "COMMENT",
                        "MINUTES",
                        "PTS",
                        "CONTESTED_SHOTS",
                        "CONTESTED_SHOTS_2PT",
                        "CONTESTED_SHOTS_3PT",
                        "DEFLECTIONS",
                        "CHARGES_DRAWN",
                        "SCREEN_ASSISTS",
                        "SCREEN_AST_PTS",
                        "OFF_LOOSE_BALLS_RECOVERED",
                        "DEF_LOOSE_BALLS_RECOVERED",
                        "LOOSE_BALLS_RECOVERED",
                        "OFF_BOXOUTS",
                        "DEF_BOXOUTS",
                        "BOX_OUT_PLAYER_TEAM_REBS",
                        "BOX_OUT_PLAYER_REBS",
                        "BOX_OUTS",
                    ],
                    "rowSet": [
                        [
                            "0022500571",
                            1610612761,
                            "TOR",
                            "Toronto",
                            1630567,
                            "Scottie Barnes",
                            "F",
                            "",
                            "38:23",
                            26,
                            6.0,
                            3.0,
                            3.0,
                            3.0,
                            0.0,
                            0.0,
                            0.0,
                            1.0,
                            0.0,
                            1.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ]
                    ],
                },
                {
                    "name": "TeamStats",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_CITY",
                        "MINUTES",
                        "PTS",
                        "CONTESTED_SHOTS",
                        "CONTESTED_SHOTS_2PT",
                        "CONTESTED_SHOTS_3PT",
                        "DEFLECTIONS",
                        "CHARGES_DRAWN",
                        "SCREEN_ASSISTS",
                        "SCREEN_AST_PTS",
                        "OFF_LOOSE_BALLS_RECOVERED",
                        "DEF_LOOSE_BALLS_RECOVERED",
                        "LOOSE_BALLS_RECOVERED",
                        "OFF_BOXOUTS",
                        "DEF_BOXOUTS",
                        "BOX_OUT_PLAYER_TEAM_REBS",
                        "BOX_OUT_PLAYER_REBS",
                        "BOX_OUTS",
                    ],
                    "rowSet": [
                        [
                            "0022500571",
                            1610612761,
                            "Raptors",
                            "TOR",
                            "Toronto",
                            "239:00",
                            115,
                            34.0,
                            18.0,
                            16.0,
                            15.0,
                            1.0,
                            5.0,
                            10.0,
                            1.0,
                            0.0,
                            1.0,
                            1.0,
                            5.0,
                            6.0,
                            4.0,
                            6.0,
                        ]
                    ],
                },
            ]
        }

        response = HustleStatsBoxscoreResponse.model_validate(raw_response)

        assert len(response.hustle_stats_available) == 1
        assert response.hustle_stats_available[0].game_id == "0022500571"
        assert response.hustle_stats_available[0].hustle_status == 1

        assert len(response.player_stats) == 1
        player = response.player_stats[0]
        assert player.player_name == "Scottie Barnes"
        assert player.team_abbreviation == "TOR"
        assert player.contested_shots == 6.0
        assert player.deflections == 3.0

        assert len(response.team_stats) == 1
        team = response.team_stats[0]
        assert team.team_name == "Raptors"
        assert team.contested_shots == 34.0
        assert team.deflections == 15.0

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HustleStatsAvailable",
                    "headers": ["GAME_ID", "HUSTLE_STATUS"],
                    "rowSet": [],
                },
                {
                    "name": "PlayerStats",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
                {
                    "name": "TeamStats",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = HustleStatsBoxscoreResponse.model_validate(raw_response)

        assert response.hustle_stats_available == []
        assert response.player_stats == []
        assert response.team_stats == []
