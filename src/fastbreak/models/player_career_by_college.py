"""Response models for the playercareerbycollege endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class CollegePlayerCareer(PandasMixin, PolarsMixin, BaseModel):
    """Career statistics for a player who attended a specific college."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    college: str = Field(alias="COLLEGE")
    gp: int = Field(alias="GP")
    min: float = Field(alias="MIN")
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
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class PlayerCareerByCollegeResponse(BaseModel):
    """Response from the playercareerbycollege endpoint.

    Contains career statistics for all NBA players from a specific college.
    """

    players: list[CollegePlayerCareer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
