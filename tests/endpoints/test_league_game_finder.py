"""Tests for LeagueGameFinder endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueGameFinder
from fastbreak.models import LeagueGameFinderResponse


class TestLeagueGameFinder:
    """Tests for LeagueGameFinder endpoint."""

    def test_init_with_defaults(self):
        """LeagueGameFinder uses sensible defaults."""
        endpoint = LeagueGameFinder()

        assert endpoint.player_or_team == "T"
        assert endpoint.season is None
        assert endpoint.team_id is None

    def test_init_with_team_filter(self):
        """LeagueGameFinder accepts team_id filter."""
        endpoint = LeagueGameFinder(team_id="1610612747", season="2024-25")

        assert endpoint.team_id == "1610612747"
        assert endpoint.season == "2024-25"

    def test_init_with_player_mode(self):
        """LeagueGameFinder accepts player mode."""
        endpoint = LeagueGameFinder(player_or_team="P", player_id="201566")

        assert endpoint.player_or_team == "P"
        assert endpoint.player_id == "201566"

    def test_init_with_stat_filters(self):
        """LeagueGameFinder accepts stat threshold filters."""
        endpoint = LeagueGameFinder(gt_pts="30", gt_ast="10")

        assert endpoint.gt_pts == "30"
        assert endpoint.gt_ast == "10"

    def test_params_with_required_only(self):
        """params() returns only required parameters when no filters set."""
        endpoint = LeagueGameFinder()

        params = endpoint.params()

        assert params == {"PlayerOrTeam": "T"}

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = LeagueGameFinder(
            player_or_team="T",
            team_id="1610612747",
            season="2024-25",
            outcome="W",
        )

        params = endpoint.params()

        assert params == {
            "PlayerOrTeam": "T",
            "TeamID": "1610612747",
            "Season": "2024-25",
            "Outcome": "W",
        }

    def test_params_with_stat_thresholds(self):
        """params() includes stat threshold filters."""
        endpoint = LeagueGameFinder(gt_pts="40", gt_reb="15")

        params = endpoint.params()

        assert params["GtPts"] == "40"
        assert params["GtReb"] == "15"

    def test_path_is_correct(self):
        """LeagueGameFinder has correct API path."""
        endpoint = LeagueGameFinder()

        assert endpoint.path == "leaguegamefinder"

    def test_response_model_is_correct(self):
        """LeagueGameFinder uses LeagueGameFinderResponse model."""
        endpoint = LeagueGameFinder()

        assert endpoint.response_model is LeagueGameFinderResponse

    def test_endpoint_is_frozen(self):
        """LeagueGameFinder is immutable (frozen dataclass)."""
        endpoint = LeagueGameFinder()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestLeagueGameFinderResponse:
    """Tests for LeagueGameFinderResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueGameFinderResults",
                    "headers": [
                        "SEASON_ID",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "GAME_ID",
                        "GAME_DATE",
                        "MATCHUP",
                        "WL",
                        "MIN",
                        "PTS",
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
                        "PLUS_MINUS",
                    ],
                    "rowSet": [
                        [
                            "22024",
                            1610612747,
                            "LAL",
                            "Los Angeles Lakers",
                            "0022400001",
                            "2024-10-22",
                            "LAL vs. MIN",
                            "W",
                            240,
                            110,
                            42,
                            88,
                            0.477,
                            12,
                            35,
                            0.343,
                            14,
                            18,
                            0.778,
                            10,
                            35,
                            45,
                            28,
                            8,
                            5,
                            12,
                            20,
                            7.0,
                        ],
                        [
                            "22024",
                            1610612747,
                            "LAL",
                            "Los Angeles Lakers",
                            "0022400015",
                            "2024-10-25",
                            "LAL @ PHX",
                            "L",
                            240,
                            105,
                            38,
                            85,
                            0.447,
                            10,
                            30,
                            0.333,
                            19,
                            22,
                            0.864,
                            8,
                            32,
                            40,
                            25,
                            6,
                            3,
                            15,
                            22,
                            -5.0,
                        ],
                    ],
                },
            ]
        }

        response = LeagueGameFinderResponse.model_validate(raw_response)

        assert len(response.games) == 2

        game1 = response.games[0]
        assert game1.team_abbreviation == "LAL"
        assert game1.team_name == "Los Angeles Lakers"
        assert game1.matchup == "LAL vs. MIN"
        assert game1.wl == "W"
        assert game1.pts == 110
        assert game1.reb == 45
        assert game1.ast == 28
        assert game1.plus_minus == 7.0

        game2 = response.games[1]
        assert game2.wl == "L"
        assert game2.plus_minus == -5.0

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueGameFinderResults",
                    "headers": ["SEASON_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = LeagueGameFinderResponse.model_validate(raw_response)

        assert response.games == []

    def test_handles_null_values(self):
        """Response handles null values for optional fields."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueGameFinderResults",
                    "headers": [
                        "SEASON_ID",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "GAME_ID",
                        "GAME_DATE",
                        "MATCHUP",
                        "WL",
                        "MIN",
                        "PTS",
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
                        "PLUS_MINUS",
                    ],
                    "rowSet": [
                        [
                            "22024",
                            1610612747,
                            "LAL",
                            "Los Angeles Lakers",
                            "0022400001",
                            "2024-10-22",
                            "LAL vs. MIN",
                            None,  # WL can be null for in-progress games
                            0,
                            0,
                            0,
                            0,
                            None,  # FG_PCT null when no attempts
                            0,
                            0,
                            None,
                            0,
                            0,
                            None,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            None,  # PLUS_MINUS null
                        ],
                    ],
                },
            ]
        }

        response = LeagueGameFinderResponse.model_validate(raw_response)

        game = response.games[0]
        assert game.wl is None
        assert game.fg_pct is None
        assert game.plus_minus is None
