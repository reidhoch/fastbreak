"""Tests for PlayerDashPtReb endpoint."""

from fastbreak.endpoints import PlayerDashPtReb
from fastbreak.models import PlayerDashPtRebResponse


class TestPlayerDashPtReb:
    """Tests for PlayerDashPtReb endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashPtReb uses sensible defaults."""
        endpoint = PlayerDashPtReb()

        assert endpoint.player_id == 0
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.per_mode == "PerGame"
        # Always-sent params have default 0
        assert endpoint.team_id == 0
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.period == 0
        assert endpoint.last_n_games == 0

    def test_init_with_player_id(self):
        """PlayerDashPtReb accepts player_id."""
        endpoint = PlayerDashPtReb(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashPtReb accepts optional filters."""
        endpoint = PlayerDashPtReb(
            player_id=203999,
            season="2023-24",
            outcome="W",
            ist_round="Finals",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.outcome == "W"
        assert endpoint.ist_round == "Finals"

    def test_params_with_required_only(self):
        """params() returns required and always-sent parameters."""
        endpoint = PlayerDashPtReb(player_id=203999)

        params = endpoint.params()

        assert params == {
            "PlayerID": "203999",
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "TeamID": "0",
            "Month": "0",
            "OpponentTeamID": "0",
            "Period": "0",
            "LastNGames": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerDashPtReb(
            player_id=203999,
            outcome="W",
            location="Home",
            ist_round="Finals",
        )

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["ISTRound"] == "Finals"

    def test_path_is_correct(self):
        """PlayerDashPtReb has correct API path."""
        endpoint = PlayerDashPtReb()

        assert endpoint.path == "playerdashptreb"

    def test_response_model_is_correct(self):
        """PlayerDashPtReb uses correct response model."""
        endpoint = PlayerDashPtReb()

        assert endpoint.response_model is PlayerDashPtRebResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashPtReb is immutable (frozen dataclass)."""
        endpoint = PlayerDashPtReb()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen


class TestPlayerDashPtRebResponse:
    """Tests for PlayerDashPtRebResponse model."""

    @staticmethod
    def _make_overall_headers() -> list[str]:
        """Return headers for overall rebounding (16 columns)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME_LAST_FIRST",
            "G",
            "OVERALL",
            "REB_FREQUENCY",
            "OREB",
            "DREB",
            "REB",
            "C_OREB",
            "C_DREB",
            "C_REB",
            "C_REB_PCT",
            "UC_OREB",
            "UC_DREB",
            "UC_REB",
            "UC_REB_PCT",
        ]

    @staticmethod
    def _make_breakdown_headers(range_col: str) -> list[str]:
        """Return headers for breakdown result sets (17 columns)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME_LAST_FIRST",
            "SORT_ORDER",
            "G",
            range_col,
            "REB_FREQUENCY",
            "OREB",
            "DREB",
            "REB",
            "C_OREB",
            "C_DREB",
            "C_REB",
            "C_REB_PCT",
            "UC_OREB",
            "UC_DREB",
            "UC_REB",
            "UC_REB_PCT",
        ]

    @staticmethod
    def _make_overall_row(
        player_id: int, player_name: str, games: int, reb: float
    ) -> list:
        """Create a test row for overall rebounding (16 values)."""
        return [
            player_id,
            player_name,
            games,
            "Overall",
            1.0,  # REB_FREQUENCY
            reb * 0.2,  # OREB
            reb * 0.8,  # DREB
            reb,
            reb * 0.1,  # C_OREB
            reb * 0.3,  # C_DREB
            reb * 0.4,  # C_REB
            0.4,  # C_REB_PCT
            reb * 0.1,  # UC_OREB
            reb * 0.5,  # UC_DREB
            reb * 0.6,  # UC_REB
            0.6,  # UC_REB_PCT
        ]

    @staticmethod
    def _make_breakdown_row(
        player_id: int,
        player_name: str,
        sort_order: int,
        games: int,
        range_value: str,
        reb: float,
    ) -> list:
        """Create a test row for breakdown result sets (17 values)."""
        return [
            player_id,
            player_name,
            sort_order,
            games,
            range_value,
            0.5,  # REB_FREQUENCY
            reb * 0.2,  # OREB
            reb * 0.8,  # DREB
            reb,
            reb * 0.1,  # C_OREB
            reb * 0.3,  # C_DREB
            reb * 0.4,  # C_REB
            0.4,  # C_REB_PCT
            reb * 0.1,  # UC_OREB
            reb * 0.5,  # UC_DREB
            reb * 0.6,  # UC_REB
            0.6,  # UC_REB_PCT
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        overall_headers = self._make_overall_headers()
        shot_type_headers = self._make_breakdown_headers("SHOT_TYPE_RANGE")
        num_contested_headers = self._make_breakdown_headers("REB_NUM_CONTESTING_RANGE")
        shot_dist_headers = self._make_breakdown_headers("SHOT_DIST_RANGE")
        reb_dist_headers = self._make_breakdown_headers("REB_DIST_RANGE")

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallRebounding",
                    "headers": overall_headers,
                    "rowSet": [
                        self._make_overall_row(203999, "Jokić, Nikola", 8, 12.0)
                    ],
                },
                {
                    "name": "ShotTypeRebounding",
                    "headers": shot_type_headers,
                    "rowSet": [
                        self._make_breakdown_row(
                            203999, "Jokić, Nikola", 1, 8, "Miss 2FG", 7.0
                        ),
                        self._make_breakdown_row(
                            203999, "Jokić, Nikola", 2, 8, "Miss 3FG", 5.0
                        ),
                    ],
                },
                {
                    "name": "NumContestedRebounding",
                    "headers": num_contested_headers,
                    "rowSet": [
                        self._make_breakdown_row(
                            203999,
                            "Jokić, Nikola",
                            1,
                            8,
                            "0 Contesting Rebounders",
                            6.0,
                        ),
                    ],
                },
                {
                    "name": "ShotDistanceRebounding",
                    "headers": shot_dist_headers,
                    "rowSet": [
                        self._make_breakdown_row(
                            203999, "Jokić, Nikola", 1, 8, "0-6 Feet", 4.0
                        ),
                    ],
                },
                {
                    "name": "RebDistanceRebounding",
                    "headers": reb_dist_headers,
                    "rowSet": [
                        self._make_breakdown_row(
                            203999, "Jokić, Nikola", 1, 8, "0-3 Feet", 3.5
                        ),
                    ],
                },
            ]
        }

        response = PlayerDashPtRebResponse.model_validate(raw_response)

        # Check overall
        assert response.overall is not None
        assert response.overall.player_id == 203999
        assert response.overall.reb == 12.0
        assert response.overall.overall == "Overall"

        # Check shot type breakdown
        assert len(response.by_shot_type) == 2
        assert response.by_shot_type[0].shot_type_range == "Miss 2FG"
        assert response.by_shot_type[0].reb == 7.0
        assert response.by_shot_type[1].shot_type_range == "Miss 3FG"

        # Check num contested breakdown
        assert len(response.by_num_contested) == 1
        assert (
            response.by_num_contested[0].reb_num_contesting_range
            == "0 Contesting Rebounders"
        )

        # Check shot distance breakdown
        assert len(response.by_shot_distance) == 1
        assert response.by_shot_distance[0].shot_dist_range == "0-6 Feet"

        # Check reb distance breakdown
        assert len(response.by_reb_distance) == 1
        assert response.by_reb_distance[0].reb_dist_range == "0-3 Feet"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        overall_headers = self._make_overall_headers()
        shot_type_headers = self._make_breakdown_headers("SHOT_TYPE_RANGE")
        num_contested_headers = self._make_breakdown_headers("REB_NUM_CONTESTING_RANGE")
        shot_dist_headers = self._make_breakdown_headers("SHOT_DIST_RANGE")
        reb_dist_headers = self._make_breakdown_headers("REB_DIST_RANGE")

        raw_response = {
            "resultSets": [
                {"name": "OverallRebounding", "headers": overall_headers, "rowSet": []},
                {
                    "name": "ShotTypeRebounding",
                    "headers": shot_type_headers,
                    "rowSet": [],
                },
                {
                    "name": "NumContestedRebounding",
                    "headers": num_contested_headers,
                    "rowSet": [],
                },
                {
                    "name": "ShotDistanceRebounding",
                    "headers": shot_dist_headers,
                    "rowSet": [],
                },
                {
                    "name": "RebDistanceRebounding",
                    "headers": reb_dist_headers,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashPtRebResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.by_shot_type == []
        assert response.by_num_contested == []
        assert response.by_shot_distance == []
        assert response.by_reb_distance == []
