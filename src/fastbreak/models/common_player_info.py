"""Models for the common player info endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import named_result_sets_validator


class PlayerInfo(BaseModel):
    """Detailed player information from CommonPlayerInfo result set."""

    person_id: int = Field(alias="PERSON_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    display_first_last: str = Field(alias="DISPLAY_FIRST_LAST")
    display_last_comma_first: str = Field(alias="DISPLAY_LAST_COMMA_FIRST")
    display_fi_last: str = Field(alias="DISPLAY_FI_LAST")
    player_slug: str = Field(alias="PLAYER_SLUG")
    birthdate: str = Field(alias="BIRTHDATE")
    school: str = Field(alias="SCHOOL")
    country: str = Field(alias="COUNTRY")
    last_affiliation: str = Field(alias="LAST_AFFILIATION")
    height: str = Field(alias="HEIGHT")
    weight: str = Field(alias="WEIGHT")
    season_exp: int = Field(alias="SEASON_EXP")
    jersey: str = Field(alias="JERSEY")
    position: str = Field(alias="POSITION")
    roster_status: str = Field(alias="ROSTERSTATUS")
    games_played_current_season_flag: str = Field(
        alias="GAMES_PLAYED_CURRENT_SEASON_FLAG"
    )
    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_code: str = Field(alias="TEAM_CODE")
    team_city: str = Field(alias="TEAM_CITY")
    player_code: str = Field(alias="PLAYERCODE")
    from_year: int = Field(alias="FROM_YEAR")
    to_year: int = Field(alias="TO_YEAR")
    dleague_flag: str = Field(alias="DLEAGUE_FLAG")
    nba_flag: str = Field(alias="NBA_FLAG")
    games_played_flag: str = Field(alias="GAMES_PLAYED_FLAG")
    draft_year: str = Field(alias="DRAFT_YEAR")
    draft_round: str = Field(alias="DRAFT_ROUND")
    draft_number: str = Field(alias="DRAFT_NUMBER")
    greatest_75_flag: str = Field(alias="GREATEST_75_FLAG")


class PlayerHeadlineStats(BaseModel):
    """Headline stats from PlayerHeadlineStats result set."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    time_frame: str = Field(alias="TimeFrame")
    pts: float = Field(alias="PTS")
    ast: float = Field(alias="AST")
    reb: float = Field(alias="REB")
    pie: float = Field(alias="PIE")


class AvailableSeason(BaseModel):
    """A season available for a player from AvailableSeasons result set."""

    season_id: str = Field(alias="SEASON_ID")


class CommonPlayerInfoResponse(BaseModel):
    """Response from the common player info endpoint.

    Contains three result sets:
    - player_info: Detailed player biographical and team information
    - headline_stats: Current season summary stats
    - available_seasons: List of seasons the player has data for
    """

    player_info: PlayerInfo | None = None
    headline_stats: PlayerHeadlineStats | None = None
    available_seasons: list[AvailableSeason] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "player_info": ("CommonPlayerInfo", True),
                "headline_stats": ("PlayerHeadlineStats", True),
                "available_seasons": ("AvailableSeasons", False),
            }
        )
    )
