"""Assist leaders endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.assist_leaders import AssistLeadersResponse


@dataclass(frozen=True)
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

    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    player_or_team: str = "Team"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "PlayerOrTeam": self.player_or_team,
        }
