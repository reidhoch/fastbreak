"""Tests for season utility functions."""

from datetime import date

import pytest

from fastbreak.league import League
from fastbreak.seasons import (
    get_current_season_year,
    get_season_from_date,
    season_start_year,
    season_to_season_id,
)


class TestGetSeasonFromDate:
    """Tests for get_season_from_date function."""

    def test_october_returns_new_season(self) -> None:
        """October starts a new season."""
        assert get_season_from_date(date(2024, 10, 15)) == "2024-25"

    def test_november_same_season(self) -> None:
        """November is part of the season that started in October."""
        assert get_season_from_date(date(2024, 11, 15)) == "2024-25"

    def test_december_same_season(self) -> None:
        """December is part of the season that started in October."""
        assert get_season_from_date(date(2024, 12, 25)) == "2024-25"

    def test_january_previous_year_season(self) -> None:
        """January is part of the season that started previous October."""
        assert get_season_from_date(date(2025, 1, 15)) == "2024-25"

    def test_june_previous_year_season(self) -> None:
        """June (playoffs) is part of the season that started previous October."""
        assert get_season_from_date(date(2025, 6, 15)) == "2024-25"

    def test_september_previous_year_season(self) -> None:
        """September (pre-season) is still considered previous season."""
        assert get_season_from_date(date(2025, 9, 15)) == "2024-25"

    def test_year_2000_format(self) -> None:
        """Season crossing 2000 formats correctly."""
        assert get_season_from_date(date(1999, 11, 1)) == "1999-00"

    def test_defaults_to_today(self) -> None:
        """Without argument, uses today's date."""
        result = get_season_from_date()
        # Just verify it returns a valid format
        assert len(result) == 7
        assert result[4] == "-"

    def test_wnba_may_starts_new_season(self) -> None:
        """WNBA season starts in May — May is the new season."""
        assert get_season_from_date(date(2025, 5, 15), league=League.WNBA) == "2025-26"

    def test_wnba_april_is_previous_season(self) -> None:
        """April is before WNBA season start, so it belongs to the previous season."""
        assert get_season_from_date(date(2025, 4, 30), league=League.WNBA) == "2024-25"

    def test_wnba_summer_in_season(self) -> None:
        """July is mid-WNBA-season, same season that started in May."""
        assert get_season_from_date(date(2025, 7, 15), league=League.WNBA) == "2025-26"

    def test_wnba_january_is_previous_season(self) -> None:
        """January is off-season for WNBA, belongs to previous season."""
        assert get_season_from_date(date(2026, 1, 15), league=League.WNBA) == "2025-26"


class TestSeasonHelpers:
    """Tests for season helper functions."""

    def test_season_start_year(self) -> None:
        """Extracts start year from season string."""
        assert season_start_year("2024-25") == 2024
        assert season_start_year("1999-00") == 1999

    def test_season_start_year_raises_for_non_season_string(self) -> None:
        """season_start_year raises ValueError for a non-season string."""
        with pytest.raises(ValueError, match="Invalid season format"):
            season_start_year("invalid")

    def test_season_start_year_raises_for_empty_string(self) -> None:
        """season_start_year raises ValueError for an empty string."""
        with pytest.raises(ValueError, match="Invalid season format"):
            season_start_year("")

    def test_season_to_season_id(self) -> None:
        """Converts season to NBA season ID format."""
        assert season_to_season_id("2024-25") == "22024"
        assert season_to_season_id("1999-00") == "21999"

    def test_season_start_year_preserves_exception_cause_for_non_numeric_year(
        self,
    ) -> None:
        """ValueError for a non-numeric year preserves the original parse error as __cause__."""
        with pytest.raises(ValueError) as exc_info:
            season_start_year("202X-25")
        assert exc_info.value.__cause__ is not None

    def test_season_start_year_raises_for_short_string(self) -> None:
        """A string shorter than four digits raises ValueError."""
        with pytest.raises(ValueError, match="Invalid season format"):
            season_start_year("202")

    def test_season_to_season_id_propagates_format_error(self) -> None:
        """season_to_season_id raises ValueError for an invalid season format."""
        with pytest.raises(ValueError, match="Invalid season format"):
            season_to_season_id("invalid")


class TestGetCurrentSeasonYear:
    """Tests for get_current_season_year()."""

    def test_returns_four_digit_string(self) -> None:
        """Returns a 4-digit year string."""
        result = get_current_season_year()
        assert len(result) == 4
        assert result.isdigit()

    def test_consistent_with_get_season_from_date(self) -> None:
        """Year matches the start year of the current season."""
        season = get_season_from_date()
        expected_year = str(season_start_year(season))
        assert get_current_season_year() == expected_year
