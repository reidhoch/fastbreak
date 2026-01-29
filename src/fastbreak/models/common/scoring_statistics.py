from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class ScoringStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Scoring distribution statistics for a player or team."""

    minutes: str
    percentageFieldGoalsAttempted2pt: float = Field(ge=0.0, le=1.0)
    percentageFieldGoalsAttempted3pt: float = Field(ge=0.0, le=1.0)
    percentagePoints2pt: float = Field(ge=0.0, le=1.0)
    percentagePointsMidrange2pt: float = Field(ge=0.0, le=1.0)
    percentagePoints3pt: float = Field(ge=0.0, le=1.0)
    percentagePointsFastBreak: float = Field(ge=0.0, le=1.0)
    percentagePointsFreeThrow: float = Field(ge=0.0, le=1.0)
    percentagePointsOffTurnovers: float = Field(ge=0.0, le=1.0)
    percentagePointsPaint: float = Field(ge=0.0, le=1.0)
    percentageAssisted2pt: float = Field(ge=0.0, le=1.0)
    percentageUnassisted2pt: float = Field(ge=0.0, le=1.0)
    percentageAssisted3pt: float = Field(ge=0.0, le=1.0)
    percentageUnassisted3pt: float = Field(ge=0.0, le=1.0)
    percentageAssistedFGM: float = Field(ge=0.0, le=1.0)
    percentageUnassistedFGM: float = Field(ge=0.0, le=1.0)
