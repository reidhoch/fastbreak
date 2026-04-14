"""Rotation analysis — stints, lineups, substitution timeline, minutes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastbreak.league import League

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fastbreak.clients.base import BaseClient
    from fastbreak.models.game_rotation import GameRotationResponse, RotationEntry

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REGULATION_PERIODS = 4
_OT_PERIOD_SECONDS = 300
_TIME_DIVISOR = 10  # API returns tenths of seconds


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PlayerStint:
    """Single stretch of court time for a player."""

    player_id: int
    player_name: str
    in_time: float
    out_time: float
    duration_minutes: float
    points: int | None
    pt_diff: float | None
    usg_pct: float | None


@dataclass(frozen=True, slots=True)
class PlayerMinutes:
    """Aggregated per-player minutes."""

    player_id: int
    player_name: str
    total_minutes: float
    stint_count: int
    avg_stint_minutes: float
    total_points: int
    total_pt_diff: float


@dataclass(frozen=True, slots=True)
class LineupStint:
    """Interval where a specific set of players overlaps on court."""

    player_ids: frozenset[int]
    player_names: tuple[str, ...]
    in_time: float
    out_time: float
    duration_minutes: float


@dataclass(frozen=True, slots=True)
class SubstitutionEvent:
    """A single substitution."""

    time: float
    period: int
    player_in_id: int | None
    player_in_name: str
    player_out_id: int | None
    player_out_name: str


@dataclass(frozen=True, slots=True)
class RotationSummary:
    """Top-level wrapper for a team's rotation data in one game."""

    game_id: str
    team_id: int
    player_stints: tuple[PlayerStint, ...]
    player_minutes: tuple[PlayerMinutes, ...]
    lineup_stints: tuple[LineupStint, ...]
    substitution_events: tuple[SubstitutionEvent, ...]
    total_game_minutes: float


# ---------------------------------------------------------------------------
# Period helper
# ---------------------------------------------------------------------------


def _period_from_seconds(seconds: float, *, league: League = League.NBA) -> int:
    """Derive the period number from seconds since tip-off.

    Periods use half-open intervals ``[start, end)`` so that boundary
    times map to the *next* period, consistent with
    :func:`fastbreak.games.elapsed_game_seconds`:

    - NBA (12-min quarters): Q1: ``[0, 720)``, Q2: ``[720, 1440)``, …
    - WNBA (10-min quarters): Q1: ``[0, 600)``, Q2: ``[600, 1200)``, …
    - ``seconds <= 0`` maps to period 1 (tip-off).
    """
    if seconds <= 0:
        return 1
    quarter_seconds = league.quarter_seconds
    full_regulation = _REGULATION_PERIODS * quarter_seconds
    if seconds < full_regulation:
        return int(seconds // quarter_seconds) + 1
    ot_seconds = seconds - full_regulation
    return _REGULATION_PERIODS + int(ot_seconds // _OT_PERIOD_SECONDS) + 1


# ---------------------------------------------------------------------------
# Pure computation functions
# ---------------------------------------------------------------------------


def player_stints(entries: Sequence[RotationEntry]) -> list[PlayerStint]:
    """Map rotation entries to player stints, preserving input order."""
    return [
        PlayerStint(
            player_id=e.person_id,
            player_name=f"{e.player_first} {e.player_last}",
            in_time=e.in_time_real / _TIME_DIVISOR,
            out_time=e.out_time_real / _TIME_DIVISOR,
            duration_minutes=(e.out_time_real - e.in_time_real) / (_TIME_DIVISOR * 60),
            points=e.player_pts,
            pt_diff=e.pt_diff,
            usg_pct=e.usg_pct,
        )
        for e in entries
    ]


def player_total_minutes(entries: Sequence[RotationEntry]) -> list[PlayerMinutes]:
    """Aggregate per-player minutes, sorted by total_minutes descending."""
    groups: dict[int, list[RotationEntry]] = defaultdict(list)
    for e in entries:
        groups[e.person_id].append(e)

    result: list[PlayerMinutes] = []
    for pid, group in groups.items():
        first = group[0]
        total_min = sum(
            (e.out_time_real - e.in_time_real) / (_TIME_DIVISOR * 60) for e in group
        )
        count = len(group)
        result.append(
            PlayerMinutes(
                player_id=pid,
                player_name=f"{first.player_first} {first.player_last}",
                total_minutes=total_min,
                stint_count=count,
                avg_stint_minutes=total_min / count,
                total_points=sum(e.player_pts or 0 for e in group),
                total_pt_diff=sum(e.pt_diff or 0.0 for e in group),
            )
        )
    return sorted(result, key=lambda m: m.total_minutes, reverse=True)


# Alias for rotation-chart use case.
minutes_distribution = player_total_minutes


def stint_plus_minus(entries: Sequence[RotationEntry]) -> dict[int, float]:
    """Return ``{person_id: total_pt_diff}``.  None → 0.0."""
    totals: dict[int, float] = defaultdict(float)
    for e in entries:
        totals[e.person_id] += e.pt_diff or 0.0
    return dict(totals)


def _make_lineup_stint(
    ids: frozenset[int], names: dict[int, str], start: float, end: float
) -> LineupStint:
    return LineupStint(
        player_ids=ids,
        player_names=tuple(sorted(names[pid] for pid in ids)),
        in_time=start / _TIME_DIVISOR,
        out_time=end / _TIME_DIVISOR,
        duration_minutes=(end - start) / (_TIME_DIVISOR * 60),
    )


type _RawSegment = tuple[frozenset[int], dict[int, str], float, float]


def _sweep_segments(
    entries: Sequence[RotationEntry],
    sorted_boundaries: list[float],
) -> list[_RawSegment]:
    """Sweep consecutive boundary pairs and return raw lineup segments."""
    raw: list[_RawSegment] = []
    for i in range(len(sorted_boundaries) - 1):
        t_start = sorted_boundaries[i]
        t_end = sorted_boundaries[i + 1]
        if t_start == t_end:
            continue

        player_ids: set[int] = set()
        player_names: dict[int, str] = {}
        for e in entries:
            if e.in_time_real <= t_start and e.out_time_real >= t_end:
                player_ids.add(e.person_id)
                player_names[e.person_id] = f"{e.player_first} {e.player_last}"

        if player_ids:
            raw.append((frozenset(player_ids), player_names, t_start, t_end))
    return raw


def lineup_stints(entries: Sequence[RotationEntry]) -> list[LineupStint]:
    """Reconstruct lineup stints using a sweep-line algorithm.

    Collects all time boundaries, sweeps consecutive pairs, determines
    which players are on court in each interval ``[t_start, t_end]``,
    then merges consecutive segments with identical player sets.
    """
    if not entries:
        return []

    boundaries: set[float] = set()
    for e in entries:
        boundaries.add(e.in_time_real)
        boundaries.add(e.out_time_real)

    raw = _sweep_segments(entries, sorted(boundaries))
    if not raw:
        return []

    # Merge consecutive segments with identical player sets.
    merged: list[LineupStint] = []
    cur_ids, cur_names, cur_start, cur_end = raw[0]
    for fset, names, t_start, t_end in raw[1:]:
        if fset == cur_ids:
            cur_end = t_end
        else:
            merged.append(_make_lineup_stint(cur_ids, cur_names, cur_start, cur_end))
            cur_ids, cur_names, cur_start, cur_end = fset, names, t_start, t_end

    merged.append(_make_lineup_stint(cur_ids, cur_names, cur_start, cur_end))
    return merged


def rotation_timeline(entries: Sequence[RotationEntry]) -> list[SubstitutionEvent]:
    """Build a chronological substitution timeline from rotation entries.

    At each time point, pairs "enter" events with "exit" events in
    input order.  When multiple substitutions happen simultaneously,
    the pairing is arbitrary — the API does not encode which player
    replaced which.  Unpaired events use ``None`` for the missing side.
    """
    if not entries:
        return []

    # Collect enter/exit events keyed by time.
    enters: dict[float, list[RotationEntry]] = defaultdict(list)
    exits: dict[float, list[RotationEntry]] = defaultdict(list)
    for e in entries:
        enters[e.in_time_real].append(e)
        exits[e.out_time_real].append(e)

    all_times = sorted(set(enters) | set(exits))
    events: list[SubstitutionEvent] = []

    for t in all_times:
        ins = list(enters.get(t, []))
        outs = list(exits.get(t, []))
        t_sec = t / _TIME_DIVISOR
        period = _period_from_seconds(t_sec)

        # Pair ins/outs.
        while ins and outs:
            ei = ins.pop(0)
            eo = outs.pop(0)
            events.append(
                SubstitutionEvent(
                    time=t_sec,
                    period=period,
                    player_in_id=ei.person_id,
                    player_in_name=f"{ei.player_first} {ei.player_last}",
                    player_out_id=eo.person_id,
                    player_out_name=f"{eo.player_first} {eo.player_last}",
                )
            )

        # Remaining unpaired enters (game start, period start).
        events.extend(
            SubstitutionEvent(
                time=t_sec,
                period=period,
                player_in_id=ei.person_id,
                player_in_name=f"{ei.player_first} {ei.player_last}",
                player_out_id=None,
                player_out_name="",
            )
            for ei in ins
        )

        # Remaining unpaired exits (game end, period end).
        events.extend(
            SubstitutionEvent(
                time=t_sec,
                period=period,
                player_in_id=None,
                player_in_name="",
                player_out_id=eo.person_id,
                player_out_name=f"{eo.player_first} {eo.player_last}",
            )
            for eo in outs
        )

    return events


# ---------------------------------------------------------------------------
# Async fetchers
# ---------------------------------------------------------------------------


async def get_game_rotations(
    client: BaseClient,
    game_id: str,
) -> GameRotationResponse:
    """Fetch rotation data for a game."""
    from fastbreak.endpoints.game_rotation import GameRotation  # noqa: PLC0415

    return await client.get(GameRotation(game_id=game_id))


async def get_rotation_summary(
    client: BaseClient,
    game_id: str,
    *,
    team_id: int,
) -> RotationSummary:
    """Fetch rotations and build a full summary for one team.

    Raises :class:`ValueError` if *team_id* is not found in either
    the home or away rotation entries.
    """
    response = await get_game_rotations(client, game_id)

    entries: list[RotationEntry] | None = None
    if response.home_team and response.home_team[0].team_id == team_id:
        entries = list(response.home_team)
    elif response.away_team and response.away_team[0].team_id == team_id:
        entries = list(response.away_team)

    if entries is None:
        msg = f"team_id {team_id} not found in game {game_id} rotations"
        raise ValueError(msg)

    total_min = (
        max(e.out_time_real for e in entries) / (_TIME_DIVISOR * 60) if entries else 0.0
    )

    return RotationSummary(
        game_id=game_id,
        team_id=team_id,
        player_stints=tuple(player_stints(entries)),
        player_minutes=tuple(player_total_minutes(entries)),
        lineup_stints=tuple(lineup_stints(entries)),
        substitution_events=tuple(rotation_timeline(entries)),
        total_game_minutes=total_min,
    )
