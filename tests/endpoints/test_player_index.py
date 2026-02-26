"""Tests for PlayerIndex endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerIndex
from fastbreak.models import PlayerIndexResponse
from fastbreak.seasons import get_season_from_date


class TestPlayerIndex:
    """Tests for PlayerIndex endpoint."""

    def test_init_with_defaults(self):
        """PlayerIndex uses sensible defaults."""
        endpoint = PlayerIndex()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()

    def test_init_with_custom_season(self):
        """PlayerIndex accepts custom season."""
        endpoint = PlayerIndex(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerIndex(season="2023-24")

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"

    def test_path_is_correct(self):
        """PlayerIndex has correct API path."""
        endpoint = PlayerIndex()

        assert endpoint.path == "playerindex"

    def test_response_model_is_correct(self):
        """PlayerIndex uses correct response model."""
        endpoint = PlayerIndex()

        assert endpoint.response_model is PlayerIndexResponse

    def test_endpoint_is_frozen(self):
        """PlayerIndex is immutable (frozen dataclass)."""
        endpoint = PlayerIndex()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerIndexResponse:
    """Tests for PlayerIndexResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for player index (26 columns)."""
        return [
            "PERSON_ID",
            "PLAYER_LAST_NAME",
            "PLAYER_FIRST_NAME",
            "PLAYER_SLUG",
            "TEAM_ID",
            "TEAM_SLUG",
            "IS_DEFUNCT",
            "TEAM_CITY",
            "TEAM_NAME",
            "TEAM_ABBREVIATION",
            "JERSEY_NUMBER",
            "POSITION",
            "HEIGHT",
            "WEIGHT",
            "COLLEGE",
            "COUNTRY",
            "DRAFT_YEAR",
            "DRAFT_ROUND",
            "DRAFT_NUMBER",
            "ROSTER_STATUS",
            "FROM_YEAR",
            "TO_YEAR",
            "PTS",
            "REB",
            "AST",
            "STATS_TIMEFRAME",
        ]

    @staticmethod
    def _make_row(
        person_id: int,
        last_name: str,
        first_name: str,
        team_abbrev: str,
        position: str,
        pts: float | None,
    ) -> list:
        """Create a test row for player index (26 values)."""
        return [
            person_id,
            last_name,
            first_name,
            f"{first_name.lower()}-{last_name.lower()}",  # PLAYER_SLUG
            1610612747,  # TEAM_ID (Lakers)
            "lakers",  # TEAM_SLUG
            0,  # IS_DEFUNCT
            "Los Angeles",  # TEAM_CITY
            "Lakers",  # TEAM_NAME
            team_abbrev,
            "23",  # JERSEY_NUMBER
            position,
            "6-9",  # HEIGHT
            "250",  # WEIGHT
            "None",  # COLLEGE
            "USA",  # COUNTRY
            2003,  # DRAFT_YEAR
            1,  # DRAFT_ROUND
            1,  # DRAFT_NUMBER
            1.0,  # ROSTER_STATUS
            "2003",  # FROM_YEAR
            "2024",  # TO_YEAR
            pts,
            8.0,  # REB
            8.0,  # AST
            "Season",  # STATS_TIMEFRAME
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerIndex",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(2544, "James", "LeBron", "LAL", "F", 25.0),
                        self._make_row(203076, "Davis", "Anthony", "LAL", "F-C", 24.0),
                    ],
                }
            ]
        }

        response = PlayerIndexResponse.model_validate(raw_response)

        assert len(response.players) == 2

        # Check first player
        lebron = response.players[0]
        assert lebron.person_id == 2544
        assert lebron.player_last_name == "James"
        assert lebron.player_first_name == "LeBron"
        assert lebron.player_slug == "lebron-james"
        assert lebron.team_abbreviation == "LAL"
        assert lebron.position == "F"
        assert lebron.height == "6-9"
        assert lebron.draft_year == 2003
        assert lebron.draft_round == 1
        assert lebron.draft_number == 1
        assert lebron.pts == 25.0
        assert lebron.roster_status == 1.0

        # Check second player
        ad = response.players[1]
        assert ad.person_id == 203076
        assert ad.player_last_name == "Davis"
        assert ad.position == "F-C"

    def test_parse_empty_result_set(self):
        """Response handles empty result set."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [{"name": "PlayerIndex", "headers": headers, "rowSet": []}]
        }

        response = PlayerIndexResponse.model_validate(raw_response)

        assert response.players == []
