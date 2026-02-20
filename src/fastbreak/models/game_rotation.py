"""Models for the game rotation endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class RotationEntry(PandasMixin, PolarsMixin, BaseModel):
    """A single rotation entry (player stint)."""

    game_id: str = Field(alias="GAME_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_city: str = Field(alias="TEAM_CITY")
    team_name: str = Field(alias="TEAM_NAME")
    person_id: int = Field(alias="PERSON_ID")
    player_first: str = Field(alias="PLAYER_FIRST")
    player_last: str = Field(alias="PLAYER_LAST")
    in_time_real: float = Field(alias="IN_TIME_REAL")
    out_time_real: float = Field(alias="OUT_TIME_REAL")
    player_pts: int = Field(alias="PLAYER_PTS")
    pt_diff: float = Field(alias="PT_DIFF")
    usg_pct: float = Field(alias="USG_PCT")


class GameRotationResponse(FrozenResponse):
    """Response from the game rotation endpoint."""

    away_team: list[RotationEntry] = Field(default_factory=list)
    home_team: list[RotationEntry] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "away_team": "AwayTeam",
                "home_team": "HomeTeam",
            }
        )
    )
