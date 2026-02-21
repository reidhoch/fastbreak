"""Homepage v2 endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.homepage_v2 import HomepageV2Response
from fastbreak.types import LeagueID, PlayerOrTeam, Season, SeasonType


class HomepageV2(Endpoint[HomepageV2Response]):
    """Fetch homepage statistics for multiple stat categories.

    Returns top 5 leaders across multiple statistical categories including
    points, rebounds, assists, blocks, steals, and three-point percentage.
    This is the data used to populate the NBA.com homepage leader widgets.

    Args:
        stat_type: Type of statistics ("Traditional", "Advanced", etc.)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        player_or_team: "Player" or "Team" scope
        player_scope: "All Players" or "Rookies"
        game_scope: "Season" or "Last 10" etc.

    Example:
        >>> async with NBAClient() as client:
        ...     homepage = await client.get(HomepageV2(season="2024-25"))
        ...     print("Points Leaders:")
        ...     for leader in homepage.pts_leaders:
        ...         print(f"  {leader.rank}. {leader.player}: {leader.pts}")

    """

    path: ClassVar[str] = "homepagev2"
    response_model: ClassVar[type[HomepageV2Response]] = HomepageV2Response

    stat_type: str = "Traditional"
    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    player_or_team: PlayerOrTeam = "Player"
    player_scope: str = "All Players"
    game_scope: str = "Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "StatType": self.stat_type,
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PlayerOrTeam": self.player_or_team,
            "PlayerScope": self.player_scope,
            "GameScope": self.game_scope,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
