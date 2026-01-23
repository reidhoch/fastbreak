"""Models for the Player Dashboard Shot Defense endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set_by_name


class DefendingShots(BaseModel):
    """Defensive statistics for shots contested by a player.

    Contains field goal defense data by category (overall, 2PT, 3PT, etc.)
    comparing opponent shooting percentage vs their normal percentage.
    """

    matchup_id: int = Field(alias="MATCHUPID")
    gp: int = Field(alias="GP")
    games: int = Field(alias="G")
    defense_category: str = Field(alias="DEFENSE_CATEGORY")
    freq: float = Field(alias="FREQ")
    d_fgm: float = Field(alias="D_FGM")
    d_fga: float = Field(alias="D_FGA")
    d_fg_pct: float | None = Field(alias="D_FG_PCT")
    normal_fg_pct: float | None = Field(alias="NORMAL_FG_PCT")
    pct_plusminus: float | None = Field(alias="PCT_PLUSMINUS")


class PlayerDashPtShotDefendResponse(BaseModel):
    """Response from the player dashboard shot defense endpoint.

    Contains defensive statistics showing how opponents shoot when
    defended by this player compared to their normal percentages.
    """

    defending_shots: list[DefendingShots] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "defending_shots": parse_result_set_by_name(
                data,
                "DefendingShots",
            ),
        }
