"""Tests for PlayerDashPtShotDefend endpoint."""

from fastbreak.endpoints import PlayerDashPtShotDefend
from fastbreak.models import PlayerDashPtShotDefendResponse


class TestPlayerDashPtShotDefend:
    """Tests for PlayerDashPtShotDefend endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashPtShotDefend uses sensible defaults."""
        endpoint = PlayerDashPtShotDefend()

        assert endpoint.player_id == ""
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.per_mode == "PerGame"

    def test_init_with_player_id(self):
        """PlayerDashPtShotDefend accepts player_id."""
        endpoint = PlayerDashPtShotDefend(player_id="203999")

        assert endpoint.player_id == "203999"

    def test_params_with_required_only(self):
        """params() returns required parameters."""
        endpoint = PlayerDashPtShotDefend(player_id="203999")

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """PlayerDashPtShotDefend has correct API path."""
        endpoint = PlayerDashPtShotDefend()

        assert endpoint.path == "playerdashptshotdefend"

    def test_response_model_is_correct(self):
        """PlayerDashPtShotDefend uses correct response model."""
        endpoint = PlayerDashPtShotDefend()

        assert endpoint.response_model is PlayerDashPtShotDefendResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashPtShotDefend is immutable (frozen dataclass)."""
        endpoint = PlayerDashPtShotDefend()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen


class TestPlayerDashPtShotDefendResponse:
    """Tests for PlayerDashPtShotDefendResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for defending shots (10 columns)."""
        return [
            "MATCHUPID",
            "GP",
            "G",
            "DEFENSE_CATEGORY",
            "FREQ",
            "D_FGM",
            "D_FGA",
            "D_FG_PCT",
            "NORMAL_FG_PCT",
            "PCT_PLUSMINUS",
        ]

    @staticmethod
    def _make_row(
        matchup_id: int,
        games: int,
        category: str,
        d_fgm: float,
        d_fga: float,
        normal_pct: float,
    ) -> list:
        """Create a test row for defending shots (10 values)."""
        d_fg_pct = d_fgm / d_fga if d_fga > 0 else 0.0
        return [
            matchup_id,
            games,
            games,
            category,
            1.0 if category == "Overall" else 0.5,
            d_fgm,
            d_fga,
            d_fg_pct,
            normal_pct,
            d_fg_pct - normal_pct,
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "DefendingShots",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(203999, 8, "Overall", 10.0, 21.0, 0.48),
                        self._make_row(203999, 8, "3 Pointers", 3.0, 8.0, 0.36),
                        self._make_row(203999, 8, "2 Pointers", 7.0, 13.0, 0.52),
                    ],
                }
            ]
        }

        response = PlayerDashPtShotDefendResponse.model_validate(raw_response)

        assert len(response.defending_shots) == 3

        # Check overall
        overall = response.defending_shots[0]
        assert overall.matchup_id == 203999
        assert overall.defense_category == "Overall"
        assert overall.d_fgm == 10.0
        assert overall.d_fga == 21.0

        # Check 3 pointers
        threes = response.defending_shots[1]
        assert threes.defense_category == "3 Pointers"
        assert threes.d_fga == 8.0

        # Check 2 pointers
        twos = response.defending_shots[2]
        assert twos.defense_category == "2 Pointers"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [{"name": "DefendingShots", "headers": headers, "rowSet": []}]
        }

        response = PlayerDashPtShotDefendResponse.model_validate(raw_response)

        assert response.defending_shots == []
