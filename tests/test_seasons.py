"""Tests for season utility functions."""

from datetime import date

import pytest

from fastbreak.seasons import (
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


class TestSeasonHelpers:
    """Tests for season helper functions."""

    def test_season_start_year(self) -> None:
        """Extracts start year from season string."""
        assert season_start_year("2024-25") == 2024
        assert season_start_year("1999-00") == 1999

    def test_season_to_season_id(self) -> None:
        """Converts season to NBA season ID format."""
        assert season_to_season_id("2024-25") == "22024"
        assert season_to_season_id("1999-00") == "21999"
