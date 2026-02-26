"""Tests for PlayerDashboardByTeamPerformance endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByTeamPerformance
from fastbreak.models import PlayerDashboardByTeamPerformanceResponse
from fastbreak.seasons import get_season_from_date


class TestPlayerDashboardByTeamPerformance:
    """Tests for PlayerDashboardByTeamPerformance endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByTeamPerformance uses sensible defaults."""
        endpoint = PlayerDashboardByTeamPerformance(player_id=2544)

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
        """PlayerDashboardByTeamPerformance accepts player_id."""
        endpoint = PlayerDashboardByTeamPerformance(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashboardByTeamPerformance accepts optional filters."""
        endpoint = PlayerDashboardByTeamPerformance(
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
        endpoint = PlayerDashboardByTeamPerformance(player_id=203999)

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
        endpoint = PlayerDashboardByTeamPerformance(
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
        """PlayerDashboardByTeamPerformance has correct API path."""
        endpoint = PlayerDashboardByTeamPerformance(player_id=2544)

        assert endpoint.path == "playerdashboardbyteamperformance"

    def test_response_model_is_correct(self):
        """PlayerDashboardByTeamPerformance uses correct response model."""
        endpoint = PlayerDashboardByTeamPerformance(player_id=2544)

        assert endpoint.response_model is PlayerDashboardByTeamPerformanceResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByTeamPerformance is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByTeamPerformance(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashboardByTeamPerformanceResponse:
    """Tests for PlayerDashboardByTeamPerformanceResponse model."""

    @staticmethod
    def _make_overall_headers() -> list[str]:
        """Return headers for overall result set (63 columns)."""
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
    def _make_performance_headers() -> list[str]:
        """Return headers for performance result sets (65 columns)."""
        return [
            "GROUP_SET",
            "GROUP_VALUE_ORDER",
            "GROUP_VALUE",
            "GROUP_VALUE_2",
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
    def _make_overall_row(group_value: str, gp: int, wins: int, losses: int) -> list:
        """Create a test row for overall stats (63 values)."""
        return [
            "Overall",
            group_value,
            gp,
            wins,
            losses,
            wins / gp if gp > 0 else 0.0,
            35.0,  # MIN
            10.0,
            20.0,
            0.5,
            2.0,
            5.0,
            0.4,
            5.0,
            6.0,
            0.833,  # shooting
            2.0,
            8.0,
            10.0,  # rebounds
            8.0,
            3.0,
            1.5,
            0.5,
            0.5,
            2.0,
            5.0,
            27.0,
            10.0,  # stats
            55.0,
            5,
            2,
            50.0,  # fantasy
            *[1] * 31,  # rank columns + team_count
        ]

    @staticmethod
    def _make_performance_row(
        group_set: str,
        group_value_order: int,
        group_value: str,
        group_value_2: str,
        gp: int,
        wins: int,
        losses: int,
    ) -> list:
        """Create a test row for performance stats (65 values)."""
        return [
            group_set,
            group_value_order,
            group_value,
            group_value_2,
            gp,
            wins,
            losses,
            wins / gp if gp > 0 else 0.0,
            35.0,  # MIN
            10.0,
            20.0,
            0.5,
            2.0,
            5.0,
            0.4,
            5.0,
            6.0,
            0.833,  # shooting
            2.0,
            8.0,
            10.0,  # rebounds
            8.0,
            3.0,
            1.5,
            0.5,
            0.5,
            2.0,
            5.0,
            27.0,
            10.0,  # stats
            55.0,
            5,
            2,
            50.0,  # fantasy
            *[1] * 31,  # rank columns + team_count
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        overall_headers = self._make_overall_headers()
        performance_headers = self._make_performance_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": overall_headers,
                    "rowSet": [self._make_overall_row("2024-25", 8, 5, 3)],
                },
                {
                    "name": "ScoreDifferentialPlayerDashboard",
                    "headers": performance_headers,
                    "rowSet": [
                        self._make_performance_row(
                            "Score Differential", 0, "W", "All", 5, 5, 0
                        ),
                        self._make_performance_row(
                            "Score Differential", 1, "L", "All", 3, 0, 3
                        ),
                    ],
                },
                {
                    "name": "PointsScoredPlayerDashboard",
                    "headers": performance_headers,
                    "rowSet": [
                        self._make_performance_row(
                            "Points Scored", 0, "W", "All", 5, 5, 0
                        ),
                    ],
                },
                {
                    "name": "PontsAgainstPlayerDashboard",  # Note: API typo
                    "headers": performance_headers,
                    "rowSet": [
                        self._make_performance_row(
                            "Points Against", 0, "W", "All", 5, 5, 0
                        ),
                    ],
                },
            ]
        }

        response = PlayerDashboardByTeamPerformanceResponse.model_validate(raw_response)

        # Check overall
        assert response.overall is not None
        assert response.overall.group_value == "2024-25"
        assert response.overall.gp == 8
        assert response.overall.w == 5
        assert response.overall.losses == 3

        # Check score differential
        assert len(response.by_score_differential) == 2
        assert response.by_score_differential[0].group_value == "W"
        assert response.by_score_differential[0].group_value_2 == "All"
        assert response.by_score_differential[0].gp == 5
        assert response.by_score_differential[1].group_value == "L"
        assert response.by_score_differential[1].gp == 3

        # Check points scored
        assert len(response.by_points_scored) == 1
        assert response.by_points_scored[0].group_set == "Points Scored"

        # Check points against (note: using API's typo in result set name)
        assert len(response.by_points_against) == 1
        assert response.by_points_against[0].group_set == "Points Against"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        overall_headers = self._make_overall_headers()
        performance_headers = self._make_performance_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": overall_headers,
                    "rowSet": [],
                },
                {
                    "name": "ScoreDifferentialPlayerDashboard",
                    "headers": performance_headers,
                    "rowSet": [],
                },
                {
                    "name": "PointsScoredPlayerDashboard",
                    "headers": performance_headers,
                    "rowSet": [],
                },
                {
                    "name": "PontsAgainstPlayerDashboard",
                    "headers": performance_headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashboardByTeamPerformanceResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.by_score_differential == []
        assert response.by_points_scored == []
        assert response.by_points_against == []
