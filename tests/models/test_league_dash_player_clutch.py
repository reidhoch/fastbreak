"""Tests for LeagueDashPlayerClutch models."""

import pytest

from fastbreak.models.league_dash_player_clutch import (
    LeagueDashPlayerClutchResponse,
    LeagueDashPlayerClutchRow,
)

_REQUIRED_ROW: dict = {
    "PLAYER_ID": 201142,
    "PLAYER_NAME": "Kevin Durant",
    "TEAM_ID": 1610612756,
    "TEAM_ABBREVIATION": "PHX",
    "GP": 42,
    "W": 22,
    "L": 20,
    "MIN": 8.2,
    "FGM": 3.8,
    "FGA": 7.5,
    "FG3M": 0.9,
    "FG3A": 2.1,
    "FTM": 2.5,
    "FTA": 2.9,
    "OREB": 0.4,
    "DREB": 2.1,
    "REB": 2.5,
    "AST": 2.0,
    "TOV": 0.8,
    "STL": 0.6,
    "BLK": 0.4,
    "BLKA": 0.2,
    "PF": 0.9,
    "PFD": 2.1,
    "PTS": 11.0,
    "PLUS_MINUS": 3.1,
    "GP_RANK": 20,
    "W_RANK": 15,
    "L_RANK": 16,
    "W_PCT_RANK": 12,
    "MIN_RANK": 10,
    "FGM_RANK": 5,
    "FGA_RANK": 8,
    "FG_PCT_RANK": 3,
    "FG3M_RANK": 40,
    "FG3A_RANK": 35,
    "FG3_PCT_RANK": 25,
    "FTM_RANK": 6,
    "FTA_RANK": 7,
    "FT_PCT_RANK": 15,
    "OREB_RANK": 80,
    "DREB_RANK": 20,
    "REB_RANK": 25,
    "AST_RANK": 18,
    "TOV_RANK": 30,
    "STL_RANK": 22,
    "BLK_RANK": 35,
    "BLKA_RANK": 60,
    "PF_RANK": 90,
    "PFD_RANK": 8,
    "PTS_RANK": 4,
    "PLUS_MINUS_RANK": 6,
    "NBA_FANTASY_PTS_RANK": 5,
    "DD2_RANK": 10,
    "TD3_RANK": 20,
    "WNBA_FANTASY_PTS_RANK": 5,
}

_HEADERS = list(_REQUIRED_ROW.keys())


class TestLeagueDashPlayerClutchRow:
    """Tests for LeagueDashPlayerClutchRow model."""

    def test_parse_required_fields(self) -> None:
        """Parses a complete row with all required fields and rank columns."""
        row = LeagueDashPlayerClutchRow.model_validate(_REQUIRED_ROW)

        assert row.player_id == 201142
        assert row.player_name == "Kevin Durant"
        assert row.team_abbreviation == "PHX"
        assert row.gp == 42
        assert row.pts == pytest.approx(11.0)
        assert row.pts_rank == 4
        assert row.plus_minus_rank == 6
        assert row.wnba_fantasy_pts_rank == 5

    def test_optional_fields_default_to_none(self) -> None:
        """Optional fields (group_set, nickname, age, fantasy pts, dd2, td3) default to None."""
        row = LeagueDashPlayerClutchRow.model_validate(_REQUIRED_ROW)

        assert row.group_set is None
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
            "GROUP_SET": "Clutch",
            "NICKNAME": "KD",
            "AGE": 35.0,
            "NBA_FANTASY_PTS": 32.4,
            "DD2": 5,
            "TD3": 0,
            "WNBA_FANTASY_PTS": 29.1,
            "W_PCT": 0.524,
        }

        row = LeagueDashPlayerClutchRow.model_validate(data)

        assert row.group_set == "Clutch"
        assert row.nickname == "KD"
        assert row.age == pytest.approx(35.0)
        assert row.nba_fantasy_pts == pytest.approx(32.4)
        assert row.dd2 == 5
        assert row.td3 == 0
        assert row.wnba_fantasy_pts == pytest.approx(29.1)


class TestLeagueDashPlayerClutchResponse:
    """Tests for LeagueDashPlayerClutchResponse model."""

    def test_parse_result_sets_format(self) -> None:
        """Parses tabular resultSets API response correctly."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPlayerClutch",
                    "headers": _HEADERS,
                    "rowSet": [list(_REQUIRED_ROW.values())],
                }
            ]
        }

        response = LeagueDashPlayerClutchResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].player_name == "Kevin Durant"
        assert response.players[0].pts_rank == 4

    def test_handles_empty_result_set(self) -> None:
        """Handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueDashPlayerClutch",
                    "headers": _HEADERS,
                    "rowSet": [],
                }
            ]
        }

        response = LeagueDashPlayerClutchResponse.model_validate(data)

        assert response.players == []

    def test_handles_pre_validated_dict(self) -> None:
        """Handles already-structured dict data."""
        data = {"players": [_REQUIRED_ROW]}

        response = LeagueDashPlayerClutchResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].player_id == 201142
