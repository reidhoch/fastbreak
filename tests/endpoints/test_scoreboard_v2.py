"""Tests for the ScoreboardV2 endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints.scoreboard_v2 import ScoreboardV2
from fastbreak.models.scoreboard_v2 import ScoreboardV2Response


class TestScoreboardV2:
    """Tests for ScoreboardV2 endpoint."""

    def test_init_with_defaults(self):
        """ScoreboardV2 uses sensible defaults."""
        endpoint = ScoreboardV2()

        assert endpoint.game_date == ""
        assert endpoint.league_id == "00"
        assert endpoint.day_offset == "0"

    def test_init_with_game_date(self):
        """ScoreboardV2 accepts game date."""
        endpoint = ScoreboardV2(game_date="2024-12-25")

        assert endpoint.game_date == "2024-12-25"
        assert endpoint.league_id == "00"
        assert endpoint.day_offset == "0"

    def test_init_with_custom_league(self):
        """ScoreboardV2 accepts custom league ID."""
        endpoint = ScoreboardV2(league_id="10", game_date="2024-07-15")

        assert endpoint.league_id == "10"

    def test_init_with_day_offset(self):
        """ScoreboardV2 accepts day offset."""
        endpoint = ScoreboardV2(game_date="2024-12-25", day_offset="1")

        assert endpoint.day_offset == "1"

    def test_params_returns_correct_dict(self):
        """params() returns correct parameters."""
        endpoint = ScoreboardV2(game_date="2024-12-25")

        params = endpoint.params()

        assert params == {
            "GameDate": "2024-12-25",
            "LeagueID": "00",
            "DayOffset": "0",
        }

    def test_path_is_correct(self):
        """ScoreboardV2 has correct API path."""
        endpoint = ScoreboardV2(game_date="2024-12-25")

        assert endpoint.path == "scoreboardv2"

    def test_response_model_is_correct(self):
        """ScoreboardV2 uses ScoreboardV2Response model."""
        endpoint = ScoreboardV2(game_date="2024-12-25")

        assert endpoint.response_model is ScoreboardV2Response

    def test_endpoint_is_frozen(self):
        """ScoreboardV2 is immutable (frozen dataclass)."""
        endpoint = ScoreboardV2(game_date="2024-12-25")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_date = "2024-01-01"  # type: ignore[misc]


class TestScoreboardV2Response:
    """Tests for ScoreboardV2Response model."""

    def test_response_from_api_data(self):
        """Response parses NBA API tabular resultSets format correctly."""
        api_data = {
            "resource": "scoreboardV2",
            "parameters": {
                "GameDate": "2024-12-25",
                "LeagueID": "00",
                "DayOffset": "0",
            },
            "resultSets": [
                {
                    "name": "GameHeader",
                    "headers": [
                        "GAME_DATE_EST",
                        "GAME_SEQUENCE",
                        "GAME_ID",
                        "GAME_STATUS_ID",
                        "GAME_STATUS_TEXT",
                        "GAMECODE",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "SEASON",
                        "LIVE_PERIOD",
                        "LIVE_PC_TIME",
                        "NATL_TV_BROADCASTER_ABBREVIATION",
                        "HOME_TV_BROADCASTER_ABBREVIATION",
                        "AWAY_TV_BROADCASTER_ABBREVIATION",
                        "LIVE_PERIOD_TIME_BCAST",
                        "ARENA_NAME",
                        "WH_STATUS",
                        "WNBA_COMMISSIONER_FLAG",
                    ],
                    "rowSet": [
                        [
                            "2024-12-25T00:00:00",
                            1,
                            "0022400405",
                            3,
                            "Final",
                            "20241225/SASNYK",
                            1610612752,
                            1610612759,
                            "2024",
                            4,
                            "     ",
                            "ABC/ESPN",
                            None,
                            None,
                            "Q4       - ABC/ESPN",
                            "Madison Square Garden",
                            1,
                            0,
                        ],
                    ],
                },
                {
                    "name": "LineScore",
                    "headers": [
                        "GAME_DATE_EST",
                        "GAME_SEQUENCE",
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_CITY_NAME",
                        "TEAM_NAME",
                        "TEAM_WINS_LOSSES",
                        "PTS_QTR1",
                        "PTS_QTR2",
                        "PTS_QTR3",
                        "PTS_QTR4",
                        "PTS_OT1",
                        "PTS_OT2",
                        "PTS_OT3",
                        "PTS_OT4",
                        "PTS_OT5",
                        "PTS_OT6",
                        "PTS_OT7",
                        "PTS_OT8",
                        "PTS_OT9",
                        "PTS_OT10",
                        "PTS",
                        "FG_PCT",
                        "FT_PCT",
                        "FG3_PCT",
                        "AST",
                        "REB",
                        "TOV",
                    ],
                    "rowSet": [
                        [
                            "2024-12-25T00:00:00",
                            1,
                            "0022400405",
                            1610612759,
                            "SAS",
                            "San Antonio",
                            "Spurs",
                            "15-15",
                            27,
                            31,
                            25,
                            31,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            114,
                            0.506,
                            0.824,
                            0.421,
                            33,
                            45,
                            15,
                        ],
                        [
                            "2024-12-25T00:00:00",
                            1,
                            "0022400405",
                            1610612752,
                            "NYK",
                            "New York",
                            "Knicks",
                            "20-10",
                            28,
                            23,
                            37,
                            29,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            117,
                            0.45,
                            0.875,
                            0.333,
                            26,
                            47,
                            5,
                        ],
                    ],
                },
                {
                    "name": "SeriesStandings",
                    "headers": [
                        "GAME_ID",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "GAME_DATE_EST",
                        "HOME_TEAM_WINS",
                        "HOME_TEAM_LOSSES",
                        "SERIES_LEADER",
                    ],
                    "rowSet": [
                        [
                            "0022400405",
                            1610612752,
                            1610612759,
                            "2024-12-25T00:00:00",
                            1,
                            1,
                            "Tied",
                        ],
                    ],
                },
                {
                    "name": "LastMeeting",
                    "headers": [
                        "GAME_ID",
                        "LAST_GAME_ID",
                        "LAST_GAME_DATE_EST",
                        "LAST_GAME_HOME_TEAM_ID",
                        "LAST_GAME_HOME_TEAM_CITY",
                        "LAST_GAME_HOME_TEAM_NAME",
                        "LAST_GAME_HOME_TEAM_ABBREVIATION",
                        "LAST_GAME_HOME_TEAM_POINTS",
                        "LAST_GAME_VISITOR_TEAM_ID",
                        "LAST_GAME_VISITOR_TEAM_CITY",
                        "LAST_GAME_VISITOR_TEAM_NAME",
                        "LAST_GAME_VISITOR_TEAM_CITY1",
                        "LAST_GAME_VISITOR_TEAM_POINTS",
                    ],
                    "rowSet": [
                        [
                            "0022400405",
                            "0022301070",
                            "2024-03-29T00:00:00",
                            1610612752,
                            "New York",
                            "Knicks",
                            "NYK",
                            126,
                            1610612759,
                            "San Antonio",
                            "Spurs",
                            "SAS",
                            130,
                        ],
                    ],
                },
                {
                    "name": "EastConfStandingsByDay",
                    "headers": [
                        "TEAM_ID",
                        "LEAGUE_ID",
                        "SEASON_ID",
                        "STANDINGSDATE",
                        "CONFERENCE",
                        "TEAM",
                        "G",
                        "W",
                        "L",
                        "W_PCT",
                        "HOME_RECORD",
                        "ROAD_RECORD",
                    ],
                    "rowSet": [
                        [
                            1610612739,
                            "00",
                            "22024",
                            "2024-12-25",
                            "East",
                            "Cleveland",
                            30,
                            26,
                            4,
                            0.867,
                            "17-1",
                            "9-3",
                        ],
                    ],
                },
                {
                    "name": "WestConfStandingsByDay",
                    "headers": [
                        "TEAM_ID",
                        "LEAGUE_ID",
                        "SEASON_ID",
                        "STANDINGSDATE",
                        "CONFERENCE",
                        "TEAM",
                        "G",
                        "W",
                        "L",
                        "W_PCT",
                        "HOME_RECORD",
                        "ROAD_RECORD",
                    ],
                    "rowSet": [
                        [
                            1610612760,
                            "00",
                            "22024",
                            "2024-12-25",
                            "West",
                            "Oklahoma City",
                            28,
                            23,
                            5,
                            0.821,
                            "11-2",
                            "11-3",
                        ],
                    ],
                },
                {
                    "name": "Available",
                    "headers": ["GAME_ID", "PT_AVAILABLE"],
                    "rowSet": [["0022400405", 0]],
                },
                {
                    "name": "TeamLeaders",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NICKNAME",
                        "TEAM_ABBREVIATION",
                        "PTS_PLAYER_ID",
                        "PTS_PLAYER_NAME",
                        "PTS",
                        "REB_PLAYER_ID",
                        "REB_PLAYER_NAME",
                        "REB",
                        "AST_PLAYER_ID",
                        "AST_PLAYER_NAME",
                        "AST",
                    ],
                    "rowSet": [
                        [
                            "0022400405",
                            1610612752,
                            "New York",
                            "Knicks",
                            "NYK",
                            1628969,
                            "Mikal Bridges",
                            41,
                            1628404,
                            "Josh Hart",
                            12,
                            1628973,
                            "Jalen Brunson",
                            9,
                        ],
                    ],
                },
                {
                    "name": "TicketLinks",
                    "headers": ["GAME_ID", "LEAG_TIX"],
                    "rowSet": [],
                },
            ],
        }

        response = ScoreboardV2Response.model_validate(api_data)

        # Check game header
        assert len(response.game_header) == 1
        game = response.game_header[0]
        assert game.game_id == "0022400405"
        assert game.game_status_text == "Final"
        assert game.home_team_id == 1610612752
        assert game.visitor_team_id == 1610612759
        assert game.arena_name == "Madison Square Garden"
        assert game.natl_tv_broadcaster_abbreviation == "ABC/ESPN"

        # Check line scores
        assert len(response.line_score) == 2
        spurs = response.line_score[0]
        assert spurs.team_abbreviation == "SAS"
        assert spurs.pts == 114
        assert spurs.pts_qtr1 == 27
        assert spurs.pts_qtr3 == 25
        assert spurs.fg_pct == 0.506

        knicks = response.line_score[1]
        assert knicks.team_abbreviation == "NYK"
        assert knicks.pts == 117
        assert knicks.team_wins_losses == "20-10"

        # Check series standings
        assert len(response.series_standings) == 1
        series = response.series_standings[0]
        assert series.series_leader == "Tied"
        assert series.home_team_wins == 1

        # Check last meeting
        assert len(response.last_meeting) == 1
        meeting = response.last_meeting[0]
        assert meeting.last_game_home_team_name == "Knicks"
        assert meeting.last_game_home_team_points == 126
        assert meeting.last_game_visitor_team_points == 130

        # Check conference standings
        assert len(response.east_conf_standings_by_day) == 1
        east_team = response.east_conf_standings_by_day[0]
        assert east_team.team == "Cleveland"
        assert east_team.wins == 26
        assert east_team.win_pct == 0.867

        assert len(response.west_conf_standings_by_day) == 1
        west_team = response.west_conf_standings_by_day[0]
        assert west_team.team == "Oklahoma City"
        assert west_team.wins == 23

        # Check team leaders
        assert len(response.team_leaders) == 1
        leader = response.team_leaders[0]
        assert leader.pts_player_name == "Mikal Bridges"
        assert leader.pts == 41
        assert leader.reb_player_name == "Josh Hart"
        assert leader.reb == 12

        # Check empty result sets
        assert len(response.ticket_links) == 0

    def test_response_empty_games(self):
        """Response handles no games gracefully."""
        api_data = {
            "resource": "scoreboardV2",
            "resultSets": [
                {"name": "GameHeader", "headers": ["GAME_ID"], "rowSet": []},
                {"name": "LineScore", "headers": ["GAME_ID"], "rowSet": []},
                {"name": "SeriesStandings", "headers": ["GAME_ID"], "rowSet": []},
                {"name": "LastMeeting", "headers": ["GAME_ID"], "rowSet": []},
                {
                    "name": "EastConfStandingsByDay",
                    "headers": ["TEAM_ID"],
                    "rowSet": [],
                },
                {
                    "name": "WestConfStandingsByDay",
                    "headers": ["TEAM_ID"],
                    "rowSet": [],
                },
                {"name": "Available", "headers": ["GAME_ID"], "rowSet": []},
                {"name": "TeamLeaders", "headers": ["GAME_ID"], "rowSet": []},
                {"name": "TicketLinks", "headers": ["GAME_ID"], "rowSet": []},
            ],
        }

        response = ScoreboardV2Response.model_validate(api_data)

        assert len(response.game_header) == 0
        assert len(response.line_score) == 0
        assert len(response.east_conf_standings_by_day) == 0
