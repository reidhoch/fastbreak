"""Models for the league dash player bio stats endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class PlayerBioStats(PandasMixin, PolarsMixin, BaseModel):
    """Player biographical and statistical data."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    age: float | None = Field(alias="AGE")
    player_height: str | None = Field(alias="PLAYER_HEIGHT", default=None)
    player_height_inches: int | None = Field(alias="PLAYER_HEIGHT_INCHES", default=None)
    player_weight: str | None = Field(alias="PLAYER_WEIGHT", default=None)
    college: str | None = Field(alias="COLLEGE")
    country: str | None = Field(alias="COUNTRY")
    draft_year: str | None = Field(alias="DRAFT_YEAR")
    draft_round: str | None = Field(alias="DRAFT_ROUND")
    draft_number: str | None = Field(alias="DRAFT_NUMBER")
    gp: int = Field(alias="GP")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    net_rating: float | None = Field(alias="NET_RATING")
    oreb_pct: float | None = Field(alias="OREB_PCT")
    dreb_pct: float | None = Field(alias="DREB_PCT")
    usg_pct: float | None = Field(alias="USG_PCT")
    ts_pct: float | None = Field(alias="TS_PCT")
    ast_pct: float | None = Field(alias="AST_PCT")


class LeagueDashPlayerBioStatsResponse(FrozenResponse):
    """Response from the league dash player bio stats endpoint.

    Contains player biographical information (height, weight, college,
    draft info) combined with basic statistics and advanced metrics.
    """

    players: list[PlayerBioStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("players", "LeagueDashPlayerBioStats")
    )
