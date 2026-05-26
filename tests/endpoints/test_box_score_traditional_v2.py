"""Tests for BoxScoreTraditionalV2 endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import BoxScoreTraditionalV2
from fastbreak.models import BoxScoreTraditionalV2Response


_PLAYER_HEADERS = [
    "GAME_ID",
    "TEAM_ID",
    "TEAM_ABBREVIATION",
    "TEAM_CITY",
    "PLAYER_ID",
    "PLAYER_NAME",
    "NICKNAME",
    "START_POSITION",
    "COMMENT",
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
    "TO",
    "PF",
    "PTS",
    "PLUS_MINUS",
]


def _player_row(
    *,
    player_id: int,
    name: str,
    start_position: str,
    minutes: str = "20:00",
    pts: int = 10,
) -> list[object]:
    """Build a PlayerStats row matching _PLAYER_HEADERS."""
    return [
        "0022400123",
        1610612753,
        "ORL",
        "Orlando",
        player_id,
        name,
        name.split()[0],
        start_position,
        "",
        minutes,
        4,
        8,
        0.5,
        1,
        3,
        0.333,
        1,
        2,
        0.5,
        1,
        4,
        5,
        2,
        1,
        0,
        1,
        2,
        pts,
        -3.0,
    ]


class TestBoxScoreTraditionalV2:
    """Tests for BoxScoreTraditionalV2 endpoint."""

    def test_init_with_game_id(self):
        """BoxScoreTraditionalV2 requires game_id."""
        endpoint = BoxScoreTraditionalV2(game_id="0022400123")

        assert endpoint.game_id == "0022400123"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = BoxScoreTraditionalV2(game_id="0022400123")

        assert endpoint.params() == {"GameID": "0022400123"}

    def test_path_is_correct(self):
        """BoxScoreTraditionalV2 has correct API path."""
        endpoint = BoxScoreTraditionalV2(game_id="0022400123")

        assert endpoint.path == "boxscoretraditionalv2"

    def test_response_model_is_correct(self):
        """BoxScoreTraditionalV2 uses BoxScoreTraditionalV2Response model."""
        endpoint = BoxScoreTraditionalV2(game_id="0022400123")

        assert endpoint.response_model is BoxScoreTraditionalV2Response

    def test_endpoint_is_frozen(self):
        """BoxScoreTraditionalV2 is immutable (frozen Pydantic model)."""
        endpoint = BoxScoreTraditionalV2(game_id="0022400123")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_id = "0022400999"  # type: ignore[misc]


class TestBoxScoreTraditionalV2Response:
    """Tests for BoxScoreTraditionalV2Response model."""

    def test_parse_full_response(self):
        """Response parses all three result sets cleanly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerStats",
                    "headers": _PLAYER_HEADERS,
                    "rowSet": [
                        _player_row(
                            player_id=1630532,
                            name="Franz Wagner",
                            start_position="F",
                            pts=22,
                        ),
                        _player_row(
                            player_id=1629006,
                            name="Cole Anthony",
                            start_position="",
                            pts=8,
                        ),
                    ],
                },
                {
                    "name": "TeamStats",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_CITY",
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
                        "TO",
                        "PF",
                        "PTS",
                        "PLUS_MINUS",
                    ],
                    "rowSet": [
                        [
                            "0022400123",
                            1610612753,
                            "Magic",
                            "ORL",
                            "Orlando",
                            "240:00",
                            40,
                            90,
                            0.444,
                            10,
                            30,
                            0.333,
                            15,
                            20,
                            0.75,
                            10,
                            30,
                            40,
                            22,
                            8,
                            5,
                            12,
                            18,
                            105,
                            7.0,
                        ],
                    ],
                },
                {
                    "name": "TeamStarterBenchStats",
                    "headers": [
                        "GAME_ID",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "TEAM_CITY",
                        "STARTERS_BENCH",
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
                        "TO",
                        "PF",
                        "PTS",
                    ],
                    "rowSet": [
                        [
                            "0022400123",
                            1610612753,
                            "Magic",
                            "ORL",
                            "Orlando",
                            "Starters",
                            "180:00",
                            30,
                            60,
                            0.5,
                            8,
                            20,
                            0.4,
                            10,
                            14,
                            0.714,
                            7,
                            22,
                            29,
                            18,
                            6,
                            4,
                            8,
                            12,
                            78,
                        ],
                    ],
                },
            ]
        }

        response = BoxScoreTraditionalV2Response.model_validate(raw_response)

        assert len(response.player_stats) == 2
        assert len(response.team_stats) == 1
        assert len(response.starter_bench_stats) == 1

        starter, bench = response.player_stats
        assert starter.start_position == "F"
        assert bench.start_position == ""

    def test_start_position_distinguishes_starters_from_bench(self):
        """A non-empty start_position is the v2-only signal for starters."""
        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerStats",
                    "headers": _PLAYER_HEADERS,
                    "rowSet": [
                        _player_row(
                            player_id=10 + i,
                            name=f"Starter {i}",
                            start_position=pos,
                        )
                        for i, pos in enumerate(["G", "G", "F", "F", "C"])
                    ]
                    + [
                        _player_row(
                            player_id=20 + i,
                            name=f"Bench {i}",
                            start_position="",
                        )
                        for i in range(3)
                    ],
                },
                {
                    "name": "TeamStats",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
                {
                    "name": "TeamStarterBenchStats",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = BoxScoreTraditionalV2Response.model_validate(raw_response)

        starters = [p for p in response.player_stats if p.start_position]
        bench = [p for p in response.player_stats if not p.start_position]
        assert len(starters) == 5
        assert len(bench) == 3
        # Starting positions are NBA's positional codes — never empty for starters
        assert {p.start_position for p in starters} == {"G", "F", "C"}

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {"name": "PlayerStats", "headers": ["GAME_ID"], "rowSet": []},
                {"name": "TeamStats", "headers": ["GAME_ID"], "rowSet": []},
                {
                    "name": "TeamStarterBenchStats",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = BoxScoreTraditionalV2Response.model_validate(raw_response)

        assert response.player_stats == []
        assert response.team_stats == []
        assert response.starter_bench_stats == []

    def test_parse_dnp_player_with_empty_minutes(self):
        """DNP rows have None MIN; numeric fields coerce to 0."""
        # DNP row: every numeric stat field is empty string in some old games
        dnp_row = (
            [
                "0022400123",
                1610612753,
                "ORL",
                "Orlando",
                999,
                "Bench Warmer",
                "Bench",
                "",
                "DNP - Coach's Decision",
                None,  # MIN
            ]
            + [""] * 18
            + [None]
        )  # all numeric stats empty + PLUS_MINUS null

        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerStats",
                    "headers": _PLAYER_HEADERS,
                    "rowSet": [dnp_row],
                },
                {"name": "TeamStats", "headers": ["GAME_ID"], "rowSet": []},
                {
                    "name": "TeamStarterBenchStats",
                    "headers": ["GAME_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = BoxScoreTraditionalV2Response.model_validate(raw_response)

        assert len(response.player_stats) == 1
        dnp = response.player_stats[0]
        assert dnp.start_position == ""
        assert dnp.pts == 0
        assert dnp.fgm == 0
        assert dnp.minutes is None
        assert dnp.plus_minus is None
