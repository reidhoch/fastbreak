"""League dash opponent pt shot endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_opp_pt_shot import LeagueDashOppPtShotResponse
from fastbreak.types import LeagueID, PerMode, Season, SeasonType


class LeagueDashOppPtShot(Endpoint[LeagueDashOppPtShotResponse]):
    """Fetch opponent tracking shot statistics (defensive quality).

    Returns how opponents shoot against each team, measuring defensive
    effectiveness. Lower opponent FG% indicates better team defense.

    This is the defensive counterpart to LeagueDashTeamPtShot.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        per_mode: Stats mode ("Totals", "PerGame", etc.)

    Example:
        >>> async with NBAClient() as client:
        ...     defense = await client.get(LeagueDashOppPtShot(season="2024-25"))
        ...     # Sort by opponent FG% (lower = better defense)
        ...     for team in sorted(defense.teams, key=lambda t: t.fg_pct)[:5]:
        ...         print(f"{team.team_abbreviation}: {team.fg_pct:.1%} opp FG%")

    """

    path: ClassVar[str] = "leaguedashoppptshot"
    response_model: ClassVar[type[LeagueDashOppPtShotResponse]] = (
        LeagueDashOppPtShotResponse
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
