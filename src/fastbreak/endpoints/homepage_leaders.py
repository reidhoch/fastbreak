"""Homepage leaders endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.homepage_leaders import HomepageLeadersResponse
from fastbreak.types import LeagueID, PlayerOrTeam, Season, SeasonType


class HomepageLeaders(Endpoint[HomepageLeadersResponse]):
    """Fetch detailed leaders for a specific statistical category.

    Returns leaders for a single stat category with additional efficiency
    metrics like EFG%, TS%, and per-48 minute stats. Use HomepageV2 if
    you need multiple stat categories at once.

    Args:
        stat_category: Stat to rank by ("Points", "Rebounds", "Assists", etc.)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        player_or_team: "Player" or "Team" scope
        player_scope: "All Players" or "Rookies"
        game_scope: "Season" or "Last 10" etc.

    Example:
        >>> async with NBAClient() as client:
        ...     leaders = await client.get(HomepageLeaders(
        ...         stat_category="Points",
        ...         season="2024-25"
        ...     ))
        ...     for leader in leaders.leaders[:3]:
        ...         print(f"{leader.player}: {leader.pts} PPG ({leader.ts_pct:.1%} TS%)")

    """

    path: ClassVar[str] = "homepageleaders"
    response_model: ClassVar[type[HomepageLeadersResponse]] = HomepageLeadersResponse

    stat_category: str = "Points"
    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    player_or_team: PlayerOrTeam = "Player"
    player_scope: str = "All Players"
    game_scope: str = "Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "StatCategory": self.stat_category,
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PlayerOrTeam": self.player_or_team,
            "PlayerScope": self.player_scope,
            "GameScope": self.game_scope,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
