"""Models for the league hustle stats team endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class LeagueHustleTeam(PandasMixin, PolarsMixin, BaseModel):
    """Season-aggregated hustle statistics for a team."""

    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    min: float = Field(alias="MIN")
    contested_shots: float = Field(alias="CONTESTED_SHOTS")
    contested_shots_2pt: float = Field(alias="CONTESTED_SHOTS_2PT")
    contested_shots_3pt: float = Field(alias="CONTESTED_SHOTS_3PT")
    deflections: float = Field(alias="DEFLECTIONS")
    charges_drawn: float = Field(alias="CHARGES_DRAWN")
    screen_assists: float = Field(alias="SCREEN_ASSISTS")
    screen_ast_pts: float = Field(alias="SCREEN_AST_PTS")
    off_loose_balls_recovered: float = Field(alias="OFF_LOOSE_BALLS_RECOVERED")
    def_loose_balls_recovered: float = Field(alias="DEF_LOOSE_BALLS_RECOVERED")
    loose_balls_recovered: float = Field(alias="LOOSE_BALLS_RECOVERED")
    pct_loose_balls_recovered_off: float | None = Field(
        alias="PCT_LOOSE_BALLS_RECOVERED_OFF"
    )
    pct_loose_balls_recovered_def: float | None = Field(
        alias="PCT_LOOSE_BALLS_RECOVERED_DEF"
    )
    off_boxouts: float = Field(alias="OFF_BOXOUTS")
    def_boxouts: float = Field(alias="DEF_BOXOUTS")
    box_outs: float = Field(alias="BOX_OUTS")
    pct_box_outs_off: float | None = Field(alias="PCT_BOX_OUTS_OFF")
    pct_box_outs_def: float | None = Field(alias="PCT_BOX_OUTS_DEF")


class LeagueHustleStatsTeamResponse(FrozenResponse):
    """Response from the league hustle stats team endpoint.

    Contains season-aggregated hustle statistics for all teams.
    """

    teams: list[LeagueHustleTeam] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "teams": parse_result_set_by_name(
                data,
                "HustleStatsTeam",
            ),
        }
