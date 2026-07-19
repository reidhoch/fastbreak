"""League dash player pt shot endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_player_pt_shot import (
    LeagueDashPlayerPtShotResponse,
)
from fastbreak.types import LeagueID, PerMode, Season, SeasonType, ShotClockRange


class LeagueDashPlayerPtShot(Endpoint[LeagueDashPlayerPtShotResponse]):
    """Fetch player tracking shot statistics.

    Returns player-level shot data including frequencies, makes, attempts,
    and percentages broken down by 2-point and 3-point shots, with optional
    filtering by defender distance, dribbles, touch time, and shot clock.

    This is the player-level counterpart to :class:`LeagueDashTeamPtShot`.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2025-26")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        per_mode: Stats mode ("Totals", "PerGame", etc.)
        close_def_dist_range: Closest-defender distance filter
            (e.g., "0-2 Feet - Very Tight", "6+ Feet - Wide Open")
        dribble_range: Dribbles-before-shot filter (e.g., "0 Dribbles")
        touch_time_range: Touch-time filter (e.g., "Touch < 2 Seconds")
        shot_clock_range: Shot-clock range filter (e.g., "24-22")
        general_range: General range filter (e.g., "Overall", "Catch and Shoot")

    Example:
        >>> async with NBAClient() as client:
        ...     shots = await client.get(LeagueDashPlayerPtShot(season="2025-26"))
        ...     for player in shots.players[:5]:
        ...         print(f"{player.player_name}: {player.fg3_pct:.1%} 3PT")

    """

    path: ClassVar[str] = "leaguedashplayerptshot"
    response_model: ClassVar[type[LeagueDashPlayerPtShotResponse]] = (
        LeagueDashPlayerPtShotResponse
    )

    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"
    close_def_dist_range: str | None = None
    dribble_range: str | None = None
    touch_time_range: str | None = None
    shot_clock_range: ShotClockRange | None = None
    general_range: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }
        if self.season is not None:
            result["Season"] = self.season
        if self.close_def_dist_range is not None:
            result["CloseDefDistRange"] = self.close_def_dist_range
        if self.dribble_range is not None:
            result["DribbleRange"] = self.dribble_range
        if self.touch_time_range is not None:
            result["TouchTimeRange"] = self.touch_time_range
        if self.shot_clock_range is not None:
            result["ShotClockRange"] = self.shot_clock_range
        if self.general_range is not None:
            result["GeneralRange"] = self.general_range
        return result
