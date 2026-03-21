# fastbreak.rotations

## Overview

`fastbreak.rotations` provides async fetchers and pure computation functions for analyzing NBA game rotation data — player stints, lineup reconstruction, substitution timelines, and minutes aggregation.

- `get_game_rotations` and `get_rotation_summary` are **async** — they call the NBA Stats API via the `GameRotation` endpoint and require an `NBAClient` instance.
- `player_stints`, `player_total_minutes`, `stint_plus_minus`, `lineup_stints`, and `rotation_timeline` are **sync** — they operate on `RotationEntry` lists and require no additional API calls.
- `minutes_distribution` is an alias for `player_total_minutes`.

Timing uses **seconds from tip-off** for in/out times and **minutes** for durations. The NBA API returns times in tenths of seconds; all conversion is handled internally. Periods follow NBA conventions: Q1–Q4 are 720 seconds each, overtime periods are 300 seconds each.

```python
from fastbreak.rotations import (
    get_game_rotations,
    get_rotation_summary,
    player_stints,
    player_total_minutes,
    stint_plus_minus,
    lineup_stints,
    minutes_distribution,
    rotation_timeline,
    PlayerStint,
    PlayerMinutes,
    LineupStint,
    SubstitutionEvent,
    RotationSummary,
)
```

---

## Function Reference

### `get_game_rotations(client, game_id) -> GameRotationResponse`

Fetch rotation data for a game.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `NBAClient` | NBA API client instance |
| `game_id` | `str` | NBA game ID (e.g., `"0022500571"`) |

**Returns**: `GameRotationResponse` with `home_team` and `away_team` lists of `RotationEntry`.

---

### `get_rotation_summary(client, game_id, *, team_id) -> RotationSummary`

Fetch rotations and build a full summary for one team.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `NBAClient` | NBA API client instance |
| `game_id` | `str` | NBA game ID |
| `team_id` | `int` | Team ID to select (home or away) |

**Returns**: `RotationSummary` containing stints, minutes, lineups, substitutions, and total game minutes.

**Raises**: `ValueError` if `team_id` is not found in either the home or away rotation entries.

---

### `player_stints(entries) -> list[PlayerStint]`

Map rotation entries to player stints, preserving input order.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `Sequence[RotationEntry]` | Rotation entries (home or away) |

**Returns**: List of `PlayerStint` with `player_id`, `player_name`, `in_time`, `out_time`, `duration_minutes`, `points`, `pt_diff`, `usg_pct`.

---

### `player_total_minutes(entries) -> list[PlayerMinutes]`

Aggregate per-player minutes, sorted by `total_minutes` descending. `None` values for `player_pts` and `pt_diff` are coalesced to 0.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `Sequence[RotationEntry]` | Rotation entries |

**Returns**: List of `PlayerMinutes` sorted by total minutes descending.

---

### `stint_plus_minus(entries) -> dict[int, float]`

Return `{person_id: total_pt_diff}`. `None` values are treated as 0.0.

---

### `lineup_stints(entries) -> list[LineupStint]`

Reconstruct lineup stints using a sweep-line algorithm. Merges consecutive segments with identical player sets.

**Returns**: Chronologically sorted list of `LineupStint` with `player_ids` (frozenset), `player_names` (sorted tuple), `in_time`, `out_time`, `duration_minutes`.

---

### `rotation_timeline(entries) -> list[SubstitutionEvent]`

Build a chronological substitution timeline. Pairs "enter" events with "exit" events at each time point. Unpaired events use `None` for the missing side (e.g., game start/end).

**Returns**: Chronologically sorted list of `SubstitutionEvent`.

---

## Dataclasses

All dataclasses use `frozen=True, slots=True`.

### `PlayerStint`
| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | Player ID |
| `player_name` | `str` | Full name |
| `in_time` | `float` | Seconds from tip-off |
| `out_time` | `float` | Seconds from tip-off |
| `duration_minutes` | `float` | Stint length in minutes |
| `points` | `int \| None` | Points scored during stint |
| `pt_diff` | `float \| None` | Point differential |
| `usg_pct` | `float \| None` | Usage percentage |

### `PlayerMinutes`
| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | Player ID |
| `player_name` | `str` | Full name |
| `total_minutes` | `float` | Sum of all stint durations |
| `stint_count` | `int` | Number of stints |
| `avg_stint_minutes` | `float` | Average stint length |
| `total_points` | `int` | Sum of points (None → 0) |
| `total_pt_diff` | `float` | Sum of pt_diff (None → 0) |

### `LineupStint`
| Field | Type | Description |
|-------|------|-------------|
| `player_ids` | `frozenset[int]` | Set of player IDs on court |
| `player_names` | `tuple[str, ...]` | Alphabetically sorted names |
| `in_time` | `float` | Seconds from tip-off |
| `out_time` | `float` | Seconds from tip-off |
| `duration_minutes` | `float` | Lineup duration in minutes |

### `SubstitutionEvent`
| Field | Type | Description |
|-------|------|-------------|
| `time` | `float` | Seconds from tip-off |
| `period` | `int` | Game period (1–4, 5+ for OT) |
| `player_in_id` | `int \| None` | Player entering (None at game end) |
| `player_in_name` | `str` | Name or empty string |
| `player_out_id` | `int \| None` | Player exiting (None at game start) |
| `player_out_name` | `str` | Name or empty string |

### `RotationSummary`
| Field | Type | Description |
|-------|------|-------------|
| `game_id` | `str` | NBA game ID |
| `team_id` | `int` | Team ID |
| `player_stints` | `tuple[PlayerStint, ...]` | All stints |
| `player_minutes` | `tuple[PlayerMinutes, ...]` | Aggregated by player |
| `lineup_stints` | `tuple[LineupStint, ...]` | Reconstructed lineups |
| `substitution_events` | `tuple[SubstitutionEvent, ...]` | Timeline |
| `total_game_minutes` | `float` | Max out_time / 60 |
