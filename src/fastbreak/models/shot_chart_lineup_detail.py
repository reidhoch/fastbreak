"""Models for the shot chart lineup detail endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class LineupShot(BaseModel):
    """An individual shot with lineup context."""

    grid_type: str = Field(alias="GRID_TYPE")
    game_id: str = Field(alias="GAME_ID")
    game_event_id: int = Field(alias="GAME_EVENT_ID")
    group_id: str | None = Field(alias="GROUP_ID")
    group_name: str | None = Field(alias="GROUP_NAME")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    period: int = Field(alias="PERIOD")
    minutes_remaining: int = Field(alias="MINUTES_REMAINING")
    seconds_remaining: int = Field(alias="SECONDS_REMAINING")
    event_type: str = Field(alias="EVENT_TYPE")
    action_type: str = Field(alias="ACTION_TYPE")
    shot_type: str = Field(alias="SHOT_TYPE")
    shot_zone_basic: str = Field(alias="SHOT_ZONE_BASIC")
    shot_zone_area: str = Field(alias="SHOT_ZONE_AREA")
    shot_zone_range: str = Field(alias="SHOT_ZONE_RANGE")
    shot_distance: int = Field(alias="SHOT_DISTANCE")
    loc_x: int = Field(alias="LOC_X")
    loc_y: int = Field(alias="LOC_Y")
    shot_attempted_flag: int = Field(alias="SHOT_ATTEMPTED_FLAG")
    shot_made_flag: int = Field(alias="SHOT_MADE_FLAG")
    game_date: str = Field(alias="GAME_DATE")
    htm: str = Field(alias="HTM")
    vtm: str = Field(alias="VTM")


class LineupLeagueAverage(BaseModel):
    """League average shooting percentages by zone."""

    grid_type: str = Field(alias="GRID_TYPE")
    shot_zone_basic: str = Field(alias="SHOT_ZONE_BASIC")
    shot_zone_area: str = Field(alias="SHOT_ZONE_AREA")
    shot_zone_range: str = Field(alias="SHOT_ZONE_RANGE")
    fga: int = Field(alias="FGA")
    fgm: int = Field(alias="FGM")
    fg_pct: float = Field(alias="FG_PCT")


class ShotChartLineupDetailResponse(BaseModel):
    """Response from the shot chart lineup detail endpoint.

    Contains individual shot data with lineup context and league averages.
    """

    shots: list[LineupShot] = Field(default_factory=list)
    league_averages: list[LineupLeagueAverage] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        shots = parse_result_set_by_name(data, "ShotChartLineupDetail")
        league_averages = parse_result_set_by_name(
            data,
            "ShotChartLineupLeagueAverage",
        )

        return {
            "shots": shots,
            "league_averages": league_averages,
        }
