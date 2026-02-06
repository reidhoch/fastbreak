"""Response models for the playercareerstats endpoint."""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class SeasonTotals(PandasMixin, PolarsMixin, BaseModel):
    """Season totals for a player (regular season, playoffs, all-star)."""

    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    player_age: float = Field(alias="PLAYER_AGE")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class CareerTotals(PandasMixin, PolarsMixin, BaseModel):
    """Career totals for a player."""

    player_id: int = Field(alias="PLAYER_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class CollegeSeasonTotals(PandasMixin, PolarsMixin, BaseModel):
    """College season totals for a player."""

    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    organization_id: int = Field(alias="ORGANIZATION_ID")
    school_name: str = Field(alias="SCHOOL_NAME")
    player_age: float = Field(alias="PLAYER_AGE")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class CollegeCareerTotals(PandasMixin, PolarsMixin, BaseModel):
    """College career totals for a player."""

    player_id: int = Field(alias="PLAYER_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    organization_id: int = Field(alias="ORGANIZATION_ID")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    pf: float = Field(alias="PF")
    pts: float = Field(alias="PTS")


class SeasonRankings(PandasMixin, PolarsMixin, BaseModel):
    """Season rankings for a player's stats.

    Note: The NBA API returns "NR" (Not Ranked) for player_age, gp, and gs
    in some seasons. Rank fields return null when player didn't qualify.
    """

    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    player_age: float | None = Field(alias="PLAYER_AGE")
    gp: int | None = Field(alias="GP")
    gs: int | None = Field(alias="GS")
    rank_min: int | None = Field(alias="RANK_PG_MIN")
    rank_fgm: int | None = Field(alias="RANK_PG_FGM")
    rank_fga: int | None = Field(alias="RANK_PG_FGA")
    rank_fg_pct: int | None = Field(alias="RANK_FG_PCT")
    rank_fg3m: int | None = Field(alias="RANK_PG_FG3M")
    rank_fg3a: int | None = Field(alias="RANK_PG_FG3A")
    rank_fg3_pct: int | None = Field(alias="RANK_FG3_PCT")
    rank_ftm: int | None = Field(alias="RANK_PG_FTM")
    rank_fta: int | None = Field(alias="RANK_PG_FTA")
    rank_ft_pct: int | None = Field(alias="RANK_FT_PCT")
    rank_oreb: int | None = Field(alias="RANK_PG_OREB")
    rank_dreb: int | None = Field(alias="RANK_PG_DREB")
    rank_reb: int | None = Field(alias="RANK_PG_REB")
    rank_ast: int | None = Field(alias="RANK_PG_AST")
    rank_stl: int | None = Field(alias="RANK_PG_STL")
    rank_blk: int | None = Field(alias="RANK_PG_BLK")
    rank_tov: int | None = Field(alias="RANK_PG_TOV")
    rank_pts: int | None = Field(alias="RANK_PG_PTS")
    rank_eff: int | None = Field(alias="RANK_PG_EFF")

    @field_validator("player_age", "gp", "gs", mode="before")
    @classmethod
    def coerce_nr_to_none(cls, v: str | int | None) -> int | None:
        """Coerce 'NR' (Not Ranked) strings to None."""
        if v == "NR":
            return None
        return v  # type: ignore[return-value]


class StatHigh(PandasMixin, PolarsMixin, BaseModel):
    """A single stat high (season or career)."""

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


class PlayerCareerStatsResponse(FrozenResponse):
    """Response from the playercareerstats endpoint.

    Contains comprehensive career statistics including season-by-season data,
    career totals, rankings, and stat highs across regular season, playoffs,
    all-star games, college, and showcase seasons.
    """

    season_totals_regular_season: list[SeasonTotals] = Field(default_factory=list)
    career_totals_regular_season: list[CareerTotals] = Field(default_factory=list)
    season_totals_post_season: list[SeasonTotals] = Field(default_factory=list)
    career_totals_post_season: list[CareerTotals] = Field(default_factory=list)
    season_totals_all_star: list[SeasonTotals] = Field(default_factory=list)
    career_totals_all_star: list[CareerTotals] = Field(default_factory=list)
    season_totals_college: list[CollegeSeasonTotals] = Field(default_factory=list)
    career_totals_college: list[CollegeCareerTotals] = Field(default_factory=list)
    season_totals_showcase: list[SeasonTotals] = Field(default_factory=list)
    career_totals_showcase: list[CareerTotals] = Field(default_factory=list)
    season_rankings_regular_season: list[SeasonRankings] = Field(default_factory=list)
    season_rankings_post_season: list[SeasonRankings] = Field(default_factory=list)
    season_highs: list[StatHigh] = Field(default_factory=list)
    career_highs: list[StatHigh] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "season_totals_regular_season": parse_result_set_by_name(
                data,
                "SeasonTotalsRegularSeason",
            ),
            "career_totals_regular_season": parse_result_set_by_name(
                data,
                "CareerTotalsRegularSeason",
            ),
            "season_totals_post_season": parse_result_set_by_name(
                data,
                "SeasonTotalsPostSeason",
            ),
            "career_totals_post_season": parse_result_set_by_name(
                data,
                "CareerTotalsPostSeason",
            ),
            "season_totals_all_star": parse_result_set_by_name(
                data,
                "SeasonTotalsAllStarSeason",
            ),
            "career_totals_all_star": parse_result_set_by_name(
                data,
                "CareerTotalsAllStarSeason",
            ),
            "season_totals_college": parse_result_set_by_name(
                data,
                "SeasonTotalsCollegeSeason",
            ),
            "career_totals_college": parse_result_set_by_name(
                data,
                "CareerTotalsCollegeSeason",
            ),
            "season_totals_showcase": parse_result_set_by_name(
                data,
                "SeasonTotalsShowcaseSeason",
            ),
            "career_totals_showcase": parse_result_set_by_name(
                data,
                "CareerTotalsShowcaseSeason",
            ),
            "season_rankings_regular_season": parse_result_set_by_name(
                data,
                "SeasonRankingsRegularSeason",
            ),
            "season_rankings_post_season": parse_result_set_by_name(
                data,
                "SeasonRankingsPostSeason",
            ),
            "season_highs": parse_result_set_by_name(
                data,
                "SeasonHighs",
            ),
            "career_highs": parse_result_set_by_name(
                data,
                "CareerHighs",
            ),
        }
