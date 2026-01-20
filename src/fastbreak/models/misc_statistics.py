from pydantic import BaseModel


class MiscStatistics(BaseModel):
    """Miscellaneous statistics for a player or team in a game."""

    minutes: str
    pointsOffTurnovers: int
    pointsSecondChance: int
    pointsFastBreak: int
    pointsPaint: int
    oppPointsOffTurnovers: int
    oppPointsSecondChance: int
    oppPointsFastBreak: int
    oppPointsPaint: int
    blocks: int
    blocksAgainst: int
    foulsPersonal: int
    foulsDrawn: int
