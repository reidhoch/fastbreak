"""Tests for league dash lineups models."""

from fastbreak.models.league_dash_lineups import (
    LeagueDashLineupsResponse,
)


class TestLeagueDashLineupsResponse:
    """Tests for LeagueDashLineupsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"lineups": []}

        response = LeagueDashLineupsResponse.model_validate(data)

        assert response.lineups == []
