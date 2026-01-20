from pydantic import BaseModel


class Broadcaster(BaseModel):
    broadcasterId: int
    broadcastDisplay: str
    broadcasterDisplay: str
    broadcasterVideoLink: str
    broadcasterDescription: str
    broadcasterTeamId: int
    regionId: int


class Broadcasters(BaseModel):
    internationalBroadcasters: list[Broadcaster]
    internationalRadioBroadcasters: list[Broadcaster]
    internationalOttBroadcasters: list[Broadcaster]
    nationalBroadcasters: list[Broadcaster]
    nationalRadioBroadcasters: list[Broadcaster]
    nationalOttBroadcasters: list[Broadcaster]
    homeTvBroadcasters: list[Broadcaster]
    homeRadioBroadcasters: list[Broadcaster]
    homeOttBroadcasters: list[Broadcaster]
    awayTvBroadcasters: list[Broadcaster]
    awayRadioBroadcasters: list[Broadcaster]
    awayOttBroadcasters: list[Broadcaster]
