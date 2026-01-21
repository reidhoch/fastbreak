"""Endpoint for fetching cumulative team stats."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.cume_stats_team import CumeStatsTeamResponse


@dataclass(frozen=True)
class CumeStatsTeam(Endpoint[CumeStatsTeamResponse]):
    """Fetch cumulative team stats for specific games.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2025-26")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        team_id: The team's unique identifier
        game_ids: Comma-separated list of game IDs to include

    """

    path: ClassVar[str] = "cumestatsteam"
    response_model: ClassVar[type[CumeStatsTeamResponse]] = CumeStatsTeamResponse

    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    team_id: int = 0
    game_ids: str = ""

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "TeamID": str(self.team_id),
            "GameIDs": self.game_ids,
        }
