"""Models for the cumestatsplayer endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import named_result_sets_validator


class GameByGameStat(BaseModel):
    """Single game stats for a player."""

    date_est: str = Field(alias="DATE_EST")
    visitor_team: str = Field(alias="VISITOR_TEAM")
    home_team: str = Field(alias="HOME_TEAM")
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
    avg_tot_reb: float = Field(alias="AVG_TOT_REB")
    ast: int = Field(alias="AST")
    pf: int = Field(alias="PF")
    dq: int = Field(alias="DQ")
    stl: int = Field(alias="STL")
    turnovers: int = Field(alias="TURNOVERS")
    blk: int = Field(alias="BLK")
    pts: int = Field(alias="PTS")
    avg_pts: float = Field(alias="AVG_PTS")


class TotalPlayerStat(BaseModel):
    """Cumulative stats for a player across games."""

    display_fi_last: str = Field(alias="DISPLAY_FI_LAST")
    person_id: int = Field(alias="PERSON_ID")
    jersey_num: str = Field(alias="JERSEY_NUM")
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
    max_blk: int = Field(alias="MAX_BLK")
    max_pts: int = Field(alias="MAX_PTS")
    avg_actual_minutes: int = Field(alias="AVG_ACTUAL_MINUTES")
    avg_actual_seconds: float = Field(alias="AVG_ACTUAL_SECONDS")
    avg_tot_reb: float = Field(alias="AVG_TOT_REB")
    avg_ast: float = Field(alias="AVG_AST")
    avg_stl: float = Field(alias="AVG_STL")
    avg_turnovers: float = Field(alias="AVG_TURNOVERS")
    avg_blk: float = Field(alias="AVG_BLK")
    avg_pts: float = Field(alias="AVG_PTS")
    per_min_tot_reb: float = Field(alias="PER_MIN_TOT_REB")
    per_min_ast: float = Field(alias="PER_MIN_AST")
    per_min_stl: float = Field(alias="PER_MIN_STL")
    per_min_turnovers: float = Field(alias="PER_MIN_TURNOVERS")
    per_min_blk: float = Field(alias="PER_MIN_BLK")
    per_min_pts: float = Field(alias="PER_MIN_PTS")


class CumeStatsPlayerResponse(BaseModel):
    """Response from the cumestatsplayer endpoint.

    Contains two result sets:
    - game_by_game_stats: Individual game stats for the specified games
    - total_player_stats: Cumulative totals across all specified games
    """

    game_by_game_stats: list[GameByGameStat] = Field(default_factory=list)
    total_player_stats: TotalPlayerStat | None = None

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "game_by_game_stats": "GameByGameStats",
                "total_player_stats": ("TotalPlayerStats", True),
            }
        )
    )
