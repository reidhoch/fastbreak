"""Team data, lookup, and API utility functions for the NBA Stats API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.league_dash_team_stats import LeagueDashTeamStatsRow
    from fastbreak.models.team_dash_lineups import LineupStats
    from fastbreak.models.team_game_log import TeamGameLogEntry
    from fastbreak.types import PerMode, SeasonType


class TeamID(IntEnum):
    """NBA team IDs.

    These are the official team IDs used by the NBA Stats API.
    """

    # Eastern Conference - Atlantic Division
    CELTICS = 1610612738
    NETS = 1610612751
    KNICKS = 1610612752
    SIXERS = 1610612755
    RAPTORS = 1610612761

    # Eastern Conference - Central Division
    BULLS = 1610612741
    CAVALIERS = 1610612739
    PISTONS = 1610612765
    PACERS = 1610612754
    BUCKS = 1610612749

    # Eastern Conference - Southeast Division
    HAWKS = 1610612737
    HORNETS = 1610612766
    HEAT = 1610612748
    MAGIC = 1610612753
    WIZARDS = 1610612764

    # Western Conference - Northwest Division
    NUGGETS = 1610612743
    TIMBERWOLVES = 1610612750
    THUNDER = 1610612760
    TRAIL_BLAZERS = 1610612757
    JAZZ = 1610612762

    # Western Conference - Pacific Division
    WARRIORS = 1610612744
    CLIPPERS = 1610612746
    LAKERS = 1610612747
    SUNS = 1610612756
    KINGS = 1610612758

    # Western Conference - Southwest Division
    MAVERICKS = 1610612742
    ROCKETS = 1610612745
    GRIZZLIES = 1610612763
    PELICANS = 1610612740
    SPURS = 1610612759


@dataclass(frozen=True, slots=True)
class TeamInfo:
    """Static information about an NBA team."""

    id: int
    abbreviation: str
    city: str
    name: str
    full_name: str
    conference: str
    division: str


TEAMS: dict[int, TeamInfo] = {
    # Eastern Conference - Atlantic Division
    TeamID.CELTICS: TeamInfo(
        id=TeamID.CELTICS,
        abbreviation="BOS",
        city="Boston",
        name="Celtics",
        full_name="Boston Celtics",
        conference="East",
        division="Atlantic",
    ),
    TeamID.NETS: TeamInfo(
        id=TeamID.NETS,
        abbreviation="BKN",
        city="Brooklyn",
        name="Nets",
        full_name="Brooklyn Nets",
        conference="East",
        division="Atlantic",
    ),
    TeamID.KNICKS: TeamInfo(
        id=TeamID.KNICKS,
        abbreviation="NYK",
        city="New York",
        name="Knicks",
        full_name="New York Knicks",
        conference="East",
        division="Atlantic",
    ),
    TeamID.SIXERS: TeamInfo(
        id=TeamID.SIXERS,
        abbreviation="PHI",
        city="Philadelphia",
        name="76ers",
        full_name="Philadelphia 76ers",
        conference="East",
        division="Atlantic",
    ),
    TeamID.RAPTORS: TeamInfo(
        id=TeamID.RAPTORS,
        abbreviation="TOR",
        city="Toronto",
        name="Raptors",
        full_name="Toronto Raptors",
        conference="East",
        division="Atlantic",
    ),
    # Eastern Conference - Central Division
    TeamID.BULLS: TeamInfo(
        id=TeamID.BULLS,
        abbreviation="CHI",
        city="Chicago",
        name="Bulls",
        full_name="Chicago Bulls",
        conference="East",
        division="Central",
    ),
    TeamID.CAVALIERS: TeamInfo(
        id=TeamID.CAVALIERS,
        abbreviation="CLE",
        city="Cleveland",
        name="Cavaliers",
        full_name="Cleveland Cavaliers",
        conference="East",
        division="Central",
    ),
    TeamID.PISTONS: TeamInfo(
        id=TeamID.PISTONS,
        abbreviation="DET",
        city="Detroit",
        name="Pistons",
        full_name="Detroit Pistons",
        conference="East",
        division="Central",
    ),
    TeamID.PACERS: TeamInfo(
        id=TeamID.PACERS,
        abbreviation="IND",
        city="Indiana",
        name="Pacers",
        full_name="Indiana Pacers",
        conference="East",
        division="Central",
    ),
    TeamID.BUCKS: TeamInfo(
        id=TeamID.BUCKS,
        abbreviation="MIL",
        city="Milwaukee",
        name="Bucks",
        full_name="Milwaukee Bucks",
        conference="East",
        division="Central",
    ),
    # Eastern Conference - Southeast Division
    TeamID.HAWKS: TeamInfo(
        id=TeamID.HAWKS,
        abbreviation="ATL",
        city="Atlanta",
        name="Hawks",
        full_name="Atlanta Hawks",
        conference="East",
        division="Southeast",
    ),
    TeamID.HORNETS: TeamInfo(
        id=TeamID.HORNETS,
        abbreviation="CHA",
        city="Charlotte",
        name="Hornets",
        full_name="Charlotte Hornets",
        conference="East",
        division="Southeast",
    ),
    TeamID.HEAT: TeamInfo(
        id=TeamID.HEAT,
        abbreviation="MIA",
        city="Miami",
        name="Heat",
        full_name="Miami Heat",
        conference="East",
        division="Southeast",
    ),
    TeamID.MAGIC: TeamInfo(
        id=TeamID.MAGIC,
        abbreviation="ORL",
        city="Orlando",
        name="Magic",
        full_name="Orlando Magic",
        conference="East",
        division="Southeast",
    ),
    TeamID.WIZARDS: TeamInfo(
        id=TeamID.WIZARDS,
        abbreviation="WAS",
        city="Washington",
        name="Wizards",
        full_name="Washington Wizards",
        conference="East",
        division="Southeast",
    ),
    # Western Conference - Northwest Division
    TeamID.NUGGETS: TeamInfo(
        id=TeamID.NUGGETS,
        abbreviation="DEN",
        city="Denver",
        name="Nuggets",
        full_name="Denver Nuggets",
        conference="West",
        division="Northwest",
    ),
    TeamID.TIMBERWOLVES: TeamInfo(
        id=TeamID.TIMBERWOLVES,
        abbreviation="MIN",
        city="Minnesota",
        name="Timberwolves",
        full_name="Minnesota Timberwolves",
        conference="West",
        division="Northwest",
    ),
    TeamID.THUNDER: TeamInfo(
        id=TeamID.THUNDER,
        abbreviation="OKC",
        city="Oklahoma City",
        name="Thunder",
        full_name="Oklahoma City Thunder",
        conference="West",
        division="Northwest",
    ),
    TeamID.TRAIL_BLAZERS: TeamInfo(
        id=TeamID.TRAIL_BLAZERS,
        abbreviation="POR",
        city="Portland",
        name="Trail Blazers",
        full_name="Portland Trail Blazers",
        conference="West",
        division="Northwest",
    ),
    TeamID.JAZZ: TeamInfo(
        id=TeamID.JAZZ,
        abbreviation="UTA",
        city="Utah",
        name="Jazz",
        full_name="Utah Jazz",
        conference="West",
        division="Northwest",
    ),
    # Western Conference - Pacific Division
    TeamID.WARRIORS: TeamInfo(
        id=TeamID.WARRIORS,
        abbreviation="GSW",
        city="Golden State",
        name="Warriors",
        full_name="Golden State Warriors",
        conference="West",
        division="Pacific",
    ),
    TeamID.CLIPPERS: TeamInfo(
        id=TeamID.CLIPPERS,
        abbreviation="LAC",
        city="Los Angeles",
        name="Clippers",
        full_name="Los Angeles Clippers",
        conference="West",
        division="Pacific",
    ),
    TeamID.LAKERS: TeamInfo(
        id=TeamID.LAKERS,
        abbreviation="LAL",
        city="Los Angeles",
        name="Lakers",
        full_name="Los Angeles Lakers",
        conference="West",
        division="Pacific",
    ),
    TeamID.SUNS: TeamInfo(
        id=TeamID.SUNS,
        abbreviation="PHX",
        city="Phoenix",
        name="Suns",
        full_name="Phoenix Suns",
        conference="West",
        division="Pacific",
    ),
    TeamID.KINGS: TeamInfo(
        id=TeamID.KINGS,
        abbreviation="SAC",
        city="Sacramento",
        name="Kings",
        full_name="Sacramento Kings",
        conference="West",
        division="Pacific",
    ),
    # Western Conference - Southwest Division
    TeamID.MAVERICKS: TeamInfo(
        id=TeamID.MAVERICKS,
        abbreviation="DAL",
        city="Dallas",
        name="Mavericks",
        full_name="Dallas Mavericks",
        conference="West",
        division="Southwest",
    ),
    TeamID.ROCKETS: TeamInfo(
        id=TeamID.ROCKETS,
        abbreviation="HOU",
        city="Houston",
        name="Rockets",
        full_name="Houston Rockets",
        conference="West",
        division="Southwest",
    ),
    TeamID.GRIZZLIES: TeamInfo(
        id=TeamID.GRIZZLIES,
        abbreviation="MEM",
        city="Memphis",
        name="Grizzlies",
        full_name="Memphis Grizzlies",
        conference="West",
        division="Southwest",
    ),
    TeamID.PELICANS: TeamInfo(
        id=TeamID.PELICANS,
        abbreviation="NOP",
        city="New Orleans",
        name="Pelicans",
        full_name="New Orleans Pelicans",
        conference="West",
        division="Southwest",
    ),
    TeamID.SPURS: TeamInfo(
        id=TeamID.SPURS,
        abbreviation="SAS",
        city="San Antonio",
        name="Spurs",
        full_name="San Antonio Spurs",
        conference="West",
        division="Southwest",
    ),
}

_TEAMS_BY_ABBREVIATION: dict[str, TeamInfo] = {
    t.abbreviation: t for t in TEAMS.values()
}
_TEAMS_BY_NAME: dict[str, TeamInfo] = {t.name.lower(): t for t in TEAMS.values()}
_TEAMS_BY_CITY: dict[str, TeamInfo] = {t.city.lower(): t for t in TEAMS.values()}
_VALID_CONFERENCES: frozenset[str] = frozenset({t.conference for t in TEAMS.values()})
_VALID_DIVISIONS: frozenset[str] = frozenset({t.division for t in TEAMS.values()})


def get_team(identifier: int | str) -> TeamInfo | None:
    """Look up team information by ID, abbreviation, name, or city.

    Args:
        identifier: Team ID (int), abbreviation (e.g., "LAL"),
                   name (e.g., "Lakers"), or city (e.g., "Los Angeles")

    Returns:
        TeamInfo if found, None otherwise

    Examples:
        >>> get_team(1610612747)
        TeamInfo(id=1610612747, abbreviation='LAL', ...)
        >>> get_team("LAL")
        TeamInfo(id=1610612747, abbreviation='LAL', ...)
        >>> get_team("Lakers")
        TeamInfo(id=1610612747, abbreviation='LAL', ...)

    """
    if isinstance(identifier, int):
        return TEAMS.get(identifier)

    # Try abbreviation first (case-insensitive)
    upper = identifier.upper()
    if upper in _TEAMS_BY_ABBREVIATION:
        return _TEAMS_BY_ABBREVIATION[upper]

    # Try name or city (case-insensitive)
    lower = identifier.lower()
    if lower in _TEAMS_BY_NAME:
        return _TEAMS_BY_NAME[lower]
    if lower in _TEAMS_BY_CITY:
        return _TEAMS_BY_CITY[lower]

    return None


def get_team_id(identifier: str) -> int | None:
    """Get a team's ID by abbreviation, name, or city.

    Args:
        identifier: Team abbreviation, name, or city

    Returns:
        Team ID if found, None otherwise

    Examples:
        >>> get_team_id("LAL")
        1610612747
        >>> get_team_id("Lakers")
        1610612747

    """
    team = get_team(identifier)
    return team.id if team else None


def teams_by_conference(conference: str) -> list[TeamInfo]:
    """Get all teams in a conference.

    Args:
        conference: Conference name, case-insensitive ("East" or "West")

    Returns:
        List of TeamInfo for teams in the conference

    Raises:
        ValueError: If the conference is not "East" or "West".

    """
    conf = conference.capitalize()
    if conf not in _VALID_CONFERENCES:
        msg = f"Unknown conference: {conference!r}. Expected one of: {sorted(_VALID_CONFERENCES)}"
        raise ValueError(msg)
    return [t for t in TEAMS.values() if t.conference == conf]


def teams_by_division(division: str) -> list[TeamInfo]:
    """Get all teams in a division.

    Args:
        division: Division name, case-insensitive (e.g., "Atlantic", "pacific")

    Returns:
        List of TeamInfo for teams in the division

    Raises:
        ValueError: If the division name is not recognized.

    """
    div = division.capitalize()
    if div not in _VALID_DIVISIONS:
        msg = f"Unknown division: {division!r}. Expected one of: {sorted(_VALID_DIVISIONS)}"
        raise ValueError(msg)
    return [t for t in TEAMS.values() if t.division == div]


def search_teams(query: str, *, limit: int = 5) -> list[TeamInfo]:
    """Search for teams by partial abbreviation, name, or city.

    Args:
        query: Search string (abbreviation, city, or team name)
        limit: Maximum results to return

    Returns:
        List of matching TeamInfo objects, sorted by relevance

    Raises:
        ValueError: If limit is less than 1.

    Examples:
        search_teams("IND")      # Indiana Pacers
        search_teams("Lakers")   # Los Angeles Lakers
        search_teams("New")      # New Orleans Pelicans, New York Knicks

    """
    if limit < 1:
        msg = f"limit must be a positive integer, got {limit}"
        raise ValueError(msg)
    if not query or not query.strip():
        return []

    q = query.strip().lower()
    q_upper = q.upper()
    matches: list[tuple[int, TeamInfo]] = []

    for team in TEAMS.values():
        abbr = team.abbreviation.upper()
        city = team.city.lower()
        name = team.name.lower()
        full = team.full_name.lower()

        if abbr == q_upper:
            priority = 0
        elif q in (city, name, full):
            priority = 1
        elif city.startswith(q) or name.startswith(q) or abbr.startswith(q_upper):
            priority = 2
        elif q in city or q in name or q in full:
            priority = 3
        else:
            continue

        matches.append((priority, team))

    matches.sort(key=lambda x: (x[0], x[1].abbreviation))
    return [team for _, team in matches[:limit]]


async def get_team_game_log(
    client: NBAClient,
    *,
    team_id: int,
    season: str | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[TeamGameLogEntry]:
    """Return a team's game-by-game stats for a season.

    Args:
        client: NBA API client
        team_id: NBA team ID
        season: Season in YYYY-YY format (defaults to current)
        season_type: "Regular Season", "Playoffs", etc.

    Returns:
        List of TeamGameLogEntry objects, one per game played

    Examples:
        log = await get_team_game_log(client, team_id=1610612754)

    """
    from fastbreak.endpoints import TeamGameLog  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        TeamGameLog(team_id=team_id, season=season, season_type=season_type)
    )
    return response.games


async def get_team_stats(
    client: NBAClient,
    *,
    season: str | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[LeagueDashTeamStatsRow]:
    """Return per-game stats for all teams in the league.

    Args:
        client: NBA API client
        season: Season in YYYY-YY format (defaults to current)
        season_type: "Regular Season", "Playoffs", etc.
        per_mode: Stat aggregation mode ("PerGame", "Totals", "Per36", etc.)

    Returns:
        List of LeagueDashTeamStatsRow objects, one per team

    Examples:
        teams = await get_team_stats(client)
        top_offense = sorted(teams, key=lambda t: t.pts, reverse=True)[:5]

    """
    from fastbreak.endpoints import LeagueDashTeamStats  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueDashTeamStats(season=season, season_type=season_type, per_mode=per_mode)
    )
    return response.teams


async def get_lineup_stats(
    client: NBAClient,
    team_id: int,
    *,
    season: str | None = None,
    season_type: SeasonType = "Regular Season",
    group_quantity: int = 5,
) -> list[LineupStats]:
    """Return lineup combination stats for a team.

    Args:
        client: NBA API client
        team_id: NBA team ID
        season: Season in YYYY-YY format (defaults to current)
        season_type: "Regular Season", "Playoffs", etc.
        group_quantity: Number of players in each lineup (2-5, default 5)

    Returns:
        List of LineupStats objects sorted by minutes played (API default)

    Examples:
        lineups = await get_lineup_stats(client, team_id=1610612754)
        best = sorted(lineups, key=lambda l: l.plus_minus, reverse=True)[:5]

    """
    from fastbreak.endpoints import TeamDashLineups  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        TeamDashLineups(
            team_id=team_id,
            season=season,
            season_type=season_type,
            group_quantity=group_quantity,
        )
    )
    return response.lineups
