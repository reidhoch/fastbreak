"""Models for the cumestatsteam endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class TeamPlayerStat(PandasMixin, PolarsMixin, BaseModel):
    """Per-player stats for a team across specified games."""

    jersey_num: str = Field(alias="JERSEY_NUM")
    player: str = Field(alias="PLAYER")
    person_id: int = Field(alias="PERSON_ID")
    team_id: int = Field(alias="TEAM_ID")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    actual_minutes: int = Field(alias="ACTUAL_MINUTES")
    actual_seconds: int = Field(alias="ACTUAL_SECONDS")
    fg: int = Field(alias="FG")
    fga: int = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3: int = Field(alias="FG3")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ft: int = Field(alias="FT")
    fta: int = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    off_reb: int = Field(alias="OFF_REB")
    def_reb: int = Field(alias="DEF_REB")
    tot_reb: int = Field(alias="TOT_REB")
    ast: int = Field(alias="AST")
    pf: int = Field(alias="PF")
    dq: int = Field(alias="DQ")
    stl: int = Field(alias="STL")
    turnovers: int = Field(alias="TURNOVERS")
    blk: int = Field(alias="BLK")
    pts: int = Field(alias="PTS")
    max_actual_minutes: int = Field(alias="MAX_ACTUAL_MINUTES")
    max_actual_seconds: int = Field(alias="MAX_ACTUAL_SECONDS")
    max_reb: int = Field(alias="MAX_REB")
    max_ast: int = Field(alias="MAX_AST")
    max_stl: int = Field(alias="MAX_STL")
    max_turnovers: int = Field(alias="MAX_TURNOVERS")
    max_blkp: int = Field(alias="MAX_BLKP")
    max_pts: int = Field(alias="MAX_PTS")
    avg_actual_minutes: float = Field(alias="AVG_ACTUAL_MINUTES")
    avg_actual_seconds: float = Field(alias="AVG_ACTUAL_SECONDS")
    avg_reb: float = Field(alias="AVG_REB")
    avg_ast: float = Field(alias="AVG_AST")
    avg_stl: float = Field(alias="AVG_STL")
    avg_turnovers: float = Field(alias="AVG_TURNOVERS")
    avg_blkp: float = Field(alias="AVG_BLKP")
    avg_pts: float = Field(alias="AVG_PTS")
    per_min_reb: float = Field(alias="PER_MIN_REB")
    per_min_ast: float = Field(alias="PER_MIN_AST")
    per_min_stl: float = Field(alias="PER_MIN_STL")
    per_min_turnovers: float = Field(alias="PER_MIN_TURNOVERS")
    per_min_blk: float = Field(alias="PER_MIN_BLK")
    per_min_pts: float = Field(alias="PER_MIN_PTS")


class TotalTeamStat(PandasMixin, PolarsMixin, BaseModel):
    """Aggregate team stats across specified games."""

    city: str = Field(alias="CITY")
    nickname: str = Field(alias="NICKNAME")
    team_id: int = Field(alias="TEAM_ID")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    w_home: int = Field(alias="W_HOME")
    losses_home: int = Field(alias="L_HOME")
    w_road: int = Field(alias="W_ROAD")
    losses_road: int = Field(alias="L_ROAD")
    team_turnovers: int = Field(alias="TEAM_TURNOVERS")
    team_rebounds: int = Field(alias="TEAM_REBOUNDS")
    gp: int = Field(alias="GP")
    gs: int = Field(alias="GS")
    actual_minutes: int = Field(alias="ACTUAL_MINUTES")
    actual_seconds: int = Field(alias="ACTUAL_SECONDS")
    fg: int = Field(alias="FG")
    fga: int = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3: int = Field(alias="FG3")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ft: int = Field(alias="FT")
    fta: int = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    off_reb: int = Field(alias="OFF_REB")
    def_reb: int = Field(alias="DEF_REB")
    tot_reb: int = Field(alias="TOT_REB")
    ast: int = Field(alias="AST")
    pf: int = Field(alias="PF")
    stl: int = Field(alias="STL")
    total_turnovers: int = Field(alias="TOTAL_TURNOVERS")
    blk: int = Field(alias="BLK")
    pts: int = Field(alias="PTS")
    avg_reb: float = Field(alias="AVG_REB")
    avg_pts: float = Field(alias="AVG_PTS")
    dq: int = Field(alias="DQ")


class CumeStatsTeamResponse(FrozenResponse):
    """Response from the cumestatsteam endpoint.

    Contains two result sets:
    - game_by_game_stats: Per-player stats for the team
    - total_team_stats: Aggregate team totals
    """

    game_by_game_stats: list[TeamPlayerStat] = Field(default_factory=list)
    total_team_stats: TotalTeamStat | None = None

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "game_by_game_stats": "GameByGameStats",
                "total_team_stats": ("TotalTeamStats", True),
            }
        )
    )
