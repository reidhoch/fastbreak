"""Player and team tracking data helpers for the NBA Stats API.

Wraps the seven NBA player-tracking endpoints (4 player, 3 team) and exposes
two profile dataclasses that fetch all sub-endpoints concurrently.

Examples::

    from fastbreak.clients import BaseClient
    from fastbreak.tracking import get_player_tracking_profile, get_team_tracking_profile

    async with NBAClient() as client:
        profile = await get_player_tracking_profile(client, player_id=1641705)
        # profile.shots, profile.passes, profile.rebounds, profile.shot_defense

        team_profile = await get_team_tracking_profile(client, team_id=1610612747)
        # team_profile.shots, team_profile.passes, team_profile.rebounds
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.player_dash_pt_pass import PlayerDashPtPassResponse
    from fastbreak.models.player_dash_pt_reb import PlayerDashPtRebResponse
    from fastbreak.models.player_dash_pt_shot_defend import (
        PlayerDashPtShotDefendResponse,
    )
    from fastbreak.models.player_dash_pt_shots import PlayerDashPtShotsResponse
    from fastbreak.models.team_dash_pt_pass import TeamDashPtPassResponse
    from fastbreak.models.team_dash_pt_reb import TeamDashPtRebResponse
    from fastbreak.models.team_dash_pt_shots import TeamDashPtShotsResponse
    from fastbreak.types import PerMode, Season, SeasonType


@dataclass(frozen=True)
class PlayerTrackingProfile:
    """Aggregated tracking data for a single player.

    Attributes:
        player_id: NBA player ID.
        shots: Shot type, shot clock, dribbles, defender distance, touch time.
        passes: Passes made/received, AST rate, FG% on passes.
        rebounds: Contested/uncontested boards by shot type and distance.
        shot_defense: Opponent FG% when defended vs. normal FG% by category.
    """

    player_id: int
    shots: PlayerDashPtShotsResponse
    passes: PlayerDashPtPassResponse
    rebounds: PlayerDashPtRebResponse
    shot_defense: PlayerDashPtShotDefendResponse


@dataclass(frozen=True)
class TeamTrackingProfile:
    """Aggregated tracking data for a single team.

    Attributes:
        team_id: NBA team ID.
        shots: Team shot breakdowns by type, shot clock, dribbles, etc.
        passes: Pass flow for every player on the team.
        rebounds: Team rebounding with contested/uncontested breakdown.
    """

    team_id: int
    shots: TeamDashPtShotsResponse
    passes: TeamDashPtPassResponse
    rebounds: TeamDashPtRebResponse


async def get_player_shots(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtShotsResponse:
    """Fetch player shot tracking data (shot type, clock, dribbles, defender, touch).

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashPtShotsResponse with seven shot-breakdown result sets.
    """
    from fastbreak.endpoints import PlayerDashPtShots  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        PlayerDashPtShots(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_player_passes(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtPassResponse:
    """Fetch player passing data (passes made/received, AST rate, FG% on passes).

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashPtPassResponse with passes made and passes received result sets.
    """
    from fastbreak.endpoints import PlayerDashPtPass  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        PlayerDashPtPass(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_player_rebounds(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtRebResponse:
    """Fetch player rebounding data (contested/uncontested by shot type and distance).

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashPtRebResponse with overall and shot-type rebounding result sets.
    """
    from fastbreak.endpoints import PlayerDashPtReb  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        PlayerDashPtReb(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_player_shot_defense(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerDashPtShotDefendResponse:
    """Fetch player shot defense data (opponent FG% when defended vs. normal FG%).

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerDashPtShotDefendResponse with defending shots breakdown.
    """
    from fastbreak.endpoints import PlayerDashPtShotDefend  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        PlayerDashPtShotDefend(
            player_id=player_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_team_shots(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamDashPtShotsResponse:
    """Fetch team-level shot tracking data.

    Same shot breakdowns as player tracking but aggregated at the team level.

    Args:
        client: NBA API client.
        team_id: NBA team ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        TeamDashPtShotsResponse with team shot breakdowns.
    """
    from fastbreak.endpoints import TeamDashPtShots  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        TeamDashPtShots(
            team_id=team_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_team_passes(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamDashPtPassResponse:
    """Fetch team passing data (pass flow for every player on the team).

    Args:
        client: NBA API client.
        team_id: NBA team ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        TeamDashPtPassResponse with team passing result sets.
    """
    from fastbreak.endpoints import TeamDashPtPass  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        TeamDashPtPass(
            team_id=team_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_team_rebounds(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamDashPtRebResponse:
    """Fetch team rebounding data (contested/uncontested breakdown).

    Args:
        client: NBA API client.
        team_id: NBA team ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        TeamDashPtRebResponse with team rebounding result sets.
    """
    from fastbreak.endpoints import TeamDashPtReb  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        TeamDashPtReb(
            team_id=team_id,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            last_n_games=last_n_games,
            league_id=client.league_id,
        )
    )


async def get_player_tracking_profile(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> PlayerTrackingProfile:
    """Fetch all four player tracking endpoints concurrently.

    Uses ``client.get_many()`` so the client's ``request_delay`` and
    ``max_concurrency`` settings are respected.  Raises ``ExceptionGroup`` if
    any sub-request fails (same contract as ``get_box_scores()``).  Callers
    that need partial results should call the thin helpers individually.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        PlayerTrackingProfile with shots, passes, rebounds, and shot_defense.

    Raises:
        ExceptionGroup: If any of the four API requests fails.
    """
    from fastbreak.endpoints import (  # noqa: PLC0415
        PlayerDashPtPass,
        PlayerDashPtReb,
        PlayerDashPtShotDefend,
        PlayerDashPtShots,
    )

    season = season or get_season_from_date(league=client.league)
    params: dict[str, Any] = {
        "player_id": player_id,
        "season": season,
        "season_type": season_type,
        "per_mode": per_mode,
        "last_n_games": last_n_games,
        "league_id": client.league_id,
    }

    results: list[Any] = await client.get_many(
        [
            PlayerDashPtShots(**params),
            PlayerDashPtPass(**params),
            PlayerDashPtReb(**params),
            PlayerDashPtShotDefend(**params),
        ]
    )

    return PlayerTrackingProfile(
        player_id=player_id,
        shots=cast("PlayerDashPtShotsResponse", results[0]),
        passes=cast("PlayerDashPtPassResponse", results[1]),
        rebounds=cast("PlayerDashPtRebResponse", results[2]),
        shot_defense=cast("PlayerDashPtShotDefendResponse", results[3]),
    )


async def get_team_tracking_profile(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    last_n_games: int = 0,
) -> TeamTrackingProfile:
    """Fetch all three team tracking endpoints concurrently.

    Uses ``client.get_many()`` so the client's ``request_delay`` and
    ``max_concurrency`` settings are respected.  Raises ``ExceptionGroup`` if
    any sub-request fails.  Callers that need partial results should call the
    thin helpers individually.

    Args:
        client: NBA API client.
        team_id: NBA team ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        per_mode: "PerGame" or "Totals".
        last_n_games: Restrict to last N games (0 = full season).

    Returns:
        TeamTrackingProfile with shots, passes, and rebounds.

    Raises:
        ExceptionGroup: If any of the three API requests fails.
    """
    from fastbreak.endpoints import (  # noqa: PLC0415
        TeamDashPtPass,
        TeamDashPtReb,
        TeamDashPtShots,
    )

    season = season or get_season_from_date(league=client.league)
    params: dict[str, Any] = {
        "team_id": team_id,
        "season": season,
        "season_type": season_type,
        "per_mode": per_mode,
        "last_n_games": last_n_games,
        "league_id": client.league_id,
    }

    results: list[Any] = await client.get_many(
        [
            TeamDashPtShots(**params),
            TeamDashPtPass(**params),
            TeamDashPtReb(**params),
        ]
    )

    return TeamTrackingProfile(
        team_id=team_id,
        shots=cast("TeamDashPtShotsResponse", results[0]),
        passes=cast("TeamDashPtPassResponse", results[1]),
        rebounds=cast("TeamDashPtRebResponse", results[2]),
    )
