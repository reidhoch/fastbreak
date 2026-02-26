"""Game lookup utilities for the NBA Stats API."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.box_score_summary import BoxScoreSummaryData
    from fastbreak.models.box_score_traditional import BoxScoreTraditionalData
    from fastbreak.models.play_by_play import PlayByPlayAction
    from fastbreak.models.scoreboard_v3 import ScoreboardGame
    from fastbreak.types import Date, SeasonType


async def get_game_ids(  # noqa: PLR0913
    client: NBAClient,
    season: str | None = None,
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
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

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
    return sorted({entry.game_id for entry in entries})


async def get_games_on_date(
    client: NBAClient,
    game_date: str,
) -> list[ScoreboardGame]:
    """Return all games scheduled on a specific date.

    Args:
        client: NBA API client
        game_date: Date in YYYY-MM-DD format (e.g., "2025-01-15")

    Returns:
        List of ScoreboardGame objects for that date

    Examples:
        games = await get_games_on_date(client, "2025-01-15")
        for game in games:
            print(game.game_status_text)

    """
    try:
        date.fromisoformat(game_date)
    except ValueError:
        msg = f"Invalid game_date: {game_date!r}. Expected YYYY-MM-DD format (e.g., '2025-01-15')."
        raise ValueError(msg) from None

    from fastbreak.endpoints import ScoreboardV3  # noqa: PLC0415

    response = await client.get(ScoreboardV3(game_date=game_date))
    scoreboard = response.scoreboard
    if scoreboard is None:
        return []
    return scoreboard.games


async def get_todays_games(client: NBAClient) -> list[ScoreboardGame]:
    """Return all games scheduled for today.

    Args:
        client: NBA API client

    Returns:
        List of ScoreboardGame objects for today

    Examples:
        games = await get_todays_games(client)

    """
    return await get_games_on_date(client, date.today().isoformat())  # noqa: DTZ011


async def get_game_summary(
    client: NBAClient,
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


async def get_box_scores(
    client: NBAClient,
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

    if not game_ids:
        return {}

    endpoints = [BoxScoreTraditional(game_id=gid) for gid in game_ids]
    responses = await client.get_many(endpoints)
    return {
        gid: resp.boxScoreTraditional
        for gid, resp in zip(game_ids, responses, strict=True)
    }


async def get_play_by_play(
    client: NBAClient,
    game_id: str,
) -> list[PlayByPlayAction]:
    """Return all play-by-play actions for a game.

    Args:
        client: NBA API client
        game_id: NBA game ID string

    Returns:
        List of PlayByPlayAction objects in chronological order

    Examples:
        actions = await get_play_by_play(client, "0022400001")
        shots = [a for a in actions if a.actionType == "2pt"]

    """
    from fastbreak.endpoints import PlayByPlay  # noqa: PLC0415

    response = await client.get(PlayByPlay(game_id=game_id))
    return response.game.actions
