"""Models for the Player Dashboard by Last N Games endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
    parse_single_result_set,
)
from fastbreak.models.player_dashboard_by_game_splits import GameSplitStats


class PlayerDashboardByLastNGamesResponse(BaseModel):
    """Response from the player dashboard by last N games endpoint.

    Contains rolling averages at different lookback windows:
    - overall: Overall season stats
    - last_5: Stats from last 5 games
    - last_10: Stats from last 10 games
    - last_15: Stats from last 15 games
    - last_20: Stats from last 20 games
    - by_game_number: Stats by game number ranges (Games 1-10, 11-20, etc.)
    """

    overall: GameSplitStats | None = None
    last_5: GameSplitStats | None = None
    last_10: GameSplitStats | None = None
    last_15: GameSplitStats | None = None
    last_20: GameSplitStats | None = None
    by_game_number: list[GameSplitStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "overall": parse_single_result_set(d, "OverallPlayerDashboard"),
            "last_5": parse_single_result_set(d, "Last5PlayerDashboard"),
            "last_10": parse_single_result_set(d, "Last10PlayerDashboard"),
            "last_15": parse_single_result_set(d, "Last15PlayerDashboard"),
            "last_20": parse_single_result_set(d, "Last20PlayerDashboard"),
            "by_game_number": parse_result_set_by_name(d, "GameNumberPlayerDashboard"),
        }
