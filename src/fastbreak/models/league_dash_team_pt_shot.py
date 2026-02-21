"""Models for the league dash team pt shot endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class TeamPtShotStats(PandasMixin, PolarsMixin, BaseModel):
    """Team tracking shot statistics."""

    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    gp: int = Field(alias="GP")
    g: int = Field(alias="G")
    fga_frequency: float = Field(alias="FGA_FREQUENCY")
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    efg_pct: float = Field(alias="EFG_PCT")
    fg2a_frequency: float = Field(alias="FG2A_FREQUENCY")
    fg2m: int = Field(alias="FG2M")
    fg2a: int = Field(alias="FG2A")
    fg2_pct: float = Field(alias="FG2_PCT")
    fg3a_frequency: float = Field(alias="FG3A_FREQUENCY")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")


class LeagueDashTeamPtShotResponse(FrozenResponse):
    """Response from the league dash team pt shot endpoint.

    Contains team-level tracking shot data including shot frequencies,
    makes, attempts, and percentages for 2-point and 3-point shots.
    """

    teams: list[TeamPtShotStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("teams", "LeagueDashPTShots")
    )
