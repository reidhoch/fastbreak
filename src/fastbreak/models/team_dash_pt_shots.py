"""Models for the Team Dashboard PT Shots endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class _TeamBaseShotStats(PandasMixin, PolarsMixin, BaseModel):
    """Base shooting statistics shared across all shot breakdown types."""

    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    sort_order: int | None = Field(alias="SORT_ORDER")
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


class TeamShotTypeStats(_TeamBaseShotStats):
    """Shot stats broken down by shot type/distance range."""

    shot_type: str = Field(alias="SHOT_TYPE")


class TeamShotClockStats(_TeamBaseShotStats):
    """Shot stats broken down by shot clock range."""

    shot_clock_range: str = Field(alias="SHOT_CLOCK_RANGE")


class TeamDribbleStats(_TeamBaseShotStats):
    """Shot stats broken down by number of dribbles before shot."""

    dribble_range: str = Field(alias="DRIBBLE_RANGE")


class TeamClosestDefenderStats(_TeamBaseShotStats):
    """Shot stats broken down by closest defender distance."""

    close_def_dist_range: str | None = Field(alias="CLOSE_DEF_DIST_RANGE")


class TeamTouchTimeStats(_TeamBaseShotStats):
    """Shot stats broken down by touch time before shot."""

    touch_time_range: str = Field(alias="TOUCH_TIME_RANGE")


class TeamDashPtShotsResponse(FrozenResponse):
    """Response from the team dashboard PT shots endpoint.

    Contains shooting statistics broken down by various factors like
    shot type, shot clock, dribbles, defender distance, and touch time.
    """

    general_shooting: list[TeamShotTypeStats] = Field(default_factory=list)
    shot_clock_shooting: list[TeamShotClockStats] = Field(default_factory=list)
    dribble_shooting: list[TeamDribbleStats] = Field(default_factory=list)
    closest_defender_shooting: list[TeamClosestDefenderStats] = Field(
        default_factory=list
    )
    closest_defender_10ft_plus_shooting: list[TeamClosestDefenderStats] = Field(
        default_factory=list
    )
    touch_time_shooting: list[TeamTouchTimeStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "general_shooting": "GeneralShooting",
                "shot_clock_shooting": "ShotClockShooting",
                "dribble_shooting": "DribbleShooting",
                "closest_defender_shooting": "ClosestDefenderShooting",
                "closest_defender_10ft_plus_shooting": "ClosestDefender10ftPlusShooting",
                "touch_time_shooting": "TouchTimeShooting",
            }
        )
    )
