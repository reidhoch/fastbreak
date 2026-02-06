"""Models for the draft combine non-stationary shooting endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class NonstationaryShootingPlayer(PandasMixin, PolarsMixin, BaseModel):
    """A player's draft combine non-stationary shooting results."""

    # Basic info
    temp_player_id: int = Field(alias="TEMP_PLAYER_ID")
    player_id: int = Field(alias="PLAYER_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    player_name: str = Field(alias="PLAYER_NAME")
    position: str = Field(alias="POSITION")

    # Off-dribble 15-foot shooting
    off_drib_fifteen_break_left_made: int | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_LEFT_MADE"
    )
    off_drib_fifteen_break_left_attempt: int | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_LEFT_ATTEMPT"
    )
    off_drib_fifteen_break_left_pct: float | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_LEFT_PCT"
    )
    off_drib_fifteen_top_key_made: int | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_TOP_KEY_MADE"
    )
    off_drib_fifteen_top_key_attempt: int | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_TOP_KEY_ATTEMPT"
    )
    off_drib_fifteen_top_key_pct: float | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_TOP_KEY_PCT"
    )
    off_drib_fifteen_break_right_made: int | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_RIGHT_MADE"
    )
    off_drib_fifteen_break_right_attempt: int | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_RIGHT_ATTEMPT"
    )
    off_drib_fifteen_break_right_pct: float | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_RIGHT_PCT"
    )

    # Off-dribble college 3-point shooting
    off_drib_college_break_left_made: int | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_LEFT_MADE"
    )
    off_drib_college_break_left_attempt: int | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_LEFT_ATTEMPT"
    )
    off_drib_college_break_left_pct: float | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_LEFT_PCT"
    )
    off_drib_college_top_key_made: int | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_TOP_KEY_MADE"
    )
    off_drib_college_top_key_attempt: int | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_TOP_KEY_ATTEMPT"
    )
    off_drib_college_top_key_pct: float | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_TOP_KEY_PCT"
    )
    off_drib_college_break_right_made: int | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_RIGHT_MADE"
    )
    off_drib_college_break_right_attempt: int | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_RIGHT_ATTEMPT"
    )
    off_drib_college_break_right_pct: float | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_RIGHT_PCT"
    )

    # On-the-move shooting
    on_move_fifteen_made: int | None = Field(default=None, alias="ON_MOVE_FIFTEEN_MADE")
    on_move_fifteen_attempt: int | None = Field(
        default=None, alias="ON_MOVE_FIFTEEN_ATTEMPT"
    )
    on_move_fifteen_pct: float | None = Field(default=None, alias="ON_MOVE_FIFTEEN_PCT")
    on_move_college_made: int | None = Field(default=None, alias="ON_MOVE_COLLEGE_MADE")
    on_move_college_attempt: int | None = Field(
        default=None, alias="ON_MOVE_COLLEGE_ATTEMPT"
    )
    on_move_college_pct: float | None = Field(default=None, alias="ON_MOVE_COLLEGE_PCT")


class DraftCombineNonstationaryShootingResponse(FrozenResponse):
    """Response from the draft combine non-stationary shooting endpoint."""

    players: list[NonstationaryShootingPlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
