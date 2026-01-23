"""Models for the league game log endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set_by_name


class GameLogEntry(BaseModel):
    """A single game log entry from the league game log."""

    season_id: str = Field(alias="SEASON_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    matchup: str = Field(alias="MATCHUP")
    wl: str | None = Field(alias="WL")
    min: int = Field(alias="MIN")
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: int = Field(alias="FTM")
    fta: int = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: int = Field(alias="OREB")
    dreb: int = Field(alias="DREB")
    reb: int = Field(alias="REB")
    ast: int = Field(alias="AST")
    stl: int = Field(alias="STL")
    blk: int = Field(alias="BLK")
    tov: int = Field(alias="TOV")
    pf: int = Field(alias="PF")
    pts: int = Field(alias="PTS")
    plus_minus: float | None = Field(alias="PLUS_MINUS")
    video_available: int = Field(alias="VIDEO_AVAILABLE")


class LeagueGameLogResponse(BaseModel):
    """Response from the league game log endpoint.

    Contains a sorted list of game logs across the league.
    """

    games: list[GameLogEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "games": parse_result_set_by_name(
                data,
                "LeagueGameLog",
            ),
        }
