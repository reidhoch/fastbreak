"""Models for the schedule league v2 endpoint."""

from pydantic import BaseModel, Field


class ScheduleBroadcaster(BaseModel):
    """A single broadcaster for a game."""

    broadcaster_scope: str | None = Field(default=None, alias="broadcasterScope")
    broadcaster_media: str | None = Field(default=None, alias="broadcasterMedia")
    broadcaster_id: int | None = Field(default=None, alias="broadcasterId")
    broadcaster_display: str | None = Field(default=None, alias="broadcasterDisplay")
    broadcaster_abbreviation: str | None = Field(
        default=None, alias="broadcasterAbbreviation"
    )
    broadcaster_description: str | None = Field(
        default=None, alias="broadcasterDescription"
    )
    tape_delay_comments: str | None = Field(default=None, alias="tapeDelayComments")
    broadcaster_video_link: str | None = Field(
        default=None, alias="broadcasterVideoLink"
    )
    broadcaster_team_id: int | None = Field(default=None, alias="broadcasterTeamId")
    broadcaster_ranking: int | None = Field(default=None, alias="broadcasterRanking")


class GameBroadcasters(BaseModel):
    """All broadcasters for a game."""

    national_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="nationalBroadcasters"
    )
    national_radio_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="nationalRadioBroadcasters"
    )
    national_ott_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="nationalOttBroadcasters"
    )
    home_tv_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="homeTvBroadcasters"
    )
    home_radio_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="homeRadioBroadcasters"
    )
    home_ott_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="homeOttBroadcasters"
    )
    away_tv_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="awayTvBroadcasters"
    )
    away_radio_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="awayRadioBroadcasters"
    )
    away_ott_broadcasters: list[ScheduleBroadcaster] = Field(
        default_factory=list, alias="awayOttBroadcasters"
    )


class ScheduleTeam(BaseModel):
    """Team info in a scheduled game."""

    team_id: int | None = Field(default=None, alias="teamId")
    team_name: str | None = Field(default=None, alias="teamName")
    team_city: str | None = Field(default=None, alias="teamCity")
    team_tricode: str | None = Field(default=None, alias="teamTricode")
    team_slug: str | None = Field(default=None, alias="teamSlug")
    wins: int | None = Field(default=None, alias="wins")
    losses: int | None = Field(default=None, alias="losses")
    score: int | None = Field(default=None, alias="score")
    seed: int | None = Field(default=None, alias="seed")


class PointsLeader(BaseModel):
    """Points leader for a game."""

    person_id: int | None = Field(default=None, alias="personId")
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    team_id: int | None = Field(default=None, alias="teamId")
    team_city: str | None = Field(default=None, alias="teamCity")
    team_name: str | None = Field(default=None, alias="teamName")
    team_tricode: str | None = Field(default=None, alias="teamTricode")
    points: float | None = Field(default=None, alias="points")


class ScheduledGame(BaseModel):
    """A single game in the schedule."""

    game_id: str | None = Field(default=None, alias="gameId")
    game_code: str | None = Field(default=None, alias="gameCode")
    game_status: int | None = Field(default=None, alias="gameStatus")
    game_status_text: str | None = Field(default=None, alias="gameStatusText")
    game_sequence: int | None = Field(default=None, alias="gameSequence")
    game_date_est: str | None = Field(default=None, alias="gameDateEst")
    game_time_est: str | None = Field(default=None, alias="gameTimeEst")
    game_date_time_est: str | None = Field(default=None, alias="gameDateTimeEst")
    game_date_utc: str | None = Field(default=None, alias="gameDateUTC")
    game_time_utc: str | None = Field(default=None, alias="gameTimeUTC")
    game_date_time_utc: str | None = Field(default=None, alias="gameDateTimeUTC")
    away_team_time: str | None = Field(default=None, alias="awayTeamTime")
    home_team_time: str | None = Field(default=None, alias="homeTeamTime")
    day: str | None = Field(default=None, alias="day")
    month_num: int | None = Field(default=None, alias="monthNum")
    week_number: int | None = Field(default=None, alias="weekNumber")
    week_name: str | None = Field(default=None, alias="weekName")
    if_necessary: str | None = Field(default=None, alias="ifNecessary")
    series_game_number: str | None = Field(default=None, alias="seriesGameNumber")
    game_label: str | None = Field(default=None, alias="gameLabel")
    game_sub_label: str | None = Field(default=None, alias="gameSubLabel")
    series_text: str | None = Field(default=None, alias="seriesText")
    arena_name: str | None = Field(default=None, alias="arenaName")
    arena_state: str | None = Field(default=None, alias="arenaState")
    arena_city: str | None = Field(default=None, alias="arenaCity")
    postponed_status: str | None = Field(default=None, alias="postponedStatus")
    branch_link: str | None = Field(default=None, alias="branchLink")
    game_subtype: str | None = Field(default=None, alias="gameSubtype")
    is_neutral: bool | None = Field(default=None, alias="isNeutral")
    broadcasters: GameBroadcasters | None = Field(default=None, alias="broadcasters")
    home_team: ScheduleTeam | None = Field(default=None, alias="homeTeam")
    away_team: ScheduleTeam | None = Field(default=None, alias="awayTeam")
    points_leaders: list[PointsLeader] = Field(
        default_factory=list, alias="pointsLeaders"
    )


class GameDate(BaseModel):
    """A single date with its games."""

    game_date: str | None = Field(default=None, alias="gameDate")
    games: list[ScheduledGame] = Field(default_factory=list, alias="games")


class ScheduleWeek(BaseModel):
    """A week in the schedule."""

    week_number: int | None = Field(default=None, alias="weekNumber")
    week_name: str | None = Field(default=None, alias="weekName")
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")


class LeagueSchedule(BaseModel):
    """The main schedule data."""

    season_year: str | None = Field(default=None, alias="seasonYear")
    league_id: str | None = Field(default=None, alias="leagueId")
    game_dates: list[GameDate] = Field(default_factory=list, alias="gameDates")
    weeks: list[ScheduleWeek] = Field(default_factory=list, alias="weeks")


class ScheduleLeagueV2Response(BaseModel):
    """Response from the schedule league v2 endpoint.

    This endpoint returns the full season schedule with all games organized
    by date. Each game includes detailed information about teams, broadcasters,
    venue, and points leaders (for completed games).

    Note: This response uses a nested JSON format instead of the typical
    resultSets tabular format used by older NBA API endpoints.
    """

    league_schedule: LeagueSchedule | None = Field(default=None, alias="leagueSchedule")
