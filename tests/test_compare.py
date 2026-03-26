"""Tests for fastbreak.compare — player comparison helpers.

TDD test suite covering:
- build_compared_player: construct ComparedPlayer from stats + estimated metrics
- comparison_deltas: pairwise stat deltas
- comparison_edges: win/loss/tie counting
- stat_leader: who leads for a metric
- compare_players: pure orchestrator
- get_player_comparison: async wrapper with mocked client
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from fastbreak.compare import (
    COMPARISON_METRICS,
    ComparedPlayer,
    ComparisonResult,
    EdgeSummary,
    build_compared_player,
    compare_players,
    comparison_deltas,
    comparison_edges,
    get_player_comparison,
    stat_leader,
)
from fastbreak.metrics import (
    ast_to_tov,
    effective_fg_pct,
    free_throw_rate,
    game_score,
    three_point_rate,
    true_shooting,
)

# ---------------------------------------------------------------------------
# Test stubs
# ---------------------------------------------------------------------------


@dataclass
class _StatsStub:
    """Lightweight stub satisfying _CompareStatsLike protocol."""

    description: str = "J. Doe"
    min: float = 35.0
    pts: float = 25.0
    reb: float = 7.0
    oreb: float = 1.0
    dreb: float = 6.0
    ast: float = 5.0
    stl: float = 1.5
    blk: float = 0.5
    tov: float = 3.0
    pf: float = 2.0
    plus_minus: float = 4.0
    fgm: float = 9.0
    fga: float = 18.0
    fg_pct: float = 0.500
    fg3m: float = 2.0
    fg3a: float = 6.0
    fg3_pct: float = 0.333
    ftm: float = 5.0
    fta: float = 6.0
    ft_pct: float = 0.833


@dataclass
class _EstimatedStub:
    """Lightweight stub for PlayerEstimatedMetric fields we use."""

    player_id: int = 1
    e_off_rating: float = 115.0
    e_def_rating: float = 108.0
    e_net_rating: float = 7.0
    e_usg_pct: float = 0.28
    e_pace: float = 100.0


def _make_stats(**overrides: float | str) -> _StatsStub:
    return _StatsStub(**overrides)  # type: ignore[arg-type]


def _make_estimated(**overrides: float) -> _EstimatedStub:
    return _EstimatedStub(**overrides)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# TestBuildComparedPlayer
# ---------------------------------------------------------------------------


class TestBuildComparedPlayer:
    """Step 1: build_compared_player constructs ComparedPlayer from raw data."""

    def test_returns_compared_player(self) -> None:
        result = build_compared_player(1, _make_stats())
        assert isinstance(result, ComparedPlayer)

    def test_player_id_preserved(self) -> None:
        result = build_compared_player(42, _make_stats())
        assert result.player_id == 42

    def test_name_from_description(self) -> None:
        result = build_compared_player(1, _make_stats(description="L. James"))
        assert result.name == "L. James"

    def test_box_score_fields_copied(self) -> None:
        stats = _make_stats(pts=30.0, reb=10.0, ast=8.0, stl=2.0, blk=1.0)
        result = build_compared_player(1, stats)
        assert result.pts == 30.0
        assert result.reb == 10.0
        assert result.ast == 8.0
        assert result.stl == 2.0
        assert result.blk == 1.0

    def test_all_box_score_fields(self) -> None:
        stats = _make_stats()
        result = build_compared_player(1, stats)
        for field in (
            "min",
            "pts",
            "reb",
            "oreb",
            "dreb",
            "ast",
            "stl",
            "blk",
            "tov",
            "pf",
            "plus_minus",
            "fgm",
            "fga",
            "fg_pct",
            "fg3m",
            "fg3a",
            "fg3_pct",
            "ftm",
            "fta",
            "ft_pct",
        ):
            assert getattr(result, field) == getattr(stats, field), f"{field} mismatch"

    def test_ts_pct_matches_metrics(self) -> None:
        stats = _make_stats(pts=25.0, fga=18.0, fta=6.0)
        result = build_compared_player(1, stats)
        expected = true_shooting(pts=25.0, fga=18.0, fta=6.0)
        assert result.ts_pct == pytest.approx(expected)

    def test_efg_pct_matches_metrics(self) -> None:
        stats = _make_stats(fgm=9.0, fg3m=2.0, fga=18.0)
        result = build_compared_player(1, stats)
        expected = effective_fg_pct(fgm=9.0, fg3m=2.0, fga=18.0)
        assert result.efg_pct == pytest.approx(expected)

    def test_ast_tov_matches_metrics(self) -> None:
        stats = _make_stats(ast=5.0, tov=3.0)
        result = build_compared_player(1, stats)
        expected = ast_to_tov(ast=5.0, tov=3.0)
        assert result.ast_tov == pytest.approx(expected)

    def test_game_score_matches_metrics(self) -> None:
        stats = _make_stats()
        result = build_compared_player(1, stats)
        expected = game_score(
            pts=stats.pts,
            fgm=stats.fgm,
            fga=stats.fga,
            ftm=stats.ftm,
            fta=stats.fta,
            oreb=stats.oreb,
            dreb=stats.dreb,
            stl=stats.stl,
            ast=stats.ast,
            blk=stats.blk,
            pf=stats.pf,
            tov=stats.tov,
        )
        assert result.game_score == pytest.approx(expected)

    def test_ft_rate_matches_metrics(self) -> None:
        stats = _make_stats(fta=6.0, fga=18.0)
        result = build_compared_player(1, stats)
        expected = free_throw_rate(fta=6.0, fga=18.0)
        assert result.ft_rate == pytest.approx(expected)

    def test_three_pt_rate_matches_metrics(self) -> None:
        stats = _make_stats(fg3a=6.0, fga=18.0)
        result = build_compared_player(1, stats)
        expected = three_point_rate(fg3a=6.0, fga=18.0)
        assert result.three_pt_rate == pytest.approx(expected)

    def test_estimated_none_when_not_provided(self) -> None:
        result = build_compared_player(1, _make_stats())
        assert result.e_off_rating is None
        assert result.e_def_rating is None
        assert result.e_net_rating is None
        assert result.e_usg_pct is None
        assert result.e_pace is None

    def test_estimated_fields_populated(self) -> None:
        est = _make_estimated(
            e_off_rating=115.0,
            e_def_rating=108.0,
            e_net_rating=7.0,
            e_usg_pct=0.28,
            e_pace=100.0,
        )
        result = build_compared_player(1, _make_stats(), estimated=est)
        assert result.e_off_rating == 115.0
        assert result.e_def_rating == 108.0
        assert result.e_net_rating == 7.0
        assert result.e_usg_pct == 0.28
        assert result.e_pace == 100.0

    def test_ts_pct_none_when_zero_attempts(self) -> None:
        stats = _make_stats(pts=0.0, fga=0.0, fta=0.0)
        result = build_compared_player(1, stats)
        assert result.ts_pct is None

    def test_efg_pct_none_when_zero_fga(self) -> None:
        stats = _make_stats(fgm=0.0, fg3m=0.0, fga=0.0)
        result = build_compared_player(1, stats)
        assert result.efg_pct is None

    def test_ast_tov_none_when_zero_tov(self) -> None:
        stats = _make_stats(ast=5.0, tov=0.0)
        result = build_compared_player(1, stats)
        assert result.ast_tov is None


# ---------------------------------------------------------------------------
# TestComparisonDeltas
# ---------------------------------------------------------------------------


class TestComparisonDeltas:
    """Step 2: comparison_deltas computes a - b for every metric."""

    def _make_player(self, **overrides: float) -> ComparedPlayer:
        defaults: dict[str, float | int | str | None] = {
            "player_id": 1,
            "name": "Test",
            "min": 30.0,
            "pts": 20.0,
            "reb": 5.0,
            "oreb": 1.0,
            "dreb": 4.0,
            "ast": 4.0,
            "stl": 1.0,
            "blk": 0.5,
            "tov": 2.0,
            "pf": 2.0,
            "plus_minus": 3.0,
            "fgm": 8.0,
            "fga": 16.0,
            "fg_pct": 0.500,
            "fg3m": 2.0,
            "fg3a": 5.0,
            "fg3_pct": 0.400,
            "ftm": 2.0,
            "fta": 3.0,
            "ft_pct": 0.667,
            "ts_pct": 0.550,
            "efg_pct": 0.562,
            "ast_tov": 2.0,
            "game_score": 15.0,
            "ft_rate": 0.188,
            "three_pt_rate": 0.312,
            "e_off_rating": 110.0,
            "e_def_rating": 108.0,
            "e_net_rating": 2.0,
            "e_usg_pct": 0.25,
            "e_pace": 100.0,
        }
        defaults.update(overrides)
        return ComparedPlayer(**defaults)  # type: ignore[arg-type]

    def test_pts_delta(self) -> None:
        a = self._make_player(pts=25.0)
        b = self._make_player(pts=20.0)
        deltas = comparison_deltas(a, b)
        assert deltas["pts"] == pytest.approx(5.0)

    def test_negative_delta(self) -> None:
        a = self._make_player(pts=15.0)
        b = self._make_player(pts=20.0)
        deltas = comparison_deltas(a, b)
        assert deltas["pts"] == pytest.approx(-5.0)

    def test_delta_none_when_a_none(self) -> None:
        a = self._make_player(e_net_rating=None)  # type: ignore[arg-type]
        b = self._make_player(e_net_rating=5.0)
        deltas = comparison_deltas(a, b)
        assert deltas["e_net_rating"] is None

    def test_delta_none_when_b_none(self) -> None:
        a = self._make_player(e_net_rating=5.0)
        b = self._make_player(e_net_rating=None)  # type: ignore[arg-type]
        deltas = comparison_deltas(a, b)
        assert deltas["e_net_rating"] is None

    def test_all_keys_present(self) -> None:
        a = self._make_player()
        b = self._make_player()
        deltas = comparison_deltas(a, b)
        for metric in COMPARISON_METRICS:
            assert metric in deltas, f"missing key: {metric}"

    def test_zero_deltas_when_identical(self) -> None:
        a = self._make_player()
        b = self._make_player()
        deltas = comparison_deltas(a, b)
        for metric, val in deltas.items():
            if val is not None:
                assert val == pytest.approx(0.0), f"{metric} should be 0"


# ---------------------------------------------------------------------------
# TestComparisonEdges
# ---------------------------------------------------------------------------


class TestComparisonEdges:
    """Step 3: comparison_edges counts wins/losses/ties."""

    def test_identical_all_ties(self) -> None:
        deltas = dict.fromkeys(COMPARISON_METRICS, 0.0)
        edges = comparison_edges(deltas)
        assert edges.ties == edges.total
        assert edges.a_leads == 0
        assert edges.b_leads == 0

    def test_a_leads_on_positive_delta(self) -> None:
        deltas = dict.fromkeys(COMPARISON_METRICS, 0.0)
        deltas["pts"] = 5.0
        edges = comparison_edges(deltas)
        assert edges.a_leads >= 1

    def test_b_leads_on_negative_delta(self) -> None:
        deltas = dict.fromkeys(COMPARISON_METRICS, 0.0)
        deltas["ast"] = -3.0
        edges = comparison_edges(deltas)
        assert edges.b_leads >= 1

    def test_higher_is_worse_inverted(self) -> None:
        """Positive tov delta means player A has MORE turnovers — B leads."""
        deltas = dict.fromkeys(COMPARISON_METRICS, 0.0)
        deltas["tov"] = 2.0  # A has more turnovers
        edges = comparison_edges(deltas)
        assert edges.b_leads >= 1

    def test_higher_is_worse_pf(self) -> None:
        """Positive pf delta means player A has MORE fouls — B leads."""
        deltas = dict.fromkeys(COMPARISON_METRICS, 0.0)
        deltas["pf"] = 1.0
        edges = comparison_edges(deltas)
        assert edges.b_leads >= 1

    def test_none_delta_is_unavailable(self) -> None:
        deltas: dict[str, float | None] = dict.fromkeys(COMPARISON_METRICS, 0.0)
        deltas["e_net_rating"] = None
        edges = comparison_edges(deltas)
        assert edges.unavailable >= 1

    def test_sum_invariant(self) -> None:
        deltas: dict[str, float | None] = dict.fromkeys(COMPARISON_METRICS, 0.0)
        deltas["pts"] = 5.0
        deltas["ast"] = -3.0
        deltas["tov"] = 2.0
        deltas["e_net_rating"] = None
        edges = comparison_edges(deltas)
        assert (
            edges.a_leads + edges.b_leads + edges.ties + edges.unavailable
            == edges.total
        )

    def test_total_equals_metrics_count(self) -> None:
        deltas = dict.fromkeys(COMPARISON_METRICS, 0.0)
        edges = comparison_edges(deltas)
        assert edges.total == len(COMPARISON_METRICS)


# ---------------------------------------------------------------------------
# TestStatLeader
# ---------------------------------------------------------------------------


class TestStatLeader:
    """Step 4: stat_leader returns the player_id of whoever leads."""

    def _make_player(self, pid: int, **overrides: float) -> ComparedPlayer:
        defaults: dict[str, float | int | str | None] = {
            "player_id": pid,
            "name": f"P{pid}",
            "min": 30.0,
            "pts": 20.0,
            "reb": 5.0,
            "oreb": 1.0,
            "dreb": 4.0,
            "ast": 4.0,
            "stl": 1.0,
            "blk": 0.5,
            "tov": 2.0,
            "pf": 2.0,
            "plus_minus": 3.0,
            "fgm": 8.0,
            "fga": 16.0,
            "fg_pct": 0.500,
            "fg3m": 2.0,
            "fg3a": 5.0,
            "fg3_pct": 0.400,
            "ftm": 2.0,
            "fta": 3.0,
            "ft_pct": 0.667,
            "ts_pct": 0.550,
            "efg_pct": 0.562,
            "ast_tov": 2.0,
            "game_score": 15.0,
            "ft_rate": 0.188,
            "three_pt_rate": 0.312,
            "e_off_rating": 110.0,
            "e_def_rating": 108.0,
            "e_net_rating": 2.0,
            "e_usg_pct": 0.25,
            "e_pace": 100.0,
        }
        defaults.update(overrides)
        return ComparedPlayer(**defaults)  # type: ignore[arg-type]

    def test_returns_a_when_higher(self) -> None:
        a = self._make_player(10, pts=25.0)
        b = self._make_player(20, pts=20.0)
        assert stat_leader(a, b, "pts") == 10

    def test_returns_b_when_higher(self) -> None:
        a = self._make_player(10, pts=15.0)
        b = self._make_player(20, pts=20.0)
        assert stat_leader(a, b, "pts") == 20

    def test_returns_none_when_equal(self) -> None:
        a = self._make_player(10, pts=20.0)
        b = self._make_player(20, pts=20.0)
        assert stat_leader(a, b, "pts") is None

    def test_returns_none_when_a_none(self) -> None:
        a = self._make_player(10, e_net_rating=None)  # type: ignore[arg-type]
        b = self._make_player(20, e_net_rating=5.0)
        assert stat_leader(a, b, "e_net_rating") is None

    def test_returns_none_when_b_none(self) -> None:
        a = self._make_player(10, e_net_rating=5.0)
        b = self._make_player(20, e_net_rating=None)  # type: ignore[arg-type]
        assert stat_leader(a, b, "e_net_rating") is None

    def test_inverted_for_higher_is_worse(self) -> None:
        """Player A has 5 TOV, player B has 3 TOV — B leads (lower is better)."""
        a = self._make_player(10, tov=5.0)
        b = self._make_player(20, tov=3.0)
        assert stat_leader(a, b, "tov", higher_is_worse=True) == 20

    def test_inverted_a_leads_when_lower(self) -> None:
        """Player A has 1 TOV, player B has 3 TOV — A leads (lower is better)."""
        a = self._make_player(10, tov=1.0)
        b = self._make_player(20, tov=3.0)
        assert stat_leader(a, b, "tov", higher_is_worse=True) == 10


# ---------------------------------------------------------------------------
# TestComparePlayers
# ---------------------------------------------------------------------------


class TestComparePlayers:
    """Step 5: compare_players pure orchestrator."""

    def test_returns_comparison_result(self) -> None:
        result = compare_players(
            player_a_id=1,
            player_a_stats=_make_stats(description="Player A"),
            player_b_id=2,
            player_b_stats=_make_stats(description="Player B"),
        )
        assert isinstance(result, ComparisonResult)

    def test_player_ids_correct(self) -> None:
        result = compare_players(
            player_a_id=42,
            player_a_stats=_make_stats(),
            player_b_id=99,
            player_b_stats=_make_stats(),
        )
        assert result.player_a.player_id == 42
        assert result.player_b.player_id == 99

    def test_deltas_populated(self) -> None:
        result = compare_players(
            player_a_id=1,
            player_a_stats=_make_stats(pts=30.0),
            player_b_id=2,
            player_b_stats=_make_stats(pts=20.0),
        )
        assert result.deltas["pts"] == pytest.approx(10.0)

    def test_edges_populated(self) -> None:
        result = compare_players(
            player_a_id=1,
            player_a_stats=_make_stats(),
            player_b_id=2,
            player_b_stats=_make_stats(),
        )
        assert isinstance(result.edges, EdgeSummary)
        assert result.edges.total == len(COMPARISON_METRICS)

    def test_without_estimated(self) -> None:
        result = compare_players(
            player_a_id=1,
            player_a_stats=_make_stats(),
            player_b_id=2,
            player_b_stats=_make_stats(),
        )
        assert result.player_a.e_net_rating is None
        assert result.player_b.e_net_rating is None

    def test_with_estimated(self) -> None:
        est_a = _make_estimated(e_net_rating=10.0)
        est_b = _make_estimated(e_net_rating=5.0)
        result = compare_players(
            player_a_id=1,
            player_a_stats=_make_stats(),
            player_b_id=2,
            player_b_stats=_make_stats(),
            estimated_a=est_a,
            estimated_b=est_b,
        )
        assert result.player_a.e_net_rating == 10.0
        assert result.player_b.e_net_rating == 5.0
        assert result.deltas["e_net_rating"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# TestGetPlayerComparison
# ---------------------------------------------------------------------------


class TestGetPlayerComparison:
    """Step 6: get_player_comparison async wrapper."""

    def _mock_compare_response(self, mocker: MockerFixture) -> object:
        """Build a mock PlayerCompareResponse with 2 individual rows."""
        row_a = mocker.MagicMock()
        for field in (
            "min",
            "pts",
            "reb",
            "oreb",
            "dreb",
            "ast",
            "stl",
            "blk",
            "tov",
            "pf",
            "plus_minus",
            "fgm",
            "fga",
            "fg_pct",
            "fg3m",
            "fg3a",
            "fg3_pct",
            "ftm",
            "fta",
            "ft_pct",
        ):
            setattr(row_a, field, 20.0)
        row_a.description = "Player A"

        row_b = mocker.MagicMock()
        for field in (
            "min",
            "pts",
            "reb",
            "oreb",
            "dreb",
            "ast",
            "stl",
            "blk",
            "tov",
            "pf",
            "plus_minus",
            "fgm",
            "fga",
            "fg_pct",
            "fg3m",
            "fg3a",
            "fg3_pct",
            "ftm",
            "fta",
            "ft_pct",
        ):
            setattr(row_b, field, 15.0)
        row_b.description = "Player B"

        response = mocker.MagicMock()
        response.individual = [row_a, row_b]
        return response

    def _mock_estimated_response(self, mocker: MockerFixture) -> object:
        """Build a mock PlayerEstimatedMetricsResponse."""
        player_a = mocker.MagicMock()
        player_a.player_id = 100
        player_a.e_off_rating = 115.0
        player_a.e_def_rating = 108.0
        player_a.e_net_rating = 7.0
        player_a.e_usg_pct = 0.28
        player_a.e_pace = 100.0

        player_b = mocker.MagicMock()
        player_b.player_id = 200
        player_b.e_off_rating = 110.0
        player_b.e_def_rating = 112.0
        player_b.e_net_rating = -2.0
        player_b.e_usg_pct = 0.22
        player_b.e_pace = 98.0

        response = mocker.MagicMock()
        response.players = [player_a, player_b]
        return response

    async def test_returns_comparison_result(self, mocker: MockerFixture) -> None:
        compare_resp = self._mock_compare_response(mocker)
        est_resp = self._mock_estimated_response(mocker)

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        result = await get_player_comparison(client, 100, 200)
        assert isinstance(result, ComparisonResult)

    async def test_player_ids_set(self, mocker: MockerFixture) -> None:
        compare_resp = self._mock_compare_response(mocker)
        est_resp = self._mock_estimated_response(mocker)

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        result = await get_player_comparison(client, 100, 200)
        assert result.player_a.player_id == 100
        assert result.player_b.player_id == 200

    async def test_estimated_integrated(self, mocker: MockerFixture) -> None:
        compare_resp = self._mock_compare_response(mocker)
        est_resp = self._mock_estimated_response(mocker)

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        result = await get_player_comparison(client, 100, 200)
        assert result.player_a.e_net_rating == 7.0
        assert result.player_b.e_net_rating == -2.0

    async def test_estimated_none_when_not_found(self, mocker: MockerFixture) -> None:
        compare_resp = self._mock_compare_response(mocker)
        est_resp = mocker.MagicMock()
        est_resp.players = []  # No players in estimated metrics

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        result = await get_player_comparison(client, 100, 200)
        assert result.player_a.e_net_rating is None
        assert result.player_b.e_net_rating is None

    async def test_empty_individual_raises(self, mocker: MockerFixture) -> None:
        compare_resp = mocker.MagicMock()
        compare_resp.individual = []  # Empty — bad player IDs
        est_resp = self._mock_estimated_response(mocker)

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        with pytest.raises(ValueError, match="individual"):
            await get_player_comparison(client, 100, 200)

    async def test_calls_get_many(self, mocker: MockerFixture) -> None:
        compare_resp = self._mock_compare_response(mocker)
        est_resp = self._mock_estimated_response(mocker)

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        await get_player_comparison(client, 100, 200)
        client.get_many.assert_awaited_once()

    async def test_season_forwarded(self, mocker: MockerFixture) -> None:
        compare_resp = self._mock_compare_response(mocker)
        est_resp = self._mock_estimated_response(mocker)

        client = mocker.MagicMock()
        client.get_many = mocker.AsyncMock(return_value=[compare_resp, est_resp])

        await get_player_comparison(client, 100, 200, season="2024-25")
        args = client.get_many.call_args[0][0]
        # First endpoint is PlayerCompare — check its season
        assert args[0].season == "2024-25"
