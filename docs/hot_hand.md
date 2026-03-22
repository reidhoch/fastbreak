# fastbreak.hot_hand

Hot hand analysis with **Miller-Sanjurjo bias correction** — streak detection on sequential shot outcomes from play-by-play data.

The "hot hand" question asks whether a player who has made several shots in a row is more likely to make the next one. The naive estimator of P(make | k consecutive makes) is **biased downward** for finite sequences — Miller & Sanjurjo (2018, Econometrica) showed this is a selection effect analogous to the Monty Hall problem. This module applies their first-order correction: `p * (1 - p) / (n - k)`.

All functions follow the established pattern: frozen dataclasses for results, pure functions for computation, and an async wrapper for the full pipeline.

```python
from fastbreak.hot_hand import (
    get_hot_hand_stats,
    hot_hand_result,
    hot_hand_score,
    miller_sanjurjo_bias,
    count_streaks,
    extract_shot_sequences,
    merge_sequences,
    HotHandAnalysis,
    HotHandResult,
    ShotSequence,
    StreakCounts,
)
```

---

## Data Classes

### `ShotSequence`

```python
@dataclass(frozen=True, slots=True)
class ShotSequence:
    player_id: int
    player_name: str
    team_id: int
    shots: tuple[bool, ...]
```

A player's sequential field goal outcomes from a single game. `True` = made, `False` = missed, in chronological order.

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Player's full name |
| `team_id` | `int` | Team ID |
| `shots` | `tuple[bool, ...]` | Chronological shot outcomes (True = made) |

---

### `StreakCounts`

```python
@dataclass(frozen=True, slots=True)
class StreakCounts:
    k: int
    n: int
    streak_opportunities: int
    makes_after_streak: int
    misses_after_streak: int
    naive_p: float | None
```

Raw streak counting results before bias correction.

| Field | Type | Description |
|-------|------|-------------|
| `k` | `int` | Streak length used for conditioning |
| `n` | `int` | Total number of shots in the sequence |
| `streak_opportunities` | `int` | Positions where the previous k shots were all makes |
| `makes_after_streak` | `int` | Makes at streak opportunity positions |
| `misses_after_streak` | `int` | Misses at streak opportunity positions |
| `naive_p` | `float \| None` | `makes / opportunities`, or `None` if no opportunities |

---

### `HotHandResult`

```python
@dataclass(frozen=True, slots=True)
class HotHandResult:
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
```

Bias-corrected hot hand analysis for a single player.

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Player's full name |
| `k` | `int` | Streak length (default 3) |
| `n` | `int` | Total shots in the sequence |
| `baseline_p` | `float \| None` | Overall make rate (sum of makes / n) |
| `naive_p` | `float \| None` | P(make \| k makes) before correction |
| `bias_correction` | `float \| None` | Miller-Sanjurjo term: `p * (1 - p) / (n - k)` |
| `corrected_p` | `float \| None` | `naive_p + bias_correction` |
| `delta` | `float \| None` | `corrected_p - baseline_p` — the hot hand effect |
| `streak_opportunities` | `int` | Number of positions following a k-make streak |
| `score` | `float \| None` | Composite score; `None` if < min_opportunities (default 3) |

A positive `delta` means the player shoots better after a streak of makes (evidence of a hot hand). A negative `delta` means they shoot worse (regression or tighter defense after makes).

---

### `HotHandAnalysis`

```python
@dataclass(frozen=True, slots=True)
class HotHandAnalysis:
    game_id: str
    sequences: tuple[ShotSequence, ...]
    results: tuple[HotHandResult, ...]
```

Full hot hand analysis for a single game. Returned by `get_hot_hand_stats`.

---

## Function Reference

### `miller_sanjurjo_bias`

```python
def miller_sanjurjo_bias(p: float, n: int, k: int) -> float | None
```

Compute the Miller-Sanjurjo (2018) expected bias correction term. For a Bernoulli(p) sequence of length n, the naive estimator of P(make | k consecutive makes) has an expected downward bias. This returns the correction term to **add** to the naive estimate.

Formula: `p * (1 - p) / (n - k)`

Returns `None` when `n <= k` (no post-streak position exists).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `p` | `float` | required | Baseline make probability |
| `n` | `int` | required | Sequence length |
| `k` | `int` | required | Streak length |

**Returns** `float | None` — the bias correction to add, or `None` if sequence is too short

**Example**

```python
from fastbreak.hot_hand import miller_sanjurjo_bias

# A 45% shooter with 20 shots, k=3 streak
bias = miller_sanjurjo_bias(p=0.45, n=20, k=3)
# → 0.01456 (about 1.5 percentage points of downward bias)

# Sequence too short for any post-streak position
bias = miller_sanjurjo_bias(p=0.5, n=3, k=3)
# → None
```

---

### `count_streaks`

```python
def count_streaks(
    shots: tuple[bool, ...],
    k: int = 3,
) -> StreakCounts
```

Count makes and misses after k-consecutive-make streaks. Walks through the shot sequence; at each position i >= k, checks whether the previous k shots are all makes. If so, records the shot at position i.

Overlapping streaks are counted — if shots 3, 4, 5, 6 are all makes (with k=3), both positions 6 (after 3-4-5) and potentially beyond are counted.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shots` | `tuple[bool, ...]` | required | Chronological shot outcomes |
| `k` | `int` | `3` | Number of consecutive makes defining a streak |

**Returns** `StreakCounts`

**Example**

```python
from fastbreak.hot_hand import count_streaks

# T T T F T T T T  (T=make, F=miss)
shots = (True, True, True, False, True, True, True, True)
result = count_streaks(shots, k=3)
# streak_opportunities=2 (positions 3 and 7)
# makes_after_streak=1 (position 7: True)
# misses_after_streak=1 (position 3: False)
# naive_p=0.5
```

---

### `hot_hand_score`

```python
def hot_hand_score(
    delta: float,
    streak_opportunities: int,
    min_opportunities: int = 3,
) -> float | None
```

Compute a composite hot hand score. Returns `None` when `streak_opportunities < min_opportunities`. The score scales the corrected delta by the log of opportunities:

```
score = delta * 100 * log2(1 + streak_opportunities)
```

This gives more weight to results with more evidence. A player with delta=+0.05 across 15 opportunities scores higher than one with the same delta across 3 opportunities.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `delta` | `float` | required | Corrected P(make\|streak) minus baseline P(make) |
| `streak_opportunities` | `int` | required | Number of post-streak positions |
| `min_opportunities` | `int` | `3` | Minimum opportunities to compute a score |

**Returns** `float | None` — composite score, or `None` if insufficient opportunities

---

### `hot_hand_result`

```python
def hot_hand_result(
    player_id: int,
    player_name: str,
    shots: tuple[bool, ...],
    k: int = 3,
    min_opportunities: int = 3,
) -> HotHandResult
```

Compute the bias-corrected hot hand analysis for a shot sequence. Orchestrates `count_streaks`, `miller_sanjurjo_bias`, and `hot_hand_score` into a single result.

All fields propagate `None` safely — if there are no streak opportunities, `naive_p`, `corrected_p`, `delta`, and `score` will all be `None`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player_id` | `int` | required | NBA player ID |
| `player_name` | `str` | required | Player's full name |
| `shots` | `tuple[bool, ...]` | required | Chronological shot outcomes |
| `k` | `int` | `3` | Consecutive makes defining a streak |
| `min_opportunities` | `int` | `3` | Minimum post-streak positions for a score |

**Returns** `HotHandResult`

**Example**

```python
from fastbreak.hot_hand import hot_hand_result

shots = (True, False, True, True, True, True, False, True, True, True, False)
result = hot_hand_result(player_id=201939, player_name="Stephen Curry", shots=shots)

print(f"Baseline: {result.baseline_p:.3f}")
print(f"Naive P(make|streak): {result.naive_p:.3f}")
print(f"Bias correction: {result.bias_correction:.4f}")
print(f"Corrected P(make|streak): {result.corrected_p:.3f}")
print(f"Delta: {result.delta:+.3f}")
if result.score is not None:
    print(f"Score: {result.score:.1f}")
```

---

### `extract_shot_sequences`

```python
def extract_shot_sequences(
    actions: list[PlayByPlayAction],
) -> list[ShotSequence]
```

Extract per-player sequential shot outcomes from play-by-play data. Walks the action list in order and records each field goal attempt (`isFieldGoal == 1`) as a make or miss for the shooting player. Actions with `teamId == 0` (game events) are skipped.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `actions` | `list[PlayByPlayAction]` | required | Play-by-play actions from `get_play_by_play` |

**Returns** `list[ShotSequence]` — one per player who attempted a field goal, sorted by `player_id`

---

### `merge_sequences`

```python
def merge_sequences(
    game_sequences: list[list[ShotSequence]],
) -> list[ShotSequence]
```

Merge per-player shot sequences from multiple games. Groups by `player_id` and concatenates shots tuples in the order the games are provided. Useful for season-level hot hand analysis.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `game_sequences` | `list[list[ShotSequence]]` | required | Sequences from multiple games (output of `extract_shot_sequences` per game) |

**Returns** `list[ShotSequence]` — merged sequences, sorted by `player_id`

---

### `get_hot_hand_stats`

```python
async def get_hot_hand_stats(
    client: NBAClient,
    game_id: str,
    *,
    k: int = 3,
    min_opportunities: int = 3,
) -> HotHandAnalysis
```

Fetch play-by-play and return hot hand analysis for one game. This is the async convenience wrapper that calls `get_play_by_play`, `extract_shot_sequences`, and `hot_hand_result` per player.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `game_id` | `str` | required | NBA game ID string |
| `k` | `int` | `3` | Consecutive makes defining a streak |
| `min_opportunities` | `int` | `3` | Minimum post-streak positions for a score |

**Returns** `HotHandAnalysis` — sequences and results for all players in the game

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.hot_hand import get_hot_hand_stats

async def main():
    async with NBAClient() as client:
        analysis = await get_hot_hand_stats(client, "0022500571")

    print(f"Game {analysis.game_id}: {len(analysis.results)} players analyzed")
    for r in analysis.results:
        if r.score is not None:
            print(f"  {r.player_name:<22} delta={r.delta:+.3f}  score={r.score:+.1f}")

asyncio.run(main())
```

---

## Complete Examples

### Single game hot hand analysis

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.hot_hand import get_hot_hand_stats

async def main():
    async with NBAClient() as client:
        analysis = await get_hot_hand_stats(client, "0022500571")

    # Players with enough streak opportunities to compute a score
    scorable = [r for r in analysis.results if r.score is not None]
    scorable.sort(key=lambda r: (r.score or 0.0), reverse=True)

    print(f"Hot Hand Analysis — Game {analysis.game_id}")
    print(f"{'Player':<22} {'FGA':>4} {'Base%':>6} {'Naive':>6} {'Corr':>6} {'Delta':>7} {'Score':>7}")
    print("-" * 65)
    for r in scorable:
        assert r.baseline_p is not None and r.naive_p is not None
        assert r.corrected_p is not None and r.delta is not None and r.score is not None
        print(
            f"{r.player_name:<22} {r.n:>4} {r.baseline_p:>6.1%} "
            f"{r.naive_p:>6.1%} {r.corrected_p:>6.1%} "
            f"{r.delta:>+7.3f} {r.score:>+7.1f}"
        )

asyncio.run(main())
```

### Season-level analysis across multiple games

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.games import get_game_ids, get_play_by_play
from fastbreak.hot_hand import extract_shot_sequences, merge_sequences, hot_hand_result

async def main():
    async with NBAClient() as client:
        game_ids = await get_game_ids(client, "2025-26", team_id=1610612744)
        # Take first 10 regular-season games
        game_ids = [g for g in game_ids if g[:3] == "002"][:10]

        game_seqs = []
        for gid in game_ids:
            actions = await get_play_by_play(client, gid)
            game_seqs.append(extract_shot_sequences(actions))

    merged = merge_sequences(game_seqs)

    print(f"Season Hot Hand ({len(game_ids)} games)")
    print(f"{'Player':<22} {'FGA':>5} {'Opps':>5} {'Delta':>7} {'Score':>7}")
    print("-" * 52)

    for seq in merged:
        result = hot_hand_result(seq.player_id, seq.player_name, seq.shots)
        if result.score is not None:
            print(
                f"{result.player_name:<22} {result.n:>5} "
                f"{result.streak_opportunities:>5} "
                f"{result.delta:>+7.3f} {result.score:>+7.1f}"
            )

asyncio.run(main())
```

### Step-by-step pure functions (no API)

```python
from fastbreak.hot_hand import miller_sanjurjo_bias, count_streaks, hot_hand_result

# Simulate a shot sequence
shots = (True, True, True, False, True, True, True, True, False, True)

# Step 1: Count streaks
counts = count_streaks(shots, k=3)
print(f"Sequence length: {counts.n}")
print(f"Streak opportunities: {counts.streak_opportunities}")
print(f"Makes after streak: {counts.makes_after_streak}")
if counts.naive_p is not None:
    print(f"Naive P(make|streak): {counts.naive_p:.3f}")

# Step 2: Bias correction
baseline = sum(shots) / len(shots)
bias = miller_sanjurjo_bias(baseline, len(shots), k=3)
print(f"\nBaseline: {baseline:.3f}")
if bias is not None:
    print(f"Bias correction: {bias:.4f}")
if counts.naive_p is not None and bias is not None:
    print(f"Corrected P(make|streak): {counts.naive_p + bias:.3f}")

# Step 3: All-in-one
result = hot_hand_result(0, "Test Player", shots)
if result.delta is not None:
    print(f"\nDelta (corrected - baseline): {result.delta:+.3f}")
print(f"Score: {result.score}")
```

---

## Helpers vs. Raw Data

| Need | Use helper | Use raw data |
|------|-----------|--------------|
| Full game hot hand analysis | `get_hot_hand_stats` | `get_play_by_play` + `extract_shot_sequences` + `hot_hand_result` |
| Season-level analysis | `merge_sequences` over multiple games | Concatenate manually |
| Custom streak length | Pass `k=N` to any function | Same |
| Bias correction only | `miller_sanjurjo_bias(p, n, k)` | n/a — pure Python |
| Simulated/external data | `hot_hand_result(id, name, shots)` | `count_streaks` + manual assembly |

---

## Notes

- The default streak length `k=3` (three consecutive makes) is the standard in the hot hand literature. Lower values (k=1, k=2) produce more streak opportunities but weaker evidence; higher values require longer sequences.
- The bias correction `p * (1 - p) / (n - k)` is the first-order approximation from Miller & Sanjurjo (2018). It is sufficient for NBA game-length sequences (typically 10-30 FGA per player per game).
- The correction is always non-negative — the naive estimator is biased **downward**, so the correction adds to it. After correction, the true hot hand effect may still be positive, zero, or negative.
- `score` is `None` when `streak_opportunities < min_opportunities` (default 3). This prevents noisy results from players with very few streak opportunities.
- The composite score formula `delta * 100 * log2(1 + opportunities)` weights the delta by evidence quantity. Two players with the same delta but different opportunity counts will have different scores — more opportunities means more confidence.
- Offensive rebounds, free throws, and non-field-goal actions are excluded from shot sequences. Only `isFieldGoal == 1` actions count.
