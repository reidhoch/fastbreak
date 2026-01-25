"""Models for the league season matchups endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class SeasonMatchup(BaseModel):
    """A player-vs-player matchup statistics entry."""

    season_id: str = Field(alias="SEASON_ID")
    off_player_id: int = Field(alias="OFF_PLAYER_ID")
    off_player_name: str = Field(alias="OFF_PLAYER_NAME")
    def_player_id: int = Field(alias="DEF_PLAYER_ID")
    def_player_name: str = Field(alias="DEF_PLAYER_NAME")

    # Games and time
    gp: int = Field(alias="GP")
    matchup_min: float = Field(alias="MATCHUP_MIN")
    partial_poss: float = Field(alias="PARTIAL_POSS")

    # Scoring
    player_pts: float = Field(alias="PLAYER_PTS")
    team_pts: float = Field(alias="TEAM_PTS")

    # Matchup stats
    matchup_ast: float = Field(alias="MATCHUP_AST")
    matchup_tov: float = Field(alias="MATCHUP_TOV")
    matchup_blk: float = Field(alias="MATCHUP_BLK")
    matchup_fgm: float = Field(alias="MATCHUP_FGM")
    matchup_fga: float = Field(alias="MATCHUP_FGA")
    matchup_fg_pct: float | None = Field(default=None, alias="MATCHUP_FG_PCT")
    matchup_fg3m: float = Field(alias="MATCHUP_FG3M")
    matchup_fg3a: float = Field(alias="MATCHUP_FG3A")
    matchup_fg3_pct: float | None = Field(default=None, alias="MATCHUP_FG3_PCT")
    matchup_ftm: float = Field(alias="MATCHUP_FTM")
    matchup_fta: float = Field(alias="MATCHUP_FTA")

    # Help defense
    help_blk: float = Field(alias="HELP_BLK")
    help_fgm: float = Field(alias="HELP_FGM")
    help_fga: float = Field(alias="HELP_FGA")
    help_fg_pct: float | None = Field(default=None, alias="HELP_FG_PERC")

    # Shooting fouls drawn
    sfl: float = Field(alias="SFL")


class LeagueSeasonMatchupsResponse(BaseModel):
    """Response from the league season matchups endpoint.

    Contains player-vs-player matchup statistics for the season.
    """

    matchups: list[SeasonMatchup] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "matchups": parse_result_set_by_name(
                data,
                "SeasonMatchups",
            ),
        }
