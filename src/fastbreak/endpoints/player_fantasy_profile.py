"""Player Fantasy Profile endpoint for split fantasy production."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerDashboardEndpoint
from fastbreak.models.player_fantasy_profile import PlayerFantasyProfileResponse


class PlayerFantasyProfile(PlayerDashboardEndpoint[PlayerFantasyProfileResponse]):
    """Fetch a player's fantasy production split five ways.

    Returns overall, home/road, last-N-games, days-of-rest, and per-opponent
    splits, each with box-score stats plus fantasy columns (double-doubles,
    triple-doubles, FanDuel points, NBA fantasy points).

    This is the full tabular fantasy profile — the counterpart to
    :class:`PlayerFantasyProfileBarGraph`, which carries only season and
    last-five averages.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2025-26")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        (plus the standard dashboard filters inherited from
        :class:`PlayerDashboardEndpoint`)

    Example:
        >>> async with NBAClient() as client:
        ...     profile = await client.get(PlayerFantasyProfile(player_id=201939))
        ...     if profile.overall:
        ...         print(f"NBA fantasy pts: {profile.overall.nba_fantasy_pts}")

    """

    path: ClassVar[str] = "playerfantasyprofile"
    response_model: ClassVar[type[PlayerFantasyProfileResponse]] = (
        PlayerFantasyProfileResponse
    )
