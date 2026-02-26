"""Tests for PlayerDashboardByClutch endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByClutch
from fastbreak.models import PlayerDashboardByClutchResponse
from fastbreak.seasons import get_season_from_date


class TestPlayerDashboardByClutch:
    """Tests for PlayerDashboardByClutch endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByClutch uses sensible defaults."""
        endpoint = PlayerDashboardByClutch(player_id=2544)

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
        """PlayerDashboardByClutch accepts player_id."""
        endpoint = PlayerDashboardByClutch(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashboardByClutch accepts optional filters."""
        endpoint = PlayerDashboardByClutch(
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
        endpoint = PlayerDashboardByClutch(player_id=203999)

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
        endpoint = PlayerDashboardByClutch(
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
        """PlayerDashboardByClutch has correct API path."""
        endpoint = PlayerDashboardByClutch(player_id=2544)

        assert endpoint.path == "playerdashboardbyclutch"

    def test_response_model_is_correct(self):
        """PlayerDashboardByClutch uses PlayerDashboardByClutchResponse model."""
        endpoint = PlayerDashboardByClutch(player_id=2544)

        assert endpoint.response_model is PlayerDashboardByClutchResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByClutch is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByClutch(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashboardByClutchResponse:
    """Tests for PlayerDashboardByClutchResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        # Minimal headers for testing - actual API has 63 columns
        headers = [
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

        # Sample row data (63 values to match 63 headers)
        overall_row = [
            "Overall",
            "2024-25",
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
            29.5,
            10.0,
            60.0,
            8,
            5,
            55.0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,  # TEAM_COUNT
        ]

        clutch_row = [
            "Last 5 MIN <= 5 PTS",
            "2024-25",
            5,
            3,
            2,
            0.6,
            5.0,
            2.0,
            3.5,
            0.571,
            0.5,
            1.0,
            0.5,
            1.5,
            2.0,
            0.75,
            0.5,
            1.5,
            2.0,
            2.0,
            0.5,
            0.5,
            0.0,
            0.5,
            0.5,
            2.0,
            6.0,
            4.0,
            10.0,
            5,
            5,
            9.0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,  # TEAM_COUNT
        ]

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [overall_row],
                },
                {
                    "name": "Last5Min5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [clutch_row],
                },
                {
                    "name": "Last3Min5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last1Min5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last30Sec3PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last10Sec3PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last5MinPlusMinus5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last3MinPlusMinus5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last1MinPlusMinus5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last30Sec3Point2PlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last10Sec3Point2PlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashboardByClutchResponse.model_validate(raw_response)

        # Check overall stats
        assert response.overall is not None
        assert response.overall.group_set == "Overall"
        assert response.overall.group_value == "2024-25"
        assert response.overall.gp == 10
        assert response.overall.w == 6
        assert response.overall.losses == 4
        assert response.overall.pts == 29.5
        assert response.overall.reb == 11.5
        assert response.overall.ast == 9.5
        assert response.overall.plus_minus == 10.0
        assert response.overall.dd2 == 8
        assert response.overall.td3 == 5

        # Check clutch stats
        assert response.last_5_min_lte_5_pts is not None
        assert response.last_5_min_lte_5_pts.group_set == "Last 5 MIN <= 5 PTS"
        assert response.last_5_min_lte_5_pts.gp == 5
        assert response.last_5_min_lte_5_pts.pts == 6.0
        assert response.last_5_min_lte_5_pts.plus_minus == 4.0

        # Check empty result sets return None
        assert response.last_3_min_lte_5_pts is None
        assert response.last_1_min_lte_5_pts is None
        assert response.last_30_sec_lte_3_pts is None

    def test_parse_all_empty_result_sets(self):
        """Response handles all empty result sets."""
        headers = ["GROUP_SET", "GROUP_VALUE"]

        raw_response = {
            "resultSets": [
                {"name": "OverallPlayerDashboard", "headers": headers, "rowSet": []},
                {
                    "name": "Last5Min5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last3Min5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last1Min5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last30Sec3PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last10Sec3PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last5MinPlusMinus5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last3MinPlusMinus5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last1MinPlusMinus5PointPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last30Sec3Point2PlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "Last10Sec3Point2PlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashboardByClutchResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.last_5_min_lte_5_pts is None
        assert response.last_3_min_lte_5_pts is None
        assert response.last_1_min_lte_5_pts is None
        assert response.last_30_sec_lte_3_pts is None
        assert response.last_10_sec_lte_3_pts is None
        assert response.last_5_min_pm_5_pts is None
        assert response.last_3_min_pm_5_pts is None
        assert response.last_1_min_pm_5_pts is None
        assert response.last_30_sec_pm_3_pts is None
        assert response.last_10_sec_pm_3_pts is None
