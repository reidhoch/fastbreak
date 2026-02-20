"""Models for the league game finder endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class GameFinderResult(PandasMixin, PolarsMixin, BaseModel):
    """A single game result from the league game finder."""

    season_id: str = Field(alias="SEASON_ID")
    team_id: int | None = Field(default=None, alias="TEAM_ID")
    team_abbreviation: str | None = Field(default=None, alias="TEAM_ABBREVIATION")
    team_name: str | None = Field(default=None, alias="TEAM_NAME")
    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    matchup: str | None = Field(default=None, alias="MATCHUP")
    wl: str | None = Field(alias="WL")
    min: int = Field(alias="MIN")
    pts: int = Field(alias="PTS")
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: int = Field(alias="FTM")
    fta: int = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: int = Field(alias="OREB")
    dreb: int = Field(alias="DREB")
    reb: int = Field(alias="REB")
    ast: int = Field(alias="AST")
    stl: int = Field(alias="STL")
    blk: int = Field(alias="BLK")
    tov: int = Field(alias="TOV")
    pf: int = Field(alias="PF")
    plus_minus: float | None = Field(alias="PLUS_MINUS")


class LeagueGameFinderResponse(FrozenResponse):
    """Response from the league game finder endpoint.

    Contains a list of games matching the search criteria with box score stats.
    """

    games: list[GameFinderResult] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": "LeagueGameFinderResults"})
    )
