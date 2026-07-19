"""Models for the Team Dashboard by Year Over Year endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats


class TeamDashboardByYearOverYearResponse(FrozenResponse):
    """Response from the team dashboard by year-over-year endpoint.

    Team-level counterpart to ``PlayerDashboardByYearOverYear``: overall stats
    plus one row per season the franchise has played (season-over-season).
    """

    overall: TeamSplitStats | None = None
    by_year: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "by_year": "ByYearTeamDashboard",
            }
        )
    )
