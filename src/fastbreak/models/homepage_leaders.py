"""Models for the homepage leaders endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class HomepageLeader(PandasMixin, PolarsMixin, BaseModel):
    """A player entry in homepage leaders for a specific stat category."""

    rank: int = Field(alias="RANK")
    player_id: int = Field(alias="PLAYERID")
    player: str = Field(alias="PLAYER")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    pts: float = Field(alias="PTS")
    fg_pct: float = Field(alias="FG_PCT")
    fg3_pct: float = Field(alias="FG3_PCT")
    ft_pct: float = Field(alias="FT_PCT")
    efg_pct: float = Field(alias="EFG_PCT")
    ts_pct: float = Field(alias="TS_PCT")
    pts_per_48: float = Field(alias="PTS_PER48")


class HomepageLeadersResponse(FrozenResponse):
    """Response from the homepage leaders endpoint.

    Contains detailed statistical leaders for a specific category with
    additional efficiency metrics like EFG%, TS%, and per-48 stats.
    """

    leaders: list[HomepageLeader] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("leaders", "HomePageLeaders")
    )
