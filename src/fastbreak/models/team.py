from pydantic import BaseModel

from fastbreak.models.player import Player
from fastbreak.models.usage_statistics import UsageStatistics


class Team(BaseModel):
    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[Player]
    statistics: UsageStatistics
