"""Tests for draft combine drill results models."""

from fastbreak.models.draft_combine_drill_results import (
    DraftCombineDrillResultsResponse,
    DrillResultsPlayer,
)


class TestDrillResultsPlayer:
    """Tests for DrillResultsPlayer model."""

    def test_parse_player_data(self):
        """DrillResultsPlayer parses API data correctly."""
        data = {
            "TEMP_PLAYER_ID": 1001,
            "PLAYER_ID": 203999,
            "FIRST_NAME": "Zion",
            "LAST_NAME": "Williamson",
            "PLAYER_NAME": "Zion Williamson",
            "POSITION": "PF",
            "STANDING_VERTICAL_LEAP": 36.5,
            "MAX_VERTICAL_LEAP": 45.0,
            "LANE_AGILITY_TIME": 11.15,
            "MODIFIED_LANE_AGILITY_TIME": 3.05,
            "THREE_QUARTER_SPRINT": 3.28,
            "BENCH_PRESS": 12,
        }

        player = DrillResultsPlayer.model_validate(data)

        assert player.player_id == 203999
        assert player.player_name == "Zion Williamson"
        assert player.position == "PF"
        assert player.standing_vertical_leap == 36.5
        assert player.max_vertical_leap == 45.0
        assert player.lane_agility_time == 11.15
        assert player.bench_press == 12

    def test_parse_player_with_null_fields(self):
        """DrillResultsPlayer handles null values for optional fields."""
        data = {
            "TEMP_PLAYER_ID": 1002,
            "PLAYER_ID": 204000,
            "FIRST_NAME": "Test",
            "LAST_NAME": "Player",
            "PLAYER_NAME": "Test Player",
            "POSITION": "G",
            "STANDING_VERTICAL_LEAP": None,
            "MAX_VERTICAL_LEAP": None,
            "LANE_AGILITY_TIME": None,
            "MODIFIED_LANE_AGILITY_TIME": None,
            "THREE_QUARTER_SPRINT": None,
            "BENCH_PRESS": None,
        }

        player = DrillResultsPlayer.model_validate(data)

        assert player.standing_vertical_leap is None
        assert player.max_vertical_leap is None
        assert player.lane_agility_time is None
        assert player.bench_press is None


class TestDraftCombineDrillResultsResponse:
    """Tests for DraftCombineDrillResultsResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "Results",
                    "headers": [
                        "TEMP_PLAYER_ID",
                        "PLAYER_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "PLAYER_NAME",
                        "POSITION",
                        "STANDING_VERTICAL_LEAP",
                        "MAX_VERTICAL_LEAP",
                        "LANE_AGILITY_TIME",
                        "MODIFIED_LANE_AGILITY_TIME",
                        "THREE_QUARTER_SPRINT",
                        "BENCH_PRESS",
                    ],
                    "rowSet": [
                        [
                            1001,
                            203999,
                            "Zion",
                            "Williamson",
                            "Zion Williamson",
                            "PF",
                            36.5,
                            45.0,
                            11.15,
                            3.05,
                            3.28,
                            12,
                        ],
                        [
                            1002,
                            204000,
                            "Ja",
                            "Morant",
                            "Ja Morant",
                            "G",
                            40.5,
                            44.0,
                            10.80,
                            2.90,
                            3.15,
                            8,
                        ],
                    ],
                }
            ]
        }

        response = DraftCombineDrillResultsResponse.model_validate(data)

        assert len(response.players) == 2
        assert response.players[0].player_name == "Zion Williamson"
        assert response.players[1].player_name == "Ja Morant"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "Results",
                    "headers": [
                        "TEMP_PLAYER_ID",
                        "PLAYER_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "PLAYER_NAME",
                        "POSITION",
                    ],
                    "rowSet": [],
                }
            ]
        }

        response = DraftCombineDrillResultsResponse.model_validate(data)

        assert response.players == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}

        response = DraftCombineDrillResultsResponse.model_validate(data)

        assert response.players == []
