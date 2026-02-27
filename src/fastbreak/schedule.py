"""Schedule utilities for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.schedule_league_v2 import ScheduledGame
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
        return []

    team_games: list[ScheduledGame] = []
    for game_date in response.league_schedule.game_dates:
        for game in game_date.games:
            home_id = game.home_team.team_id if game.home_team is not None else None
            away_id = game.away_team.team_id if game.away_team is not None else None
            if team_id in (home_id, away_id):
                team_games.append(game)

    def _sort_key(g: ScheduledGame) -> str:
        return g.game_date_est or ""

    team_games.sort(key=_sort_key)
    return team_games
