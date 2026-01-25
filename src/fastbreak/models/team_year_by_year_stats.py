"""Models for the Team Year by Year Stats endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class TeamYearStats(PandasMixin, PolarsMixin, BaseModel):
    """A single season's statistics for a team.

    Contains traditional stats plus playoff and ranking info.
    """

    team_id: int = Field(alias="TEAM_ID")
    team_city: str = Field(alias="TEAM_CITY")
    team_name: str = Field(alias="TEAM_NAME")
    year: str = Field(alias="YEAR")

    # Record
    gp: int = Field(alias="GP")
    wins: int = Field(alias="WINS")
    losses: int = Field(alias="LOSSES")
    win_pct: float = Field(alias="WIN_PCT")

    # Rankings
    conf_rank: int = Field(alias="CONF_RANK")
    div_rank: int = Field(alias="DIV_RANK")

    # Playoff info
    po_wins: int = Field(alias="PO_WINS")
    po_losses: int = Field(alias="PO_LOSSES")
    # Conference/division counts (not tracked for all historical seasons)
    conf_count: int | None = Field(default=None, alias="CONF_COUNT")
    div_count: int | None = Field(default=None, alias="DIV_COUNT")
    nba_finals_appearance: str = Field(alias="NBA_FINALS_APPEARANCE")

    # Traditional stats
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    pf: float = Field(alias="PF")
    stl: float = Field(alias="STL")
    tov: float = Field(alias="TOV")
    blk: float = Field(alias="BLK")
    pts: float = Field(alias="PTS")
    pts_rank: int = Field(alias="PTS_RANK")


class TeamYearByYearStatsResponse(BaseModel):
    """Response from the team year by year stats endpoint.

    Contains historical season-by-season statistics for a franchise.
    """

    seasons: list[TeamYearStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "seasons": parse_result_set_by_name(data, "TeamStats"),
        }
