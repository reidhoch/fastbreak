"""Response models for the matchupsrollup endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class MatchupRollupEntry(BaseModel):
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


class MatchupsRollupResponse(BaseModel):
    """Response from the matchupsrollup endpoint.

    Contains matchup statistics aggregated by defender against a specific
    offensive team.
    """

    matchups: list[MatchupRollupEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"matchups": rows}
