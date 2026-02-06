"""Models for the draft combine spot shooting endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class SpotShootingPlayer(PandasMixin, PolarsMixin, BaseModel):
    """A player's draft combine spot shooting results."""

    # Basic info
    temp_player_id: int = Field(alias="TEMP_PLAYER_ID")
    player_id: int = Field(alias="PLAYER_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    player_name: str = Field(alias="PLAYER_NAME")
    position: str = Field(alias="POSITION")

    # 15-foot shooting
    fifteen_corner_left_made: int | None = Field(
        default=None, alias="FIFTEEN_CORNER_LEFT_MADE"
    )
    fifteen_corner_left_attempt: int | None = Field(
        default=None, alias="FIFTEEN_CORNER_LEFT_ATTEMPT"
    )
    fifteen_corner_left_pct: float | None = Field(
        default=None, alias="FIFTEEN_CORNER_LEFT_PCT"
    )
    fifteen_break_left_made: int | None = Field(
        default=None, alias="FIFTEEN_BREAK_LEFT_MADE"
    )
    fifteen_break_left_attempt: int | None = Field(
        default=None, alias="FIFTEEN_BREAK_LEFT_ATTEMPT"
    )
    fifteen_break_left_pct: float | None = Field(
        default=None, alias="FIFTEEN_BREAK_LEFT_PCT"
    )
    fifteen_top_key_made: int | None = Field(default=None, alias="FIFTEEN_TOP_KEY_MADE")
    fifteen_top_key_attempt: int | None = Field(
        default=None, alias="FIFTEEN_TOP_KEY_ATTEMPT"
    )
    fifteen_top_key_pct: float | None = Field(default=None, alias="FIFTEEN_TOP_KEY_PCT")
    fifteen_break_right_made: int | None = Field(
        default=None, alias="FIFTEEN_BREAK_RIGHT_MADE"
    )
    fifteen_break_right_attempt: int | None = Field(
        default=None, alias="FIFTEEN_BREAK_RIGHT_ATTEMPT"
    )
    fifteen_break_right_pct: float | None = Field(
        default=None, alias="FIFTEEN_BREAK_RIGHT_PCT"
    )
    fifteen_corner_right_made: int | None = Field(
        default=None, alias="FIFTEEN_CORNER_RIGHT_MADE"
    )
    fifteen_corner_right_attempt: int | None = Field(
        default=None, alias="FIFTEEN_CORNER_RIGHT_ATTEMPT"
    )
    fifteen_corner_right_pct: float | None = Field(
        default=None, alias="FIFTEEN_CORNER_RIGHT_PCT"
    )

    # College 3-point shooting
    college_corner_left_made: int | None = Field(
        default=None, alias="COLLEGE_CORNER_LEFT_MADE"
    )
    college_corner_left_attempt: int | None = Field(
        default=None, alias="COLLEGE_CORNER_LEFT_ATTEMPT"
    )
    college_corner_left_pct: float | None = Field(
        default=None, alias="COLLEGE_CORNER_LEFT_PCT"
    )
    college_break_left_made: int | None = Field(
        default=None, alias="COLLEGE_BREAK_LEFT_MADE"
    )
    college_break_left_attempt: int | None = Field(
        default=None, alias="COLLEGE_BREAK_LEFT_ATTEMPT"
    )
    college_break_left_pct: float | None = Field(
        default=None, alias="COLLEGE_BREAK_LEFT_PCT"
    )
    college_top_key_made: int | None = Field(default=None, alias="COLLEGE_TOP_KEY_MADE")
    college_top_key_attempt: int | None = Field(
        default=None, alias="COLLEGE_TOP_KEY_ATTEMPT"
    )
    college_top_key_pct: float | None = Field(default=None, alias="COLLEGE_TOP_KEY_PCT")
    college_break_right_made: int | None = Field(
        default=None, alias="COLLEGE_BREAK_RIGHT_MADE"
    )
    college_break_right_attempt: int | None = Field(
        default=None, alias="COLLEGE_BREAK_RIGHT_ATTEMPT"
    )
    college_break_right_pct: float | None = Field(
        default=None, alias="COLLEGE_BREAK_RIGHT_PCT"
    )
    college_corner_right_made: int | None = Field(
        default=None, alias="COLLEGE_CORNER_RIGHT_MADE"
    )
    college_corner_right_attempt: int | None = Field(
        default=None, alias="COLLEGE_CORNER_RIGHT_ATTEMPT"
    )
    college_corner_right_pct: float | None = Field(
        default=None, alias="COLLEGE_CORNER_RIGHT_PCT"
    )

    # NBA 3-point shooting
    nba_corner_left_made: int | None = Field(default=None, alias="NBA_CORNER_LEFT_MADE")
    nba_corner_left_attempt: int | None = Field(
        default=None, alias="NBA_CORNER_LEFT_ATTEMPT"
    )
    nba_corner_left_pct: float | None = Field(default=None, alias="NBA_CORNER_LEFT_PCT")
    nba_break_left_made: int | None = Field(default=None, alias="NBA_BREAK_LEFT_MADE")
    nba_break_left_attempt: int | None = Field(
        default=None, alias="NBA_BREAK_LEFT_ATTEMPT"
    )
    nba_break_left_pct: float | None = Field(default=None, alias="NBA_BREAK_LEFT_PCT")
    nba_top_key_made: int | None = Field(default=None, alias="NBA_TOP_KEY_MADE")
    nba_top_key_attempt: int | None = Field(default=None, alias="NBA_TOP_KEY_ATTEMPT")
    nba_top_key_pct: float | None = Field(default=None, alias="NBA_TOP_KEY_PCT")
    nba_break_right_made: int | None = Field(default=None, alias="NBA_BREAK_RIGHT_MADE")
    nba_break_right_attempt: int | None = Field(
        default=None, alias="NBA_BREAK_RIGHT_ATTEMPT"
    )
    nba_break_right_pct: float | None = Field(default=None, alias="NBA_BREAK_RIGHT_PCT")
    nba_corner_right_made: int | None = Field(
        default=None, alias="NBA_CORNER_RIGHT_MADE"
    )
    nba_corner_right_attempt: int | None = Field(
        default=None, alias="NBA_CORNER_RIGHT_ATTEMPT"
    )
    nba_corner_right_pct: float | None = Field(
        default=None, alias="NBA_CORNER_RIGHT_PCT"
    )


class DraftCombineSpotShootingResponse(FrozenResponse):
    """Response from the draft combine spot shooting endpoint."""

    players: list[SpotShootingPlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
