# fastbreak.transition

High-level helpers for transition analysis — classifying NBA possessions as **transition** (fast break) or **half-court** based on play-by-play timing.

A possession is classified as "transition" when the first field goal attempt occurs within a configurable time window (default **8 seconds**) of the possession change. All functions follow the established pattern: frozen dataclasses for results, pure functions for computation, and an async wrapper for the full pipeline.

```python
from fastbreak.transition import (
    classify_possessions,
    transition_frequency,
    transition_efficiency,
    get_transition_stats,
    TransitionPossession,
    TransitionSummary,
    TransitionEfficiency,
    TransitionAnalysis,
)
```

---

## Data Classes

### `TransitionPossession`

```python
@dataclass(frozen=True, slots=True)
class TransitionPossession:
    team_id: int
    period: int
    game_clock: float
    elapsed: float
    classification: Classification
    trigger: Trigger
    actions: tuple[PlayByPlayAction, ...]
    points_scored: int
```

A single classified possession from a game's play-by-play data.

| Field | Type | Description |
|-------|------|-------------|
| `team_id` | `int` | Team with the ball during this possession |
| `period` | `int` | Period number (1-4 regulation, 5+ overtime) |
| `game_clock` | `float` | Seconds remaining in the period when the possession started |
| `elapsed` | `float` | Seconds from possession start to the first field goal attempt (0.0 if no FGA) |
| `classification` | `str` | `"transition"` or `"halfcourt"` |
| `trigger` | `str` | How the possession started — see table below |
| `actions` | `tuple[PlayByPlayAction, ...]` | All play-by-play actions in this possession |
| `points_scored` | `int` | Points scored by the offensive team (sum of `shotValue` on made FGs) |

**Trigger values**

| Trigger | Meaning |
|---------|---------|
| `"start_of_period"` | First possession of a period (Q1, Q2, OT, etc.) |
| `"made_fg"` | Previous team scored — new team inbounds |
| `"turnover"` | Previous team turned the ball over |
| `"defensive_rebound"` | Rebounding team gained possession after a missed shot |

---

### `TransitionSummary`

```python
@dataclass(frozen=True, slots=True)
class TransitionSummary:
    total_possessions: int
    transition_possessions: int
    halfcourt_possessions: int
    transition_pct: float | None
    halfcourt_pct: float | None
```

Frequency breakdown. Percentages are `None` when `total_possessions == 0`.

---

### `TransitionEfficiency`

```python
@dataclass(frozen=True, slots=True)
class TransitionEfficiency:
    transition_ppp: float | None
    halfcourt_ppp: float | None
    transition_points: int
    halfcourt_points: int
    transition_possessions: int
    halfcourt_possessions: int
```

Points-per-possession (PPP) efficiency split by classification. PPP fields are `None` when the corresponding possession count is 0.

---

### `TransitionAnalysis`

```python
@dataclass(frozen=True, slots=True)
class TransitionAnalysis:
    game_id: str
    possessions: tuple[TransitionPossession, ...]
    summary: TransitionSummary
    efficiency: TransitionEfficiency
```

Full transition analysis for a single game, combining possessions, frequency, and efficiency. Returned by `get_transition_stats`.

---

## Function Reference

### `classify_possessions`

```python
def classify_possessions(
    actions: list[PlayByPlayAction],
    *,
    transition_window: float = 8.0,
) -> list[TransitionPossession]
```

Classify possessions from play-by-play actions. This is the core pure function.

**Possession change detection:**

| Event | Condition |
|-------|-----------|
| Made field goal | `isFieldGoal == 1` and `shotResult == "Made"` |
| Turnover | `actionType` is `"turnover"` (case-insensitive) |
| Defensive rebound | `actionType` is `"rebound"` (case-insensitive), `subType` is not `"offensive"` (case-insensitive), and team changed |
| Period boundary | New period number |

Actions with `teamId == 0` (game events like period markers, jump balls without a team) are skipped entirely.

**Classification logic:**

1. For each possession, find the first field goal attempt (`isFieldGoal == 1`).
2. Compute `elapsed` = time from possession start to the first FGA (using `elapsed_game_seconds`).
3. If `elapsed <= transition_window` → `"transition"`, otherwise `"halfcourt"`.
4. If no FGA exists in the possession → `"halfcourt"` (no fast break without a shot attempt).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `actions` | `list[PlayByPlayAction]` | required | Play-by-play actions from `get_play_by_play` |
| `transition_window` | `float` | `8.0` | Seconds threshold — possessions with FGA within this window are "transition" |

**Returns** `list[TransitionPossession]` — one per detected possession

**Example**

```python
from fastbreak.games import get_play_by_play
from fastbreak.transition import classify_possessions

async with NBAClient() as client:
    actions = await get_play_by_play(client, "0022500571")

possessions = classify_possessions(actions)
trans = [p for p in possessions if p.classification == "transition"]
print(f"{len(trans)} transition possessions out of {len(possessions)} total")

# Use a tighter window for "early transition" analysis
early = classify_possessions(actions, transition_window=4.0)
```

---

### `transition_frequency`

```python
def transition_frequency(
    possessions: list[TransitionPossession],
) -> TransitionSummary
```

Compute transition vs half-court frequency breakdown.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `possessions` | `list[TransitionPossession]` | required | Output of `classify_possessions` |

**Returns** `TransitionSummary` — counts and percentages (percentages are `None` when total is 0)

---

### `transition_efficiency`

```python
def transition_efficiency(
    possessions: list[TransitionPossession],
) -> TransitionEfficiency
```

Compute points-per-possession split by possession type.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `possessions` | `list[TransitionPossession]` | required | Output of `classify_possessions` |

**Returns** `TransitionEfficiency` — PPP and point totals (PPP is `None` when count is 0)

---

### `get_transition_stats`

```python
async def get_transition_stats(
    client: NBAClient,
    game_id: str,
    *,
    transition_window: float = 8.0,
) -> TransitionAnalysis
```

Fetch play-by-play and return a full transition analysis for one game. This is the async convenience wrapper that calls `get_play_by_play`, `classify_possessions`, `transition_frequency`, and `transition_efficiency` in sequence.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `game_id` | `str` | required | NBA game ID string |
| `transition_window` | `float` | `8.0` | Seconds threshold for transition classification |

**Returns** `TransitionAnalysis` — possessions, summary, and efficiency data

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.transition import get_transition_stats

async def main():
    async with NBAClient() as client:
        analysis = await get_transition_stats(client, "0022500571")

    s = analysis.summary
    e = analysis.efficiency

    print(f"Total possessions:  {s.total_possessions}")
    print(f"Transition rate:    {s.transition_pct:.1%}")
    print(f"Transition PPP:     {e.transition_ppp:.2f}")
    print(f"Half-court PPP:     {e.halfcourt_ppp:.2f}")

asyncio.run(main())
```

---

## Related: `elapsed_game_seconds`

The transition module uses `elapsed_game_seconds` from `fastbreak.games` to convert game clocks to a linear time axis. This function is also available for direct use:

```python
from fastbreak.games import elapsed_game_seconds

# Q1 with 10:00 remaining → 120 seconds elapsed since tip-off
elapsed_game_seconds("PT10M00.00S", period=1)  # → 120.0

# Q4 buzzer → full regulation
elapsed_game_seconds("PT00M00.00S", period=4)  # → 2880.0

# OT1 with 2:30 remaining
elapsed_game_seconds("PT02M30.00S", period=5)  # → 3030.0
```

Regulation periods (1-4) are 720 seconds (12 minutes) each. Overtime periods (5+) are 300 seconds (5 minutes) each.

---

## Complete Examples

### Basic game-level transition analysis

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.transition import get_transition_stats

async def main():
    async with NBAClient() as client:
        analysis = await get_transition_stats(client, "0022500571")

    s = analysis.summary
    e = analysis.efficiency

    print(f"Possessions: {s.total_possessions}")
    print(f"Transition:  {s.transition_possessions} ({s.transition_pct:.1%})")
    print(f"Half-court:  {s.halfcourt_possessions} ({s.halfcourt_pct:.1%})")
    print()

    if e.transition_ppp is not None and e.halfcourt_ppp is not None:
        diff = e.transition_ppp - e.halfcourt_ppp
        label = "more" if diff > 0 else "less"
        print(f"Transition PPP:  {e.transition_ppp:.2f}")
        print(f"Half-court PPP:  {e.halfcourt_ppp:.2f}")
        print(f"Transition is {abs(diff):.2f} PPP {label} efficient")

asyncio.run(main())
```

### Comparing transition windows

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.games import get_play_by_play
from fastbreak.transition import classify_possessions, transition_frequency

async def main():
    async with NBAClient() as client:
        actions = await get_play_by_play(client, "0022500571")

    for window in [4.0, 6.0, 8.0, 10.0]:
        poss = classify_possessions(actions, transition_window=window)
        s = transition_frequency(poss)
        pct = f"{s.transition_pct:.1%}" if s.transition_pct is not None else "N/A"
        print(f"Window {window:.0f}s: {s.transition_possessions} transition ({pct})")

asyncio.run(main())
```

### Identifying fast-break scoring plays

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.games import get_play_by_play
from fastbreak.transition import classify_possessions

async def main():
    async with NBAClient() as client:
        actions = await get_play_by_play(client, "0022500571")

    possessions = classify_possessions(actions)

    # Find transition possessions that scored
    fast_break_scores = [
        p for p in possessions
        if p.classification == "transition" and p.points_scored > 0
    ]

    print(f"Fast-break scoring plays: {len(fast_break_scores)}")
    for p in fast_break_scores[:10]:
        print(
            f"  Q{p.period} {p.game_clock:5.1f}s  "
            f"elapsed={p.elapsed:.1f}s  "
            f"pts={p.points_scored}  "
            f"trigger={p.trigger}"
        )

asyncio.run(main())
```

---

## Helpers vs. Raw Endpoints

| Need | Use helper | Use raw data |
|------|-----------|--------------|
| Full game transition analysis | `get_transition_stats` | `get_play_by_play` + `classify_possessions` |
| Custom transition window | `classify_possessions(actions, transition_window=N)` | Same — just change the kwarg |
| Frequency breakdown only | `transition_frequency(possessions)` | Count manually from `possessions` list |
| Per-team transition rate | Filter `possessions` by `team_id` before calling helpers | Same |
| Multi-game aggregation | Call `get_transition_stats` per game, combine results | Batch with `get_many` + manual processing |

---

## Notes

- The 8-second default window is a common analytical convention for NBA transition analysis. Adjust with `transition_window` for different definitions (e.g., 6s for "early transition", 10s for "extended transition").
- Points are counted from `shotValue` on made field goals only. Free throws are not currently included in `points_scored`.
- Offensive rebounds do not reset the possession — the team retains possession and the clock continues from the original possession start.
- Actions with `teamId == 0` (game events like period markers) are completely excluded from possession grouping.
