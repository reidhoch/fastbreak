"""Player situational split helpers for the NBA Stats API.

Wraps five player-dashboard-by-* endpoints and exposes a ``PlayerSplitsProfile``
dataclass that fetches all sub-endpoints concurrently.

Examples::

    from fastbreak.clients import NBAClient
    from fastbreak.splits import get_player_splits_profile, stat_delta

    async with NBAClient() as client:
        profile = await get_player_splits_profile(client, player_id=1641705)

        # Concurrent fetch: game, general, shooting, last-N, team performance
        home = next((s for s in profile.general_splits.by_location if s.group_value == "Home"), None)
        road = next((s for s in profile.general_splits.by_location if s.group_value == "Road"), None)
        fg_pct_diff = stat_delta(
            home.fg_pct if home else None,
            road.fg_pct if road else None,
        )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from fastbreak.metrics import stat_delta as stat_delta  # noqa: PLC0414
from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.player_dashboard_by_game_splits import (
        PlayerDashboardByGameSplitsResponse,
    )
    from fastbreak.models.player_dashboard_by_general_splits import (
        PlayerDashboardByGeneralSplitsResponse,
    )
    from fastbreak.models.player_dashboard_by_last_n_games import (
        PlayerDashboardByLastNGamesResponse,
    )
    from fastbreak.models.player_dashboard_by_shooting_splits import (
        PlayerDashboardByShootingSplitsResponse,
    )
    from fastbreak.models.player_dashboard_by_team_performance import (
        PlayerDashboardByTeamPerformanceResponse,
    )
    from fastbreak.types import PerMode, Season, SeasonType


@dataclass(frozen=True)
class PlayerSplitsProfile:
    """Aggregated situational split data for a single player.

    Attributes:
        player_id: NBA player ID.
        game_splits: Stats by half, period, score margin, and actual margin.
        general_splits: Stats by location, W/L, month, rest, and position.
        shooting_splits: Stats by shot distance, area, type, and assist type.
        last_n_games: Rolling stats for last 5/10/15/20 games.
        team_performance: Stats by score differential and points scored ranges.
    """

    player_id: int
    game_splits: PlayerDashboardByGameSplitsResponse
    general_splits: PlayerDashboardByGeneralSplitsResponse
    shooting_splits: PlayerDashboardByShootingSplitsResponse
    last_n_games: PlayerDashboardByLastNGamesResponse
    team_performance: PlayerDashboardByTeamPerformanceResponse


async def get_player_game_splits(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashboardByGameSplitsResponse:
    """Fetch player stats broken down by game segments.

    Returns stats split by half, period, score margin, and actual score margin.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: \"Regular Season\", \"Playoffs\", or \"Pre Season\".
        per_mode: \"PerGame\" or \"Totals\".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashboardByGameSplitsResponse with overall, by_half, by_period,
        by_score_margin, and by_actual_margin result sets.
    """
    from fastbreak.endpoints import PlayerDashboardByGameSplits  # noqa: PLC0415

    season = season or get_season_from_date()
    return await client.get(
        PlayerDashboardByGameSplits(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
        )
    )


async def get_player_general_splits(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashboardByGeneralSplitsResponse:
    """Fetch player situational splits by location, outcome, month, and rest.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: \"Regular Season\", \"Playoffs\", or \"Pre Season\".
        per_mode: \"PerGame\" or \"Totals\".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashboardByGeneralSplitsResponse with splits by location,
        wins/losses, month, All-Star break, starting position, and days rest.
    """
    from fastbreak.endpoints import PlayerDashboardByGeneralSplits  # noqa: PLC0415

    season = season or get_season_from_date()
    return await client.get(
        PlayerDashboardByGeneralSplits(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
        )
    )


async def get_player_shooting_splits(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashboardByShootingSplitsResponse:
    """Fetch player shooting splits by distance, area, shot type, and assist.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: \"Regular Season\", \"Playoffs\", or \"Pre Season\".
        per_mode: \"PerGame\" or \"Totals\".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashboardByShootingSplitsResponse with splits by shot distance
        (5ft and 8ft buckets), court area, assisted/unassisted, and shot type.
    """
    from fastbreak.endpoints import PlayerDashboardByShootingSplits  # noqa: PLC0415

    season = season or get_season_from_date()
    return await client.get(
        PlayerDashboardByShootingSplits(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
        )
    )


async def get_player_last_n_games(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashboardByLastNGamesResponse:
    """Fetch player rolling-average stats for last 5/10/15/20 games.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: \"Regular Season\", \"Playoffs\", or \"Pre Season\".
        per_mode: \"PerGame\" or \"Totals\".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashboardByLastNGamesResponse with overall, last_5, last_10,
        last_15, last_20, and by_game_number result sets.
    """
    from fastbreak.endpoints import PlayerDashboardByLastNGames  # noqa: PLC0415

    season = season or get_season_from_date()
    return await client.get(
        PlayerDashboardByLastNGames(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
        )
    )


async def get_player_team_performance_splits(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashboardByTeamPerformanceResponse:
    """Fetch player stats split by team score differential and points ranges.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: \"Regular Season\", \"Playoffs\", or \"Pre Season\".
        per_mode: \"PerGame\" or \"Totals\".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashboardByTeamPerformanceResponse with splits by score
        differential, points scored, and points against.
    """
    from fastbreak.endpoints import PlayerDashboardByTeamPerformance  # noqa: PLC0415

    season = season or get_season_from_date()
    return await client.get(
        PlayerDashboardByTeamPerformance(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
        )
    )


async def get_player_splits_profile(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerSplitsProfile:
    """Fetch all five player split endpoints concurrently.

    Uses ``client.get_many()`` so the client's ``request_delay`` and
    ``max_concurrency`` settings are respected.  Raises ``ExceptionGroup`` if
    any sub-request fails.  Callers that need partial results should call the
    thin helpers individually.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: \"Regular Season\", \"Playoffs\", or \"Pre Season\".
        per_mode: \"PerGame\" or \"Totals\".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerSplitsProfile with game_splits, general_splits, shooting_splits,
        last_n_games, and team_performance.

    Raises:
        ExceptionGroup: If any of the five API requests fails.
    """
    from fastbreak.endpoints import (  # noqa: PLC0415
        PlayerDashboardByGameSplits,
        PlayerDashboardByGeneralSplits,
        PlayerDashboardByLastNGames,
        PlayerDashboardByShootingSplits,
        PlayerDashboardByTeamPerformance,
    )

    season = season or get_season_from_date()
    params: dict[str, Any] = {
        "player_id": player_id,
        "season": season,
        "season_type": season_type,
        "per_mode": per_mode,
        "last_n_games": last_n_games,
    }

    results: list[Any] = await client.get_many(
        [
            PlayerDashboardByGameSplits(**params),
            PlayerDashboardByGeneralSplits(**params),
            PlayerDashboardByShootingSplits(**params),
            PlayerDashboardByLastNGames(**params),
            PlayerDashboardByTeamPerformance(**params),
        ]
    )

    return PlayerSplitsProfile(
        player_id=player_id,
        game_splits=cast("PlayerDashboardByGameSplitsResponse", results[0]),
        general_splits=cast("PlayerDashboardByGeneralSplitsResponse", results[1]),
        shooting_splits=cast("PlayerDashboardByShootingSplitsResponse", results[2]),
        last_n_games=cast("PlayerDashboardByLastNGamesResponse", results[3]),
        team_performance=cast("PlayerDashboardByTeamPerformanceResponse", results[4]),
    )
