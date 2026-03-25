"""Tests for fastbreak.estimated — pure computation helpers for estimated metrics.

TDD order: all tests written before production code.
PBT covers the mathematical invariants of rank_estimated_metrics.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from fastbreak.estimated import (
    find_player,
    find_team,
    get_estimated_leaders,
    get_player_estimated_metrics,
    get_team_estimated_metrics,
    rank_estimated_metrics,
)
from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetric
from fastbreak.models.team_estimated_metrics import TeamEstimatedMetric
from tests.strategies import XDIST_SUPPRESS as _XDIST

# ─── shared constants ─────────────────────────────────────────────────────────

_PLAYER_ID = 1641705
_TEAM_ID = 1610612754


# ─── PlayerEstimatedMetric factory ────────────────────────────────────────────


def _make_player(
    *,
    player_id: int = _PLAYER_ID,
    player_name: str = "Test Player",
    gp: int = 50,
    wins: int = 25,
    losses: int = 25,
    win_pct: float | None = 0.500,
    minutes: float = 33.0,
    e_off_rating: float | None = 110.0,
    e_def_rating: float | None = 108.0,
    e_net_rating: float | None = 2.0,
    e_ast_ratio: float | None = 15.0,
    e_oreb_pct: float | None = 0.05,
    e_dreb_pct: float | None = 0.15,
    e_reb_pct: float | None = 0.10,
    e_tov_pct: float | None = 12.0,
    e_usg_pct: float | None = 0.20,
    e_pace: float | None = 100.0,
) -> PlayerEstimatedMetric:
    return PlayerEstimatedMetric.model_validate(
        {
            "PLAYER_ID": player_id,
            "PLAYER_NAME": player_name,
            "GP": gp,
            "W": wins,
            "L": losses,
            "W_PCT": win_pct,
            "MIN": minutes,
            "E_OFF_RATING": e_off_rating,
            "E_DEF_RATING": e_def_rating,
            "E_NET_RATING": e_net_rating,
            "E_AST_RATIO": e_ast_ratio,
            "E_OREB_PCT": e_oreb_pct,
            "E_DREB_PCT": e_dreb_pct,
            "E_REB_PCT": e_reb_pct,
            "E_TOV_PCT": e_tov_pct,
            "E_USG_PCT": e_usg_pct,
            "E_PACE": e_pace,
            # All rank fields set to None
            "GP_RANK": None,
            "W_RANK": None,
            "L_RANK": None,
            "W_PCT_RANK": None,
            "MIN_RANK": None,
            "E_OFF_RATING_RANK": None,
            "E_DEF_RATING_RANK": None,
            "E_NET_RATING_RANK": None,
            "E_AST_RATIO_RANK": None,
            "E_OREB_PCT_RANK": None,
            "E_DREB_PCT_RANK": None,
            "E_REB_PCT_RANK": None,
            "E_TOV_PCT_RANK": None,
            "E_USG_PCT_RANK": None,
            "E_PACE_RANK": None,
        }
    )


# ─── TeamEstimatedMetric factory ──────────────────────────────────────────────


def _make_team(
    *,
    team_id: int = _TEAM_ID,
    team_name: str = "Test Team",
    gp: int = 50,
    wins: int = 25,
    losses: int = 25,
    win_pct: float | None = 0.500,
    minutes: float = 12000.0,
    e_off_rating: float | None = 110.0,
    e_def_rating: float | None = 108.0,
    e_net_rating: float | None = 2.0,
    e_pace: float | None = 100.0,
    e_ast_ratio: float | None = 15.0,
    e_oreb_pct: float | None = 0.25,
    e_dreb_pct: float | None = 0.75,
    e_reb_pct: float | None = 0.50,
    e_tm_tov_pct: float | None = 0.12,
) -> TeamEstimatedMetric:
    return TeamEstimatedMetric.model_validate(
        {
            "TEAM_ID": team_id,
            "TEAM_NAME": team_name,
            "GP": gp,
            "W": wins,
            "L": losses,
            "W_PCT": win_pct,
            "MIN": minutes,
            "E_OFF_RATING": e_off_rating,
            "E_DEF_RATING": e_def_rating,
            "E_NET_RATING": e_net_rating,
            "E_PACE": e_pace,
            "E_AST_RATIO": e_ast_ratio,
            "E_OREB_PCT": e_oreb_pct,
            "E_DREB_PCT": e_dreb_pct,
            "E_REB_PCT": e_reb_pct,
            "E_TM_TOV_PCT": e_tm_tov_pct,
            # All rank fields set to None
            "GP_RANK": None,
            "W_RANK": None,
            "L_RANK": None,
            "W_PCT_RANK": None,
            "MIN_RANK": None,
            "E_OFF_RATING_RANK": None,
            "E_DEF_RATING_RANK": None,
            "E_NET_RATING_RANK": None,
            "E_AST_RATIO_RANK": None,
            "E_OREB_PCT_RANK": None,
            "E_DREB_PCT_RANK": None,
            "E_REB_PCT_RANK": None,
            "E_TM_TOV_PCT_RANK": None,
            "E_PACE_RANK": None,
        }
    )


# ─── TestFindPlayer ────────────────────────────────────────────────────────────


class TestFindPlayer:
    """Tests for find_player() pure lookup function."""

    def test_returns_matching_player(self) -> None:
        p1 = _make_player(player_id=1, player_name="Alice")
        p2 = _make_player(player_id=2, player_name="Bob")
        players = [p1, p2]

        result = find_player(players, player_id=2)

        assert result is p2

    def test_returns_none_when_not_found(self) -> None:
        players = [_make_player(player_id=1)]

        result = find_player(players, player_id=999)

        assert result is None

    def test_empty_list_returns_none(self) -> None:
        result = find_player([], player_id=_PLAYER_ID)

        assert result is None

    def test_returns_first_match_if_duplicates(self) -> None:
        p1 = _make_player(player_id=5, player_name="First")
        p2 = _make_player(player_id=5, player_name="Second")
        players = [p1, p2]

        result = find_player(players, player_id=5)

        assert result is p1
        assert result.player_name == "First"

    def test_correct_player_from_multiple(self) -> None:
        p1 = _make_player(player_id=10, player_name="Alpha", e_net_rating=1.0)
        p2 = _make_player(player_id=20, player_name="Beta", e_net_rating=5.5)
        p3 = _make_player(player_id=30, player_name="Gamma", e_net_rating=9.0)
        players = [p1, p2, p3]

        result = find_player(players, player_id=20)

        assert result is not None
        assert result.player_name == "Beta"
        assert result.e_net_rating == pytest.approx(5.5)


# ─── TestFindTeam ──────────────────────────────────────────────────────────────


class TestFindTeam:
    """Tests for find_team() pure lookup function."""

    def test_returns_matching_team(self) -> None:
        t1 = _make_team(team_id=1, team_name="Team A")
        t2 = _make_team(team_id=2, team_name="Team B")
        teams = [t1, t2]

        result = find_team(teams, team_id=2)

        assert result is t2

    def test_returns_none_when_not_found(self) -> None:
        teams = [_make_team(team_id=1)]

        result = find_team(teams, team_id=999)

        assert result is None

    def test_empty_list_returns_none(self) -> None:
        result = find_team([], team_id=_TEAM_ID)

        assert result is None

    def test_correct_team_from_multiple(self) -> None:
        t1 = _make_team(team_id=100, team_name="Rockets", e_net_rating=-3.0)
        t2 = _make_team(team_id=200, team_name="Lakers", e_net_rating=4.5)
        t3 = _make_team(team_id=300, team_name="Celtics", e_net_rating=7.2)
        teams = [t1, t2, t3]

        result = find_team(teams, team_id=200)

        assert result is not None
        assert result.team_name == "Lakers"
        assert result.e_net_rating == pytest.approx(4.5)


# ─── TestRankEstimatedMetrics ──────────────────────────────────────────────────


class TestRankEstimatedMetrics:
    """Tests for rank_estimated_metrics() pure computation."""

    def test_sorts_by_net_rating_descending_by_default(self) -> None:
        p1 = _make_player(player_id=1, e_net_rating=2.0)
        p2 = _make_player(player_id=2, e_net_rating=8.0)
        p3 = _make_player(player_id=3, e_net_rating=5.0)
        players = [p1, p2, p3]

        result = rank_estimated_metrics(players)

        assert [p.player_id for p in result] == [2, 3, 1]

    def test_ascending_sort(self) -> None:
        p1 = _make_player(player_id=1, e_net_rating=2.0)
        p2 = _make_player(player_id=2, e_net_rating=8.0)
        p3 = _make_player(player_id=3, e_net_rating=5.0)
        players = [p1, p2, p3]

        result = rank_estimated_metrics(players, ascending=True)

        assert [p.player_id for p in result] == [1, 3, 2]

    def test_filters_by_min_gp(self) -> None:
        p1 = _make_player(player_id=1, gp=50)
        p2 = _make_player(player_id=2, gp=10)
        players = [p1, p2]

        result = rank_estimated_metrics(players, min_gp=20)

        assert len(result) == 1
        assert result[0].player_id == 1

    def test_gp_exactly_at_min_gp_is_included(self) -> None:
        p1 = _make_player(player_id=1, gp=20)
        players = [p1]

        result = rank_estimated_metrics(players, min_gp=20)

        assert len(result) == 1
        assert result[0].player_id == 1

    def test_filters_by_min_minutes(self) -> None:
        p1 = _make_player(player_id=1, minutes=33.0)
        p2 = _make_player(player_id=2, minutes=12.0)
        players = [p1, p2]

        result = rank_estimated_metrics(players, min_minutes=30.0)

        assert len(result) == 1
        assert result[0].player_id == 1

    def test_minutes_exactly_at_min_minutes_is_included(self) -> None:
        p1 = _make_player(player_id=1, minutes=30.0)
        players = [p1]

        result = rank_estimated_metrics(players, min_minutes=30.0)

        assert len(result) == 1
        assert result[0].player_id == 1

    def test_excludes_none_values_for_sort_field(self) -> None:
        p1 = _make_player(player_id=1, e_net_rating=5.0)
        p2 = _make_player(player_id=2, e_net_rating=None)
        players = [p1, p2]

        result = rank_estimated_metrics(players)

        assert len(result) == 1
        assert result[0].player_id == 1

    def test_empty_list_returns_empty(self) -> None:
        result = rank_estimated_metrics([])

        assert result == []

    def test_min_gp_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="min_gp"):
            rank_estimated_metrics([], min_gp=-1)

    def test_min_minutes_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="min_minutes"):
            rank_estimated_metrics([], min_minutes=-1.0)

    def test_min_gp_zero_is_valid(self) -> None:
        result = rank_estimated_metrics([], min_gp=0)

        assert result == []

    def test_min_minutes_zero_is_valid(self) -> None:
        result = rank_estimated_metrics([], min_minutes=0.0)

        assert result == []

    def test_by_e_off_rating(self) -> None:
        p1 = _make_player(player_id=1, e_off_rating=105.0)
        p2 = _make_player(player_id=2, e_off_rating=115.0)
        p3 = _make_player(player_id=3, e_off_rating=110.0)
        players = [p1, p2, p3]

        result = rank_estimated_metrics(players, by="e_off_rating")

        assert [p.player_id for p in result] == [2, 3, 1]

    def test_by_e_usg_pct(self) -> None:
        p1 = _make_player(player_id=1, e_usg_pct=0.18)
        p2 = _make_player(player_id=2, e_usg_pct=0.30)
        p3 = _make_player(player_id=3, e_usg_pct=0.25)
        players = [p1, p2, p3]

        result = rank_estimated_metrics(players, by="e_usg_pct")

        assert [p.player_id for p in result] == [2, 3, 1]

    # ─── Property-based tests ─────────────────────────────────────────────────

    @settings(suppress_health_check=_XDIST)
    @given(
        players=st.lists(
            st.builds(
                _make_player,
                player_id=st.integers(min_value=1, max_value=9_999_999),
                gp=st.integers(min_value=0, max_value=82),
                minutes=st.floats(
                    min_value=0.0,
                    max_value=48.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
                e_net_rating=st.one_of(
                    st.none(),
                    st.floats(
                        min_value=-50.0,
                        max_value=50.0,
                        allow_nan=False,
                        allow_infinity=False,
                    ),
                ),
            ),
            max_size=20,
        ),
        min_gp=st.integers(min_value=0, max_value=82),
        min_minutes=st.floats(
            min_value=0.0, max_value=48.0, allow_nan=False, allow_infinity=False
        ),
    )
    def test_pbt_result_is_subset(
        self,
        players: list[PlayerEstimatedMetric],
        min_gp: int,
        min_minutes: float,
    ) -> None:
        """All results satisfy gp >= min_gp and minutes >= min_minutes."""
        result = rank_estimated_metrics(players, min_gp=min_gp, min_minutes=min_minutes)

        for p in result:
            assert p.gp >= min_gp
            assert p.minutes >= min_minutes
            assert p.e_net_rating is not None

    @settings(suppress_health_check=_XDIST)
    @given(
        players=st.lists(
            st.builds(
                _make_player,
                player_id=st.integers(min_value=1, max_value=9_999_999),
                e_net_rating=st.floats(
                    min_value=-50.0,
                    max_value=50.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
            ),
            max_size=20,
        ),
    )
    def test_pbt_result_is_sorted_desc(
        self,
        players: list[PlayerEstimatedMetric],
    ) -> None:
        """Default descending sort: each element >= the next."""
        result = rank_estimated_metrics(players)

        for i in range(len(result) - 1):
            assert result[i].e_net_rating >= result[i + 1].e_net_rating  # type: ignore[operator]


# ── Response fixture helpers (singular resultSet format) ─────────────────────

_PLAYER_HEADERS = [
    "PLAYER_ID",
    "PLAYER_NAME",
    "GP",
    "W",
    "L",
    "W_PCT",
    "MIN",
    "E_OFF_RATING",
    "E_DEF_RATING",
    "E_NET_RATING",
    "E_AST_RATIO",
    "E_OREB_PCT",
    "E_DREB_PCT",
    "E_REB_PCT",
    "E_TOV_PCT",
    "E_USG_PCT",
    "E_PACE",
    "GP_RANK",
    "W_RANK",
    "L_RANK",
    "W_PCT_RANK",
    "MIN_RANK",
    "E_OFF_RATING_RANK",
    "E_DEF_RATING_RANK",
    "E_NET_RATING_RANK",
    "E_AST_RATIO_RANK",
    "E_OREB_PCT_RANK",
    "E_DREB_PCT_RANK",
    "E_REB_PCT_RANK",
    "E_TOV_PCT_RANK",
    "E_USG_PCT_RANK",
    "E_PACE_RANK",
]


def _make_player_response(rows: list[list]) -> dict:
    return {
        "resource": "playerestimatedmetrics",
        "parameters": {},
        "resultSet": {
            "headers": _PLAYER_HEADERS,
            "rowSet": rows,
        },
    }


_TEAM_HEADERS = [
    "TEAM_NAME",
    "TEAM_ID",
    "GP",
    "W",
    "L",
    "W_PCT",
    "MIN",
    "E_OFF_RATING",
    "E_DEF_RATING",
    "E_NET_RATING",
    "E_PACE",
    "E_AST_RATIO",
    "E_OREB_PCT",
    "E_DREB_PCT",
    "E_REB_PCT",
    "E_TM_TOV_PCT",
    "GP_RANK",
    "W_RANK",
    "L_RANK",
    "W_PCT_RANK",
    "MIN_RANK",
    "E_OFF_RATING_RANK",
    "E_DEF_RATING_RANK",
    "E_NET_RATING_RANK",
    "E_AST_RATIO_RANK",
    "E_OREB_PCT_RANK",
    "E_DREB_PCT_RANK",
    "E_REB_PCT_RANK",
    "E_TM_TOV_PCT_RANK",
    "E_PACE_RANK",
]


def _make_team_response(rows: list[list]) -> dict:
    return {
        "resource": "teamestimatedmetrics",
        "parameters": {},
        "resultSet": {
            "headers": _TEAM_HEADERS,
            "rowSet": rows,
        },
    }


def _player_row(
    player_id: int = _PLAYER_ID,
    player_name: str = "Test Player",
    gp: int = 50,
) -> list:
    """Minimal player row matching _PLAYER_HEADERS order."""
    return [
        player_id,
        player_name,
        gp,
        25,
        25,
        0.500,
        33.0,
        110.0,
        108.0,
        2.0,
        15.0,
        0.05,
        0.15,
        0.10,
        0.12,
        0.20,
        100.0,
        *([None] * 15),  # ranks
    ]


def _team_row(team_id: int = _TEAM_ID, team_name: str = "Test Team") -> list:
    """Minimal team row matching _TEAM_HEADERS order."""
    return [
        team_name,
        team_id,
        50,
        25,
        25,
        0.500,
        12000.0,
        110.0,
        108.0,
        2.0,
        100.0,
        15.0,
        0.25,
        0.75,
        0.50,
        0.12,
        *([None] * 14),  # ranks
    ]


class TestGetPlayerEstimatedMetrics:
    """Tests for get_player_estimated_metrics() async fetcher."""

    async def test_returns_list(self, make_mock_client) -> None:
        json_data = _make_player_response([_player_row()])
        client, _ = make_mock_client(json_data=json_data)
        result = await get_player_estimated_metrics(client)
        assert len(result) == 1
        assert result[0].player_id == _PLAYER_ID
        assert result[0].e_net_rating == pytest.approx(2.0)

    async def test_empty_result_set(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([]))
        result = await get_player_estimated_metrics(client)
        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        client, mock_session = make_mock_client(json_data=_make_player_response([]))
        await get_player_estimated_metrics(client)
        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([]))
        result = await get_player_estimated_metrics(client, season="2025-26")
        assert result == []

    async def test_season_type_kwarg_accepted(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([]))
        result = await get_player_estimated_metrics(client, season_type="Playoffs")
        assert result == []


class TestGetTeamEstimatedMetrics:
    """Tests for get_team_estimated_metrics() async fetcher."""

    async def test_returns_list(self, make_mock_client) -> None:
        json_data = _make_team_response([_team_row()])
        client, _ = make_mock_client(json_data=json_data)
        result = await get_team_estimated_metrics(client)
        assert len(result) == 1
        assert result[0].team_id == _TEAM_ID
        assert result[0].e_net_rating == pytest.approx(2.0)

    async def test_empty_result_set(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_team_response([]))
        result = await get_team_estimated_metrics(client)
        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        client, mock_session = make_mock_client(json_data=_make_team_response([]))
        await get_team_estimated_metrics(client)
        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_team_response([]))
        result = await get_team_estimated_metrics(client, season="2025-26")
        assert result == []


class TestGetEstimatedLeaders:
    """Tests for get_estimated_leaders() convenience wrapper."""

    async def test_returns_top_n_sorted(self, make_mock_client) -> None:
        rows = [
            _player_row(player_id=1, player_name="A"),
            _player_row(player_id=2, player_name="B"),
            _player_row(player_id=3, player_name="C"),
        ]
        client, _ = make_mock_client(json_data=_make_player_response(rows))
        result = await get_estimated_leaders(client, top_n=2)
        assert len(result) == 2

    async def test_top_n_exceeds_results(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([_player_row()]))
        result = await get_estimated_leaders(client, top_n=100)
        assert len(result) == 1

    async def test_top_n_less_than_one_raises(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([]))
        with pytest.raises(ValueError, match="top_n"):
            await get_estimated_leaders(client, top_n=0)

    async def test_top_n_one_is_valid(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([_player_row()]))
        result = await get_estimated_leaders(client, top_n=1)
        assert len(result) == 1

    async def test_filters_by_min_gp(self, make_mock_client) -> None:
        rows = [
            _player_row(player_id=1, gp=50),
            _player_row(player_id=2, gp=5),
        ]
        client, _ = make_mock_client(json_data=_make_player_response(rows))
        result = await get_estimated_leaders(client, min_gp=20, top_n=10)
        assert len(result) == 1
        assert result[0].player_id == 1

    async def test_empty_response_returns_empty(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([]))
        result = await get_estimated_leaders(client)
        assert result == []

    async def test_by_custom_metric(self, make_mock_client) -> None:
        client, _ = make_mock_client(json_data=_make_player_response([_player_row()]))
        result = await get_estimated_leaders(client, metric="e_off_rating")
        assert len(result) == 1


# ─── TestEstimatedModuleExports ──────────────────────────────────────────────


class TestEstimatedModuleExports:
    """Verify the public API is importable from both fastbreak.estimated and fastbreak."""

    def test_all_public_symbols_importable_from_estimated(self) -> None:
        from fastbreak.estimated import (
            find_player,
            find_team,
            get_estimated_leaders,
            get_player_estimated_metrics,
            get_team_estimated_metrics,
            rank_estimated_metrics,
        )

        assert callable(find_player)
        assert callable(find_team)
        assert callable(get_estimated_leaders)
        assert callable(get_player_estimated_metrics)
        assert callable(get_team_estimated_metrics)
        assert callable(rank_estimated_metrics)

    def test_all_public_symbols_importable_from_fastbreak(self) -> None:
        import fastbreak

        assert callable(fastbreak.find_player)
        assert callable(fastbreak.find_team)
        assert callable(fastbreak.get_estimated_leaders)
        assert callable(fastbreak.get_player_estimated_metrics)
        assert callable(fastbreak.get_team_estimated_metrics)
        assert callable(fastbreak.rank_estimated_metrics)

    def test_player_metric_field_matches_model_fields(self) -> None:
        """_PlayerMetricField Literal stays in sync with PlayerEstimatedMetric e_* fields."""
        from typing import get_args

        from fastbreak.estimated import _PlayerMetricField

        literal_fields = set(get_args(_PlayerMetricField))
        model_fields = {
            f
            for f in PlayerEstimatedMetric.model_fields
            if f.startswith("e_") and not f.endswith("_rank")
        }
        assert literal_fields == model_fields, (
            f"Literal/model mismatch — "
            f"in Literal only: {literal_fields - model_fields}, "
            f"in model only: {model_fields - literal_fields}"
        )

    def test_invalid_by_field_raises(self) -> None:
        """Passing an invalid field name to rank_estimated_metrics raises ValueError."""
        with pytest.raises(ValueError, match="by must be one of"):
            rank_estimated_metrics([], by="nonexistent_field")  # type: ignore[arg-type]
