"""Tests for utility functions and static data."""

from datetime import date

import pytest

from fastbreak.utils import (
    TEAMS,
    TeamID,
    get_season_from_date,
    get_team,
    get_team_id,
    season_start_year,
    season_to_season_id,
    teams_by_conference,
    teams_by_division,
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


class TestTeamID:
    """Tests for TeamID enum."""

    def test_all_30_teams_exist(self) -> None:
        """All 30 NBA teams are defined."""
        assert len(TeamID) == 30

    def test_lakers_id(self) -> None:
        """Lakers have correct ID."""
        assert TeamID.LAKERS == 1610612747

    def test_celtics_id(self) -> None:
        """Celtics have correct ID."""
        assert TeamID.CELTICS == 1610612738

    def test_enum_is_int(self) -> None:
        """TeamID values can be used as integers."""
        assert int(TeamID.LAKERS) == 1610612747


class TestTeamsData:
    """Tests for TEAMS dictionary."""

    def test_all_30_teams_have_info(self) -> None:
        """All 30 teams have TeamInfo entries."""
        assert len(TEAMS) == 30

    def test_team_info_fields(self) -> None:
        """TeamInfo has all expected fields."""
        lakers = TEAMS[TeamID.LAKERS]
        assert lakers.id == TeamID.LAKERS
        assert lakers.abbreviation == "LAL"
        assert lakers.city == "Los Angeles"
        assert lakers.name == "Lakers"
        assert lakers.full_name == "Los Angeles Lakers"
        assert lakers.conference == "West"
        assert lakers.division == "Pacific"


class TestGetTeam:
    """Tests for get_team function."""

    def test_get_by_id(self) -> None:
        """Can get team by numeric ID."""
        team = get_team(1610612747)
        assert team is not None
        assert team.name == "Lakers"

    def test_get_by_abbreviation(self) -> None:
        """Can get team by abbreviation."""
        team = get_team("LAL")
        assert team is not None
        assert team.name == "Lakers"

    def test_get_by_abbreviation_lowercase(self) -> None:
        """Abbreviation lookup is case-insensitive."""
        team = get_team("lal")
        assert team is not None
        assert team.name == "Lakers"

    def test_get_by_name(self) -> None:
        """Can get team by name."""
        team = get_team("Lakers")
        assert team is not None
        assert team.abbreviation == "LAL"

    def test_get_by_name_lowercase(self) -> None:
        """Name lookup is case-insensitive."""
        team = get_team("lakers")
        assert team is not None
        assert team.abbreviation == "LAL"

    def test_get_by_city(self) -> None:
        """Can get team by city."""
        team = get_team("Boston")
        assert team is not None
        assert team.name == "Celtics"

    def test_get_unknown_returns_none(self) -> None:
        """Unknown identifier returns None."""
        assert get_team("Unknown") is None
        assert get_team(99999) is None


class TestGetTeamId:
    """Tests for get_team_id function."""

    def test_get_id_by_abbreviation(self) -> None:
        """Can get team ID by abbreviation."""
        assert get_team_id("LAL") == 1610612747

    def test_get_id_by_name(self) -> None:
        """Can get team ID by name."""
        assert get_team_id("Lakers") == 1610612747

    def test_unknown_returns_none(self) -> None:
        """Unknown team returns None."""
        assert get_team_id("Unknown") is None


class TestTeamsByConference:
    """Tests for teams_by_conference function."""

    def test_east_has_15_teams(self) -> None:
        """Eastern Conference has 15 teams."""
        east = teams_by_conference("East")
        assert len(east) == 15

    def test_west_has_15_teams(self) -> None:
        """Western Conference has 15 teams."""
        west = teams_by_conference("West")
        assert len(west) == 15

    def test_case_insensitive(self) -> None:
        """Conference lookup is case-insensitive."""
        assert len(teams_by_conference("east")) == 15
        assert len(teams_by_conference("WEST")) == 15

    def test_celtics_in_east(self) -> None:
        """Celtics are in Eastern Conference."""
        east = teams_by_conference("East")
        team_names = [t.name for t in east]
        assert "Celtics" in team_names

    def test_lakers_in_west(self) -> None:
        """Lakers are in Western Conference."""
        west = teams_by_conference("West")
        team_names = [t.name for t in west]
        assert "Lakers" in team_names


class TestTeamsByDivision:
    """Tests for teams_by_division function."""

    def test_atlantic_has_5_teams(self) -> None:
        """Atlantic Division has 5 teams."""
        atlantic = teams_by_division("Atlantic")
        assert len(atlantic) == 5

    def test_pacific_has_5_teams(self) -> None:
        """Pacific Division has 5 teams."""
        pacific = teams_by_division("Pacific")
        assert len(pacific) == 5

    def test_all_divisions_have_5_teams(self) -> None:
        """Each division has exactly 5 teams."""
        divisions = [
            "Atlantic",
            "Central",
            "Southeast",
            "Northwest",
            "Pacific",
            "Southwest",
        ]
        for division in divisions:
            teams = teams_by_division(division)
            assert len(teams) == 5, f"{division} should have 5 teams"

    def test_lakers_in_pacific(self) -> None:
        """Lakers are in Pacific Division."""
        pacific = teams_by_division("Pacific")
        team_names = [t.name for t in pacific]
        assert "Lakers" in team_names
