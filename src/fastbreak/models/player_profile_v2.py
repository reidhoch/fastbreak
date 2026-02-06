"""Models for the Player Profile V2 endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
    parse_single_result_set,
)


class _ProfileBaseStats(PandasMixin, PolarsMixin, BaseModel):
    """Base statistics shared across season and career totals."""

    player_id: int = Field(alias="PLAYER_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class ProfileSeasonTotals(_ProfileBaseStats):
    """Season-by-season statistics for a player."""

    season_id: str = Field(alias="SEASON_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    player_age: float | None = Field(alias="PLAYER_AGE")


class ProfileCareerTotals(_ProfileBaseStats):
    """Career total statistics for a player."""


class ProfileCollegeSeasonTotals(PandasMixin, PolarsMixin, BaseModel):
    """Season-by-season college statistics for a player."""

    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    organization_id: int = Field(alias="ORGANIZATION_ID")
    school_name: str = Field(alias="SCHOOL_NAME")
    player_age: float | None = Field(alias="PLAYER_AGE")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class ProfileCollegeCareerTotals(PandasMixin, PolarsMixin, BaseModel):
    """Career college total statistics for a player."""

    player_id: int = Field(alias="PLAYER_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    organization_id: int = Field(alias="ORGANIZATION_ID")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class ProfileSeasonRankings(PandasMixin, PolarsMixin, BaseModel):
    """Season rankings for a player's statistics."""

    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    player_age: str = Field(alias="PLAYER_AGE")
    gp: str = Field(alias="GP")
    gs: str = Field(alias="GS")
    rank_pg_min: int | None = Field(alias="RANK_PG_MIN")
    rank_pg_fgm: int | None = Field(alias="RANK_PG_FGM")
    rank_pg_fga: int | None = Field(alias="RANK_PG_FGA")
    rank_fg_pct: int | None = Field(alias="RANK_FG_PCT")
    rank_pg_fg3m: int | None = Field(alias="RANK_PG_FG3M")
    rank_pg_fg3a: int | None = Field(alias="RANK_PG_FG3A")
    rank_fg3_pct: int | None = Field(alias="RANK_FG3_PCT")
    rank_pg_ftm: int | None = Field(alias="RANK_PG_FTM")
    rank_pg_fta: int | None = Field(alias="RANK_PG_FTA")
    rank_ft_pct: int | None = Field(alias="RANK_FT_PCT")
    rank_pg_oreb: int | None = Field(alias="RANK_PG_OREB")
    rank_pg_dreb: int | None = Field(alias="RANK_PG_DREB")
    rank_pg_reb: int | None = Field(alias="RANK_PG_REB")
    rank_pg_ast: int | None = Field(alias="RANK_PG_AST")
    rank_pg_stl: int | None = Field(alias="RANK_PG_STL")
    rank_pg_blk: int | None = Field(alias="RANK_PG_BLK")
    rank_pg_tov: int | None = Field(alias="RANK_PG_TOV")
    rank_pg_pts: int | None = Field(alias="RANK_PG_PTS")
    rank_pg_eff: int | None = Field(alias="RANK_PG_EFF")


class ProfileStatHigh(PandasMixin, PolarsMixin, BaseModel):
    """A single statistical high (season or career)."""

    player_id: int = Field(alias="PLAYER_ID")
    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    vs_team_id: int = Field(alias="VS_TEAM_ID")
    vs_team_city: str = Field(alias="VS_TEAM_CITY")
    vs_team_name: str = Field(alias="VS_TEAM_NAME")
    vs_team_abbreviation: str = Field(alias="VS_TEAM_ABBREVIATION")
    stat: str = Field(alias="STAT")
    stat_value: int = Field(alias="STAT_VALUE")
    stat_order: int = Field(alias="STAT_ORDER")
    date_est: str = Field(alias="DATE_EST")


class ProfileNextGame(PandasMixin, PolarsMixin, BaseModel):
    """Information about the player's next scheduled game."""

    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    game_time: str = Field(alias="GAME_TIME")
    location: str = Field(alias="LOCATION")
    player_team_id: int = Field(alias="PLAYER_TEAM_ID")
    player_team_city: str = Field(alias="PLAYER_TEAM_CITY")
    player_team_nickname: str = Field(alias="PLAYER_TEAM_NICKNAME")
    player_team_abbreviation: str = Field(alias="PLAYER_TEAM_ABBREVIATION")
    vs_team_id: int = Field(alias="VS_TEAM_ID")
    vs_team_city: str = Field(alias="VS_TEAM_CITY")
    vs_team_nickname: str = Field(alias="VS_TEAM_NICKNAME")
    vs_team_abbreviation: str = Field(alias="VS_TEAM_ABBREVIATION")


class PlayerProfileV2Response(FrozenResponse):
    """Response from the player profile v2 endpoint.

    Contains comprehensive career statistics including:
    - Season and career totals for regular season, playoffs, all-star, college, preseason
    - Season rankings for regular season and playoffs
    - Season and career statistical highs
    - Next game information
    """

    # Regular season
    season_totals_regular_season: list[ProfileSeasonTotals] = Field(
        default_factory=list
    )
    career_totals_regular_season: ProfileCareerTotals | None = None

    # Post season
    season_totals_post_season: list[ProfileSeasonTotals] = Field(default_factory=list)
    career_totals_post_season: ProfileCareerTotals | None = None

    # All-Star
    season_totals_all_star: list[ProfileSeasonTotals] = Field(default_factory=list)
    career_totals_all_star: ProfileCareerTotals | None = None

    # College
    season_totals_college: list[ProfileCollegeSeasonTotals] = Field(
        default_factory=list
    )
    career_totals_college: ProfileCollegeCareerTotals | None = None

    # Preseason
    season_totals_preseason: list[ProfileSeasonTotals] = Field(default_factory=list)
    career_totals_preseason: ProfileCareerTotals | None = None

    # Rankings
    season_rankings_regular_season: list[ProfileSeasonRankings] = Field(
        default_factory=list
    )
    season_rankings_post_season: list[ProfileSeasonRankings] = Field(
        default_factory=list
    )

    # Highs
    season_highs: list[ProfileStatHigh] = Field(default_factory=list)
    career_highs: list[ProfileStatHigh] = Field(default_factory=list)

    # Next game
    next_game: ProfileNextGame | None = None

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "season_totals_regular_season": parse_result_set_by_name(
                d, "SeasonTotalsRegularSeason"
            ),
            "career_totals_regular_season": parse_single_result_set(
                d, "CareerTotalsRegularSeason"
            ),
            "season_totals_post_season": parse_result_set_by_name(
                d, "SeasonTotalsPostSeason"
            ),
            "career_totals_post_season": parse_single_result_set(
                d, "CareerTotalsPostSeason"
            ),
            "season_totals_all_star": parse_result_set_by_name(
                d, "SeasonTotalsAllStarSeason"
            ),
            "career_totals_all_star": parse_single_result_set(
                d, "CareerTotalsAllStarSeason"
            ),
            "season_totals_college": parse_result_set_by_name(
                d, "SeasonTotalsCollegeSeason"
            ),
            "career_totals_college": parse_single_result_set(
                d, "CareerTotalsCollegeSeason"
            ),
            "season_totals_preseason": parse_result_set_by_name(
                d, "SeasonTotalsPreseason"
            ),
            "career_totals_preseason": parse_single_result_set(
                d, "CareerTotalsPreseason"
            ),
            "season_rankings_regular_season": parse_result_set_by_name(
                d, "SeasonRankingsRegularSeason"
            ),
            "season_rankings_post_season": parse_result_set_by_name(
                d, "SeasonRankingsPostSeason"
            ),
            "season_highs": parse_result_set_by_name(d, "SeasonHighs"),
            "career_highs": parse_result_set_by_name(d, "CareerHighs"),
            "next_game": parse_single_result_set(d, "NextGame"),
        }
