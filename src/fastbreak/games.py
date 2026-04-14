"""Game lookup utilities for the NBA Stats API."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from fastbreak.league import League
from fastbreak.logging import logger
from fastbreak.seasons import get_season_from_date
from fastbreak.types import validate_iso_date

_ET = ZoneInfo("America/New_York")

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from fastbreak.clients.base import BaseClient
    from fastbreak.models.box_score_advanced import BoxScoreAdvancedData
    from fastbreak.models.box_score_four_factors import BoxScoreFourFactorsData
    from fastbreak.models.box_score_hustle import BoxScoreHustleData
    from fastbreak.models.box_score_scoring import BoxScoreScoringData
    from fastbreak.models.box_score_summary import BoxScoreSummaryData
    from fastbreak.models.box_score_traditional import BoxScoreTraditionalData
    from fastbreak.models.play_by_play import PlayByPlayAction
    from fastbreak.models.scoreboard_v3 import ScoreboardGame
    from fastbreak.types import Date, ISODate, Season, SeasonType


async def get_game_ids(  # noqa: PLR0913
    client: BaseClient,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
    team_id: int | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
) -> list[str]:
    """Return sorted, deduplicated game IDs for a season.

    Uses LeagueGameLog (team-level) as the source. Because the log contains
    one row per team per game, game IDs are deduplicated before returning.

    The NBA API's TeamID parameter on leaguegamelog is silently ignored, so
    team filtering is applied client-side after fetching.

    Args:
        client: NBA API client
        season: Season in YYYY-YY format (defaults to current season)
        season_type: "Regular Season", "Playoffs", etc.
        team_id: Restrict to a specific team's games (None = all teams)
        date_from: Only include games on or after this date (MM/DD/YYYY)
        date_to: Only include games on or before this date (MM/DD/YYYY)

    Returns:
        Sorted list of unique game ID strings (ascending / chronological)

    Examples:
        ids = await get_game_ids(client, "2024-25")
        playoff_ids = await get_game_ids(client, "2024-25", season_type="Playoffs")
        ind_ids = await get_game_ids(client, "2024-25", team_id=1610612754)

    """
    from fastbreak.endpoints import LeagueGameLog  # noqa: PLC0415

    season = season or get_season_from_date()
    endpoint = LeagueGameLog(
        season=season,
        season_type=season_type,
        player_or_team="T",
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
    )
    response = await client.get(endpoint)
    entries = response.games
    if team_id is not None:
        entries = [e for e in entries if e.team_id == team_id]
        if not entries:
            logger.debug(
                "get_game_ids_team_filter_empty", team_id=team_id, season=season
            )
    return sorted({entry.game_id for entry in entries})


async def get_games_on_date(
    client: BaseClient,
    game_date: ISODate,
) -> list[ScoreboardGame]:
    """Return all games scheduled on a specific date.

    Args:
        client: NBA API client
        game_date: Date in YYYY-MM-DD format (e.g., "2025-01-15")

    Returns:
        List of ScoreboardGame objects for that date

    Raises:
        ValueError: If game_date is not in YYYY-MM-DD format, or is not a
            valid calendar date (e.g., "2025-02-30").

    Examples:
        games = await get_games_on_date(client, "2025-01-15")
        for game in games:
            print(game.game_status_text)

    """
    validate_iso_date(game_date)

    from fastbreak.endpoints import ScoreboardV3  # noqa: PLC0415

    response = await client.get(ScoreboardV3(game_date=game_date))
    scoreboard = response.scoreboard
    if scoreboard is None:
        logger.warning(
            "scoreboard_missing_from_response",
            game_date=game_date,
            hint="API returned no scoreboard for this date; this may indicate an API error or an off-day",
        )
        return []
    return scoreboard.games


async def get_todays_games(client: BaseClient) -> list[ScoreboardGame]:
    """Return all games scheduled for today.

    Args:
        client: NBA API client

    Returns:
        List of ScoreboardGame objects for today

    Examples:
        games = await get_todays_games(client)

    """
    return await get_games_on_date(client, datetime.now(tz=_ET).date().isoformat())


async def get_yesterdays_games(client: BaseClient) -> list[ScoreboardGame]:
    """Return all games that were scheduled for yesterday.

    Args:
        client: NBA API client

    Returns:
        List of ScoreboardGame objects for yesterday

    Examples:
        games = await get_yesterdays_games(client)

    """
    today = datetime.now(tz=_ET).date()
    return await get_games_on_date(client, (today - timedelta(days=1)).isoformat())


async def get_game_summary(
    client: BaseClient,
    game_id: str,
) -> BoxScoreSummaryData:
    """Return the box score summary for a single game.

    Args:
        client: NBA API client
        game_id: NBA game ID string

    Returns:
        BoxScoreSummaryData containing game metadata, team info, officials, etc.

    Examples:
        summary = await get_game_summary(client, "0022400001")

    """
    from fastbreak.endpoints import BoxScoreSummary  # noqa: PLC0415

    response = await client.get(BoxScoreSummary(game_id=game_id))
    return response.boxScoreSummary


async def _batch_box_scores[T](
    client: BaseClient,
    game_ids: list[str],
    endpoint_cls: type[Any],
    accessor: Callable[[Any], T],
) -> dict[str, T]:
    """Batch-fetch box score data for multiple games and return as a dict."""
    if not game_ids:
        return {}
    endpoints = [endpoint_cls(game_id=gid) for gid in game_ids]
    responses = await client.get_many(endpoints)
    return {gid: accessor(resp) for gid, resp in zip(game_ids, responses, strict=True)}


async def get_box_scores(
    client: BaseClient,
    game_ids: list[str],
) -> dict[str, BoxScoreTraditionalData]:
    """Fetch traditional box scores for multiple games concurrently.

    Args:
        client: NBA API client
        game_ids: List of NBA game ID strings

    Returns:
        Dict mapping game_id -> BoxScoreTraditionalData, in input order

    Examples:
        ids = await get_game_ids(client, "2024-25")
        box_scores = await get_box_scores(client, ids[:5])

    """
    from fastbreak.endpoints import BoxScoreTraditional  # noqa: PLC0415

    return await _batch_box_scores(
        client, game_ids, BoxScoreTraditional, lambda r: r.boxScoreTraditional
    )


async def get_box_scores_advanced(
    client: BaseClient,
    game_ids: list[str],
) -> dict[str, BoxScoreAdvancedData]:
    """Fetch advanced box scores for multiple games concurrently.

    Args:
        client: NBA API client
        game_ids: List of NBA game ID strings

    Returns:
        Dict mapping game_id -> BoxScoreAdvancedData, in input order

    Examples:
        ids = await get_game_ids(client, "2024-25")
        box_scores = await get_box_scores_advanced(client, ids[:5])

    """
    from fastbreak.endpoints import BoxScoreAdvanced  # noqa: PLC0415

    return await _batch_box_scores(
        client, game_ids, BoxScoreAdvanced, lambda r: r.boxScoreAdvanced
    )


async def get_box_scores_hustle(
    client: BaseClient,
    game_ids: list[str],
) -> dict[str, BoxScoreHustleData]:
    """Fetch hustle box scores for multiple games concurrently.

    Args:
        client: NBA API client
        game_ids: List of NBA game ID strings

    Returns:
        Dict mapping game_id -> BoxScoreHustleData, in input order

    Examples:
        ids = await get_game_ids(client, "2024-25")
        box_scores = await get_box_scores_hustle(client, ids[:5])

    """
    from fastbreak.endpoints import BoxScoreHustle  # noqa: PLC0415

    return await _batch_box_scores(
        client, game_ids, BoxScoreHustle, lambda r: r.box_score_hustle
    )


async def get_box_scores_scoring(
    client: BaseClient,
    game_ids: list[str],
) -> dict[str, BoxScoreScoringData]:
    """Fetch scoring distribution box scores for multiple games concurrently.

    Args:
        client: NBA API client
        game_ids: List of NBA game ID strings

    Returns:
        Dict mapping game_id -> BoxScoreScoringData, in input order

    Examples:
        ids = await get_game_ids(client, "2024-25")
        box_scores = await get_box_scores_scoring(client, ids[:5])

    """
    from fastbreak.endpoints import BoxScoreScoring  # noqa: PLC0415

    return await _batch_box_scores(
        client, game_ids, BoxScoreScoring, lambda r: r.boxScoreScoring
    )


async def get_box_scores_four_factors(
    client: BaseClient,
    game_ids: list[str],
) -> dict[str, BoxScoreFourFactorsData]:
    """Fetch four factors box scores for multiple games concurrently.

    Args:
        client: NBA API client
        game_ids: List of NBA game ID strings

    Returns:
        Dict mapping game_id -> BoxScoreFourFactorsData, in input order

    Examples:
        ids = await get_game_ids(client, "2025-26")
        box_scores = await get_box_scores_four_factors(client, ids[:5])

    """
    from fastbreak.endpoints import BoxScoreFourFactors  # noqa: PLC0415

    return await _batch_box_scores(
        client, game_ids, BoxScoreFourFactors, lambda r: r.boxScoreFourFactors
    )


async def get_play_by_play(
    client: BaseClient,
    game_id: str,
) -> list[PlayByPlayAction]:
    """Return all play-by-play actions for a game.

    Args:
        client: NBA API client
        game_id: NBA game ID string

    Returns:
        List of PlayByPlayAction objects in the order returned by the API
        (typically chronological by actionNumber)

    Examples:
        actions = await get_play_by_play(client, "0022400001")
        shots = [a for a in actions if a.actionType == "2pt"]

    """
    from fastbreak.endpoints import PlayByPlay  # noqa: PLC0415

    response = await client.get(PlayByPlay(game_id=game_id))
    return response.game.actions


@dataclass(frozen=True, slots=True)
class GameFlowPoint:
    """Score state after a scoring event in a game.

    Attributes:
        period: Period number (1-4 for regulation, 5+ for overtime).
        clock: Remaining time in the period as an ISO 8601 duration
            (e.g., ``"PT04M32.00S"``).
        elapsed_seconds: Seconds elapsed since tip-off. Regulation periods
            are 12 minutes (720 s) each; overtime periods are 5 minutes
            (300 s) each.
        score_home: Home team cumulative score at this point.
        score_away: Away team cumulative score at this point.
        margin: ``score_home - score_away`` (positive = home leading).
        description: Play description from the API.
    """

    period: int
    clock: str
    elapsed_seconds: float
    score_home: int
    score_away: int
    margin: int
    description: str


_CLOCK_RE = re.compile(r"PT(\d+)M([\d.]+)S")
_REGULATION_PERIODS = 4  # Q1-Q4
_OT_PERIOD_SECONDS = 300  # 5 minutes (same for NBA and WNBA)


def _parse_clock(clock: str) -> float:
    """Return remaining seconds in the current period from an ISO 8601 duration."""
    m = _CLOCK_RE.match(clock)
    if not m:
        return 0.0
    return int(m.group(1)) * 60 + float(m.group(2))


def elapsed_game_seconds(
    clock: str, period: int, *, league: League = League.NBA
) -> float:
    """Return seconds elapsed since tip-off from a game clock and period.

    Regulation periods (1-4) use league-specific quarter lengths:
    NBA = 12 minutes (720 seconds), WNBA = 10 minutes (600 seconds).
    Overtime periods (5+) are 5 minutes (300 seconds) for both leagues.

    Args:
        clock: ISO 8601 duration string (e.g., ``"PT04M32.00S"``).
        period: Period number (1-4 regulation, 5+ overtime).
        league: League configuration for quarter length (default: NBA).

    Returns:
        Total seconds elapsed since the start of the game.

    Examples:
        >>> elapsed_game_seconds("PT12M00.00S", 1)
        0.0
        >>> elapsed_game_seconds("PT00M00.00S", 4)
        2880.0
        >>> elapsed_game_seconds("PT05M00.00S", 5)
        2880.0

    """
    if period < 1:
        return 0.0
    remaining = _parse_clock(clock)
    quarter_seconds = league.quarter_seconds
    if period <= _REGULATION_PERIODS:
        period_offset = (period - 1) * quarter_seconds
        period_duration = quarter_seconds
    else:
        period_offset = (
            _REGULATION_PERIODS * quarter_seconds
            + (period - _REGULATION_PERIODS - 1) * _OT_PERIOD_SECONDS
        )
        period_duration = _OT_PERIOD_SECONDS
    return period_offset + (period_duration - remaining)


def game_flow(actions: list[PlayByPlayAction]) -> list[GameFlowPoint]:
    """Build a score-line timeline from a list of play-by-play actions.

    Filters to scoring events (actions where both ``scoreHome`` and
    ``scoreAway`` are non-empty strings), converts each to a
    :class:`GameFlowPoint`, and returns them in the order they appear in
    ``actions`` (typically chronological by ``actionNumber``).

    Elapsed time is computed from period and remaining clock:

    - Regulation periods (1-4): 12 minutes (720 seconds) each.
    - Overtime periods (5+): 5 minutes (300 seconds) each.

    Args:
        actions: List of PlayByPlayAction objects, e.g., from
            :func:`get_play_by_play`.

    Returns:
        List of :class:`GameFlowPoint` objects, one per scoring event,
        in chronological order. Returns an empty list if ``actions``
        contains no scoring events.

    Examples:
        actions = await get_play_by_play(client, "0022500571")
        flow = game_flow(actions)

        # Largest lead at any point in regulation
        reg = [p for p in flow if p.period <= 4]
        max_lead = max(abs(p.margin) for p in reg) if reg else 0

        # Final score
        if flow:
            last = flow[-1]
            print(f"Home {last.score_home} - Away {last.score_away}")

    """
    result: list[GameFlowPoint] = []
    for action in actions:
        if not action.scoreHome or not action.scoreAway:
            continue
        try:
            score_home = int(action.scoreHome)
            score_away = int(action.scoreAway)
        except ValueError:
            continue

        elapsed = elapsed_game_seconds(action.clock, action.period)
        result.append(
            GameFlowPoint(
                period=action.period,
                clock=action.clock,
                elapsed_seconds=elapsed,
                score_home=score_home,
                score_away=score_away,
                margin=score_home - score_away,
                description=action.description,
            )
        )

    return result
