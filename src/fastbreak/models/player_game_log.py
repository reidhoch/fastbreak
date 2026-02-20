"""Models for the Player Game Log endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class PlayerGameLogEntry(PandasMixin, PolarsMixin, BaseModel):
    """A single game entry in a player's game log.

    Contains traditional box score statistics for one game.
    """

    season_id: str = Field(alias="SEASON_ID")
    player_id: int = Field(alias="Player_ID")
    game_id: str = Field(alias="Game_ID")
    game_date: str = Field(alias="GAME_DATE")
    matchup: str = Field(alias="MATCHUP")
    wl: str | None = Field(alias="WL")
    minutes: int | None = Field(alias="MIN")
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
    pts: int = Field(alias="PTS")
    plus_minus: int | None = Field(alias="PLUS_MINUS")
    video_available: int = Field(alias="VIDEO_AVAILABLE")


class PlayerGameLogResponse(FrozenResponse):
    """Response from the player game log endpoint.

    Contains a list of game log entries for a player's season.
    """

    games: list[PlayerGameLogEntry] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": "PlayerGameLog"})
    )
