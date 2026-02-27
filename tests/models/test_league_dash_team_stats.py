"""Tests for LeagueDashTeamStats models."""

import pytest

from fastbreak.models.league_dash_team_stats import (
    LeagueDashTeamStatsResponse,
    LeagueDashTeamStatsRow,
)

_REQUIRED_ROW: dict = {
    "TEAM_ID": 1610612738,
    "TEAM_NAME": "Boston Celtics",
    "GP": 55,
    "W": 38,
    "L": 17,
    "W_PCT": 0.691,
    "MIN": 240.0,
    "FGM": 44.2,
    "FGA": 89.1,
    "FG_PCT": 0.496,
    "FG3M": 17.5,
    "FG3A": 45.3,
    "FG3_PCT": 0.386,
    "FTM": 16.0,
    "FTA": 20.4,
    "FT_PCT": 0.784,
    "OREB": 9.8,
    "DREB": 34.1,
    "REB": 43.9,
    "AST": 28.0,
    "TOV": 12.1,
    "STL": 8.3,
    "BLK": 6.0,
    "BLKA": 4.2,
    "PF": 19.5,
    "PFD": 21.3,
    "PTS": 121.9,
    "PLUS_MINUS": 8.4,
    "GP_RANK": 15,
    "W_RANK": 1,
    "L_RANK": 30,
    "W_PCT_RANK": 1,
    "MIN_RANK": 15,
    "FGM_RANK": 3,
    "FGA_RANK": 8,
    "FG_PCT_RANK": 1,
    "FG3M_RANK": 2,
    "FG3A_RANK": 3,
    "FG3_PCT_RANK": 2,
    "FTM_RANK": 18,
    "FTA_RANK": 22,
    "FT_PCT_RANK": 5,
    "OREB_RANK": 25,
    "DREB_RANK": 2,
    "REB_RANK": 5,
    "AST_RANK": 2,
    "TOV_RANK": 8,
    "STL_RANK": 3,
    "BLK_RANK": 4,
    "BLKA_RANK": 12,
    "PF_RANK": 28,
    "PFD_RANK": 20,
    "PTS_RANK": 3,
    "PLUS_MINUS_RANK": 1,
}

_HEADERS = list(_REQUIRED_ROW.keys())


class TestLeagueDashTeamStatsRow:
    """Tests for LeagueDashTeamStatsRow model."""

    def test_parse_required_fields(self) -> None:
        """Parses a complete row with all required fields and rank columns."""
        row = LeagueDashTeamStatsRow.model_validate(_REQUIRED_ROW)

        assert row.team_id == 1610612738
        assert row.team_name == "Boston Celtics"
        assert row.gp == 55
        assert row.w == 38
        assert row.losses == 17
        assert row.pts == pytest.approx(121.9)
        assert row.w_pct_rank == 1
        assert row.pts_rank == 3
        assert row.plus_minus_rank == 1

    def test_optional_fields_default_to_none(self) -> None:
        """w_pct, fg_pct, fg3_pct, ft_pct default to None when absent."""
        data = {
            k: v
            for k, v in _REQUIRED_ROW.items()
            if k not in {"W_PCT", "FG_PCT", "FG3_PCT", "FT_PCT"}
        }

        row = LeagueDashTeamStatsRow.model_validate(data)

        assert row.w_pct is None
        assert row.fg_pct is None
        assert row.fg3_pct is None
        assert row.ft_pct is None

    def test_parse_negative_plus_minus(self) -> None:
        """Handles negative plus/minus for losing teams."""
        data = {**_REQUIRED_ROW, "PLUS_MINUS": -6.1, "PLUS_MINUS_RANK": 30}

        row = LeagueDashTeamStatsRow.model_validate(data)

        assert row.plus_minus == pytest.approx(-6.1)
        assert row.plus_minus_rank == 30


class TestLeagueDashTeamStatsResponse:
    """Tests for LeagueDashTeamStatsResponse model."""

    def test_parse_result_sets_format(self) -> None:
        """Parses tabular resultSets API response correctly."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashTeamStats",
                    "headers": _HEADERS,
                    "rowSet": [list(_REQUIRED_ROW.values())],
                }
            ]
        }

        response = LeagueDashTeamStatsResponse.model_validate(data)

        assert len(response.teams) == 1
        assert response.teams[0].team_name == "Boston Celtics"
        assert response.teams[0].w_pct_rank == 1

    def test_handles_empty_result_set(self) -> None:
        """Handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashTeamStats",
                    "headers": _HEADERS,
                    "rowSet": [],
                }
            ]
        }

        response = LeagueDashTeamStatsResponse.model_validate(data)

        assert response.teams == []

    def test_handles_pre_validated_dict(self) -> None:
        """Handles already-structured dict data."""
        data = {"teams": [_REQUIRED_ROW]}

        response = LeagueDashTeamStatsResponse.model_validate(data)

        assert len(response.teams) == 1
        assert response.teams[0].team_id == 1610612738
