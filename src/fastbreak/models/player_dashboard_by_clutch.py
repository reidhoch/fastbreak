"""Models for the Player Dashboard by Clutch endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_single_result_set,
)


class ClutchStats(PandasMixin, PolarsMixin, BaseModel):
    """Player statistics for a clutch time scenario.

    Contains aggregated stats and league ranks for a specific clutch definition.
    """

    # Identifiers
    group_set: str = Field(alias="GROUP_SET")
    group_value: str = Field(alias="GROUP_VALUE")

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

    # Fantasy stats
    nba_fantasy_pts: float = Field(alias="NBA_FANTASY_PTS")
    dd2: int = Field(alias="DD2")
    td3: int = Field(alias="TD3")
    wnba_fantasy_pts: float = Field(alias="WNBA_FANTASY_PTS")

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
    nba_fantasy_pts_rank: int = Field(alias="NBA_FANTASY_PTS_RANK")
    dd2_rank: int = Field(alias="DD2_RANK")
    td3_rank: int = Field(alias="TD3_RANK")
    wnba_fantasy_pts_rank: int = Field(alias="WNBA_FANTASY_PTS_RANK")
    team_count: int = Field(alias="TEAM_COUNT")


class PlayerDashboardByClutchResponse(BaseModel):
    """Response from the player dashboard by clutch endpoint.

    Contains stats for various clutch time definitions:
    - overall: Overall player stats (not clutch-filtered)
    - last_5_min_lte_5_pts: Last 5 min, team trailing/tied by <= 5 points
    - last_3_min_lte_5_pts: Last 3 min, team trailing/tied by <= 5 points
    - last_1_min_lte_5_pts: Last 1 min, team trailing/tied by <= 5 points
    - last_30_sec_lte_3_pts: Last 30 sec, team trailing/tied by <= 3 points
    - last_10_sec_lte_3_pts: Last 10 sec, team trailing/tied by <= 3 points
    - last_5_min_pm_5_pts: Last 5 min, score +/- 5 points
    - last_3_min_pm_5_pts: Last 3 min, score +/- 5 points
    - last_1_min_pm_5_pts: Last 1 min, score +/- 5 points
    - last_30_sec_pm_3_pts: Last 30 sec, score +/- 3 points
    - last_10_sec_pm_3_pts: Last 10 sec, score +/- 3 points
    """

    overall: ClutchStats | None = None
    last_5_min_lte_5_pts: ClutchStats | None = None
    last_3_min_lte_5_pts: ClutchStats | None = None
    last_1_min_lte_5_pts: ClutchStats | None = None
    last_30_sec_lte_3_pts: ClutchStats | None = None
    last_10_sec_lte_3_pts: ClutchStats | None = None
    last_5_min_pm_5_pts: ClutchStats | None = None
    last_3_min_pm_5_pts: ClutchStats | None = None
    last_1_min_pm_5_pts: ClutchStats | None = None
    last_30_sec_pm_3_pts: ClutchStats | None = None
    last_10_sec_pm_3_pts: ClutchStats | None = None

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "overall": parse_single_result_set(d, "OverallPlayerDashboard"),
            "last_5_min_lte_5_pts": parse_single_result_set(
                d, "Last5Min5PointPlayerDashboard"
            ),
            "last_3_min_lte_5_pts": parse_single_result_set(
                d, "Last3Min5PointPlayerDashboard"
            ),
            "last_1_min_lte_5_pts": parse_single_result_set(
                d, "Last1Min5PointPlayerDashboard"
            ),
            "last_30_sec_lte_3_pts": parse_single_result_set(
                d, "Last30Sec3PointPlayerDashboard"
            ),
            "last_10_sec_lte_3_pts": parse_single_result_set(
                d, "Last10Sec3PointPlayerDashboard"
            ),
            "last_5_min_pm_5_pts": parse_single_result_set(
                d, "Last5MinPlusMinus5PointPlayerDashboard"
            ),
            "last_3_min_pm_5_pts": parse_single_result_set(
                d, "Last3MinPlusMinus5PointPlayerDashboard"
            ),
            "last_1_min_pm_5_pts": parse_single_result_set(
                d, "Last1MinPlusMinus5PointPlayerDashboard"
            ),
            "last_30_sec_pm_3_pts": parse_single_result_set(
                d, "Last30Sec3Point2PlayerDashboard"
            ),
            "last_10_sec_pm_3_pts": parse_single_result_set(
                d, "Last10Sec3Point2PlayerDashboard"
            ),
        }
