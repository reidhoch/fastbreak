"""Tests for LeagueHustleStatsPlayer endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueHustleStatsPlayer
from fastbreak.models import LeagueHustleStatsPlayerResponse
from fastbreak.utils import get_season_from_date


class TestLeagueHustleStatsPlayer:
    """Tests for LeagueHustleStatsPlayer endpoint."""

    def test_init_with_defaults(self):
        """LeagueHustleStatsPlayer uses sensible defaults."""
        endpoint = LeagueHustleStatsPlayer()

        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.league_id is None

    def test_init_with_custom_season(self):
        """LeagueHustleStatsPlayer accepts custom season."""
        endpoint = LeagueHustleStatsPlayer(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_totals_mode(self):
        """LeagueHustleStatsPlayer accepts Totals mode."""
        endpoint = LeagueHustleStatsPlayer(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_playoffs(self):
        """LeagueHustleStatsPlayer accepts Playoffs season type."""
        endpoint = LeagueHustleStatsPlayer(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueHustleStatsPlayer(
            season="2024-25",
            season_type="Regular Season",
            per_mode="PerGame",
        )

        params = endpoint.params()

        assert params == {
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
        }

    def test_params_includes_league_id(self):
        """params() includes league_id when set."""
        endpoint = LeagueHustleStatsPlayer(league_id="00")

        params = endpoint.params()

        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """LeagueHustleStatsPlayer has correct API path."""
        endpoint = LeagueHustleStatsPlayer()

        assert endpoint.path == "leaguehustlestatsplayer"

    def test_response_model_is_correct(self):
        """LeagueHustleStatsPlayer uses LeagueHustleStatsPlayerResponse model."""
        endpoint = LeagueHustleStatsPlayer()

        assert endpoint.response_model is LeagueHustleStatsPlayerResponse

    def test_endpoint_is_frozen(self):
        """LeagueHustleStatsPlayer is immutable (frozen dataclass)."""
        endpoint = LeagueHustleStatsPlayer()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestLeagueHustleStatsPlayerResponse:
    """Tests for LeagueHustleStatsPlayerResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HustleStatsPlayer",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "AGE",
                        "G",
                        "MIN",
                        "CONTESTED_SHOTS",
                        "CONTESTED_SHOTS_2PT",
                        "CONTESTED_SHOTS_3PT",
                        "DEFLECTIONS",
                        "CHARGES_DRAWN",
                        "SCREEN_ASSISTS",
                        "SCREEN_AST_PTS",
                        "OFF_LOOSE_BALLS_RECOVERED",
                        "DEF_LOOSE_BALLS_RECOVERED",
                        "LOOSE_BALLS_RECOVERED",
                        "PCT_LOOSE_BALLS_RECOVERED_OFF",
                        "PCT_LOOSE_BALLS_RECOVERED_DEF",
                        "OFF_BOXOUTS",
                        "DEF_BOXOUTS",
                        "BOX_OUTS",
                        "BOX_OUT_PLAYER_TEAM_REBS",
                        "BOX_OUT_PLAYER_REBS",
                        "PCT_BOX_OUTS_OFF",
                        "PCT_BOX_OUTS_DEF",
                        "PCT_BOX_OUTS_TEAM_REB",
                        "PCT_BOX_OUTS_REB",
                    ],
                    "rowSet": [
                        [
                            1630639,
                            "A.J. Lawson",
                            1610612761,
                            "TOR",
                            24.0,
                            24,
                            20.2,
                            2.04,
                            1.17,
                            0.88,
                            1.08,
                            0.0,
                            0.33,
                            0.75,
                            0.08,
                            0.21,
                            0.29,
                            0.286,
                            0.714,
                            0.0,
                            0.21,
                            0.21,
                            0.21,
                            0.13,
                            0.0,
                            1.0,
                            1.0,
                            0.6,
                        ],
                    ],
                },
            ]
        }

        response = LeagueHustleStatsPlayerResponse.model_validate(raw_response)

        assert len(response.players) == 1

        player = response.players[0]
        assert player.player_name == "A.J. Lawson"
        assert player.team_abbreviation == "TOR"
        assert player.g == 24
        assert player.contested_shots == 2.04
        assert player.deflections == 1.08
        assert player.loose_balls_recovered == 0.29

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HustleStatsPlayer",
                    "headers": ["PLAYER_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = LeagueHustleStatsPlayerResponse.model_validate(raw_response)

        assert response.players == []
