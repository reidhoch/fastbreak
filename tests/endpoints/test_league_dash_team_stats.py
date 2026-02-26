"""Tests for LeagueDashTeamStats endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashTeamStats
from fastbreak.models import LeagueDashTeamStatsResponse
from fastbreak.seasons import get_season_from_date


class TestLeagueDashTeamStats:
    """Tests for LeagueDashTeamStats endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashTeamStats uses sensible defaults."""
        endpoint = LeagueDashTeamStats()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_init_with_custom_season(self):
        """LeagueDashTeamStats accepts custom season."""
        endpoint = LeagueDashTeamStats(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_per_mode(self):
        """LeagueDashTeamStats accepts custom per_mode."""
        endpoint = LeagueDashTeamStats(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_custom_measure_type(self):
        """LeagueDashTeamStats accepts custom measure_type."""
        endpoint = LeagueDashTeamStats(measure_type="Advanced")

        assert endpoint.measure_type == "Advanced"

    def test_init_with_optional_filters(self):
        """LeagueDashTeamStats accepts optional filters."""
        endpoint = LeagueDashTeamStats(
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
        endpoint = LeagueDashTeamStats()

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == get_season_from_date()
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"

    def test_params_with_optional_filters(self):
        """params() correctly includes optional filters."""
        endpoint = LeagueDashTeamStats(
            conference="West",
            division="Pacific",
        )

        params = endpoint.params()

        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"

    def test_params_empty_string_for_unset_filters(self):
        """params() uses empty string for unset optional filters."""
        endpoint = LeagueDashTeamStats()

        params = endpoint.params()

        assert params["Conference"] == ""
        assert params["Division"] == ""
        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""

    def test_path_is_correct(self):
        """LeagueDashTeamStats has correct API path."""
        endpoint = LeagueDashTeamStats()

        assert endpoint.path == "leaguedashteamstats"

    def test_response_model_is_correct(self):
        """LeagueDashTeamStats uses LeagueDashTeamStatsResponse model."""
        endpoint = LeagueDashTeamStats()

        assert endpoint.response_model is LeagueDashTeamStatsResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashTeamStats is immutable (frozen dataclass)."""
        endpoint = LeagueDashTeamStats()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
