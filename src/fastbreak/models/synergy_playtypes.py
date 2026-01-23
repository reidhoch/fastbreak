"""Models for the synergy playtypes endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class PlayerSynergyPlaytype(BaseModel):
    """Player synergy play type statistics."""

    season_id: str = Field(alias="SEASON_ID")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    play_type: str = Field(alias="PLAY_TYPE")
    type_grouping: str = Field(alias="TYPE_GROUPING")
    percentile: float = Field(alias="PERCENTILE")
    gp: int = Field(alias="GP")
    poss_pct: float = Field(alias="POSS_PCT")
    ppp: float = Field(alias="PPP")
    fg_pct: float = Field(alias="FG_PCT")
    ft_poss_pct: float = Field(alias="FT_POSS_PCT")
    tov_poss_pct: float = Field(alias="TOV_POSS_PCT")
    sf_poss_pct: float = Field(alias="SF_POSS_PCT")
    plusone_poss_pct: float = Field(alias="PLUSONE_POSS_PCT")
    score_poss_pct: float = Field(alias="SCORE_POSS_PCT")
    efg_pct: float = Field(alias="EFG_PCT")
    poss: float = Field(alias="POSS")
    pts: float = Field(alias="PTS")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fgmx: float = Field(alias="FGMX")


class TeamSynergyPlaytype(BaseModel):
    """Team synergy play type statistics."""

    season_id: str = Field(alias="SEASON_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    play_type: str = Field(alias="PLAY_TYPE")
    type_grouping: str = Field(alias="TYPE_GROUPING")
    percentile: float = Field(alias="PERCENTILE")
    gp: int = Field(alias="GP")
    poss_pct: float = Field(alias="POSS_PCT")
    ppp: float = Field(alias="PPP")
    fg_pct: float = Field(alias="FG_PCT")
    ft_poss_pct: float = Field(alias="FT_POSS_PCT")
    tov_poss_pct: float = Field(alias="TOV_POSS_PCT")
    sf_poss_pct: float = Field(alias="SF_POSS_PCT")
    plusone_poss_pct: float = Field(alias="PLUSONE_POSS_PCT")
    score_poss_pct: float = Field(alias="SCORE_POSS_PCT")
    efg_pct: float = Field(alias="EFG_PCT")
    poss: float = Field(alias="POSS")
    pts: float = Field(alias="PTS")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fgmx: float = Field(alias="FGMX")


class SynergyPlaytypesResponse(BaseModel):
    """Response from the synergy playtypes endpoint.

    Contains either player or team play type statistics depending on
    the PlayerOrTeam parameter used in the request.
    """

    player_stats: list[PlayerSynergyPlaytype] = Field(default_factory=list)
    team_stats: list[TeamSynergyPlaytype] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        if not rows:
            return {"player_stats": [], "team_stats": []}

        # Check if this is player or team data by looking for PLAYER_ID
        if "PLAYER_ID" in rows[0]:
            return {"player_stats": rows}
        return {"team_stats": rows}
