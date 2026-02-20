"""Models for the Team Info Common endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class TeamInfoCommon(PandasMixin, PolarsMixin, BaseModel):
    """Basic team information including current standings.

    Contains team identity, conference/division, and win-loss record.
    """

    team_id: int = Field(alias="TEAM_ID")
    season_year: str = Field(alias="SEASON_YEAR")
    team_city: str = Field(alias="TEAM_CITY")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_conference: str = Field(alias="TEAM_CONFERENCE")
    team_division: str = Field(alias="TEAM_DIVISION")
    team_code: str = Field(alias="TEAM_CODE")
    team_slug: str = Field(alias="TEAM_SLUG")
    wins: int = Field(alias="W")
    losses: int = Field(alias="L")
    win_pct: float = Field(alias="PCT")
    conf_rank: int = Field(alias="CONF_RANK")
    div_rank: int = Field(alias="DIV_RANK")
    min_year: str = Field(alias="MIN_YEAR")
    max_year: str = Field(alias="MAX_YEAR")


class TeamSeasonRanks(PandasMixin, PolarsMixin, BaseModel):
    """Team's current season rankings in key statistics.

    Contains per-game averages and league rankings for points, rebounds, and assists.
    """

    league_id: str = Field(alias="LEAGUE_ID")
    season_id: str = Field(alias="SEASON_ID")
    team_id: int = Field(alias="TEAM_ID")
    pts_rank: int = Field(alias="PTS_RANK")
    pts_pg: float = Field(alias="PTS_PG")
    reb_rank: int = Field(alias="REB_RANK")
    reb_pg: float = Field(alias="REB_PG")
    ast_rank: int = Field(alias="AST_RANK")
    ast_pg: float = Field(alias="AST_PG")
    opp_pts_rank: int = Field(alias="OPP_PTS_RANK")
    opp_pts_pg: float = Field(alias="OPP_PTS_PG")


class AvailableSeason(PandasMixin, PolarsMixin, BaseModel):
    """A season available for the team's history."""

    season_id: str = Field(alias="SEASON_ID")


class TeamInfoCommonResponse(FrozenResponse):
    """Response from the team info common endpoint.

    Contains basic team information, season rankings, and available seasons.
    """

    team_info: TeamInfoCommon | None = Field(default=None)
    season_ranks: TeamSeasonRanks | None = Field(default=None)
    available_seasons: list[AvailableSeason] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "team_info": ("TeamInfoCommon", True),
                "season_ranks": ("TeamSeasonRanks", True),
                "available_seasons": "AvailableSeasons",
            }
        )
    )
