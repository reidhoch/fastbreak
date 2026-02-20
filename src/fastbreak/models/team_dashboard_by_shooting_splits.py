"""Models for the Team Dashboard by Shooting Splits endpoint response."""

from pydantic import Field, model_validator

from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator
from fastbreak.models.player_dashboard_by_shooting_splits import (
    AssistedByStats,
    ShootingSplitStatsWithRank,
)


class TeamDashboardByShootingSplitsResponse(FrozenResponse):
    """Response from the team dashboard by shooting splits endpoint.

    Contains detailed shooting stats by:
    - overall: Overall shooting stats
    - by_shot_distance_5ft: Shot distance in 5ft increments
    - by_shot_distance_8ft: Shot distance in 8ft increments
    - by_shot_area: Court areas (Restricted Area, Paint, Mid-Range, etc.)
    - by_assisted: Assisted vs Unassisted shots
    - by_shot_type: Detailed shot types (46+ types)
    - assisted_by: Stats by assisting player
    """

    overall: ShootingSplitStatsWithRank | None = None
    by_shot_distance_5ft: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_shot_distance_8ft: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_shot_area: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_assisted: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_shot_type: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    assisted_by: list[AssistedByStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("OverallTeamDashboard", True),
                "by_shot_distance_5ft": "Shot5FTTeamDashboard",
                "by_shot_distance_8ft": "Shot8FTTeamDashboard",
                "by_shot_area": "ShotAreaTeamDashboard",
                "by_assisted": "AssitedShotTeamDashboard",  # Note: NBA API typo
                "by_shot_type": "ShotTypeTeamDashboard",
                "assisted_by": "AssistedBy",
            }
        )
    )
