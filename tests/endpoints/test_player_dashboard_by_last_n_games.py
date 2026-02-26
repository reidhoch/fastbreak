"""Tests for PlayerDashboardByLastNGames endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByLastNGames
from fastbreak.models import PlayerDashboardByLastNGamesResponse
from fastbreak.seasons import get_season_from_date


class TestPlayerDashboardByLastNGames:
    """Tests for PlayerDashboardByLastNGames endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByLastNGames uses sensible defaults."""
        endpoint = PlayerDashboardByLastNGames(player_id=2544)

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        # Always-sent params have default 0
        assert endpoint.po_round == 0
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.period == 0
        assert endpoint.last_n_games == 0
        assert endpoint.ist_round is None

    def test_init_with_player_id(self):
        """PlayerDashboardByLastNGames accepts player_id."""
        endpoint = PlayerDashboardByLastNGames(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashboardByLastNGames accepts optional filters."""
        endpoint = PlayerDashboardByLastNGames(
            player_id=203999,
            season="2023-24",
            last_n_games=10,
            outcome="W",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.last_n_games == 10
        assert endpoint.outcome == "W"

    def test_params_with_required_only(self):
        """params() returns required and always-sent parameters."""
        endpoint = PlayerDashboardByLastNGames(player_id=203999)

        params = endpoint.params()

        assert params == {
            "PlayerID": "203999",
            "LeagueID": "00",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "PORound": "0",
            "Month": "0",
            "OpponentTeamID": "0",
            "Period": "0",
            "LastNGames": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerDashboardByLastNGames(
            player_id=203999,
            last_n_games=10,
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["LastNGames"] == "10"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_path_is_correct(self):
        """PlayerDashboardByLastNGames has correct API path."""
        endpoint = PlayerDashboardByLastNGames(player_id=2544)

        assert endpoint.path == "playerdashboardbylastngames"

    def test_response_model_is_correct(self):
        """PlayerDashboardByLastNGames uses correct response model."""
        endpoint = PlayerDashboardByLastNGames(player_id=2544)

        assert endpoint.response_model is PlayerDashboardByLastNGamesResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByLastNGames is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByLastNGames(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashboardByLastNGamesResponse:
    """Tests for PlayerDashboardByLastNGamesResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return the 63 headers for split stats."""
        return [
            "GROUP_SET",
            "GROUP_VALUE",
            "GP",
            "W",
            "L",
            "W_PCT",
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
            "NBA_FANTASY_PTS",
            "DD2",
            "TD3",
            "WNBA_FANTASY_PTS",
            "GP_RANK",
            "W_RANK",
            "L_RANK",
            "W_PCT_RANK",
            "MIN_RANK",
            "FGM_RANK",
            "FGA_RANK",
            "FG_PCT_RANK",
            "FG3M_RANK",
            "FG3A_RANK",
            "FG3_PCT_RANK",
            "FTM_RANK",
            "FTA_RANK",
            "FT_PCT_RANK",
            "OREB_RANK",
            "DREB_RANK",
            "REB_RANK",
            "AST_RANK",
            "TOV_RANK",
            "STL_RANK",
            "BLK_RANK",
            "BLKA_RANK",
            "PF_RANK",
            "PFD_RANK",
            "PTS_RANK",
            "PLUS_MINUS_RANK",
            "NBA_FANTASY_PTS_RANK",
            "DD2_RANK",
            "TD3_RANK",
            "WNBA_FANTASY_PTS_RANK",
            "TEAM_COUNT",
        ]

    @staticmethod
    def _make_row(group_set: str, group_value: str, pts: float) -> list:
        """Create a test row with specified values."""
        return [
            group_set,
            group_value,
            10,
            6,
            4,
            0.6,
            35.5,
            11.0,
            19.5,
            0.564,
            2.0,
            4.5,
            0.444,
            5.5,
            7.0,
            0.786,
            2.5,
            9.0,
            11.5,
            9.5,
            3.5,
            2.0,
            0.5,
            1.0,
            2.0,
            6.5,
            pts,
            10.0,
            60.0,
            8,
            5,
            55.0,
            *[1] * 31,
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Overall", "2024-25", 29.5)],
                },
                {
                    "name": "Last5PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 5 Games", "2024-25", 27.6)],
                },
                {
                    "name": "Last10PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 10 Games", "2024-25", 28.5)],
                },
                {
                    "name": "Last15PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 15 Games", "2024-25", 29.0)],
                },
                {
                    "name": "Last20PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 20 Games", "2024-25", 29.2)],
                },
                {
                    "name": "GameNumberPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Game Number", "Games 1-10", 26.0),
                        self._make_row("Game Number", "Games 11-20", 28.0),
                        self._make_row("Game Number", "Games 71-80", 32.0),
                    ],
                },
            ]
        }

        response = PlayerDashboardByLastNGamesResponse.model_validate(raw_response)

        # Check overall
        assert response.overall is not None
        assert response.overall.pts == 29.5

        # Check rolling averages
        assert response.last_5 is not None
        assert response.last_5.group_set == "Last 5 Games"
        assert response.last_5.pts == 27.6

        assert response.last_10 is not None
        assert response.last_10.pts == 28.5

        assert response.last_15 is not None
        assert response.last_15.pts == 29.0

        assert response.last_20 is not None
        assert response.last_20.pts == 29.2

        # Check game number ranges
        assert len(response.by_game_number) == 3
        assert response.by_game_number[0].group_value == "Games 1-10"
        assert response.by_game_number[0].pts == 26.0
        assert response.by_game_number[2].group_value == "Games 71-80"
        assert response.by_game_number[2].pts == 32.0

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {"name": "OverallPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "Last5PlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "Last10PlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "Last15PlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "Last20PlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "GameNumberPlayerDashboard", "headers": headers, "rowSet": []},
            ]
        }

        response = PlayerDashboardByLastNGamesResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.last_5 is None
        assert response.last_10 is None
        assert response.last_15 is None
        assert response.last_20 is None
        assert response.by_game_number == []

    def test_trend_analysis(self):
        """Response enables trend analysis across time windows."""
        headers = self._make_headers()

        # Simulate improving performance trend
        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Overall", "2024-25", 25.0)],
                },
                {
                    "name": "Last5PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 5 Games", "2024-25", 32.0)],
                },
                {
                    "name": "Last10PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 10 Games", "2024-25", 28.0)],
                },
                {
                    "name": "Last15PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 15 Games", "2024-25", 26.0)],
                },
                {
                    "name": "Last20PlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Last 20 Games", "2024-25", 25.5)],
                },
                {"name": "GameNumberPlayerDashboard", "headers": headers, "rowSet": []},
            ]
        }

        response = PlayerDashboardByLastNGamesResponse.model_validate(raw_response)

        # Player is on a hot streak (last 5 > last 10 > last 15 > last 20 > overall)
        assert response.last_5.pts > response.last_10.pts  # type: ignore[union-attr]
        assert response.last_10.pts > response.last_15.pts  # type: ignore[union-attr]
        assert response.last_15.pts > response.last_20.pts  # type: ignore[union-attr]
        assert response.last_20.pts > response.overall.pts  # type: ignore[union-attr]
