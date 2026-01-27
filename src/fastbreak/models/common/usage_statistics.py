from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class UsageStatistics(PandasMixin, PolarsMixin, BaseModel):
    minutes: str
    usagePercentage: float
    percentageFieldGoalsMade: float
    percentageFieldGoalsAttempted: float
    percentageThreePointersMade: float
    percentageThreePointersAttempted: float
    percentageFreeThrowsMade: float
    percentageFreeThrowsAttempted: float
    percentageReboundsOffensive: float
    percentageReboundsDefensive: float
    percentageReboundsTotal: float
    percentageAssists: float
    percentageTurnovers: float
    percentageSteals: float
    percentageBlocks: float
    percentageBlocksAllowed: float
    percentagePersonalFouls: float
    percentagePersonalFoulsDrawn: float
    percentagePoints: float
