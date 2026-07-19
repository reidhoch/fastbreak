"""Models for the Team Dashboard by Game Splits endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats


class TeamDashboardByGameSplitsResponse(FrozenResponse):
    """Response from the team dashboard by game splits endpoint.

    Team-level counterpart to ``PlayerDashboardByGameSplits``: stats split by
    half, period, general score margin, and specific score-margin ranges.
    """

    overall: TeamSplitStats | None = None
    by_half: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])
    by_period: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])
    by_score_margin: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])
    by_actual_margin: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "by_half": "ByHalfTeamDashboard",
                "by_period": "ByPeriodTeamDashboard",
                "by_score_margin": "ByScoreMarginTeamDashboard",
                "by_actual_margin": "ByActualMarginTeamDashboard",
            }
        )
    )
