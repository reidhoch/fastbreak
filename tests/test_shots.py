"""Tests for fastbreak.shots — shot chart helpers.

TDD order: all tests written before production code.
PBT covers the mathematical invariants of the pure computation functions
(zone_fg_pct, zone_breakdown, shot_quality_vs_league).
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pytest_mock import MockerFixture

from fastbreak.shots import (
    ZoneStats,
    get_league_shot_zones,
    get_shot_chart,
    shot_quality_vs_league,
    xfg_pct,
    zone_breakdown,
    zone_fg_pct,
)

# ─── shared constants ─────────────────────────────────────────────────────────

_XDIST = [HealthCheck.differing_executors]
_ZONES = [
    "Restricted Area",
    "In The Paint (Non-RA)",
    "Mid-Range",
    "Left Corner 3",
    "Right Corner 3",
    "Above the Break 3",
    "Backcourt",
]


# ─── Shot factory ─────────────────────────────────────────────────────────────


def _make_shot(
    *,
    zone: str = "Mid-Range",
    made: int = 1,
    player_id: int = 2544,
    team_id: int = 1610612747,
) -> object:
    """Minimal Shot-like object for unit tests.

    Uses the populate_by_name field names so the same factory works for
    both Pydantic constructors and plain stubs in PBT strategies.
    """
    from fastbreak.models.shot_chart_detail import Shot

    return Shot(
        grid_type="Player Track Shooting",
        game_id="0022500001",
        game_event_id=1,
        player_id=player_id,
        player_name="Test Player",
        team_id=team_id,
        team_name="Test Team",
        period=1,
        minutes_remaining=11,
        seconds_remaining=45,
        event_type="Made Shot" if made else "Missed Shot",
        action_type="Jump Shot",
        shot_type="2PT Field Goal",
        shot_zone_basic=zone,
        shot_zone_area="Left Side(L)",
        shot_zone_range="16-24 ft.",
        shot_distance=18,
        loc_x=-150,
        loc_y=100,
        shot_attempted_flag=1,
        shot_made_flag=made,
        game_date="20250115",
        htm="LAL",
        vtm="GSW",
    )


def _make_league_zone(
    *, zone: str = "Mid-Range", fga: int = 1000, fgm: int = 400
) -> object:
    """Minimal LeagueWideShotZone-like object for unit tests."""
    from fastbreak.models.shot_chart_leaguewide import LeagueWideShotZone

    # LeagueWideShotZone uses SCREAMING_SNAKE_CASE aliases (no populate_by_name)
    return LeagueWideShotZone.model_validate(
        {
            "GRID_TYPE": "League Averages",
            "SHOT_ZONE_BASIC": zone,
            "SHOT_ZONE_AREA": "Left Side(L)",
            "SHOT_ZONE_RANGE": "16-24 ft.",
            "FGA": fga,
            "FGM": fgm,
            "FG_PCT": fgm / fga,
        }
    )


# ─── Hypothesis strategies ────────────────────────────────────────────────────

_zone_strategy = st.sampled_from(_ZONES)
_made_strategy = st.integers(min_value=0, max_value=1)


@st.composite
def _shot_list(draw, min_size: int = 0, max_size: int = 50) -> list:
    """Strategy generating a list of Shot objects with random zones/results."""
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    shots = []
    for _ in range(n):
        zone = draw(_zone_strategy)
        made = draw(_made_strategy)
        shots.append(_make_shot(zone=zone, made=made))
    return shots


# ─── TestZoneFgPct ────────────────────────────────────────────────────────────


class TestZoneFgPct:
    """Tests for the pure zone_fg_pct() computation function."""

    def test_empty_list_returns_none(self) -> None:
        """FG% of an empty shot list is undefined (returns None)."""
        assert zone_fg_pct([]) is None

    def test_all_makes_returns_one(self) -> None:
        """A list where every shot is made returns FG% of 1.0."""
        shots = [_make_shot(made=1) for _ in range(5)]
        result = zone_fg_pct(shots)
        assert result == pytest.approx(1.0)

    def test_all_misses_returns_zero(self) -> None:
        """A list where no shot is made returns FG% of 0.0."""
        shots = [_make_shot(made=0) for _ in range(5)]
        result = zone_fg_pct(shots)
        assert result == pytest.approx(0.0)

    def test_mixed_makes_and_misses(self) -> None:
        """FG% equals made / attempted for mixed shots."""
        shots = [_make_shot(made=1)] * 3 + [_make_shot(made=0)] * 2
        result = zone_fg_pct(shots)
        assert result == pytest.approx(0.6)

    def test_single_make_returns_one(self) -> None:
        """A single made shot returns 1.0."""
        assert zone_fg_pct([_make_shot(made=1)]) == pytest.approx(1.0)

    def test_single_miss_returns_zero(self) -> None:
        """A single missed shot returns 0.0."""
        assert zone_fg_pct([_make_shot(made=0)]) == pytest.approx(0.0)

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=1))
    def test_result_in_unit_interval(self, shots: list) -> None:
        """FG% is always in [0.0, 1.0] for any non-empty shot list."""
        result = zone_fg_pct(shots)
        assert result is not None
        assert 0.0 <= result <= 1.0

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=0, max_size=0))
    def test_empty_always_returns_none(self, shots: list) -> None:
        """Empty list always returns None (property version)."""
        assert zone_fg_pct(shots) is None


# ─── TestZoneBreakdown ────────────────────────────────────────────────────────


class TestZoneBreakdown:
    """Tests for the pure zone_breakdown() grouping function."""

    def test_empty_shots_returns_empty_dict(self) -> None:
        """An empty shot list returns an empty breakdown dict."""
        assert zone_breakdown([]) == {}

    def test_single_zone_creates_one_entry(self) -> None:
        """Shots in one zone produce a single breakdown entry."""
        shots = [_make_shot(zone="Restricted Area", made=1)] * 3
        result = zone_breakdown(shots)
        assert list(result.keys()) == ["Restricted Area"]

    def test_zone_stats_type(self) -> None:
        """Values in the breakdown are ZoneStats instances."""
        shots = [_make_shot(zone="Mid-Range", made=1)]
        result = zone_breakdown(shots)
        assert isinstance(result["Mid-Range"], ZoneStats)

    def test_fga_counts_all_attempts(self) -> None:
        """fga equals total shots in that zone regardless of make/miss."""
        shots = [_make_shot(zone="Mid-Range", made=1)] * 3 + [
            _make_shot(zone="Mid-Range", made=0)
        ] * 2
        result = zone_breakdown(shots)
        assert result["Mid-Range"].fga == 5

    def test_fgm_counts_only_makes(self) -> None:
        """fgm equals only made shots in that zone."""
        shots = [_make_shot(zone="Mid-Range", made=1)] * 3 + [
            _make_shot(zone="Mid-Range", made=0)
        ] * 2
        result = zone_breakdown(shots)
        assert result["Mid-Range"].fgm == 3

    def test_fg_pct_matches_zone_fg_pct(self) -> None:
        """ZoneStats.fg_pct matches calling zone_fg_pct on the filtered list."""
        shots = [_make_shot(zone="Mid-Range", made=1)] * 3 + [
            _make_shot(zone="Mid-Range", made=0)
        ] * 2
        result = zone_breakdown(shots)
        expected = zone_fg_pct([s for s in shots if s.shot_zone_basic == "Mid-Range"])
        assert result["Mid-Range"].fg_pct == pytest.approx(expected)

    def test_multiple_zones_separated(self) -> None:
        """Shots in different zones appear in separate entries."""
        shots = [
            _make_shot(zone="Restricted Area", made=1),
            _make_shot(zone="Mid-Range", made=0),
        ]
        result = zone_breakdown(shots)
        assert "Restricted Area" in result
        assert "Mid-Range" in result
        assert result["Restricted Area"].fga == 1
        assert result["Mid-Range"].fga == 1

    def test_zone_name_stored_on_stats(self) -> None:
        """The zone attribute of ZoneStats matches the key."""
        shots = [_make_shot(zone="Left Corner 3", made=1)]
        result = zone_breakdown(shots)
        assert result["Left Corner 3"].zone == "Left Corner 3"

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=0, max_size=50))
    def test_total_fga_equals_shot_count(self, shots: list) -> None:
        """Total FGA across all zones must equal the number of shots."""
        result = zone_breakdown(shots)
        total_fga = sum(v.fga for v in result.values())
        assert total_fga == len(shots)

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=0, max_size=50))
    def test_total_fgm_equals_made_shot_count(self, shots: list) -> None:
        """Total FGM across all zones must equal the total made shots."""
        result = zone_breakdown(shots)
        total_fgm = sum(v.fgm for v in result.values())
        expected_makes = sum(s.shot_made_flag for s in shots)
        assert total_fgm == expected_makes

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=1, max_size=50))
    def test_fg_pct_in_unit_interval(self, shots: list) -> None:
        """Every zone's fg_pct is in [0.0, 1.0]."""
        result = zone_breakdown(shots)
        for stats in result.values():
            assert stats.fg_pct is not None
            assert 0.0 <= stats.fg_pct <= 1.0

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=1, max_size=50))
    def test_zone_fg_pct_composition(self, shots: list) -> None:
        """zone_fg_pct on filtered shots equals breakdown fg_pct for every zone."""
        result = zone_breakdown(shots)
        for zone, stats in result.items():
            filtered = [s for s in shots if s.shot_zone_basic == zone]
            expected = zone_fg_pct(filtered)
            assert stats.fg_pct == pytest.approx(expected)


# ─── TestShotQualityVsLeague ──────────────────────────────────────────────────


class TestShotQualityVsLeague:
    """Tests for the pure shot_quality_vs_league() delta function."""

    def test_empty_player_shots_returns_empty_dict(self) -> None:
        """No player shots → no zones in the result."""
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]
        assert shot_quality_vs_league([], lg) == {}

    def test_delta_positive_when_player_above_league(self) -> None:
        """Delta > 0 when player FG% exceeds league average in that zone."""
        shots = [_make_shot(zone="Mid-Range", made=1)] * 10  # 100% FG
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]  # 40% league
        result = shot_quality_vs_league(shots, lg)
        assert result["Mid-Range"] is not None
        assert result["Mid-Range"] > 0.0

    def test_delta_negative_when_player_below_league(self) -> None:
        """Delta < 0 when player FG% is below the league average."""
        shots = [_make_shot(zone="Mid-Range", made=0)] * 10  # 0% FG
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]  # 40% league
        result = shot_quality_vs_league(shots, lg)
        assert result["Mid-Range"] is not None
        assert result["Mid-Range"] < 0.0

    def test_delta_zero_when_equal_to_league(self) -> None:
        """Delta is 0.0 when player FG% exactly matches the league average."""
        # League avg is 50% in this zone
        shots = [_make_shot(zone="Mid-Range", made=1)] * 5 + [
            _make_shot(zone="Mid-Range", made=0)
        ] * 5
        lg = [_make_league_zone(zone="Mid-Range", fgm=500, fga=1000)]
        result = shot_quality_vs_league(shots, lg)
        assert result["Mid-Range"] == pytest.approx(0.0)

    def test_zone_absent_from_league_data_returns_none(self) -> None:
        """A zone in player shots but not in league data gets delta=None."""
        shots = [_make_shot(zone="Backcourt", made=1)]
        lg = [_make_league_zone(zone="Mid-Range")]  # Backcourt not present
        result = shot_quality_vs_league(shots, lg)
        assert result["Backcourt"] is None

    def test_only_player_zones_appear_in_result(self) -> None:
        """Zones present in league data but absent from player shots do not appear."""
        shots = [_make_shot(zone="Restricted Area", made=1)]
        lg = [
            _make_league_zone(zone="Restricted Area"),
            _make_league_zone(zone="Mid-Range"),
        ]
        result = shot_quality_vs_league(shots, lg)
        assert "Mid-Range" not in result
        assert "Restricted Area" in result

    def test_multiple_zones_computed_independently(self) -> None:
        """Deltas for different zones are computed independently."""
        shots = [
            _make_shot(zone="Restricted Area", made=1),  # 100%
            _make_shot(zone="Mid-Range", made=0),  # 0%
        ]
        lg = [
            _make_league_zone(zone="Restricted Area", fgm=600, fga=1000),  # 60%
            _make_league_zone(zone="Mid-Range", fgm=400, fga=1000),  # 40%
        ]
        result = shot_quality_vs_league(shots, lg)
        assert result["Restricted Area"] == pytest.approx(0.4)
        assert result["Mid-Range"] == pytest.approx(-0.4)

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=1, max_size=30))
    def test_delta_bounded_in_unit_interval(self, shots: list) -> None:
        """All non-None deltas are in [-1.0, 1.0] since FG% is in [0, 1]."""
        lg = [_make_league_zone(zone=z) for z in _ZONES]
        result = shot_quality_vs_league(shots, lg)
        for delta in result.values():
            if delta is not None:
                assert -1.0 <= delta <= 1.0

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=0, max_size=30))
    def test_result_keys_subset_of_player_zones(self, shots: list) -> None:
        """Result keys are exactly the zones present in player shots."""
        lg = [_make_league_zone(zone=z) for z in _ZONES]
        result = shot_quality_vs_league(shots, lg)
        player_zones = {s.shot_zone_basic for s in shots}
        assert set(result.keys()) == player_zones


# ─── TestGetShotChart ─────────────────────────────────────────────────────────


class TestGetShotChart:
    """Tests for the get_shot_chart() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        """get_shot_chart calls client.get exactly once."""
        from fastbreak.clients.nba import NBAClient

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_shot_chart(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        """player_id is forwarded to the ShotChartDetail endpoint."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.endpoints import ShotChartDetail

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_shot_chart(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ShotChartDetail)
        assert endpoint.player_id == 201939

    async def test_team_id_defaults_to_zero(self, mocker: MockerFixture) -> None:
        """team_id defaults to 0 (all teams) when not specified."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.endpoints import ShotChartDetail

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_shot_chart(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ShotChartDetail)
        assert endpoint.team_id == 0

    async def test_custom_team_id_forwarded(self, mocker: MockerFixture) -> None:
        """A non-zero team_id is forwarded correctly."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.endpoints import ShotChartDetail

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_shot_chart(client, player_id=2544, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ShotChartDetail)
        assert endpoint.team_id == 1610612747

    async def test_context_measure_defaults_to_fga(self, mocker: MockerFixture) -> None:
        """context_measure defaults to 'FGA' for all field goal attempts."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.endpoints import ShotChartDetail

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_shot_chart(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ShotChartDetail)
        assert endpoint.context_measure == "FGA"

    async def test_season_type_forwarded(self, mocker: MockerFixture) -> None:
        """season_type is forwarded to the endpoint."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.endpoints import ShotChartDetail

        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_shot_chart(client, player_id=2544, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ShotChartDetail)
        assert endpoint.season_type == "Playoffs"


# ─── TestGetLeagueShotZones ───────────────────────────────────────────────────


class TestGetLeagueShotZones:
    """Tests for the get_league_shot_zones() async API wrapper."""

    async def test_returns_list_of_league_wide_shot_zones(
        self, mocker: MockerFixture
    ) -> None:
        """Returns the list of LeagueWideShotZone items from the response."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.models.shot_chart_leaguewide import LeagueWideShotZone

        zone = _make_league_zone()
        response = mocker.MagicMock()
        response.league_wide = [zone]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_shot_zones(client)

        assert result == [zone]
        assert isinstance(result[0], LeagueWideShotZone)

    async def test_calls_shot_chart_leaguewide_endpoint(
        self, mocker: MockerFixture
    ) -> None:
        """Uses the ShotChartLeaguewide endpoint under the hood."""
        from fastbreak.clients.nba import NBAClient
        from fastbreak.endpoints import ShotChartLeaguewide

        response = mocker.MagicMock()
        response.league_wide = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_league_shot_zones(client)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ShotChartLeaguewide)

    async def test_empty_response_returns_empty_list(
        self, mocker: MockerFixture
    ) -> None:
        """An API response with no zones returns an empty list."""
        from fastbreak.clients.nba import NBAClient

        response = mocker.MagicMock()
        response.league_wide = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_shot_zones(client)

        assert result == []


# ─── TestXfgPct ───────────────────────────────────────────────────────────────


class TestXfgPct:
    """Tests for the pure xfg_pct() expected-FG% computation function."""

    def test_empty_player_shots_returns_none(self) -> None:
        """No player shots → expected FG% is undefined (returns None)."""
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]
        assert xfg_pct([], lg) is None

    def test_single_zone_uses_league_average(self) -> None:
        """xFG% for shots from one zone equals that zone's league average."""
        shots = [_make_shot(zone="Mid-Range")] * 10
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]  # 40% league
        result = xfg_pct(shots, lg)
        assert result == pytest.approx(0.4)

    def test_two_zones_volume_weighted(self) -> None:
        """xFG% is the FGA-weighted average of per-zone league rates."""
        # 10 shots from RA (60% league) + 10 from Mid-Range (40% league) → 50%
        shots = [_make_shot(zone="Restricted Area")] * 10 + [
            _make_shot(zone="Mid-Range")
        ] * 10
        lg = [
            _make_league_zone(zone="Restricted Area", fgm=600, fga=1000),
            _make_league_zone(zone="Mid-Range", fgm=400, fga=1000),
        ]
        result = xfg_pct(shots, lg)
        assert result == pytest.approx(0.5)

    def test_uneven_zone_volume_weights_toward_heavier_zone(self) -> None:
        """More shots from a zone pull xFG% toward that zone's league rate."""
        # 1 shot RA (60%), 9 shots Mid-Range (40%) → 0.42
        shots = [_make_shot(zone="Restricted Area")] * 1 + [
            _make_shot(zone="Mid-Range")
        ] * 9
        lg = [
            _make_league_zone(zone="Restricted Area", fgm=600, fga=1000),
            _make_league_zone(zone="Mid-Range", fgm=400, fga=1000),
        ]
        result = xfg_pct(shots, lg)
        assert result == pytest.approx(0.42)

    def test_zone_missing_from_league_data_excluded(self) -> None:
        """Shots from a zone not in league data are excluded from xFG%."""
        shots = [_make_shot(zone="Backcourt", made=1)]
        lg = [_make_league_zone(zone="Mid-Range")]
        assert xfg_pct(shots, lg) is None

    def test_partial_zone_match_uses_only_matched_shots(self) -> None:
        """Unmatched zones are dropped; xFG% is computed over matched shots only."""
        shots = [_make_shot(zone="Mid-Range")] * 5 + [_make_shot(zone="Backcourt")] * 5
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]  # 40%
        result = xfg_pct(shots, lg)
        assert result == pytest.approx(0.4)

    def test_precomputed_player_zones_accepted(self) -> None:
        """Passing player_zones= skips re-processing player_shots."""
        shots = [_make_shot(zone="Mid-Range")] * 10
        precomputed = zone_breakdown(shots)
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]
        result = xfg_pct([], lg, player_zones=precomputed)
        assert result == pytest.approx(0.4)

    def test_actual_minus_xfg_isolates_shot_making(self) -> None:
        """actual_fg_pct - xfg_pct > 0 means above-average shot-making."""
        # Player shoots 60% from a zone where league averages 40%
        shots = [_make_shot(zone="Mid-Range", made=1)] * 6 + [
            _make_shot(zone="Mid-Range", made=0)
        ] * 4
        lg = [_make_league_zone(zone="Mid-Range", fgm=400, fga=1000)]
        actual = zone_fg_pct(shots)
        expected = xfg_pct(shots, lg)
        assert actual is not None and expected is not None
        assert actual - expected == pytest.approx(0.2)

    @settings(suppress_health_check=_XDIST)
    @given(shots=_shot_list(min_size=1, max_size=50))
    def test_result_in_unit_interval(self, shots: list) -> None:
        """xFG% is always in [0.0, 1.0] for any non-empty matched shot list."""
        lg = [_make_league_zone(zone=z) for z in _ZONES]
        result = xfg_pct(shots, lg)
        assert result is not None
        assert 0.0 <= result <= 1.0
