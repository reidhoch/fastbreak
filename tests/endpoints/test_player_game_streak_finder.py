"""Tests for PlayerGameStreakFinder endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import PlayerGameStreakFinder
from fastbreak.models import PlayerGameStreakFinderResponse


class TestPlayerGameStreakFinder:
    """Tests for PlayerGameStreakFinder endpoint."""

    def test_init_with_defaults(self):
        """PlayerGameStreakFinder uses sensible defaults."""
        endpoint = PlayerGameStreakFinder(player_id="2544")

        assert endpoint.player_id == "2544"
        assert endpoint.league_id == "00"

    def test_init_with_player_id(self):
        """PlayerGameStreakFinder accepts player_id."""
        endpoint = PlayerGameStreakFinder(player_id="2544")

        assert endpoint.player_id == "2544"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerGameStreakFinder(player_id="2544")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """PlayerGameStreakFinder has correct API path."""
        endpoint = PlayerGameStreakFinder(player_id="2544")

        assert endpoint.path == "playergamestreakfinder"

    def test_response_model_is_correct(self):
        """PlayerGameStreakFinder uses correct response model."""
        endpoint = PlayerGameStreakFinder(player_id="2544")

        assert endpoint.response_model is PlayerGameStreakFinderResponse

    def test_endpoint_is_frozen(self):
        """PlayerGameStreakFinder is immutable (frozen dataclass)."""
        endpoint = PlayerGameStreakFinder(player_id="2544")

        try:
            endpoint.player_id = "203999"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen


class TestPlayerGameStreakFinderResponse:
    """Tests for PlayerGameStreakFinderResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for player game streak finder (9 columns)."""
        return [
            "PLAYER_NAME_LAST_FIRST",
            "PLAYER_ID",
            "GAMESTREAK",
            "STARTDATE",
            "ENDDATE",
            "ACTIVESTREAK",
            "NUMSEASONS",
            "LASTSEASON",
            "FIRSTSEASON",
        ]

    @staticmethod
    def _make_row(
        player_name: str,
        player_id: int,
        streak: int,
        start: str,
        end: str,
        active: int,
        seasons: int,
    ) -> list:
        """Create a test row for player game streak (9 values)."""
        return [
            player_name,
            player_id,
            streak,
            start,
            end,
            active,
            seasons,
            "2024-25",
            "2003-04",
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerGameStreakFinderResults",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            "James, LeBron",
                            2544,
                            1588,
                            "2003-10-29T00:00:00",
                            "2026-01-22T00:00:00",
                            1,
                            23,
                        ),
                    ],
                }
            ]
        }

        response = PlayerGameStreakFinderResponse.model_validate(raw_response)

        assert len(response.streaks) == 1

        streak = response.streaks[0]
        assert streak.player_name == "James, LeBron"
        assert streak.player_id == 2544
        assert streak.game_streak == 1588
        assert streak.start_date == "2003-10-29T00:00:00"
        assert streak.end_date == "2026-01-22T00:00:00"
        assert streak.active_streak == 1
        assert streak.num_seasons == 23
        assert streak.first_season == "2003-04"
        assert streak.last_season == "2024-25"

    def test_parse_empty_result_set(self):
        """Response handles empty result set."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerGameStreakFinderResults",
                    "headers": headers,
                    "rowSet": [],
                }
            ]
        }

        response = PlayerGameStreakFinderResponse.model_validate(raw_response)

        assert response.streaks == []
