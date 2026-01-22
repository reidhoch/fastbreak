"""Endpoint for fetching NBA draft history."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.draft_history import DraftHistoryResponse


@dataclass(frozen=True)
class DraftHistory(Endpoint[DraftHistoryResponse]):
    """Fetch NBA draft history.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season year to filter by (e.g., "2024" for 2024 draft)
        team_id: Team identifier to filter by (optional)
        round_num: Round number to filter by (optional)
        round_pick: Pick within round to filter by (optional)
        overall_pick: Overall pick number to filter by (optional)
        college: College/organization to filter by (optional)

    """

    path: ClassVar[str] = "drafthistory"
    response_model: ClassVar[type[DraftHistoryResponse]] = DraftHistoryResponse

    league_id: str = "00"
    season: str | None = None
    team_id: str | None = None
    round_num: str | None = None
    round_pick: str | None = None
    overall_pick: str | None = None
    college: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        params: dict[str, str] = {"LeagueID": self.league_id}
        if self.season is not None:
            params["Season"] = self.season
        if self.team_id is not None:
            params["TeamID"] = self.team_id
        if self.round_num is not None:
            params["RoundNum"] = self.round_num
        if self.round_pick is not None:
            params["RoundPick"] = self.round_pick
        if self.overall_pick is not None:
            params["OverallPick"] = self.overall_pick
        if self.college is not None:
            params["College"] = self.college
        return params
