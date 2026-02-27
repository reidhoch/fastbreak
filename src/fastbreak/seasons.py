"""Season utility functions."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.types import Season

_SEASON_START_MONTH = 10
_SEASON_YEAR_LEN = 4


def get_season_from_date(reference_date: date | None = None) -> Season:
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
        >>> get_season_from_date()  # doctest: +SKIP
        '2025-26'

    """
    ref = reference_date or datetime.now(tz=UTC).date()

    # NBA seasons start in October, so Jan-Sep dates belong to the previous year's season
    start_year = ref.year if ref.month >= _SEASON_START_MONTH else ref.year - 1

    end_year_short = (start_year + 1) % 100
    return f"{start_year}-{end_year_short:02d}"


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
