"""Tests for the rotations utility module."""

from __future__ import annotations

import dataclasses

import pytest
from hypothesis import given, settings, strategies as st

from pytest_mock import MockerFixture

from fastbreak.models.game_rotation import GameRotationResponse, RotationEntry
from fastbreak.rotations import (
    LineupStint,
    PlayerMinutes,
    PlayerStint,
    RotationSummary,
    SubstitutionEvent,
    _period_from_seconds,
    get_game_rotations,
    get_rotation_summary,
    lineup_stints,
    player_stints,
    player_total_minutes,
    rotation_timeline,
    stint_plus_minus,
)


# ---------------------------------------------------------------------------
# TestDataclassFrozenSlots
# ---------------------------------------------------------------------------


class TestDataclassFrozenSlots:
    """All five dataclasses must be frozen and use __slots__."""

    @pytest.mark.parametrize(
        "cls",
        [PlayerStint, PlayerMinutes, LineupStint, SubstitutionEvent, RotationSummary],
    )
    def test_is_frozen(self, cls):
        assert dataclasses.fields(cls)  # is a dataclass
        instance = _make_instance(cls)
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(instance, dataclasses.fields(cls)[0].name, None)

    @pytest.mark.parametrize(
        "cls",
        [PlayerStint, PlayerMinutes, LineupStint, SubstitutionEvent, RotationSummary],
    )
    def test_has_slots(self, cls):
        assert hasattr(cls, "__slots__")


# ---------------------------------------------------------------------------
# TestPeriodFromSeconds
# ---------------------------------------------------------------------------


class TestPeriodFromSeconds:
    def test_negative_is_period_1(self):
        assert _period_from_seconds(-100) == 1

    def test_zero_is_period_1(self):
        assert _period_from_seconds(0) == 1

    def test_mid_q1(self):
        assert _period_from_seconds(360) == 1

    def test_end_q1_boundary(self):
        assert _period_from_seconds(720) == 1

    def test_start_q2(self):
        assert _period_from_seconds(720.1) == 2

    def test_end_regulation(self):
        assert _period_from_seconds(2880) == 4

    def test_start_ot1(self):
        assert _period_from_seconds(2880.1) == 5

    def test_end_ot1(self):
        assert _period_from_seconds(3180) == 5

    def test_start_ot2(self):
        assert _period_from_seconds(3180.1) == 6


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_instance(cls):
    """Build a minimal instance of any of the five dataclasses."""
    if cls is PlayerStint:
        return PlayerStint(
            player_id=1,
            player_name="A B",
            in_time=0.0,
            out_time=720.0,
            duration_minutes=12.0,
            points=10,
            pt_diff=5.0,
            usg_pct=0.2,
        )
    if cls is PlayerMinutes:
        return PlayerMinutes(
            player_id=1,
            player_name="A B",
            total_minutes=12.0,
            stint_count=1,
            avg_stint_minutes=12.0,
            total_points=10,
            total_pt_diff=5.0,
        )
    if cls is LineupStint:
        return LineupStint(
            player_ids=frozenset({1}),
            player_names=("A B",),
            in_time=0.0,
            out_time=720.0,
            duration_minutes=12.0,
        )
    if cls is SubstitutionEvent:
        return SubstitutionEvent(
            time=360.0,
            period=1,
            player_in_id=1,
            player_in_name="A",
            player_out_id=2,
            player_out_name="B",
        )
    if cls is RotationSummary:
        return RotationSummary(
            game_id="0022500571",
            team_id=100,
            player_stints=(),
            player_minutes=(),
            lineup_stints=(),
            substitution_events=(),
            total_game_minutes=0.0,
        )
    msg = f"Unknown class {cls}"
    raise TypeError(msg)


def _make_rotation_entry(
    *,
    person_id: int = 1,
    player_first: str = "First",
    player_last: str = "Last",
    in_time_real: float = 0.0,
    out_time_real: float = 7200.0,
    player_pts: int | None = 10,
    pt_diff: float | None = 5.0,
    usg_pct: float | None = 0.2,
    game_id: str = "0022500571",
    team_id: int = 100,
    team_city: str = "Test",
    team_name: str = "Team",
) -> RotationEntry:
    """Build a RotationEntry with sensible defaults."""
    return RotationEntry.model_validate(
        {
            "GAME_ID": game_id,
            "TEAM_ID": team_id,
            "TEAM_CITY": team_city,
            "TEAM_NAME": team_name,
            "PERSON_ID": person_id,
            "PLAYER_FIRST": player_first,
            "PLAYER_LAST": player_last,
            "IN_TIME_REAL": in_time_real,
            "OUT_TIME_REAL": out_time_real,
            "PLAYER_PTS": player_pts,
            "PT_DIFF": pt_diff,
            "USG_PCT": usg_pct,
        }
    )


# ---------------------------------------------------------------------------
# TestPlayerStints
# ---------------------------------------------------------------------------


class TestPlayerStints:
    def test_empty_entries(self):
        assert player_stints([]) == []

    def test_single_entry_maps_correctly(self):
        entry = _make_rotation_entry(
            person_id=42, player_first="LeBron", player_last="James"
        )
        result = player_stints([entry])
        assert len(result) == 1
        assert result[0].player_id == 42

    def test_player_name_format(self):
        entry = _make_rotation_entry(player_first="Stephen", player_last="Curry")
        result = player_stints([entry])
        assert result[0].player_name == "Stephen Curry"

    def test_duration_calculation(self):
        entry = _make_rotation_entry(in_time_real=0.0, out_time_real=7200.0)
        result = player_stints([entry])
        assert result[0].duration_minutes == 12.0

    def test_duration_short_stint(self):
        entry = _make_rotation_entry(in_time_real=0.0, out_time_real=600.0)
        result = player_stints([entry])
        assert result[0].duration_minutes == 1.0

    def test_none_fields_preserved(self):
        entry = _make_rotation_entry(player_pts=None, pt_diff=None, usg_pct=None)
        result = player_stints([entry])
        assert result[0].points is None
        assert result[0].pt_diff is None
        assert result[0].usg_pct is None

    def test_multiple_entries_order_preserved(self):
        e1 = _make_rotation_entry(person_id=1, in_time_real=0.0, out_time_real=3600.0)
        e2 = _make_rotation_entry(person_id=2, in_time_real=0.0, out_time_real=7200.0)
        result = player_stints([e1, e2])
        assert [s.player_id for s in result] == [1, 2]

    def test_zero_duration_stint(self):
        entry = _make_rotation_entry(in_time_real=3600.0, out_time_real=3600.0)
        result = player_stints([entry])
        assert result[0].duration_minutes == 0.0


# ---------------------------------------------------------------------------
# TestPlayerTotalMinutes
# ---------------------------------------------------------------------------


class TestPlayerTotalMinutes:
    def test_empty(self):
        assert player_total_minutes([]) == []

    def test_single_stint(self):
        entry = _make_rotation_entry(
            person_id=1,
            in_time_real=0.0,
            out_time_real=7200.0,
            player_pts=10,
            pt_diff=5.0,
        )
        result = player_total_minutes([entry])
        assert len(result) == 1
        assert result[0].total_minutes == 12.0
        assert result[0].stint_count == 1

    def test_two_stints_summed(self):
        e1 = _make_rotation_entry(
            person_id=1,
            in_time_real=0.0,
            out_time_real=3600.0,
            player_pts=5,
            pt_diff=2.0,
        )
        e2 = _make_rotation_entry(
            person_id=1,
            in_time_real=7200.0,
            out_time_real=10800.0,
            player_pts=8,
            pt_diff=3.0,
        )
        result = player_total_minutes([e1, e2])
        assert len(result) == 1
        assert result[0].total_minutes == 12.0
        assert result[0].total_points == 13
        assert result[0].total_pt_diff == 5.0

    def test_two_players_sorted_by_minutes_desc(self):
        e1 = _make_rotation_entry(
            person_id=1, player_first="A", in_time_real=0.0, out_time_real=3600.0
        )
        e2 = _make_rotation_entry(
            person_id=2, player_first="B", in_time_real=0.0, out_time_real=7200.0
        )
        result = player_total_minutes([e1, e2])
        assert result[0].player_id == 2  # more minutes
        assert result[1].player_id == 1

    def test_avg_stint_minutes_correct(self):
        e1 = _make_rotation_entry(person_id=1, in_time_real=0.0, out_time_real=3600.0)
        e2 = _make_rotation_entry(
            person_id=1, in_time_real=7200.0, out_time_real=10800.0
        )
        result = player_total_minutes([e1, e2])
        assert result[0].avg_stint_minutes == 6.0

    def test_none_pts_treated_as_zero(self):
        entry = _make_rotation_entry(person_id=1, player_pts=None)
        result = player_total_minutes([entry])
        assert result[0].total_points == 0

    def test_none_pt_diff_treated_as_zero(self):
        entry = _make_rotation_entry(person_id=1, pt_diff=None)
        result = player_total_minutes([entry])
        assert result[0].total_pt_diff == 0.0

    def test_mixed_none_and_values(self):
        e1 = _make_rotation_entry(person_id=1, player_pts=None, pt_diff=None)
        e2 = _make_rotation_entry(person_id=1, player_pts=10, pt_diff=3.0)
        result = player_total_minutes([e1, e2])
        assert result[0].total_points == 10
        assert result[0].total_pt_diff == 3.0

    def test_single_stint_avg_equals_total(self):
        entry = _make_rotation_entry(
            person_id=1, in_time_real=0.0, out_time_real=6000.0
        )
        result = player_total_minutes([entry])
        assert result[0].avg_stint_minutes == result[0].total_minutes


# ---------------------------------------------------------------------------
# TestStintPlusMinus
# ---------------------------------------------------------------------------


class TestStintPlusMinus:
    def test_empty(self):
        assert stint_plus_minus([]) == {}

    def test_single(self):
        entry = _make_rotation_entry(person_id=1, pt_diff=5.0)
        result = stint_plus_minus([entry])
        assert result == {1: 5.0}

    def test_summed(self):
        e1 = _make_rotation_entry(person_id=1, pt_diff=3.0)
        e2 = _make_rotation_entry(person_id=1, pt_diff=-2.0)
        result = stint_plus_minus([e1, e2])
        assert result == {1: 1.0}

    def test_none_treated_as_zero(self):
        entry = _make_rotation_entry(person_id=1, pt_diff=None)
        result = stint_plus_minus([entry])
        assert result == {1: 0.0}

    def test_two_players(self):
        e1 = _make_rotation_entry(person_id=1, pt_diff=5.0)
        e2 = _make_rotation_entry(person_id=2, pt_diff=-3.0)
        result = stint_plus_minus([e1, e2])
        assert result == {1: 5.0, 2: -3.0}


# ---------------------------------------------------------------------------
# TestLineupStints
# ---------------------------------------------------------------------------


def _five_starters(
    in_time: float = 0.0, out_time: float = 7200.0
) -> list[RotationEntry]:
    """Five players all on court for the same interval."""
    return [
        _make_rotation_entry(
            person_id=i,
            player_first=f"P{i}",
            player_last="X",
            in_time_real=in_time,
            out_time_real=out_time,
        )
        for i in range(1, 6)
    ]


class TestLineupStints:
    def test_empty_entries(self):
        assert lineup_stints([]) == []

    def test_five_players_full_quarter(self):
        entries = _five_starters(0.0, 7200.0)
        result = lineup_stints(entries)
        assert len(result) == 1
        assert result[0].player_ids == frozenset({1, 2, 3, 4, 5})
        assert result[0].duration_minutes == 12.0

    def test_five_players_with_sub(self):
        # 5 starters for first 6 min, then player 5 out, player 6 in
        entries = _five_starters(0.0, 3600.0)
        entries.append(
            _make_rotation_entry(
                person_id=6,
                player_first="P6",
                player_last="X",
                in_time_real=3600.0,
                out_time_real=7200.0,
            )
        )
        # Extend starters 1-4 to full quarter
        for i in range(1, 5):
            entries.append(
                _make_rotation_entry(
                    person_id=i,
                    player_first=f"P{i}",
                    player_last="X",
                    in_time_real=3600.0,
                    out_time_real=7200.0,
                )
            )
        result = lineup_stints(entries)
        assert len(result) == 2
        assert result[0].player_ids == frozenset({1, 2, 3, 4, 5})
        assert result[1].player_ids == frozenset({1, 2, 3, 4, 6})

    def test_player_ids_as_frozenset(self):
        entries = _five_starters()
        result = lineup_stints(entries)
        assert isinstance(result[0].player_ids, frozenset)

    def test_player_names_sorted_alphabetically(self):
        entries = [
            _make_rotation_entry(person_id=1, player_first="Zach", player_last="B"),
            _make_rotation_entry(person_id=2, player_first="Adam", player_last="A"),
            _make_rotation_entry(person_id=3, player_first="Mike", player_last="C"),
            _make_rotation_entry(person_id=4, player_first="Luke", player_last="D"),
            _make_rotation_entry(person_id=5, player_first="John", player_last="E"),
        ]
        result = lineup_stints(entries)
        assert result[0].player_names == tuple(sorted(result[0].player_names))

    def test_duration_minutes_correct(self):
        entries = _five_starters(0.0, 3600.0)
        result = lineup_stints(entries)
        assert result[0].duration_minutes == 6.0

    def test_zero_duration_segments_skipped(self):
        # Two groups with a zero-length boundary point between them
        entries = _five_starters(0.0, 3600.0)
        entries.extend(_five_starters(3600.0, 7200.0))
        result = lineup_stints(entries)
        # Should merge since same players, or at minimum no zero-duration stints
        for stint in result:
            assert stint.duration_minutes > 0

    def test_consecutive_same_lineup_merged(self):
        # Same 5 players in two consecutive stints
        entries = _five_starters(0.0, 3600.0)
        entries.extend(_five_starters(3600.0, 7200.0))
        result = lineup_stints(entries)
        assert len(result) == 1
        assert result[0].duration_minutes == 12.0

    def test_ot_game_times(self):
        entries = _five_starters(28800.0, 31800.0)
        result = lineup_stints(entries)
        assert len(result) == 1
        assert result[0].duration_minutes == 5.0

    def test_fewer_than_five_players(self):
        # Only 3 players — should still produce a lineup stint
        entries = [
            _make_rotation_entry(person_id=i, in_time_real=0.0, out_time_real=7200.0)
            for i in range(1, 4)
        ]
        result = lineup_stints(entries)
        assert len(result) == 1
        assert len(result[0].player_ids) == 3

    def test_chronological_order(self):
        entries = _five_starters(0.0, 3600.0)
        sub_entries = [
            _make_rotation_entry(
                person_id=i,
                player_first=f"P{i}",
                player_last="X",
                in_time_real=3600.0,
                out_time_real=7200.0,
            )
            for i in [1, 2, 3, 4, 6]
        ]
        entries.extend(sub_entries)
        result = lineup_stints(entries)
        for i in range(len(result) - 1):
            assert result[i].in_time <= result[i + 1].in_time

    def test_non_overlapping_players(self):
        # Two players with non-overlapping times: no segment where both are on court
        e1 = _make_rotation_entry(person_id=1, in_time_real=0.0, out_time_real=3600.0)
        e2 = _make_rotation_entry(
            person_id=2, in_time_real=3600.0, out_time_real=7200.0
        )
        result = lineup_stints([e1, e2])
        # Each player on court alone in their segment
        assert len(result) == 2
        assert result[0].player_ids == frozenset({1})
        assert result[1].player_ids == frozenset({2})


# ---------------------------------------------------------------------------
# TestRotationTimeline
# ---------------------------------------------------------------------------


class TestRotationTimeline:
    def test_empty_entries(self):
        assert rotation_timeline([]) == []

    def test_game_start_events(self):
        entries = _five_starters(0.0, 7200.0)
        result = rotation_timeline(entries)
        starts = [e for e in result if e.time == 0.0]
        assert len(starts) == 5
        for ev in starts:
            assert ev.player_out_id is None

    def test_mid_game_substitution(self):
        # Player 5 exits at 360s, player 6 enters at 360s
        entries = [
            _make_rotation_entry(
                person_id=5,
                player_first="P5",
                player_last="X",
                in_time_real=0.0,
                out_time_real=3600.0,
            ),
            _make_rotation_entry(
                person_id=6,
                player_first="P6",
                player_last="X",
                in_time_real=3600.0,
                out_time_real=7200.0,
            ),
        ]
        mid_events = [e for e in rotation_timeline(entries) if e.time == 360.0]
        assert len(mid_events) == 1
        assert mid_events[0].player_in_id == 6
        assert mid_events[0].player_out_id == 5

    def test_period_derived_correctly(self):
        entries = _five_starters(0.0, 7200.0)
        result = rotation_timeline(entries)
        for ev in result:
            if ev.time == 0.0:
                assert ev.period == 1

    def test_chronological_order(self):
        entries = [
            _make_rotation_entry(person_id=1, in_time_real=0.0, out_time_real=3600.0),
            _make_rotation_entry(
                person_id=2, in_time_real=3600.0, out_time_real=7200.0
            ),
        ]
        result = rotation_timeline(entries)
        for i in range(len(result) - 1):
            assert result[i].time <= result[i + 1].time

    def test_ot_period_derivation(self):
        entries = _five_starters(28800.0, 31800.0)
        result = rotation_timeline(entries)
        starts = [e for e in result if e.time == 2880.0]
        for ev in starts:
            assert ev.period == 4  # 2880 is end of Q4

    def test_game_end_events(self):
        entries = _five_starters(0.0, 7200.0)
        result = rotation_timeline(entries)
        ends = [e for e in result if e.time == 720.0]
        assert len(ends) == 5
        for ev in ends:
            assert ev.player_in_id is None

    def test_multiple_subs_at_same_time(self):
        # Two subs at the same time
        entries = [
            _make_rotation_entry(person_id=1, in_time_real=0.0, out_time_real=3600.0),
            _make_rotation_entry(person_id=2, in_time_real=0.0, out_time_real=3600.0),
            _make_rotation_entry(
                person_id=3, in_time_real=3600.0, out_time_real=7200.0
            ),
            _make_rotation_entry(
                person_id=4, in_time_real=3600.0, out_time_real=7200.0
            ),
        ]
        result = rotation_timeline(entries)
        mid_events = [e for e in result if e.time == 360.0]
        assert len(mid_events) == 2
        ins = {e.player_in_id for e in mid_events}
        outs = {e.player_out_id for e in mid_events}
        assert ins == {3, 4}
        assert outs == {1, 2}


# ---------------------------------------------------------------------------
# TestGetGameRotations
# ---------------------------------------------------------------------------


def _make_mock_response(
    home_entries: list[RotationEntry] | None = None,
    away_entries: list[RotationEntry] | None = None,
) -> GameRotationResponse:
    return GameRotationResponse(
        home_team=home_entries or [],
        away_team=away_entries or [],
    )


class TestGetGameRotations:
    async def test_calls_client_get(self, mocker: MockerFixture):
        response = _make_mock_response()
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        result = await get_game_rotations(client, game_id="0022500571")
        client.get.assert_called_once()
        assert result is response

    async def test_passes_game_id(self, mocker: MockerFixture):
        response = _make_mock_response()
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        await get_game_rotations(client, game_id="0022500999")
        endpoint = client.get.call_args[0][0]
        assert endpoint.game_id == "0022500999"

    async def test_returns_game_rotation_response(self, mocker: MockerFixture):
        response = _make_mock_response()
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        result = await get_game_rotations(client, game_id="0022500571")
        assert isinstance(result, GameRotationResponse)

    async def test_uses_game_rotation_endpoint(self, mocker: MockerFixture):
        from fastbreak.endpoints.game_rotation import GameRotation

        response = _make_mock_response()
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        await get_game_rotations(client, game_id="0022500571")
        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, GameRotation)


# ---------------------------------------------------------------------------
# TestGetRotationSummary
# ---------------------------------------------------------------------------


class TestGetRotationSummary:
    def _make_team_entries(self) -> list[RotationEntry]:
        return _five_starters(0.0, 7200.0)

    async def test_returns_rotation_summary(self, mocker: MockerFixture):
        entries = self._make_team_entries()
        response = _make_mock_response(home_entries=entries)
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        result = await get_rotation_summary(client, "0022500571", team_id=100)
        assert isinstance(result, RotationSummary)

    async def test_game_id_preserved(self, mocker: MockerFixture):
        entries = self._make_team_entries()
        response = _make_mock_response(home_entries=entries)
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        result = await get_rotation_summary(client, "0022500571", team_id=100)
        assert result.game_id == "0022500571"

    async def test_selects_home_team(self, mocker: MockerFixture):
        home = [
            _make_rotation_entry(
                person_id=i, team_id=100, in_time_real=0.0, out_time_real=7200.0
            )
            for i in range(1, 6)
        ]
        away = [
            _make_rotation_entry(
                person_id=i, team_id=200, in_time_real=0.0, out_time_real=7200.0
            )
            for i in range(6, 11)
        ]
        response = _make_mock_response(home_entries=home, away_entries=away)
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        result = await get_rotation_summary(client, "0022500571", team_id=100)
        assert result.team_id == 100
        assert len(result.player_stints) == 5

    async def test_selects_away_team(self, mocker: MockerFixture):
        home = [
            _make_rotation_entry(
                person_id=i, team_id=100, in_time_real=0.0, out_time_real=7200.0
            )
            for i in range(1, 6)
        ]
        away = [
            _make_rotation_entry(
                person_id=i, team_id=200, in_time_real=0.0, out_time_real=7200.0
            )
            for i in range(6, 11)
        ]
        response = _make_mock_response(home_entries=home, away_entries=away)
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        result = await get_rotation_summary(client, "0022500571", team_id=200)
        assert result.team_id == 200
        # away has person_ids 6-10
        ids = {s.player_id for s in result.player_stints}
        assert ids == {6, 7, 8, 9, 10}

    async def test_raises_for_unknown_team_id(self, mocker: MockerFixture):
        entries = [_make_rotation_entry(person_id=1, team_id=100)]
        response = _make_mock_response(home_entries=entries)
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        with pytest.raises(ValueError, match="999"):
            await get_rotation_summary(client, "0022500571", team_id=999)

    async def test_empty_entries_zero_minutes(self, mocker: MockerFixture):
        response = _make_mock_response()
        client = mocker.AsyncMock()
        client.get = mocker.AsyncMock(return_value=response)
        with pytest.raises(ValueError):
            await get_rotation_summary(client, "0022500571", team_id=100)


# ---------------------------------------------------------------------------
# TestRotationsProperties (Hypothesis)
# ---------------------------------------------------------------------------


_entry_strategy = st.builds(
    _make_rotation_entry,
    person_id=st.integers(min_value=1, max_value=8),
    in_time_real=st.floats(
        min_value=0.0, max_value=28800.0, allow_nan=False, allow_infinity=False
    ),
    out_time_real=st.floats(
        min_value=0.0, max_value=28800.0, allow_nan=False, allow_infinity=False
    ),
    player_pts=st.one_of(st.none(), st.integers(min_value=0, max_value=30)),
    pt_diff=st.one_of(
        st.none(),
        st.floats(
            min_value=-20.0, max_value=20.0, allow_nan=False, allow_infinity=False
        ),
    ),
    usg_pct=st.one_of(
        st.none(),
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    ),
).filter(lambda e: e.in_time_real <= e.out_time_real)


class TestRotationsProperties:
    @given(entries=st.lists(_entry_strategy, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_stint_durations_non_negative(self, entries):
        for s in player_stints(entries):
            assert s.duration_minutes >= 0

    @given(entries=st.lists(_entry_strategy, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_total_minutes_non_negative(self, entries):
        for m in player_total_minutes(entries):
            assert m.total_minutes >= 0

    @given(entries=st.lists(_entry_strategy, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_avg_lte_total(self, entries):
        for m in player_total_minutes(entries):
            assert m.avg_stint_minutes <= m.total_minutes + 1e-9

    @given(entries=st.lists(_entry_strategy, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_stint_count_equals_entry_count(self, entries):
        minutes_list = player_total_minutes(entries)
        total_stints = sum(m.stint_count for m in minutes_list)
        assert total_stints == len(entries)

    @given(entries=st.lists(_entry_strategy, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_lineup_stints_chronological(self, entries):
        result = lineup_stints(entries)
        for i in range(len(result) - 1):
            assert result[i].in_time <= result[i + 1].in_time
