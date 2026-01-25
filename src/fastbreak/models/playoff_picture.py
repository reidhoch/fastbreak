"""Models for the playoff picture endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class PlayoffMatchup(BaseModel):
    """A playoff series matchup between two teams."""

    conference: str | None = Field(default=None, alias="CONFERENCE")
    high_seed_rank: int | None = Field(default=None, alias="HIGH_SEED_RANK")
    high_seed_team: str | None = Field(default=None, alias="HIGH_SEED_TEAM")
    high_seed_team_id: int | None = Field(default=None, alias="HIGH_SEED_TEAM_ID")
    low_seed_rank: int | None = Field(default=None, alias="LOW_SEED_RANK")
    low_seed_team: str | None = Field(default=None, alias="LOW_SEED_TEAM")
    low_seed_team_id: int | None = Field(default=None, alias="LOW_SEED_TEAM_ID")
    high_seed_series_w: int | None = Field(default=None, alias="HIGH_SEED_SERIES_W")
    high_seed_series_l: int | None = Field(default=None, alias="HIGH_SEED_SERIES_L")
    high_seed_series_remaining_g: int | None = Field(
        default=None, alias="HIGH_SEED_SERIES_REMAINING_G"
    )
    high_seed_series_remaining_home_g: int | None = Field(
        default=None, alias="HIGH_SEED_SERIES_REMAINING_HOME_G"
    )
    high_seed_series_remaining_away_g: int | None = Field(
        default=None, alias="HIGH_SEED_SERIES_REMAINING_AWAY_G"
    )


class PlayoffStanding(BaseModel):
    """Team standing in playoff picture context."""

    conference: str | None = Field(default=None, alias="CONFERENCE")
    rank: int | None = Field(default=None, alias="RANK")
    team: str | None = Field(default=None, alias="TEAM")
    team_slug: str | None = Field(default=None, alias="TEAM_SLUG")
    team_id: int | None = Field(default=None, alias="TEAM_ID")
    wins: int | None = Field(default=None, alias="WINS")
    losses: int | None = Field(default=None, alias="LOSSES")
    pct: float | None = Field(default=None, alias="PCT")
    div: str | None = Field(default=None, alias="DIV")
    conf: str | None = Field(default=None, alias="CONF")
    home: str | None = Field(default=None, alias="HOME")
    away: str | None = Field(default=None, alias="AWAY")
    gb: float | None = Field(default=None, alias="GB")
    gr_over_500: int | None = Field(default=None, alias="GR_OVER_500")
    gr_over_500_home: int | None = Field(default=None, alias="GR_OVER_500_HOME")
    gr_over_500_away: int | None = Field(default=None, alias="GR_OVER_500_AWAY")
    gr_under_500: int | None = Field(default=None, alias="GR_UNDER_500")
    gr_under_500_home: int | None = Field(default=None, alias="GR_UNDER_500_HOME")
    gr_under_500_away: int | None = Field(default=None, alias="GR_UNDER_500_AWAY")
    ranking_criteria: int | None = Field(default=None, alias="RANKING_CRITERIA")
    clinched_playoffs: int | None = Field(default=None, alias="CLINCHED_PLAYOFFS")
    clinched_conference: int | None = Field(default=None, alias="CLINCHED_CONFERENCE")
    clinched_division: int | None = Field(default=None, alias="CLINCHED_DIVISION")
    eliminated_playoffs: int | None = Field(default=None, alias="ELIMINATED_PLAYOFFS")
    sosa_remaining: int | None = Field(default=None, alias="SOSA_REMAINING")


class RemainingGames(BaseModel):
    """Remaining games for a team."""

    team: str | None = Field(default=None, alias="TEAM")
    team_id: int | None = Field(default=None, alias="TEAM_ID")
    remaining_g: int | None = Field(default=None, alias="REMAINING_G")
    remaining_home_g: int | None = Field(default=None, alias="REMAINING_HOME_G")
    remaining_away_g: int | None = Field(default=None, alias="REMAINING_AWAY_G")


class PlayoffPictureResponse(BaseModel):
    """Response from the playoff picture endpoint.

    Contains result sets for both conferences:
    - east_conf_playoff_picture: Current playoff matchups in the East
    - west_conf_playoff_picture: Current playoff matchups in the West
    - east_conf_standings: Full Eastern Conference standings with clinch status
    - west_conf_standings: Full Western Conference standings with clinch status
    - east_conf_remaining_games: Remaining games for East teams
    - west_conf_remaining_games: Remaining games for West teams
    """

    east_conf_playoff_picture: list[PlayoffMatchup] = Field(default_factory=list)
    west_conf_playoff_picture: list[PlayoffMatchup] = Field(default_factory=list)
    east_conf_standings: list[PlayoffStanding] = Field(default_factory=list)
    west_conf_standings: list[PlayoffStanding] = Field(default_factory=list)
    east_conf_remaining_games: list[RemainingGames] = Field(default_factory=list)
    west_conf_remaining_games: list[RemainingGames] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "east_conf_playoff_picture": parse_result_set_by_name(
                data,
                "EastConfPlayoffPicture",
            ),
            "west_conf_playoff_picture": parse_result_set_by_name(
                data,
                "WestConfPlayoffPicture",
            ),
            "east_conf_standings": parse_result_set_by_name(
                data,
                "EastConfStandings",
            ),
            "west_conf_standings": parse_result_set_by_name(
                data,
                "WestConfStandings",
            ),
            "east_conf_remaining_games": parse_result_set_by_name(
                data,
                "EastConfRemainingGames",
            ),
            "west_conf_remaining_games": parse_result_set_by_name(
                data,
                "WestConfRemainingGames",
            ),
        }
