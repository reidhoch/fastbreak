"""Tests for PlayerFantasyProfile endpoint.

Schema captured from the live API (2024-25): 5 result sets — Overall, Location,
LastNGames, DaysRestModified (which carries an extra SEASON_YEAR column), and
Opponent. Rows carry fantasy columns (DD2, TD3, FAN_DUEL_PTS, NBA_FANTASY_PTS)
and, unlike the dashboard splits, no *_RANK columns.
"""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerFantasyProfile
from fastbreak.models import PlayerFantasyProfileResponse

_BASE_HEADERS = [
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
    "DD2",
    "TD3",
    "FAN_DUEL_PTS",
    "NBA_FANTASY_PTS",
]


def _base_row(group_set: str, group_value: str) -> list:
    # Two id strings, then numbers for the remaining 30 columns.
    return [group_set, group_value, *[float(i) for i in range(len(_BASE_HEADERS) - 2)]]


def _days_rest_headers() -> list[str]:
    # DaysRestModified inserts SEASON_YEAR after GROUP_VALUE.
    return [*_BASE_HEADERS[:2], "SEASON_YEAR", *_BASE_HEADERS[2:]]


def _days_rest_row(group_value: str) -> list:
    return [
        "Days Rest",
        group_value,
        "2024-25",
        *[float(i) for i in range(len(_BASE_HEADERS) - 2)],
    ]


class TestPlayerFantasyProfile:
    def test_init_defaults(self):
        endpoint = PlayerFantasyProfile(player_id=201939)
        assert endpoint.player_id == 201939
        assert endpoint.path == "playerfantasyprofile"
        assert endpoint.params()["PlayerID"] == "201939"

    def test_response_model(self):
        assert (
            PlayerFantasyProfile(player_id=201939).response_model
            is PlayerFantasyProfileResponse
        )

    def test_frozen(self):
        endpoint = PlayerFantasyProfile(player_id=201939)
        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerFantasyProfileResponse:
    def test_parse_all_result_sets(self):
        raw = {
            "resultSets": [
                {
                    "name": "Overall",
                    "headers": _BASE_HEADERS,
                    "rowSet": [_base_row("Overall", "2024-25")],
                },
                {
                    "name": "Location",
                    "headers": _BASE_HEADERS,
                    "rowSet": [
                        _base_row("Location", "Home"),
                        _base_row("Location", "Road"),
                    ],
                },
                {
                    "name": "LastNGames",
                    "headers": _BASE_HEADERS,
                    "rowSet": [_base_row("Last N Games", "Last 5 Games")],
                },
                {
                    "name": "DaysRestModified",
                    "headers": _days_rest_headers(),
                    "rowSet": [_days_rest_row("0 Days Rest")],
                },
                {
                    "name": "Opponent",
                    "headers": _BASE_HEADERS,
                    "rowSet": [_base_row("vs. Opponent", "Atlanta Hawks")],
                },
            ]
        }

        resp = PlayerFantasyProfileResponse.model_validate(raw)

        assert resp.overall is not None
        assert resp.overall.group_value == "2024-25"
        assert len(resp.by_location) == 2
        assert len(resp.last_n_games) == 1
        assert len(resp.by_days_rest) == 1
        assert len(resp.by_opponent) == 1
        # Fantasy-specific columns are captured.
        assert resp.overall.fan_duel_pts is not None
        assert resp.overall.nba_fantasy_pts is not None
        # The DaysRest split's extra SEASON_YEAR column is captured, not fatal.
        assert resp.by_days_rest[0].season_year == "2024-25"
        # And the base sets simply have season_year = None.
        assert resp.overall.season_year is None

    def test_parse_empty(self):
        raw = {
            "resultSets": [
                {"name": "Overall", "headers": _BASE_HEADERS, "rowSet": []},
                {"name": "Location", "headers": _BASE_HEADERS, "rowSet": []},
                {"name": "LastNGames", "headers": _BASE_HEADERS, "rowSet": []},
                {
                    "name": "DaysRestModified",
                    "headers": _days_rest_headers(),
                    "rowSet": [],
                },
                {"name": "Opponent", "headers": _BASE_HEADERS, "rowSet": []},
            ]
        }

        resp = PlayerFantasyProfileResponse.model_validate(raw)

        assert resp.overall is None
        assert resp.by_location == []
        assert resp.by_opponent == []
