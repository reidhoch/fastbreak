"""Utility functions and static data for the NBA Stats API."""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import IntEnum

# October is when the NBA season starts
_SEASON_START_MONTH = 10


def get_season_from_date(reference_date: date | None = None) -> str:
    """Return the NBA season for a given date in YYYY-YY format.

    The NBA season typically starts in October and ends in June.
    A season is identified by the year it starts (e.g., "2024-25" for the
    season that started in October 2024).

    Args:
        reference_date: Date to get season for (defaults to today)

    Returns:
        Season string in YYYY-YY format (e.g., "2024-25")

    Examples:
        >>> get_season_from_date(date(2024, 11, 15))
        '2024-25'
        >>> get_season_from_date(date(2025, 3, 15))
        '2024-25'
        >>> get_season_from_date(date(2025, 10, 15))
        '2025-26'
        >>> get_season_from_date()  # returns current season
        '2025-26'

    """
    ref = reference_date or datetime.now(tz=UTC).date()

    # NBA season starts in October
    # If we're in Oct-Dec, we're in the season that started this year
    # If we're in Jan-Sep, we're in the season that started last year
    start_year = ref.year if ref.month >= _SEASON_START_MONTH else ref.year - 1

    end_year_short = (start_year + 1) % 100
    return f"{start_year}-{end_year_short:02d}"


def season_start_year(season: str) -> int:
    """Extract the start year from a season string.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")

    Returns:
        The start year as an integer (e.g., 2024)

    """
    return int(season.split("-", maxsplit=1)[0])


def season_to_season_id(season: str) -> str:
    """Convert a season string to NBA season ID format.

    Some endpoints use a season ID format like "22024" where the prefix
    indicates the season type (2 = regular season).

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")

    Returns:
        Season ID string (e.g., "22024")

    """
    start_year = season_start_year(season)
    return f"2{start_year}"


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


# Complete team information lookup
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

# Lookup indexes for quick access
_TEAMS_BY_ABBREVIATION: dict[str, TeamInfo] = {
    t.abbreviation: t for t in TEAMS.values()
}
_TEAMS_BY_NAME: dict[str, TeamInfo] = {t.name.lower(): t for t in TEAMS.values()}
_TEAMS_BY_CITY: dict[str, TeamInfo] = {t.city.lower(): t for t in TEAMS.values()}


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
        conference: "East" or "West"

    Returns:
        List of TeamInfo for teams in the conference

    """
    conf = conference.capitalize()
    return [t for t in TEAMS.values() if t.conference == conf]


def teams_by_division(division: str) -> list[TeamInfo]:
    """Get all teams in a division.

    Args:
        division: Division name (e.g., "Atlantic", "Pacific")

    Returns:
        List of TeamInfo for teams in the division

    """
    div = division.capitalize()
    return [t for t in TEAMS.values() if t.division == div]
