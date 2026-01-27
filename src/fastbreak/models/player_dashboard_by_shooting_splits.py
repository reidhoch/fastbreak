"""Models for the Player Dashboard by Shooting Splits endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
    parse_single_result_set,
)


class ShootingSplitStats(PandasMixin, PolarsMixin, BaseModel):
    """Shooting statistics for a shot category.

    Contains field goal attempts/makes by distance, area, or shot type.
    """

    group_set: str = Field(alias="GROUP_SET")
    group_value: str = Field(alias="GROUP_VALUE")

    # Shooting stats
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    efg_pct: float = Field(alias="EFG_PCT")
    blka: int = Field(alias="BLKA")

    # Assist percentages
    pct_ast_2pm: float = Field(alias="PCT_AST_2PM")
    pct_uast_2pm: float = Field(alias="PCT_UAST_2PM")
    pct_ast_3pm: float = Field(alias="PCT_AST_3PM")
    pct_uast_3pm: float = Field(alias="PCT_UAST_3PM")
    pct_ast_fgm: float = Field(alias="PCT_AST_FGM")
    pct_uast_fgm: float = Field(alias="PCT_UAST_FGM")


class ShootingSplitStatsWithRank(ShootingSplitStats):
    """Shooting statistics with league rank columns."""

    fgm_rank: int = Field(alias="FGM_RANK")
    fga_rank: int = Field(alias="FGA_RANK")
    fg_pct_rank: int = Field(alias="FG_PCT_RANK")
    fg3m_rank: int = Field(alias="FG3M_RANK")
    fg3a_rank: int = Field(alias="FG3A_RANK")
    fg3_pct_rank: int = Field(alias="FG3_PCT_RANK")
    efg_pct_rank: int = Field(alias="EFG_PCT_RANK")
    blka_rank: int = Field(alias="BLKA_RANK")
    pct_ast_2pm_rank: int = Field(alias="PCT_AST_2PM_RANK")
    pct_uast_2pm_rank: int = Field(alias="PCT_UAST_2PM_RANK")
    pct_ast_3pm_rank: int = Field(alias="PCT_AST_3PM_RANK")
    pct_uast_3pm_rank: int = Field(alias="PCT_UAST_3PM_RANK")
    pct_ast_fgm_rank: int = Field(alias="PCT_AST_FGM_RANK")
    pct_uast_fgm_rank: int = Field(alias="PCT_UAST_FGM_RANK")


class AssistedByStats(PandasMixin, PolarsMixin, BaseModel):
    """Stats for shots assisted by a specific player."""

    group_set: str = Field(alias="GROUP_SET")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")

    # Shooting stats
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    efg_pct: float = Field(alias="EFG_PCT")
    blka: int = Field(alias="BLKA")

    # Assist percentages
    pct_ast_2pm: float = Field(alias="PCT_AST_2PM")
    pct_uast_2pm: float = Field(alias="PCT_UAST_2PM")
    pct_ast_3pm: float = Field(alias="PCT_AST_3PM")
    pct_uast_3pm: float = Field(alias="PCT_UAST_3PM")
    pct_ast_fgm: float = Field(alias="PCT_AST_FGM")
    pct_uast_fgm: float = Field(alias="PCT_UAST_FGM")

    # Rank columns
    fgm_rank: int = Field(alias="FGM_RANK")
    fga_rank: int = Field(alias="FGA_RANK")
    fg_pct_rank: int = Field(alias="FG_PCT_RANK")
    fg3m_rank: int = Field(alias="FG3M_RANK")
    fg3a_rank: int = Field(alias="FG3A_RANK")
    fg3_pct_rank: int = Field(alias="FG3_PCT_RANK")
    efg_pct_rank: int = Field(alias="EFG_PCT_RANK")
    blka_rank: int = Field(alias="BLKA_RANK")
    pct_ast_2pm_rank: int = Field(alias="PCT_AST_2PM_RANK")
    pct_uast_2pm_rank: int = Field(alias="PCT_UAST_2PM_RANK")
    pct_ast_3pm_rank: int = Field(alias="PCT_AST_3PM_RANK")
    pct_uast_3pm_rank: int = Field(alias="PCT_UAST_3PM_RANK")
    pct_ast_fgm_rank: int = Field(alias="PCT_AST_FGM_RANK")
    pct_uast_fgm_rank: int = Field(alias="PCT_UAST_FGM_RANK")


class PlayerDashboardByShootingSplitsResponse(BaseModel):
    """Response from the player dashboard by shooting splits endpoint.

    Contains detailed shooting stats by:
    - overall: Overall shooting stats
    - by_shot_distance_5ft: Shot distance in 5ft increments
    - by_shot_distance_8ft: Shot distance in 8ft increments
    - by_shot_area: Court areas (Restricted Area, Paint, Mid-Range, etc.)
    - by_assisted: Assisted vs Unassisted shots
    - by_shot_type_summary: Shot type summary (no rank columns)
    - by_shot_type_detail: Detailed shot types (43+ types)
    - assisted_by: Stats by assisting player
    """

    overall: ShootingSplitStatsWithRank | None = None
    by_shot_distance_5ft: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_shot_distance_8ft: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_shot_area: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_assisted: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    by_shot_type_summary: list[ShootingSplitStats] = Field(default_factory=list)
    by_shot_type_detail: list[ShootingSplitStatsWithRank] = Field(default_factory=list)
    assisted_by: list[AssistedByStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "overall": parse_single_result_set(d, "OverallPlayerDashboard"),
            "by_shot_distance_5ft": parse_result_set_by_name(
                d, "Shot5FTPlayerDashboard"
            ),
            "by_shot_distance_8ft": parse_result_set_by_name(
                d, "Shot8FTPlayerDashboard"
            ),
            "by_shot_area": parse_result_set_by_name(d, "ShotAreaPlayerDashboard"),
            "by_assisted": parse_result_set_by_name(
                d,
                "AssitedShotPlayerDashboard",  # Note: NBA API typo
            ),
            "by_shot_type_summary": parse_result_set_by_name(
                d, "ShotTypeSummaryPlayerDashboard"
            ),
            "by_shot_type_detail": parse_result_set_by_name(
                d, "ShotTypePlayerDashboard"
            ),
            "assisted_by": parse_result_set_by_name(d, "AssistedBy"),
        }
