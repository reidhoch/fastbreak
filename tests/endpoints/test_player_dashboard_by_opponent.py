"""Tests for PlayerDashboardByOpponent endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByOpponent
from fastbreak.models import PlayerDashboardByOpponentResponse


class TestPlayerDashboardByOpponent:
    """Tests for PlayerDashboardByOpponent endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByOpponent uses sensible defaults."""
        endpoint = PlayerDashboardByOpponent(player_id="2544")

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_params_returns_dashboard_parameters(self):
        """params() returns the standard dashboard query parameters."""
        endpoint = PlayerDashboardByOpponent(player_id="2544")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["OpponentTeamID"] == "0"

    def test_path_is_correct(self):
        """PlayerDashboardByOpponent has correct API path."""
        endpoint = PlayerDashboardByOpponent(player_id="2544")

        assert endpoint.path == "playerdashboardbyopponent"

    def test_response_model_is_correct(self):
        """PlayerDashboardByOpponent uses correct response model."""
        endpoint = PlayerDashboardByOpponent(player_id="2544")

        assert endpoint.response_model is PlayerDashboardByOpponentResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByOpponent is immutable (frozen)."""
        endpoint = PlayerDashboardByOpponent(player_id="2544")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.player_id = "203999"  # type: ignore[misc]


class TestPlayerDashboardByOpponentResponse:
    """Tests for PlayerDashboardByOpponentResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return the 62-column header list for the player opponent dashboard."""
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
    def _make_row(group_set: str, group_value: str) -> list:
        """Build a row: 2 identifiers + 30 stats + 30 ranks + TEAM_COUNT (63 values)."""
        identifiers: list = [group_set, group_value]
        stats: list = [
            70,
            44,
            26,
            0.629,
            34.9,
            9.3,
            18.1,
            0.513,
            2.1,
            5.7,
            0.376,
            3.7,
            4.7,
            0.782,
            1.0,
            6.8,
            7.8,
            8.2,
            3.7,
            1.0,
            0.6,
            0.7,
            1.4,
            3.8,
            24.4,
            -0.8,
            47.1,
            32,
            10,
            45.7,
        ]
        ranks: list = [1] * 30
        return identifiers + stats + ranks + [30]

    def _raw_response(self) -> dict:
        headers = self._make_headers()
        return {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Overall", "2024-25")],
                },
                {
                    "name": "ConferencePlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("vs. Conference", "East"),
                        self._make_row("vs. Conference", "West"),
                    ],
                },
                {
                    "name": "DivisionPlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("vs. Division", "Atlantic")],
                },
                {
                    "name": "OpponentPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("vs. Opponent", "Atlanta Hawks"),
                        self._make_row("vs. Opponent", "Boston Celtics"),
                    ],
                },
            ]
        }

    def test_parse_all_result_sets(self):
        """Response parses all four result sets into the right buckets."""
        response = PlayerDashboardByOpponentResponse.model_validate(
            self._raw_response()
        )

        assert response.overall is not None
        assert response.overall.group_set == "Overall"
        assert response.overall.pts == 24.4
        assert response.overall.team_count == 30

        assert len(response.by_conference) == 2
        assert response.by_conference[0].group_value == "East"

        assert len(response.by_division) == 1
        assert response.by_division[0].group_value == "Atlantic"

        assert len(response.by_opponent) == 2
        assert response.by_opponent[0].group_value == "Atlanta Hawks"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets gracefully."""
        headers = self._make_headers()
        raw = {
            "resultSets": [
                {"name": "OverallPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "ConferencePlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "DivisionPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "OpponentPlayerDashboard", "headers": headers, "rowSet": []},
            ]
        }

        response = PlayerDashboardByOpponentResponse.model_validate(raw)

        assert response.overall is None
        assert response.by_conference == []
        assert response.by_division == []
        assert response.by_opponent == []
