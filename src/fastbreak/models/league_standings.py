"""Models for the league standings endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import tabular_validator


class TeamStanding(BaseModel):
    """A single team's standings entry."""

    # Team identification
    league_id: str = Field(alias="LeagueID")
    season_id: str = Field(alias="SeasonID")
    team_id: int = Field(alias="TeamID")
    team_city: str = Field(alias="TeamCity")
    team_name: str = Field(alias="TeamName")
    team_slug: str = Field(alias="TeamSlug")

    # Conference standings
    conference: str = Field(alias="Conference")
    conference_record: str = Field(alias="ConferenceRecord")
    playoff_rank: int = Field(alias="PlayoffRank")
    clinch_indicator: str = Field(alias="ClinchIndicator")

    # Division standings
    division: str = Field(alias="Division")
    division_record: str = Field(alias="DivisionRecord")
    division_rank: int = Field(alias="DivisionRank")

    # Win/Loss record
    wins: int = Field(alias="WINS")
    losses: int = Field(alias="LOSSES")
    win_pct: float = Field(alias="WinPCT")
    league_rank: int | None = Field(default=None, alias="LeagueRank")
    record: str = Field(alias="Record")

    # Home/Road splits
    home: str = Field(alias="HOME")
    road: str = Field(alias="ROAD")

    # Recent performance
    l10: str = Field(alias="L10")
    last_10_home: str = Field(alias="Last10Home")
    last_10_road: str = Field(alias="Last10Road")

    # Situational records
    ot: str = Field(alias="OT")
    three_pts_or_less: str = Field(alias="ThreePTSOrLess")
    ten_pts_or_more: str = Field(alias="TenPTSOrMore")

    # Streak information
    long_home_streak: int = Field(alias="LongHomeStreak")
    str_long_home_streak: str = Field(alias="strLongHomeStreak")
    long_road_streak: int = Field(alias="LongRoadStreak")
    str_long_road_streak: str = Field(alias="strLongRoadStreak")
    long_win_streak: int = Field(alias="LongWinStreak")
    long_loss_streak: int = Field(alias="LongLossStreak")

    # Current streaks
    current_home_streak: int = Field(alias="CurrentHomeStreak")
    str_current_home_streak: str = Field(alias="strCurrentHomeStreak")
    current_road_streak: int = Field(alias="CurrentRoadStreak")
    str_current_road_streak: str = Field(alias="strCurrentRoadStreak")
    current_streak: int = Field(alias="CurrentStreak")
    str_current_streak: str = Field(alias="strCurrentStreak")

    # Games back
    conference_games_back: float = Field(alias="ConferenceGamesBack")
    division_games_back: float = Field(alias="DivisionGamesBack")

    # Clinching status
    clinched_conference_title: int | None = Field(
        default=None,
        alias="ClinchedConferenceTitle",
    )
    clinched_division_title: int | None = Field(
        default=None,
        alias="ClinchedDivisionTitle",
    )
    clinched_playoff_birth: int | None = Field(
        default=None,
        alias="ClinchedPlayoffBirth",
    )
    clinched_play_in: int = Field(alias="ClinchedPlayIn")

    # Elimination status
    eliminated_conference: int | None = Field(
        default=None,
        alias="EliminatedConference",
    )
    eliminated_division: int | None = Field(default=None, alias="EliminatedDivision")

    # Halftime situation records
    ahead_at_half: str = Field(alias="AheadAtHalf")
    behind_at_half: str = Field(alias="BehindAtHalf")
    tied_at_half: str = Field(alias="TiedAtHalf")

    # Third quarter situation records
    ahead_at_third: str = Field(alias="AheadAtThird")
    behind_at_third: str = Field(alias="BehindAtThird")
    tied_at_third: str = Field(alias="TiedAtThird")

    # Scoring records
    score_100_pts: str = Field(alias="Score100PTS")
    opp_score_100_pts: str = Field(alias="OppScore100PTS")
    opp_over_500: str = Field(alias="OppOver500")

    # Statistical advantage records
    lead_in_fg_pct: str = Field(alias="LeadInFGPCT")
    lead_in_reb: str = Field(alias="LeadInReb")
    fewer_turnovers: str = Field(alias="FewerTurnovers")

    # Points per game
    points_pg: float = Field(alias="PointsPG")
    opp_points_pg: float = Field(alias="OppPointsPG")
    diff_points_pg: float = Field(alias="DiffPointsPG")

    # Conference matchup records
    vs_east: str = Field(alias="vsEast")
    vs_atlantic: str = Field(alias="vsAtlantic")
    vs_central: str = Field(alias="vsCentral")
    vs_southeast: str = Field(alias="vsSoutheast")
    vs_west: str = Field(alias="vsWest")
    vs_northwest: str = Field(alias="vsNorthwest")
    vs_pacific: str = Field(alias="vsPacific")
    vs_southwest: str = Field(alias="vsSouthwest")

    # Monthly records
    jan: str = Field(alias="Jan")
    feb: str = Field(alias="Feb")
    mar: str = Field(alias="Mar")
    apr: str = Field(alias="Apr")
    may: str = Field(alias="May")
    jun: str = Field(alias="Jun")
    jul: str = Field(alias="Jul")
    aug: str = Field(alias="Aug")
    sep: str = Field(alias="Sep")
    oct: str = Field(alias="Oct")
    nov: str = Field(alias="Nov")
    dec: str = Field(alias="Dec")

    # Score threshold records
    score_80_plus: str = Field(alias="Score_80_Plus")
    opp_score_80_plus: str = Field(alias="Opp_Score_80_Plus")
    score_below_80: str = Field(alias="Score_Below_80")
    opp_score_below_80: str = Field(alias="Opp_Score_Below_80")

    # Total points
    total_points: int = Field(alias="TotalPoints")
    opp_total_points: int = Field(alias="OppTotalPoints")
    diff_total_points: int = Field(alias="DiffTotalPoints")

    # Playoff information
    league_games_back: float = Field(alias="LeagueGamesBack")
    playoff_seeding: int | None = Field(default=None, alias="PlayoffSeeding")
    clinched_post_season: int = Field(alias="ClinchedPostSeason")

    # Neutral site
    neutral: str = Field(alias="NEUTRAL")


class LeagueStandingsResponse(BaseModel):
    """Response from the league standings endpoint."""

    standings: list[TeamStanding]

    from_result_sets = model_validator(mode="before")(tabular_validator("standings"))
