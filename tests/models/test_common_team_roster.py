from fastbreak.models import Coach, CommonTeamRosterResponse, RosterPlayer


class TestRosterPlayer:
    """Tests for RosterPlayer model."""

    def test_parse_valid_entry(self):
        """RosterPlayer parses valid data."""
        data = {
            "TeamID": 1610612745,
            "SEASON": "2024",
            "LeagueID": "00",
            "PLAYER": "Jalen Green",
            "NICKNAME": "Jalen",
            "PLAYER_SLUG": "jalen-green",
            "NUM": "4",
            "POSITION": "G",
            "HEIGHT": "6-4",
            "WEIGHT": "186",
            "BIRTH_DATE": "FEB 09, 2002",
            "AGE": 23.0,
            "EXP": "3",
            "SCHOOL": "NBA G League Ignite",
            "PLAYER_ID": 1630224,
            "HOW_ACQUIRED": None,
        }

        player = RosterPlayer.model_validate(data)

        assert player.team_id == 1610612745
        assert player.player == "Jalen Green"
        assert player.player_id == 1630224
        assert player.position == "G"
        assert player.age == 23.0
        assert player.how_acquired is None

    def test_parse_with_how_acquired(self):
        """RosterPlayer handles how_acquired field."""
        data = {
            "TeamID": 1610612745,
            "SEASON": "2024",
            "LeagueID": "00",
            "PLAYER": "Fred VanVleet",
            "NICKNAME": "Fred",
            "PLAYER_SLUG": "fred-vanvleet",
            "NUM": "5",
            "POSITION": "G",
            "HEIGHT": "6-0",
            "WEIGHT": "197",
            "BIRTH_DATE": "FEB 25, 1994",
            "AGE": 31.0,
            "EXP": "8",
            "SCHOOL": "Wichita State",
            "PLAYER_ID": 1627832,
            "HOW_ACQUIRED": "Signed on 07/07/23",
        }

        player = RosterPlayer.model_validate(data)

        assert player.how_acquired == "Signed on 07/07/23"

    def test_parse_rookie(self):
        """RosterPlayer handles rookie experience."""
        data = {
            "TeamID": 1610612745,
            "SEASON": "2024",
            "LeagueID": "00",
            "PLAYER": "Reed Sheppard",
            "NICKNAME": "Reed",
            "PLAYER_SLUG": "reed-sheppard",
            "NUM": "15",
            "POSITION": "G",
            "HEIGHT": "6-2",
            "WEIGHT": "185",
            "BIRTH_DATE": "JUN 24, 2004",
            "AGE": 21.0,
            "EXP": "R",
            "SCHOOL": "Kentucky",
            "PLAYER_ID": 1642263,
            "HOW_ACQUIRED": "#3 Pick in 2024 Draft",
        }

        player = RosterPlayer.model_validate(data)

        assert player.exp == "R"
        assert player.how_acquired == "#3 Pick in 2024 Draft"


class TestCoach:
    """Tests for Coach model."""

    def test_parse_head_coach(self):
        """Coach parses head coach data."""
        data = {
            "TEAM_ID": 1610612745,
            "SEASON": "2024",
            "COACH_ID": 203152,
            "FIRST_NAME": "Ime",
            "LAST_NAME": "Udoka",
            "COACH_NAME": "Ime Udoka",
            "IS_ASSISTANT": 1,
            "COACH_TYPE": "Head Coach",
            "SORT_SEQUENCE": None,
            "SUB_SORT_SEQUENCE": 1,
        }

        coach = Coach.model_validate(data)

        assert coach.coach_id == 203152
        assert coach.coach_name == "Ime Udoka"
        assert coach.is_assistant == 1
        assert coach.coach_type == "Head Coach"
        assert coach.sort_sequence is None

    def test_parse_assistant_coach(self):
        """Coach parses assistant coach data."""
        data = {
            "TEAM_ID": 1610612745,
            "SEASON": "2024",
            "COACH_ID": 1628179,
            "FIRST_NAME": "Royal",
            "LAST_NAME": "Ivey",
            "COACH_NAME": "Royal Ivey",
            "IS_ASSISTANT": 2,
            "COACH_TYPE": "Assistant Coach",
            "SORT_SEQUENCE": None,
            "SUB_SORT_SEQUENCE": 5,
        }

        coach = Coach.model_validate(data)

        assert coach.is_assistant == 2
        assert coach.coach_type == "Assistant Coach"


class TestCommonTeamRosterResponse:
    """Tests for CommonTeamRosterResponse model."""

    def test_parse_result_sets_format(self):
        """CommonTeamRosterResponse parses tabular data correctly."""
        data = {
            "resource": "commonteamroster",
            "parameters": {
                "TeamID": 1610612745,
                "LeagueID": "00",
                "Season": "2024-25",
            },
            "resultSets": [
                {
                    "name": "CommonTeamRoster",
                    "headers": [
                        "TeamID",
                        "SEASON",
                        "LeagueID",
                        "PLAYER",
                        "NICKNAME",
                        "PLAYER_SLUG",
                        "NUM",
                        "POSITION",
                        "HEIGHT",
                        "WEIGHT",
                        "BIRTH_DATE",
                        "AGE",
                        "EXP",
                        "SCHOOL",
                        "PLAYER_ID",
                        "HOW_ACQUIRED",
                    ],
                    "rowSet": [
                        [
                            1610612745,
                            "2024",
                            "00",
                            "Jalen Green",
                            "Jalen",
                            "jalen-green",
                            "4",
                            "G",
                            "6-4",
                            "186",
                            "FEB 09, 2002",
                            23.0,
                            "3",
                            "NBA G League Ignite",
                            1630224,
                            None,
                        ],
                        [
                            1610612745,
                            "2024",
                            "00",
                            "Alperen Sengun",
                            "Alperen",
                            "alperen-sengun",
                            "28",
                            "C",
                            "6-11",
                            "243",
                            "JUL 25, 2002",
                            22.0,
                            "3",
                            "Besiktas",
                            1630578,
                            "Draft Rights Traded from OKC on 07/30/21",
                        ],
                    ],
                },
                {
                    "name": "Coaches",
                    "headers": [
                        "TEAM_ID",
                        "SEASON",
                        "COACH_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "COACH_NAME",
                        "IS_ASSISTANT",
                        "COACH_TYPE",
                        "SORT_SEQUENCE",
                        "SUB_SORT_SEQUENCE",
                    ],
                    "rowSet": [
                        [
                            1610612745,
                            "2024",
                            203152,
                            "Ime",
                            "Udoka",
                            "Ime Udoka",
                            1,
                            "Head Coach",
                            None,
                            1,
                        ],
                    ],
                },
            ],
        }

        response = CommonTeamRosterResponse.model_validate(data)

        assert len(response.players) == 2
        assert response.players[0].player == "Jalen Green"
        assert response.players[1].player == "Alperen Sengun"
        assert len(response.coaches) == 1
        assert response.coaches[0].coach_name == "Ime Udoka"

    def test_handles_empty_roster(self):
        """CommonTeamRosterResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "CommonTeamRoster",
                    "headers": [
                        "TeamID",
                        "SEASON",
                        "LeagueID",
                        "PLAYER",
                        "NICKNAME",
                        "PLAYER_SLUG",
                        "NUM",
                        "POSITION",
                        "HEIGHT",
                        "WEIGHT",
                        "BIRTH_DATE",
                        "AGE",
                        "EXP",
                        "SCHOOL",
                        "PLAYER_ID",
                        "HOW_ACQUIRED",
                    ],
                    "rowSet": [],
                },
                {
                    "name": "Coaches",
                    "headers": [
                        "TEAM_ID",
                        "SEASON",
                        "COACH_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "COACH_NAME",
                        "IS_ASSISTANT",
                        "COACH_TYPE",
                        "SORT_SEQUENCE",
                        "SUB_SORT_SEQUENCE",
                    ],
                    "rowSet": [],
                },
            ],
        }

        response = CommonTeamRosterResponse.model_validate(data)

        assert len(response.players) == 0
        assert len(response.coaches) == 0

    def test_multiple_coaches(self):
        """CommonTeamRosterResponse handles multiple coaches."""
        data = {
            "resultSets": [
                {
                    "name": "CommonTeamRoster",
                    "headers": [
                        "TeamID",
                        "SEASON",
                        "LeagueID",
                        "PLAYER",
                        "NICKNAME",
                        "PLAYER_SLUG",
                        "NUM",
                        "POSITION",
                        "HEIGHT",
                        "WEIGHT",
                        "BIRTH_DATE",
                        "AGE",
                        "EXP",
                        "SCHOOL",
                        "PLAYER_ID",
                        "HOW_ACQUIRED",
                    ],
                    "rowSet": [],
                },
                {
                    "name": "Coaches",
                    "headers": [
                        "TEAM_ID",
                        "SEASON",
                        "COACH_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "COACH_NAME",
                        "IS_ASSISTANT",
                        "COACH_TYPE",
                        "SORT_SEQUENCE",
                        "SUB_SORT_SEQUENCE",
                    ],
                    "rowSet": [
                        [
                            1610612745,
                            "2024",
                            203152,
                            "Ime",
                            "Udoka",
                            "Ime Udoka",
                            1,
                            "Head Coach",
                            None,
                            1,
                        ],
                        [
                            1610612745,
                            "2024",
                            204224,
                            "Ben",
                            "Sullivan",
                            "Ben Sullivan",
                            2,
                            "Assistant Coach",
                            None,
                            5,
                        ],
                        [
                            1610612745,
                            "2024",
                            1628179,
                            "Royal",
                            "Ivey",
                            "Royal Ivey",
                            2,
                            "Assistant Coach",
                            None,
                            5,
                        ],
                    ],
                },
            ],
        }

        response = CommonTeamRosterResponse.model_validate(data)

        assert len(response.coaches) == 3
        coach_types = [c.coach_type for c in response.coaches]
        assert "Head Coach" in coach_types
        assert coach_types.count("Assistant Coach") == 2
