"""Tests for player career by college rollup models."""

from fastbreak.models.player_career_by_college_rollup import (
    PlayerCareerByCollegeRollupResponse,
)


class TestPlayerCareerByCollegeRollupResponse:
    """Tests for PlayerCareerByCollegeRollupResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"entries": []}

        response = PlayerCareerByCollegeRollupResponse.model_validate(data)

        assert response.entries == []
