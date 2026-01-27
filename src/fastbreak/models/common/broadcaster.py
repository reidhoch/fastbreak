from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Broadcaster(PandasMixin, PolarsMixin, BaseModel):
    broadcasterId: int
    broadcastDisplay: str
    broadcasterDisplay: str
    broadcasterVideoLink: str
    broadcasterDescription: str
    broadcasterTeamId: int
    regionId: int | None = None  # Not present in older game data


class Broadcasters(PandasMixin, PolarsMixin, BaseModel):
    # International fields may not exist in older game data
    internationalBroadcasters: list[Broadcaster] = Field(default_factory=list)
    internationalRadioBroadcasters: list[Broadcaster] = Field(default_factory=list)
    internationalOttBroadcasters: list[Broadcaster] = Field(default_factory=list)
    nationalBroadcasters: list[Broadcaster]
    nationalRadioBroadcasters: list[Broadcaster]
    nationalOttBroadcasters: list[Broadcaster]
    homeTvBroadcasters: list[Broadcaster]
    homeRadioBroadcasters: list[Broadcaster]
    homeOttBroadcasters: list[Broadcaster]
    awayTvBroadcasters: list[Broadcaster]
    awayRadioBroadcasters: list[Broadcaster]
    awayOttBroadcasters: list[Broadcaster]
