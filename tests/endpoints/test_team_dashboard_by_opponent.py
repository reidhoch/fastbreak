"""Tests for TeamDashboardByOpponent endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import TeamDashboardByOpponent
from fastbreak.models import TeamDashboardByOpponentResponse


class TestTeamDashboardByOpponent:
    """Tests for TeamDashboardByOpponent endpoint."""

    def test_init_with_defaults(self):
        """TeamDashboardByOpponent uses sensible defaults."""
        endpoint = TeamDashboardByOpponent(team_id="1610612747")

        assert endpoint.team_id == 1610612747
        assert endpoint.league_id == "00"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_params_returns_dashboard_parameters(self):
        """params() returns the standard dashboard query parameters."""
        endpoint = TeamDashboardByOpponent(team_id="1610612747")

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["OpponentTeamID"] == "0"

    def test_path_is_correct(self):
        """TeamDashboardByOpponent has correct API path."""
        endpoint = TeamDashboardByOpponent(team_id="1610612747")

        assert endpoint.path == "teamdashboardbyopponent"

    def test_response_model_is_correct(self):
        """TeamDashboardByOpponent uses correct response model."""
        endpoint = TeamDashboardByOpponent(team_id="1610612747")

        assert endpoint.response_model is TeamDashboardByOpponentResponse

    def test_endpoint_is_frozen(self):
        """TeamDashboardByOpponent is immutable (frozen)."""
        endpoint = TeamDashboardByOpponent(team_id="1610612747")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = "1610612738"  # type: ignore[misc]


class TestTeamDashboardByOpponentResponse:
    """Tests for TeamDashboardByOpponentResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return the 54-column header list for the team opponent dashboard.

        2 identifiers + 26 stats + 26 ranks.  Team rows have no
        fantasy/DD2/TD3/WNBA columns and no TEAM_COUNT.
        """
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
        ]

    @staticmethod
    def _make_row(group_set: str, group_value: str) -> list:
        """Build a row: 2 identifiers + 26 stats + 26 ranks (54 values)."""
        identifiers: list = [group_set, group_value]
        stats: list = [
            82,
            50,
            32,
            0.61,
            48.1,
            40.9,
            85.5,
            0.479,
            13.3,
            36.4,
            0.366,
            18.2,
            23.2,
            0.785,
            9.7,
            32.8,
            42.4,
            26.0,
            14.0,
            7.7,
            4.5,
            4.2,
            17.3,
            19.2,
            113.4,
            1.2,
        ]
        ranks: list = [1] * 26
        return identifiers + stats + ranks

    def _raw_response(self) -> dict:
        headers = self._make_headers()
        return {
            "resultSets": [
                {
                    "name": "OverallTeamDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Overall", "2024-25")],
                },
                {
                    "name": "ConferenceTeamDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("vs. Conference", "East"),
                        self._make_row("vs. Conference", "West"),
                    ],
                },
                {
                    "name": "DivisionTeamDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("vs. Division", "Atlantic")],
                },
                {
                    "name": "OpponentTeamDashboard",
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
        response = TeamDashboardByOpponentResponse.model_validate(self._raw_response())

        assert response.overall is not None
        assert response.overall.group_set == "Overall"
        assert response.overall.pts == 113.4

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
                {"name": "OverallTeamDashboard", "headers": headers, "rowSet": []},
                {"name": "ConferenceTeamDashboard", "headers": headers, "rowSet": []},
                {"name": "DivisionTeamDashboard", "headers": headers, "rowSet": []},
                {"name": "OpponentTeamDashboard", "headers": headers, "rowSet": []},
            ]
        }

        response = TeamDashboardByOpponentResponse.model_validate(raw)

        assert response.overall is None
        assert response.by_conference == []
        assert response.by_division == []
        assert response.by_opponent == []
