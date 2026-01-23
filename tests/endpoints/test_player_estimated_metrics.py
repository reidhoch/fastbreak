"""Tests for PlayerEstimatedMetrics endpoint."""

from fastbreak.endpoints import PlayerEstimatedMetrics
from fastbreak.models import PlayerEstimatedMetricsResponse


class TestPlayerEstimatedMetrics:
    """Tests for PlayerEstimatedMetrics endpoint."""

    def test_init_with_defaults(self):
        """PlayerEstimatedMetrics uses sensible defaults."""
        endpoint = PlayerEstimatedMetrics()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"

    def test_init_with_custom_season(self):
        """PlayerEstimatedMetrics accepts custom season."""
        endpoint = PlayerEstimatedMetrics(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerEstimatedMetrics(season="2023-24", season_type="Playoffs")

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Playoffs"

    def test_path_is_correct(self):
        """PlayerEstimatedMetrics has correct API path."""
        endpoint = PlayerEstimatedMetrics()

        assert endpoint.path == "playerestimatedmetrics"

    def test_response_model_is_correct(self):
        """PlayerEstimatedMetrics uses correct response model."""
        endpoint = PlayerEstimatedMetrics()

        assert endpoint.response_model is PlayerEstimatedMetricsResponse

    def test_endpoint_is_frozen(self):
        """PlayerEstimatedMetrics is immutable (frozen dataclass)."""
        endpoint = PlayerEstimatedMetrics()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen


class TestPlayerEstimatedMetricsResponse:
    """Tests for PlayerEstimatedMetricsResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for player estimated metrics (32 columns)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME",
            "GP",
            "W",
            "L",
            "W_PCT",
            "MIN",
            "E_OFF_RATING",
            "E_DEF_RATING",
            "E_NET_RATING",
            "E_AST_RATIO",
            "E_OREB_PCT",
            "E_DREB_PCT",
            "E_REB_PCT",
            "E_TOV_PCT",
            "E_USG_PCT",
            "E_PACE",
            "GP_RANK",
            "W_RANK",
            "L_RANK",
            "W_PCT_RANK",
            "MIN_RANK",
            "E_OFF_RATING_RANK",
            "E_DEF_RATING_RANK",
            "E_NET_RATING_RANK",
            "E_AST_RATIO_RANK",
            "E_OREB_PCT_RANK",
            "E_DREB_PCT_RANK",
            "E_REB_PCT_RANK",
            "E_TOV_PCT_RANK",
            "E_USG_PCT_RANK",
            "E_PACE_RANK",
        ]

    @staticmethod
    def _make_row(
        player_id: int,
        player_name: str,
        games: int,
        wins: int,
        off_rating: float,
        def_rating: float,
    ) -> list:
        """Create a test row for player estimated metrics (32 values)."""
        losses = games - wins
        net_rating = off_rating - def_rating
        win_pct = wins / games if games > 0 else 0.0
        return [
            player_id,
            player_name,
            games,
            wins,
            losses,
            win_pct,
            30.0,  # MIN
            off_rating,
            def_rating,
            net_rating,
            15.0,  # E_AST_RATIO
            0.05,  # E_OREB_PCT
            0.15,  # E_DREB_PCT
            0.10,  # E_REB_PCT
            10.0,  # E_TOV_PCT
            0.20,  # E_USG_PCT
            100.0,  # E_PACE
            1,  # GP_RANK
            10,  # W_RANK
            50,  # L_RANK
            20,  # W_PCT_RANK
            5,  # MIN_RANK
            15,  # E_OFF_RATING_RANK
            25,  # E_DEF_RATING_RANK
            12,  # E_NET_RATING_RANK
            30,  # E_AST_RATIO_RANK
            100,  # E_OREB_PCT_RANK
            80,  # E_DREB_PCT_RANK
            90,  # E_REB_PCT_RANK
            45,  # E_TOV_PCT_RANK
            35,  # E_USG_PCT_RANK
            55,  # E_PACE_RANK
        ]

    def test_parse_singular_result_set(self):
        """Response parses NBA's singular resultSet format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resource": "playerestimatedmetrics",
            "resultSet": {
                "name": "PlayerEstimatedMetrics",
                "headers": headers,
                "rowSet": [
                    self._make_row(203999, "Nikola Jokic", 70, 50, 118.5, 108.0),
                    self._make_row(201566, "Russell Westbrook", 65, 30, 105.0, 112.0),
                ],
            },
        }

        response = PlayerEstimatedMetricsResponse.model_validate(raw_response)

        assert len(response.players) == 2

        # Check first player (Jokic)
        jokic = response.players[0]
        assert jokic.player_id == 203999
        assert jokic.player_name == "Nikola Jokic"
        assert jokic.gp == 70
        assert jokic.wins == 50
        assert jokic.losses == 20
        assert jokic.e_off_rating == 118.5
        assert jokic.e_def_rating == 108.0
        assert jokic.e_net_rating == 10.5
        assert jokic.gp_rank == 1

        # Check second player (Westbrook)
        westbrook = response.players[1]
        assert westbrook.player_id == 201566
        assert westbrook.player_name == "Russell Westbrook"
        assert westbrook.gp == 65
        assert westbrook.e_net_rating == -7.0

    def test_parse_empty_result_set(self):
        """Response handles empty result set."""
        headers = self._make_headers()

        raw_response = {
            "resource": "playerestimatedmetrics",
            "resultSet": {
                "name": "PlayerEstimatedMetrics",
                "headers": headers,
                "rowSet": [],
            },
        }

        response = PlayerEstimatedMetricsResponse.model_validate(raw_response)

        assert response.players == []
