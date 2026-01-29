from typing import Self

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class PlayerTrackStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking statistics for an individual player."""

    minutes: str
    speed: float = Field(ge=0.0)
    distance: float = Field(ge=0.0)
    reboundChancesOffensive: int = Field(ge=0)
    reboundChancesDefensive: int = Field(ge=0)
    reboundChancesTotal: int = Field(ge=0)
    touches: int = Field(ge=0)
    secondaryAssists: int = Field(ge=0)
    freeThrowAssists: int = Field(ge=0)
    passes: int = Field(ge=0)
    assists: int = Field(ge=0)
    contestedFieldGoalsMade: int = Field(ge=0)
    contestedFieldGoalsAttempted: int = Field(ge=0)
    contestedFieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    uncontestedFieldGoalsMade: int = Field(ge=0)
    uncontestedFieldGoalsAttempted: int = Field(ge=0)
    uncontestedFieldGoalsPercentage: float = Field(ge=0.0, le=1.0)
    fieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    defendedAtRimFieldGoalsMade: int = Field(ge=0)
    defendedAtRimFieldGoalsAttempted: int = Field(ge=0)
    defendedAtRimFieldGoalPercentage: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_made_not_exceeding_attempted(self) -> Self:
        """Validate that made shots do not exceed attempted shots."""
        if self.contestedFieldGoalsMade > self.contestedFieldGoalsAttempted:
            msg = f"contestedFieldGoalsMade ({self.contestedFieldGoalsMade}) > contestedFieldGoalsAttempted ({self.contestedFieldGoalsAttempted})"
            raise ValueError(msg)
        if self.uncontestedFieldGoalsMade > self.uncontestedFieldGoalsAttempted:
            msg = f"uncontestedFieldGoalsMade ({self.uncontestedFieldGoalsMade}) > uncontestedFieldGoalsAttempted ({self.uncontestedFieldGoalsAttempted})"
            raise ValueError(msg)
        if self.defendedAtRimFieldGoalsMade > self.defendedAtRimFieldGoalsAttempted:
            msg = f"defendedAtRimFieldGoalsMade ({self.defendedAtRimFieldGoalsMade}) > defendedAtRimFieldGoalsAttempted ({self.defendedAtRimFieldGoalsAttempted})"
            raise ValueError(msg)
        return self


class TeamPlayerTrackStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking statistics aggregated at team level."""

    minutes: str
    distance: float = Field(ge=0.0)
    reboundChancesOffensive: int = Field(ge=0)
    reboundChancesDefensive: int = Field(ge=0)
    reboundChancesTotal: int = Field(ge=0)
    touches: int = Field(ge=0)
    secondaryAssists: int = Field(ge=0)
    freeThrowAssists: int = Field(ge=0)
    passes: int = Field(ge=0)
    assists: int = Field(ge=0)
    contestedFieldGoalsMade: int = Field(ge=0)
    contestedFieldGoalsAttempted: int = Field(ge=0)
    contestedFieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    uncontestedFieldGoalsMade: int = Field(ge=0)
    uncontestedFieldGoalsAttempted: int = Field(ge=0)
    uncontestedFieldGoalsPercentage: float = Field(ge=0.0, le=1.0)
    fieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    defendedAtRimFieldGoalsMade: int = Field(ge=0)
    defendedAtRimFieldGoalsAttempted: int = Field(ge=0)
    defendedAtRimFieldGoalPercentage: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_made_not_exceeding_attempted(self) -> Self:
        """Validate that made shots do not exceed attempted shots."""
        if self.contestedFieldGoalsMade > self.contestedFieldGoalsAttempted:
            msg = f"contestedFieldGoalsMade ({self.contestedFieldGoalsMade}) > contestedFieldGoalsAttempted ({self.contestedFieldGoalsAttempted})"
            raise ValueError(msg)
        if self.uncontestedFieldGoalsMade > self.uncontestedFieldGoalsAttempted:
            msg = f"uncontestedFieldGoalsMade ({self.uncontestedFieldGoalsMade}) > uncontestedFieldGoalsAttempted ({self.uncontestedFieldGoalsAttempted})"
            raise ValueError(msg)
        if self.defendedAtRimFieldGoalsMade > self.defendedAtRimFieldGoalsAttempted:
            msg = f"defendedAtRimFieldGoalsMade ({self.defendedAtRimFieldGoalsMade}) > defendedAtRimFieldGoalsAttempted ({self.defendedAtRimFieldGoalsAttempted})"
            raise ValueError(msg)
        return self
