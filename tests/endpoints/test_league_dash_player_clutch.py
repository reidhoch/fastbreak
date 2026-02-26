"""Tests for LeagueDashPlayerClutch endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashPlayerClutch
from fastbreak.models import LeagueDashPlayerClutchResponse
from fastbreak.seasons import get_season_from_date


class TestLeagueDashPlayerClutch:
    """Tests for LeagueDashPlayerClutch endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashPlayerClutch uses sensible defaults."""
        endpoint = LeagueDashPlayerClutch()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.clutch_time == "Last 5 Minutes"
        assert endpoint.ahead_behind == "Ahead or Behind"
        assert endpoint.point_diff == 5
        assert endpoint.measure_type == "Base"
        assert endpoint.per_mode == "PerGame"

    def test_init_with_custom_season(self):
        """LeagueDashPlayerClutch accepts custom season."""
        endpoint = LeagueDashPlayerClutch(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_clutch_time(self):
        """LeagueDashPlayerClutch accepts custom clutch_time."""
        endpoint = LeagueDashPlayerClutch(clutch_time="Last 2 Minutes")

        assert endpoint.clutch_time == "Last 2 Minutes"

    def test_init_with_custom_ahead_behind(self):
        """LeagueDashPlayerClutch accepts custom ahead_behind."""
        endpoint = LeagueDashPlayerClutch(ahead_behind="Ahead or Tied")

        assert endpoint.ahead_behind == "Ahead or Tied"

    def test_init_with_custom_point_diff(self):
        """LeagueDashPlayerClutch accepts custom point_diff."""
        endpoint = LeagueDashPlayerClutch(point_diff=3)

        assert endpoint.point_diff == 3

    def test_init_with_custom_measure_type(self):
        """LeagueDashPlayerClutch accepts custom measure_type."""
        endpoint = LeagueDashPlayerClutch(measure_type="Advanced")

        assert endpoint.measure_type == "Advanced"

    def test_init_with_optional_filters(self):
        """LeagueDashPlayerClutch accepts optional filters."""
        endpoint = LeagueDashPlayerClutch(
            conference="East",
            division="Atlantic",
            location="Home",
            outcome="W",
        )

        assert endpoint.conference == "East"
        assert endpoint.division == "Atlantic"
        assert endpoint.location == "Home"
        assert endpoint.outcome == "W"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueDashPlayerClutch()

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == get_season_from_date()
        assert params["SeasonType"] == "Regular Season"
        assert params["ClutchTime"] == "Last 5 Minutes"
        assert params["AheadBehind"] == "Ahead or Behind"
        assert params["PointDiff"] == "5"
        assert params["MeasureType"] == "Base"
        assert params["PerMode"] == "PerGame"

    def test_params_with_optional_filters(self):
        """params() correctly includes optional filters."""
        endpoint = LeagueDashPlayerClutch(
            conference="West",
            division="Pacific",
        )

        params = endpoint.params()

        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"

    def test_params_empty_string_for_unset_filters(self):
        """params() uses empty string for unset optional filters."""
        endpoint = LeagueDashPlayerClutch()

        params = endpoint.params()

        assert params["Conference"] == ""
        assert params["Division"] == ""
        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""

    def test_path_is_correct(self):
        """LeagueDashPlayerClutch has correct API path."""
        endpoint = LeagueDashPlayerClutch()

        assert endpoint.path == "leaguedashplayerclutch"

    def test_response_model_is_correct(self):
        """LeagueDashPlayerClutch uses LeagueDashPlayerClutchResponse model."""
        endpoint = LeagueDashPlayerClutch()

        assert endpoint.response_model is LeagueDashPlayerClutchResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashPlayerClutch is immutable (frozen dataclass)."""
        endpoint = LeagueDashPlayerClutch()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
