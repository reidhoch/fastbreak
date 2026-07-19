"""Models for the Team Dashboard by Clutch endpoint response."""

from pydantic import model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats


class TeamDashboardByClutchResponse(FrozenResponse):
    """Response from the team dashboard by clutch endpoint.

    Team-level counterpart to ``PlayerDashboardByClutch``: stats for the
    standard clutch definitions (last 5/3/1 min within 5 pts, last 30/10 sec
    within 3 pts, and the plus/minus variants).
    """

    overall: TeamSplitStats | None = None
    last_5_min_lte_5_pts: TeamSplitStats | None = None
    last_3_min_lte_5_pts: TeamSplitStats | None = None
    last_1_min_lte_5_pts: TeamSplitStats | None = None
    last_30_sec_lte_3_pts: TeamSplitStats | None = None
    last_10_sec_lte_3_pts: TeamSplitStats | None = None
    last_5_min_pm_5_pts: TeamSplitStats | None = None
    last_3_min_pm_5_pts: TeamSplitStats | None = None
    last_1_min_pm_5_pts: TeamSplitStats | None = None
    last_30_sec_pm_3_pts: TeamSplitStats | None = None
    last_10_sec_pm_3_pts: TeamSplitStats | None = None

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "last_5_min_lte_5_pts": ("Last5Min5PointTeamDashboard", True),
                "last_3_min_lte_5_pts": ("Last3Min5PointTeamDashboard", True),
                "last_1_min_lte_5_pts": ("Last1Min5PointTeamDashboard", True),
                "last_30_sec_lte_3_pts": ("Last30Sec3PointTeamDashboard", True),
                "last_10_sec_lte_3_pts": ("Last10Sec3PointTeamDashboard", True),
                "last_5_min_pm_5_pts": (
                    "Last5MinPlusMinus5PointTeamDashboard",
                    True,
                ),
                "last_3_min_pm_5_pts": (
                    "Last3MinPlusMinus5PointTeamDashboard",
                    True,
                ),
                "last_1_min_pm_5_pts": (
                    "Last1MinPlusMinus5PointTeamDashboard",
                    True,
                ),
                "last_30_sec_pm_3_pts": ("Last30Sec3Point2TeamDashboard", True),
                "last_10_sec_pm_3_pts": ("Last10Sec3Point2TeamDashboard", True),
            }
        )
    )
