from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class MeetingTeam(PandasMixin, PolarsMixin, BaseModel):
    """Simplified team info for past meetings."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    score: int
    wins: int
    losses: int


class Meeting(PandasMixin, PolarsMixin, BaseModel):
    """A single past meeting between two teams."""

    recencyOrder: int
    gameId: str
    gameTimeUTC: str
    gameEt: str
    gameStatus: int
    gameStatusText: str
    gameClock: str
    broadcasterVideoLink: str
    awayTeam: MeetingTeam
    homeTeam: MeetingTeam


class LastFiveMeetings(PandasMixin, PolarsMixin, BaseModel):
    """Container for the last five meetings between teams."""

    meetings: list[Meeting]
