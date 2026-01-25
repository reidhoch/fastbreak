"""Models for the Player Compare endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class PlayerCompareStats(BaseModel):
    """Statistics for a player in the comparison.

    Contains aggregated stats for a player or group of players.
    """

    group_set: str = Field(alias="GROUP_SET")
    description: str = Field(alias="DESCRIPTION")
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
    tov: float = Field(alias="TOV")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    blka: float = Field(alias="BLKA")
    pf: float = Field(alias="PF")
    pfd: float = Field(alias="PFD")
    pts: float = Field(alias="PTS")
    plus_minus: float = Field(alias="PLUS_MINUS")


class PlayerCompareResponse(BaseModel):
    """Response from the player compare endpoint.

    Contains two result sets:
    - overall_compare: Combined stats for each player group
    - individual: Individual player stats for comparison
    """

    overall_compare: list[PlayerCompareStats] = Field(default_factory=list)
    individual: list[PlayerCompareStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "overall_compare": parse_result_set_by_name(
                data,
                "OverallCompare",
            ),
            "individual": parse_result_set_by_name(
                data,
                "Individual",
            ),
        }
