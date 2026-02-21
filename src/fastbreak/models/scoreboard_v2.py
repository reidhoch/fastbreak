"""Models for the ScoreboardV2 endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class GameHeader(PandasMixin, PolarsMixin, BaseModel):
    """Game header information for a scoreboard game."""

    game_date_est: str = Field(alias="GAME_DATE_EST")
    game_sequence: int = Field(alias="GAME_SEQUENCE")
    game_id: str = Field(alias="GAME_ID")
    game_status_id: int = Field(alias="GAME_STATUS_ID")
    game_status_text: str = Field(alias="GAME_STATUS_TEXT")
    game_code: str = Field(alias="GAMECODE")
    home_team_id: int = Field(alias="HOME_TEAM_ID")
    visitor_team_id: int = Field(alias="VISITOR_TEAM_ID")
    season: str = Field(alias="SEASON")
    live_period: int = Field(alias="LIVE_PERIOD")
    live_pc_time: str | None = Field(default=None, alias="LIVE_PC_TIME")
    natl_tv_broadcaster_abbreviation: str | None = Field(
        default=None, alias="NATL_TV_BROADCASTER_ABBREVIATION"
    )
    home_tv_broadcaster_abbreviation: str | None = Field(
        default=None, alias="HOME_TV_BROADCASTER_ABBREVIATION"
    )
    away_tv_broadcaster_abbreviation: str | None = Field(
        default=None, alias="AWAY_TV_BROADCASTER_ABBREVIATION"
    )
    live_period_time_bcast: str | None = Field(
        default=None, alias="LIVE_PERIOD_TIME_BCAST"
    )
    arena_name: str | None = Field(default=None, alias="ARENA_NAME")
    wh_status: int | None = Field(default=None, alias="WH_STATUS")
    wnba_commissioner_flag: int | None = Field(
        default=None, alias="WNBA_COMMISSIONER_FLAG"
    )


class LineScore(PandasMixin, PolarsMixin, BaseModel):
    """Quarter-by-quarter line score for a team."""

    game_date_est: str = Field(alias="GAME_DATE_EST")
    game_sequence: int = Field(alias="GAME_SEQUENCE")
    game_id: str = Field(alias="GAME_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_city_name: str = Field(alias="TEAM_CITY_NAME")
    team_name: str = Field(alias="TEAM_NAME")
    team_wins_losses: str = Field(alias="TEAM_WINS_LOSSES")
    pts_qtr1: int | None = Field(default=None, alias="PTS_QTR1")
    pts_qtr2: int | None = Field(default=None, alias="PTS_QTR2")
    pts_qtr3: int | None = Field(default=None, alias="PTS_QTR3")
    pts_qtr4: int | None = Field(default=None, alias="PTS_QTR4")
    pts_ot1: int | None = Field(default=None, alias="PTS_OT1")
    pts_ot2: int | None = Field(default=None, alias="PTS_OT2")
    pts_ot3: int | None = Field(default=None, alias="PTS_OT3")
    pts_ot4: int | None = Field(default=None, alias="PTS_OT4")
    pts_ot5: int | None = Field(default=None, alias="PTS_OT5")
    pts_ot6: int | None = Field(default=None, alias="PTS_OT6")
    pts_ot7: int | None = Field(default=None, alias="PTS_OT7")
    pts_ot8: int | None = Field(default=None, alias="PTS_OT8")
    pts_ot9: int | None = Field(default=None, alias="PTS_OT9")
    pts_ot10: int | None = Field(default=None, alias="PTS_OT10")
    pts: int | None = Field(default=None, alias="PTS")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")
    ft_pct: float | None = Field(default=None, alias="FT_PCT")
    fg3_pct: float | None = Field(default=None, alias="FG3_PCT")
    ast: int | None = Field(default=None, alias="AST")
    reb: int | None = Field(default=None, alias="REB")
    tov: int | None = Field(default=None, alias="TOV")


class SeriesStanding(PandasMixin, PolarsMixin, BaseModel):
    """Season series standing between two teams."""

    game_id: str = Field(alias="GAME_ID")
    home_team_id: int = Field(alias="HOME_TEAM_ID")
    visitor_team_id: int = Field(alias="VISITOR_TEAM_ID")
    game_date_est: str = Field(alias="GAME_DATE_EST")
    home_team_wins: int = Field(alias="HOME_TEAM_WINS")
    home_team_losses: int = Field(alias="HOME_TEAM_LOSSES")
    series_leader: str | None = Field(default=None, alias="SERIES_LEADER")


class LastMeeting(PandasMixin, PolarsMixin, BaseModel):
    """Information about the last meeting between two teams."""

    game_id: str = Field(alias="GAME_ID")
    last_game_id: str = Field(alias="LAST_GAME_ID")
    last_game_date_est: str = Field(alias="LAST_GAME_DATE_EST")
    last_game_home_team_id: int = Field(alias="LAST_GAME_HOME_TEAM_ID")
    last_game_home_team_city: str = Field(alias="LAST_GAME_HOME_TEAM_CITY")
    last_game_home_team_name: str = Field(alias="LAST_GAME_HOME_TEAM_NAME")
    last_game_home_team_abbreviation: str = Field(
        alias="LAST_GAME_HOME_TEAM_ABBREVIATION"
    )
    last_game_home_team_points: int = Field(alias="LAST_GAME_HOME_TEAM_POINTS")
    last_game_visitor_team_id: int = Field(alias="LAST_GAME_VISITOR_TEAM_ID")
    last_game_visitor_team_city: str = Field(alias="LAST_GAME_VISITOR_TEAM_CITY")
    last_game_visitor_team_name: str = Field(alias="LAST_GAME_VISITOR_TEAM_NAME")
    last_game_visitor_team_city1: str = Field(alias="LAST_GAME_VISITOR_TEAM_CITY1")
    last_game_visitor_team_points: int = Field(alias="LAST_GAME_VISITOR_TEAM_POINTS")


class ConferenceStanding(PandasMixin, PolarsMixin, BaseModel):
    """Conference standing for a team on a specific date."""

    team_id: int = Field(alias="TEAM_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    season_id: str = Field(alias="SEASON_ID")
    standings_date: str = Field(alias="STANDINGSDATE")
    conference: str = Field(alias="CONFERENCE")
    team: str = Field(alias="TEAM")
    games: int = Field(alias="G")
    wins: int = Field(alias="W")
    losses: int = Field(alias="L")
    win_pct: float = Field(alias="W_PCT")
    home_record: str = Field(alias="HOME_RECORD")
    road_record: str = Field(alias="ROAD_RECORD")


class AvailableGame(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking availability for a game."""

    game_id: str = Field(alias="GAME_ID")
    pt_available: int = Field(alias="PT_AVAILABLE")


class TeamLeader(PandasMixin, PolarsMixin, BaseModel):
    """Team statistical leaders for a game."""

    game_id: str = Field(alias="GAME_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_city: str = Field(alias="TEAM_CITY")
    team_nickname: str = Field(alias="TEAM_NICKNAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    pts_player_id: int = Field(alias="PTS_PLAYER_ID")
    pts_player_name: str = Field(alias="PTS_PLAYER_NAME")
    pts: int = Field(alias="PTS")
    reb_player_id: int = Field(alias="REB_PLAYER_ID")
    reb_player_name: str = Field(alias="REB_PLAYER_NAME")
    reb: int = Field(alias="REB")
    ast_player_id: int = Field(alias="AST_PLAYER_ID")
    ast_player_name: str = Field(alias="AST_PLAYER_NAME")
    ast: int = Field(alias="AST")


class TicketLink(PandasMixin, PolarsMixin, BaseModel):
    """Ticket purchase link for a game."""

    game_id: str = Field(alias="GAME_ID")
    leag_tix: str | None = Field(default=None, alias="LEAG_TIX")


class ScoreboardV2Response(FrozenResponse):
    """Response from the ScoreboardV2 endpoint.

    Returns the daily scoreboard with comprehensive game information including:
    - Game headers with status, teams, and broadcasters
    - Quarter-by-quarter line scores
    - Season series standings between teams
    - Last meeting information
    - Conference standings for the date
    - Player tracking availability
    - Team leaders for each game (pts/reb/ast)
    """

    game_header: list[GameHeader] = Field(default_factory=list)
    line_score: list[LineScore] = Field(default_factory=list)
    series_standings: list[SeriesStanding] = Field(default_factory=list)
    last_meeting: list[LastMeeting] = Field(default_factory=list)
    east_conf_standings_by_day: list[ConferenceStanding] = Field(default_factory=list)
    west_conf_standings_by_day: list[ConferenceStanding] = Field(default_factory=list)
    available: list[AvailableGame] = Field(default_factory=list)
    team_leaders: list[TeamLeader] = Field(default_factory=list)
    ticket_links: list[TicketLink] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "game_header": "GameHeader",
                "line_score": "LineScore",
                "series_standings": "SeriesStandings",
                "last_meeting": "LastMeeting",
                "east_conf_standings_by_day": "EastConfStandingsByDay",
                "west_conf_standings_by_day": "WestConfStandingsByDay",
                "available": "Available",
                "team_leaders": "TeamLeaders",
                "ticket_links": "TicketLinks",
            },
            ignore_missing=True,
        )
    )
