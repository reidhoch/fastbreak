from typing import Self

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class TraditionalGroupStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Traditional statistics for a group (starters or bench)."""

    minutes: str
    fieldGoalsMade: int = Field(ge=0)
    fieldGoalsAttempted: int = Field(ge=0)
    fieldGoalsPercentage: float = Field(ge=0.0, le=1.0)
    threePointersMade: int = Field(ge=0)
    threePointersAttempted: int = Field(ge=0)
    threePointersPercentage: float = Field(ge=0.0, le=1.0)
    freeThrowsMade: int = Field(ge=0)
    freeThrowsAttempted: int = Field(ge=0)
    freeThrowsPercentage: float = Field(ge=0.0, le=1.0)
    reboundsOffensive: int = Field(ge=0)
    reboundsDefensive: int = Field(ge=0)
    reboundsTotal: int = Field(ge=0)
    assists: int = Field(ge=0)
    steals: int = Field(ge=0)
    blocks: int = Field(ge=0)
    turnovers: int = Field(ge=0)
    foulsPersonal: int = Field(ge=0)
    points: int = Field(ge=0)

    @model_validator(mode="after")
    def check_made_not_exceeding_attempted(self) -> Self:
        """Validate that made shots do not exceed attempted shots.

        Each check is skipped when ``attempted == 0``: the NBA did not record
        shots *attempted* until the 1951-52 season, so pre-1951 box scores
        report makes while leaving attempts at 0 as a "not tracked" sentinel.
        A correctly tracked game can never have makes without attempts, so
        guarding on ``attempted > 0`` tolerates the historical sentinel without
        masking genuine made-exceeds-attempted corruption.
        """
        if (
            self.fieldGoalsAttempted > 0
            and self.fieldGoalsMade > self.fieldGoalsAttempted
        ):
            msg = f"fieldGoalsMade ({self.fieldGoalsMade}) > fieldGoalsAttempted ({self.fieldGoalsAttempted})"
            raise ValueError(msg)
        if (
            self.threePointersAttempted > 0
            and self.threePointersMade > self.threePointersAttempted
        ):
            msg = f"threePointersMade ({self.threePointersMade}) > threePointersAttempted ({self.threePointersAttempted})"
            raise ValueError(msg)
        if (
            self.freeThrowsAttempted > 0
            and self.freeThrowsMade > self.freeThrowsAttempted
        ):
            msg = f"freeThrowsMade ({self.freeThrowsMade}) > freeThrowsAttempted ({self.freeThrowsAttempted})"
            raise ValueError(msg)
        return self

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
