"""League dashboard player stats response model."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class LeagueDashPlayerStatsRow(PandasMixin, PolarsMixin, BaseModel):
    """Individual player statistics from league dashboard."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    nickname: str | None = Field(default=None, alias="NICKNAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    age: float | None = Field(default=None, alias="AGE")
    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    w_pct: float | None = Field(default=None, alias="W_PCT")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(default=None, alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(default=None, alias="FT_PCT")
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
    nba_fantasy_pts: float | None = Field(default=None, alias="NBA_FANTASY_PTS")
    dd2: int | None = Field(default=None, alias="DD2")
    td3: int | None = Field(default=None, alias="TD3")


class LeagueDashPlayerStatsResponse(FrozenResponse):
    """Response from leaguedashplayerstats endpoint."""

    players: list[LeagueDashPlayerStatsRow] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("players"))
