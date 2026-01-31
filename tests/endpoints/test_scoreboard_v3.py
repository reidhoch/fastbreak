"""Tests for the ScoreboardV3 endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints.scoreboard_v3 import ScoreboardV3
from fastbreak.models.scoreboard_v3 import ScoreboardV3Response


class TestScoreboardV3:
    """Tests for ScoreboardV3 endpoint."""

    def test_init_with_defaults(self):
        """ScoreboardV3 uses sensible defaults."""
        endpoint = ScoreboardV3()

        assert endpoint.league_id == "00"
        assert endpoint.game_date == ""

    def test_init_with_game_date(self):
        """ScoreboardV3 accepts game date."""
        endpoint = ScoreboardV3(game_date="2024-12-25")

        assert endpoint.game_date == "2024-12-25"

    def test_init_with_custom_league(self):
        """ScoreboardV3 accepts custom league ID."""
        endpoint = ScoreboardV3(league_id="10", game_date="2024-07-15")

        assert endpoint.league_id == "10"

    def test_params_returns_correct_dict(self):
        """params() returns correct parameters."""
        endpoint = ScoreboardV3(game_date="2024-12-25")

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "GameDate": "2024-12-25",
        }

    def test_path_is_correct(self):
        """ScoreboardV3 has correct API path."""
        endpoint = ScoreboardV3()

        assert endpoint.path == "scoreboardv3"

    def test_response_model_is_correct(self):
        """ScoreboardV3 uses ScoreboardV3Response model."""
        endpoint = ScoreboardV3()

        assert endpoint.response_model is ScoreboardV3Response

    def test_endpoint_is_frozen(self):
        """ScoreboardV3 is immutable (frozen dataclass)."""
        endpoint = ScoreboardV3()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_date = "2024-01-01"  # type: ignore[misc]


class TestScoreboardV3Response:
    """Tests for ScoreboardV3Response model."""

    def test_response_from_api_data(self):
        """Response parses NBA API nested JSON format correctly."""
        api_data = {
            "scoreboard": {
                "gameDate": "2024-12-25",
                "leagueId": "00",
                "leagueName": "National Basketball Association",
                "games": [
                    {
                        "gameId": "0022400405",
                        "gameCode": "20241225/SASNYK",
                        "gameStatus": 3,
                        "gameStatusText": "Final",
                        "period": 4,
                        "gameClock": "",
                        "gameTimeUTC": "2024-12-25T17:00:00Z",
                        "gameEt": "2024-12-25T12:00:00Z",
                        "regulationPeriods": 4,
                        "seriesGameNumber": "",
                        "gameLabel": "",
                        "gameSubLabel": "",
                        "seriesText": "",
                        "ifNecessary": False,
                        "seriesConference": "",
                        "poRoundDesc": "",
                        "gameSubtype": "",
                        "isNeutral": False,
                        "gameLeaders": {
                            "homeLeaders": {
                                "personId": 1628969,
                                "name": "Mikal Bridges",
                                "playerSlug": "mikal-bridges",
                                "jerseyNum": "25",
                                "position": "G-F",
                                "teamTricode": "NYK",
                                "points": 41,
                                "rebounds": 1,
                                "assists": 4,
                            },
                            "awayLeaders": {
                                "personId": 1641705,
                                "name": "Victor Wembanyama",
                                "playerSlug": "victor-wembanyama",
                                "jerseyNum": "1",
                                "position": "F-C",
                                "teamTricode": "SAS",
                                "points": 42,
                                "rebounds": 18,
                                "assists": 4,
                            },
                        },
                        "teamLeaders": {
                            "homeLeaders": {
                                "personId": 1626157,
                                "name": "Karl-Anthony Towns",
                                "playerSlug": "karl-anthony-towns",
                                "jerseyNum": "32",
                                "position": "C-F",
                                "teamTricode": "NYK",
                                "points": 24.4,
                                "rebounds": 12.8,
                                "assists": 3.1,
                            },
                            "awayLeaders": {
                                "personId": 1628368,
                                "name": "De'Aaron Fox",
                                "playerSlug": "deaaron-fox",
                                "jerseyNum": "4",
                                "position": "G",
                                "teamTricode": "SAS",
                                "points": 23.5,
                                "rebounds": 4.8,
                                "assists": 6.3,
                            },
                            "seasonLeadersFlag": 0,
                        },
                        "broadcasters": {
                            "nationalBroadcasters": [
                                {
                                    "broadcasterId": 1001315,
                                    "broadcastDisplay": "ABC/ESPN",
                                    "broadcasterTeamId": -1,
                                    "broadcasterDescription": "",
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
                            "teamId": 1610612752,
                            "teamName": "Knicks",
                            "teamCity": "New York",
                            "teamTricode": "NYK",
                            "teamSlug": "knicks",
                            "wins": 20,
                            "losses": 10,
                            "score": 117,
                            "seed": 0,
                            "inBonus": None,
                            "timeoutsRemaining": 0,
                            "periods": [
                                {"period": 1, "periodType": "REGULAR", "score": 28},
                                {"period": 2, "periodType": "REGULAR", "score": 23},
                                {"period": 3, "periodType": "REGULAR", "score": 37},
                                {"period": 4, "periodType": "REGULAR", "score": 29},
                            ],
                        },
                        "awayTeam": {
                            "teamId": 1610612759,
                            "teamName": "Spurs",
                            "teamCity": "San Antonio",
                            "teamTricode": "SAS",
                            "teamSlug": "spurs",
                            "wins": 15,
                            "losses": 15,
                            "score": 114,
                            "seed": 0,
                            "inBonus": None,
                            "timeoutsRemaining": 1,
                            "periods": [
                                {"period": 1, "periodType": "REGULAR", "score": 27},
                                {"period": 2, "periodType": "REGULAR", "score": 31},
                                {"period": 3, "periodType": "REGULAR", "score": 25},
                                {"period": 4, "periodType": "REGULAR", "score": 31},
                            ],
                        },
                    }
                ],
            }
        }

        response = ScoreboardV3Response.model_validate(api_data)

        # Check scoreboard metadata
        assert response.scoreboard is not None
        assert response.scoreboard.game_date == "2024-12-25"
        assert response.scoreboard.league_id == "00"
        assert response.scoreboard.league_name == "National Basketball Association"

        # Check games
        assert len(response.scoreboard.games) == 1
        game = response.scoreboard.games[0]
        assert game.game_id == "0022400405"
        assert game.game_status == 3
        assert game.game_status_text == "Final"
        assert game.period == 4

        # Check game leaders
        assert game.game_leaders is not None
        assert game.game_leaders.home_leaders is not None
        assert game.game_leaders.home_leaders.name == "Mikal Bridges"
        assert game.game_leaders.home_leaders.points == 41
        assert game.game_leaders.away_leaders is not None
        assert game.game_leaders.away_leaders.name == "Victor Wembanyama"
        assert game.game_leaders.away_leaders.points == 42
        assert game.game_leaders.away_leaders.rebounds == 18

        # Check team leaders (season averages)
        assert game.team_leaders is not None
        assert game.team_leaders.home_leaders is not None
        assert game.team_leaders.home_leaders.name == "Karl-Anthony Towns"
        assert game.team_leaders.home_leaders.points == 24.4  # Float for season avg

        # Check teams
        assert game.home_team is not None
        assert game.home_team.team_name == "Knicks"
        assert game.home_team.score == 117
        assert game.home_team.wins == 20
        assert game.home_team.losses == 10

        # Check periods
        assert len(game.home_team.periods) == 4
        assert game.home_team.periods[0].period == 1
        assert game.home_team.periods[0].score == 28
        assert game.home_team.periods[2].score == 37  # Q3

        assert game.away_team is not None
        assert game.away_team.team_name == "Spurs"
        assert game.away_team.score == 114

        # Check broadcasters
        assert game.broadcasters is not None
        assert len(game.broadcasters.national_broadcasters) == 1
        assert (
            game.broadcasters.national_broadcasters[0].broadcast_display == "ABC/ESPN"
        )

    def test_response_empty_games(self):
        """Response handles no games gracefully."""
        api_data = {
            "scoreboard": {
                "gameDate": "2024-07-04",
                "leagueId": "00",
                "leagueName": "National Basketball Association",
                "games": [],
            }
        }

        response = ScoreboardV3Response.model_validate(api_data)

        assert response.scoreboard is not None
        assert len(response.scoreboard.games) == 0

    def test_response_live_game(self):
        """Response handles in-progress game with game clock."""
        api_data = {
            "scoreboard": {
                "gameDate": "2024-12-25",
                "leagueId": "00",
                "leagueName": "National Basketball Association",
                "games": [
                    {
                        "gameId": "0022400406",
                        "gameStatus": 2,
                        "gameStatusText": "Q3 5:42",
                        "period": 3,
                        "gameClock": "PT05M42.00S",
                        "homeTeam": {
                            "teamId": 1,
                            "teamName": "Team A",
                            "score": 72,
                            "inBonus": "1",
                            "timeoutsRemaining": 4,
                            "periods": [],
                        },
                        "awayTeam": {
                            "teamId": 2,
                            "teamName": "Team B",
                            "score": 68,
                            "inBonus": None,
                            "timeoutsRemaining": 3,
                            "periods": [],
                        },
                    }
                ],
            }
        }

        response = ScoreboardV3Response.model_validate(api_data)

        game = response.scoreboard.games[0]
        assert game.game_status == 2  # In progress
        assert game.game_status_text == "Q3 5:42"
        assert game.game_clock == "PT05M42.00S"
        assert game.home_team.in_bonus == "1"
        assert game.home_team.timeouts_remaining == 4
        assert game.away_team.in_bonus is None
