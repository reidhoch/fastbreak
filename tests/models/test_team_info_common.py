"""Tests for team info common models."""

from fastbreak.models.team_info_common import (
    TeamInfoCommonResponse,
)


class TestTeamInfoCommonResponse:
    """Tests for TeamInfoCommonResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "team_info": None,
            "available_seasons": [],
        }

        response = TeamInfoCommonResponse.model_validate(data)

        assert response.team_info is None
        assert response.available_seasons == []
