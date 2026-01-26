"""Tests for league_dash_team_shot_locations model and parsing functions."""

import pytest

from fastbreak.models.league_dash_team_shot_locations import (
    LeagueDashTeamShotLocationsResponse,
    ShotRange,
    TeamShotLocations,
    _get_result_set,
    _parse_shot_locations,
    _parse_team_row,
)


class TestGetResultSet:
    """Tests for _get_result_set function."""

    def test_returns_first_result_set_from_list(self):
        """Returns first dict from resultSets list."""
        data = {"resultSets": [{"name": "ShotLocations", "rowSet": []}]}
        result = _get_result_set(data)
        assert result == {"name": "ShotLocations", "rowSet": []}

    def test_returns_none_for_empty_list(self):
        """Returns None when resultSets list is empty."""
        data = {"resultSets": []}
        result = _get_result_set(data)
        assert result is None

    def test_returns_none_when_first_item_not_dict(self):
        """Returns None when first item in list is not a dict."""
        data = {"resultSets": ["not a dict", {"valid": "dict"}]}
        result = _get_result_set(data)
        assert result is None

    def test_returns_shot_locations_from_dict(self):
        """Returns ShotLocations key from dict resultSets."""
        shot_locations = {"name": "ShotLocations", "rowSet": [[1, "Team"]]}
        data = {"resultSets": {"ShotLocations": shot_locations}}
        result = _get_result_set(data)
        assert result == shot_locations

    def test_returns_entire_dict_when_no_shot_locations_key(self):
        """Returns entire dict when ShotLocations key not present."""
        data = {"resultSets": {"other": "data", "rowSet": []}}
        result = _get_result_set(data)
        assert result == {"other": "data", "rowSet": []}

    def test_returns_none_when_result_not_dict(self):
        """Returns None when ShotLocations value is not a dict."""
        data = {"resultSets": {"ShotLocations": "not a dict"}}
        result = _get_result_set(data)
        assert result is None

    def test_returns_empty_dict_when_resultsets_missing(self):
        """Returns empty dict when resultSets key is missing."""
        data = {"otherKey": "value"}
        result = _get_result_set(data)
        # When missing, get() returns default {} which is a dict, so it's returned
        assert result == {}

    def test_returns_none_when_resultsets_is_none(self):
        """Returns None when resultSets is None."""
        data = {"resultSets": None}
        result = _get_result_set(data)
        assert result is None

    def test_returns_none_when_resultsets_is_invalid_type(self):
        """Returns None when resultSets is neither list nor dict."""
        data = {"resultSets": "invalid"}
        result = _get_result_set(data)
        assert result is None


class TestParseTeamRow:
    """Tests for _parse_team_row function."""

    def test_parses_team_id_and_name(self):
        """Parses team_id and team_name from first two columns."""
        row = [1610612744, "Golden State Warriors"]
        result = _parse_team_row(row)
        assert result["team_id"] == 1610612744
        assert result["team_name"] == "Golden State Warriors"

    def test_parses_single_shot_range(self):
        """Parses one shot range with FGM, FGA, FG_PCT."""
        row = [1, "Team", 10.0, 20.0, 0.5]
        result = _parse_team_row(row)
        assert result["range_less_than_5ft"]["fgm"] == 10.0
        assert result["range_less_than_5ft"]["fga"] == 20.0
        assert result["range_less_than_5ft"]["fg_pct"] == 0.5

    def test_parses_multiple_shot_ranges(self):
        """Parses multiple shot ranges correctly."""
        row = [
            1,
            "Team",
            10.0,
            20.0,
            0.5,  # range_less_than_5ft
            15.0,
            30.0,
            0.5,  # range_5_9ft
            8.0,
            25.0,
            0.32,  # range_10_14ft
        ]
        result = _parse_team_row(row)

        assert result["range_less_than_5ft"]["fgm"] == 10.0
        assert result["range_less_than_5ft"]["fga"] == 20.0
        assert result["range_less_than_5ft"]["fg_pct"] == 0.5

        assert result["range_5_9ft"]["fgm"] == 15.0
        assert result["range_5_9ft"]["fga"] == 30.0
        assert result["range_5_9ft"]["fg_pct"] == 0.5

        assert result["range_10_14ft"]["fgm"] == 8.0
        assert result["range_10_14ft"]["fga"] == 25.0
        assert result["range_10_14ft"]["fg_pct"] == 0.32

    def test_parses_all_seven_ranges(self):
        """Parses all seven shot ranges from full row."""
        row = [
            1,
            "Team",
            1.0,
            2.0,
            0.1,  # range_less_than_5ft
            2.0,
            3.0,
            0.2,  # range_5_9ft
            3.0,
            4.0,
            0.3,  # range_10_14ft
            4.0,
            5.0,
            0.4,  # range_15_19ft
            5.0,
            6.0,
            0.5,  # range_20_24ft
            6.0,
            7.0,
            0.6,  # range_25_29ft
            7.0,
            8.0,
            0.7,  # range_back_court
        ]
        result = _parse_team_row(row)

        assert result["range_less_than_5ft"]["fgm"] == 1.0
        assert result["range_back_court"]["fgm"] == 7.0
        assert result["range_back_court"]["fga"] == 8.0
        assert result["range_back_court"]["fg_pct"] == 0.7

    def test_handles_null_fgm_fga_as_zero(self):
        """Null FGM and FGA values are converted to 0.0."""
        row = [1, "Team", None, None, 0.0]
        result = _parse_team_row(row)
        assert result["range_less_than_5ft"]["fgm"] == 0.0
        assert result["range_less_than_5ft"]["fga"] == 0.0

    def test_preserves_null_fg_pct(self):
        """FG_PCT can be None (not converted to 0)."""
        row = [1, "Team", 0.0, 0.0, None]
        result = _parse_team_row(row)
        assert result["range_less_than_5ft"]["fg_pct"] is None

    def test_stops_at_incomplete_range(self):
        """Stops parsing when not enough columns for complete range."""
        # Only enough for team_id, team_name, and partial range
        row = [1, "Team", 10.0, 20.0]  # Missing FG_PCT
        result = _parse_team_row(row)
        # Should only have team_id and team_name
        assert result["team_id"] == 1
        assert result["team_name"] == "Team"
        assert "range_less_than_5ft" not in result

    def test_handles_row_with_only_team_info(self):
        """Handles row with only team_id and team_name."""
        row = [1, "Team"]
        result = _parse_team_row(row)
        assert result == {"team_id": 1, "team_name": "Team"}


class TestParseShotLocations:
    """Tests for _parse_shot_locations function."""

    def test_parses_multiple_teams(self):
        """Parses multiple team rows from result set."""
        data = {
            "resultSets": [
                {
                    "rowSet": [
                        [1, "Team A", 10.0, 20.0, 0.5],
                        [2, "Team B", 15.0, 25.0, 0.6],
                    ]
                }
            ]
        }
        result = _parse_shot_locations(data)
        assert len(result) == 2
        assert result[0]["team_id"] == 1
        assert result[0]["team_name"] == "Team A"
        assert result[1]["team_id"] == 2
        assert result[1]["team_name"] == "Team B"

    def test_returns_empty_list_when_no_result_set(self):
        """Returns empty list when _get_result_set returns None."""
        data = {"resultSets": []}
        result = _parse_shot_locations(data)
        assert result == []

    def test_returns_empty_list_when_no_rows(self):
        """Returns empty list when rowSet is empty."""
        data = {"resultSets": [{"rowSet": []}]}
        result = _parse_shot_locations(data)
        assert result == []

    def test_returns_empty_list_when_rowset_missing(self):
        """Returns empty list when rowSet key is missing."""
        data = {"resultSets": [{"name": "ShotLocations"}]}
        result = _parse_shot_locations(data)
        assert result == []

    def test_parses_dict_format_result_sets(self):
        """Parses when resultSets is a dict with ShotLocations key."""
        data = {
            "resultSets": {"ShotLocations": {"rowSet": [[1, "Team", 10.0, 20.0, 0.5]]}}
        }
        result = _parse_shot_locations(data)
        assert len(result) == 1
        assert result[0]["team_id"] == 1


class TestLeagueDashTeamShotLocationsResponse:
    """Tests for the response model."""

    def test_from_result_sets_parses_teams(self):
        """Model validator parses teams from API response."""
        data = {
            "resultSets": [
                {
                    "name": "ShotLocations",
                    "rowSet": [
                        [1610612744, "Golden State Warriors", 10.0, 20.0, 0.5],
                    ],
                }
            ]
        }
        response = LeagueDashTeamShotLocationsResponse.model_validate(data)
        assert len(response.teams) == 1
        assert response.teams[0].team_id == 1610612744
        assert response.teams[0].team_name == "Golden State Warriors"

    def test_from_result_sets_passes_through_non_tabular(self):
        """Non-tabular data passes through unchanged."""
        data = {"teams": [{"team_id": 1, "team_name": "Test"}]}
        response = LeagueDashTeamShotLocationsResponse.model_validate(data)
        assert len(response.teams) == 1
        assert response.teams[0].team_id == 1

    def test_parses_shot_ranges_into_model(self):
        """Shot range data is parsed into ShotRange models."""
        data = {"resultSets": [{"rowSet": [[1, "Team", 10.0, 20.0, 0.5]]}]}
        response = LeagueDashTeamShotLocationsResponse.model_validate(data)
        team = response.teams[0]
        assert isinstance(team.range_less_than_5ft, ShotRange)
        assert team.range_less_than_5ft.fgm == 10.0
        assert team.range_less_than_5ft.fga == 20.0
        assert team.range_less_than_5ft.fg_pct == 0.5

    def test_default_shot_ranges_for_missing_data(self):
        """Missing shot ranges use default ShotRange values."""
        data = {
            "resultSets": [
                {
                    "rowSet": [[1, "Team"]]  # No shot range data
                }
            ]
        }
        response = LeagueDashTeamShotLocationsResponse.model_validate(data)
        team = response.teams[0]
        # All ranges should have defaults
        assert team.range_less_than_5ft.fgm == 0.0
        assert team.range_less_than_5ft.fga == 0.0
        assert team.range_less_than_5ft.fg_pct is None

    def test_empty_response(self):
        """Handles empty result sets."""
        data = {"resultSets": [{"rowSet": []}]}
        response = LeagueDashTeamShotLocationsResponse.model_validate(data)
        assert response.teams == []


class TestTeamShotLocations:
    """Tests for the TeamShotLocations model."""

    def test_model_creation_with_all_fields(self):
        """Model can be created with all shot range fields."""
        team = TeamShotLocations(
            team_id=1,
            team_name="Test Team",
            range_less_than_5ft=ShotRange(fgm=10, fga=20, fg_pct=0.5),
            range_5_9ft=ShotRange(fgm=5, fga=15, fg_pct=0.33),
        )
        assert team.team_id == 1
        assert team.range_less_than_5ft.fgm == 10
        assert team.range_5_9ft.fg_pct == 0.33

    def test_default_shot_ranges(self):
        """Default shot ranges are empty ShotRange objects."""
        team = TeamShotLocations(team_id=1, team_name="Test")
        assert team.range_less_than_5ft.fgm == 0.0
        assert team.range_back_court.fga == 0.0


class TestShotRange:
    """Tests for the ShotRange model."""

    def test_default_values(self):
        """Default values are correct."""
        shot_range = ShotRange()
        assert shot_range.fgm == 0.0
        assert shot_range.fga == 0.0
        assert shot_range.fg_pct is None

    def test_with_values(self):
        """Model accepts provided values."""
        shot_range = ShotRange(fgm=10.5, fga=20.0, fg_pct=0.525)
        assert shot_range.fgm == 10.5
        assert shot_range.fga == 20.0
        assert shot_range.fg_pct == 0.525
