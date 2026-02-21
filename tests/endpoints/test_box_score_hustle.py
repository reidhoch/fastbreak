"""Tests for BoxScoreHustle endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import BoxScoreHustle
from fastbreak.models import BoxScoreHustleResponse


class TestBoxScoreHustle:
    """Tests for BoxScoreHustle endpoint."""

    def test_init_with_game_id(self):
        """BoxScoreHustle requires game_id."""
        endpoint = BoxScoreHustle(game_id="0022400001")

        assert endpoint.game_id == "0022400001"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = BoxScoreHustle(game_id="0022400001")

        params = endpoint.params()

        assert params == {"GameID": "0022400001"}

    def test_path_is_correct(self):
        """BoxScoreHustle has correct API path."""
        endpoint = BoxScoreHustle(game_id="0022400001")

        assert endpoint.path == "boxscorehustlev2"

    def test_response_model_is_correct(self):
        """BoxScoreHustle uses BoxScoreHustleResponse model."""
        endpoint = BoxScoreHustle(game_id="0022400001")

        assert endpoint.response_model is BoxScoreHustleResponse

    def test_endpoint_is_frozen(self):
        """BoxScoreHustle is immutable (frozen dataclass)."""
        endpoint = BoxScoreHustle(game_id="0022400001")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_id = "0022400000"  # type: ignore[misc]


class TestBoxScoreHustleResponse:
    """Tests for BoxScoreHustleResponse model."""

    def test_parse_nested_json_response(self):
        """Response parses NBA's v2 nested JSON format correctly."""
        raw_response = {
            "meta": {
                "version": 1,
                "request": "http://nba.cloud/games/0022400001/boxscorehustle",
                "time": "2024-10-22T00:00:00.000Z",
            },
            "boxScoreHustle": {
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
                                "minutes": "35:56",
                                "points": 37,
                                "contestedShots": 6,
                                "contestedShots2pt": 5,
                                "contestedShots3pt": 1,
                                "deflections": 6,
                                "chargesDrawn": 1,
                                "screenAssists": 0,
                                "screenAssistPoints": 0,
                                "looseBallsRecoveredOffensive": 0,
                                "looseBallsRecoveredDefensive": 1,
                                "looseBallsRecoveredTotal": 1,
                                "offensiveBoxOuts": 0,
                                "defensiveBoxOuts": 0,
                                "boxOutPlayerTeamRebounds": 0,
                                "boxOutPlayerRebounds": 0,
                                "boxOuts": 0,
                            },
                        }
                    ],
                    "statistics": {
                        "minutes": "240:00",
                        "points": 116,
                        "contestedShots": 40,
                        "contestedShots2pt": 28,
                        "contestedShots3pt": 12,
                        "deflections": 17,
                        "chargesDrawn": 1,
                        "screenAssists": 8,
                        "screenAssistPoints": 19,
                        "looseBallsRecoveredOffensive": 1,
                        "looseBallsRecoveredDefensive": 1,
                        "looseBallsRecoveredTotal": 2,
                        "offensiveBoxOuts": 1,
                        "defensiveBoxOuts": 5,
                        "boxOutPlayerTeamRebounds": 6,
                        "boxOutPlayerRebounds": 3,
                        "boxOuts": 6,
                    },
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
                                "minutes": "40:57",
                                "points": 28,
                                "contestedShots": 3,
                                "contestedShots2pt": 2,
                                "contestedShots3pt": 1,
                                "deflections": 10,
                                "chargesDrawn": 0,
                                "screenAssists": 1,
                                "screenAssistPoints": 2,
                                "looseBallsRecoveredOffensive": 0,
                                "looseBallsRecoveredDefensive": 0,
                                "looseBallsRecoveredTotal": 0,
                                "offensiveBoxOuts": 0,
                                "defensiveBoxOuts": 0,
                                "boxOutPlayerTeamRebounds": 0,
                                "boxOutPlayerRebounds": 0,
                                "boxOuts": 0,
                            },
                        }
                    ],
                    "statistics": {
                        "minutes": "240:00",
                        "points": 117,
                        "contestedShots": 25,
                        "contestedShots2pt": 11,
                        "contestedShots3pt": 14,
                        "deflections": 24,
                        "chargesDrawn": 0,
                        "screenAssists": 7,
                        "screenAssistPoints": 15,
                        "looseBallsRecoveredOffensive": 3,
                        "looseBallsRecoveredDefensive": 1,
                        "looseBallsRecoveredTotal": 4,
                        "offensiveBoxOuts": 2,
                        "defensiveBoxOuts": 4,
                        "boxOutPlayerTeamRebounds": 6,
                        "boxOutPlayerRebounds": 2,
                        "boxOuts": 6,
                    },
                },
            },
        }

        response = BoxScoreHustleResponse.model_validate(raw_response)

        # Verify meta
        assert response.meta.version == 1

        # Verify box score data
        data = response.box_score_hustle
        assert data.game_id == "0022400001"
        assert data.home_team_id == 1610612738
        assert data.away_team_id == 1610612737

        # Verify home team
        home = data.home_team
        assert home.team_name == "Celtics"
        assert home.team_tricode == "BOS"
        assert home.statistics.deflections == 17
        assert home.statistics.contested_shots == 40

        # Verify home player
        assert len(home.players) == 1
        player = home.players[0]
        assert player.first_name == "Jaylen"
        assert player.family_name == "Brown"
        assert player.name_i == "J. Brown"
        assert player.statistics.deflections == 6
        assert player.statistics.charges_drawn == 1

        # Verify away team
        away = data.away_team
        assert away.team_name == "Hawks"
        assert away.statistics.deflections == 24

        # Verify away player
        away_player = away.players[0]
        assert away_player.first_name == "Dyson"
        assert away_player.statistics.deflections == 10

    def test_parse_empty_players(self):
        """Response handles teams with no players."""
        raw_response = {
            "meta": {
                "version": 1,
                "request": "http://nba.cloud/games/test/boxscorehustle",
                "time": "2024-01-01T00:00:00.000Z",
            },
            "boxScoreHustle": {
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
                    "statistics": {
                        "minutes": "0:00",
                        "points": 0,
                        "contestedShots": 0,
                        "contestedShots2pt": 0,
                        "contestedShots3pt": 0,
                        "deflections": 0,
                        "chargesDrawn": 0,
                        "screenAssists": 0,
                        "screenAssistPoints": 0,
                        "looseBallsRecoveredOffensive": 0,
                        "looseBallsRecoveredDefensive": 0,
                        "looseBallsRecoveredTotal": 0,
                        "offensiveBoxOuts": 0,
                        "defensiveBoxOuts": 0,
                        "boxOutPlayerTeamRebounds": 0,
                        "boxOutPlayerRebounds": 0,
                        "boxOuts": 0,
                    },
                },
                "awayTeam": {
                    "teamId": 1,
                    "teamCity": "Test",
                    "teamName": "Away",
                    "teamTricode": "AWY",
                    "teamSlug": "away",
                    "players": [],
                    "statistics": {
                        "minutes": "0:00",
                        "points": 0,
                        "contestedShots": 0,
                        "contestedShots2pt": 0,
                        "contestedShots3pt": 0,
                        "deflections": 0,
                        "chargesDrawn": 0,
                        "screenAssists": 0,
                        "screenAssistPoints": 0,
                        "looseBallsRecoveredOffensive": 0,
                        "looseBallsRecoveredDefensive": 0,
                        "looseBallsRecoveredTotal": 0,
                        "offensiveBoxOuts": 0,
                        "defensiveBoxOuts": 0,
                        "boxOutPlayerTeamRebounds": 0,
                        "boxOutPlayerRebounds": 0,
                        "boxOuts": 0,
                    },
                },
            },
        }

        response = BoxScoreHustleResponse.model_validate(raw_response)

        assert response.box_score_hustle.home_team.players == []
        assert response.box_score_hustle.away_team.players == []
