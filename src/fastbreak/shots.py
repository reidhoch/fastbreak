"""Shot chart helpers for the NBA Stats API.

Provides per-shot coordinate data (ShotChartDetail), league-wide zone averages
(ShotChartLeaguewide), and pure-computation helpers for zone FG% analysis.

Examples::

    from fastbreak.clients import NBAClient
    from fastbreak.shots import get_shot_chart, get_league_shot_zones, zone_breakdown, shot_quality_vs_league

    async with NBAClient() as client:
        response = await get_shot_chart(client, player_id=2544)
        print(f"Shots: {len(response.shots)}")

        breakdown = zone_breakdown(response.shots)
        for zone, stats in breakdown.items():
            print(f"{zone}: {stats.fgm}/{stats.fga} ({stats.fg_pct:.1%})")

        lg_zones = await get_league_shot_zones(client)
        deltas = shot_quality_vs_league(response.shots, lg_zones)
        for zone, delta in deltas.items():
            if delta is not None:
                print(f"{zone}: {delta:+.1%} vs league avg")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.shot_chart_detail import Shot, ShotChartDetailResponse
    from fastbreak.models.shot_chart_leaguewide import (
        LeagueWideShotZone,
        ShotChartLeaguewideResponse,
    )
    from fastbreak.types import ContextMeasure, Season, SeasonType


@dataclass(frozen=True)
class ZoneStats:
    """Shot statistics for a single court zone.

    Attributes:
        zone: Zone name matching Shot.shot_zone_basic (e.g., "Mid-Range").
        fga: Total field goal attempts from this zone.
        fgm: Total field goals made from this zone.
        fg_pct: Field goal percentage (fgm / fga), or None if no attempts.
    """

    zone: str
    fga: int
    fgm: int
    fg_pct: float | None


def zone_fg_pct(shots: list[Shot]) -> float | None:
    """Compute FG% for a list of Shot objects.

    Args:
        shots: List of Shot objects from ShotChartDetailResponse.

    Returns:
        FG% as a float in [0.0, 1.0], or None if the list is empty.
    """
    fga = len(shots)
    if fga == 0:
        return None
    fgm = sum(s.shot_made_flag for s in shots)
    return fgm / fga


def zone_breakdown(shots: list[Shot]) -> dict[str, ZoneStats]:
    """Group shots by shot_zone_basic and compute FG% per zone.

    Args:
        shots: List of Shot objects from ShotChartDetailResponse.

    Returns:
        Dict mapping zone name → ZoneStats with fga, fgm, and fg_pct.
        Empty dict when shots is empty.
    """
    counts: dict[str, tuple[int, int]] = {}
    for shot in shots:
        zone = shot.shot_zone_basic
        fga, fgm = counts.get(zone, (0, 0))
        counts[zone] = (fga + 1, fgm + shot.shot_made_flag)

    return {
        zone: ZoneStats(zone=zone, fga=fga, fgm=fgm, fg_pct=fgm / fga)
        for zone, (fga, fgm) in counts.items()
    }


def shot_quality_vs_league(
    player_shots: list[Shot],
    league_zones: list[LeagueWideShotZone],
    *,
    player_zones: dict[str, ZoneStats] | None = None,
) -> dict[str, float | None]:
    """Compute per-zone FG% delta vs. league average.

    Positive delta means the player shoots above league average in that zone;
    negative means below. Zones in player shots with no matching league data
    receive a delta of None.

    Args:
        player_shots: Shot objects from ShotChartDetailResponse.
        league_zones: League-wide zone averages from ShotChartLeaguewideResponse.
        player_zones: Pre-computed zone breakdown from zone_breakdown(). If provided,
            player_shots is not re-processed (avoids redundant computation).

    Returns:
        Dict mapping zone name → delta (float or None).
        Keys match exactly the zones present in player_shots.
    """
    _player_zones = (
        player_zones if player_zones is not None else zone_breakdown(player_shots)
    )

    # Aggregate league data by basic zone — the leaguewide endpoint returns one
    # row per (basic, area, range) combination, so the same shot_zone_basic can
    # appear multiple times.  Sum fga/fgm across sub-zones and compute a single
    # weighted FG% per basic zone to avoid silent last-wins overwriting.
    league_totals: dict[str, tuple[int, int]] = {}
    for z in league_zones:
        total_fga, total_fgm = league_totals.get(z.shot_zone_basic, (0, 0))
        league_totals[z.shot_zone_basic] = (total_fga + z.fga, total_fgm + z.fgm)
    league_lookup: dict[str, float] = {
        zone: fgm / fga for zone, (fga, fgm) in league_totals.items() if fga > 0
    }

    result: dict[str, float | None] = {}
    for zone, stats in _player_zones.items():
        if zone not in league_lookup or stats.fg_pct is None:
            result[zone] = None
        else:
            result[zone] = stats.fg_pct - league_lookup[zone]
    return result


async def get_shot_chart(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    *,
    team_id: int = 0,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    context_measure: ContextMeasure = "FGA",
) -> ShotChartDetailResponse:
    """Fetch per-shot coordinates and zone data for a player.

    Returns individual shot attempts with x/y court coordinates
    (LOC_X, LOC_Y), zone classifications, and league average FG% by zone
    for normalization.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        team_id: Filter to a specific team (0 for all teams, default).
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", "Pre Season", etc.
        context_measure: Shot type filter — "FGA" (all attempts), "FG3A"
            (three-pointers only), "FGM" (makes only), etc.

    Returns:
        ShotChartDetailResponse with shots (list[Shot]) and
        league_averages (list[LeagueAverage]) by zone.
    """
    from fastbreak.endpoints import ShotChartDetail  # noqa: PLC0415

    season = season or get_season_from_date()
    return await client.get(
        ShotChartDetail(
            player_id=player_id,
            team_id=team_id,
            season=season,
            season_type=season_type,
            context_measure=context_measure,
        )
    )


async def get_league_shot_zones(
    client: NBAClient,
    *,
    season: Season | None = None,
) -> list[LeagueWideShotZone]:
    """Fetch league-wide FG% by shot zone for normalization.

    Returns the denominator data needed for shot_quality_vs_league().
    Zone keys match Shot.shot_zone_basic for direct comparison.

    Args:
        client: NBA API client.
        season: Season in YYYY-YY format (defaults to current season).

    Returns:
        List of LeagueWideShotZone with zone name, FGA, FGM, and FG%.
    """
    from fastbreak.endpoints import ShotChartLeaguewide  # noqa: PLC0415

    season = season or get_season_from_date()
    response: ShotChartLeaguewideResponse = await client.get(
        ShotChartLeaguewide(season=season)
    )
    return response.league_wide
