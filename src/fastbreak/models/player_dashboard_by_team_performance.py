"""Models for the Player Dashboard by Team Performance endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.player_dashboard_by_game_splits import GameSplitStats


class TeamPerformanceStats(GameSplitStats):
    """Player stats for a team performance split.

    Extends GameSplitStats with additional grouping columns for win/loss
    and score range breakdowns.
    """

    group_value_order: int | None = Field(alias="GROUP_VALUE_ORDER")
    group_value_2: str = Field(alias="GROUP_VALUE_2")


class PlayerDashboardByTeamPerformanceResponse(FrozenResponse):
    """Response from the player dashboard by team performance endpoint.

    Contains player stats split by:
    - overall: Overall stats for the player
    - by_score_differential: Stats by win/loss and score margin
    - by_points_scored: Stats by team points scored ranges
    - by_points_against: Stats by opponent points scored ranges
    """

    overall: GameSplitStats | None = None
    by_score_differential: list[TeamPerformanceStats] = Field(default_factory=list)
    by_points_scored: list[TeamPerformanceStats] = Field(default_factory=list)
    by_points_against: list[TeamPerformanceStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallPlayerDashboard", True),
                "by_score_differential": "ScoreDifferentialPlayerDashboard",
                "by_points_scored": "PointsScoredPlayerDashboard",
                "by_points_against": "PontsAgainstPlayerDashboard",  # Note: NBA API typo
            }
        )
    )
