"""Models for the Team Dashboard by General Splits endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class TeamSplitStats(PandasMixin, PolarsMixin, BaseModel):
    """Team statistics for a general split segment.

    Contains aggregated stats and league ranks for a specific split
    (location, wins/losses, month, etc.).
    """

    # Identifiers
    group_set: str = Field(alias="GROUP_SET")
    group_value: str | int = Field(alias="GROUP_VALUE")

    # Basic stats
    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    w_pct: float = Field(alias="W_PCT")
    min: float = Field(alias="MIN")

    # Shooting stats
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")

    # Rebounds
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")

    # Other stats
    ast: float = Field(alias="AST")
    tov: float = Field(alias="TOV")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    blka: float = Field(alias="BLKA")
    pf: float = Field(alias="PF")
    pfd: float = Field(alias="PFD")
    pts: float = Field(alias="PTS")
    plus_minus: float = Field(alias="PLUS_MINUS")

    # Rank columns
    gp_rank: int = Field(alias="GP_RANK")
    w_rank: int = Field(alias="W_RANK")
    l_rank: int = Field(alias="L_RANK")
    w_pct_rank: int = Field(alias="W_PCT_RANK")
    min_rank: int = Field(alias="MIN_RANK")
    fgm_rank: int = Field(alias="FGM_RANK")
    fga_rank: int = Field(alias="FGA_RANK")
    fg_pct_rank: int = Field(alias="FG_PCT_RANK")
    fg3m_rank: int = Field(alias="FG3M_RANK")
    fg3a_rank: int = Field(alias="FG3A_RANK")
    fg3_pct_rank: int = Field(alias="FG3_PCT_RANK")
    ftm_rank: int = Field(alias="FTM_RANK")
    fta_rank: int = Field(alias="FTA_RANK")
    ft_pct_rank: int = Field(alias="FT_PCT_RANK")
    oreb_rank: int = Field(alias="OREB_RANK")
    dreb_rank: int = Field(alias="DREB_RANK")
    reb_rank: int = Field(alias="REB_RANK")
    ast_rank: int = Field(alias="AST_RANK")
    tov_rank: int = Field(alias="TOV_RANK")
    stl_rank: int = Field(alias="STL_RANK")
    blk_rank: int = Field(alias="BLK_RANK")
    blka_rank: int = Field(alias="BLKA_RANK")
    pf_rank: int = Field(alias="PF_RANK")
    pfd_rank: int = Field(alias="PFD_RANK")
    pts_rank: int = Field(alias="PTS_RANK")
    plus_minus_rank: int = Field(alias="PLUS_MINUS_RANK")


class TeamDashboardByGeneralSplitsResponse(BaseModel):
    """Response from the team dashboard by general splits endpoint.

    Contains stats split by various general categories:
    - overall: Overall team stats
    - by_location: Stats by game location (Home, Road)
    - by_wins_losses: Stats by game outcome (Wins, Losses)
    - by_month: Stats by month (January, February, etc.)
    - by_pre_post_all_star: Stats by pre/post All-Star break
    - by_days_rest: Stats by days of rest (0, 1, 2, 3+ Days Rest)
    """

    overall: TeamSplitStats | None = None
    by_location: list[TeamSplitStats] = Field(default_factory=list)
    by_wins_losses: list[TeamSplitStats] = Field(default_factory=list)
    by_month: list[TeamSplitStats] = Field(default_factory=list)
    by_pre_post_all_star: list[TeamSplitStats] = Field(default_factory=list)
    by_days_rest: list[TeamSplitStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        overall_rows = parse_result_set_by_name(
            data,
            "OverallTeamDashboard",
        )

        return {
            "overall": overall_rows[0] if overall_rows else None,
            "by_location": parse_result_set_by_name(
                data,
                "LocationTeamDashboard",
            ),
            "by_wins_losses": parse_result_set_by_name(
                data,
                "WinsLossesTeamDashboard",
            ),
            "by_month": parse_result_set_by_name(
                data,
                "MonthTeamDashboard",
            ),
            "by_pre_post_all_star": parse_result_set_by_name(
                data,
                "PrePostAllStarTeamDashboard",
            ),
            "by_days_rest": parse_result_set_by_name(
                data,
                "DaysRestTeamDashboard",
            ),
        }
