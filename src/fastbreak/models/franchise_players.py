"""Models for the franchise players endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class FranchisePlayer(PandasMixin, PolarsMixin, BaseModel):
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

    # Rebounds (OREB/DREB not tracked before 1973, REB missing for some early seasons)
    oreb: float | None = Field(default=None, alias="OREB")
    dreb: float | None = Field(default=None, alias="DREB")
    reb: float | None = Field(default=None, alias="REB")

    # Other stats (STL/BLK not tracked before 1973, TOV not tracked before 1977)
    ast: float = Field(alias="AST")
    pf: float = Field(alias="PF")
    stl: float | None = Field(default=None, alias="STL")
    tov: float | None = Field(default=None, alias="TOV")
    blk: float | None = Field(default=None, alias="BLK")
    pts: float = Field(alias="PTS")


class FranchisePlayersResponse(FrozenResponse):
    """Response from the franchise players endpoint."""

    players: list[FranchisePlayer] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("players"))
