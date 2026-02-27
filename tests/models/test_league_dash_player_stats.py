"""Tests for LeagueDashPlayerStats models."""

import pytest

from fastbreak.models.league_dash_player_stats import (
    LeagueDashPlayerStatsResponse,
    LeagueDashPlayerStatsRow,
)

_REQUIRED_ROW: dict = {
    "PLAYER_ID": 2544,
    "PLAYER_NAME": "LeBron James",
    "TEAM_ID": 1610612747,
    "TEAM_ABBREVIATION": "LAL",
    "GP": 55,
    "W": 30,
    "L": 25,
    "MIN": 35.3,
    "FGM": 10.1,
    "FGA": 19.8,
    "FG3M": 2.1,
    "FG3A": 6.0,
    "FTM": 4.7,
    "FTA": 6.2,
    "OREB": 1.2,
    "DREB": 6.5,
    "REB": 7.7,
    "AST": 8.3,
    "TOV": 3.5,
    "STL": 1.3,
    "BLK": 0.5,
    "BLKA": 0.6,
    "PF": 1.7,
    "PFD": 5.1,
    "PTS": 27.0,
    "PLUS_MINUS": 4.2,
    "GP_RANK": 15,
    "W_RANK": 12,
    "L_RANK": 18,
    "W_PCT_RANK": 10,
    "MIN_RANK": 5,
    "FGM_RANK": 3,
    "FGA_RANK": 4,
    "FG_PCT_RANK": 20,
    "FG3M_RANK": 80,
    "FG3A_RANK": 75,
    "FG3_PCT_RANK": 90,
    "FTM_RANK": 10,
    "FTA_RANK": 8,
    "FT_PCT_RANK": 50,
    "OREB_RANK": 120,
    "DREB_RANK": 15,
    "REB_RANK": 25,
    "AST_RANK": 3,
    "TOV_RANK": 5,
    "STL_RANK": 30,
    "BLK_RANK": 100,
    "BLKA_RANK": 80,
    "PF_RANK": 200,
    "PFD_RANK": 6,
    "PTS_RANK": 2,
    "PLUS_MINUS_RANK": 8,
    "NBA_FANTASY_PTS_RANK": 2,
    "DD2_RANK": 3,
    "TD3_RANK": 5,
    "WNBA_FANTASY_PTS_RANK": 2,
}

_HEADERS = list(_REQUIRED_ROW.keys())


class TestLeagueDashPlayerStatsRow:
    """Tests for LeagueDashPlayerStatsRow model."""

    def test_parse_required_fields(self) -> None:
        """Parses a complete row with all required fields and rank columns."""
        row = LeagueDashPlayerStatsRow.model_validate(_REQUIRED_ROW)

        assert row.player_id == 2544
        assert row.player_name == "LeBron James"
        assert row.team_abbreviation == "LAL"
        assert row.gp == 55
        assert row.pts == pytest.approx(27.0)
        assert row.pts_rank == 2
        assert row.plus_minus_rank == 8
        assert row.wnba_fantasy_pts_rank == 2

    def test_optional_fields_default_to_none(self) -> None:
        """Optional fields (nickname, age, fantasy pts, dd2, td3) default to None."""
        row = LeagueDashPlayerStatsRow.model_validate(_REQUIRED_ROW)

        assert row.nickname is None
        assert row.age is None
        assert row.nba_fantasy_pts is None
        assert row.dd2 is None
        assert row.td3 is None
        assert row.wnba_fantasy_pts is None

    def test_optional_fields_populated(self) -> None:
        """Optional fields parse correctly when present."""
        data = {
            **_REQUIRED_ROW,
            "NICKNAME": "King James",
            "AGE": 39.0,
            "NBA_FANTASY_PTS": 58.5,
            "DD2": 28,
            "TD3": 4,
            "WNBA_FANTASY_PTS": 52.1,
            "W_PCT": 0.545,
        }

        row = LeagueDashPlayerStatsRow.model_validate(data)

        assert row.nickname == "King James"
        assert row.age == pytest.approx(39.0)
        assert row.nba_fantasy_pts == pytest.approx(58.5)
        assert row.dd2 == 28
        assert row.td3 == 4
        assert row.wnba_fantasy_pts == pytest.approx(52.1)


class TestLeagueDashPlayerStatsResponse:
    """Tests for LeagueDashPlayerStatsResponse model."""

    def test_parse_result_sets_format(self) -> None:
        """Parses tabular resultSets API response correctly."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPlayerStats",
                    "headers": _HEADERS,
                    "rowSet": [list(_REQUIRED_ROW.values())],
                }
            ]
        }

        response = LeagueDashPlayerStatsResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].player_name == "LeBron James"
        assert response.players[0].pts_rank == 2

    def test_handles_empty_result_set(self) -> None:
        """Handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPlayerStats",
                    "headers": _HEADERS,
                    "rowSet": [],
                }
            ]
        }

        response = LeagueDashPlayerStatsResponse.model_validate(data)

        assert response.players == []

    def test_handles_pre_validated_dict(self) -> None:
        """Handles already-structured dict data."""
        data = {"players": [_REQUIRED_ROW]}

        response = LeagueDashPlayerStatsResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].player_id == 2544
