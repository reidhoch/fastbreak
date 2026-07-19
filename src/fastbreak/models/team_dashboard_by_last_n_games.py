"""Models for the Team Dashboard by Last N Games endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats


class TeamDashboardByLastNGamesResponse(FrozenResponse):
    """Response from the team dashboard by last-N-games endpoint.

    Team-level counterpart to ``PlayerDashboardByLastNGames``: overall plus the
    last 5/10/15/20 games, and a per-game-number breakdown.
    """

    overall: TeamSplitStats | None = None
    last_5: TeamSplitStats | None = None
    last_10: TeamSplitStats | None = None
    last_15: TeamSplitStats | None = None
    last_20: TeamSplitStats | None = None
    by_game_number: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "last_5": ("Last5TeamDashboard", True),
                "last_10": ("Last10TeamDashboard", True),
                "last_15": ("Last15TeamDashboard", True),
                "last_20": ("Last20TeamDashboard", True),
                "by_game_number": "GameNumberTeamDashboard",
            }
        )
    )
