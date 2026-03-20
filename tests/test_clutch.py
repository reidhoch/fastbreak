"""Tests for fastbreak.clutch — clutch performance analysis helpers.

TDD order: each test was written before the corresponding production code.
PBT covers mathematical invariants of the pure clutch_score() and
build_clutch_profile() functions.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from pytest_mock import MockerFixture

from fastbreak.clutch import (
    ClutchProfile,
    build_clutch_profile,
    clutch_score,
    get_league_clutch_leaders,
    get_league_team_clutch_leaders,
    get_player_clutch_profile,
    get_player_clutch_stats,
    get_team_clutch_stats,
)
from fastbreak.clients.nba import NBAClient
from fastbreak.metrics import ast_to_tov, true_shooting

# ─── shared constants ─────────────────────────────────────────────────────────

_XDIST = [HealthCheck.differing_executors]
_DEFAULT_THRESHOLD = 5.0

# ─── Hypothesis strategies ────────────────────────────────────────────────────

_nn = st.floats(
    min_value=0.0,
    max_value=50.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)
_pos = st.floats(
    min_value=0.1,
    max_value=50.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)
_delta = st.floats(
    min_value=-1.0,
    max_value=1.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)
_pm = st.floats(
    min_value=-20.0,
    max_value=20.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)
_min_above = st.floats(
    min_value=_DEFAULT_THRESHOLD,
    max_value=200.0,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)
_min_below = st.floats(
    min_value=0.0,
    max_value=4.99,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)


# ─── Lightweight stats stub (used in PBT to avoid MagicMock) ─────────────────


class _StatsLike:
    """Minimal stub mirroring the ClutchStats fields consumed by build_clutch_profile."""

    def __init__(
        self,
        pts: float,
        fga: float,
        fta: float,
        ast: float = 2.0,
        tov: float = 1.0,
        minutes: float = 30.0,
        plus_minus: float = 0.0,
    ) -> None:
        self.pts = pts
        self.fga = fga
        self.fta = fta
        self.ast = ast
        self.tov = tov
        self.min = minutes
        self.plus_minus = plus_minus


# ─── Mock factory for mock-based tests ───────────────────────────────────────


def _make_stats(
    mocker: MockerFixture,
    *,
    pts: float = 20.0,
    fga: float = 15.0,
    fta: float = 4.0,
    ast: float = 3.0,
    tov: float = 2.0,
    minutes: float = 28.0,
    plus_minus: float = 3.0,
):
    s = mocker.MagicMock()
    s.pts = pts
    s.fga = fga
    s.fta = fta
    s.ast = ast
    s.tov = tov
    s.min = minutes
    s.plus_minus = plus_minus
    return s


# ─── TestClutchScore ──────────────────────────────────────────────────────────


class TestClutchScore:
    """Tests for the pure clutch_score() computation function."""

    def test_neutral_inputs_return_zero(self) -> None:
        """All-zero deltas produce a score of exactly 0.0."""
        result = clutch_score(
            ts_delta=0.0, ato_delta=0.0, plus_minus=0.0, clutch_min=25.0
        )
        assert result == pytest.approx(0.0)

    def test_below_min_threshold_returns_none(self) -> None:
        """Insufficient clutch minutes returns None (small sample guard)."""
        result = clutch_score(
            ts_delta=0.1, ato_delta=0.5, plus_minus=3.0, clutch_min=1.0
        )
        assert result is None

    def test_exactly_at_threshold_is_valid(self) -> None:
        """A clutch_min equal to min_threshold is not suppressed."""
        result = clutch_score(
            ts_delta=0.0, ato_delta=0.0, plus_minus=0.0, clutch_min=_DEFAULT_THRESHOLD
        )
        assert result is not None

    def test_positive_deltas_produce_positive_score(self) -> None:
        """Better clutch TS% and A/TO both push score above zero."""
        result = clutch_score(
            ts_delta=0.05, ato_delta=1.0, plus_minus=2.0, clutch_min=30.0
        )
        assert result is not None
        assert result > 0.0

    def test_negative_deltas_produce_negative_score(self) -> None:
        """Worse clutch TS% and A/TO both push score below zero."""
        result = clutch_score(
            ts_delta=-0.05, ato_delta=-1.0, plus_minus=-2.0, clutch_min=30.0
        )
        assert result is not None
        assert result < 0.0

    def test_exact_formula_output(self) -> None:
        """Pin the exact weighted formula: ts*10 + ato*3 + pm*0.5."""
        # 0.05*10 + 0.5*3 + 3.0*0.5 = 0.5 + 1.5 + 1.5 = 3.5
        result = clutch_score(
            ts_delta=0.05, ato_delta=0.5, plus_minus=3.0, clutch_min=7.0
        )
        assert result == pytest.approx(3.5)

    def test_exact_formula_negative(self) -> None:
        """Pin exact output with negative deltas to catch sign mutations."""
        # -0.03*10 + -1.0*3 + -4.0*0.5 = -0.3 + -3.0 + -2.0 = -5.3
        result = clutch_score(
            ts_delta=-0.03, ato_delta=-1.0, plus_minus=-4.0, clutch_min=10.0
        )
        assert result == pytest.approx(-5.3)

    def test_each_weight_contributes_independently(self) -> None:
        """Isolate each term to verify weights are 10, 3, and 0.5."""
        base = clutch_score(0.0, 0.0, 0.0, 10.0)
        ts_only = clutch_score(0.1, 0.0, 0.0, 10.0)
        ato_only = clutch_score(0.0, 1.0, 0.0, 10.0)
        pm_only = clutch_score(0.0, 0.0, 2.0, 10.0)
        assert base == pytest.approx(0.0)
        assert ts_only == pytest.approx(1.0)  # 0.1 * 10
        assert ato_only == pytest.approx(3.0)  # 1.0 * 3
        assert pm_only == pytest.approx(1.0)  # 2.0 * 0.5

    @settings(suppress_health_check=_XDIST)
    @given(ts=_delta, ato=_delta, pm=_pm, minutes=_min_above)
    def test_antisymmetry(
        self, ts: float, ato: float, pm: float, minutes: float
    ) -> None:
        """Negating all inputs negates the score (linear formula, no constant term)."""
        pos_score = clutch_score(ts, ato, pm, minutes)
        neg_score = clutch_score(-ts, -ato, -pm, minutes)
        assert pos_score is not None
        assert neg_score is not None
        assert neg_score == pytest.approx(-pos_score)

    @settings(suppress_health_check=_XDIST)
    @given(ts=_delta, ato=_delta, pm=_pm, minutes=_min_above)
    def test_defined_when_above_threshold(
        self, ts: float, ato: float, pm: float, minutes: float
    ) -> None:
        """Score is always a float (never None) when clutch_min >= default threshold."""
        result = clutch_score(ts, ato, pm, minutes)
        assert result is not None

    @settings(suppress_health_check=_XDIST)
    @given(ts=_delta, ato=_delta, pm=_pm, minutes=_min_below)
    def test_none_when_below_threshold(
        self, ts: float, ato: float, pm: float, minutes: float
    ) -> None:
        """Score is always None when clutch_min < default threshold."""
        assume(minutes < _DEFAULT_THRESHOLD)
        result = clutch_score(ts, ato, pm, minutes)
        assert result is None

    @settings(suppress_health_check=_XDIST)
    @given(ts1=_delta, ts2=_delta, ato=_delta, pm=_pm, minutes=_min_above)
    def test_monotone_in_ts_delta(
        self, ts1: float, ts2: float, ato: float, pm: float, minutes: float
    ) -> None:
        """Higher ts_delta produces equal or higher score (non-decreasing)."""
        lo, hi = (ts1, ts2) if ts1 <= ts2 else (ts2, ts1)
        lo_score = clutch_score(lo, ato, pm, minutes)
        hi_score = clutch_score(hi, ato, pm, minutes)
        assert lo_score is not None
        assert hi_score is not None
        assert lo_score <= hi_score + 1e-9


# ─── TestBuildClutchProfile ───────────────────────────────────────────────────


class TestBuildClutchProfile:
    """Tests for the build_clutch_profile() factory function."""

    def test_returns_clutch_profile_instance(self, mocker: MockerFixture) -> None:
        """build_clutch_profile always returns a ClutchProfile."""
        overall = _make_stats(mocker)
        clutch = _make_stats(mocker, minutes=25.0)
        result = build_clutch_profile(2544, "LeBron James", "LAL", overall, clutch)
        assert isinstance(result, ClutchProfile)

    def test_player_id_name_team_are_preserved(self, mocker: MockerFixture) -> None:
        """player_id, name, and team pass through unchanged."""
        overall = _make_stats(mocker)
        clutch = _make_stats(mocker, minutes=25.0)
        profile = build_clutch_profile(2544, "LeBron James", "LAL", overall, clutch)
        assert profile.player_id == 2544
        assert profile.name == "LeBron James"
        assert profile.team == "LAL"

    def test_none_overall_gives_none_regular_fields(
        self, mocker: MockerFixture
    ) -> None:
        """Without an overall stats row the regular-season baseline is absent."""
        clutch = _make_stats(mocker, minutes=25.0)
        profile = build_clutch_profile(1, "Player", "TST", None, clutch)
        assert profile.regular_ts is None
        assert profile.regular_ato is None
        assert profile.ts_delta is None
        assert profile.ato_delta is None

    def test_none_clutch_gives_zero_clutch_min_and_no_score(
        self, mocker: MockerFixture
    ) -> None:
        """Without clutch stats the profile has no clutch minutes and no score."""
        overall = _make_stats(mocker)
        profile = build_clutch_profile(1, "Player", "TST", overall, None)
        assert profile.clutch_min == 0.0
        assert profile.clutch_ts is None
        assert profile.score is None

    def test_ts_delta_equals_clutch_minus_regular(self, mocker: MockerFixture) -> None:
        """ts_delta == true_shooting(clutch) - true_shooting(regular)."""
        overall = _make_stats(mocker, pts=20.0, fga=15.0, fta=4.0)
        clutch = _make_stats(mocker, pts=25.0, fga=16.0, fta=5.0, minutes=30.0)
        profile = build_clutch_profile(1, "Player", "TST", overall, clutch)
        reg_ts = true_shooting(20.0, 15.0, 4.0)
        cl_ts = true_shooting(25.0, 16.0, 5.0)
        assert reg_ts is not None
        assert cl_ts is not None
        assert profile.ts_delta == pytest.approx(cl_ts - reg_ts)

    def test_ato_delta_equals_clutch_minus_regular(self, mocker: MockerFixture) -> None:
        """ato_delta == ast_to_tov(clutch) - ast_to_tov(regular)."""
        overall = _make_stats(mocker, ast=3.0, tov=2.0)
        clutch = _make_stats(mocker, ast=4.0, tov=1.5, minutes=30.0)
        profile = build_clutch_profile(1, "Player", "TST", overall, clutch)
        reg_ato = ast_to_tov(3.0, 2.0)
        cl_ato = ast_to_tov(4.0, 1.5)
        assert reg_ato is not None
        assert cl_ato is not None
        assert profile.ato_delta == pytest.approx(cl_ato - reg_ato)

    def test_score_none_when_below_default_threshold(
        self, mocker: MockerFixture
    ) -> None:
        """Player with only 2 clutch minutes gets score=None (insufficient sample)."""
        overall = _make_stats(mocker)
        clutch = _make_stats(mocker, minutes=2.0)
        profile = build_clutch_profile(1, "Player", "TST", overall, clutch)
        assert profile.score is None

    def test_score_defined_with_sufficient_clutch_minutes(
        self, mocker: MockerFixture
    ) -> None:
        """Player with 30 clutch minutes gets a computed composite score."""
        overall = _make_stats(mocker)
        clutch = _make_stats(mocker, minutes=30.0)
        profile = build_clutch_profile(1, "Player", "TST", overall, clutch)
        assert profile.score is not None

    def test_score_none_when_only_ts_delta_is_none(self) -> None:
        """When overall has fga=0 and fta=0, regular TS% is None so ts_delta is None.

        Even though ato_delta is computable (both have valid ast/tov), score
        must remain None because the ``and`` requires *both* deltas.  This
        kills the ``and → or`` mutation on the score computation guard.
        """
        overall = _StatsLike(pts=10.0, fga=0.0, fta=0.0, ast=3.0, tov=2.0)
        clutch = _StatsLike(pts=8.0, fga=5.0, fta=2.0, ast=4.0, tov=1.0, minutes=30.0)
        profile = build_clutch_profile(1, "Player", "TST", overall, clutch)
        # regular_ts is None (fga=0, fta=0), so ts_delta is None
        assert profile.regular_ts is None
        assert profile.ts_delta is None
        # ato_delta IS computable because both sides have valid ast/tov
        assert profile.ato_delta is not None
        # score must still be None — both deltas are required
        assert profile.score is None

    @settings(suppress_health_check=_XDIST)
    @given(
        pts_reg=_pos,
        fga_reg=_pos,
        fta_reg=_nn,
        pts_cl=_pos,
        fga_cl=_pos,
        fta_cl=_nn,
        minutes=_min_above,
    )
    def test_ts_delta_roundtrip(
        self,
        pts_reg: float,
        fga_reg: float,
        fta_reg: float,
        pts_cl: float,
        fga_cl: float,
        fta_cl: float,
        minutes: float,
    ) -> None:
        """ts_delta == true_shooting(clutch) - true_shooting(regular) for all valid inputs."""
        overall = _StatsLike(pts_reg, fga_reg, fta_reg)
        clutch = _StatsLike(pts_cl, fga_cl, fta_cl, minutes=minutes)
        profile = build_clutch_profile(1, "P", "T", overall, clutch)
        expected_reg = true_shooting(pts_reg, fga_reg, fta_reg)
        expected_cl = true_shooting(pts_cl, fga_cl, fta_cl)
        if expected_reg is not None and expected_cl is not None:
            assert profile.ts_delta == pytest.approx(expected_cl - expected_reg)
        else:
            assert profile.ts_delta is None


# ─── TestGetPlayerClutchStats ─────────────────────────────────────────────────


class TestGetPlayerClutchStats:
    """Tests for the get_player_clutch_stats() async API wrapper."""

    async def test_calls_player_dashboard_by_clutch_endpoint(
        self, mocker: MockerFixture
    ) -> None:
        """get_player_clutch_stats calls the API exactly once and returns the response."""
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_clutch_stats(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        """The player_id parameter is forwarded to the PlayerDashboardByClutch endpoint."""
        from fastbreak.endpoints import PlayerDashboardByClutch

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_player_clutch_stats(client, player_id=1630162)

        endpoint_arg = client.get.call_args[0][0]
        assert isinstance(endpoint_arg, PlayerDashboardByClutch)
        assert endpoint_arg.player_id == 1630162


# ─── TestGetPlayerClutchProfile ───────────────────────────────────────────────


class TestGetPlayerClutchProfile:
    """Tests for the get_player_clutch_profile() high-level helper."""

    async def test_returns_none_when_no_clutch_data(
        self, mocker: MockerFixture
    ) -> None:
        """Returns None when the player has no last_5_min_lte_5_pts data."""
        response = mocker.MagicMock()
        response.last_5_min_lte_5_pts = None
        response.overall = _make_stats(mocker)
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_clutch_profile(client, player_id=9999)

        assert result is None

    async def test_returns_profile_with_correct_player_id(
        self, mocker: MockerFixture
    ) -> None:
        """Returns a ClutchProfile carrying the correct player_id."""
        response = mocker.MagicMock()
        response.last_5_min_lte_5_pts = _make_stats(mocker, minutes=30.0)
        response.overall = _make_stats(mocker)
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_clutch_profile(
            client, player_id=2544, name="LeBron James", team="LAL"
        )

        assert isinstance(result, ClutchProfile)
        assert result.player_id == 2544

    async def test_name_and_team_are_stored_on_profile(
        self, mocker: MockerFixture
    ) -> None:
        """Name and team kwargs are stored on the returned ClutchProfile."""
        response = mocker.MagicMock()
        response.last_5_min_lte_5_pts = _make_stats(mocker, minutes=30.0)
        response.overall = _make_stats(mocker)
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_clutch_profile(
            client, player_id=2544, name="LeBron James", team="LAL"
        )

        assert result is not None
        assert result.name == "LeBron James"
        assert result.team == "LAL"


# ─── TestGetLeagueClutchLeaders ───────────────────────────────────────────────


class TestGetLeagueClutchLeaders:
    """Tests for the get_league_clutch_leaders() function."""

    def _make_row(
        self,
        mocker: MockerFixture,
        *,
        player_id: int,
        name: str,
        team: str,
        plus_minus: float,
        minutes: float,
    ):
        row = mocker.MagicMock()
        row.player_id = player_id
        row.player_name = name
        row.team_abbreviation = team
        row.plus_minus = plus_minus
        row.min = minutes
        return row

    async def test_filters_players_below_min_minutes(
        self, mocker: MockerFixture
    ) -> None:
        """Players below min_minutes threshold are excluded from results."""
        response = mocker.MagicMock()
        response.players = [
            self._make_row(
                mocker,
                player_id=1,
                name="Qualified",
                team="X",
                plus_minus=5.0,
                minutes=25.0,
            ),
            self._make_row(
                mocker,
                player_id=2,
                name="Excluded",
                team="X",
                plus_minus=3.0,
                minutes=5.0,
            ),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client, min_minutes=20.0)

        assert len(result) == 1
        assert result[0].player_id == 1

    async def test_sorted_by_plus_minus_descending(self, mocker: MockerFixture) -> None:
        """Results are sorted highest plus_minus first."""
        response = mocker.MagicMock()
        response.players = [
            self._make_row(
                mocker, player_id=1, name="A", team="X", plus_minus=1.0, minutes=25.0
            ),
            self._make_row(
                mocker, player_id=2, name="B", team="X", plus_minus=5.0, minutes=25.0
            ),
            self._make_row(
                mocker, player_id=3, name="C", team="X", plus_minus=3.0, minutes=25.0
            ),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client)

        assert [r.player_id for r in result] == [2, 3, 1]

    async def test_respects_top_n(self, mocker: MockerFixture) -> None:
        """At most top_n players are returned."""
        response = mocker.MagicMock()
        response.players = [
            self._make_row(
                mocker,
                player_id=i,
                name=f"P{i}",
                team="X",
                plus_minus=float(i),
                minutes=25.0,
            )
            for i in range(20)
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client, top_n=5)

        assert len(result) == 5

    async def test_empty_league_returns_empty_list(self, mocker: MockerFixture) -> None:
        """When no players qualify, returns an empty list."""
        response = mocker.MagicMock()
        response.players = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client)

        assert result == []

    async def test_top_n_zero_raises(self, mocker: MockerFixture) -> None:
        """top_n=0 raises ValueError (kills < to <= boundary mutant)."""
        client = NBAClient(session=mocker.MagicMock())
        with pytest.raises(ValueError, match="top_n must be >= 1"):
            await get_league_clutch_leaders(client, top_n=0)

    async def test_top_n_one_is_valid(self, mocker: MockerFixture) -> None:
        """top_n=1 does not raise (boundary: 1 < 1 is False)."""
        response = mocker.MagicMock()
        response.players = [
            self._make_row(
                mocker, player_id=1, name="A", team="X", plus_minus=5.0, minutes=25.0
            ),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client, top_n=1)
        assert len(result) == 1

    async def test_min_minutes_zero_is_valid(self, mocker: MockerFixture) -> None:
        """min_minutes=0 does not raise (kills < to <= boundary mutant)."""
        response = mocker.MagicMock()
        response.players = [
            self._make_row(
                mocker, player_id=1, name="A", team="X", plus_minus=5.0, minutes=0.0
            ),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client, min_minutes=0.0)
        assert len(result) == 1

    async def test_min_minutes_negative_raises(self, mocker: MockerFixture) -> None:
        """min_minutes=-1 raises ValueError."""
        client = NBAClient(session=mocker.MagicMock())
        with pytest.raises(ValueError, match="min_minutes must be >= 0"):
            await get_league_clutch_leaders(client, min_minutes=-1.0)

    async def test_filters_uses_gte_not_gt(self, mocker: MockerFixture) -> None:
        """Player with min exactly equal to min_minutes is included (>= not >)."""
        response = mocker.MagicMock()
        response.players = [
            self._make_row(
                mocker, player_id=1, name="A", team="X", plus_minus=5.0, minutes=20.0
            ),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_clutch_leaders(client, min_minutes=20.0)
        assert len(result) == 1


# ─── TestGetLeagueTeamClutchLeaders ─────────────────────────────────────────


class TestGetLeagueTeamClutchLeaders:
    """Tests for the get_league_team_clutch_leaders() function."""

    def _make_team(
        self,
        mocker: MockerFixture,
        *,
        team_id: int,
        team_name: str,
        plus_minus: float,
    ):
        row = mocker.MagicMock()
        row.team_id = team_id
        row.team_name = team_name
        row.plus_minus = plus_minus
        return row

    async def test_calls_api_once(self, mocker: MockerFixture) -> None:
        """client.get is called exactly once."""
        response = mocker.MagicMock()
        response.teams = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_league_team_clutch_leaders(client)

        client.get.assert_called_once()

    async def test_uses_team_clutch_endpoint(self, mocker: MockerFixture) -> None:
        """The endpoint passed to client.get is LeagueDashTeamClutch."""
        from fastbreak.endpoints import LeagueDashTeamClutch

        response = mocker.MagicMock()
        response.teams = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_league_team_clutch_leaders(client)

        endpoint_arg = client.get.call_args[0][0]
        assert isinstance(endpoint_arg, LeagueDashTeamClutch)

    async def test_sorted_by_plus_minus_desc(self, mocker: MockerFixture) -> None:
        """Results are sorted highest plus_minus first."""
        response = mocker.MagicMock()
        response.teams = [
            self._make_team(mocker, team_id=1, team_name="A", plus_minus=1.0),
            self._make_team(mocker, team_id=2, team_name="B", plus_minus=5.0),
            self._make_team(mocker, team_id=3, team_name="C", plus_minus=3.0),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_team_clutch_leaders(client)

        assert [r.team_id for r in result] == [2, 3, 1]

    async def test_respects_top_n(self, mocker: MockerFixture) -> None:
        """At most top_n teams are returned."""
        response = mocker.MagicMock()
        response.teams = [
            self._make_team(mocker, team_id=i, team_name=f"T{i}", plus_minus=float(i))
            for i in range(20)
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_team_clutch_leaders(client, top_n=5)

        assert len(result) == 5

    async def test_top_n_zero_raises(self, mocker: MockerFixture) -> None:
        """top_n=0 raises ValueError."""
        client = NBAClient(session=mocker.MagicMock())
        with pytest.raises(ValueError, match="top_n must be >= 1"):
            await get_league_team_clutch_leaders(client, top_n=0)

    async def test_top_n_default_is_30(self, mocker: MockerFixture) -> None:
        """Default top_n returns up to 30 teams."""
        response = mocker.MagicMock()
        response.teams = [
            self._make_team(mocker, team_id=i, team_name=f"T{i}", plus_minus=float(i))
            for i in range(35)
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_team_clutch_leaders(client)

        assert len(result) == 30

    async def test_empty_response(self, mocker: MockerFixture) -> None:
        """No teams returns an empty list."""
        response = mocker.MagicMock()
        response.teams = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_team_clutch_leaders(client)

        assert result == []


# ─── TestGetTeamClutchStats ─────────────────────────────────────────────────


class TestGetTeamClutchStats:
    """Tests for the get_team_clutch_stats() function."""

    def _make_team(
        self,
        mocker: MockerFixture,
        *,
        team_id: int,
        team_name: str,
        plus_minus: float = 0.0,
    ):
        row = mocker.MagicMock()
        row.team_id = team_id
        row.team_name = team_name
        row.plus_minus = plus_minus
        return row

    async def test_returns_matching_team(self, mocker: MockerFixture) -> None:
        """Returns the correct TeamClutchStats for the given team_id."""
        team = self._make_team(
            mocker, team_id=1610612747, team_name="Los Angeles Lakers"
        )
        response = mocker.MagicMock()
        response.teams = [team]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_clutch_stats(client, team_id=1610612747)

        assert result is team

    async def test_returns_none_when_not_found(self, mocker: MockerFixture) -> None:
        """Returns None for an unknown team_id."""
        response = mocker.MagicMock()
        response.teams = [
            self._make_team(mocker, team_id=1610612747, team_name="Los Angeles Lakers"),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_clutch_stats(client, team_id=9999999)

        assert result is None

    async def test_passes_season(self, mocker: MockerFixture) -> None:
        """The season kwarg is forwarded to the endpoint."""
        from fastbreak.endpoints import LeagueDashTeamClutch

        response = mocker.MagicMock()
        response.teams = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_team_clutch_stats(client, team_id=1, season="2024-25")

        endpoint_arg = client.get.call_args[0][0]
        assert isinstance(endpoint_arg, LeagueDashTeamClutch)
        assert endpoint_arg.season == "2024-25"

    async def test_passes_season_type(self, mocker: MockerFixture) -> None:
        """The season_type kwarg is forwarded to the endpoint."""
        from fastbreak.endpoints import LeagueDashTeamClutch

        response = mocker.MagicMock()
        response.teams = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_team_clutch_stats(client, team_id=1, season_type="Playoffs")

        endpoint_arg = client.get.call_args[0][0]
        assert isinstance(endpoint_arg, LeagueDashTeamClutch)
        assert endpoint_arg.season_type == "Playoffs"

    async def test_correct_team_from_multiple(self, mocker: MockerFixture) -> None:
        """Filters exactly the matching team from multiple teams."""
        lakers = self._make_team(
            mocker, team_id=1610612747, team_name="Los Angeles Lakers"
        )
        celtics = self._make_team(
            mocker, team_id=1610612738, team_name="Boston Celtics"
        )
        warriors = self._make_team(
            mocker, team_id=1610612744, team_name="Golden State Warriors"
        )
        response = mocker.MagicMock()
        response.teams = [lakers, celtics, warriors]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_clutch_stats(client, team_id=1610612738)

        assert result is celtics
