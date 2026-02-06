"""Models for the shot chart leaguewide endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class LeagueWideShotZone(PandasMixin, PolarsMixin, BaseModel):
    """A league-wide shot zone statistics entry."""

    grid_type: str = Field(alias="GRID_TYPE")
    shot_zone_basic: str = Field(alias="SHOT_ZONE_BASIC")
    shot_zone_area: str = Field(alias="SHOT_ZONE_AREA")
    shot_zone_range: str = Field(alias="SHOT_ZONE_RANGE")
    fga: int = Field(alias="FGA")
    fgm: int = Field(alias="FGM")
    fg_pct: float = Field(alias="FG_PCT")


class ShotChartLeaguewideResponse(FrozenResponse):
    """Response from the shot chart leaguewide endpoint.

    Contains league-wide shot zone statistics with field goal attempts,
    makes, and percentages for each zone.
    """

    league_wide: list[LeagueWideShotZone] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"league_wide": rows}
