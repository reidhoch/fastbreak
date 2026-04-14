"""Schedule utilities for the NBA Stats API."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastbreak.logging import logger
from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from fastbreak.clients.base import BaseClient
    from fastbreak.models.schedule_league_v2 import LeagueSchedule, ScheduledGame
    from fastbreak.types import Season


def _validate_game_index(game_dates: Sequence[date], game_index: int) -> None:
    """Raise IndexError if *game_index* is out of range for *game_dates*."""
    if game_index < 0 or game_index >= len(game_dates):
        msg = f"game_index {game_index} out of range for {len(game_dates)} games"
        raise IndexError(msg)


def days_rest_before_game(game_dates: Sequence[date], game_index: int) -> int | None:
    """Return days of rest before the game at game_index.

    Args:
        game_dates: Sorted list of game dates for a team.
        game_index: Index of the game to check (0-based).

    Returns:
        Days between previous game and this game minus 1,
        or None if this is the team's first game.

    Raises:
        IndexError: If *game_index* is out of range.

    Examples:
        # Back-to-back (Jan 15 -> Jan 16): 0 days rest
        days = days_rest_before_game([date(2025,1,15), date(2025,1,16)], 1)
        # => 0
    """
    _validate_game_index(game_dates, game_index)
    if game_index == 0:
        return None
    delta = game_dates[game_index] - game_dates[game_index - 1]
    return max(0, delta.days - 1)


def is_back_to_back(game_dates: Sequence[date], game_index: int) -> bool:
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


def game_dates_from_schedule(games: Sequence[ScheduledGame]) -> list[date]:
    """Extract a sorted list of dates from scheduled games.

    Skips games with ``None`` ``game_date_est`` and any games whose
    ``game_date_est`` cannot be parsed as a date.  Uses the first 10
    characters of the ISO-formatted ``game_date_est`` string to parse
    the date portion.  Malformed values are logged and excluded rather
    than raising.

    Args:
        games: Scheduled games (from :func:`get_team_schedule` or
               :func:`get_season_schedule`).

    Returns:
        Sorted list of :class:`~datetime.date` objects.
    """
    from datetime import date as _date  # noqa: PLC0415

    dates: list[_date] = []
    skipped = 0
    for g in games:
        if g.game_date_est is None:
            skipped += 1
            continue
        try:
            dates.append(_date.fromisoformat(g.game_date_est[:10]))
        except ValueError:
            skipped += 1
            logger.warning(
                "game_date_parse_failed",
                game_id=getattr(g, "game_id", "unknown"),
                raw_date=g.game_date_est,
                hint="Could not parse game_date_est; skipping game",
            )
    if skipped:
        logger.debug(
            "game_dates_skipped",
            skipped=skipped,
            total=len(games),
        )
    dates.sort()
    return dates


def is_home_game(game: ScheduledGame, team_id: int) -> bool:
    """Return True if *team_id* is the home team for *game*."""
    return game.home_team is not None and game.home_team.team_id == team_id


def rest_advantage(
    home_dates: Sequence[date],
    away_dates: Sequence[date],
    game_date: date,
) -> int | None:
    """Compute home-team rest advantage for a specific *game_date*.

    Returns ``home_rest - away_rest``.  Positive means the home team is
    more rested.  Returns ``None`` when *game_date* is missing from
    either list, or when either team has no prior game (first game of
    season).
    """
    try:
        home_idx = home_dates.index(game_date)
    except ValueError:
        logger.debug(
            "rest_advantage_date_not_in_home",
            game_date=str(game_date),
        )
        return None
    try:
        away_idx = away_dates.index(game_date)
    except ValueError:
        logger.debug(
            "rest_advantage_date_not_in_away",
            game_date=str(game_date),
        )
        return None

    home_rest = days_rest_before_game(home_dates, home_idx)
    away_rest = days_rest_before_game(away_dates, away_idx)

    if home_rest is None or away_rest is None:
        return None
    return home_rest - away_rest


def schedule_density(
    game_dates: Sequence[date],
    game_index: int,
    window: int = 7,
) -> int:
    """Count games in the *window*-day period ending on ``game_dates[game_index]``.

    Scans backward from *game_index* while the date delta is <= *window* - 1
    days.  The game at *game_index* always counts, so the minimum return
    value is ``1``.

    Args:
        game_dates: Sorted list of game dates for a team.
        game_index: Index of the anchor game.
        window:     Window size in days (default 7).  Must be ≥ 1.

    Returns:
        Number of games (≥ 1) in the window.

    Raises:
        ValueError: If *window* < 1.
        IndexError: If *game_index* is out of range.
    """
    if window < 1:
        msg = f"window must be >= 1, got {window}"
        raise ValueError(msg)
    _validate_game_index(game_dates, game_index)

    anchor = game_dates[game_index]
    count = 1  # the game itself
    for i in range(game_index - 1, -1, -1):
        if (anchor - game_dates[i]).days <= window - 1:
            count += 1
        else:
            break
    return count


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


def _flatten_schedule(league_schedule: LeagueSchedule) -> list[ScheduledGame]:
    """Return all games from a league schedule as a flat list."""
    return [g for gd in league_schedule.game_dates for g in gd.games]


def _collect_team_games(
    league_schedule: LeagueSchedule, team_id: int
) -> list[ScheduledGame]:
    """Return all games in a league schedule that involve the given team."""
    result: list[ScheduledGame] = []
    for game in _flatten_schedule(league_schedule):
        home_id = game.home_team.team_id if game.home_team is not None else None
        away_id = game.away_team.team_id if game.away_team is not None else None
        if team_id in (home_id, away_id):
            result.append(game)
    return result


async def _fetch_league_schedule(
    client: BaseClient, season: Season | None, **log_ctx: object
) -> LeagueSchedule | None:
    """Fetch the league schedule, returning ``None`` (with warning) when the response contains no ``league_schedule``."""
    from fastbreak.endpoints import ScheduleLeagueV2  # noqa: PLC0415

    season = season or get_season_from_date(league=client.league)
    response = await client.get(
        ScheduleLeagueV2(season=season, league_id=client.league_id)
    )

    if response.league_schedule is None:
        logger.warning(
            "league_schedule_missing_from_response",
            season=season,
            hint="Response contained no league_schedule; returning empty list",
            **log_ctx,
        )
        return None
    return response.league_schedule


async def get_team_schedule(
    client: BaseClient,
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
    league_schedule = await _fetch_league_schedule(client, season, team_id=team_id)
    if league_schedule is None:
        return []

    team_games = _collect_team_games(league_schedule, team_id)
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
# Brooklyn and New York are separate.
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
    ("Inglewood", "CA"): (33.9581, -118.3413, -8),  # Intuit Dome (LAC)
    ("Los Angeles", "CA"): (34.0430, -118.2673, -8),  # Crypto.com Arena (LAL)
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
    # WNBA-only arenas (arenas shared with NBA teams are already listed above)
    ("Uncasville", "CT"): (41.4487, -72.1171, -5),  # Mohegan Sun Arena (Sun)
    ("Arlington", "TX"): (32.7514, -97.0825, -6),  # College Park Center (Wings)
    ("Las Vegas", "NV"): (36.0909, -115.1784, -8),  # Michelob Ultra Arena (Aces)
    ("Seattle", "WA"): (47.6222, -122.3541, -8),  # Climate Pledge Arena (Storm)
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
        logger.debug(
            "arena_coords_not_found",
            current_city=current.arena_city,
            current_state=current.arena_state,
            previous_city=previous.arena_city,
            previous_state=previous.arena_state,
        )
        return None

    orig_lat, orig_lon, orig_tz = origin
    dest_lat, dest_lon, dest_tz = dest
    return TravelLeg(
        miles=_haversine_miles(orig_lat, orig_lon, dest_lat, dest_lon),
        tz_shift=dest_tz - orig_tz,
    )


def travel_distance(
    games: Sequence[ScheduledGame],
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
    games: Sequence[ScheduledGame],
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


async def get_season_schedule(
    client: BaseClient,
    *,
    season: Season | None = None,
) -> list[ScheduledGame]:
    """Return the full league schedule for a season, sorted chronologically.

    Unlike :func:`get_team_schedule` this returns **all** games across
    all teams with no team filter.

    Args:
        client: NBA API client.
        season: Season in ``YYYY-YY`` format (defaults to current season).

    Returns:
        List of :class:`ScheduledGame` in chronological order, or ``[]``
        if the API response contains no ``league_schedule``.
    """
    league_schedule = await _fetch_league_schedule(client, season)
    if league_schedule is None:
        return []

    all_games = _flatten_schedule(league_schedule)
    all_games.sort(key=_schedule_sort_key)
    return all_games
