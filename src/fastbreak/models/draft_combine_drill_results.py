"""Models for the draft combine drill results endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class DrillResultsPlayer(PandasMixin, PolarsMixin, BaseModel):
    """A player's draft combine athletic drill results."""

    # Basic info
    temp_player_id: int = Field(alias="TEMP_PLAYER_ID")
    player_id: int = Field(alias="PLAYER_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    player_name: str = Field(alias="PLAYER_NAME")
    position: str = Field(alias="POSITION")

    # Vertical leap (inches)
    standing_vertical_leap: float | None = Field(
        default=None, alias="STANDING_VERTICAL_LEAP"
    )
    max_vertical_leap: float | None = Field(default=None, alias="MAX_VERTICAL_LEAP")

    # Agility drill times (measured in seconds)
    lane_agility_time: float | None = Field(default=None, alias="LANE_AGILITY_TIME")
    modified_lane_agility_time: float | None = Field(
        default=None, alias="MODIFIED_LANE_AGILITY_TIME"
    )

    # Speed drill times (measured in seconds)
    three_quarter_sprint: float | None = Field(
        default=None, alias="THREE_QUARTER_SPRINT"
    )

    # Strength drill results (measured in reps)
    bench_press: int | None = Field(default=None, alias="BENCH_PRESS")


class DraftCombineDrillResultsResponse(FrozenResponse):
    """Response from the draft combine drill results endpoint."""

    players: list[DrillResultsPlayer] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("players"))
