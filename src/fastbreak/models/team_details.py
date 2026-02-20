"""Models for the Team Details endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class TeamBackground(PandasMixin, PolarsMixin, BaseModel):
    """Basic team background information."""

    team_id: int = Field(alias="TEAM_ID")
    abbreviation: str = Field(alias="ABBREVIATION")
    nickname: str = Field(alias="NICKNAME")
    year_founded: int = Field(alias="YEARFOUNDED")
    city: str = Field(alias="CITY")
    arena: str | None = Field(alias="ARENA")
    arena_capacity: int | None = Field(alias="ARENACAPACITY")
    owner: str | None = Field(alias="OWNER")
    general_manager: str | None = Field(alias="GENERALMANAGER")
    head_coach: str | None = Field(alias="HEADCOACH")
    d_league_affiliation: str | None = Field(alias="DLEAGUEAFFILIATION")


class TeamHistory(PandasMixin, PolarsMixin, BaseModel):
    """Team history entry for franchise moves/name changes."""

    team_id: int = Field(alias="TEAM_ID")
    city: str = Field(alias="CITY")
    nickname: str = Field(alias="NICKNAME")
    year_founded: int = Field(alias="YEARFOUNDED")
    year_active_till: int = Field(alias="YEARACTIVETILL")


class TeamSocialSite(PandasMixin, PolarsMixin, BaseModel):
    """Team social media link."""

    account_type: str = Field(alias="ACCOUNTTYPE")
    website_link: str = Field(alias="WEBSITE_LINK")


class TeamAward(PandasMixin, PolarsMixin, BaseModel):
    """Team championship/award entry."""

    year_awarded: int = Field(alias="YEARAWARDED")
    opposite_team: str | None = Field(alias="OPPOSITETEAM")


class TeamHofPlayer(PandasMixin, PolarsMixin, BaseModel):
    """Hall of Fame player associated with the team."""

    player_id: int = Field(alias="PLAYERID")
    player: str = Field(alias="PLAYER")
    position: str | None = Field(alias="POSITION")
    jersey: str | None = Field(alias="JERSEY")
    seasons_with_team: str | None = Field(alias="SEASONSWITHTEAM")
    year: int = Field(alias="YEAR")


class TeamRetiredJersey(PandasMixin, PolarsMixin, BaseModel):
    """Retired jersey entry."""

    # player_id can be None for non-players (broadcasters, coaches, owners)
    player_id: int | None = Field(default=None, alias="PLAYERID")
    player: str = Field(alias="PLAYER")
    position: str | None = Field(alias="POSITION")
    jersey: str | None = Field(alias="JERSEY")
    seasons_with_team: str | None = Field(alias="SEASONSWITHTEAM")
    # year can be None for honorary jersey retirements
    year: int | None = Field(default=None, alias="YEAR")


class TeamDetailsResponse(FrozenResponse):
    """Response from the team details endpoint.

    Contains comprehensive team information including background,
    history, social media, awards, and notable players.
    """

    background: TeamBackground | None = None
    history: list[TeamHistory] = Field(default_factory=list)
    social_sites: list[TeamSocialSite] = Field(default_factory=list)
    championships: list[TeamAward] = Field(default_factory=list)
    conference_titles: list[TeamAward] = Field(default_factory=list)
    division_titles: list[TeamAward] = Field(default_factory=list)
    hall_of_fame: list[TeamHofPlayer] = Field(default_factory=list)
    retired_jerseys: list[TeamRetiredJersey] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "background": ("TeamBackground", True),
                "history": "TeamHistory",
                "social_sites": "TeamSocialSites",
                "championships": "TeamAwardsChampionships",
                "conference_titles": "TeamAwardsConf",
                "division_titles": "TeamAwardsDiv",
                "hall_of_fame": "TeamHof",
                "retired_jerseys": "TeamRetired",
            }
        )
    )
