"""Tests for PlayerDashboardByGameSplits endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByGameSplits
from fastbreak.models import PlayerDashboardByGameSplitsResponse


class TestPlayerDashboardByGameSplits:
    """Tests for PlayerDashboardByGameSplits endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByGameSplits uses sensible defaults."""
        endpoint = PlayerDashboardByGameSplits(player_id=2544)

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        # Always-sent params have default 0
        assert endpoint.po_round == 0
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.period == 0
        assert endpoint.last_n_games == 0
        assert endpoint.ist_round == ""

    def test_init_with_player_id(self):
        """PlayerDashboardByGameSplits accepts player_id."""
        endpoint = PlayerDashboardByGameSplits(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashboardByGameSplits accepts optional filters."""
        endpoint = PlayerDashboardByGameSplits(
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
        endpoint = PlayerDashboardByGameSplits(player_id=203999)

        params = endpoint.params()

        assert params == {
            "PlayerID": "203999",
            "LeagueID": "00",
            "Season": "2024-25",
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
            "ISTRound": "",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerDashboardByGameSplits(
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
        """PlayerDashboardByGameSplits has correct API path."""
        endpoint = PlayerDashboardByGameSplits(player_id=2544)

        assert endpoint.path == "playerdashboardbygamesplits"

    def test_response_model_is_correct(self):
        """PlayerDashboardByGameSplits uses correct response model."""
        endpoint = PlayerDashboardByGameSplits(player_id=2544)

        assert endpoint.response_model is PlayerDashboardByGameSplitsResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByGameSplits is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByGameSplits(player_id=2544)

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestPlayerDashboardByGameSplitsResponse:
    """Tests for PlayerDashboardByGameSplitsResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return the 63 headers for game split stats."""
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
    def _make_row(group_set: str, group_value: str | int, pts: float) -> list:
        """Create a test row with specified values."""
        return [
            group_set,
            group_value,
            10,  # GP
            6,  # W
            4,  # L
            0.6,  # W_PCT
            35.5,  # MIN
            11.0,  # FGM
            19.5,  # FGA
            0.564,  # FG_PCT
            2.0,  # FG3M
            4.5,  # FG3A
            0.444,  # FG3_PCT
            5.5,  # FTM
            7.0,  # FTA
            0.786,  # FT_PCT
            2.5,  # OREB
            9.0,  # DREB
            11.5,  # REB
            9.5,  # AST
            3.5,  # TOV
            2.0,  # STL
            0.5,  # BLK
            1.0,  # BLKA
            2.0,  # PF
            6.5,  # PFD
            pts,  # PTS
            10.0,  # PLUS_MINUS
            60.0,  # NBA_FANTASY_PTS
            8,  # DD2
            5,  # TD3
            55.0,  # WNBA_FANTASY_PTS
            *[1] * 31,  # All rank columns = 1
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
                    "name": "ByHalfPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("By Half", "First Half", 17.5),
                        self._make_row("By Half", "Second Half", 12.0),
                    ],
                },
                {
                    "name": "ByPeriodPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("By Period", 1, 11.0),
                        self._make_row("By Period", 2, 6.5),
                        self._make_row("By Period", 3, 7.0),
                        self._make_row("By Period", 4, 5.0),
                    ],
                },
                {
                    "name": "ByScoreMarginPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("By Score Margin", "Tied", 1.6),
                        self._make_row("By Score Margin", "Behind", 10.5),
                        self._make_row("By Score Margin", "Ahead", 17.4),
                    ],
                },
                {
                    "name": "ByActualMarginPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            "By Actual Margin", "Behind 11 - 15 Points", 3.0
                        ),
                        self._make_row("By Actual Margin", "Ahead 6 - 10 Points", 8.0),
                    ],
                },
            ]
        }

        response = PlayerDashboardByGameSplitsResponse.model_validate(raw_response)

        # Check overall stats
        assert response.overall is not None
        assert response.overall.group_set == "Overall"
        assert response.overall.group_value == "2024-25"
        assert response.overall.pts == 29.5
        assert response.overall.gp == 10

        # Check by_half stats
        assert len(response.by_half) == 2
        assert response.by_half[0].group_value == "First Half"
        assert response.by_half[0].pts == 17.5
        assert response.by_half[1].group_value == "Second Half"
        assert response.by_half[1].pts == 12.0

        # Check by_period stats (note: GROUP_VALUE is int for periods)
        assert len(response.by_period) == 4
        assert response.by_period[0].group_value == 1
        assert response.by_period[0].pts == 11.0
        assert response.by_period[3].group_value == 4
        assert response.by_period[3].pts == 5.0

        # Check by_score_margin stats
        assert len(response.by_score_margin) == 3
        assert response.by_score_margin[0].group_value == "Tied"
        assert response.by_score_margin[2].group_value == "Ahead"

        # Check by_actual_margin stats
        assert len(response.by_actual_margin) == 2
        assert response.by_actual_margin[0].group_value == "Behind 11 - 15 Points"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {"name": "OverallPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "ByHalfPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "ByPeriodPlayerDashboard", "headers": headers, "rowSet": []},
                {
                    "name": "ByScoreMarginPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {
                    "name": "ByActualMarginPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashboardByGameSplitsResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.by_half == []
        assert response.by_period == []
        assert response.by_score_margin == []
        assert response.by_actual_margin == []

    def test_mixed_group_value_types(self):
        """Response handles both string and int GROUP_VALUE types."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {"name": "OverallPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "ByHalfPlayerDashboard", "headers": headers, "rowSet": []},
                {
                    "name": "ByPeriodPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("By Period", 1, 10.0),  # int group_value
                        self._make_row("By Period", 2, 8.0),
                    ],
                },
                {
                    "name": "ByScoreMarginPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            "By Score Margin", "Ahead", 15.0
                        ),  # str group_value
                    ],
                },
                {
                    "name": "ByActualMarginPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashboardByGameSplitsResponse.model_validate(raw_response)

        # Int group_value for periods
        assert response.by_period[0].group_value == 1
        assert isinstance(response.by_period[0].group_value, int)

        # String group_value for score margin
        assert response.by_score_margin[0].group_value == "Ahead"
        assert isinstance(response.by_score_margin[0].group_value, str)
