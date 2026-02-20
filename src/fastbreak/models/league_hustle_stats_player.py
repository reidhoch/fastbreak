"""Models for the league hustle stats player endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class LeagueHustlePlayer(PandasMixin, PolarsMixin, BaseModel):
    """Season-aggregated hustle statistics for a player."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    age: float | None = Field(alias="AGE")
    g: int = Field(alias="G")
    min: float = Field(alias="MIN")
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
    pct_loose_balls_recovered_off: float | None = Field(
        alias="PCT_LOOSE_BALLS_RECOVERED_OFF"
    )
    pct_loose_balls_recovered_def: float | None = Field(
        alias="PCT_LOOSE_BALLS_RECOVERED_DEF"
    )
    off_boxouts: float = Field(alias="OFF_BOXOUTS")
    def_boxouts: float = Field(alias="DEF_BOXOUTS")
    box_outs: float = Field(alias="BOX_OUTS")
    box_out_player_team_rebs: float = Field(alias="BOX_OUT_PLAYER_TEAM_REBS")
    box_out_player_rebs: float = Field(alias="BOX_OUT_PLAYER_REBS")
    pct_box_outs_off: float | None = Field(alias="PCT_BOX_OUTS_OFF")
    pct_box_outs_def: float | None = Field(alias="PCT_BOX_OUTS_DEF")
    pct_box_outs_team_reb: float | None = Field(alias="PCT_BOX_OUTS_TEAM_REB")
    pct_box_outs_reb: float | None = Field(alias="PCT_BOX_OUTS_REB")


class LeagueHustleStatsPlayerResponse(FrozenResponse):
    """Response from the league hustle stats player endpoint.

    Contains season-aggregated hustle statistics for all players.
    """

    players: list[LeagueHustlePlayer] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"players": "HustleStatsPlayer"})
    )
