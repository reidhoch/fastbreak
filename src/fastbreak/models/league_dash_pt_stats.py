"""Models for the League Dashboard Player Tracking Stats endpoint response.

This endpoint returns different statistics based on the PtMeasureType parameter.
The model uses flexible fields that accommodate various measure types.
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class TeamPtStats(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking statistics for a team.

    Fields vary based on PtMeasureType. Common fields are always present,
    while tracking-specific fields may be None if not applicable.
    """

    # Team identification
    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")

    # Basic stats
    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    min: float = Field(alias="MIN")

    # Drive stats (PtMeasureType="Drives")
    drives: float | None = Field(default=None, alias="DRIVES")
    drive_fgm: float | None = Field(default=None, alias="DRIVE_FGM")
    drive_fga: float | None = Field(default=None, alias="DRIVE_FGA")
    drive_fg_pct: float | None = Field(default=None, alias="DRIVE_FG_PCT")
    drive_ftm: float | None = Field(default=None, alias="DRIVE_FTM")
    drive_fta: float | None = Field(default=None, alias="DRIVE_FTA")
    drive_ft_pct: float | None = Field(default=None, alias="DRIVE_FT_PCT")
    drive_pts: float | None = Field(default=None, alias="DRIVE_PTS")
    drive_pts_pct: float | None = Field(default=None, alias="DRIVE_PTS_PCT")
    drive_passes: float | None = Field(default=None, alias="DRIVE_PASSES")
    drive_passes_pct: float | None = Field(default=None, alias="DRIVE_PASSES_PCT")
    drive_ast: float | None = Field(default=None, alias="DRIVE_AST")
    drive_ast_pct: float | None = Field(default=None, alias="DRIVE_AST_PCT")
    drive_tov: float | None = Field(default=None, alias="DRIVE_TOV")
    drive_tov_pct: float | None = Field(default=None, alias="DRIVE_TOV_PCT")
    drive_pf: float | None = Field(default=None, alias="DRIVE_PF")
    drive_pf_pct: float | None = Field(default=None, alias="DRIVE_PF_PCT")


class PlayerPtStats(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking statistics for an individual player.

    Fields vary based on PtMeasureType. Common fields are always present,
    while tracking-specific fields may be None if not applicable.
    """

    # Player identification
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")

    # Basic stats
    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    min: float = Field(alias="MIN")

    # Drive stats (PtMeasureType="Drives")
    drives: float | None = Field(default=None, alias="DRIVES")
    drive_fgm: float | None = Field(default=None, alias="DRIVE_FGM")
    drive_fga: float | None = Field(default=None, alias="DRIVE_FGA")
    drive_fg_pct: float | None = Field(default=None, alias="DRIVE_FG_PCT")
    drive_ftm: float | None = Field(default=None, alias="DRIVE_FTM")
    drive_fta: float | None = Field(default=None, alias="DRIVE_FTA")
    drive_ft_pct: float | None = Field(default=None, alias="DRIVE_FT_PCT")
    drive_pts: float | None = Field(default=None, alias="DRIVE_PTS")
    drive_pts_pct: float | None = Field(default=None, alias="DRIVE_PTS_PCT")
    drive_passes: float | None = Field(default=None, alias="DRIVE_PASSES")
    drive_passes_pct: float | None = Field(default=None, alias="DRIVE_PASSES_PCT")
    drive_ast: float | None = Field(default=None, alias="DRIVE_AST")
    drive_ast_pct: float | None = Field(default=None, alias="DRIVE_AST_PCT")
    drive_tov: float | None = Field(default=None, alias="DRIVE_TOV")
    drive_tov_pct: float | None = Field(default=None, alias="DRIVE_TOV_PCT")
    drive_pf: float | None = Field(default=None, alias="DRIVE_PF")
    drive_pf_pct: float | None = Field(default=None, alias="DRIVE_PF_PCT")


class LeagueDashPtStatsResponse(FrozenResponse):
    """Response from the league dashboard player tracking stats endpoint.

    Contains player tracking statistics for teams or players based on the
    PlayerOrTeam parameter. Only one of teams or players will be populated.
    """

    teams: list[TeamPtStats] = Field(default_factory=list)
    players: list[PlayerPtStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set_by_name(data, "LeagueDashPtStats")

        # Determine if this is team or player data by checking for PLAYER_ID
        if rows and "PLAYER_ID" in rows[0]:
            return {"teams": [], "players": rows}
        return {"teams": rows, "players": []}
