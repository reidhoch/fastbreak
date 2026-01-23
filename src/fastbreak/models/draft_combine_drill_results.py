"""Models for the draft combine drill results endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class DrillResultsPlayer(BaseModel):
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


class DraftCombineDrillResultsResponse(BaseModel):
    """Response from the draft combine drill results endpoint."""

    players: list[DrillResultsPlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
