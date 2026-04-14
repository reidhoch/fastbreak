"""Season utility functions."""

from __future__ import annotations

from datetime import UTC, date, datetime
from functools import lru_cache
from typing import TYPE_CHECKING

from fastbreak.league import League

if TYPE_CHECKING:
    from fastbreak.types import Season

_SEASON_YEAR_LEN = 4


@lru_cache(maxsize=64)
def _season_from_date(d: date, start_month: int) -> Season:
    start_year = d.year if d.month >= start_month else d.year - 1
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def get_season_from_date(
    reference_date: date | None = None, *, league: League = League.NBA
) -> Season:
    """Return the season for a given date in YYYY-YY format.

    The season boundary is determined by the league's start month:
    NBA starts in October, WNBA starts in May. A season is identified
    by the year it starts (e.g., ``"2024-25"`` for the season that
    started in October 2024 for NBA, or May 2025 for WNBA ``"2025-26"``).

    Args:
        reference_date: Date to get season for (defaults to today).
        league: League configuration for season start month (default: NBA).

    Returns:
        Season string in YYYY-YY format (e.g., "2024-25")

    Examples:
        >>> get_season_from_date(date(2024, 11, 15))
        '2024-25'
        >>> get_season_from_date(date(2025, 3, 15))
        '2024-25'
        >>> get_season_from_date(date(2025, 10, 15))
        '2025-26'
        >>> get_season_from_date(date(2025, 7, 15), league=League.WNBA)
        '2025-26'

    """
    d = reference_date or datetime.now(tz=UTC).date()
    return _season_from_date(d, league.season_start_month)


def get_current_season_year(*, league: League = League.NBA) -> str:
    """Return the current season start year as a YYYY string.

    Used for endpoints that accept season in YYYY format rather than YYYY-YY
    (e.g., CumeStats endpoints). Returns ``"2025"`` when the current season is
    ``"2025-26"``.

    Args:
        league: League configuration (default: NBA).

    Returns:
        Season start year as a 4-digit string (e.g., ``"2025"``).

    """
    return str(season_start_year(get_season_from_date(league=league)))


def season_start_year(season: Season) -> int:
    """Extract the start year from a season string.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25"). The ``Season``
            type alias guarantees the format is valid when the argument flows
            through Pydantic validation.

    Returns:
        The start year as an integer (e.g., 2024)

    Raises:
        ValueError: If the first four characters are not a numeric year (e.g.,
            ``"202X-25"``). Well-typed callers will never hit this path.

    """
    year_str = season[:_SEASON_YEAR_LEN]
    if len(year_str) < _SEASON_YEAR_LEN:
        msg = f"Invalid season format: {season!r}. Expected YYYY-YY (e.g., '2024-25')."
        raise ValueError(msg)
    try:
        return int(year_str)
    except ValueError as exc:
        msg = f"Invalid season format: {season!r}. Expected YYYY-YY (e.g., '2024-25')."
        raise ValueError(msg) from exc


def season_to_season_id(season: Season) -> str:
    """Convert a season string to NBA season ID format.

    Some endpoints use a season ID format like "22024" where the prefix
    indicates the season type (2 = regular season). This function always
    produces a regular-season ID (prefix "2"). Playoff or preseason IDs
    require a different prefix and are not supported here.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")

    Returns:
        Season ID string (e.g., "22024")

    """
    start_year = season_start_year(season)
    return f"2{start_year}"


@lru_cache(maxsize=32)
def season_id_to_season(season_id: str) -> str:
    """Convert an NBA season_id string to YYYY-YY format.

    Inverse of ``season_to_season_id``. Handles two API formats:

    - ``"22024"`` (type digit + 4-digit year) → ``"2024-25"``
    - ``"2024-25"`` (already YYYY-YY) → ``"2024-25"``

    Args:
        season_id: NBA season ID string (e.g., "22024") or YYYY-YY season
            string (e.g., "2024-25").

    Returns:
        Season string in YYYY-YY format (e.g., "2024-25").

    Raises:
        ValueError: If the season_id cannot be parsed.

    """
    if "-" in season_id:
        return season_id
    if len(season_id) < 5:  # noqa: PLR2004
        msg = f"Cannot parse season_id {season_id!r}: expected 'T+YYYY' format (e.g., '22024')"
        raise ValueError(msg)
    raw = season_id[1:]
    try:
        year = int(raw)
    except ValueError as exc:
        msg = (
            f"Cannot parse season_id {season_id!r}: year portion {raw!r} is not numeric"
        )
        raise ValueError(msg) from exc
    return f"{year}-{str(year + 1)[2:]}"
