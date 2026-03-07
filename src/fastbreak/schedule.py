"""Schedule utilities for the NBA Stats API."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastbreak.logging import logger
from fastbreak.seasons import get_season_from_date

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


_SORT_LAST: str = (
    "9999-99-99"  # invalid ISO date, sorts lexicographically after all real dates
)


def _schedule_sort_key(g: ScheduledGame) -> str:
    """Return the sort key for a scheduled game; games missing a date sort last."""
    if g.game_date_est is None:
        logger.warning(
            "game_missing_date_est",
            game_id=getattr(g, "game_id", "unknown"),
            hint="Game has no game_date_est; sorting to end of schedule",
        )
        return _SORT_LAST
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


@dataclass(frozen=True, slots=True)
class TravelLeg:
    """Distance and time-zone shift for a single team travel leg.

    Attributes:
        miles:    Great-circle distance in miles between the two arenas.
        tz_shift: Time-zone shift in hours.  Positive = traveling east
                  (e.g. LA → Boston = +3); negative = traveling west.
                  Based on standard-time UTC offsets — DST does not affect
                  the *relative* shift between two US cities (both shift by
                  the same hour), except for Phoenix (AZ, no DST) vs
                  Mountain-time cities in summer.
    """

    miles: float
    tz_shift: int


# (arena_city, arena_state) → (latitude, longitude, utc_std_offset)
# Keys match the arenaCity / arenaState values returned by the NBA Stats API.
# Both LA teams share Crypto.com Arena; Brooklyn and New York are separate.
type ArenaCoord = tuple[float, float, int]

_ARENA_COORDS: dict[tuple[str, str], ArenaCoord] = {
    ("Atlanta", "GA"): (33.7573, -84.3963, -5),  # State Farm Arena
    ("Boston", "MA"): (42.3662, -71.0621, -5),  # TD Garden
    ("Brooklyn", "NY"): (40.6826, -73.9754, -5),  # Barclays Center
    ("Charlotte", "NC"): (35.2251, -80.8392, -5),  # Spectrum Center
    ("Chicago", "IL"): (41.8807, -87.6742, -6),  # United Center
    ("Cleveland", "OH"): (41.4965, -81.6882, -5),  # Rocket Mortgage Fieldhouse
    ("Dallas", "TX"): (32.7905, -96.8103, -6),  # American Airlines Center
    ("Denver", "CO"): (39.7487, -105.0076, -7),  # Ball Arena
    ("Detroit", "MI"): (42.3410, -83.0554, -5),  # Little Caesars Arena
    ("Houston", "TX"): (29.7508, -95.3621, -6),  # Toyota Center
    ("Indianapolis", "IN"): (39.7640, -86.1555, -5),  # Gainbridge Fieldhouse
    ("Los Angeles", "CA"): (34.0430, -118.2673, -8),  # Crypto.com Arena (LAL + LAC)
    ("Memphis", "TN"): (35.1383, -90.0505, -6),  # FedExForum
    ("Miami", "FL"): (25.7814, -80.1870, -5),  # Kaseya Center
    ("Milwaukee", "WI"): (43.0450, -87.9178, -6),  # Fiserv Forum
    ("Minneapolis", "MN"): (44.9795, -93.2760, -6),  # Target Center
    ("New Orleans", "LA"): (29.9490, -90.0821, -6),  # Smoothie King Center
    ("New York", "NY"): (40.7505, -73.9934, -5),  # Madison Square Garden
    ("Oklahoma City", "OK"): (35.4634, -97.5151, -6),  # Paycom Center
    ("Orlando", "FL"): (28.5392, -81.3837, -5),  # Kia Center
    ("Philadelphia", "PA"): (39.9012, -75.1720, -5),  # Wells Fargo Center
    ("Phoenix", "AZ"): (33.4457, -112.0712, -7),  # Footprint Center (no DST)
    ("Portland", "OR"): (45.5316, -122.6668, -8),  # Moda Center
    ("Sacramento", "CA"): (38.5802, -121.4996, -8),  # Golden 1 Center
    ("Salt Lake City", "UT"): (40.7683, -111.9011, -7),  # Delta Center
    ("San Antonio", "TX"): (29.4270, -98.4375, -6),  # Frost Bank Center
    ("San Francisco", "CA"): (37.7680, -122.3877, -8),  # Chase Center
    ("Toronto", "ON"): (43.6435, -79.3791, -5),  # Scotiabank Arena
    ("Washington", "DC"): (38.8981, -77.0209, -5),  # Capital One Arena
}

_EARTH_RADIUS_MILES: float = 3_958.8


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in miles between two (lat, lon) points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_MILES * math.asin(min(1.0, math.sqrt(a)))


def _compute_leg(current: ScheduledGame, previous: ScheduledGame) -> TravelLeg | None:
    """Compute a TravelLeg between two consecutive ScheduledGames.

    Returns None if either game has missing arena data or an unrecognised city.
    """
    if (
        current.arena_city is None
        or current.arena_state is None
        or previous.arena_city is None
        or previous.arena_state is None
    ):
        return None

    origin = _ARENA_COORDS.get((previous.arena_city, previous.arena_state))
    dest = _ARENA_COORDS.get((current.arena_city, current.arena_state))
    if origin is None or dest is None:
        return None

    orig_lat, orig_lon, orig_tz = origin
    dest_lat, dest_lon, dest_tz = dest
    return TravelLeg(
        miles=_haversine_miles(orig_lat, orig_lon, dest_lat, dest_lon),
        tz_shift=dest_tz - orig_tz,
    )


def travel_distance(
    games: list[ScheduledGame],
    game_id: str,
) -> TravelLeg | None:
    """Return travel distance and time-zone shift for a single game leg.

    Locates *game_id* in *games* (the team's sorted schedule from
    :func:`get_team_schedule`), then computes the great-circle distance in
    miles between that game's arena and the arena of the immediately preceding
    game in the schedule.

    For computing legs across many games prefer :func:`travel_distances`, which
    processes the full schedule in a single O(n) pass.

    Args:
        games:   Team's schedule sorted chronologically, as returned by
                 :func:`get_team_schedule`.
        game_id: NBA game ID of the destination game.

    Returns:
        :class:`TravelLeg` with ``miles`` (great-circle) and ``tz_shift``
        (hours east = positive, hours west = negative), or ``None`` when:

        - *game_id* is the team's first game (no prior leg),
        - *game_id* is not found in *games*,
        - either game's ``arena_city`` / ``arena_state`` is missing, or
        - a city is not in :data:`_ARENA_COORDS` (e.g. neutral-site games).

    Examples:
        schedule = await get_team_schedule(client, team_id=1610612747)
        leg = travel_distance(schedule, game_id="0022500131")
        if leg:
            print(f"{leg.miles:.0f} mi, {leg.tz_shift:+d}h")
    """
    idx = next((i for i, g in enumerate(games) if g.game_id == game_id), None)
    if idx is None or idx == 0:
        return None
    return _compute_leg(games[idx], games[idx - 1])


def travel_distances(
    games: list[ScheduledGame],
) -> dict[str, TravelLeg | None]:
    """Return travel legs for all games in a team's sorted schedule.

    Processes the schedule in a single O(n) pass.  Use this instead of
    calling :func:`travel_distance` in a loop to avoid O(n²) behaviour.

    Args:
        games: Team's schedule sorted chronologically, as returned by
               :func:`get_team_schedule`.

    Returns:
        Dict mapping each game's ``game_id`` to its :class:`TravelLeg`, or
        ``None`` for the first game, games with missing arena data, or
        unrecognised cities.  Games with a ``None`` ``game_id`` are omitted.

    Examples:
        schedule = await get_team_schedule(client, team_id=1610612747)
        legs = travel_distances(schedule)
        for game in schedule:
            if game.game_id:
                leg = legs.get(game.game_id)
    """
    result: dict[str, TravelLeg | None] = {}
    for i, game in enumerate(games):
        if game.game_id is None:
            # Game has no ID (cancelled / placeholder); skip the result entry but
            # keep it as the implicit predecessor so the next game's leg reflects
            # the correct arena-to-arena chain.  In practice these games also lack
            # arena_city / arena_state, so _compute_leg returns None for the next leg.
            continue
        result[game.game_id] = None if i == 0 else _compute_leg(game, games[i - 1])
    return result
