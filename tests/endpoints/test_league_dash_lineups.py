"""Tests for LeagueDashLineups endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashLineups
from fastbreak.models import LeagueDashLineupsResponse
from fastbreak.seasons import get_season_from_date


class TestLeagueDashLineups:
    """Tests for LeagueDashLineups endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashLineups uses sensible defaults."""
        endpoint = LeagueDashLineups(team_id=1610612747)

        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.group_quantity == 5
        assert endpoint.league_id == "00"

    def test_init_with_custom_params(self):
        """LeagueDashLineups accepts custom parameters."""
        endpoint = LeagueDashLineups(
            team_id=1610612747,
            season="2023-24",
            season_type="Playoffs",
            per_mode="Totals",
            measure_type="Advanced",
            group_quantity=3,
        )

        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.measure_type == "Advanced"
        assert endpoint.group_quantity == 3

    def test_params_with_defaults_only(self):
        """params() returns required parameters with defaults."""
        endpoint = LeagueDashLineups(team_id=1610612747)

        params = endpoint.params()

        assert params["Season"] == get_season_from_date()
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["GroupQuantity"] == "5"
        assert params["TeamID"] == "1610612747"
        assert "Outcome" not in params
        assert "Location" not in params

    def test_params_with_all_optional_filters(self):
        """params() includes all optional filters when set."""
        endpoint = LeagueDashLineups(
            team_id=1610612747,
            outcome="W",
            location="Home",
            date_from="01/01/2025",
            date_to="01/31/2025",
            vs_conference="East",
            vs_division="Atlantic",
            game_segment="First Half",
            shot_clock_range="24-22",
            conference="West",
            division="Pacific",
            season_segment="Pre All-Star",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["DateFrom"] == "01/01/2025"
        assert params["DateTo"] == "01/31/2025"
        assert params["VsConference"] == "East"
        assert params["VsDivision"] == "Atlantic"
        assert params["GameSegment"] == "First Half"
        assert params["ShotClockRange"] == "24-22"
        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"
        assert params["SeasonSegment"] == "Pre All-Star"

    def test_params_with_partial_optional_filters(self):
        """params() includes only set optional filters."""
        endpoint = LeagueDashLineups(
            team_id=1610612747,
            outcome="L",
            location="Road",
        )

        params = endpoint.params()

        assert params["Outcome"] == "L"
        assert params["Location"] == "Road"
        assert "DateFrom" not in params
        assert "VsConference" not in params

    def test_path_is_correct(self):
        """LeagueDashLineups has correct API path."""
        endpoint = LeagueDashLineups(team_id=1610612747)

        assert endpoint.path == "leaguedashlineups"

    def test_response_model_is_correct(self):
        """LeagueDashLineups uses LeagueDashLineupsResponse model."""
        endpoint = LeagueDashLineups(team_id=1610612747)

        assert endpoint.response_model is LeagueDashLineupsResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashLineups is immutable (frozen dataclass)."""
        endpoint = LeagueDashLineups(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = 1610612738  # type: ignore[misc]
