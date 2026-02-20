"""Models for the Player Dashboard by Last N Games endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.player_dashboard_by_game_splits import GameSplitStats


class PlayerDashboardByLastNGamesResponse(FrozenResponse):
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

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallPlayerDashboard", True),
                "last_5": ("Last5PlayerDashboard", True),
                "last_10": ("Last10PlayerDashboard", True),
                "last_15": ("Last15PlayerDashboard", True),
                "last_20": ("Last20PlayerDashboard", True),
                "by_game_number": "GameNumberPlayerDashboard",
            }
        )
    )
