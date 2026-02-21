"""Models for the league dash pt team defend endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class TeamDefendStats(PandasMixin, PolarsMixin, BaseModel):
    """Team defensive tracking statistics."""

    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    gp: int = Field(alias="GP")
    g: int = Field(alias="G")
    freq: float = Field(alias="FREQ")
    d_fgm: int = Field(alias="D_FGM")
    d_fga: int = Field(alias="D_FGA")
    d_fg_pct: float = Field(alias="D_FG_PCT")
    normal_fg_pct: float = Field(alias="NORMAL_FG_PCT")
    pct_plusminus: float = Field(alias="PCT_PLUSMINUS")


class LeagueDashPtTeamDefendResponse(FrozenResponse):
    """Response from the league dash pt team defend endpoint.

    Contains team defensive tracking stats showing how well teams
    defend shots compared to league average. Negative PCT_PLUSMINUS
    indicates better defense (opponents shoot worse than normal).
    """

    teams: list[TeamDefendStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("teams", "LeagueDashPtTeamDefend")
    )
