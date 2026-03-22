"""Hot hand analysis -- streak detection with Miller-Sanjurjo bias correction.

Extracts sequential shot outcomes from play-by-play data, computes conditional
shooting probabilities after *k*-consecutive-make streaks, and applies the
Miller-Sanjurjo (2018) bias correction to the naive estimator.

Pure computation functions operate on boolean sequences (like ``metrics.py``).
The PBP extraction layer and async wrappers follow the ``transition.py`` pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import log2
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.play_by_play import PlayByPlayAction

_DEFAULT_K = 3
"""Default streak length for conditioning (3 consecutive makes)."""

_MIN_STREAK_OPPORTUNITIES = 3
"""Minimum streak opportunities required to compute a score."""

_SHOT_RESULT_MADE = "Made"
"""The ``shotResult`` value the NBA PBP API uses for a made field goal."""


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ShotSequence:
    """A player's sequential field goal outcomes.

    When produced by ``merge_sequences``, may span multiple games.
    """

    player_id: int
    player_name: str
    team_id: int
    shots: tuple[bool, ...]


@dataclass(frozen=True, slots=True)
class StreakCounts:
    """Raw streak counting results before bias correction."""

    k: int
    n: int
    streak_opportunities: int
    makes_after_streak: int
    misses_after_streak: int
    naive_p: float | None


@dataclass(frozen=True, slots=True)
class HotHandResult:
    """Bias-corrected hot hand analysis for a single player."""

    player_id: int
    player_name: str
    k: int
    n: int
    baseline_p: float | None
    naive_p: float | None
    bias_correction: float | None
    corrected_p: float | None
    delta: float | None
    streak_opportunities: int
    score: float | None


@dataclass(frozen=True, slots=True)
class HotHandAnalysis:
    """Full hot hand analysis for a single game."""

    game_id: str
    sequences: tuple[ShotSequence, ...]
    results: tuple[HotHandResult, ...]


# ---------------------------------------------------------------------------
# Internal accumulator
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _PlayerAccumulator:
    """Mutable accumulator for building a player's shot sequence."""

    player_name: str = ""
    team_id: int = 0
    shots: list[bool] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pure math functions
# ---------------------------------------------------------------------------


def miller_sanjurjo_bias(p: float, n: int, k: int) -> float | None:
    """Compute the Miller-Sanjurjo (2018) expected bias correction term.

    For a Bernoulli(*p*) sequence of length *n*, the naive estimator of
    P(make | *k* consecutive makes) has an expected downward bias. This
    returns the correction term to **add** to the naive estimate.

    Uses the first-order approximation: ``p * (1 - p) / (n - k)``.

    Returns ``None`` when *n* ≤ *k* (no post-streak position exists).
    """
    if n <= k:
        return None
    return p * (1.0 - p) / (n - k)


def count_streaks(
    shots: tuple[bool, ...],
    k: int = _DEFAULT_K,
) -> StreakCounts:
    """Count makes and misses after *k*-consecutive-make streaks.

    Walks through the shot sequence. At each position *i* ≥ *k*, checks
    whether the previous *k* shots are all makes. If so, records the
    shot at position *i*.

    Raises ``ValueError`` if *k* < 1.
    """
    if k < 1:
        msg = f"k must be >= 1, got {k}"
        raise ValueError(msg)
    n = len(shots)
    makes = 0
    misses = 0

    for i in range(k, n):
        if all(shots[i - k : i]):
            if shots[i]:
                makes += 1
            else:
                misses += 1

    opportunities = makes + misses
    naive_p: float | None = None
    if opportunities > 0:
        naive_p = makes / opportunities

    return StreakCounts(
        k=k,
        n=n,
        streak_opportunities=opportunities,
        makes_after_streak=makes,
        misses_after_streak=misses,
        naive_p=naive_p,
    )


def hot_hand_score(
    delta: float,
    streak_opportunities: int,
    min_opportunities: int = _MIN_STREAK_OPPORTUNITIES,
) -> float | None:
    """Compute a composite hot hand score.

    Returns ``None`` when *streak_opportunities* < *min_opportunities*.
    The score scales the corrected delta by the log of opportunities:

        ``score = delta * 100 * log₂(1 + streak_opportunities)``
    """
    if streak_opportunities < min_opportunities:
        return None
    return delta * 100.0 * log2(1.0 + streak_opportunities)


def hot_hand_result(
    player_id: int,
    player_name: str,
    shots: tuple[bool, ...],
    k: int = _DEFAULT_K,
    min_opportunities: int = _MIN_STREAK_OPPORTUNITIES,
) -> HotHandResult:
    """Compute the bias-corrected hot hand analysis for a shot sequence.

    Orchestrates :func:`count_streaks`, :func:`miller_sanjurjo_bias`,
    and :func:`hot_hand_score` into a single result.
    """
    counts = count_streaks(shots, k)
    n = counts.n

    baseline_p: float | None = None
    if n > 0:
        baseline_p = sum(shots) / n

    bias: float | None = None
    if baseline_p is not None:
        bias = miller_sanjurjo_bias(baseline_p, n, k)

    corrected_p: float | None = None
    if counts.naive_p is not None and bias is not None:
        corrected_p = counts.naive_p + bias

    delta: float | None = None
    if corrected_p is not None and baseline_p is not None:
        delta = corrected_p - baseline_p

    score: float | None = None
    if delta is not None:
        score = hot_hand_score(delta, counts.streak_opportunities, min_opportunities)

    return HotHandResult(
        player_id=player_id,
        player_name=player_name,
        k=k,
        n=n,
        baseline_p=baseline_p,
        naive_p=counts.naive_p,
        bias_correction=bias,
        corrected_p=corrected_p,
        delta=delta,
        streak_opportunities=counts.streak_opportunities,
        score=score,
    )


# ---------------------------------------------------------------------------
# PBP extraction
# ---------------------------------------------------------------------------


def extract_shot_sequences(
    actions: list[PlayByPlayAction],
) -> list[ShotSequence]:
    """Extract per-player sequential shot outcomes from play-by-play data.

    Walks the action list in order and records each field goal attempt
    (``isFieldGoal == 1``) as a make or miss for the shooting player.
    Actions with ``teamId == 0`` (game events) are skipped.
    """
    accumulators: dict[int, _PlayerAccumulator] = {}

    for action in actions:
        if action.teamId == 0:
            continue
        if action.isFieldGoal != 1:
            continue

        pid = action.personId
        if pid not in accumulators:
            accumulators[pid] = _PlayerAccumulator(
                player_name=action.playerName,
                team_id=action.teamId,
            )

        accumulators[pid].shots.append(action.shotResult == _SHOT_RESULT_MADE)

    return sorted(
        (
            ShotSequence(
                player_id=pid,
                player_name=acc.player_name,
                team_id=acc.team_id,
                shots=tuple(acc.shots),
            )
            for pid, acc in accumulators.items()
        ),
        key=lambda s: s.player_id,
    )


def merge_sequences(
    game_sequences: list[list[ShotSequence]],
) -> list[ShotSequence]:
    """Merge per-player shot sequences from multiple games.

    Groups by ``player_id`` and concatenates shots tuples in the order
    the games are provided. Uses the first-seen ``player_name`` and
    ``team_id`` for each player. Useful for season-level hot hand analysis.
    """
    merged: dict[int, _PlayerAccumulator] = {}

    for sequences in game_sequences:
        for seq in sequences:
            if seq.player_id not in merged:
                merged[seq.player_id] = _PlayerAccumulator(
                    player_name=seq.player_name,
                    team_id=seq.team_id,
                )
            merged[seq.player_id].shots.extend(seq.shots)

    return sorted(
        (
            ShotSequence(
                player_id=pid,
                player_name=acc.player_name,
                team_id=acc.team_id,
                shots=tuple(acc.shots),
            )
            for pid, acc in merged.items()
        ),
        key=lambda s: s.player_id,
    )


# ---------------------------------------------------------------------------
# Async wrappers
# ---------------------------------------------------------------------------


async def get_hot_hand_stats(
    client: NBAClient,
    game_id: str,
    *,
    k: int = _DEFAULT_K,
    min_opportunities: int = _MIN_STREAK_OPPORTUNITIES,
) -> HotHandAnalysis:
    """Fetch play-by-play and return hot hand analysis for one game."""
    from fastbreak.games import get_play_by_play  # noqa: PLC0415

    actions = await get_play_by_play(client, game_id)
    sequences = extract_shot_sequences(actions)
    results = [
        hot_hand_result(
            seq.player_id,
            seq.player_name,
            seq.shots,
            k=k,
            min_opportunities=min_opportunities,
        )
        for seq in sequences
    ]
    return HotHandAnalysis(
        game_id=game_id,
        sequences=tuple(sequences),
        results=tuple(results),
    )
