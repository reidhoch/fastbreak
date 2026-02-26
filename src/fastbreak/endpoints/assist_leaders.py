"""Assist leaders endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.assist_leaders import AssistLeadersResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, PerMode, PlayerOrTeam, Season, SeasonType


class AssistLeaders(Endpoint[AssistLeadersResponse]):
    """Fetch assist leaders by team or player.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals")
        player_or_team: Whether to return player or team stats ("Player", "Team")

    """

    path: ClassVar[str] = "assistleaders"
    response_model: ClassVar[type[AssistLeadersResponse]] = AssistLeadersResponse

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    player_or_team: PlayerOrTeam = "Team"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "PlayerOrTeam": self.player_or_team,
        }
