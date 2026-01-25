"""Models for the draft combine stats endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class CombinePlayer(PandasMixin, PolarsMixin, BaseModel):
    """A player's draft combine measurements and drill results."""

    # Basic info
    season: str = Field(alias="SEASON")
    player_id: int = Field(alias="PLAYER_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    player_name: str = Field(alias="PLAYER_NAME")
    position: str = Field(alias="POSITION")

    # Anthropometric measurements (inches unless noted)
    height_wo_shoes: float | None = Field(default=None, alias="HEIGHT_WO_SHOES")
    height_wo_shoes_ft_in: str | None = Field(
        default=None, alias="HEIGHT_WO_SHOES_FT_IN"
    )
    height_w_shoes: float | None = Field(default=None, alias="HEIGHT_W_SHOES")
    height_w_shoes_ft_in: str | None = Field(default=None, alias="HEIGHT_W_SHOES_FT_IN")
    weight: float | None = Field(default=None, alias="WEIGHT")
    wingspan: float | None = Field(default=None, alias="WINGSPAN")
    wingspan_ft_in: str | None = Field(default=None, alias="WINGSPAN_FT_IN")
    standing_reach: float | None = Field(default=None, alias="STANDING_REACH")
    standing_reach_ft_in: str | None = Field(default=None, alias="STANDING_REACH_FT_IN")
    body_fat_pct: float | None = Field(default=None, alias="BODY_FAT_PCT")
    hand_length: float | None = Field(default=None, alias="HAND_LENGTH")
    hand_width: float | None = Field(default=None, alias="HAND_WIDTH")

    # Athletic testing
    standing_vertical_leap: float | None = Field(
        default=None, alias="STANDING_VERTICAL_LEAP"
    )
    max_vertical_leap: float | None = Field(default=None, alias="MAX_VERTICAL_LEAP")
    lane_agility_time: float | None = Field(default=None, alias="LANE_AGILITY_TIME")
    modified_lane_agility_time: float | None = Field(
        default=None, alias="MODIFIED_LANE_AGILITY_TIME"
    )
    three_quarter_sprint: float | None = Field(
        default=None, alias="THREE_QUARTER_SPRINT"
    )
    bench_press: int | None = Field(default=None, alias="BENCH_PRESS")

    # Spot-up shooting (15 feet)
    spot_fifteen_corner_left: str | None = Field(
        default=None, alias="SPOT_FIFTEEN_CORNER_LEFT"
    )
    spot_fifteen_break_left: str | None = Field(
        default=None, alias="SPOT_FIFTEEN_BREAK_LEFT"
    )
    spot_fifteen_top_key: str | None = Field(default=None, alias="SPOT_FIFTEEN_TOP_KEY")
    spot_fifteen_break_right: str | None = Field(
        default=None, alias="SPOT_FIFTEEN_BREAK_RIGHT"
    )
    spot_fifteen_corner_right: str | None = Field(
        default=None, alias="SPOT_FIFTEEN_CORNER_RIGHT"
    )

    # Spot-up shooting (college 3pt)
    spot_college_corner_left: str | None = Field(
        default=None, alias="SPOT_COLLEGE_CORNER_LEFT"
    )
    spot_college_break_left: str | None = Field(
        default=None, alias="SPOT_COLLEGE_BREAK_LEFT"
    )
    spot_college_top_key: str | None = Field(default=None, alias="SPOT_COLLEGE_TOP_KEY")
    spot_college_break_right: str | None = Field(
        default=None, alias="SPOT_COLLEGE_BREAK_RIGHT"
    )
    spot_college_corner_right: str | None = Field(
        default=None, alias="SPOT_COLLEGE_CORNER_RIGHT"
    )

    # Spot-up shooting (NBA 3pt)
    spot_nba_corner_left: str | None = Field(default=None, alias="SPOT_NBA_CORNER_LEFT")
    spot_nba_break_left: str | None = Field(default=None, alias="SPOT_NBA_BREAK_LEFT")
    spot_nba_top_key: str | None = Field(default=None, alias="SPOT_NBA_TOP_KEY")
    spot_nba_break_right: str | None = Field(default=None, alias="SPOT_NBA_BREAK_RIGHT")
    spot_nba_corner_right: str | None = Field(
        default=None, alias="SPOT_NBA_CORNER_RIGHT"
    )

    # Off-dribble shooting (15 feet)
    off_drib_fifteen_break_left: str | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_LEFT"
    )
    off_drib_fifteen_top_key: str | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_TOP_KEY"
    )
    off_drib_fifteen_break_right: str | None = Field(
        default=None, alias="OFF_DRIB_FIFTEEN_BREAK_RIGHT"
    )

    # Off-dribble shooting (college 3pt)
    off_drib_college_break_left: str | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_LEFT"
    )
    off_drib_college_top_key: str | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_TOP_KEY"
    )
    off_drib_college_break_right: str | None = Field(
        default=None, alias="OFF_DRIB_COLLEGE_BREAK_RIGHT"
    )

    # On-the-move shooting
    on_move_fifteen: str | None = Field(default=None, alias="ON_MOVE_FIFTEEN")
    on_move_college: str | None = Field(default=None, alias="ON_MOVE_COLLEGE")


class DraftCombineStatsResponse(BaseModel):
    """Response from the draft combine stats endpoint."""

    players: list[CombinePlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
