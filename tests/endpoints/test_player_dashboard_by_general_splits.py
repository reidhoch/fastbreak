"""Tests for PlayerDashboardByGeneralSplits endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByGeneralSplits
from fastbreak.models import PlayerDashboardByGeneralSplitsResponse
from fastbreak.seasons import get_season_from_date


class TestPlayerDashboardByGeneralSplits:
    """Tests for PlayerDashboardByGeneralSplits endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByGeneralSplits uses sensible defaults."""
        endpoint = PlayerDashboardByGeneralSplits(player_id=2544)

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        # Always-sent params have default 0
        assert endpoint.po_round == 0
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.period == 0
        assert endpoint.last_n_games == 0
        assert endpoint.ist_round is None

    def test_init_with_player_id(self):
        """PlayerDashboardByGeneralSplits accepts player_id."""
        endpoint = PlayerDashboardByGeneralSplits(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashboardByGeneralSplits accepts optional filters."""
        endpoint = PlayerDashboardByGeneralSplits(
            player_id=203999,
            season="2023-24",
            last_n_games=10,
            outcome="W",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.last_n_games == 10
        assert endpoint.outcome == "W"

    def test_params_with_required_only(self):
        """params() returns required and always-sent parameters."""
        endpoint = PlayerDashboardByGeneralSplits(player_id=203999)

        params = endpoint.params()

        assert params == {
            "PlayerID": "203999",
            "LeagueID": "00",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "PORound": "0",
            "Month": "0",
            "OpponentTeamID": "0",
            "Period": "0",
            "LastNGames": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerDashboardByGeneralSplits(
            player_id=203999,
            last_n_games=10,
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["LastNGames"] == "10"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_path_is_correct(self):
        """PlayerDashboardByGeneralSplits has correct API path."""
        endpoint = PlayerDashboardByGeneralSplits(player_id=2544)

        assert endpoint.path == "playerdashboardbygeneralsplits"

    def test_response_model_is_correct(self):
        """PlayerDashboardByGeneralSplits uses correct response model."""
        endpoint = PlayerDashboardByGeneralSplits(player_id=2544)

        assert endpoint.response_model is PlayerDashboardByGeneralSplitsResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByGeneralSplits is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByGeneralSplits(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashboardByGeneralSplitsResponse:
    """Tests for PlayerDashboardByGeneralSplitsResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return the 63 headers for split stats."""
        return [
            "GROUP_SET",
            "GROUP_VALUE",
            "GP",
            "W",
            "L",
            "W_PCT",
            "MIN",
            "FGM",
            "FGA",
            "FG_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
            "FTM",
            "FTA",
            "FT_PCT",
            "OREB",
            "DREB",
            "REB",
            "AST",
            "TOV",
            "STL",
            "BLK",
            "BLKA",
            "PF",
            "PFD",
            "PTS",
            "PLUS_MINUS",
            "NBA_FANTASY_PTS",
            "DD2",
            "TD3",
            "WNBA_FANTASY_PTS",
            "GP_RANK",
            "W_RANK",
            "L_RANK",
            "W_PCT_RANK",
            "MIN_RANK",
            "FGM_RANK",
            "FGA_RANK",
            "FG_PCT_RANK",
            "FG3M_RANK",
            "FG3A_RANK",
            "FG3_PCT_RANK",
            "FTM_RANK",
            "FTA_RANK",
            "FT_PCT_RANK",
            "OREB_RANK",
            "DREB_RANK",
            "REB_RANK",
            "AST_RANK",
            "TOV_RANK",
            "STL_RANK",
            "BLK_RANK",
            "BLKA_RANK",
            "PF_RANK",
            "PFD_RANK",
            "PTS_RANK",
            "PLUS_MINUS_RANK",
            "NBA_FANTASY_PTS_RANK",
            "DD2_RANK",
            "TD3_RANK",
            "WNBA_FANTASY_PTS_RANK",
            "TEAM_COUNT",
        ]

    @staticmethod
    def _make_row(group_set: str, group_value: str, pts: float) -> list:
        """Create a test row with specified values."""
        return [
            group_set,
            group_value,
            10,
            6,
            4,
            0.6,
            35.5,  # GP, W, L, W_PCT, MIN
            11.0,
            19.5,
            0.564,
            2.0,
            4.5,
            0.444,  # FG stats
            5.5,
            7.0,
            0.786,  # FT stats
            2.5,
            9.0,
            11.5,  # REB stats
            9.5,
            3.5,
            2.0,
            0.5,
            1.0,
            2.0,
            6.5,
            pts,  # Other stats
            10.0,
            60.0,
            8,
            5,
            55.0,  # PLUS_MINUS, fantasy, DD2, TD3
            *[1] * 31,  # All rank columns = 1
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers,
                    "rowSet": [self._make_row("Overall", "2024-25", 29.5)],
                },
                {
                    "name": "LocationPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Location", "Home", 32.0),
                        self._make_row("Location", "Road", 27.0),
                    ],
                },
                {
                    "name": "WinsLossesPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Wins/Losses", "Wins", 26.0),
                        self._make_row("Wins/Losses", "Losses", 35.0),
                    ],
                },
                {
                    "name": "MonthPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Month", "October", 28.0),
                        self._make_row("Month", "November", 31.0),
                    ],
                },
                {
                    "name": "PrePostAllStarPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Pre/Post All-Star", "Pre All-Star", 30.0),
                    ],
                },
                {
                    "name": "StartingPosition",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Starting Position", "Starters", 29.5),
                    ],
                },
                {
                    "name": "DaysRestPlayerDashboard",
                    "headers": headers,
                    "rowSet": [
                        self._make_row("Days Rest", "0 Days Rest", 25.0),
                        self._make_row("Days Rest", "1 Days Rest", 28.0),
                        self._make_row("Days Rest", "2 Days Rest", 32.0),
                        self._make_row("Days Rest", "3+ Days Rest", 35.0),
                    ],
                },
            ]
        }

        response = PlayerDashboardByGeneralSplitsResponse.model_validate(raw_response)

        # Check overall
        assert response.overall is not None
        assert response.overall.pts == 29.5

        # Check by_location
        assert len(response.by_location) == 2
        assert response.by_location[0].group_value == "Home"
        assert response.by_location[0].pts == 32.0
        assert response.by_location[1].group_value == "Road"

        # Check by_wins_losses
        assert len(response.by_wins_losses) == 2
        assert response.by_wins_losses[0].group_value == "Wins"
        assert response.by_wins_losses[1].group_value == "Losses"

        # Check by_month
        assert len(response.by_month) == 2
        assert response.by_month[0].group_value == "October"

        # Check by_pre_post_all_star
        assert len(response.by_pre_post_all_star) == 1
        assert response.by_pre_post_all_star[0].group_value == "Pre All-Star"

        # Check by_starting_position
        assert len(response.by_starting_position) == 1
        assert response.by_starting_position[0].group_value == "Starters"

        # Check by_days_rest
        assert len(response.by_days_rest) == 4
        assert response.by_days_rest[0].group_value == "0 Days Rest"
        assert response.by_days_rest[3].group_value == "3+ Days Rest"
        assert response.by_days_rest[3].pts == 35.0

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {"name": "OverallPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "LocationPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "WinsLossesPlayerDashboard", "headers": headers, "rowSet": []},
                {"name": "MonthPlayerDashboard", "headers": headers, "rowSet": []},
                {
                    "name": "PrePostAllStarPlayerDashboard",
                    "headers": headers,
                    "rowSet": [],
                },
                {"name": "StartingPosition", "headers": headers, "rowSet": []},
                {"name": "DaysRestPlayerDashboard", "headers": headers, "rowSet": []},
            ]
        }

        response = PlayerDashboardByGeneralSplitsResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.by_location == []
        assert response.by_wins_losses == []
        assert response.by_month == []
        assert response.by_pre_post_all_star == []
        assert response.by_starting_position == []
        assert response.by_days_rest == []
