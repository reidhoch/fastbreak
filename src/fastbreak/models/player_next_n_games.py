"""Models for the Player Next N Games endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class NextGame(PandasMixin, PolarsMixin, BaseModel):
    """An upcoming game for a player.

    Contains game schedule information including both teams.
    """

    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    home_team_id: int = Field(alias="HOME_TEAM_ID")
    visitor_team_id: int = Field(alias="VISITOR_TEAM_ID")
    home_team_name: str = Field(alias="HOME_TEAM_NAME")
    visitor_team_name: str = Field(alias="VISITOR_TEAM_NAME")
    home_team_abbreviation: str = Field(alias="HOME_TEAM_ABBREVIATION")
    visitor_team_abbreviation: str = Field(alias="VISITOR_TEAM_ABBREVIATION")
    home_team_nickname: str = Field(alias="HOME_TEAM_NICKNAME")
    visitor_team_nickname: str = Field(alias="VISITOR_TEAM_NICKNAME")
    game_time: str | None = Field(alias="GAME_TIME")
    home_wl: str | None = Field(alias="HOME_WL")
    visitor_wl: str | None = Field(alias="VISITOR_WL")


class PlayerNextNGamesResponse(FrozenResponse):
    """Response from the player next N games endpoint.

    Contains a list of upcoming games for a player.
    """

    games: list[NextGame] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": "NextNGames"})
    )
