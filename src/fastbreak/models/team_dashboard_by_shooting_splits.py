"""Models for the Team Dashboard by Shooting Splits endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
    parse_single_result_set,
)
from fastbreak.models.player_dashboard_by_shooting_splits import (
    AssistedByStats,
    ShootingSplitStatsWithRank,
)


class TeamDashboardByShootingSplitsResponse(BaseModel):
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

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "overall": parse_single_result_set(d, "OverallTeamDashboard"),
            "by_shot_distance_5ft": parse_result_set_by_name(d, "Shot5FTTeamDashboard"),
            "by_shot_distance_8ft": parse_result_set_by_name(d, "Shot8FTTeamDashboard"),
            "by_shot_area": parse_result_set_by_name(d, "ShotAreaTeamDashboard"),
            "by_assisted": parse_result_set_by_name(
                d,
                "AssitedShotTeamDashboard",  # Note: NBA API typo
            ),
            "by_shot_type": parse_result_set_by_name(d, "ShotTypeTeamDashboard"),
            "assisted_by": parse_result_set_by_name(d, "AssistedBy"),
        }
