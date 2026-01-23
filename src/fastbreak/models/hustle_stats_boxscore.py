"""Models for the hustle stats box score endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set_by_name


class HustleStatsAvailable(BaseModel):
    """Availability status for hustle stats."""

    game_id: str = Field(alias="GAME_ID")
    hustle_status: int = Field(alias="HUSTLE_STATUS")


class HustleStatsPlayer(BaseModel):
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


class HustleStatsTeam(BaseModel):
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


class HustleStatsBoxscoreResponse(BaseModel):
    """Response from the hustle stats box score endpoint.

    Contains availability status, player-level hustle stats, and team-level
    hustle stats for a given game.
    """

    hustle_stats_available: list[HustleStatsAvailable] = Field(default_factory=list)
    player_stats: list[HustleStatsPlayer] = Field(default_factory=list)
    team_stats: list[HustleStatsTeam] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "hustle_stats_available": parse_result_set_by_name(
                data,
                "HustleStatsAvailable",
            ),
            "player_stats": parse_result_set_by_name(
                data,
                "PlayerStats",
            ),
            "team_stats": parse_result_set_by_name(
                data,
                "TeamStats",
            ),
        }
