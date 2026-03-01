"""League standings helpers for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.league_standings import TeamStanding
    from fastbreak.types import Conference, Season, SeasonType


def magic_number(
    my_wins: int,
    opp_wins: int,
    opp_games_remaining: int,
) -> int:
    """Clinching magic number for the leading team over a specific opponent.

    Returns the number of wins by the leading team or losses by the opponent
    (in any combination) required for the leading team to guarantee finishing
    ahead of the opponent.

    A return value of 0 means the leading team has already clinched.

    Args:
        my_wins:             Wins for the leading team.
        opp_wins:            Current wins for the opponent.
        opp_games_remaining: Games the opponent has yet to play.

    Returns:
        Non-negative integer magic number.

    Examples:
        # With 50 wins, opponent at 48 wins with 15 games left:
        magic_number(my_wins=50, opp_wins=48, opp_games_remaining=15)  # → 14

        # Compute opp_games_remaining from a TeamStanding:
        #   opp_games_remaining = 82 - opp.wins - opp.losses
    """
    return max(0, 1 + opp_games_remaining + opp_wins - my_wins)


async def get_standings(
    client: NBAClient,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
) -> list[TeamStanding]:
    """Return league standings for all 30 teams.

    Args:
        client: NBA API client
        season: Season in YYYY-YY format (defaults to current season)
        season_type: "Regular Season", "Playoffs", or "Pre Season"

    Returns:
        List of TeamStanding entries in the order returned by the API
        (typically sorted by conference rank).

    Examples:
        standings = await get_standings(client)
        for s in standings:
            print(s.team_name, s.wins, s.losses)
    """
    from fastbreak.endpoints import LeagueStandings  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(LeagueStandings(season=season, season_type=season_type))
    return response.standings


async def get_conference_standings(
    client: NBAClient,
    conference: Conference,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
) -> list[TeamStanding]:
    """Return standings for a single conference, sorted by playoff rank.

    Args:
        client: NBA API client
        conference: "East" or "West"
        season: Season in YYYY-YY format (defaults to current season)
        season_type: "Regular Season", "Playoffs", or "Pre Season"

    Returns:
        List of TeamStanding entries for the requested conference,
        sorted ascending by playoff_rank (1 = best).

    Examples:
        east = await get_conference_standings(client, "East")
        print(east[0].team_name)  # 1-seed
    """
    standings = await get_standings(client, season=season, season_type=season_type)
    filtered = [s for s in standings if s.conference == conference]
    filtered.sort(key=lambda s: s.playoff_rank)
    return filtered
