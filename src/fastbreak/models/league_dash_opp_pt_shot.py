"""Models for the league dash opponent pt shot endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class OppPtShotStats(PandasMixin, PolarsMixin, BaseModel):
    """Opponent tracking shot statistics (defensive quality)."""

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


class LeagueDashOppPtShotResponse(FrozenResponse):
    """Response from the league dash opponent pt shot endpoint.

    Contains opponent tracking shot data showing how well teams defend.
    Lower FG_PCT indicates better defense. This is the defensive
    counterpart to LeagueDashTeamPtShot.
    """

    teams: list[OppPtShotStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("teams", "LeagueDashPTShots")
    )
