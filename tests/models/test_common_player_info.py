import pytest

from fastbreak.models import (
    AvailableSeason,
    CommonPlayerInfoResponse,
    PlayerHeadlineStats,
    PlayerInfo,
)


class TestPlayerInfo:
    """Tests for PlayerInfo model."""

    def test_parse_valid_entry(self):
        """PlayerInfo parses valid data."""
        data = {
            "PERSON_ID": 203500,
            "FIRST_NAME": "Steven",
            "LAST_NAME": "Adams",
            "DISPLAY_FIRST_LAST": "Steven Adams",
            "DISPLAY_LAST_COMMA_FIRST": "Adams, Steven",
            "DISPLAY_FI_LAST": "S. Adams",
            "PLAYER_SLUG": "steven-adams",
            "BIRTHDATE": "1993-07-20T00:00:00",
            "SCHOOL": "Pittsburgh",
            "COUNTRY": "New Zealand",
            "LAST_AFFILIATION": "Pittsburgh/New Zealand",
            "HEIGHT": "6-11",
            "WEIGHT": "265",
            "SEASON_EXP": 12,
            "JERSEY": "12",
            "POSITION": "Center",
            "ROSTERSTATUS": "Active",
            "GAMES_PLAYED_CURRENT_SEASON_FLAG": "Y",
            "TEAM_ID": 1610612745,
            "TEAM_NAME": "Rockets",
            "TEAM_ABBREVIATION": "HOU",
            "TEAM_CODE": "rockets",
            "TEAM_CITY": "Houston",
            "PLAYERCODE": "steven_adams",
            "FROM_YEAR": 2013,
            "TO_YEAR": 2025,
            "DLEAGUE_FLAG": "N",
            "NBA_FLAG": "Y",
            "GAMES_PLAYED_FLAG": "Y",
            "DRAFT_YEAR": "2013",
            "DRAFT_ROUND": "1",
            "DRAFT_NUMBER": "12",
            "GREATEST_75_FLAG": "N",
        }

        player = PlayerInfo.model_validate(data)

        assert player.person_id == 203500
        assert player.first_name == "Steven"
        assert player.last_name == "Adams"
        assert player.display_first_last == "Steven Adams"
        assert player.height == "6-11"
        assert player.weight == "265"
        assert player.season_exp == 12
        assert player.position == "Center"
        assert player.roster_status == "Active"
        assert player.team_abbreviation == "HOU"
        assert player.from_year == 2013
        assert player.to_year == 2025
        assert player.draft_year == "2013"
        assert player.draft_round == "1"
        assert player.draft_number == "12"
        assert player.greatest_75_flag == "N"

    def test_parse_greatest_75_player(self):
        """PlayerInfo handles Greatest 75 players."""
        data = {
            "PERSON_ID": 2544,
            "FIRST_NAME": "LeBron",
            "LAST_NAME": "James",
            "DISPLAY_FIRST_LAST": "LeBron James",
            "DISPLAY_LAST_COMMA_FIRST": "James, LeBron",
            "DISPLAY_FI_LAST": "L. James",
            "PLAYER_SLUG": "lebron-james",
            "BIRTHDATE": "1984-12-30T00:00:00",
            "SCHOOL": "St. Vincent-St. Mary HS (OH)",
            "COUNTRY": "USA",
            "LAST_AFFILIATION": "St. Vincent-St. Mary HS (OH)/USA",
            "HEIGHT": "6-9",
            "WEIGHT": "250",
            "SEASON_EXP": 22,
            "JERSEY": "23",
            "POSITION": "Forward",
            "ROSTERSTATUS": "Active",
            "GAMES_PLAYED_CURRENT_SEASON_FLAG": "Y",
            "TEAM_ID": 1610612747,
            "TEAM_NAME": "Lakers",
            "TEAM_ABBREVIATION": "LAL",
            "TEAM_CODE": "lakers",
            "TEAM_CITY": "Los Angeles",
            "PLAYERCODE": "lebron_james",
            "FROM_YEAR": 2003,
            "TO_YEAR": 2025,
            "DLEAGUE_FLAG": "N",
            "NBA_FLAG": "Y",
            "GAMES_PLAYED_FLAG": "Y",
            "DRAFT_YEAR": "2003",
            "DRAFT_ROUND": "1",
            "DRAFT_NUMBER": "1",
            "GREATEST_75_FLAG": "Y",
        }

        player = PlayerInfo.model_validate(data)

        assert player.greatest_75_flag == "Y"
        assert player.draft_number == "1"
        assert player.season_exp == 22

    def test_parse_undrafted_player(self):
        """PlayerInfo handles undrafted players."""
        data = {
            "PERSON_ID": 1627832,
            "FIRST_NAME": "Fred",
            "LAST_NAME": "VanVleet",
            "DISPLAY_FIRST_LAST": "Fred VanVleet",
            "DISPLAY_LAST_COMMA_FIRST": "VanVleet, Fred",
            "DISPLAY_FI_LAST": "F. VanVleet",
            "PLAYER_SLUG": "fred-vanvleet",
            "BIRTHDATE": "1994-02-25T00:00:00",
            "SCHOOL": "Wichita State",
            "COUNTRY": "USA",
            "LAST_AFFILIATION": "Wichita State/USA",
            "HEIGHT": "6-1",
            "WEIGHT": "197",
            "SEASON_EXP": 9,
            "JERSEY": "5",
            "POSITION": "Guard",
            "ROSTERSTATUS": "Active",
            "GAMES_PLAYED_CURRENT_SEASON_FLAG": "Y",
            "TEAM_ID": 1610612745,
            "TEAM_NAME": "Rockets",
            "TEAM_ABBREVIATION": "HOU",
            "TEAM_CODE": "rockets",
            "TEAM_CITY": "Houston",
            "PLAYERCODE": "fred_vanvleet",
            "FROM_YEAR": 2016,
            "TO_YEAR": 2025,
            "DLEAGUE_FLAG": "Y",
            "NBA_FLAG": "Y",
            "GAMES_PLAYED_FLAG": "Y",
            "DRAFT_YEAR": "Undrafted",
            "DRAFT_ROUND": "",
            "DRAFT_NUMBER": "",
            "GREATEST_75_FLAG": "N",
        }

        player = PlayerInfo.model_validate(data)

        assert player.draft_year == "Undrafted"
        assert player.draft_round == ""
        assert player.draft_number == ""
        assert player.dleague_flag == "Y"


class TestPlayerHeadlineStats:
    """Tests for PlayerHeadlineStats model."""

    def test_parse_valid_entry(self):
        """PlayerHeadlineStats parses valid data."""
        data = {
            "PLAYER_ID": 203500,
            "PLAYER_NAME": "Steven Adams",
            "TimeFrame": "2025-26",
            "PTS": 5.8,
            "AST": 1.5,
            "REB": 8.6,
            "PIE": 0.092,
        }

        stats = PlayerHeadlineStats.model_validate(data)

        assert stats.player_id == 203500
        assert stats.player_name == "Steven Adams"
        assert stats.time_frame == "2025-26"
        assert stats.pts == pytest.approx(5.8)
        assert stats.ast == pytest.approx(1.5)
        assert stats.reb == pytest.approx(8.6)
        assert stats.pie == pytest.approx(0.092)

    def test_parse_zero_pie(self):
        """PlayerHeadlineStats handles zero PIE value."""
        data = {
            "PLAYER_ID": 203500,
            "PLAYER_NAME": "Steven Adams",
            "TimeFrame": "2025-26",
            "PTS": 5.8,
            "AST": 1.5,
            "REB": 8.6,
            "PIE": 0,
        }

        stats = PlayerHeadlineStats.model_validate(data)

        assert stats.pie == 0


class TestAvailableSeason:
    """Tests for AvailableSeason model."""

    def test_parse_regular_season(self):
        """AvailableSeason parses regular season ID."""
        data = {"SEASON_ID": "22024"}

        season = AvailableSeason.model_validate(data)

        assert season.season_id == "22024"

    def test_parse_playoff_season(self):
        """AvailableSeason parses playoff season ID."""
        data = {"SEASON_ID": "42024"}

        season = AvailableSeason.model_validate(data)

        assert season.season_id == "42024"

    def test_parse_preseason(self):
        """AvailableSeason parses preseason ID."""
        data = {"SEASON_ID": "12024"}

        season = AvailableSeason.model_validate(data)

        assert season.season_id == "12024"


class TestCommonPlayerInfoResponse:
    """Tests for CommonPlayerInfoResponse model."""

    def test_parse_full_response(self):
        """CommonPlayerInfoResponse parses all three result sets."""
        data = {
            "resource": "commonplayerinfo",
            "parameters": [{"PlayerID": 203500}, {"LeagueID": "00"}],
            "resultSets": [
                {
                    "name": "CommonPlayerInfo",
                    "headers": [
                        "PERSON_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "DISPLAY_FIRST_LAST",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FI_LAST",
                        "PLAYER_SLUG",
                        "BIRTHDATE",
                        "SCHOOL",
                        "COUNTRY",
                        "LAST_AFFILIATION",
                        "HEIGHT",
                        "WEIGHT",
                        "SEASON_EXP",
                        "JERSEY",
                        "POSITION",
                        "ROSTERSTATUS",
                        "GAMES_PLAYED_CURRENT_SEASON_FLAG",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_CODE",
                        "TEAM_CITY",
                        "PLAYERCODE",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "DLEAGUE_FLAG",
                        "NBA_FLAG",
                        "GAMES_PLAYED_FLAG",
                        "DRAFT_YEAR",
                        "DRAFT_ROUND",
                        "DRAFT_NUMBER",
                        "GREATEST_75_FLAG",
                    ],
                    "rowSet": [
                        [
                            203500,
                            "Steven",
                            "Adams",
                            "Steven Adams",
                            "Adams, Steven",
                            "S. Adams",
                            "steven-adams",
                            "1993-07-20T00:00:00",
                            "Pittsburgh",
                            "New Zealand",
                            "Pittsburgh/New Zealand",
                            "6-11",
                            "265",
                            12,
                            "12",
                            "Center",
                            "Active",
                            "Y",
                            1610612745,
                            "Rockets",
                            "HOU",
                            "rockets",
                            "Houston",
                            "steven_adams",
                            2013,
                            2025,
                            "N",
                            "Y",
                            "Y",
                            "2013",
                            "1",
                            "12",
                            "N",
                        ]
                    ],
                },
                {
                    "name": "PlayerHeadlineStats",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TimeFrame",
                        "PTS",
                        "AST",
                        "REB",
                        "PIE",
                    ],
                    "rowSet": [[203500, "Steven Adams", "2025-26", 5.8, 1.5, 8.6, 0]],
                },
                {
                    "name": "AvailableSeasons",
                    "headers": ["SEASON_ID"],
                    "rowSet": [["12013"], ["22013"], ["42013"], ["12014"], ["22014"]],
                },
            ],
        }

        response = CommonPlayerInfoResponse.model_validate(data)

        # Check player info
        assert response.player_info is not None
        assert response.player_info.display_first_last == "Steven Adams"
        assert response.player_info.team_abbreviation == "HOU"
        assert response.player_info.position == "Center"

        # Check headline stats
        assert response.headline_stats is not None
        assert response.headline_stats.pts == pytest.approx(5.8)
        assert response.headline_stats.reb == pytest.approx(8.6)

        # Check available seasons
        assert len(response.available_seasons) == 5
        assert response.available_seasons[0].season_id == "12013"

    def test_handles_empty_available_seasons(self):
        """CommonPlayerInfoResponse handles empty AvailableSeasons."""
        data = {
            "resultSets": [
                {
                    "name": "CommonPlayerInfo",
                    "headers": [
                        "PERSON_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "DISPLAY_FIRST_LAST",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FI_LAST",
                        "PLAYER_SLUG",
                        "BIRTHDATE",
                        "SCHOOL",
                        "COUNTRY",
                        "LAST_AFFILIATION",
                        "HEIGHT",
                        "WEIGHT",
                        "SEASON_EXP",
                        "JERSEY",
                        "POSITION",
                        "ROSTERSTATUS",
                        "GAMES_PLAYED_CURRENT_SEASON_FLAG",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_CODE",
                        "TEAM_CITY",
                        "PLAYERCODE",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "DLEAGUE_FLAG",
                        "NBA_FLAG",
                        "GAMES_PLAYED_FLAG",
                        "DRAFT_YEAR",
                        "DRAFT_ROUND",
                        "DRAFT_NUMBER",
                        "GREATEST_75_FLAG",
                    ],
                    "rowSet": [
                        [
                            1,
                            "Test",
                            "Player",
                            "Test Player",
                            "Player, Test",
                            "T. Player",
                            "test-player",
                            "2000-01-01T00:00:00",
                            "School",
                            "USA",
                            "School/USA",
                            "6-0",
                            "180",
                            0,
                            "1",
                            "Guard",
                            "Active",
                            "N",
                            0,
                            "",
                            "",
                            "",
                            "",
                            "test_player",
                            2025,
                            2025,
                            "N",
                            "Y",
                            "N",
                            "2025",
                            "1",
                            "1",
                            "N",
                        ]
                    ],
                },
                {
                    "name": "PlayerHeadlineStats",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TimeFrame",
                        "PTS",
                        "AST",
                        "REB",
                        "PIE",
                    ],
                    "rowSet": [],
                },
                {
                    "name": "AvailableSeasons",
                    "headers": ["SEASON_ID"],
                    "rowSet": [],
                },
            ],
        }

        response = CommonPlayerInfoResponse.model_validate(data)

        assert response.player_info is not None
        assert response.headline_stats is None
        assert len(response.available_seasons) == 0

    def test_handles_empty_player_info(self):
        """CommonPlayerInfoResponse handles empty CommonPlayerInfo."""
        data = {
            "resultSets": [
                {
                    "name": "CommonPlayerInfo",
                    "headers": ["PERSON_ID", "FIRST_NAME"],
                    "rowSet": [],
                },
                {
                    "name": "PlayerHeadlineStats",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TimeFrame",
                        "PTS",
                        "AST",
                        "REB",
                        "PIE",
                    ],
                    "rowSet": [],
                },
                {
                    "name": "AvailableSeasons",
                    "headers": ["SEASON_ID"],
                    "rowSet": [],
                },
            ],
        }

        response = CommonPlayerInfoResponse.model_validate(data)

        assert response.player_info is None
        assert response.headline_stats is None
        assert len(response.available_seasons) == 0

    def test_preserves_season_order(self):
        """CommonPlayerInfoResponse maintains season order from API."""
        data = {
            "resultSets": [
                {
                    "name": "CommonPlayerInfo",
                    "headers": [
                        "PERSON_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "DISPLAY_FIRST_LAST",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FI_LAST",
                        "PLAYER_SLUG",
                        "BIRTHDATE",
                        "SCHOOL",
                        "COUNTRY",
                        "LAST_AFFILIATION",
                        "HEIGHT",
                        "WEIGHT",
                        "SEASON_EXP",
                        "JERSEY",
                        "POSITION",
                        "ROSTERSTATUS",
                        "GAMES_PLAYED_CURRENT_SEASON_FLAG",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_CODE",
                        "TEAM_CITY",
                        "PLAYERCODE",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "DLEAGUE_FLAG",
                        "NBA_FLAG",
                        "GAMES_PLAYED_FLAG",
                        "DRAFT_YEAR",
                        "DRAFT_ROUND",
                        "DRAFT_NUMBER",
                        "GREATEST_75_FLAG",
                    ],
                    "rowSet": [
                        [
                            1,
                            "A",
                            "B",
                            "A B",
                            "B, A",
                            "A. B",
                            "a-b",
                            "2000-01-01T00:00:00",
                            "S",
                            "C",
                            "S/C",
                            "6-0",
                            "180",
                            1,
                            "1",
                            "G",
                            "Active",
                            "Y",
                            1,
                            "T",
                            "AB",
                            "t",
                            "City",
                            "a_b",
                            2020,
                            2025,
                            "N",
                            "Y",
                            "Y",
                            "2020",
                            "1",
                            "1",
                            "N",
                        ]
                    ],
                },
                {
                    "name": "PlayerHeadlineStats",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TimeFrame",
                        "PTS",
                        "AST",
                        "REB",
                        "PIE",
                    ],
                    "rowSet": [[1, "A B", "2025-26", 10.0, 5.0, 5.0, 0.1]],
                },
                {
                    "name": "AvailableSeasons",
                    "headers": ["SEASON_ID"],
                    "rowSet": [["42024"], ["22024"], ["12024"], ["42023"]],
                },
            ],
        }

        response = CommonPlayerInfoResponse.model_validate(data)

        assert response.available_seasons[0].season_id == "42024"
        assert response.available_seasons[1].season_id == "22024"
        assert response.available_seasons[2].season_id == "12024"
        assert response.available_seasons[3].season_id == "42023"
