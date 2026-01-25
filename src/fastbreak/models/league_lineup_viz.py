"""Models for the league lineup viz endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class LineupViz(BaseModel):
    """Lineup visualization statistics for a player combination."""

    group_id: str = Field(alias="GROUP_ID")
    group_name: str = Field(alias="GROUP_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    min: float = Field(alias="MIN")
    off_rating: float = Field(alias="OFF_RATING")
    def_rating: float = Field(alias="DEF_RATING")
    net_rating: float = Field(alias="NET_RATING")
    pace: float = Field(alias="PACE")
    ts_pct: float = Field(alias="TS_PCT")
    fta_rate: float = Field(alias="FTA_RATE")
    tm_ast_pct: float = Field(alias="TM_AST_PCT")
    pct_fga_2pt: float = Field(alias="PCT_FGA_2PT")
    pct_fga_3pt: float = Field(alias="PCT_FGA_3PT")
    pct_pts_2pt_mr: float = Field(alias="PCT_PTS_2PT_MR")
    pct_pts_fb: float = Field(alias="PCT_PTS_FB")
    pct_pts_ft: float = Field(alias="PCT_PTS_FT")
    pct_pts_paint: float = Field(alias="PCT_PTS_PAINT")
    pct_ast_fgm: float = Field(alias="PCT_AST_FGM")
    pct_uast_fgm: float = Field(alias="PCT_UAST_FGM")
    opp_fg3_pct: float = Field(alias="OPP_FG3_PCT")
    opp_efg_pct: float = Field(alias="OPP_EFG_PCT")
    opp_fta_rate: float = Field(alias="OPP_FTA_RATE")
    opp_tov_pct: float = Field(alias="OPP_TOV_PCT")
    sum_tm_min: float = Field(alias="SUM_TM_MIN")


class LeagueLineupVizResponse(BaseModel):
    """Response from the league lineup viz endpoint.

    Contains lineup visualization statistics for player combinations.
    """

    lineups: list[LineupViz] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "lineups": parse_result_set_by_name(
                data,
                "LeagueLineupViz",
            ),
        }
