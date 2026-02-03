"""Tests for team dashboard by shooting splits models."""

from fastbreak.models.team_dashboard_by_shooting_splits import (
    TeamDashboardByShootingSplitsResponse,
)


class TestTeamDashboardByShootingSplitsResponse:
    """Tests for TeamDashboardByShootingSplitsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "overall": None,
            "by_shot_distance_5ft": [],
            "by_shot_distance_8ft": [],
            "by_shot_area": [],
            "by_assisted": [],
            "by_shot_type": [],
            "assisted_by": [],
        }

        response = TeamDashboardByShootingSplitsResponse.model_validate(data)

        assert response.overall is None
        assert response.by_shot_distance_5ft == []
        assert response.by_shot_area == []
