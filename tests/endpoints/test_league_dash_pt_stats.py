"""Tests for LeagueDashPtStats endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashPtStats
from fastbreak.models import LeagueDashPtStatsResponse
from fastbreak.utils import get_season_from_date


class TestLeagueDashPtStats:
    """Tests for LeagueDashPtStats endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashPtStats uses sensible defaults."""
        endpoint = LeagueDashPtStats(team_id=1610612747)

        assert endpoint.pt_measure_type == "Drives"
        assert endpoint.player_or_team == "Team"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.league_id == "00"

    def test_init_with_custom_params(self):
        """LeagueDashPtStats accepts custom parameters."""
        endpoint = LeagueDashPtStats(
            team_id=1610612747,
            pt_measure_type="Possessions",
            player_or_team="Player",
            season="2023-24",
            season_type="Playoffs",
        )

        assert endpoint.pt_measure_type == "Possessions"
        assert endpoint.player_or_team == "Player"
        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"

    def test_params_with_defaults_only(self):
        """params() returns required parameters with defaults."""
        endpoint = LeagueDashPtStats(team_id=1610612747)

        params = endpoint.params()

        assert params["PtMeasureType"] == "Drives"
        assert params["PlayerOrTeam"] == "Team"
        assert params["Season"] == get_season_from_date()
        assert params["TeamID"] == "1610612747"
        assert "Outcome" not in params
        assert "Location" not in params

    def test_params_with_all_optional_filters(self):
        """params() includes all optional filters when set."""
        endpoint = LeagueDashPtStats(
            team_id=1610612747,
            outcome="W",
            location="Home",
            date_from="01/01/2025",
            date_to="01/31/2025",
            vs_conference="East",
            vs_division="Atlantic",
            game_scope="Yesterday",
            player_experience="Rookie",
            player_position="G",
            starter_bench="Starter",
            conference="West",
            division="Pacific",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["DateFrom"] == "01/01/2025"
        assert params["DateTo"] == "01/31/2025"
        assert params["VsConference"] == "East"
        assert params["VsDivision"] == "Atlantic"
        assert params["GameScope"] == "Yesterday"
        assert params["PlayerExperience"] == "Rookie"
        assert params["PlayerPosition"] == "G"
        assert params["StarterBench"] == "Starter"
        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"

    def test_params_with_partial_optional_filters(self):
        """params() includes only set optional filters."""
        endpoint = LeagueDashPtStats(
            team_id=1610612747,
            outcome="L",
            player_experience="Veteran",
        )

        params = endpoint.params()

        assert params["Outcome"] == "L"
        assert params["PlayerExperience"] == "Veteran"
        assert "Location" not in params
        assert "VsConference" not in params

    def test_path_is_correct(self):
        """LeagueDashPtStats has correct API path."""
        endpoint = LeagueDashPtStats(team_id=1610612747)

        assert endpoint.path == "leaguedashptstats"

    def test_response_model_is_correct(self):
        """LeagueDashPtStats uses LeagueDashPtStatsResponse model."""
        endpoint = LeagueDashPtStats(team_id=1610612747)

        assert endpoint.response_model is LeagueDashPtStatsResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashPtStats is immutable (frozen dataclass)."""
        endpoint = LeagueDashPtStats(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = 1610612738  # type: ignore[misc]
