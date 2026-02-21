"""League dash player bio stats endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_player_bio_stats import (
    LeagueDashPlayerBioStatsResponse,
)
from fastbreak.types import LeagueID, PerMode, Season, SeasonType


class LeagueDashPlayerBioStats(Endpoint[LeagueDashPlayerBioStatsResponse]):
    """Fetch player biographical and statistical data.

    Returns player info including height, weight, college, country,
    draft info, age, and basic stats with advanced metrics like
    usage rate, true shooting, and net rating.

    Great for filtering players by physical attributes or background.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        per_mode: Stats mode ("Totals", "PerGame", etc.)
        college: Filter by college name
        country: Filter by country
        draft_year: Filter by draft year
        draft_pick: Filter by draft pick range
        height: Filter by height
        weight: Filter by weight

    Example:
        >>> async with NBAClient() as client:
        ...     bio = await client.get(LeagueDashPlayerBioStats(
        ...         season="2024-25",
        ...         college="Duke"
        ...     ))
        ...     for player in bio.players[:5]:
        ...         print(f"{player.player_name}: {player.player_height}, {player.college}")

    """

    path: ClassVar[str] = "leaguedashplayerbiostats"
    response_model: ClassVar[type[LeagueDashPlayerBioStatsResponse]] = (
        LeagueDashPlayerBioStatsResponse
    )

    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"
    college: str | None = None
    country: str | None = None
    draft_year: str | None = None
    draft_pick: str | None = None
    height: str | None = None
    weight: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }
        if self.season is not None:
            result["Season"] = self.season
        if self.college is not None:
            result["College"] = self.college
        if self.country is not None:
            result["Country"] = self.country
        if self.draft_year is not None:
            result["DraftYear"] = self.draft_year
        if self.draft_pick is not None:
            result["DraftPick"] = self.draft_pick
        if self.height is not None:
            result["Height"] = self.height
        if self.weight is not None:
            result["Weight"] = self.weight
        return result
