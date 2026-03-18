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
    internationalBroadcasters: list[Broadcaster] = Field(
        default_factory=list[Broadcaster]
    )
    internationalRadioBroadcasters: list[Broadcaster] = Field(
        default_factory=list[Broadcaster]
    )
    internationalOttBroadcasters: list[Broadcaster] = Field(
        default_factory=list[Broadcaster]
    )
    nationalBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
    nationalRadioBroadcasters: list[Broadcaster] = Field(
        default_factory=list[Broadcaster]
    )
    nationalOttBroadcasters: list[Broadcaster] = Field(
        default_factory=list[Broadcaster]
    )
    homeTvBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
    homeRadioBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
    homeOttBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
    awayTvBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
    awayRadioBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
    awayOttBroadcasters: list[Broadcaster] = Field(default_factory=list[Broadcaster])
