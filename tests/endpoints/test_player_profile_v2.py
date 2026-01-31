"""Tests for PlayerProfileV2 endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerProfileV2
from fastbreak.models import PlayerProfileV2Response


class TestPlayerProfileV2:
    """Tests for PlayerProfileV2 endpoint."""

    def test_init_with_defaults(self):
        """PlayerProfileV2 uses sensible defaults."""
        endpoint = PlayerProfileV2(player_id="2544")

        assert endpoint.player_id == "2544"
        assert endpoint.league_id == "00"
        assert endpoint.per_mode == "PerGame"

    def test_init_with_player_id(self):
        """PlayerProfileV2 accepts player_id."""
        endpoint = PlayerProfileV2(player_id="2544")

        assert endpoint.player_id == "2544"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerProfileV2(player_id="2544", per_mode="Per36")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"
        assert params["PerMode"] == "Per36"

    def test_path_is_correct(self):
        """PlayerProfileV2 has correct API path."""
        endpoint = PlayerProfileV2(player_id="2544")

        assert endpoint.path == "playerprofilev2"

    def test_response_model_is_correct(self):
        """PlayerProfileV2 uses correct response model."""
        endpoint = PlayerProfileV2(player_id="2544")

        assert endpoint.response_model is PlayerProfileV2Response

    def test_endpoint_is_frozen(self):
        """PlayerProfileV2 is immutable (frozen dataclass)."""
        endpoint = PlayerProfileV2(player_id="2544")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.player_id = "203999"  # type: ignore[misc]


class TestPlayerProfileV2Response:
    """Tests for PlayerProfileV2Response model."""

    @staticmethod
    def _make_season_headers() -> list[str]:
        """Return headers for season totals (27 columns)."""
        return [
            "PLAYER_ID",
            "SEASON_ID",
            "LEAGUE_ID",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "PLAYER_AGE",
            "GP",
            "GS",
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
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
        ]

    @staticmethod
    def _make_career_headers() -> list[str]:
        """Return headers for career totals (24 columns)."""
        return [
            "PLAYER_ID",
            "LEAGUE_ID",
            "TEAM_ID",
            "GP",
            "GS",
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
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
        ]

    @staticmethod
    def _make_rankings_headers() -> list[str]:
        """Return headers for season rankings (27 columns)."""
        return [
            "PLAYER_ID",
            "SEASON_ID",
            "LEAGUE_ID",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "PLAYER_AGE",
            "GP",
            "GS",
            "RANK_PG_MIN",
            "RANK_PG_FGM",
            "RANK_PG_FGA",
            "RANK_FG_PCT",
            "RANK_PG_FG3M",
            "RANK_PG_FG3A",
            "RANK_FG3_PCT",
            "RANK_PG_FTM",
            "RANK_PG_FTA",
            "RANK_FT_PCT",
            "RANK_PG_OREB",
            "RANK_PG_DREB",
            "RANK_PG_REB",
            "RANK_PG_AST",
            "RANK_PG_STL",
            "RANK_PG_BLK",
            "RANK_PG_TOV",
            "RANK_PG_PTS",
            "RANK_PG_EFF",
        ]

    @staticmethod
    def _make_highs_headers() -> list[str]:
        """Return headers for stat highs (11 columns)."""
        return [
            "PLAYER_ID",
            "GAME_ID",
            "GAME_DATE",
            "VS_TEAM_ID",
            "VS_TEAM_CITY",
            "VS_TEAM_NAME",
            "VS_TEAM_ABBREVIATION",
            "STAT",
            "STAT_VALUE",
            "STAT_ORDER",
            "DATE_EST",
        ]

    @staticmethod
    def _make_next_game_headers() -> list[str]:
        """Return headers for next game (12 columns)."""
        return [
            "GAME_ID",
            "GAME_DATE",
            "GAME_TIME",
            "LOCATION",
            "PLAYER_TEAM_ID",
            "PLAYER_TEAM_CITY",
            "PLAYER_TEAM_NICKNAME",
            "PLAYER_TEAM_ABBREVIATION",
            "VS_TEAM_ID",
            "VS_TEAM_CITY",
            "VS_TEAM_NICKNAME",
            "VS_TEAM_ABBREVIATION",
        ]

    @staticmethod
    def _make_season_row(
        player_id: int,
        season_id: str,
        team_abbr: str,
        pts: float,
    ) -> list:
        """Create a test row for season totals (27 values)."""
        return [
            player_id,
            season_id,
            "00",  # LEAGUE_ID
            1610612747,  # TEAM_ID
            team_abbr,
            35.0,  # PLAYER_AGE
            82,  # GP
            82,  # GS
            35.0,  # MIN
            10.0,  # FGM
            20.0,  # FGA
            0.5,  # FG_PCT
            2.0,  # FG3M
            5.0,  # FG3A
            0.4,  # FG3_PCT
            5.0,  # FTM
            6.0,  # FTA
            0.833,  # FT_PCT
            1.0,  # OREB
            7.0,  # DREB
            8.0,  # REB
            8.0,  # AST
            1.5,  # STL
            0.5,  # BLK
            3.5,  # TOV
            1.5,  # PF
            pts,  # PTS
        ]

    @staticmethod
    def _make_career_row(player_id: int, pts: float) -> list:
        """Create a test row for career totals (24 values)."""
        return [
            player_id,
            "00",  # LEAGUE_ID
            0,  # TEAM_ID
            1500,  # GP
            1500,  # GS
            36.0,  # MIN
            10.0,  # FGM
            20.0,  # FGA
            0.5,  # FG_PCT
            2.0,  # FG3M
            5.0,  # FG3A
            0.4,  # FG3_PCT
            5.0,  # FTM
            6.0,  # FTA
            0.833,  # FT_PCT
            1.0,  # OREB
            7.0,  # DREB
            8.0,  # REB
            7.5,  # AST
            1.5,  # STL
            0.7,  # BLK
            3.5,  # TOV
            1.8,  # PF
            pts,  # PTS
        ]

    @staticmethod
    def _make_rankings_row(
        player_id: int,
        season_id: str,
        pts_rank: int,
    ) -> list:
        """Create a test row for season rankings (27 values)."""
        return [
            player_id,
            season_id,
            "00",  # LEAGUE_ID
            1610612747,  # TEAM_ID
            "LAL",
            "NR",  # PLAYER_AGE (string)
            "NR",  # GP (string)
            "NR",  # GS (string)
            5,  # RANK_PG_MIN
            3,  # RANK_PG_FGM
            2,  # RANK_PG_FGA
            10,  # RANK_FG_PCT
            15,  # RANK_PG_FG3M
            12,  # RANK_PG_FG3A
            50,  # RANK_FG3_PCT
            8,  # RANK_PG_FTM
            7,  # RANK_PG_FTA
            60,  # RANK_FT_PCT
            100,  # RANK_PG_OREB
            20,  # RANK_PG_DREB
            25,  # RANK_PG_REB
            5,  # RANK_PG_AST
            30,  # RANK_PG_STL
            80,  # RANK_PG_BLK
            10,  # RANK_PG_TOV
            pts_rank,  # RANK_PG_PTS
            2,  # RANK_PG_EFF
        ]

    @staticmethod
    def _make_high_row(player_id: int, stat: str, value: int, order: int) -> list:
        """Create a test row for stat highs (11 values)."""
        return [
            player_id,
            "0021300893",  # GAME_ID
            "MAR 03 2014",  # GAME_DATE
            1610612766,  # VS_TEAM_ID
            "Charlotte",  # VS_TEAM_CITY
            "Bobcats",  # VS_TEAM_NAME
            "CHA",  # VS_TEAM_ABBREVIATION
            stat,
            value,
            order,
            "2014-03-03T00:00:00",  # DATE_EST
        ]

    @staticmethod
    def _make_next_game_row() -> list:
        """Create a test row for next game (12 values)."""
        return [
            "0022500648",  # GAME_ID
            "JAN 24 2026",  # GAME_DATE
            "08:30 PM",  # GAME_TIME
            "A",  # LOCATION
            1610612747,  # PLAYER_TEAM_ID
            "Los Angeles",  # PLAYER_TEAM_CITY
            "Lakers",  # PLAYER_TEAM_NICKNAME
            "LAL",  # PLAYER_TEAM_ABBREVIATION
            1610612742,  # VS_TEAM_ID
            "Dallas",  # VS_TEAM_CITY
            "Mavericks",  # VS_TEAM_NICKNAME
            "DAL",  # VS_TEAM_ABBREVIATION
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "SeasonTotalsRegularSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [
                        self._make_season_row(2544, "2023-24", "LAL", 25.7),
                        self._make_season_row(2544, "2022-23", "LAL", 28.9),
                    ],
                },
                {
                    "name": "CareerTotalsRegularSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [self._make_career_row(2544, 27.1)],
                },
                {
                    "name": "SeasonTotalsPostSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [self._make_season_row(2544, "2019-20", "LAL", 27.6)],
                },
                {
                    "name": "CareerTotalsPostSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [self._make_career_row(2544, 28.4)],
                },
                {
                    "name": "SeasonTotalsAllStarSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsAllStarSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonTotalsCollegeSeason",
                    "headers": [
                        "PLAYER_ID",
                        "SEASON_ID",
                        "LEAGUE_ID",
                        "ORGANIZATION_ID",
                        "SCHOOL_NAME",
                        "PLAYER_AGE",
                        "GP",
                        "GS",
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
                        "STL",
                        "BLK",
                        "TOV",
                        "PF",
                        "PTS",
                    ],
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsCollegeSeason",
                    "headers": [
                        "PLAYER_ID",
                        "LEAGUE_ID",
                        "ORGANIZATION_ID",
                        "GP",
                        "GS",
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
                        "STL",
                        "BLK",
                        "TOV",
                        "PF",
                        "PTS",
                    ],
                    "rowSet": [],
                },
                {
                    "name": "SeasonTotalsPreseason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsPreseason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonRankingsRegularSeason",
                    "headers": self._make_rankings_headers(),
                    "rowSet": [self._make_rankings_row(2544, "2023-24", 3)],
                },
                {
                    "name": "SeasonRankingsPostSeason",
                    "headers": self._make_rankings_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonHighs",
                    "headers": self._make_highs_headers(),
                    "rowSet": [self._make_high_row(2544, "PTS", 36, 1)],
                },
                {
                    "name": "CareerHighs",
                    "headers": self._make_highs_headers(),
                    "rowSet": [self._make_high_row(2544, "PTS", 61, 1)],
                },
                {
                    "name": "NextGame",
                    "headers": self._make_next_game_headers(),
                    "rowSet": [self._make_next_game_row()],
                },
            ]
        }

        response = PlayerProfileV2Response.model_validate(raw_response)

        # Check season totals
        assert len(response.season_totals_regular_season) == 2
        assert response.season_totals_regular_season[0].season_id == "2023-24"
        assert response.season_totals_regular_season[0].pts == 25.7

        # Check career totals
        assert response.career_totals_regular_season is not None
        assert response.career_totals_regular_season.pts == 27.1

        # Check post season
        assert len(response.season_totals_post_season) == 1
        assert response.career_totals_post_season is not None

        # Check rankings
        assert len(response.season_rankings_regular_season) == 1
        assert response.season_rankings_regular_season[0].rank_pg_pts == 3

        # Check highs
        assert len(response.season_highs) == 1
        assert response.season_highs[0].stat == "PTS"
        assert response.season_highs[0].stat_value == 36
        assert len(response.career_highs) == 1
        assert response.career_highs[0].stat_value == 61

        # Check next game
        assert response.next_game is not None
        assert response.next_game.game_id == "0022500648"
        assert response.next_game.vs_team_abbreviation == "DAL"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "SeasonTotalsRegularSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsRegularSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonTotalsPostSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsPostSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonTotalsAllStarSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsAllStarSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonTotalsCollegeSeason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsCollegeSeason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonTotalsPreseason",
                    "headers": self._make_season_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerTotalsPreseason",
                    "headers": self._make_career_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonRankingsRegularSeason",
                    "headers": self._make_rankings_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonRankingsPostSeason",
                    "headers": self._make_rankings_headers(),
                    "rowSet": [],
                },
                {
                    "name": "SeasonHighs",
                    "headers": self._make_highs_headers(),
                    "rowSet": [],
                },
                {
                    "name": "CareerHighs",
                    "headers": self._make_highs_headers(),
                    "rowSet": [],
                },
                {
                    "name": "NextGame",
                    "headers": self._make_next_game_headers(),
                    "rowSet": [],
                },
            ]
        }

        response = PlayerProfileV2Response.model_validate(raw_response)

        assert response.season_totals_regular_season == []
        assert response.career_totals_regular_season is None
        assert response.next_game is None
