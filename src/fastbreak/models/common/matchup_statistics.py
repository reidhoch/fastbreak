from typing import Self

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class MatchupStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Statistics for a specific player-vs-player defensive matchup."""

    matchupMinutes: str
    matchupMinutesSort: float = Field(ge=0.0)
    partialPossessions: float = Field(ge=0.0)
    percentageDefenderTotalTime: float = Field(ge=0.0, le=1.0)
    percentageOffensiveTotalTime: float = Field(ge=0.0, le=1.0)
    percentageTotalTimeBothOn: float = Field(ge=0.0, le=1.0)
    switchesOn: int = Field(ge=0)
    playerPoints: int = Field(ge=0)
    teamPoints: int = Field(ge=0)
    matchupAssists: int = Field(ge=0)
    matchupPotentialAssists: int = Field(ge=0)
    matchupTurnovers: int = Field(ge=0)
    matchupBlocks: int = Field(ge=0)
    matchupFieldGoalsMade: int = Field(ge=0)
    matchupFieldGoalsAttempted: int = Field(ge=0)
    matchupFieldGoalsPercentage: float = Field(ge=0.0, le=1.0)
    matchupThreePointersMade: int = Field(ge=0)
    matchupThreePointersAttempted: int = Field(ge=0)
    matchupThreePointersPercentage: float = Field(ge=0.0, le=1.0)
    helpBlocks: int = Field(ge=0)
    helpFieldGoalsMade: int = Field(ge=0)
    helpFieldGoalsAttempted: int = Field(ge=0)
    helpFieldGoalsPercentage: float = Field(ge=0.0, le=1.0)
    matchupFreeThrowsMade: int = Field(ge=0)
    matchupFreeThrowsAttempted: int = Field(ge=0)
    shootingFouls: int = Field(ge=0)

    @model_validator(mode="after")
    def check_made_not_exceeding_attempted(self) -> Self:
        """Validate that made shots do not exceed attempted shots."""
        if self.matchupFieldGoalsMade > self.matchupFieldGoalsAttempted:
            msg = f"matchupFieldGoalsMade ({self.matchupFieldGoalsMade}) > matchupFieldGoalsAttempted ({self.matchupFieldGoalsAttempted})"
            raise ValueError(msg)
        if self.matchupThreePointersMade > self.matchupThreePointersAttempted:
            msg = f"matchupThreePointersMade ({self.matchupThreePointersMade}) > matchupThreePointersAttempted ({self.matchupThreePointersAttempted})"
            raise ValueError(msg)
        if self.helpFieldGoalsMade > self.helpFieldGoalsAttempted:
            msg = f"helpFieldGoalsMade ({self.helpFieldGoalsMade}) > helpFieldGoalsAttempted ({self.helpFieldGoalsAttempted})"
            raise ValueError(msg)
        if self.matchupFreeThrowsMade > self.matchupFreeThrowsAttempted:
            msg = f"matchupFreeThrowsMade ({self.matchupFreeThrowsMade}) > matchupFreeThrowsAttempted ({self.matchupFreeThrowsAttempted})"
            raise ValueError(msg)
        return self
