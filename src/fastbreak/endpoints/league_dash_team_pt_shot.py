"""League dash team pt shot endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_team_pt_shot import LeagueDashTeamPtShotResponse
from fastbreak.types import LeagueID, PerMode, Season, SeasonType


class LeagueDashTeamPtShot(Endpoint[LeagueDashTeamPtShotResponse]):
    """Fetch team tracking shot statistics.

    Returns team-level shot data including frequencies, makes, attempts,
    and percentages broken down by 2-point and 3-point shots.

    This is the offensive counterpart to LeagueDashOppPtShot.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        per_mode: Stats mode ("Totals", "PerGame", etc.)

    Example:
        >>> async with NBAClient() as client:
        ...     shots = await client.get(LeagueDashTeamPtShot(season="2024-25"))
        ...     for team in shots.teams[:5]:
        ...         print(f"{team.team_abbreviation}: {team.fg3_pct:.1%} 3PT")

    """

    path: ClassVar[str] = "leaguedashteamptshot"
    response_model: ClassVar[type[LeagueDashTeamPtShotResponse]] = (
        LeagueDashTeamPtShotResponse
    )

    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
