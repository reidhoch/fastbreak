"""Models for the franchise players endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class FranchisePlayer(BaseModel):
    """A player's franchise career statistics."""

    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    team: str = Field(alias="TEAM")
    person_id: int = Field(alias="PERSON_ID")
    player: str = Field(alias="PLAYER")
    season_type: str = Field(alias="SEASON_TYPE")
    active_with_team: int = Field(alias="ACTIVE_WITH_TEAM")

    # Games
    gp: int = Field(alias="GP")

    # Shooting
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")
    fg3m: float | None = Field(default=None, alias="FG3M")
    fg3a: float | None = Field(default=None, alias="FG3A")
    fg3_pct: float | None = Field(default=None, alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(default=None, alias="FT_PCT")

    # Rebounds
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")

    # Other stats
    ast: float = Field(alias="AST")
    pf: float = Field(alias="PF")
    stl: float = Field(alias="STL")
    tov: float | None = Field(default=None, alias="TOV")
    blk: float = Field(alias="BLK")
    pts: float = Field(alias="PTS")


class FranchisePlayersResponse(BaseModel):
    """Response from the franchise players endpoint."""

    players: list[FranchisePlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
