from fastbreak.models import CommonAllPlayersResponse, CommonPlayer


class TestCommonPlayer:
    """Tests for CommonPlayer model."""

    def test_parse_valid_entry(self):
        """CommonPlayer parses valid data."""
        data = {
            "PERSON_ID": 1630173,
            "DISPLAY_LAST_COMMA_FIRST": "Achiuwa, Precious",
            "DISPLAY_FIRST_LAST": "Precious Achiuwa",
            "ROSTERSTATUS": 1,
            "FROM_YEAR": "2020",
            "TO_YEAR": "2025",
            "PLAYERCODE": "precious_achiuwa",
            "PLAYER_SLUG": "precious_achiuwa",
            "TEAM_ID": 1610612758,
            "TEAM_CITY": "Sacramento",
            "TEAM_NAME": "Kings",
            "TEAM_ABBREVIATION": "SAC",
            "TEAM_SLUG": "kings",
            "TEAM_CODE": "kings",
            "GAMES_PLAYED_FLAG": "Y",
            "OTHERLEAGUE_EXPERIENCE_CH": "00",
        }

        player = CommonPlayer.model_validate(data)

        assert player.person_id == 1630173
        assert player.display_last_comma_first == "Achiuwa, Precious"
        assert player.display_first_last == "Precious Achiuwa"
        assert player.roster_status == 1
        assert player.from_year == "2020"
        assert player.to_year == "2025"
        assert player.player_code == "precious_achiuwa"
        assert player.player_slug == "precious_achiuwa"
        assert player.team_id == 1610612758
        assert player.team_city == "Sacramento"
        assert player.team_name == "Kings"
        assert player.team_abbreviation == "SAC"
        assert player.team_slug == "kings"
        assert player.team_code == "kings"
        assert player.games_played_flag == "Y"
        assert player.other_league_experience == "00"

    def test_parse_free_agent_with_null_team_slug(self):
        """CommonPlayer handles null team_slug for free agents."""
        data = {
            "PERSON_ID": 1628964,
            "DISPLAY_LAST_COMMA_FIRST": "Bamba, Mo",
            "DISPLAY_FIRST_LAST": "Mo Bamba",
            "ROSTERSTATUS": 0,
            "FROM_YEAR": "2018",
            "TO_YEAR": "2025",
            "PLAYERCODE": "mohamed_bamba",
            "PLAYER_SLUG": "mo_bamba",
            "TEAM_ID": 0,
            "TEAM_CITY": "",
            "TEAM_NAME": "",
            "TEAM_ABBREVIATION": "",
            "TEAM_SLUG": None,
            "TEAM_CODE": "",
            "GAMES_PLAYED_FLAG": "Y",
            "OTHERLEAGUE_EXPERIENCE_CH": "11",
        }

        player = CommonPlayer.model_validate(data)

        assert player.person_id == 1628964
        assert player.display_first_last == "Mo Bamba"
        assert player.roster_status == 0
        assert player.team_id == 0
        assert player.team_slug is None
        assert player.team_abbreviation == ""

    def test_parse_player_with_special_characters(self):
        """CommonPlayer handles names with special characters."""
        data = {
            "PERSON_ID": 203999,
            "DISPLAY_LAST_COMMA_FIRST": "Jokić, Nikola",
            "DISPLAY_FIRST_LAST": "Nikola Jokić",
            "ROSTERSTATUS": 1,
            "FROM_YEAR": "2015",
            "TO_YEAR": "2025",
            "PLAYERCODE": "nikola_jokic",
            "PLAYER_SLUG": "nikola_jokić",
            "TEAM_ID": 1610612743,
            "TEAM_CITY": "Denver",
            "TEAM_NAME": "Nuggets",
            "TEAM_ABBREVIATION": "DEN",
            "TEAM_SLUG": "nuggets",
            "TEAM_CODE": "nuggets",
            "GAMES_PLAYED_FLAG": "Y",
            "OTHERLEAGUE_EXPERIENCE_CH": "00",
        }

        player = CommonPlayer.model_validate(data)

        assert player.display_first_last == "Nikola Jokić"
        assert player.display_last_comma_first == "Jokić, Nikola"

    def test_parse_rookie_single_year(self):
        """CommonPlayer handles rookies with same from/to year."""
        data = {
            "PERSON_ID": 1642843,
            "DISPLAY_LAST_COMMA_FIRST": "Flagg, Cooper",
            "DISPLAY_FIRST_LAST": "Cooper Flagg",
            "ROSTERSTATUS": 1,
            "FROM_YEAR": "2025",
            "TO_YEAR": "2025",
            "PLAYERCODE": "tmp_cooper_flagg",
            "PLAYER_SLUG": "cooper_flagg",
            "TEAM_ID": 1610612742,
            "TEAM_CITY": "Dallas",
            "TEAM_NAME": "Mavericks",
            "TEAM_ABBREVIATION": "DAL",
            "TEAM_SLUG": "mavericks",
            "TEAM_CODE": "mavericks",
            "GAMES_PLAYED_FLAG": "Y",
            "OTHERLEAGUE_EXPERIENCE_CH": "00",
        }

        player = CommonPlayer.model_validate(data)

        assert player.from_year == "2025"
        assert player.to_year == "2025"
        assert player.display_first_last == "Cooper Flagg"


class TestCommonAllPlayersResponse:
    """Tests for CommonAllPlayersResponse model."""

    def test_parse_result_sets_format(self):
        """CommonAllPlayersResponse parses tabular data correctly."""
        data = {
            "resource": "commonallplayers",
            "parameters": {
                "LeagueID": "00",
                "Season": "2025-26",
                "IsOnlyCurrentSeason": 1,
            },
            "resultSets": [
                {
                    "name": "CommonAllPlayers",
                    "headers": [
                        "PERSON_ID",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FIRST_LAST",
                        "ROSTERSTATUS",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "PLAYERCODE",
                        "PLAYER_SLUG",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_SLUG",
                        "TEAM_CODE",
                        "GAMES_PLAYED_FLAG",
                        "OTHERLEAGUE_EXPERIENCE_CH",
                    ],
                    "rowSet": [
                        [
                            1630173,
                            "Achiuwa, Precious",
                            "Precious Achiuwa",
                            1,
                            "2020",
                            "2025",
                            "precious_achiuwa",
                            "precious_achiuwa",
                            1610612758,
                            "Sacramento",
                            "Kings",
                            "SAC",
                            "kings",
                            "kings",
                            "Y",
                            "00",
                        ],
                        [
                            203500,
                            "Adams, Steven",
                            "Steven Adams",
                            1,
                            "2013",
                            "2025",
                            "steven_adams",
                            "steven_adams",
                            1610612745,
                            "Houston",
                            "Rockets",
                            "HOU",
                            "rockets",
                            "rockets",
                            "Y",
                            "00",
                        ],
                        [
                            1628389,
                            "Adebayo, Bam",
                            "Bam Adebayo",
                            1,
                            "2017",
                            "2025",
                            "bam_adebayo",
                            "bam_adebayo",
                            1610612748,
                            "Miami",
                            "Heat",
                            "MIA",
                            "heat",
                            "heat",
                            "Y",
                            "00",
                        ],
                    ],
                }
            ],
        }

        response = CommonAllPlayersResponse.model_validate(data)

        assert len(response.players) == 3
        assert response.players[0].display_first_last == "Precious Achiuwa"
        assert response.players[0].team_abbreviation == "SAC"
        assert response.players[1].display_first_last == "Steven Adams"
        assert response.players[1].team_abbreviation == "HOU"
        assert response.players[2].display_first_last == "Bam Adebayo"
        assert response.players[2].team_abbreviation == "MIA"

    def test_handles_empty_result_set(self):
        """CommonAllPlayersResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "CommonAllPlayers",
                    "headers": [
                        "PERSON_ID",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FIRST_LAST",
                        "ROSTERSTATUS",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "PLAYERCODE",
                        "PLAYER_SLUG",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_SLUG",
                        "TEAM_CODE",
                        "GAMES_PLAYED_FLAG",
                        "OTHERLEAGUE_EXPERIENCE_CH",
                    ],
                    "rowSet": [],
                }
            ],
        }

        response = CommonAllPlayersResponse.model_validate(data)

        assert len(response.players) == 0

    def test_handles_free_agents_with_null_fields(self):
        """CommonAllPlayersResponse handles players without teams."""
        data = {
            "resultSets": [
                {
                    "name": "CommonAllPlayers",
                    "headers": [
                        "PERSON_ID",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FIRST_LAST",
                        "ROSTERSTATUS",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "PLAYERCODE",
                        "PLAYER_SLUG",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_SLUG",
                        "TEAM_CODE",
                        "GAMES_PLAYED_FLAG",
                        "OTHERLEAGUE_EXPERIENCE_CH",
                    ],
                    "rowSet": [
                        [
                            1628964,
                            "Bamba, Mo",
                            "Mo Bamba",
                            0,
                            "2018",
                            "2025",
                            "mohamed_bamba",
                            "mo_bamba",
                            0,
                            "",
                            "",
                            "",
                            None,
                            "",
                            "Y",
                            "11",
                        ],
                    ],
                }
            ],
        }

        response = CommonAllPlayersResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].roster_status == 0
        assert response.players[0].team_slug is None
        assert response.players[0].team_id == 0

    def test_preserves_order_from_api(self):
        """CommonAllPlayersResponse maintains order from API response."""
        data = {
            "resultSets": [
                {
                    "name": "CommonAllPlayers",
                    "headers": [
                        "PERSON_ID",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FIRST_LAST",
                        "ROSTERSTATUS",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "PLAYERCODE",
                        "PLAYER_SLUG",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_SLUG",
                        "TEAM_CODE",
                        "GAMES_PLAYED_FLAG",
                        "OTHERLEAGUE_EXPERIENCE_CH",
                    ],
                    "rowSet": [
                        [
                            1,
                            "Zebra, Zack",
                            "Zack Zebra",
                            1,
                            "2020",
                            "2025",
                            "z",
                            "z",
                            1,
                            "C",
                            "T",
                            "AB",
                            "s",
                            "c",
                            "Y",
                            "00",
                        ],
                        [
                            2,
                            "Apple, Adam",
                            "Adam Apple",
                            1,
                            "2020",
                            "2025",
                            "a",
                            "a",
                            1,
                            "C",
                            "T",
                            "AB",
                            "s",
                            "c",
                            "Y",
                            "00",
                        ],
                        [
                            3,
                            "Middle, Mike",
                            "Mike Middle",
                            1,
                            "2020",
                            "2025",
                            "m",
                            "m",
                            1,
                            "C",
                            "T",
                            "AB",
                            "s",
                            "c",
                            "Y",
                            "00",
                        ],
                    ],
                }
            ],
        }

        response = CommonAllPlayersResponse.model_validate(data)

        assert response.players[0].display_first_last == "Zack Zebra"
        assert response.players[1].display_first_last == "Adam Apple"
        assert response.players[2].display_first_last == "Mike Middle"

    def test_handles_various_roster_statuses(self):
        """CommonAllPlayersResponse handles different roster status values."""
        data = {
            "resultSets": [
                {
                    "name": "CommonAllPlayers",
                    "headers": [
                        "PERSON_ID",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FIRST_LAST",
                        "ROSTERSTATUS",
                        "FROM_YEAR",
                        "TO_YEAR",
                        "PLAYERCODE",
                        "PLAYER_SLUG",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_SLUG",
                        "TEAM_CODE",
                        "GAMES_PLAYED_FLAG",
                        "OTHERLEAGUE_EXPERIENCE_CH",
                    ],
                    "rowSet": [
                        [
                            1,
                            "Active, Player",
                            "Player Active",
                            1,
                            "2020",
                            "2025",
                            "a",
                            "a",
                            1,
                            "C",
                            "T",
                            "AB",
                            "s",
                            "c",
                            "Y",
                            "00",
                        ],
                        [
                            2,
                            "Inactive, Player",
                            "Player Inactive",
                            0,
                            "2020",
                            "2025",
                            "i",
                            "i",
                            0,
                            "",
                            "",
                            "",
                            None,
                            "",
                            "Y",
                            "00",
                        ],
                    ],
                }
            ],
        }

        response = CommonAllPlayersResponse.model_validate(data)

        assert response.players[0].roster_status == 1
        assert response.players[1].roster_status == 0
