"""Tests for the 5 team-dashboard-twin endpoints and their models.

These mirror the existing player dashboard variants. All 5 routes were verified
to return HTTP 200 with populated result sets against the live API before
implementation (see the ``...TeamDashboard`` result-set names below).
"""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import (
    TeamDashboardByClutch,
    TeamDashboardByGameSplits,
    TeamDashboardByLastNGames,
    TeamDashboardByTeamPerformance,
    TeamDashboardByYearOverYear,
)
from fastbreak.models import (
    TeamDashboardByClutchResponse,
    TeamDashboardByGameSplitsResponse,
    TeamDashboardByLastNGamesResponse,
    TeamDashboardByTeamPerformanceResponse,
    TeamDashboardByYearOverYearResponse,
)
from fastbreak.models.team_dashboard_by_general_splits import TeamSplitStats

_ALIASES = [f.alias for f in TeamSplitStats.model_fields.values()]


def _row(group_set: str, group_value: str) -> list:
    """Build a schema-correct TeamSplitStats row (numbers after the 2 ids)."""
    values: list[object] = [group_set, group_value]
    values += [float(i) for i in range(len(_ALIASES) - 2)]
    return values


def _result_set(name: str, group_set: str, group_value: str, n: int = 1) -> dict:
    return {
        "name": name,
        "headers": _ALIASES,
        "rowSet": [_row(group_set, group_value) for _ in range(n)],
    }


class TestTeamDashboardEndpointMetadata:
    """Path / response-model / frozen checks for all 5 twins."""

    @pytest.mark.parametrize(
        ("cls", "path", "model"),
        [
            (
                TeamDashboardByClutch,
                "teamdashboardbyclutch",
                TeamDashboardByClutchResponse,
            ),
            (
                TeamDashboardByGameSplits,
                "teamdashboardbygamesplits",
                TeamDashboardByGameSplitsResponse,
            ),
            (
                TeamDashboardByLastNGames,
                "teamdashboardbylastngames",
                TeamDashboardByLastNGamesResponse,
            ),
            (
                TeamDashboardByTeamPerformance,
                "teamdashboardbyteamperformance",
                TeamDashboardByTeamPerformanceResponse,
            ),
            (
                TeamDashboardByYearOverYear,
                "teamdashboardbyyearoveryear",
                TeamDashboardByYearOverYearResponse,
            ),
        ],
    )
    def test_metadata(self, cls, path, model):
        endpoint = cls(team_id=1610612744)
        assert endpoint.path == path
        assert endpoint.response_model is model
        assert endpoint.params()["TeamID"] == "1610612744"

    def test_frozen(self):
        endpoint = TeamDashboardByClutch(team_id=1610612744)
        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


# All clutch result-set names (the validator requires every one to be present,
# matching the live API which always returns the full set).
_CLUTCH_SETS = [
    "OverallTeamDashboard",
    "Last5Min5PointTeamDashboard",
    "Last3Min5PointTeamDashboard",
    "Last1Min5PointTeamDashboard",
    "Last30Sec3PointTeamDashboard",
    "Last10Sec3PointTeamDashboard",
    "Last5MinPlusMinus5PointTeamDashboard",
    "Last3MinPlusMinus5PointTeamDashboard",
    "Last1MinPlusMinus5PointTeamDashboard",
    "Last30Sec3Point2TeamDashboard",
    "Last10Sec3Point2TeamDashboard",
]


class TestTeamDashboardByClutchResponse:
    def test_parse(self):
        raw = {"resultSets": [_result_set(name, name, name) for name in _CLUTCH_SETS]}
        resp = TeamDashboardByClutchResponse.model_validate(raw)
        assert resp.overall is not None
        assert resp.last_5_min_lte_5_pts is not None
        assert resp.last_1_min_lte_5_pts is not None
        assert resp.last_30_sec_lte_3_pts is not None
        assert resp.last_10_sec_pm_3_pts is not None


class TestTeamDashboardByGameSplitsResponse:
    def test_parse(self):
        raw = {
            "resultSets": [
                _result_set("OverallTeamDashboard", "Overall", "Overall"),
                _result_set("ByHalfTeamDashboard", "By Half", "First Half", n=2),
                _result_set("ByPeriodTeamDashboard", "By Period", "Q1", n=4),
                _result_set("ByScoreMarginTeamDashboard", "By Score Margin", "Ahead"),
                _result_set("ByActualMarginTeamDashboard", "By Actual Margin", "10-14"),
            ]
        }
        resp = TeamDashboardByGameSplitsResponse.model_validate(raw)
        assert resp.overall is not None
        assert len(resp.by_half) == 2
        assert len(resp.by_period) == 4
        assert len(resp.by_score_margin) == 1
        assert len(resp.by_actual_margin) == 1


class TestTeamDashboardByLastNGamesResponse:
    def test_parse(self):
        raw = {
            "resultSets": [
                _result_set("OverallTeamDashboard", "Overall", "Overall"),
                _result_set("Last5TeamDashboard", "Last 5", "Last 5"),
                _result_set("Last10TeamDashboard", "Last 10", "Last 10"),
                _result_set("Last15TeamDashboard", "Last 15", "Last 15"),
                _result_set("Last20TeamDashboard", "Last 20", "Last 20"),
                _result_set("GameNumberTeamDashboard", "Game Number", "1-10", n=3),
            ]
        }
        resp = TeamDashboardByLastNGamesResponse.model_validate(raw)
        assert resp.overall is not None
        assert resp.last_5 is not None
        assert resp.last_10 is not None
        assert resp.last_15 is not None
        assert resp.last_20 is not None
        assert len(resp.by_game_number) == 3


class TestTeamDashboardByTeamPerformanceResponse:
    def test_parse_including_nba_typo_result_set(self):
        raw = {
            "resultSets": [
                _result_set("OverallTeamDashboard", "Overall", "Overall"),
                _result_set(
                    "ScoreDifferentialTeamDashboard", "Score Diff", "5-10", n=2
                ),
                _result_set("PointsScoredTeamDashboard", "Points Scored", "110+"),
                # NBA API misspells this result set as "Ponts"; the model matches it.
                _result_set("PontsAgainstTeamDashboard", "Points Against", "100-110"),
            ]
        }
        resp = TeamDashboardByTeamPerformanceResponse.model_validate(raw)
        assert resp.overall is not None
        assert len(resp.by_score_differential) == 2
        assert len(resp.by_points_scored) == 1
        assert len(resp.by_points_against) == 1, (
            "the NBA 'Ponts' typo must be matched, else this stays empty"
        )


class TestTeamDashboardByYearOverYearResponse:
    def test_parse(self):
        raw = {
            "resultSets": [
                _result_set("OverallTeamDashboard", "Overall", "Overall"),
                _result_set("ByYearTeamDashboard", "By Year", "2024-25", n=5),
            ]
        }
        resp = TeamDashboardByYearOverYearResponse.model_validate(raw)
        assert resp.overall is not None
        assert len(resp.by_year) == 5
