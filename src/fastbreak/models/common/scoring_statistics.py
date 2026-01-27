from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class ScoringStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Scoring distribution statistics for a player or team."""

    minutes: str
    percentageFieldGoalsAttempted2pt: float
    percentageFieldGoalsAttempted3pt: float
    percentagePoints2pt: float
    percentagePointsMidrange2pt: float
    percentagePoints3pt: float
    percentagePointsFastBreak: float
    percentagePointsFreeThrow: float
    percentagePointsOffTurnovers: float
    percentagePointsPaint: float
    percentageAssisted2pt: float
    percentageUnassisted2pt: float
    percentageAssisted3pt: float
    percentageUnassisted3pt: float
    percentageAssistedFGM: float
    percentageUnassistedFGM: float
