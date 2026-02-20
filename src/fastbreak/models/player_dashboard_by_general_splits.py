"""Models for the Player Dashboard by General Splits endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.player_dashboard_by_game_splits import GameSplitStats


class PlayerDashboardByGeneralSplitsResponse(FrozenResponse):
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

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallPlayerDashboard", True),
                "by_location": "LocationPlayerDashboard",
                "by_wins_losses": "WinsLossesPlayerDashboard",
                "by_month": "MonthPlayerDashboard",
                "by_pre_post_all_star": "PrePostAllStarPlayerDashboard",
                "by_starting_position": "StartingPosition",
                "by_days_rest": "DaysRestPlayerDashboard",
            }
        )
    )
