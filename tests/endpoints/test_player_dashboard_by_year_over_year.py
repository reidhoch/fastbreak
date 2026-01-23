"""Tests for PlayerDashboardByYearOverYear endpoint."""

from fastbreak.endpoints import PlayerDashboardByYearOverYear
from fastbreak.models import PlayerDashboardByYearOverYearResponse


class TestPlayerDashboardByYearOverYear:
    """Tests for PlayerDashboardByYearOverYear endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByYearOverYear uses sensible defaults."""
        endpoint = PlayerDashboardByYearOverYear()

        assert endpoint.player_id == ""
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.per_mode == "PerGame"

    def test_init_with_player_id(self):
        """PlayerDashboardByYearOverYear accepts player_id."""
        endpoint = PlayerDashboardByYearOverYear(player_id="203999")

        assert endpoint.player_id == "203999"

    def test_params_with_required_only(self):
        """params() returns required parameters."""
        endpoint = PlayerDashboardByYearOverYear(player_id="203999")

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """PlayerDashboardByYearOverYear has correct API path."""
        endpoint = PlayerDashboardByYearOverYear()

        assert endpoint.path == "playerdashboardbyyearoveryear"

    def test_response_model_is_correct(self):
        """PlayerDashboardByYearOverYear uses correct response model."""
        endpoint = PlayerDashboardByYearOverYear()

        assert endpoint.response_model is PlayerDashboardByYearOverYearResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByYearOverYear is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByYearOverYear()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen


class TestPlayerDashboardByYearOverYearResponse:
    """Tests for PlayerDashboardByYearOverYearResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for year over year result sets (66 columns)."""
        return [
            "GROUP_SET",
            "GROUP_VALUE",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "MAX_GAME_DATE",
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
    def _make_row(
        group_set: str,
        group_value: str,
        team_id: int,
        team_abbrev: str,
        gp: int,
        wins: int,
        losses: int,
    ) -> list:
        """Create a test row for year over year stats (66 values)."""
        return [
            group_set,
            group_value,
            team_id,
            team_abbrev,
            "2025-04-13T00:00:00",  # MAX_GAME_DATE
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
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Overall", "2024-25", 1610612743, "DEN", 8, 5, 3)
                    ],
                },
                {
                    "name": "ByYearPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            "By Year", "2024-25", 1610612743, "DEN", 8, 5, 3
                        ),
                        self._make_row(
                            "By Year", "2023-24", 1610612743, "DEN", 79, 53, 26
                        ),
                        self._make_row(
                            "By Year", "2022-23", 1610612743, "DEN", 69, 46, 23
                        ),
                    ],
                },
            ]
        }

        response = PlayerDashboardByYearOverYearResponse.model_validate(raw_response)

        # Check overall
        assert response.overall is not None
        assert response.overall.group_value == "2024-25"
        assert response.overall.team_id == 1610612743
        assert response.overall.team_abbreviation == "DEN"
        assert response.overall.gp == 8
        assert response.overall.w == 5
        assert response.overall.losses == 3

        # Check by year
        assert len(response.by_year) == 3
        assert response.by_year[0].group_value == "2024-25"
        assert response.by_year[0].gp == 8
        assert response.by_year[1].group_value == "2023-24"
        assert response.by_year[1].gp == 79
        assert response.by_year[2].group_value == "2022-23"
        assert response.by_year[2].gp == 69

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "ByYearPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashboardByYearOverYearResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.by_year == []
