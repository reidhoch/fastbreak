"""Tests for shot chart lineup detail models."""

from fastbreak.models.shot_chart_lineup_detail import (
    ShotChartLineupDetailResponse,
)


class TestShotChartLineupDetailResponse:
    """Tests for ShotChartLineupDetailResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"shots": [], "league_averages": []}

        response = ShotChartLineupDetailResponse.model_validate(data)

        assert response.shots == []
        assert response.league_averages == []
