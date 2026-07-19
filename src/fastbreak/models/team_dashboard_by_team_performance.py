"""Models for the Team Dashboard by Team Performance endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats


class TeamDashboardByTeamPerformanceResponse(FrozenResponse):
    """Response from the team dashboard by team performance endpoint.

    Team-level counterpart to ``PlayerDashboardByTeamPerformance``: stats split
    by score differential, points scored, and points allowed.
    """

    overall: TeamSplitStats | None = None
    by_score_differential: list[TeamSplitStats] = Field(
        default_factory=list[TeamSplitStats]
    )
    by_points_scored: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])
    by_points_against: list[TeamSplitStats] = Field(
        default_factory=list[TeamSplitStats]
    )

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "by_score_differential": "ScoreDifferentialTeamDashboard",
                "by_points_scored": "PointsScoredTeamDashboard",
                # NBA API typo preserved verbatim ("Ponts", not "Points").
                "by_points_against": "PontsAgainstTeamDashboard",
            }
        )
    )
