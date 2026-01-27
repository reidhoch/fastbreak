"""Models for the all-time leaders grids endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class LeaderEntry(PandasMixin, PolarsMixin, BaseModel):
    """A single player's entry in a leader category."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    rank: int
    value: float
    is_active: bool


class AllTimeLeadersResponse(BaseModel):
    """Response from the all-time leaders grids endpoint."""

    gp_leaders: list[LeaderEntry] = Field(default_factory=list)
    pts_leaders: list[LeaderEntry] = Field(default_factory=list)
    ast_leaders: list[LeaderEntry] = Field(default_factory=list)
    stl_leaders: list[LeaderEntry] = Field(default_factory=list)
    oreb_leaders: list[LeaderEntry] = Field(default_factory=list)
    dreb_leaders: list[LeaderEntry] = Field(default_factory=list)
    reb_leaders: list[LeaderEntry] = Field(default_factory=list)
    blk_leaders: list[LeaderEntry] = Field(default_factory=list)
    fgm_leaders: list[LeaderEntry] = Field(default_factory=list)
    fga_leaders: list[LeaderEntry] = Field(default_factory=list)
    fg_pct_leaders: list[LeaderEntry] = Field(default_factory=list)
    tov_leaders: list[LeaderEntry] = Field(default_factory=list)
    fg3m_leaders: list[LeaderEntry] = Field(default_factory=list)
    fg3a_leaders: list[LeaderEntry] = Field(default_factory=list)
    fg3_pct_leaders: list[LeaderEntry] = Field(default_factory=list)
    pf_leaders: list[LeaderEntry] = Field(default_factory=list)
    ftm_leaders: list[LeaderEntry] = Field(default_factory=list)
    fta_leaders: list[LeaderEntry] = Field(default_factory=list)
    ft_pct_leaders: list[LeaderEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        categories = {
            "GPLeaders": ("gp_leaders", "GP", "GP_RANK"),
            "PTSLeaders": ("pts_leaders", "PTS", "PTS_RANK"),
            "ASTLeaders": ("ast_leaders", "AST", "AST_RANK"),
            "STLLeaders": ("stl_leaders", "STL", "STL_RANK"),
            "OREBLeaders": ("oreb_leaders", "OREB", "OREB_RANK"),
            "DREBLeaders": ("dreb_leaders", "DREB", "DREB_RANK"),
            "REBLeaders": ("reb_leaders", "REB", "REB_RANK"),
            "BLKLeaders": ("blk_leaders", "BLK", "BLK_RANK"),
            "FGMLeaders": ("fgm_leaders", "FGM", "FGM_RANK"),
            "FGALeaders": ("fga_leaders", "FGA", "FGA_RANK"),
            "FG_PCTLeaders": ("fg_pct_leaders", "FG_PCT", "FG_PCT_RANK"),
            "TOVLeaders": ("tov_leaders", "TOV", "TOV_RANK"),
            "FG3MLeaders": ("fg3m_leaders", "FG3M", "FG3M_RANK"),
            "FG3ALeaders": ("fg3a_leaders", "FG3A", "FG3A_RANK"),
            "FG3_PCTLeaders": ("fg3_pct_leaders", "FG3_PCT", "FG3_PCT_RANK"),
            "PFLeaders": ("pf_leaders", "PF", "PF_RANK"),
            "FTMLeaders": ("ftm_leaders", "FTM", "FTM_RANK"),
            "FTALeaders": ("fta_leaders", "FTA", "FTA_RANK"),
            "FT_PCTLeaders": ("ft_pct_leaders", "FT_PCT", "FT_PCT_RANK"),
        }

        result: dict[str, list[dict[str, Any]]] = {}

        for rs_name, (field_name, stat_col, rank_col) in categories.items():
            rows = parse_result_set_by_name(data, rs_name)
            result[field_name] = [
                {
                    "PLAYER_ID": row["PLAYER_ID"],
                    "PLAYER_NAME": row["PLAYER_NAME"],
                    "rank": row[rank_col],
                    "value": row[stat_col],
                    "is_active": row["IS_ACTIVE_FLAG"] == "Y",
                }
                for row in rows
            ]

        return result
