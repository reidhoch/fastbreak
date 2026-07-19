"""Models for the league dash pt defend endpoint (player defensive tracking)."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class PlayerDefendStats(PandasMixin, PolarsMixin, BaseModel):
    """Player defensive tracking statistics.

    Player-level counterpart to ``TeamDefendStats``: how well a defender holds
    opponents below their normal FG% on shots they contest. Negative
    ``pct_plusminus`` indicates good defense (opponents shoot worse than usual).
    """

    close_def_person_id: int = Field(alias="CLOSE_DEF_PERSON_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    player_last_team_id: int = Field(alias="PLAYER_LAST_TEAM_ID")
    player_last_team_abbreviation: str = Field(alias="PLAYER_LAST_TEAM_ABBREVIATION")
    player_position: str | None = Field(default=None, alias="PLAYER_POSITION")
    age: float = Field(alias="AGE")
    gp: int = Field(alias="GP")
    g: int = Field(alias="G")
    freq: float = Field(alias="FREQ")
    d_fgm: float = Field(alias="D_FGM")
    d_fga: float = Field(alias="D_FGA")
    d_fg_pct: float | None = Field(alias="D_FG_PCT")
    normal_fg_pct: float | None = Field(alias="NORMAL_FG_PCT")
    pct_plusminus: float | None = Field(alias="PCT_PLUSMINUS")


class LeagueDashPtDefendResponse(FrozenResponse):
    """Response from the league dash pt defend endpoint.

    Contains player defensive tracking stats showing how well each defender
    holds opponents below their normal FG% by shot category. The player-level
    counterpart to ``LeagueDashPtTeamDefend``.
    """

    players: list[PlayerDefendStats] = Field(default_factory=list[PlayerDefendStats])

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("players", "LeagueDashPTDefend")
    )
