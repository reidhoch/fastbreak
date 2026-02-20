"""Models for the Player Dashboard Shot Defense endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class DefendingShots(PandasMixin, PolarsMixin, BaseModel):
    """Defensive statistics for shots contested by a player.

    Contains field goal defense data by category (overall, 2PT, 3PT, etc.)
    comparing opponent shooting percentage vs their normal percentage.
    """

    matchup_id: int = Field(alias="MATCHUPID")
    gp: int = Field(alias="GP")
    games: int = Field(alias="G")
    defense_category: str = Field(alias="DEFENSE_CATEGORY")
    freq: float | None = Field(alias="FREQ")
    d_fgm: float | None = Field(alias="D_FGM")
    d_fga: float | None = Field(alias="D_FGA")
    d_fg_pct: float | None = Field(alias="D_FG_PCT")
    normal_fg_pct: float | None = Field(alias="NORMAL_FG_PCT")
    pct_plusminus: float | None = Field(alias="PCT_PLUSMINUS")


class PlayerDashPtShotDefendResponse(FrozenResponse):
    """Response from the player dashboard shot defense endpoint.

    Contains defensive statistics showing how opponents shoot when
    defended by this player compared to their normal percentages.
    """

    defending_shots: list[DefendingShots] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"defending_shots": "DefendingShots"})
    )
