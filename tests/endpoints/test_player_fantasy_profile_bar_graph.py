"""Tests for PlayerFantasyProfileBarGraph endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import PlayerFantasyProfileBarGraph
from fastbreak.models import PlayerFantasyProfileBarGraphResponse


class TestPlayerFantasyProfileBarGraph:
    """Tests for PlayerFantasyProfileBarGraph endpoint."""

    def test_init_with_defaults(self):
        """PlayerFantasyProfileBarGraph uses sensible defaults."""
        endpoint = PlayerFantasyProfileBarGraph(player_id="2544")

        assert endpoint.player_id == "2544"
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"

    def test_init_with_player_id(self):
        """PlayerFantasyProfileBarGraph accepts player_id."""
        endpoint = PlayerFantasyProfileBarGraph(player_id="2544")

        assert endpoint.player_id == "2544"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerFantasyProfileBarGraph(player_id="2544", season="2023-24")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Regular Season"

    def test_path_is_correct(self):
        """PlayerFantasyProfileBarGraph has correct API path."""
        endpoint = PlayerFantasyProfileBarGraph(player_id="2544")

        assert endpoint.path == "playerfantasyprofilebargraph"

    def test_response_model_is_correct(self):
        """PlayerFantasyProfileBarGraph uses correct response model."""
        endpoint = PlayerFantasyProfileBarGraph(player_id="2544")

        assert endpoint.response_model is PlayerFantasyProfileBarGraphResponse

    def test_endpoint_is_frozen(self):
        """PlayerFantasyProfileBarGraph is immutable (frozen dataclass)."""
        endpoint = PlayerFantasyProfileBarGraph(player_id="2544")

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen


class TestPlayerFantasyProfileBarGraphResponse:
    """Tests for PlayerFantasyProfileBarGraphResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for fantasy stats (15 columns)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "FAN_DUEL_PTS",
            "NBA_FANTASY_PTS",
            "PTS",
            "REB",
            "AST",
            "FG3M",
            "FT_PCT",
            "STL",
            "BLK",
            "TOV",
            "FG_PCT",
        ]

    @staticmethod
    def _make_row(
        player_id: int,
        player_name: str,
        team_id: int,
        team_abbrev: str,
        pts: float,
        reb: float,
        ast: float,
    ) -> list:
        """Create a test row for fantasy stats (15 values)."""
        # Fantasy points are roughly: PTS + REB*1.2 + AST*1.5 + ...
        fan_duel = pts + reb * 1.2 + ast * 1.5 + 5.0
        nba_fantasy = pts + reb * 1.2 + ast * 1.5 + 6.0
        return [
            player_id,
            player_name,
            team_id,
            team_abbrev,
            fan_duel,
            nba_fantasy,
            pts,
            reb,
            ast,
            2.0,  # FG3M
            0.80,  # FT_PCT
            1.0,  # STL
            0.5,  # BLK
            3.0,  # TOV
            0.50,  # FG_PCT
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "SeasonAvg",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            2544, "LeBron James", 1610612747, "LAL", 25.0, 8.0, 8.0
                        ),
                    ],
                },
                {
                    "name": "LastFiveGamesAvg",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            2544, "LeBron James", 1610612747, "LAL", 22.0, 6.0, 7.0
                        ),
                    ],
                },
            ]
        }

        response = PlayerFantasyProfileBarGraphResponse.model_validate(raw_response)

        # Check season avg
        assert response.season_avg is not None
        assert response.season_avg.player_id == 2544
        assert response.season_avg.player_name == "LeBron James"
        assert response.season_avg.team_abbreviation == "LAL"
        assert response.season_avg.pts == 25.0
        assert response.season_avg.reb == 8.0
        assert response.season_avg.ast == 8.0

        # Check last 5 games avg
        assert response.last_five_games_avg is not None
        assert response.last_five_games_avg.player_id == 2544
        assert response.last_five_games_avg.pts == 22.0
        assert response.last_five_games_avg.reb == 6.0

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {"name": "SeasonAvg", "headers": headers, "rowSet": []},
                {"name": "LastFiveGamesAvg", "headers": headers, "rowSet": []},
            ]
        }

        response = PlayerFantasyProfileBarGraphResponse.model_validate(raw_response)

        assert response.season_avg is None
        assert response.last_five_games_avg is None
