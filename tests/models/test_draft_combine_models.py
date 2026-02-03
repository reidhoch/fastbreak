"""Tests for draft combine models - non-tabular data paths.

These tests cover the model_validator branches for non-tabular (pre-parsed) data.
"""

from fastbreak.models.draft_combine_nonstationary_shooting import (
    DraftCombineNonstationaryShootingResponse,
)
from fastbreak.models.draft_combine_player_anthro import (
    DraftCombinePlayerAnthroResponse,
)
from fastbreak.models.draft_combine_spot_shooting import (
    DraftCombineSpotShootingResponse,
)
from fastbreak.models.draft_combine_stats import (
    DraftCombineStatsResponse,
)


class TestDraftCombinePlayerAnthroResponse:
    """Tests for DraftCombinePlayerAnthroResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}

        response = DraftCombinePlayerAnthroResponse.model_validate(data)

        assert response.players == []

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
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
                        "HEIGHT_WO_SHOES",
                        "HEIGHT_WO_SHOES_FT_IN",
                        "HEIGHT_W_SHOES",
                        "HEIGHT_W_SHOES_FT_IN",
                        "WEIGHT",
                        "WINGSPAN",
                        "WINGSPAN_FT_IN",
                        "STANDING_REACH",
                        "STANDING_REACH_FT_IN",
                        "BODY_FAT_PCT",
                        "HAND_LENGTH",
                        "HAND_WIDTH",
                    ],
                    "rowSet": [],
                }
            ]
        }

        response = DraftCombinePlayerAnthroResponse.model_validate(data)

        assert response.players == []


class TestDraftCombineNonstationaryShootingResponse:
    """Tests for DraftCombineNonstationaryShootingResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}

        response = DraftCombineNonstationaryShootingResponse.model_validate(data)

        assert response.players == []

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
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

        response = DraftCombineNonstationaryShootingResponse.model_validate(data)

        assert response.players == []


class TestDraftCombineSpotShootingResponse:
    """Tests for DraftCombineSpotShootingResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}

        response = DraftCombineSpotShootingResponse.model_validate(data)

        assert response.players == []

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
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

        response = DraftCombineSpotShootingResponse.model_validate(data)

        assert response.players == []


class TestDraftCombineStatsResponse:
    """Tests for DraftCombineStatsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}

        response = DraftCombineStatsResponse.model_validate(data)

        assert response.players == []

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
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

        response = DraftCombineStatsResponse.model_validate(data)

        assert response.players == []
