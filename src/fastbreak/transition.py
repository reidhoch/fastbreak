"""Transition analysis -- classify possessions as transition or half-court."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from fastbreak.games import elapsed_game_seconds

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.play_by_play import PlayByPlayAction

_TRANSITION_WINDOW = 8.0
_PERIOD_END_CLOCK = "PT00M00.00S"

type Classification = Literal["transition", "halfcourt"]
"""Possession classification: transition (fast break) or half-court."""

type Trigger = Literal["made_fg", "turnover", "defensive_rebound", "start_of_period"]
"""How a possession started."""


@dataclass(frozen=True, slots=True)
class TransitionPossession:
    """A single classified possession.

    Attributes:
        team_id: Team with the ball during this possession.
        period: Period number (1-4 regulation, 5+ overtime).
        game_clock: Seconds remaining in the period at possession start.
        elapsed: Seconds from possession start to first field goal attempt
            (``0.0`` if no FGA in the possession).
        classification: ``"transition"`` or ``"halfcourt"``.
        trigger: How this possession started: ``"made_fg"``,
            ``"turnover"``, ``"defensive_rebound"``, or
            ``"start_of_period"``.
        actions: All play-by-play actions in this possession.
        points_scored: Points scored by the offensive team.
    """

    team_id: int
    period: int
    game_clock: float
    elapsed: float
    classification: Classification
    trigger: Trigger
    actions: tuple[PlayByPlayAction, ...]
    points_scored: int


@dataclass(frozen=True, slots=True)
class TransitionSummary:
    """Frequency breakdown of transition vs half-court possessions."""

    total_possessions: int
    transition_possessions: int
    halfcourt_possessions: int
    transition_pct: float | None
    halfcourt_pct: float | None


@dataclass(frozen=True, slots=True)
class TransitionEfficiency:
    """Points-per-possession efficiency split by possession type."""

    transition_ppp: float | None
    halfcourt_ppp: float | None
    transition_points: int
    halfcourt_points: int
    transition_possessions: int
    halfcourt_possessions: int


@dataclass(frozen=True, slots=True)
class TransitionAnalysis:
    """Full transition analysis for a single game."""

    game_id: str
    possessions: tuple[TransitionPossession, ...]
    summary: TransitionSummary
    efficiency: TransitionEfficiency


@dataclass(slots=True)
class _PossessionState:
    """Mutable accumulator for the current in-progress possession."""

    period: int = 0
    team_id: int = 0
    start_elapsed: float = 0.0
    trigger: Trigger = "start_of_period"
    actions: list[PlayByPlayAction] = field(default_factory=list)


def _finalize_possession(
    state: _PossessionState,
    transition_window: float,
) -> TransitionPossession | None:
    """Build a TransitionPossession from accumulated state, or None if empty."""
    if not state.actions:
        return None

    first_fga_elapsed: float | None = None
    for a in state.actions:
        if a.isFieldGoal == 1:
            first_fga_elapsed = elapsed_game_seconds(a.clock, a.period)
            break

    classification: Classification
    if first_fga_elapsed is not None:
        elapsed = first_fga_elapsed - state.start_elapsed
        classification = "transition" if elapsed <= transition_window else "halfcourt"
    else:
        elapsed = 0.0
        classification = "halfcourt"

    points = sum(a.shotValue for a in state.actions if _is_made_fg(a))

    return TransitionPossession(
        team_id=state.team_id,
        period=state.period,
        game_clock=elapsed_game_seconds(_PERIOD_END_CLOCK, state.period)
        - state.start_elapsed,
        elapsed=elapsed,
        classification=classification,
        trigger=state.trigger,
        actions=tuple(state.actions),
        points_scored=points,
    )


def _is_made_fg(action: PlayByPlayAction) -> bool:
    return action.isFieldGoal == 1 and action.shotResult == "Made"


def _is_turnover(action: PlayByPlayAction) -> bool:
    return action.actionType.lower() == "turnover"


def _is_defensive_rebound(action: PlayByPlayAction, current_team_id: int) -> bool:
    return (
        action.actionType.lower() == "rebound"
        and action.subType.lower() != "offensive"
        and current_team_id not in (0, action.teamId)
    )


def _flush(
    state: _PossessionState,
    possessions: list[TransitionPossession],
    transition_window: float,
) -> None:
    """Finalize the current possession if non-empty and append to the list."""
    if poss := _finalize_possession(state, transition_window):
        possessions.append(poss)


def _end_possession(
    action: PlayByPlayAction,
    state: _PossessionState,
    trigger: Trigger,
    possessions: list[TransitionPossession],
    transition_window: float,
) -> _PossessionState:
    """Finalize the current possession and return a fresh state for the next."""
    if state.team_id == 0:
        state.team_id = action.teamId
    state.actions.append(action)
    _flush(state, possessions, transition_window)
    return _PossessionState(
        period=state.period,
        start_elapsed=elapsed_game_seconds(action.clock, action.period),
        trigger=trigger,
    )


def classify_possessions(
    actions: list[PlayByPlayAction],
    *,
    transition_window: float = _TRANSITION_WINDOW,
) -> list[TransitionPossession]:
    """Classify possessions as transition or halfcourt based on play-by-play timing.

    Walks the action list, detects possession changes, and classifies each
    possession by the time between the possession start and the first field
    goal attempt.  If the elapsed time is ``<= transition_window`` seconds,
    the possession is ``"transition"``; otherwise ``"halfcourt"``.

    Possession changes are triggered by:

    - **Made field goal** (``isFieldGoal == 1`` and
      ``shotResult == "Made"``).
    - **Turnover** (``actionType`` is ``"turnover"``, case-insensitive).
    - **Defensive rebound** (``actionType`` is ``"rebound"``,
      case-insensitive, ``subType`` is not ``"offensive"`` (case-insensitive),
      and team changed).
    - **Period boundary** (new period number).

    Actions with ``teamId == 0`` (game events like period markers) are
    skipped entirely.

    Args:
        actions: Play-by-play actions, typically from
            :func:`~fastbreak.games.get_play_by_play`.
        transition_window: Seconds threshold for transition classification
            (default ``8.0``).

    Returns:
        List of :class:`TransitionPossession` objects, one per detected
        possession.

    """
    if not actions:
        return []

    possessions: list[TransitionPossession] = []
    state = _PossessionState()

    for action in actions:
        if action.teamId == 0:
            continue

        # Period change starts a new possession.  Do NOT continue — the
        # action itself might also end the possession (e.g. a made FG on
        # the very first play of the period).
        if action.period != state.period:
            _flush(state, possessions, transition_window)
            state = _PossessionState(
                period=action.period,
                team_id=action.teamId,
                start_elapsed=elapsed_game_seconds(action.clock, action.period),
                trigger="start_of_period",
            )

        # Made field goal ends the current possession.
        if _is_made_fg(action):
            state = _end_possession(
                action,
                state,
                "made_fg",
                possessions,
                transition_window,
            )
            continue

        # Turnover ends the current possession.
        if _is_turnover(action):
            state = _end_possession(
                action,
                state,
                "turnover",
                possessions,
                transition_window,
            )
            continue

        # Defensive rebound (team change) starts a new possession.
        if _is_defensive_rebound(action, state.team_id):
            _flush(state, possessions, transition_window)
            state = _PossessionState(
                period=state.period,
                team_id=action.teamId,
                start_elapsed=elapsed_game_seconds(action.clock, action.period),
                trigger="defensive_rebound",
                actions=[action],
            )
            continue

        # Regular action — accumulate into the current possession.
        if state.team_id == 0:
            state.team_id = action.teamId
        state.actions.append(action)

    _flush(state, possessions, transition_window)
    return possessions


def transition_frequency(
    possessions: list[TransitionPossession],
) -> TransitionSummary:
    """Compute transition vs half-court frequency breakdown.

    Args:
        possessions: Output of :func:`classify_possessions`.

    Returns:
        :class:`TransitionSummary` with counts and percentages.
        Percentages are ``None`` when *total_possessions* is 0.

    """
    total = len(possessions)
    trans = sum(1 for p in possessions if p.classification == "transition")
    half = total - trans
    return TransitionSummary(
        total_possessions=total,
        transition_possessions=trans,
        halfcourt_possessions=half,
        transition_pct=trans / total if total > 0 else None,
        halfcourt_pct=half / total if total > 0 else None,
    )


def transition_efficiency(
    possessions: list[TransitionPossession],
) -> TransitionEfficiency:
    """Compute points-per-possession split by possession type.

    Args:
        possessions: Output of :func:`classify_possessions`.

    Returns:
        :class:`TransitionEfficiency` with PPP and point totals.
        PPP fields are ``None`` when the corresponding count is 0.

    """
    trans_pts = 0
    half_pts = 0
    trans_count = 0
    half_count = 0
    for p in possessions:
        if p.classification == "transition":
            trans_pts += p.points_scored
            trans_count += 1
        else:
            half_pts += p.points_scored
            half_count += 1

    return TransitionEfficiency(
        transition_ppp=trans_pts / trans_count if trans_count > 0 else None,
        halfcourt_ppp=half_pts / half_count if half_count > 0 else None,
        transition_points=trans_pts,
        halfcourt_points=half_pts,
        transition_possessions=trans_count,
        halfcourt_possessions=half_count,
    )


async def get_transition_stats(
    client: BaseClient,
    game_id: str,
    *,
    transition_window: float = _TRANSITION_WINDOW,
) -> TransitionAnalysis:
    """Fetch play-by-play and return a full transition analysis for one game.

    Args:
        client: NBA API client.
        game_id: NBA game ID string.
        transition_window: Seconds threshold for transition classification
            (default ``8.0``).

    Returns:
        :class:`TransitionAnalysis` containing possessions, summary, and
        efficiency data.

    Examples:
        analysis = await get_transition_stats(client, "0022500571")
        print(f"Transition %: {analysis.summary.transition_pct:.1%}")

    """
    from fastbreak.games import get_play_by_play  # noqa: PLC0415

    actions = await get_play_by_play(client, game_id)
    poss = classify_possessions(actions, transition_window=transition_window)
    summary = transition_frequency(poss)
    eff = transition_efficiency(poss)

    return TransitionAnalysis(
        game_id=game_id,
        possessions=tuple(poss),
        summary=summary,
        efficiency=eff,
    )
