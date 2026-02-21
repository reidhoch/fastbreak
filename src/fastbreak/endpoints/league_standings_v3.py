"""League standings v3 endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_standings_v3 import LeagueStandingsV3Response
from fastbreak.types import LeagueID, Season, SeasonType


class LeagueStandingsV3(Endpoint[LeagueStandingsV3Response]):
    """Fetch comprehensive league standings.

    Returns detailed standings including records, streaks, situational
    splits (home/road, vs conferences, by month), clinch status, and
    games back calculations.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")

    Example:
        >>> async with NBAClient() as client:
        ...     standings = await client.get(LeagueStandingsV3(season="2024-25"))
        ...     east = [t for t in standings.standings if t.conference == "East"]
        ...     for team in sorted(east, key=lambda t: t.playoff_rank)[:8]:
        ...         print(f"{team.playoff_rank}. {team.team_name}: {team.record}")

    """

    path: ClassVar[str] = "leaguestandingsv3"
    response_model: ClassVar[type[LeagueStandingsV3Response]] = (
        LeagueStandingsV3Response
    )

    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
