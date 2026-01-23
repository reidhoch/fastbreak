"""Models for the scoreboard v3 endpoint."""

from pydantic import BaseModel, Field


class ScoreboardBroadcaster(BaseModel):
    """A broadcaster for a game."""

    broadcaster_id: int | None = Field(default=None, alias="broadcasterId")
    broadcast_display: str | None = Field(default=None, alias="broadcastDisplay")
    broadcaster_team_id: int | None = Field(default=None, alias="broadcasterTeamId")
    broadcaster_description: str | None = Field(
        default=None, alias="broadcasterDescription"
    )


class ScoreboardBroadcasters(BaseModel):
    """All broadcasters for a game."""

    national_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="nationalBroadcasters"
    )
    national_radio_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="nationalRadioBroadcasters"
    )
    national_ott_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="nationalOttBroadcasters"
    )
    home_tv_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="homeTvBroadcasters"
    )
    home_radio_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="homeRadioBroadcasters"
    )
    home_ott_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="homeOttBroadcasters"
    )
    away_tv_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="awayTvBroadcasters"
    )
    away_radio_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="awayRadioBroadcasters"
    )
    away_ott_broadcasters: list[ScoreboardBroadcaster] = Field(
        default_factory=list, alias="awayOttBroadcasters"
    )


class GameLeader(BaseModel):
    """A game leader (top performer in the game)."""

    person_id: int | None = Field(default=None, alias="personId")
    name: str | None = Field(default=None, alias="name")
    player_slug: str | None = Field(default=None, alias="playerSlug")
    jersey_num: str | None = Field(default=None, alias="jerseyNum")
    position: str | None = Field(default=None, alias="position")
    team_tricode: str | None = Field(default=None, alias="teamTricode")
    points: int | None = Field(default=None, alias="points")
    rebounds: int | None = Field(default=None, alias="rebounds")
    assists: int | None = Field(default=None, alias="assists")


class GameLeaders(BaseModel):
    """Game leaders for both teams."""

    home_leaders: GameLeader | None = Field(default=None, alias="homeLeaders")
    away_leaders: GameLeader | None = Field(default=None, alias="awayLeaders")


class TeamLeader(BaseModel):
    """A team's season statistical leader."""

    person_id: int | None = Field(default=None, alias="personId")
    name: str | None = Field(default=None, alias="name")
    player_slug: str | None = Field(default=None, alias="playerSlug")
    jersey_num: str | None = Field(default=None, alias="jerseyNum")
    position: str | None = Field(default=None, alias="position")
    team_tricode: str | None = Field(default=None, alias="teamTricode")
    points: float | None = Field(default=None, alias="points")
    rebounds: float | None = Field(default=None, alias="rebounds")
    assists: float | None = Field(default=None, alias="assists")


class TeamLeaders(BaseModel):
    """Season leaders for both teams."""

    home_leaders: TeamLeader | None = Field(default=None, alias="homeLeaders")
    away_leaders: TeamLeader | None = Field(default=None, alias="awayLeaders")
    season_leaders_flag: int | None = Field(default=None, alias="seasonLeadersFlag")


class PeriodScore(BaseModel):
    """Score for a single period."""

    period: int | None = Field(default=None, alias="period")
    period_type: str | None = Field(default=None, alias="periodType")
    score: int | None = Field(default=None, alias="score")


class ScoreboardTeam(BaseModel):
    """Team info in scoreboard."""

    team_id: int | None = Field(default=None, alias="teamId")
    team_name: str | None = Field(default=None, alias="teamName")
    team_city: str | None = Field(default=None, alias="teamCity")
    team_tricode: str | None = Field(default=None, alias="teamTricode")
    team_slug: str | None = Field(default=None, alias="teamSlug")
    wins: int | None = Field(default=None, alias="wins")
    losses: int | None = Field(default=None, alias="losses")
    score: int | None = Field(default=None, alias="score")
    seed: int | None = Field(default=None, alias="seed")
    in_bonus: str | None = Field(default=None, alias="inBonus")
    timeouts_remaining: int | None = Field(default=None, alias="timeoutsRemaining")
    periods: list[PeriodScore] = Field(default_factory=list, alias="periods")


class ScoreboardGame(BaseModel):
    """A single game in the scoreboard."""

    game_id: str | None = Field(default=None, alias="gameId")
    game_code: str | None = Field(default=None, alias="gameCode")
    game_status: int | None = Field(default=None, alias="gameStatus")
    game_status_text: str | None = Field(default=None, alias="gameStatusText")
    period: int | None = Field(default=None, alias="period")
    game_clock: str | None = Field(default=None, alias="gameClock")
    game_time_utc: str | None = Field(default=None, alias="gameTimeUTC")
    game_et: str | None = Field(default=None, alias="gameEt")
    regulation_periods: int | None = Field(default=None, alias="regulationPeriods")
    series_game_number: str | None = Field(default=None, alias="seriesGameNumber")
    game_label: str | None = Field(default=None, alias="gameLabel")
    game_sub_label: str | None = Field(default=None, alias="gameSubLabel")
    series_text: str | None = Field(default=None, alias="seriesText")
    if_necessary: bool | None = Field(default=None, alias="ifNecessary")
    series_conference: str | None = Field(default=None, alias="seriesConference")
    po_round_desc: str | None = Field(default=None, alias="poRoundDesc")
    game_subtype: str | None = Field(default=None, alias="gameSubtype")
    is_neutral: bool | None = Field(default=None, alias="isNeutral")
    game_leaders: GameLeaders | None = Field(default=None, alias="gameLeaders")
    team_leaders: TeamLeaders | None = Field(default=None, alias="teamLeaders")
    broadcasters: ScoreboardBroadcasters | None = Field(
        default=None, alias="broadcasters"
    )
    home_team: ScoreboardTeam | None = Field(default=None, alias="homeTeam")
    away_team: ScoreboardTeam | None = Field(default=None, alias="awayTeam")


class Scoreboard(BaseModel):
    """The main scoreboard data."""

    game_date: str | None = Field(default=None, alias="gameDate")
    league_id: str | None = Field(default=None, alias="leagueId")
    league_name: str | None = Field(default=None, alias="leagueName")
    games: list[ScoreboardGame] = Field(default_factory=list, alias="games")


class ScoreboardV3Response(BaseModel):
    """Response from the scoreboard v3 endpoint.

    This endpoint returns the daily scoreboard with all games for a given date.
    Each game includes live score, period breakdowns, game leaders, team season
    leaders, and broadcaster information.

    The response uses nested JSON format (v3 style) instead of resultSets.
    """

    scoreboard: Scoreboard | None = Field(default=None, alias="scoreboard")
