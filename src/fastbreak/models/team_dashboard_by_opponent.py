"""Models for the Team Dashboard by Opponent endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats


class TeamDashboardByOpponentResponse(FrozenResponse):
    """Response from the team dashboard by opponent endpoint.

    Contains stats split by opponent:
    - overall: Overall team stats
    - by_conference: Stats vs each conference (East, West)
    - by_division: Stats vs each division (Atlantic, Central, etc.)
    - by_opponent: Stats vs each individual team
    """

    overall: TeamSplitStats | None = None
    by_conference: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])
    by_division: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])
    by_opponent: list[TeamSplitStats] = Field(default_factory=list[TeamSplitStats])

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "by_conference": "ConferenceTeamDashboard",
                "by_division": "DivisionTeamDashboard",
                "by_opponent": "OpponentTeamDashboard",
            }
        )
    )
