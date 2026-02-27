"""Schedule utilities for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastbreak.logging import logger

if TYPE_CHECKING:
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.schedule_league_v2 import LeagueSchedule, ScheduledGame
    from fastbreak.types import Season


def days_rest_before_game(game_dates: list[date], game_index: int) -> int | None:
    """Return days of rest before the game at game_index.

    Args:
        game_dates: Sorted list of game dates for a team.
        game_index: Index of the game to check (0-based).

    Returns:
        Days between previous game and this game minus 1,
        or None if this is the team's first game.

    Examples:
        # Back-to-back (Jan 15 -> Jan 16): 0 days rest
        days = days_rest_before_game([date(2025,1,15), date(2025,1,16)], 1)
        # => 0
    """
    if game_index == 0:
        return None
    delta = game_dates[game_index] - game_dates[game_index - 1]
    return max(0, delta.days - 1)


def is_back_to_back(game_dates: list[date], game_index: int) -> bool:
    """Return True if the game at game_index is a back-to-back.

    Args:
        game_dates: Sorted list of game dates for a team.
        game_index: Index of the game to check (0-based).

    Returns:
        True if days_rest_before_game == 0 (played the night before).
    """
    rest = days_rest_before_game(game_dates, game_index)
    return rest == 0


def _schedule_sort_key(g: ScheduledGame) -> str:
    """Return the sort key for a scheduled game; games missing a date sort last."""
    if g.game_date_est is None:
        logger.warning(
            "game_missing_date_est",
            game_id=getattr(g, "game_id", "unknown"),
            hint="Game has no game_date_est; sorting to end of schedule",
        )
        return "9999-99-99"  # invalid ISO date, sorts lexicographically after all real dates
    return g.game_date_est


def _collect_team_games(
    league_schedule: LeagueSchedule, team_id: int
) -> list[ScheduledGame]:
    """Return all games in a league schedule that involve the given team."""
    games: list[ScheduledGame] = []
    for game_date in league_schedule.game_dates:
        for game in game_date.games:
            home_id = game.home_team.team_id if game.home_team is not None else None
            away_id = game.away_team.team_id if game.away_team is not None else None
            if team_id in (home_id, away_id):
                games.append(game)
    return games


async def get_team_schedule(
    client: NBAClient,
    team_id: int,
    season: Season | None = None,
) -> list[ScheduledGame]:
    """Return all scheduled games for a team in a season, sorted by date.

    Args:
        client: NBA API client
        team_id: NBA team ID
        season: Season in YYYY-YY format (defaults to current season)

    Returns:
        List of ScheduledGame objects in chronological order

    Examples:
        games = await get_team_schedule(client, 1610612747, "2024-25")
    """
    from fastbreak.endpoints import ScheduleLeagueV2  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(ScheduleLeagueV2(season=season))

    if response.league_schedule is None:
        logger.warning(
            "league_schedule_missing_from_response",
            team_id=team_id,
            season=season,
            hint="Response contained no league_schedule; returning empty list",
        )
        return []

    team_games = _collect_team_games(response.league_schedule, team_id)
    team_games.sort(key=_schedule_sort_key)
    return team_games
