"""Models for the box score summary v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class ArenaV3(BaseModel):
    """Arena information in V3 format."""

    arena_id: int = Field(alias="arenaId")
    arena_name: str = Field(alias="arenaName")
    arena_city: str = Field(alias="arenaCity")
    arena_state: str = Field(alias="arenaState")
    arena_country: str = Field(alias="arenaCountry")
    arena_timezone: str = Field(alias="arenaTimezone")
    arena_street_address: str = Field(alias="arenaStreetAddress")
    arena_postal_code: str = Field(alias="arenaPostalCode")


class OfficialV3(BaseModel):
    """Game official information in V3 format."""

    person_id: int = Field(alias="personId")
    name: str
    name_i: str = Field(alias="nameI")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    jersey_num: str = Field(alias="jerseyNum")
    assignment: str


class BroadcasterV3(BaseModel):
    """Broadcaster information in V3 format."""

    broadcaster_id: int = Field(alias="broadcasterId")
    broadcast_display: str = Field(alias="broadcastDisplay")
    broadcaster_display: str = Field(alias="broadcasterDisplay")
    broadcaster_video_link: str = Field(alias="broadcasterVideoLink")
    broadcaster_description: str = Field(alias="broadcasterDescription")
    broadcaster_team_id: int = Field(alias="broadcasterTeamId")
    region_id: int = Field(alias="regionId")


class BroadcastersV3(BaseModel):
    """All broadcaster information for a game in V3 format."""

    international_broadcasters: list[BroadcasterV3] = Field(
        alias="internationalBroadcasters", default_factory=list
    )
    international_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="internationalRadioBroadcasters", default_factory=list
    )
    international_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="internationalOttBroadcasters", default_factory=list
    )
    national_broadcasters: list[BroadcasterV3] = Field(
        alias="nationalBroadcasters", default_factory=list
    )
    national_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="nationalRadioBroadcasters", default_factory=list
    )
    national_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="nationalOttBroadcasters", default_factory=list
    )
    home_tv_broadcasters: list[BroadcasterV3] = Field(
        alias="homeTvBroadcasters", default_factory=list
    )
    home_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="homeRadioBroadcasters", default_factory=list
    )
    home_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="homeOttBroadcasters", default_factory=list
    )
    away_tv_broadcasters: list[BroadcasterV3] = Field(
        alias="awayTvBroadcasters", default_factory=list
    )
    away_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="awayRadioBroadcasters", default_factory=list
    )
    away_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="awayOttBroadcasters", default_factory=list
    )


class SummaryTeamV3(BaseModel):
    """Team summary information in V3 format."""

    team_id: int = Field(alias="teamId")
    team_city: str = Field(alias="teamCity")
    team_name: str = Field(alias="teamName")
    team_tricode: str = Field(alias="teamTricode")
    team_slug: str = Field(alias="teamSlug")
    team_wins: int = Field(alias="teamWins")
    team_losses: int = Field(alias="teamLosses")
    score: int
    seed: int | None = None
    inactive_players: list[dict[str, object]] = Field(
        alias="inactivePlayers", default_factory=list
    )


class BoxScoreSummaryV3Data(BaseModel):
    """Box score summary data in V3 format."""

    game_id: str = Field(alias="gameId")
    game_code: str = Field(alias="gameCode")
    game_status: int = Field(alias="gameStatus")
    game_status_text: str = Field(alias="gameStatusText")
    period: int
    game_clock: str = Field(alias="gameClock")
    game_time_utc: str = Field(alias="gameTimeUTC")
    game_et: str = Field(alias="gameEt")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    duration: str
    attendance: int
    sellout: int
    series_game_number: str = Field(alias="seriesGameNumber")
    game_label: str = Field(alias="gameLabel")
    game_sub_label: str = Field(alias="gameSubLabel")
    series_text: str = Field(alias="seriesText")
    if_necessary: bool = Field(alias="ifNecessary")
    is_neutral: bool = Field(alias="isNeutral")
    arena: ArenaV3
    officials: list[OfficialV3]
    broadcasters: BroadcastersV3
    home_team: SummaryTeamV3 = Field(alias="homeTeam")
    away_team: SummaryTeamV3 = Field(alias="awayTeam")


class BoxScoreSummaryV3Response(FrozenResponse):
    """Response from the box score summary v3 endpoint.

    Contains game metadata (status, arena, officials, broadcasters, teams)
    in modern nested JSON format.
    """

    meta: Meta
    box_score_summary: BoxScoreSummaryV3Data = Field(alias="boxScoreSummary")
