"""Models for the leaders tiles endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import singular_result_set_validator


class LeaderTile(PandasMixin, PolarsMixin, BaseModel):
    """A leader tile entry showing current stat leaders."""

    rank: int = Field(alias="RANK")
    player_id: int = Field(alias="PLAYER_ID")
    player: str = Field(alias="PLAYER")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    pts: float = Field(alias="PTS")


class AllTimeSeasonHigh(PandasMixin, PolarsMixin, BaseModel):
    """Historical all-time season high record for comparison."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    pts: float = Field(alias="PTS")
    season_year: str = Field(alias="SEASON_YEAR")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")


class LastSeasonHigh(PandasMixin, PolarsMixin, BaseModel):
    """Last season's high for comparison."""

    rank: int = Field(alias="RANK")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    pts: float = Field(alias="PTS")
    season_year: str = Field(alias="SEASON_YEAR")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")


class LeadersTilesResponse(FrozenResponse):
    """Response from the leaders tiles endpoint.

    Contains current stat leaders plus historical comparisons including
    the all-time season high and last season's leader for the stat.
    """

    leaders: list[LeaderTile] = Field(default_factory=list)
    all_time_season_high: list[AllTimeSeasonHigh] = Field(default_factory=list)
    last_season_high: list[LastSeasonHigh] = Field(default_factory=list)

    from_result_set = model_validator(mode="before")(
        singular_result_set_validator(
            {
                "leaders": "LeadersTiles",
                "all_time_season_high": "AllTimeSeasonHigh",
                "last_season_high": "LastSeasonHigh",
            }
        )
    )
