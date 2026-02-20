"""Models for the video status endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class GameVideoStatus(PandasMixin, PolarsMixin, BaseModel):
    """Video availability status for a single game."""

    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    visitor_team_id: int = Field(alias="VISITOR_TEAM_ID")
    visitor_team_city: str = Field(alias="VISITOR_TEAM_CITY")
    visitor_team_name: str = Field(alias="VISITOR_TEAM_NAME")
    visitor_team_abbreviation: str = Field(alias="VISITOR_TEAM_ABBREVIATION")
    home_team_id: int = Field(alias="HOME_TEAM_ID")
    home_team_city: str = Field(alias="HOME_TEAM_CITY")
    home_team_name: str = Field(alias="HOME_TEAM_NAME")
    home_team_abbreviation: str = Field(alias="HOME_TEAM_ABBREVIATION")
    game_status: int = Field(alias="GAME_STATUS")
    game_status_text: str = Field(alias="GAME_STATUS_TEXT")
    is_available: int = Field(alias="IS_AVAILABLE")
    pt_xyz_available: int = Field(alias="PT_XYZ_AVAILABLE")


class VideoStatusResponse(FrozenResponse):
    """Response from the videostatus endpoint.

    Contains video availability status for games on a given date.
    """

    games: list[GameVideoStatus] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": "VideoStatus"})
    )
