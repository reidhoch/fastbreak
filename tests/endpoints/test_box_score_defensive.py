"""Tests for BoxScoreDefensive endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import BoxScoreDefensive
from fastbreak.models import BoxScoreDefensiveResponse


class TestBoxScoreDefensive:
    """Tests for BoxScoreDefensive endpoint."""

    def test_init_with_game_id(self):
        """BoxScoreDefensive requires game_id."""
        endpoint = BoxScoreDefensive(game_id="0022400001")

        assert endpoint.game_id == "0022400001"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = BoxScoreDefensive(game_id="0022400001")

        params = endpoint.params()

        assert params == {"GameID": "0022400001"}

    def test_path_is_correct(self):
        """BoxScoreDefensive has correct API path."""
        endpoint = BoxScoreDefensive(game_id="0022400001")

        assert endpoint.path == "boxscoredefensivev2"

    def test_response_model_is_correct(self):
        """BoxScoreDefensive uses BoxScoreDefensiveResponse model."""
        endpoint = BoxScoreDefensive(game_id="0022400001")

        assert endpoint.response_model is BoxScoreDefensiveResponse

    def test_endpoint_is_frozen(self):
        """BoxScoreDefensive is immutable (frozen dataclass)."""
        endpoint = BoxScoreDefensive(game_id="0022400001")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_id = "0022400000"  # type: ignore[misc]


class TestBoxScoreDefensiveResponse:
    """Tests for BoxScoreDefensiveResponse model."""

    def test_parse_nested_json_response(self):
        """Response parses NBA's v2 nested JSON format correctly."""
        raw_response = {
            "meta": {
                "version": 1,
                "request": "http://nba.cloud/games/0022400001/boxscoredefensive",
                "time": "2024-10-22T00:00:00.000Z",
            },
            "boxScoreDefensive": {
                "gameId": "0022400001",
                "awayTeamId": 1610612737,
                "homeTeamId": 1610612738,
                "homeTeam": {
                    "teamId": 1610612738,
                    "teamCity": "Boston",
                    "teamName": "Celtics",
                    "teamTricode": "BOS",
                    "teamSlug": "celtics",
                    "players": [
                        {
                            "personId": 1627759,
                            "firstName": "Jaylen",
                            "familyName": "Brown",
                            "nameI": "J. Brown",
                            "playerSlug": "jaylen-brown",
                            "position": "F",
                            "comment": "",
                            "jerseyNum": "7",
                            "statistics": {
                                "matchupMinutes": "13:07",
                                "partialPossessions": 76.3,
                                "switchesOn": 0,
                                "playerPoints": 25,
                                "defensiveRebounds": 3,
                                "matchupAssists": 5,
                                "matchupTurnovers": 1,
                                "steals": 1,
                                "blocks": 0,
                                "matchupFieldGoalsMade": 12,
                                "matchupFieldGoalsAttempted": 22,
                                "matchupFieldGoalPercentage": 0.545,
                                "matchupThreePointersMade": 1,
                                "matchupThreePointersAttempted": 3,
                                "matchupThreePointerPercentage": 0.333,
                            },
                        }
                    ],
                    "statistics": {"minutes": None},
                },
                "awayTeam": {
                    "teamId": 1610612737,
                    "teamCity": "Atlanta",
                    "teamName": "Hawks",
                    "teamTricode": "ATL",
                    "teamSlug": "hawks",
                    "players": [
                        {
                            "personId": 1630700,
                            "firstName": "Dyson",
                            "familyName": "Daniels",
                            "nameI": "D. Daniels",
                            "playerSlug": "dyson-daniels",
                            "position": "G",
                            "comment": "",
                            "jerseyNum": "5",
                            "statistics": {
                                "matchupMinutes": "17:35",
                                "partialPossessions": 82.5,
                                "switchesOn": 0,
                                "playerPoints": 20,
                                "defensiveRebounds": 3,
                                "matchupAssists": 6,
                                "matchupTurnovers": 5,
                                "steals": 6,
                                "blocks": 0,
                                "matchupFieldGoalsMade": 8,
                                "matchupFieldGoalsAttempted": 15,
                                "matchupFieldGoalPercentage": 0.533,
                                "matchupThreePointersMade": 3,
                                "matchupThreePointersAttempted": 8,
                                "matchupThreePointerPercentage": 0.375,
                            },
                        }
                    ],
                    "statistics": {"minutes": None},
                },
            },
        }

        response = BoxScoreDefensiveResponse.model_validate(raw_response)

        # Verify meta
        assert response.meta.version == 1

        # Verify box score data
        data = response.box_score_defensive
        assert data.game_id == "0022400001"
        assert data.home_team_id == 1610612738
        assert data.away_team_id == 1610612737

        # Verify home team
        home = data.home_team
        assert home.team_name == "Celtics"
        assert home.team_tricode == "BOS"
        assert home.statistics.minutes is None

        # Verify home player defensive stats
        assert len(home.players) == 1
        player = home.players[0]
        assert player.first_name == "Jaylen"
        assert player.family_name == "Brown"
        assert player.statistics.partial_possessions == 76.3
        assert player.statistics.matchup_field_goal_percentage == 0.545
        assert player.statistics.steals == 1
        assert player.statistics.blocks == 0

        # Verify away team
        away = data.away_team
        assert away.team_name == "Hawks"

        # Verify away player defensive stats
        away_player = away.players[0]
        assert away_player.first_name == "Dyson"
        assert away_player.statistics.steals == 6
        assert away_player.statistics.partial_possessions == 82.5

    def test_parse_empty_players(self):
        """Response handles teams with no players."""
        raw_response = {
            "meta": {
                "version": 1,
                "request": "http://nba.cloud/games/test/boxscoredefensive",
                "time": "2024-01-01T00:00:00.000Z",
            },
            "boxScoreDefensive": {
                "gameId": "0022400001",
                "awayTeamId": 1,
                "homeTeamId": 2,
                "homeTeam": {
                    "teamId": 2,
                    "teamCity": "Test",
                    "teamName": "Home",
                    "teamTricode": "HOM",
                    "teamSlug": "home",
                    "players": [],
                    "statistics": {"minutes": None},
                },
                "awayTeam": {
                    "teamId": 1,
                    "teamCity": "Test",
                    "teamName": "Away",
                    "teamTricode": "AWY",
                    "teamSlug": "away",
                    "players": [],
                    "statistics": {"minutes": None},
                },
            },
        }

        response = BoxScoreDefensiveResponse.model_validate(raw_response)

        assert response.box_score_defensive.home_team.players == []
        assert response.box_score_defensive.away_team.players == []

    def test_parse_null_teams(self):
        """Response handles null homeTeam/awayTeam for pre-game requests."""
        raw_response = {
            "meta": {
                "version": 1,
                "request": "http://nba.cloud/games/0022400999/boxscoredefensive",
                "time": "2024-01-01T00:00:00.000Z",
            },
            "boxScoreDefensive": {
                "gameId": "0022400999",
                "awayTeamId": 1610612737,
                "homeTeamId": 1610612738,
                "homeTeam": None,
                "awayTeam": None,
            },
        }

        response = BoxScoreDefensiveResponse.model_validate(raw_response)

        assert response.box_score_defensive.game_id == "0022400999"
        assert response.box_score_defensive.home_team is None
        assert response.box_score_defensive.away_team is None
