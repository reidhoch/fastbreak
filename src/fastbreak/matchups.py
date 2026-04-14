"""Matchup analysis helpers for the NBA Stats API.

Provides player-vs-player matchup data, defensive assignment analysis,
and team matchup summaries. Wraps LeagueSeasonMatchups, MatchupsRollup,
BoxScoreMatchupsV3, and PlayerVsPlayer endpoints.

Examples::

    from fastbreak.clients import BaseClient
    from fastbreak.matchups import get_primary_defenders, matchup_ppp

    async with NBAClient() as client:
        defenders = await get_primary_defenders(client, player_id=2544, top_n=5)

    ppp = matchup_ppp(player_pts=12.0, partial_poss=8.5)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.box_score_matchups_v3 import BoxScoreMatchupsV3Response
    from fastbreak.models.league_season_matchups import SeasonMatchup
    from fastbreak.models.matchups_rollup import MatchupRollupEntry
    from fastbreak.models.player_vs_player import PlayerVsPlayerResponse
    from fastbreak.types import MeasureType, PerMode, Season, SeasonType


def matchup_ppp(player_pts: float, partial_poss: float) -> float | None:
    """Points per possession in matchup situations.

    Returns None if partial_poss <= 0.
    """
    if partial_poss <= 0:
        return None
    return player_pts / partial_poss


def help_defense_rate(matchup_fga: float, help_fga: float) -> float | None:
    """Fraction of opponent shots that involved help defense (0-1).

    Returns None if total FGA is 0.
    """
    total = matchup_fga + help_fga
    if total <= 0:
        return None
    return help_fga / total


def rank_matchups(
    matchups: list[SeasonMatchup],
    *,
    min_poss: float = 10.0,
    by: Literal["matchup_fg_pct", "ppp"] = "matchup_fg_pct",
    ascending: bool = True,
) -> list[SeasonMatchup]:
    """Sort matchups by effectiveness, filtering below a volume threshold.

    Matchups below min_poss partial possessions are excluded.
    Matchups with None for the sort key are excluded.
    """
    filtered = [m for m in matchups if m.partial_poss >= min_poss]

    if by == "ppp":
        keyed = [(m, matchup_ppp(m.player_pts, m.partial_poss)) for m in filtered]
        keyed = [(m, k) for m, k in keyed if k is not None]
        keyed.sort(key=lambda x: x[1], reverse=not ascending)  # type: ignore[arg-type,return-value]
        return [m for m, _ in keyed]

    # Default: sort by matchup FG%
    valid = [m for m in filtered if m.matchup_fg_pct is not None]
    valid.sort(key=lambda m: m.matchup_fg_pct, reverse=not ascending)  # type: ignore[arg-type,return-value]
    return valid


async def get_season_matchups(  # noqa: PLR0913
    client: BaseClient,
    *,
    off_player_id: int | None = None,
    def_player_id: int | None = None,
    off_team_id: int | None = None,
    def_team_id: int | None = None,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[SeasonMatchup]:
    """Season-long player-vs-player matchup stats.

    Wraps LeagueSeasonMatchups. At least one filter (player or team ID)
    should be provided; passing no filters returns league-wide data.
    """
    from fastbreak.endpoints import LeagueSeasonMatchups  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    response = await client.get(
        LeagueSeasonMatchups(
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            off_player_id=str(off_player_id) if off_player_id is not None else None,
            def_player_id=str(def_player_id) if def_player_id is not None else None,
            off_team_id=str(off_team_id) if off_team_id is not None else None,
            def_team_id=str(def_team_id) if def_team_id is not None else None,
            league_id=client.league_id,
        )
    )
    return response.matchups


async def get_matchup_rollup(  # noqa: PLR0913
    client: BaseClient,
    *,
    off_team_id: int = 0,
    def_team_id: int = 0,
    off_player_id: int = 0,
    def_player_id: int = 0,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[MatchupRollupEntry]:
    """Defender-aggregated matchup stats.

    Wraps MatchupsRollup. Includes percent_of_time and position fields.
    Pass 0 for any ID parameter to mean "all" (endpoint convention).
    """
    from fastbreak.endpoints import MatchupsRollup  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    response = await client.get(
        MatchupsRollup(
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            off_team_id=off_team_id,
            def_team_id=def_team_id,
            off_player_id=off_player_id,
            def_player_id=def_player_id,
            league_id=client.league_id,
        )
    )
    return response.matchups


async def get_game_matchups(
    client: BaseClient,
    game_id: str,
) -> BoxScoreMatchupsV3Response:
    """Per-game player-vs-player defensive matchup data.

    Wraps BoxScoreMatchupsV3 (the preferred v3 endpoint).
    """
    from fastbreak.endpoints import BoxScoreMatchupsV3  # noqa: PLC0415

    return await client.get(BoxScoreMatchupsV3(game_id=game_id))


async def get_player_matchup_stats(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    vs_player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    measure_type: MeasureType = "Base",
) -> PlayerVsPlayerResponse:
    """Detailed head-to-head comparison with on/off splits and shot areas.

    Wraps PlayerVsPlayer. Requires both player IDs.
    """
    from fastbreak.endpoints import PlayerVsPlayer  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    return await client.get(
        PlayerVsPlayer(
            player_id=str(player_id),
            vs_player_id=str(vs_player_id),
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            measure_type=measure_type,
            league_id=client.league_id,
        )
    )


async def get_primary_defenders(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    top_n: int = 5,
) -> list[SeasonMatchup]:
    """Who guards this player? Sorted by matchup minutes descending."""
    matchups = await get_season_matchups(
        client,
        off_player_id=player_id,
        season=season,
        season_type=season_type,
        per_mode=per_mode,
    )
    matchups.sort(key=lambda m: m.matchup_min, reverse=True)
    return matchups[:top_n]


async def get_defensive_assignments(  # noqa: PLR0913
    client: BaseClient,
    defender_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    top_n: int = 5,
) -> list[SeasonMatchup]:
    """Who does this defender guard? Sorted by matchup minutes descending."""
    matchups = await get_season_matchups(
        client,
        def_player_id=defender_id,
        season=season,
        season_type=season_type,
        per_mode=per_mode,
    )
    matchups.sort(key=lambda m: m.matchup_min, reverse=True)
    return matchups[:top_n]


async def get_team_matchup_summary(  # noqa: PLR0913
    client: BaseClient,
    off_team_id: int,
    def_team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[SeasonMatchup]:
    """All player-vs-player matchups between two teams.

    Returns the full list — apply rank_matchups() to filter/sort.
    """
    return await get_season_matchups(
        client,
        off_team_id=off_team_id,
        def_team_id=def_team_id,
        season=season,
        season_type=season_type,
        per_mode=per_mode,
    )
