"""Clutch performance analysis helpers for the NBA Stats API.

Provides a composite ClutchProfile aggregating a player's standard clutch
definition (last 5 minutes, score within 5 points) against their full-season
baseline, plus league-wide player and team clutch leader queries.

Examples::

    from fastbreak.clients import BaseClient
    from fastbreak.clutch import get_player_clutch_profile, get_league_clutch_leaders

    async with NBAClient() as client:
        profile = await get_player_clutch_profile(
            client, player_id=2544, name="LeBron James", team="LAL"
        )
        if profile and profile.score is not None:
            print(f"{profile.name}: clutch score {profile.score:+.2f}")

        leaders = await get_league_clutch_leaders(client, min_minutes=25.0, top_n=10)
        for row in leaders:
            print(f"{row.player_name}: {row.plus_minus:+.1f} in clutch")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from fastbreak.metrics import ast_to_tov, stat_delta, true_shooting
from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.league_dash_player_clutch import LeagueDashPlayerClutchRow
    from fastbreak.models.league_dash_team_clutch import TeamClutchStats
    from fastbreak.models.player_dashboard_by_clutch import (
        PlayerDashboardByClutchResponse,
    )
    from fastbreak.types import Season, SeasonType


class _ClutchStatsLike(Protocol):
    """Structural protocol for stats objects accepted by build_clutch_profile."""

    pts: float
    fga: float
    fta: float
    ast: float
    tov: float
    min: float
    plus_minus: float


@dataclass(frozen=True)
class ClutchProfile:
    """Computed clutch performance profile for a single player.

    Attributes:
        player_id: NBA player ID.
        name: Player's full name.
        team: Team abbreviation.
        clutch_min: Minutes played in clutch situations (last 5 min, ≤5 pts).
        regular_ts: True shooting % for the full season baseline.
        clutch_ts: True shooting % in clutch situations.
        ts_delta: clutch_ts - regular_ts (positive = better under pressure).
        regular_ato: Assist-to-turnover ratio for the full season.
        clutch_ato: Assist-to-turnover ratio in clutch situations.
        ato_delta: clutch_ato - regular_ato (positive = better decisions).
        clutch_plus_minus: Plus/minus in clutch situations.
        score: Composite clutch rating (None if insufficient sample size).
    """

    player_id: int
    name: str
    team: str
    clutch_min: float
    regular_ts: float | None
    clutch_ts: float | None
    ts_delta: float | None
    regular_ato: float | None
    clutch_ato: float | None
    ato_delta: float | None
    clutch_plus_minus: float
    score: float | None


def clutch_score(
    ts_delta: float,
    ato_delta: float,
    plus_minus: float,
    clutch_min: float,
    min_threshold: float = 5.0,
) -> float | None:
    """Compute a composite clutch performance score.

    Returns None when ``clutch_min < min_threshold`` (insufficient sample).

    The formula is a weighted linear combination::

        score = ts_delta * 10 + ato_delta * 3 + plus_minus * 0.5

    Weights reflect predictive value: shooting quality under pressure is the
    strongest signal, followed by decision-making, then team outcome context.
    The linear (no-constant) form means ``score(-x) == -score(x)``.

    Args:
        ts_delta: Clutch TS% minus regular-season TS%.
        ato_delta: Clutch A/TO minus regular-season A/TO.
        plus_minus: Plus/minus in clutch situations.
        clutch_min: Minutes played in clutch situations.
        min_threshold: Minimum clutch minutes required (default 5).

    Returns:
        Composite score float, or None if sample is too small.
    """
    if clutch_min < min_threshold:
        return None
    return ts_delta * 10.0 + ato_delta * 3.0 + plus_minus * 0.5


def build_clutch_profile(  # noqa: PLR0913
    player_id: int,
    name: str,
    team: str,
    overall: _ClutchStatsLike | None,
    clutch: _ClutchStatsLike | None,
    *,
    min_threshold: float = 5.0,
) -> ClutchProfile:
    """Build a ClutchProfile from overall and clutch stats objects.

    Both ``overall`` and ``clutch`` must expose ``.pts``, ``.fga``, ``.fta``,
    ``.ast``, ``.tov``, ``.min``, and ``.plus_minus`` attributes (matching the
    ``ClutchStats`` model fields).  Either may be None.

    Args:
        player_id: NBA player ID.
        name: Player full name (used for display only).
        team: Team abbreviation (used for display only).
        overall: Full-season stats object, or None.
        clutch: Clutch-situation stats object, or None.
        min_threshold: Minimum clutch minutes required to compute a score.

    Returns:
        ClutchProfile with all computed delta and composite score fields.
    """
    regular_ts: float | None = None
    regular_ato: float | None = None
    if overall is not None:
        regular_ts = true_shooting(overall.pts, overall.fga, overall.fta)
        regular_ato = ast_to_tov(overall.ast, overall.tov)

    clutch_ts: float | None = None
    clutch_ato: float | None = None
    clutch_min = 0.0
    clutch_plus_minus = 0.0
    if clutch is not None:
        clutch_ts = true_shooting(clutch.pts, clutch.fga, clutch.fta)
        clutch_ato = ast_to_tov(clutch.ast, clutch.tov)
        clutch_min = clutch.min
        clutch_plus_minus = clutch.plus_minus

    ts_delta = stat_delta(clutch_ts, regular_ts)
    ato_delta = stat_delta(clutch_ato, regular_ato)

    score: float | None = None
    if ts_delta is not None and ato_delta is not None:
        score = clutch_score(
            ts_delta, ato_delta, clutch_plus_minus, clutch_min, min_threshold
        )

    return ClutchProfile(
        player_id=player_id,
        name=name,
        team=team,
        clutch_min=clutch_min,
        regular_ts=regular_ts,
        clutch_ts=clutch_ts,
        ts_delta=ts_delta,
        regular_ato=regular_ato,
        clutch_ato=clutch_ato,
        ato_delta=ato_delta,
        clutch_plus_minus=clutch_plus_minus,
        score=score,
    )


async def get_player_clutch_stats(
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> PlayerDashboardByClutchResponse:
    """Fetch all clutch time splits for a single player.

    Returns stats for eleven clutch definitions (last 5/3/1 min at ≤5 pts,
    last 30/10 sec at ≤3 pts, and the same definitions with ±5/±3 pt spread).

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", etc.

    Returns:
        PlayerDashboardByClutchResponse with eleven clutch scenario splits.
    """
    from fastbreak.endpoints import PlayerDashboardByClutch  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        PlayerDashboardByClutch(
            player_id=player_id,
            season=season,
            season_type=season_type,
            league_id=client.league_id,
        )
    )


async def get_player_clutch_profile(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    name: str = "",
    team: str = "",
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    min_threshold: float = 5.0,
) -> ClutchProfile | None:
    """Build a ClutchProfile comparing clutch vs. regular performance.

    Uses the standard NBA clutch definition: last 5 minutes with score within
    5 points.  Returns None if the player has no qualifying clutch minutes.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        name: Player's display name (stored on profile for convenience).
        team: Team abbreviation (stored on profile for convenience).
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", etc.
        min_threshold: Minimum clutch minutes required to compute a score.

    Returns:
        ClutchProfile, or None if the player has no clutch minutes recorded.
    """
    response = await get_player_clutch_stats(
        client, player_id, season=season, season_type=season_type
    )
    if response.last_5_min_lte_5_pts is None:
        return None
    return build_clutch_profile(
        player_id,
        name,
        team,
        response.overall,
        response.last_5_min_lte_5_pts,
        min_threshold=min_threshold,
    )


async def get_league_clutch_leaders(
    client: BaseClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    min_minutes: float = 20.0,
    top_n: int = 10,
) -> list[LeagueDashPlayerClutchRow]:
    """Fetch league-wide clutch leaders sorted by plus/minus.

    Uses the standard clutch definition (last 5 min, ≤5 pts) across all
    players.  Filters out players with insufficient clutch sample size.

    Args:
        client: NBA API client.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", etc.
        min_minutes: Minimum clutch minutes to qualify (default 20).
        top_n: Maximum number of players to return (default 10).

    Returns:
        List of LeagueDashPlayerClutchRow sorted by plus_minus descending,
        capped at top_n entries.

    Raises:
        ValueError: If top_n < 1 or min_minutes < 0.
    """
    if top_n < 1:
        msg = f"top_n must be >= 1, got {top_n}"
        raise ValueError(msg)
    if min_minutes < 0:
        msg = f"min_minutes must be >= 0, got {min_minutes}"
        raise ValueError(msg)

    from fastbreak.endpoints import LeagueDashPlayerClutch  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    response = await client.get(
        LeagueDashPlayerClutch(
            season=season, season_type=season_type, league_id=client.league_id
        )
    )
    qualified = [p for p in response.players if p.min >= min_minutes]
    qualified.sort(key=lambda p: p.plus_minus, reverse=True)
    return qualified[:top_n]


async def get_league_team_clutch_leaders(
    client: BaseClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    top_n: int = 30,
) -> list[TeamClutchStats]:
    """Fetch league-wide team clutch leaders sorted by plus/minus.

    Uses the standard clutch definition (last 5 min, ≤5 pts) across all teams.

    Args:
        client: NBA API client.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", etc.
        top_n: Maximum number of teams to return (default 30).

    Returns:
        List of TeamClutchStats sorted by plus_minus descending,
        capped at top_n entries.

    Raises:
        ValueError: If top_n < 1.
    """
    if top_n < 1:
        msg = f"top_n must be >= 1, got {top_n}"
        raise ValueError(msg)

    from fastbreak.endpoints import LeagueDashTeamClutch  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    response = await client.get(
        LeagueDashTeamClutch(
            season=season, season_type=season_type, league_id=client.league_id
        )
    )
    teams = list(response.teams)
    teams.sort(key=lambda t: t.plus_minus, reverse=True)
    return teams[:top_n]


async def get_team_clutch_stats(
    client: BaseClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> TeamClutchStats | None:
    """Fetch clutch stats for a single team.

    Filters from league-wide response to one team.
    Returns None if team_id not found.

    Args:
        client: NBA API client.
        team_id: NBA team ID.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", etc.

    Returns:
        TeamClutchStats for the matching team, or None if not found.
    """
    from fastbreak.endpoints import LeagueDashTeamClutch  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    response = await client.get(
        LeagueDashTeamClutch(
            season=season, season_type=season_type, league_id=client.league_id
        )
    )
    for team in response.teams:
        if team.team_id == team_id:
            return team
    return None
