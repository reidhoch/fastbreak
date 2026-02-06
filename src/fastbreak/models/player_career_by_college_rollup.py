"""Response models for the playercareerbycollegerollup endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class CollegeRollupEntry(PandasMixin, PolarsMixin, BaseModel):
    """NCAA tournament region rollup showing NBA stats from college players."""

    region: str = Field(alias="REGION")
    seed: int = Field(alias="SEED")
    college: str = Field(alias="COLLEGE")
    players: int = Field(alias="PLAYERS")
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


class PlayerCareerByCollegeRollupResponse(FrozenResponse):
    """Response from the playercareerbycollegerollup endpoint.

    Contains NBA career statistics rolled up by college and NCAA tournament
    region/seed. Organized by tournament regions (East, Midwest, South, West).
    """

    entries: list[CollegeRollupEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSet format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"entries": rows}
