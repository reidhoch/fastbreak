"""Tests for fastbreak.defense — defensive analysis helpers.

TDD order: all tests written before production code.
PBT covers the mathematical invariants of defensive_shot_quality_vs_league.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from fastbreak.defense import (
    defensive_shot_quality_vs_league,
    get_box_scores_defensive,
    get_team_defense_zones,
    get_team_opponent_stats,
)
from fastbreak.models.box_score_defensive import BoxScoreDefensiveResponse
from fastbreak.models.league_dash_pt_team_defend import TeamDefendStats

# ─── shared constants ─────────────────────────────────────────────────────────

_XDIST = [HealthCheck.differing_executors]
_TEAM_ID = 1610612738  # Boston Celtics


# ─── TeamDefendStats factory ──────────────────────────────────────────────────


def _make_team_defend_stats(
    *,
    team_id: int = _TEAM_ID,
    team_name: str = "Celtics",
    team_abbreviation: str = "BOS",
    gp: int = 60,
    g: int = 60,
    freq: float = 1.0,
    d_fgm: int = 2400,
    d_fga: int = 5000,
    d_fg_pct: float = 0.480,
    normal_fg_pct: float = 0.500,
    pct_plusminus: float = -0.020,
) -> TeamDefendStats:
    return TeamDefendStats.model_validate(
        {
            "TEAM_ID": team_id,
            "TEAM_NAME": team_name,
            "TEAM_ABBREVIATION": team_abbreviation,
            "GP": gp,
            "G": g,
            "FREQ": freq,
            "D_FGM": d_fgm,
            "D_FGA": d_fga,
            "D_FG_PCT": d_fg_pct,
            "NORMAL_FG_PCT": normal_fg_pct,
            "PCT_PLUSMINUS": pct_plusminus,
        }
    )


# ─── Hypothesis strategy ──────────────────────────────────────────────────────


@st.composite
def _team_defend_stats_list(
    draw: st.DrawFn, min_size: int = 0, max_size: int = 30
) -> list[TeamDefendStats]:
    """Strategy: list of TeamDefendStats with unique team_ids in 1..50."""
    team_ids = draw(
        st.lists(
            st.integers(min_value=1, max_value=50),
            min_size=min_size,
            max_size=max_size,
            unique=True,
        )
    )
    result = []
    for tid in team_ids:
        delta = draw(st.floats(min_value=-0.3, max_value=0.3, allow_nan=False))
        result.append(_make_team_defend_stats(team_id=tid, pct_plusminus=delta))
    return result


# ─── TestDefensiveShotQualityVsLeague ─────────────────────────────────────────


class TestDefensiveShotQualityVsLeague:
    """Tests for defensive_shot_quality_vs_league() pure computation."""

    def test_known_team_id_returns_pct_plusminus(self) -> None:
        stats = [_make_team_defend_stats(team_id=_TEAM_ID, pct_plusminus=-0.023)]

        result = defensive_shot_quality_vs_league(stats, team_id=_TEAM_ID)

        assert result == {"BOS": pytest.approx(-0.023)}

    def test_unknown_team_id_returns_empty_dict(self) -> None:
        stats = [_make_team_defend_stats(team_id=_TEAM_ID)]

        result = defensive_shot_quality_vs_league(stats, team_id=9999)

        assert result == {}

    def test_empty_zones_returns_empty_dict(self) -> None:
        assert defensive_shot_quality_vs_league([], team_id=_TEAM_ID) == {}

    def test_multiple_teams_only_returns_target(self) -> None:
        zones = [
            _make_team_defend_stats(
                team_id=1, team_abbreviation="AAA", pct_plusminus=-0.01
            ),
            _make_team_defend_stats(
                team_id=2, team_abbreviation="BBB", pct_plusminus=0.03
            ),
            _make_team_defend_stats(
                team_id=3, team_abbreviation="CCC", pct_plusminus=-0.02
            ),
        ]

        result = defensive_shot_quality_vs_league(zones, team_id=2)

        assert result == {"BBB": pytest.approx(0.03)}
        assert "AAA" not in result
        assert "CCC" not in result

    @settings(suppress_health_check=_XDIST)
    @given(
        zones=_team_defend_stats_list(),
        team_id=st.integers(min_value=1, max_value=50),
    )
    def test_pbt_found_iff_nonempty(
        self, zones: list[TeamDefendStats], team_id: int
    ) -> None:
        """Non-empty result ↔ team_id exists in zones (biconditional)."""
        result = defensive_shot_quality_vs_league(zones, team_id=team_id)
        found = any(s.team_id == team_id for s in zones)
        assert bool(result) == found

    @settings(suppress_health_check=_XDIST)
    @given(
        zones=_team_defend_stats_list(min_size=1),
        team_id=st.integers(min_value=1, max_value=50),
    )
    def test_pbt_value_matches_source(
        self, zones: list[TeamDefendStats], team_id: int
    ) -> None:
        """When found, result value matches the source pct_plusminus exactly."""
        result = defensive_shot_quality_vs_league(zones, team_id=team_id)
        if result:
            matching = next(s for s in zones if s.team_id == team_id)
            assert next(iter(result.values())) == pytest.approx(matching.pct_plusminus)


# ─── ResultSet fixture helper ─────────────────────────────────────────────────

_TEAM_DEFEND_HEADERS = [
    "TEAM_ID",
    "TEAM_NAME",
    "TEAM_ABBREVIATION",
    "GP",
    "G",
    "FREQ",
    "D_FGM",
    "D_FGA",
    "D_FG_PCT",
    "NORMAL_FG_PCT",
    "PCT_PLUSMINUS",
]


def _make_team_defend_response(rows: list[list]) -> dict:
    return {
        "resource": "leaguedashptteamdefend",
        "parameters": {},
        "resultSets": [
            {
                "name": "LeagueDashPtTeamDefend",
                "headers": _TEAM_DEFEND_HEADERS,
                "rowSet": rows,
            }
        ],
    }


# ─── TestGetTeamDefenseZones ───────────────────────────────────────────────────


class TestGetTeamDefenseZones:
    """Tests for get_team_defense_zones() async fetcher."""

    async def test_returns_list_of_team_defend_stats(self, make_mock_client) -> None:
        json_data = _make_team_defend_response(
            [
                [
                    1610612738,
                    "Celtics",
                    "BOS",
                    60,
                    60,
                    1.0,
                    2400,
                    5000,
                    0.480,
                    0.500,
                    -0.020,
                ]
            ]
        )
        client, _ = make_mock_client(json_data=json_data)

        result = await get_team_defense_zones(client)

        assert len(result) == 1
        assert result[0].team_id == 1610612738
        assert result[0].team_abbreviation == "BOS"
        assert result[0].pct_plusminus == pytest.approx(-0.020)

    async def test_empty_result_set_returns_empty_list(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_team_defend_response([]))

        result = await get_team_defense_zones(client)

        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        client, mock_session = make_mock_client(
            json_data=_make_team_defend_response([])
        )

        await get_team_defense_zones(client)

        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        """Explicit season= kwarg does not raise."""
        client, _ = make_mock_client(json_data=_make_team_defend_response([]))

        result = await get_team_defense_zones(client, season="2025-26")

        assert result == []

    async def test_season_type_kwarg_accepted(self, make_mock_client) -> None:
        """Explicit season_type= kwarg does not raise."""
        client, _ = make_mock_client(json_data=_make_team_defend_response([]))

        result = await get_team_defense_zones(client, season_type="Playoffs")

        assert result == []

    async def test_defense_category_kwarg_accepted(self, make_mock_client) -> None:
        """Explicit defense_category= kwarg does not raise."""
        client, _ = make_mock_client(json_data=_make_team_defend_response([]))

        result = await get_team_defense_zones(client, defense_category="3 Pointers")

        assert result == []


# ─── OppPtShot fixture helper ──────────────────────────────────────────────────

_OPP_PT_SHOT_HEADERS = [
    "TEAM_ID",
    "TEAM_NAME",
    "TEAM_ABBREVIATION",
    "GP",
    "G",
    "FGA_FREQUENCY",
    "FGM",
    "FGA",
    "FG_PCT",
    "EFG_PCT",
    "FG2A_FREQUENCY",
    "FG2M",
    "FG2A",
    "FG2_PCT",
    "FG3A_FREQUENCY",
    "FG3M",
    "FG3A",
    "FG3_PCT",
]


def _make_opp_pt_shot_response(rows: list[list]) -> dict:
    return {
        "resource": "leaguedashoppptshot",
        "parameters": {},
        "resultSets": [
            {
                "name": "LeagueDashPTShots",
                "headers": _OPP_PT_SHOT_HEADERS,
                "rowSet": rows,
            }
        ],
    }


# ─── TestGetTeamOpponentStats ──────────────────────────────────────────────────


class TestGetTeamOpponentStats:
    """Tests for get_team_opponent_stats() async fetcher."""

    async def test_returns_list_of_opp_pt_shot_stats(self, make_mock_client) -> None:
        json_data = _make_opp_pt_shot_response(
            [
                [
                    1610612738,
                    "Celtics",
                    "BOS",
                    60,
                    60,
                    1.0,
                    2400,
                    5000,
                    0.480,
                    0.495,
                    0.65,
                    1800,
                    3200,
                    0.5625,
                    0.35,
                    600,
                    1800,
                    0.333,
                ]
            ]
        )
        client, _ = make_mock_client(json_data=json_data)

        result = await get_team_opponent_stats(client)

        assert len(result) == 1
        assert result[0].team_id == 1610612738
        assert result[0].team_abbreviation == "BOS"
        assert result[0].fg_pct == pytest.approx(0.480)
        assert result[0].efg_pct == pytest.approx(0.495)

    async def test_empty_result_set_returns_empty_list(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_opp_pt_shot_response([]))

        result = await get_team_opponent_stats(client)

        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        client, mock_session = make_mock_client(
            json_data=_make_opp_pt_shot_response([])
        )

        await get_team_opponent_stats(client)

        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_opp_pt_shot_response([]))

        result = await get_team_opponent_stats(client, season="2025-26")

        assert result == []

    async def test_season_type_kwarg_accepted(self, make_mock_client) -> None:
        """Explicit season_type= kwarg does not raise."""
        client, _ = make_mock_client(json_data=_make_opp_pt_shot_response([]))

        result = await get_team_opponent_stats(client, season_type="Playoffs")

        assert result == []


# ─── BoxScoreDefensive fixture ────────────────────────────────────────────────


def _make_box_score_defensive_json(game_id: str = "0022500001") -> dict:
    return {
        "meta": {
            "version": 1,
            "request": f"http://nba.cloud/games/{game_id}/boxscoredefensive",
            "time": "2025-10-22T00:00:00.000Z",
        },
        "boxScoreDefensive": {
            "gameId": game_id,
            "awayTeamId": 1610612737,
            "homeTeamId": 1610612738,
            "homeTeam": {
                "teamId": 1610612738,
                "teamCity": "Boston",
                "teamName": "Celtics",
                "teamTricode": "BOS",
                "teamSlug": "celtics",
                "players": [],
                "statistics": {"minutes": None},
            },
            "awayTeam": {
                "teamId": 1610612737,
                "teamCity": "Atlanta",
                "teamName": "Hawks",
                "teamTricode": "ATL",
                "teamSlug": "hawks",
                "players": [],
                "statistics": {"minutes": None},
            },
        },
    }


# ─── TestGetBoxScoresDefensive ────────────────────────────────────────────────


class TestGetBoxScoresDefensive:
    """Tests for get_box_scores_defensive() batch fetcher."""

    async def test_returns_dict_keyed_by_game_id(self, make_mock_client) -> None:
        client, _ = make_mock_client(
            json_data=_make_box_score_defensive_json("0022500001")
        )

        result = await get_box_scores_defensive(client, game_ids=["0022500001"])

        assert "0022500001" in result
        assert result["0022500001"].meta.version == 1
        assert result["0022500001"].box_score_defensive.game_id == "0022500001"

    async def test_empty_game_ids_returns_empty_dict(self, make_mock_client) -> None:
        client, mock_session = make_mock_client(
            json_data=_make_box_score_defensive_json()
        )

        result = await get_box_scores_defensive(client, game_ids=[])

        assert result == {}
        mock_session.get.assert_not_called()

    async def test_multiple_games_all_returned(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_box_score_defensive_json())

        result = await get_box_scores_defensive(
            client, game_ids=["0022500001", "0022500002"]
        )

        assert len(result) == 2
        assert isinstance(result["0022500001"], BoxScoreDefensiveResponse)
        assert isinstance(result["0022500002"], BoxScoreDefensiveResponse)

    async def test_raises_exception_group_on_failure(
        self, make_mock_client, make_client_response_error
    ) -> None:
        error = make_client_response_error(500)
        client, _ = make_mock_client(raise_error=error, max_retries=0)

        with pytest.raises(ExceptionGroup):
            await get_box_scores_defensive(client, game_ids=["0022500001"])


# ─── TestDefenseModuleExports ─────────────────────────────────────────────────


class TestDefenseModuleExports:
    """Verify the public API is importable from both fastbreak.defense and fastbreak."""

    def test_all_public_symbols_importable_from_defense(self) -> None:
        from fastbreak.defense import (
            defensive_shot_quality_vs_league,
            get_box_scores_defensive,
            get_player_shot_defense,
            get_team_defense_zones,
            get_team_opponent_stats,
        )

        assert callable(defensive_shot_quality_vs_league)
        assert callable(get_box_scores_defensive)
        assert callable(get_player_shot_defense)
        assert callable(get_team_defense_zones)
        assert callable(get_team_opponent_stats)

    def test_all_public_symbols_importable_from_fastbreak(self) -> None:
        import fastbreak

        assert callable(fastbreak.defensive_shot_quality_vs_league)
        assert callable(fastbreak.get_box_scores_defensive)
        assert callable(fastbreak.get_player_shot_defense)
        assert callable(fastbreak.get_team_defense_zones)
        assert callable(fastbreak.get_team_opponent_stats)
