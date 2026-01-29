from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class UsageStatistics(PandasMixin, PolarsMixin, BaseModel):
    minutes: str
    usagePercentage: float = Field(ge=0.0, le=1.0)
    percentageFieldGoalsMade: float = Field(ge=0.0, le=1.0)
    percentageFieldGoalsAttempted: float = Field(ge=0.0, le=1.0)
    percentageThreePointersMade: float = Field(ge=0.0, le=1.0)
    percentageThreePointersAttempted: float = Field(ge=0.0, le=1.0)
    percentageFreeThrowsMade: float = Field(ge=0.0, le=1.0)
    percentageFreeThrowsAttempted: float = Field(ge=0.0, le=1.0)
    percentageReboundsOffensive: float = Field(ge=0.0, le=1.0)
    percentageReboundsDefensive: float = Field(ge=0.0, le=1.0)
    percentageReboundsTotal: float = Field(ge=0.0, le=1.0)
    percentageAssists: float = Field(ge=0.0, le=1.0)
    percentageTurnovers: float = Field(ge=0.0, le=1.0)
    percentageSteals: float = Field(ge=0.0, le=1.0)
    percentageBlocks: float = Field(ge=0.0, le=1.0)
    percentageBlocksAllowed: float = Field(ge=0.0, le=1.0)
    percentagePersonalFouls: float = Field(ge=0.0, le=1.0)
    percentagePersonalFoulsDrawn: float = Field(ge=0.0, le=1.0)
    percentagePoints: float = Field(ge=0.0, le=1.0)
