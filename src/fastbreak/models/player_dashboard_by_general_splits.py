"""Models for the Player Dashboard by General Splits endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)
from fastbreak.models.player_dashboard_by_game_splits import GameSplitStats


class PlayerDashboardByGeneralSplitsResponse(BaseModel):
    """Response from the player dashboard by general splits endpoint.

    Contains stats split by various general categories:
    - overall: Overall player stats
    - by_location: Stats by game location (Home, Road)
    - by_wins_losses: Stats by game outcome (Wins, Losses)
    - by_month: Stats by month (January, February, etc.)
    - by_pre_post_all_star: Stats by pre/post All-Star break
    - by_starting_position: Stats by starting position (Starters, Bench)
    - by_days_rest: Stats by days of rest (0, 1, 2, 3+ Days Rest)
    """

    overall: GameSplitStats | None = None
    by_location: list[GameSplitStats] = Field(default_factory=list)
    by_wins_losses: list[GameSplitStats] = Field(default_factory=list)
    by_month: list[GameSplitStats] = Field(default_factory=list)
    by_pre_post_all_star: list[GameSplitStats] = Field(default_factory=list)
    by_starting_position: list[GameSplitStats] = Field(default_factory=list)
    by_days_rest: list[GameSplitStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        overall_rows = parse_result_set_by_name(
            data,
            "OverallPlayerDashboard",
        )

        return {
            "overall": overall_rows[0] if overall_rows else None,
            "by_location": parse_result_set_by_name(
                data,
                "LocationPlayerDashboard",
            ),
            "by_wins_losses": parse_result_set_by_name(
                data,
                "WinsLossesPlayerDashboard",
            ),
            "by_month": parse_result_set_by_name(
                data,
                "MonthPlayerDashboard",
            ),
            "by_pre_post_all_star": parse_result_set_by_name(
                data,
                "PrePostAllStarPlayerDashboard",
            ),
            "by_starting_position": parse_result_set_by_name(
                data,
                "StartingPosition",
            ),
            "by_days_rest": parse_result_set_by_name(
                data,
                "DaysRestPlayerDashboard",
            ),
        }
