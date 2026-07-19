"""Tests for LeagueDashPtDefend endpoint (player defensive tracking)."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashPtDefend
from fastbreak.models import LeagueDashPtDefendResponse


class TestLeagueDashPtDefend:
    """Tests for LeagueDashPtDefend endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashPtDefend uses sensible defaults."""
        endpoint = LeagueDashPtDefend()

        assert endpoint.league_id == "00"
        assert endpoint.season is None
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "Totals"
        assert endpoint.defense_category == "Overall"

    def test_params_include_defense_category(self):
        """DefenseCategory is a required parameter and always present."""
        params = LeagueDashPtDefend(
            season="2025-26", defense_category="3 Pointers"
        ).params()

        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"
        assert params["DefenseCategory"] == "3 Pointers"
        assert params["Season"] == "2025-26"

    def test_params_omits_season_when_none(self):
        """Season is omitted from params when not set."""
        assert "Season" not in LeagueDashPtDefend().params()

    def test_path_is_correct(self):
        """LeagueDashPtDefend has correct API path."""
        assert LeagueDashPtDefend().path == "leaguedashptdefend"

    def test_response_model_is_correct(self):
        """LeagueDashPtDefend uses correct response model."""
        assert LeagueDashPtDefend().response_model is LeagueDashPtDefendResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashPtDefend is immutable (frozen)."""
        endpoint = LeagueDashPtDefend()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestLeagueDashPtDefendResponse:
    """Tests for LeagueDashPtDefendResponse model."""

    @staticmethod
    def _headers() -> list[str]:
        return [
            "CLOSE_DEF_PERSON_ID",
            "PLAYER_NAME",
            "PLAYER_LAST_TEAM_ID",
            "PLAYER_LAST_TEAM_ABBREVIATION",
            "PLAYER_POSITION",
            "AGE",
            "GP",
            "G",
            "FREQ",
            "D_FGM",
            "D_FGA",
            "D_FG_PCT",
            "NORMAL_FG_PCT",
            "PCT_PLUSMINUS",
        ]

    @staticmethod
    def _row() -> list:
        return [
            1630700,
            "Dyson Daniels",
            1610612737,
            "ATL",
            "G",
            22.0,
            70,
            70,
            0.5,
            6.0,
            14.0,
            0.429,
            0.470,
            -0.041,
        ]

    def test_parse_tabular_response(self):
        """Response parses the LeagueDashPTDefend result set."""
        raw = {
            "resultSets": [
                {
                    "name": "LeagueDashPTDefend",
                    "headers": self._headers(),
                    "rowSet": [self._row()],
                }
            ]
        }

        response = LeagueDashPtDefendResponse.model_validate(raw)

        assert len(response.players) == 1
        p = response.players[0]
        assert p.close_def_person_id == 1630700
        assert p.player_name == "Dyson Daniels"
        assert p.d_fg_pct == pytest.approx(0.429)
        assert p.pct_plusminus == pytest.approx(-0.041)

    def test_parse_empty_result_set(self):
        """Empty rowSet yields no players."""
        raw = {
            "resultSets": [
                {
                    "name": "LeagueDashPTDefend",
                    "headers": self._headers(),
                    "rowSet": [],
                }
            ]
        }

        response = LeagueDashPtDefendResponse.model_validate(raw)

        assert response.players == []
