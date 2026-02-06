"""Models for the franchise history endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class Franchise(PandasMixin, PolarsMixin, BaseModel):
    """A franchise history entry.

    Represents either an active franchise or a defunct team,
    including historical records across different city/name combinations.
    """

    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_city: str = Field(alias="TEAM_CITY")
    team_name: str = Field(alias="TEAM_NAME")
    start_year: str = Field(alias="START_YEAR")
    end_year: str = Field(alias="END_YEAR")
    years: int = Field(alias="YEARS")
    games: int = Field(alias="GAMES")
    wins: int = Field(alias="WINS")
    losses: int = Field(alias="LOSSES")
    win_pct: float = Field(alias="WIN_PCT")
    po_appearances: int = Field(alias="PO_APPEARANCES")
    div_titles: int = Field(alias="DIV_TITLES")
    conf_titles: int = Field(alias="CONF_TITLES")
    league_titles: int = Field(alias="LEAGUE_TITLES")


class FranchiseHistoryResponse(FrozenResponse):
    """Response from the franchise history endpoint.

    Contains two lists:
    - franchise_history: Active NBA franchises with their historical records
    - defunct_teams: Teams that no longer exist in the NBA
    """

    franchise_history: list[Franchise] = Field(default_factory=list)
    defunct_teams: list[Franchise] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "franchise_history": "FranchiseHistory",
                "defunct_teams": "DefunctTeams",
            }
        )
    )
