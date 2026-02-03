"""Tests for team dashboard by general splits models."""

from fastbreak.models.team_dashboard_by_general_splits import (
    TeamDashboardByGeneralSplitsResponse,
)


class TestTeamDashboardByGeneralSplitsResponse:
    """Tests for TeamDashboardByGeneralSplitsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "overall": None,
            "by_location": [],
            "by_wins_losses": [],
            "by_month": [],
            "by_pre_post_all_star": [],
            "by_days_rest": [],
        }

        response = TeamDashboardByGeneralSplitsResponse.model_validate(data)

        assert response.overall is None
        assert response.by_location == []
