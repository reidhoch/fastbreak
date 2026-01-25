"""Models for the draft combine player anthro endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class AnthroPlayer(BaseModel):
    """A player's draft combine anthropometric measurements."""

    # Basic info
    temp_player_id: int = Field(alias="TEMP_PLAYER_ID")
    player_id: int = Field(alias="PLAYER_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    player_name: str = Field(alias="PLAYER_NAME")
    position: str = Field(alias="POSITION")

    # Height measurements (inches and formatted)
    height_wo_shoes: float | None = Field(default=None, alias="HEIGHT_WO_SHOES")
    height_wo_shoes_ft_in: str | None = Field(
        default=None, alias="HEIGHT_WO_SHOES_FT_IN"
    )
    height_w_shoes: float | None = Field(default=None, alias="HEIGHT_W_SHOES")
    height_w_shoes_ft_in: str | None = Field(default=None, alias="HEIGHT_W_SHOES_FT_IN")

    # Weight and body composition
    weight: float | None = Field(default=None, alias="WEIGHT")
    body_fat_pct: float | None = Field(default=None, alias="BODY_FAT_PCT")

    # Wingspan and reach measurements in inches and formatted strings
    wingspan: float | None = Field(default=None, alias="WINGSPAN")
    wingspan_ft_in: str | None = Field(default=None, alias="WINGSPAN_FT_IN")
    standing_reach: float | None = Field(default=None, alias="STANDING_REACH")
    standing_reach_ft_in: str | None = Field(default=None, alias="STANDING_REACH_FT_IN")

    # Hand measurements (inches)
    hand_length: float | None = Field(default=None, alias="HAND_LENGTH")
    hand_width: float | None = Field(default=None, alias="HAND_WIDTH")


class DraftCombinePlayerAnthroResponse(BaseModel):
    """Response from the draft combine player anthro endpoint."""

    players: list[AnthroPlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"players": rows}
