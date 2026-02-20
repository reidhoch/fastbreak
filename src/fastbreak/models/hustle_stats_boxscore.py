"""Models for the hustle stats box score endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class HustleStatsAvailable(PandasMixin, PolarsMixin, BaseModel):
    """Availability status for hustle stats."""

    game_id: str = Field(alias="GAME_ID")
    hustle_status: int = Field(alias="HUSTLE_STATUS")


class HustleStatsPlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player-level hustle statistics from a box score."""

    game_id: str = Field(alias="GAME_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_city: str = Field(alias="TEAM_CITY")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    start_position: str = Field(alias="START_POSITION")
    comment: str = Field(alias="COMMENT")
    minutes: str = Field(alias="MINUTES")
    pts: int = Field(alias="PTS")
    contested_shots: float = Field(alias="CONTESTED_SHOTS")
    contested_shots_2pt: float = Field(alias="CONTESTED_SHOTS_2PT")
    contested_shots_3pt: float = Field(alias="CONTESTED_SHOTS_3PT")
    deflections: float = Field(alias="DEFLECTIONS")
    charges_drawn: float = Field(alias="CHARGES_DRAWN")
    screen_assists: float = Field(alias="SCREEN_ASSISTS")
    screen_ast_pts: float = Field(alias="SCREEN_AST_PTS")
    off_loose_balls_recovered: float = Field(alias="OFF_LOOSE_BALLS_RECOVERED")
    def_loose_balls_recovered: float = Field(alias="DEF_LOOSE_BALLS_RECOVERED")
    loose_balls_recovered: float = Field(alias="LOOSE_BALLS_RECOVERED")
    off_boxouts: float = Field(alias="OFF_BOXOUTS")
    def_boxouts: float = Field(alias="DEF_BOXOUTS")
    box_out_player_team_rebs: float = Field(alias="BOX_OUT_PLAYER_TEAM_REBS")
    box_out_player_rebs: float = Field(alias="BOX_OUT_PLAYER_REBS")
    box_outs: float = Field(alias="BOX_OUTS")


class HustleStatsTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team-level hustle statistics from a box score."""

    game_id: str = Field(alias="GAME_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_city: str = Field(alias="TEAM_CITY")
    minutes: str = Field(alias="MINUTES")
    pts: int = Field(alias="PTS")
    contested_shots: float = Field(alias="CONTESTED_SHOTS")
    contested_shots_2pt: float = Field(alias="CONTESTED_SHOTS_2PT")
    contested_shots_3pt: float = Field(alias="CONTESTED_SHOTS_3PT")
    deflections: float = Field(alias="DEFLECTIONS")
    charges_drawn: float = Field(alias="CHARGES_DRAWN")
    screen_assists: float = Field(alias="SCREEN_ASSISTS")
    screen_ast_pts: float = Field(alias="SCREEN_AST_PTS")
    off_loose_balls_recovered: float = Field(alias="OFF_LOOSE_BALLS_RECOVERED")
    def_loose_balls_recovered: float = Field(alias="DEF_LOOSE_BALLS_RECOVERED")
    loose_balls_recovered: float = Field(alias="LOOSE_BALLS_RECOVERED")
    off_boxouts: float = Field(alias="OFF_BOXOUTS")
    def_boxouts: float = Field(alias="DEF_BOXOUTS")
    box_out_player_team_rebs: float = Field(alias="BOX_OUT_PLAYER_TEAM_REBS")
    box_out_player_rebs: float = Field(alias="BOX_OUT_PLAYER_REBS")
    box_outs: float = Field(alias="BOX_OUTS")


class HustleStatsBoxscoreResponse(FrozenResponse):
    """Response from the hustle stats box score endpoint.

    Contains availability status, player-level hustle stats, and team-level
    hustle stats for a given game.
    """

    hustle_stats_available: list[HustleStatsAvailable] = Field(default_factory=list)
    player_stats: list[HustleStatsPlayer] = Field(default_factory=list)
    team_stats: list[HustleStatsTeam] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "hustle_stats_available": "HustleStatsAvailable",
                "player_stats": "PlayerStats",
                "team_stats": "TeamStats",
            }
        )
    )
