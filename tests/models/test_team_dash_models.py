"""Tests for team dash models - non-tabular data paths."""

from fastbreak.models.team_dash_lineups import TeamDashLineupsResponse
from fastbreak.models.team_dash_pt_pass import TeamDashPtPassResponse
from fastbreak.models.team_dash_pt_reb import TeamDashPtRebResponse
from fastbreak.models.team_dash_pt_shots import TeamDashPtShotsResponse


class TestTeamDashLineupsResponse:
    """Tests for TeamDashLineupsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"lineups": []}

        response = TeamDashLineupsResponse.model_validate(data)

        assert response.lineups == []


class TestTeamDashPtPassResponse:
    """Tests for TeamDashPtPassResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"passes_made": [], "passes_received": []}

        response = TeamDashPtPassResponse.model_validate(data)

        assert response.passes_made == []
        assert response.passes_received == []


class TestTeamDashPtRebResponse:
    """Tests for TeamDashPtRebResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "overall": None,
            "by_shot_type": [],
            "by_num_contested": [],
            "by_shot_distance": [],
            "by_reb_distance": [],
        }

        response = TeamDashPtRebResponse.model_validate(data)

        assert response.overall is None
        assert response.by_shot_type == []


class TestTeamDashPtShotsResponse:
    """Tests for TeamDashPtShotsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "general_shooting": [],
            "shot_clock_shooting": [],
            "dribble_shooting": [],
            "closest_defender_shooting": [],
            "closest_defender_10ft_plus_shooting": [],
            "touch_time_shooting": [],
        }

        response = TeamDashPtShotsResponse.model_validate(data)

        assert response.general_shooting == []
