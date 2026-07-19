"""Models for the league dash player pt shot endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class PlayerPtShotStats(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking shot statistics.

    Player-level counterpart to ``TeamPtShotStats``: identical shot-frequency,
    makes, attempts, and percentage fields, keyed by player instead of team.
    """

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    player_last_team_id: int = Field(alias="PLAYER_LAST_TEAM_ID")
    player_last_team_abbreviation: str = Field(alias="PLAYER_LAST_TEAM_ABBREVIATION")
    age: float = Field(alias="AGE")
    gp: int = Field(alias="GP")
    g: int = Field(alias="G")
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


class LeagueDashPlayerPtShotResponse(FrozenResponse):
    """Response from the league dash player pt shot endpoint.

    Contains player-level tracking shot data (shot frequencies, makes,
    attempts, percentages for 2s and 3s). The offensive, player-level
    counterpart to ``LeagueDashTeamPtShot``.
    """

    players: list[PlayerPtShotStats] = Field(default_factory=list[PlayerPtShotStats])

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("players", "LeagueDashPTShots")
    )
