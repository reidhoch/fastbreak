from typing import Self

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class TraditionalGroupStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Traditional statistics for a group (starters or bench)."""

    minutes: str
    fieldGoalsMade: int = Field(ge=0)
    fieldGoalsAttempted: int = Field(ge=0)
    # No le=1.0 ceiling: pre-1951 box scores tracked makes more reliably than
    # attempts, so the API-derived percentage can exceed 1.0 (e.g. game
    # 0024700084 reported a team freeThrowsPercentage of 1.133). See
    # check_rebounds_total for the surviving cross-field invariant.
    fieldGoalsPercentage: float = Field(ge=0.0)
    threePointersMade: int = Field(ge=0)
    threePointersAttempted: int = Field(ge=0)
    threePointersPercentage: float = Field(ge=0.0)
    freeThrowsMade: int = Field(ge=0)
    freeThrowsAttempted: int = Field(ge=0)
    freeThrowsPercentage: float = Field(ge=0.0)
    reboundsOffensive: int = Field(ge=0)
    reboundsDefensive: int = Field(ge=0)
    reboundsTotal: int = Field(ge=0)
    assists: int = Field(ge=0)
    steals: int = Field(ge=0)
    blocks: int = Field(ge=0)
    turnovers: int = Field(ge=0)
    foulsPersonal: int = Field(ge=0)
    points: int = Field(ge=0)

    # NOTE: made-vs-attempted is intentionally NOT validated. The NBA did not
    # record shots *attempted* until the 1951-52 season, so pre-1951 box scores
    # either leave attempts at 0 (a "not tracked" sentinel) or report makes that
    # exceed the (untrustworthy) attempt count -- e.g. game 0024700084 has
    # players at 4 FTM / 1 FTA. Both signal that the attempt count is unreliable
    # rather than a parsing bug, so we tolerate them like the other documented
    # NBA data-quality gaps (reboundChances, box-out partitions) instead of
    # discarding the entire game.

    @model_validator(mode="after")
    def check_rebounds_total(self) -> Self:
        """Validate that reboundsTotal equals offensive + defensive."""
        expected = self.reboundsOffensive + self.reboundsDefensive
        if self.reboundsTotal != expected:
            msg = f"reboundsTotal ({self.reboundsTotal}) != reboundsOffensive + reboundsDefensive ({expected})"
            raise ValueError(msg)
        return self


class TraditionalStatistics(TraditionalGroupStatistics):
    """Traditional box score statistics for a player or team."""

    plusMinusPoints: float
