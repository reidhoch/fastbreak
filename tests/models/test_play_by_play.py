import pytest
from pydantic import ValidationError

from fastbreak.models import PlayByPlayAction, PlayByPlayGame, PlayByPlayResponse


class TestPlayByPlayAction:
    """Tests for PlayByPlayAction model."""

    def test_parse_valid_action(self, sample_action_data: dict) -> None:
        """Action model parses valid data."""
        action = PlayByPlayAction(**sample_action_data)

        assert action.actionNumber == 1
        assert action.clock == "PT12M00.00S"
        assert action.period == 1
        assert action.teamTricode == "IND"
        assert action.playerName == "Huff"
        assert action.actionType == "Jump Ball"

    def test_missing_required_field_raises(self, sample_action_data: dict) -> None:
        """Missing required field raises ValidationError."""
        del sample_action_data["actionNumber"]

        with pytest.raises(ValidationError):
            PlayByPlayAction(**sample_action_data)

    def test_action_with_shot_data(self, sample_shot_action_data: dict) -> None:
        """Action with shot attempt data parses correctly."""
        action = PlayByPlayAction(**sample_shot_action_data)

        assert action.shotResult == "Made"
        assert action.isFieldGoal == 1
        assert action.shotDistance == 8
        assert action.xLegacy == 15
        assert action.yLegacy == 80


class TestPlayByPlayGame:
    """Tests for PlayByPlayGame model."""

    def test_parse_game_with_actions(self, sample_game_data: dict) -> None:
        """Game model parses with actions list."""
        game = PlayByPlayGame(**sample_game_data)

        assert game.gameId == "0022500571"
        assert game.videoAvailable == 1
        assert len(game.actions) == 2
        assert game.actions[0].playerName == "Huff"

    def test_parse_game_with_empty_actions(self) -> None:
        """Game model accepts empty actions list."""
        game_data = {
            "gameId": "0022500571",
            "videoAvailable": 1,
            "actions": [],
        }
        game = PlayByPlayGame(**game_data)

        assert game.actions == []


class TestPlayByPlayResponse:
    """Tests for PlayByPlayResponse model."""

    def test_parse_full_response(self, sample_response_data: dict) -> None:
        """Response model parses complete data."""
        response = PlayByPlayResponse(**sample_response_data)

        assert response.meta.version == 1
        assert response.game.gameId == "0022500571"
        assert len(response.game.actions) == 2

    def test_response_meta_fields(self, sample_response_data: dict) -> None:
        """Response meta contains expected fields."""
        response = PlayByPlayResponse(**sample_response_data)

        assert response.meta.version == 1
        assert "playbyplay" in response.meta.request
        assert response.meta.time == "2026-01-15T12:10:24.1024Z"

    def test_response_accesses_nested_actions(self, sample_response_data: dict) -> None:
        """Response provides access to nested action data."""
        response = PlayByPlayResponse(**sample_response_data)

        first_action = response.game.actions[0]
        assert first_action.actionType == "Jump Ball"

        second_action = response.game.actions[1]
        assert second_action.actionType == "2pt"
        assert second_action.shotResult == "Made"
