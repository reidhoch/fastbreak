"""Models for the league leaders endpoint."""

from typing import Any, TypeGuard

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


def _is_singular_result_set(data: object) -> TypeGuard[dict[str, Any]]:
    """Check if data uses the singular resultSet format."""
    return isinstance(data, dict) and "resultSet" in data


def _parse_singular_result_set(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse data from a singular resultSet response."""
    result_set = data["resultSet"]
    headers: list[str] = result_set["headers"]
    rows: list[list[Any]] = result_set["rowSet"]
    return [dict(zip(headers, row, strict=True)) for row in rows]


class LeagueLeader(PandasMixin, PolarsMixin, BaseModel):
    """A player's league leader statistics."""

    player_id: int = Field(alias="PLAYER_ID")
    rank: int = Field(alias="RANK")
    player: str = Field(alias="PLAYER")
    team_id: int = Field(alias="TEAM_ID")
    team: str = Field(alias="TEAM")
    gp: int = Field(alias="GP")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pts: float = Field(alias="PTS")
    eff: float = Field(alias="EFF")


class LeagueLeadersResponse(BaseModel):
    """Response from the league leaders endpoint.

    Contains ranked player statistics for a specific category.
    """

    leaders: list[LeagueLeader] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_set(cls, data: object) -> dict[str, Any]:
        """Transform NBA's singular resultSet format into structured data."""
        if not _is_singular_result_set(data):
            return data  # type: ignore[return-value]

        return {
            "leaders": _parse_singular_result_set(data),
        }
