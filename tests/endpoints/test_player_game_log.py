"""Tests for PlayerGameLog endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerGameLog
from fastbreak.models import PlayerGameLogResponse
from fastbreak.utils import get_season_from_date


class TestPlayerGameLog:
    """Tests for PlayerGameLog endpoint."""

    def test_init_with_defaults(self):
        """PlayerGameLog uses sensible defaults."""
        endpoint = PlayerGameLog(player_id="2544")

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"

    def test_init_with_player_id(self):
        """PlayerGameLog accepts player_id."""
        endpoint = PlayerGameLog(player_id="2544")

        assert endpoint.player_id == 2544

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerGameLog(player_id="2544", season="2023-24")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Regular Season"

    def test_path_is_correct(self):
        """PlayerGameLog has correct API path."""
        endpoint = PlayerGameLog(player_id="2544")

        assert endpoint.path == "playergamelog"

    def test_response_model_is_correct(self):
        """PlayerGameLog uses correct response model."""
        endpoint = PlayerGameLog(player_id="2544")

        assert endpoint.response_model is PlayerGameLogResponse

    def test_endpoint_is_frozen(self):
        """PlayerGameLog is immutable (frozen dataclass)."""
        endpoint = PlayerGameLog(player_id="2544")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerGameLogResponse:
    """Tests for PlayerGameLogResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for player game log (27 columns)."""
        return [
            "SEASON_ID",
            "Player_ID",
            "Game_ID",
            "GAME_DATE",
            "MATCHUP",
            "WL",
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
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
            "PLUS_MINUS",
            "VIDEO_AVAILABLE",
        ]

    @staticmethod
    def _make_row(
        player_id: int,
        game_id: str,
        game_date: str,
        matchup: str,
        wl: str,
        pts: int,
        reb: int,
        ast: int,
    ) -> list:
        """Create a test row for player game log (27 values)."""
        return [
            "22024",  # SEASON_ID
            player_id,
            game_id,
            game_date,
            matchup,
            wl,
            35,  # MIN
            10,  # FGM
            20,  # FGA
            0.5,  # FG_PCT
            3,  # FG3M
            8,  # FG3A
            0.375,  # FG3_PCT
            5,  # FTM
            6,  # FTA
            0.833,  # FT_PCT
            2,  # OREB
            reb - 2,  # DREB
            reb,
            ast,
            2,  # STL
            1,  # BLK
            3,  # TOV
            2,  # PF
            pts,
            10,  # PLUS_MINUS
            1,  # VIDEO_AVAILABLE
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerGameLog",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            2544,
                            "0022401185",
                            "Apr 11, 2025",
                            "LAL vs. HOU",
                            "W",
                            28,
                            8,
                            10,
                        ),
                        self._make_row(
                            2544,
                            "0022401170",
                            "Apr 09, 2025",
                            "LAL @ DEN",
                            "L",
                            22,
                            6,
                            8,
                        ),
                    ],
                }
            ]
        }

        response = PlayerGameLogResponse.model_validate(raw_response)

        assert len(response.games) == 2

        # Check first game
        game1 = response.games[0]
        assert game1.player_id == 2544
        assert game1.game_id == "0022401185"
        assert game1.game_date == "Apr 11, 2025"
        assert game1.matchup == "LAL vs. HOU"
        assert game1.wl == "W"
        assert game1.pts == 28
        assert game1.reb == 8
        assert game1.ast == 10

        # Check second game
        game2 = response.games[1]
        assert game2.matchup == "LAL @ DEN"
        assert game2.wl == "L"
        assert game2.pts == 22

    def test_parse_empty_result_set(self):
        """Response handles empty result set."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [{"name": "PlayerGameLog", "headers": headers, "rowSet": []}]
        }

        response = PlayerGameLogResponse.model_validate(raw_response)

        assert response.games == []
