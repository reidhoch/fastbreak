"""League hustle stats player endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_hustle_stats_player import LeagueHustleStatsPlayerResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, PerMode, Season, SeasonType


class LeagueHustleStatsPlayer(Endpoint[LeagueHustleStatsPlayerResponse]):
    """Fetch season-aggregated hustle statistics for all players.

    Hustle stats include contested shots, deflections, loose balls recovered,
    screen assists, charges drawn, and box outs aggregated across the season.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals")
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "leaguehustlestatsplayer"
    response_model: ClassVar[type[LeagueHustleStatsPlayerResponse]] = (
        LeagueHustleStatsPlayerResponse
    )

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    league_id: LeagueID | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }

        if self.league_id is not None:
            result["LeagueID"] = self.league_id

        return result
