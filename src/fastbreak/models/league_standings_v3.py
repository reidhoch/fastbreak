"""Models for the league standings v3 endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class TeamStandingV3(PandasMixin, PolarsMixin, BaseModel):
    """Team standing record with detailed stats."""

    league_id: str = Field(alias="LeagueID")
    season_id: str = Field(alias="SeasonID")
    team_id: int = Field(alias="TeamID")
    team_city: str = Field(alias="TeamCity")
    team_name: str = Field(alias="TeamName")
    team_slug: str = Field(alias="TeamSlug")
    conference: str = Field(alias="Conference")
    conference_record: str = Field(alias="ConferenceRecord")
    playoff_rank: int = Field(alias="PlayoffRank")
    clinch_indicator: str | None = Field(alias="ClinchIndicator", default=None)
    division: str = Field(alias="Division")
    division_record: str = Field(alias="DivisionRecord")
    division_rank: int = Field(alias="DivisionRank")
    wins: int = Field(alias="WINS")
    losses: int = Field(alias="LOSSES")
    win_pct: float = Field(alias="WinPCT")
    league_rank: int | None = Field(alias="LeagueRank", default=None)
    record: str = Field(alias="Record")
    home: str = Field(alias="HOME")
    road: str = Field(alias="ROAD")
    l10: str = Field(alias="L10")
    last10_home: str = Field(alias="Last10Home")
    last10_road: str = Field(alias="Last10Road")
    ot: str = Field(alias="OT")
    three_pts_or_less: str = Field(alias="ThreePTSOrLess")
    ten_pts_or_more: str = Field(alias="TenPTSOrMore")
    long_home_streak: int = Field(alias="LongHomeStreak")
    str_long_home_streak: str = Field(alias="strLongHomeStreak")
    long_road_streak: int = Field(alias="LongRoadStreak")
    str_long_road_streak: str = Field(alias="strLongRoadStreak")
    long_win_streak: int = Field(alias="LongWinStreak")
    long_loss_streak: int = Field(alias="LongLossStreak")
    current_home_streak: int = Field(alias="CurrentHomeStreak")
    str_current_home_streak: str = Field(alias="strCurrentHomeStreak")
    current_road_streak: int = Field(alias="CurrentRoadStreak")
    str_current_road_streak: str = Field(alias="strCurrentRoadStreak")
    current_streak: int = Field(alias="CurrentStreak")
    str_current_streak: str = Field(alias="strCurrentStreak")
    conference_games_back: float = Field(alias="ConferenceGamesBack")
    division_games_back: float = Field(alias="DivisionGamesBack")
    clinched_conference_title: int = Field(alias="ClinchedConferenceTitle")
    clinched_division_title: int = Field(alias="ClinchedDivisionTitle")
    clinched_playoff_birth: int = Field(alias="ClinchedPlayoffBirth")
    clinched_play_in: int = Field(alias="ClinchedPlayIn")
    eliminated_conference: int = Field(alias="EliminatedConference")
    eliminated_division: int = Field(alias="EliminatedDivision")
    ahead_at_half: str = Field(alias="AheadAtHalf")
    behind_at_half: str = Field(alias="BehindAtHalf")
    tied_at_half: str = Field(alias="TiedAtHalf")
    ahead_at_third: str = Field(alias="AheadAtThird")
    behind_at_third: str = Field(alias="BehindAtThird")
    tied_at_third: str = Field(alias="TiedAtThird")
    score_100_pts: str = Field(alias="Score100PTS")
    opp_score_100_pts: str = Field(alias="OppScore100PTS")
    opp_over_500: str = Field(alias="OppOver500")
    lead_in_fg_pct: str = Field(alias="LeadInFGPCT")
    lead_in_reb: str = Field(alias="LeadInReb")
    fewer_turnovers: str = Field(alias="FewerTurnovers")
    points_pg: float = Field(alias="PointsPG")
    opp_points_pg: float = Field(alias="OppPointsPG")
    diff_points_pg: float = Field(alias="DiffPointsPG")
    vs_east: str = Field(alias="vsEast")
    vs_atlantic: str = Field(alias="vsAtlantic")
    vs_central: str = Field(alias="vsCentral")
    vs_southeast: str = Field(alias="vsSoutheast")
    vs_west: str = Field(alias="vsWest")
    vs_northwest: str = Field(alias="vsNorthwest")
    vs_pacific: str = Field(alias="vsPacific")
    vs_southwest: str = Field(alias="vsSouthwest")
    jan: str | None = Field(alias="Jan", default=None)
    feb: str | None = Field(alias="Feb", default=None)
    mar: str | None = Field(alias="Mar", default=None)
    apr: str | None = Field(alias="Apr", default=None)
    may: str | None = Field(alias="May", default=None)
    jun: str | None = Field(alias="Jun", default=None)
    jul: str | None = Field(alias="Jul", default=None)
    aug: str | None = Field(alias="Aug", default=None)
    sep: str | None = Field(alias="Sep", default=None)
    oct: str | None = Field(alias="Oct", default=None)
    nov: str | None = Field(alias="Nov", default=None)
    dec: str | None = Field(alias="Dec", default=None)
    score_80_plus: str | None = Field(alias="Score_80_Plus", default=None)
    opp_score_80_plus: str | None = Field(alias="Opp_Score_80_Plus", default=None)
    score_below_80: str | None = Field(alias="Score_Below_80", default=None)
    opp_score_below_80: str | None = Field(alias="Opp_Score_Below_80", default=None)
    total_points: int = Field(alias="TotalPoints")
    opp_total_points: int = Field(alias="OppTotalPoints")
    diff_total_points: int = Field(alias="DiffTotalPoints")
    league_games_back: float | None = Field(alias="LeagueGamesBack", default=None)
    playoff_seeding: int | None = Field(alias="PlayoffSeeding", default=None)
    clinched_post_season: int | None = Field(alias="ClinchedPostSeason", default=None)
    neutral: str | None = Field(alias="NEUTRAL", default=None)


class LeagueStandingsV3Response(FrozenResponse):
    """Response from the league standings v3 endpoint.

    Contains comprehensive team standings with records, streaks,
    situational splits, and clinch status.
    """

    standings: list[TeamStandingV3]

    from_result_sets = model_validator(mode="before")(tabular_validator("standings"))
