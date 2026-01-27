"""Models for the Player Dashboard PT Shots endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class _BaseShotStats(PandasMixin, PolarsMixin, BaseModel):
    """Base shooting statistics shared across all shot breakdown types."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    sort_order: int = Field(alias="SORT_ORDER")
    gp: int = Field(alias="GP")
    games: int = Field(alias="G")
    fga_frequency: float = Field(alias="FGA_FREQUENCY")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    efg_pct: float | None = Field(alias="EFG_PCT")
    fg2a_frequency: float = Field(alias="FG2A_FREQUENCY")
    fg2m: float = Field(alias="FG2M")
    fg2a: float = Field(alias="FG2A")
    fg2_pct: float | None = Field(alias="FG2_PCT")
    fg3a_frequency: float = Field(alias="FG3A_FREQUENCY")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")


class ShotTypeStats(_BaseShotStats):
    """Shot stats broken down by shot type (Overall, Pullup, Catch and Shoot, etc.)."""

    shot_type: str = Field(alias="SHOT_TYPE")


class ShotClockStats(_BaseShotStats):
    """Shot stats broken down by shot clock range."""

    shot_clock_range: str = Field(alias="SHOT_CLOCK_RANGE")


class DribbleStats(_BaseShotStats):
    """Shot stats broken down by number of dribbles before shot."""

    dribble_range: str = Field(alias="DRIBBLE_RANGE")


class ClosestDefenderStats(_BaseShotStats):
    """Shot stats broken down by closest defender distance."""

    close_def_dist_range: str = Field(alias="CLOSE_DEF_DIST_RANGE")


class TouchTimeStats(_BaseShotStats):
    """Shot stats broken down by touch time before shot."""

    touch_time_range: str = Field(alias="TOUCH_TIME_RANGE")


class PlayerDashPtShotsResponse(BaseModel):
    """Response from the player dashboard PT shots endpoint.

    Contains shooting statistics broken down by various factors like
    shot type, shot clock, dribbles, defender distance, and touch time.
    """

    overall: list[ShotTypeStats] = Field(default_factory=list)
    general_shooting: list[ShotTypeStats] = Field(default_factory=list)
    shot_clock_shooting: list[ShotClockStats] = Field(default_factory=list)
    dribble_shooting: list[DribbleStats] = Field(default_factory=list)
    closest_defender_shooting: list[ClosestDefenderStats] = Field(default_factory=list)
    closest_defender_10ft_plus_shooting: list[ClosestDefenderStats] = Field(
        default_factory=list
    )
    touch_time_shooting: list[TouchTimeStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "overall": parse_result_set_by_name(data, "Overall"),
            "general_shooting": parse_result_set_by_name(
                data,
                "GeneralShooting",
            ),
            "shot_clock_shooting": parse_result_set_by_name(
                data,
                "ShotClockShooting",
            ),
            "dribble_shooting": parse_result_set_by_name(
                data,
                "DribbleShooting",
            ),
            "closest_defender_shooting": parse_result_set_by_name(
                data,
                "ClosestDefenderShooting",
            ),
            "closest_defender_10ft_plus_shooting": parse_result_set_by_name(
                data,
                "ClosestDefender10ftPlusShooting",
            ),
            "touch_time_shooting": parse_result_set_by_name(
                data,
                "TouchTimeShooting",
            ),
        }
