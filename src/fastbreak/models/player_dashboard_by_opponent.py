"""Models for the Player Dashboard by Opponent endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.player_dashboard_by_game_splits import GameSplitStats


class PlayerDashboardByOpponentResponse(FrozenResponse):
    """Response from the player dashboard by opponent endpoint.

    Contains stats split by opponent:
    - overall: Overall player stats
    - by_conference: Stats vs each conference (East, West)
    - by_division: Stats vs each division (Atlantic, Central, etc.)
    - by_opponent: Stats vs each individual team
    """

    overall: GameSplitStats | None = None
    by_conference: list[GameSplitStats] = Field(default_factory=list[GameSplitStats])
    by_division: list[GameSplitStats] = Field(default_factory=list[GameSplitStats])
    by_opponent: list[GameSplitStats] = Field(default_factory=list[GameSplitStats])

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallPlayerDashboard", True),
                "by_conference": "ConferencePlayerDashboard",
                "by_division": "DivisionPlayerDashboard",
                "by_opponent": "OpponentPlayerDashboard",
            }
        )
    )
