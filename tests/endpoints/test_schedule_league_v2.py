"""Tests for the ScheduleLeagueV2 endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints.schedule_league_v2 import ScheduleLeagueV2
from fastbreak.models.schedule_league_v2 import ScheduleLeagueV2Response


class TestScheduleLeagueV2:
    """Tests for ScheduleLeagueV2 endpoint."""

    def test_init_with_defaults(self):
        """ScheduleLeagueV2 uses sensible defaults."""
        endpoint = ScheduleLeagueV2()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"

    def test_init_with_custom_season(self):
        """ScheduleLeagueV2 accepts custom season."""
        endpoint = ScheduleLeagueV2(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_league(self):
        """ScheduleLeagueV2 accepts custom league ID."""
        endpoint = ScheduleLeagueV2(league_id="10")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correct parameters."""
        endpoint = ScheduleLeagueV2(season="2023-24")

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2023-24",
        }

    def test_path_is_correct(self):
        """ScheduleLeagueV2 has correct API path."""
        endpoint = ScheduleLeagueV2()

        assert endpoint.path == "scheduleleaguev2"

    def test_response_model_is_correct(self):
        """ScheduleLeagueV2 uses ScheduleLeagueV2Response model."""
        endpoint = ScheduleLeagueV2()

        assert endpoint.response_model is ScheduleLeagueV2Response

    def test_endpoint_is_frozen(self):
        """ScheduleLeagueV2 is immutable (frozen dataclass)."""
        endpoint = ScheduleLeagueV2()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestScheduleLeagueV2Response:
    """Tests for ScheduleLeagueV2Response model."""

    def test_response_from_api_data(self):
        """Response parses NBA API nested JSON format correctly."""
        api_data = {
            "leagueSchedule": {
                "seasonYear": "2023-24",
                "leagueId": "00",
                "gameDates": [
                    {
                        "gameDate": "10/24/2023 00:00:00",
                        "games": [
                            {
                                "gameId": "0022300061",
                                "gameCode": "20231024/LALLAC",
                                "gameStatus": 3,
                                "gameStatusText": "Final",
                                "gameSequence": 1,
                                "gameDateEst": "2023-10-24T00:00:00Z",
                                "gameTimeEst": "1900-01-01T19:30:00Z",
                                "gameDateTimeEst": "2023-10-24T19:30:00Z",
                                "gameDateUTC": "2023-10-24T04:00:00Z",
                                "gameTimeUTC": "1900-01-01T23:30:00Z",
                                "gameDateTimeUTC": "2023-10-24T23:30:00Z",
                                "awayTeamTime": "2023-10-24T16:30:00Z",
                                "homeTeamTime": "2023-10-24T19:30:00Z",
                                "day": "Tue",
                                "monthNum": 10,
                                "weekNumber": 1,
                                "weekName": "Week 1",
                                "ifNecessary": "false",
                                "seriesGameNumber": "",
                                "gameLabel": "",
                                "gameSubLabel": "",
                                "seriesText": "",
                                "arenaName": "Crypto.com Arena",
                                "arenaState": "CA",
                                "arenaCity": "Los Angeles",
                                "postponedStatus": "A",
                                "branchLink": "",
                                "gameSubtype": "",
                                "isNeutral": False,
                                "broadcasters": {
                                    "nationalBroadcasters": [
                                        {
                                            "broadcasterScope": "natl",
                                            "broadcasterMedia": "tv",
                                            "broadcasterId": 1,
                                            "broadcasterDisplay": "TNT",
                                            "broadcasterAbbreviation": "TNT",
                                            "broadcasterDescription": "",
                                            "tapeDelayComments": "",
                                            "broadcasterVideoLink": "",
                                            "broadcasterTeamId": -1,
                                            "broadcasterRanking": 0,
                                        }
                                    ],
                                    "nationalRadioBroadcasters": [],
                                    "nationalOttBroadcasters": [],
                                    "homeTvBroadcasters": [],
                                    "homeRadioBroadcasters": [],
                                    "homeOttBroadcasters": [],
                                    "awayTvBroadcasters": [],
                                    "awayRadioBroadcasters": [],
                                    "awayOttBroadcasters": [],
                                },
                                "homeTeam": {
                                    "teamId": 1610612746,
                                    "teamName": "Clippers",
                                    "teamCity": "LA",
                                    "teamTricode": "LAC",
                                    "teamSlug": "clippers",
                                    "wins": 1,
                                    "losses": 0,
                                    "score": 97,
                                    "seed": 0,
                                },
                                "awayTeam": {
                                    "teamId": 1610612747,
                                    "teamName": "Lakers",
                                    "teamCity": "Los Angeles",
                                    "teamTricode": "LAL",
                                    "teamSlug": "lakers",
                                    "wins": 0,
                                    "losses": 1,
                                    "score": 95,
                                    "seed": 0,
                                },
                                "pointsLeaders": [
                                    {
                                        "personId": 201566,
                                        "firstName": "Kawhi",
                                        "lastName": "Leonard",
                                        "teamId": 1610612746,
                                        "teamCity": "LA",
                                        "teamName": "Clippers",
                                        "teamTricode": "LAC",
                                        "points": 25.0,
                                    }
                                ],
                            }
                        ],
                    }
                ],
                "weeks": [
                    {
                        "weekNumber": 1,
                        "weekName": "Week 1",
                        "startDate": "2023-10-24T00:00:00Z",
                        "endDate": "2023-10-29T00:00:00Z",
                    }
                ],
            }
        }

        response = ScheduleLeagueV2Response.model_validate(api_data)

        # Check league schedule metadata
        assert response.league_schedule is not None
        assert response.league_schedule.season_year == "2023-24"
        assert response.league_schedule.league_id == "00"

        # Check game dates
        assert len(response.league_schedule.game_dates) == 1
        game_date = response.league_schedule.game_dates[0]
        assert game_date.game_date == "10/24/2023 00:00:00"
        assert len(game_date.games) == 1

        # Check game details
        game = game_date.games[0]
        assert game.game_id == "0022300061"
        assert game.game_status_text == "Final"
        assert game.arena_name == "Crypto.com Arena"
        assert game.arena_city == "Los Angeles"

        # Check teams
        assert game.home_team is not None
        assert game.home_team.team_name == "Clippers"
        assert game.home_team.score == 97
        assert game.away_team is not None
        assert game.away_team.team_name == "Lakers"
        assert game.away_team.score == 95

        # Check broadcasters
        assert game.broadcasters is not None
        assert len(game.broadcasters.national_broadcasters) == 1
        assert game.broadcasters.national_broadcasters[0].broadcaster_display == "TNT"

        # Check points leaders
        assert len(game.points_leaders) == 1
        assert game.points_leaders[0].first_name == "Kawhi"
        assert game.points_leaders[0].last_name == "Leonard"
        assert game.points_leaders[0].points == 25.0

        # Check weeks
        assert len(response.league_schedule.weeks) == 1
        assert response.league_schedule.weeks[0].week_name == "Week 1"

    def test_response_empty_schedule(self):
        """Response handles empty schedule gracefully."""
        api_data = {
            "leagueSchedule": {
                "seasonYear": "2024-25",
                "leagueId": "00",
                "gameDates": [],
                "weeks": [],
            }
        }

        response = ScheduleLeagueV2Response.model_validate(api_data)

        assert response.league_schedule is not None
        assert len(response.league_schedule.game_dates) == 0
        assert len(response.league_schedule.weeks) == 0

    def test_response_missing_optional_fields(self):
        """Response handles missing optional fields gracefully."""
        api_data = {
            "leagueSchedule": {
                "seasonYear": "2024-25",
                "leagueId": "00",
                "gameDates": [
                    {
                        "gameDate": "10/24/2023",
                        "games": [
                            {
                                "gameId": "0022300001",
                                "homeTeam": {"teamId": 1, "teamName": "Team A"},
                                "awayTeam": {"teamId": 2, "teamName": "Team B"},
                            }
                        ],
                    }
                ],
                "weeks": [],
            }
        }

        response = ScheduleLeagueV2Response.model_validate(api_data)

        assert response.league_schedule is not None
        game = response.league_schedule.game_dates[0].games[0]
        assert game.game_id == "0022300001"
        assert game.home_team is not None
        assert game.home_team.team_name == "Team A"
        # Check optional fields default to None
        assert game.game_status is None
        assert game.arena_name is None
        assert game.broadcasters is None
