"""Response models for the matchupsrollup endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class MatchupRollupEntry(PandasMixin, PolarsMixin, BaseModel):
    """A matchup rollup entry showing defensive matchup statistics."""

    season_id: str = Field(alias="SEASON_ID")
    position: str = Field(alias="POSITION")
    percent_of_time: float = Field(alias="PERCENT_OF_TIME")
    def_player_id: int = Field(alias="DEF_PLAYER_ID")
    def_player_name: str = Field(alias="DEF_PLAYER_NAME")
    gp: int = Field(alias="GP")
    matchup_min: float = Field(alias="MATCHUP_MIN")
    partial_poss: float = Field(alias="PARTIAL_POSS")
    player_pts: float = Field(alias="PLAYER_PTS")
    team_pts: float = Field(alias="TEAM_PTS")
    matchup_ast: float = Field(alias="MATCHUP_AST")
    matchup_tov: float = Field(alias="MATCHUP_TOV")
    matchup_blk: float = Field(alias="MATCHUP_BLK")
    matchup_fgm: float = Field(alias="MATCHUP_FGM")
    matchup_fga: float = Field(alias="MATCHUP_FGA")
    matchup_fg_pct: float = Field(alias="MATCHUP_FG_PCT")
    matchup_fg3m: float = Field(alias="MATCHUP_FG3M")
    matchup_fg3a: float = Field(alias="MATCHUP_FG3A")
    matchup_fg3_pct: float = Field(alias="MATCHUP_FG3_PCT")
    matchup_ftm: float = Field(alias="MATCHUP_FTM")
    matchup_fta: float = Field(alias="MATCHUP_FTA")
    sfl: float = Field(alias="SFL")


class MatchupsRollupResponse(FrozenResponse):
    """Response from the matchupsrollup endpoint.

    Contains matchup statistics aggregated by defender against a specific
    offensive team.
    """

    matchups: list[MatchupRollupEntry] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("matchups"))
