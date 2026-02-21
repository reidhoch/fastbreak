"""Models for the homepage v2 endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class HomePageStatPlayer(PandasMixin, PolarsMixin, BaseModel):
    """A player entry in homepage stats."""

    rank: int = Field(alias="RANK")
    player_id: int = Field(alias="PLAYER_ID")
    player: str = Field(alias="PLAYER")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    jersey_num: str = Field(alias="JERSEY_NUM")
    player_position: str = Field(alias="PLAYER_POSITION")


class HomePageStatPts(HomePageStatPlayer):
    """Points leaders entry."""

    pts: float = Field(alias="PTS")


class HomePageStatReb(HomePageStatPlayer):
    """Rebounds leaders entry."""

    reb: float = Field(alias="REB")


class HomePageStatAst(HomePageStatPlayer):
    """Assists leaders entry."""

    ast: float = Field(alias="AST")


class HomePageStatBlk(HomePageStatPlayer):
    """Blocks leaders entry."""

    blk: float = Field(alias="BLK")


class HomePageStatStl(HomePageStatPlayer):
    """Steals leaders entry."""

    stl: float = Field(alias="STL")


class HomePageStatFg3Pct(HomePageStatPlayer):
    """Three-point percentage leaders entry."""

    fg3_pct: float = Field(alias="FG3_PCT")


class HomepageV2Response(FrozenResponse):
    """Response from the homepage v2 endpoint.

    Contains top 5 leaders for multiple statistical categories including
    points, rebounds, assists, blocks, steals, and three-point percentage.
    """

    # Each stat category is a separate result set
    pts_leaders: list[HomePageStatPts] = Field(default_factory=list)
    reb_leaders: list[HomePageStatReb] = Field(default_factory=list)
    ast_leaders: list[HomePageStatAst] = Field(default_factory=list)
    blk_leaders: list[HomePageStatBlk] = Field(default_factory=list)
    stl_leaders: list[HomePageStatStl] = Field(default_factory=list)
    fg3_pct_leaders: list[HomePageStatFg3Pct] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "pts_leaders": "HomePageStat1",
                "reb_leaders": "HomePageStat2",
                "ast_leaders": "HomePageStat3",
                "blk_leaders": "HomePageStat4",
                "stl_leaders": "HomePageStat5",
                "fg3_pct_leaders": "HomePageStat6",
            },
            ignore_missing=True,
        )
    )
