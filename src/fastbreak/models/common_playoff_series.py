"""Models for the common playoff series endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class PlayoffSeriesGame(PandasMixin, PolarsMixin, BaseModel):
    """A single game in a playoff series."""

    game_id: str = Field(alias="GAME_ID")
    home_team_id: int = Field(alias="HOME_TEAM_ID")
    visitor_team_id: int = Field(alias="VISITOR_TEAM_ID")
    series_id: str = Field(alias="SERIES_ID")
    game_num: int = Field(alias="GAME_NUM")


class CommonPlayoffSeriesResponse(FrozenResponse):
    """Response from the common playoff series endpoint."""

    games: list[PlayoffSeriesGame] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("games"))
