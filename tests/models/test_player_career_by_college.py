"""Tests for player career by college models."""

from fastbreak.models.player_career_by_college import (
    PlayerCareerByCollegeResponse,
)


class TestPlayerCareerByCollegeResponse:
    """Tests for PlayerCareerByCollegeResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}

        response = PlayerCareerByCollegeResponse.model_validate(data)

        assert response.players == []
