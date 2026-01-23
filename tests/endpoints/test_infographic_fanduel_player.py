"""Tests for InfographicFanDuelPlayer endpoint."""

from fastbreak.endpoints import InfographicFanDuelPlayer
from fastbreak.models import InfographicFanDuelPlayerResponse


class TestInfographicFanDuelPlayer:
    """Tests for InfographicFanDuelPlayer endpoint."""

    def test_init_with_game_id(self):
        """InfographicFanDuelPlayer requires game_id."""
        endpoint = InfographicFanDuelPlayer(game_id="0022500571")

        assert endpoint.game_id == "0022500571"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = InfographicFanDuelPlayer(game_id="0022500571")

        params = endpoint.params()

        assert params == {"GameID": "0022500571"}

    def test_path_is_correct(self):
        """InfographicFanDuelPlayer has correct API path."""
        endpoint = InfographicFanDuelPlayer(game_id="0022500571")

        assert endpoint.path == "infographicfanduelplayer"

    def test_response_model_is_correct(self):
        """InfographicFanDuelPlayer uses InfographicFanDuelPlayerResponse model."""
        endpoint = InfographicFanDuelPlayer(game_id="0022500571")

        assert endpoint.response_model is InfographicFanDuelPlayerResponse

    def test_endpoint_is_frozen(self):
        """InfographicFanDuelPlayer is immutable (frozen dataclass)."""
        endpoint = InfographicFanDuelPlayer(game_id="0022500571")

        try:
            endpoint.game_id = "0022500000"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestInfographicFanDuelPlayerResponse:
    """Tests for InfographicFanDuelPlayerResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "FanDuelPlayer",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "JERSEY_NUM",
                        "PLAYER_POSITION",
                        "LOCATION",
                        "FAN_DUEL_PTS",
                        "NBA_FANTASY_PTS",
                        "USG_PCT",
                        "MIN",
                        "FGM",
                        "FGA",
                        "FG_PCT",
                        "FG3M",
                        "FG3A",
                        "FG3_PCT",
                        "FTM",
                        "FTA",
                        "FT_PCT",
                        "OREB",
                        "DREB",
                        "REB",
                        "AST",
                        "TOV",
                        "STL",
                        "BLK",
                        "BLKA",
                        "PF",
                        "PFD",
                        "PTS",
                        "PLUS_MINUS",
                    ],
                    "rowSet": [
                        [
                            1630567,
                            "Scottie Barnes",
                            1610612761,
                            "Toronto Raptors",
                            "TOR",
                            "4",
                            "F-G",
                            "Road",
                            56.9,
                            59.9,
                            0.245,
                            38.4,
                            10,
                            16,
                            0.625,
                            1,
                            3,
                            0.333,
                            5,
                            9,
                            0.556,
                            0,
                            7,
                            7,
                            13,
                            3,
                            2,
                            1,
                            1,
                            2,
                            7,
                            26,
                            14,
                        ],
                        [
                            1627783,
                            "Pascal Siakam",
                            1610612754,
                            "Indiana Pacers",
                            "IND",
                            "43",
                            "F",
                            "Home",
                            40.0,
                            40.0,
                            0.311,
                            35.3,
                            10,
                            23,
                            0.435,
                            4,
                            11,
                            0.364,
                            2,
                            3,
                            0.667,
                            4,
                            6,
                            10,
                            4,
                            4,
                            0,
                            0,
                            0,
                            5,
                            3,
                            26,
                            -4,
                        ],
                    ],
                },
            ]
        }

        response = InfographicFanDuelPlayerResponse.model_validate(raw_response)

        assert len(response.players) == 2

        scottie = response.players[0]
        assert scottie.player_name == "Scottie Barnes"
        assert scottie.team_abbreviation == "TOR"
        assert scottie.fan_duel_pts == 56.9
        assert scottie.nba_fantasy_pts == 59.9
        assert scottie.pts == 26
        assert scottie.ast == 13
        assert scottie.plus_minus == 14

        pascal = response.players[1]
        assert pascal.player_name == "Pascal Siakam"
        assert pascal.team_abbreviation == "IND"
        assert pascal.fan_duel_pts == 40.0

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "FanDuelPlayer",
                    "headers": ["PLAYER_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = InfographicFanDuelPlayerResponse.model_validate(raw_response)

        assert response.players == []
