# Examples

This directory contains example scripts demonstrating how to use the fastbreak library.

## Running Examples

```bash
# From the repository root
uv run python examples/<example_name>.py
```

## Simple Examples

### [todays_games.py](todays_games.py)

Fetch and display today's NBA games with tip-off times in your local timezone.

```bash
uv run python examples/todays_games.py
```

### [gravity.py](gravity.py)

Fetch the top 10 gravity leaders for a season. Gravity measures how much defensive attention a player draws based on defender proximity.

```bash
uv run python examples/gravity.py
```

### [boxscores.py](boxscores.py)

Fetch box scores for all of yesterday's games using `get_many()` for concurrent requests. Demonstrates the scoreboard → game IDs → box scores pattern.

```bash
uv run python examples/boxscores.py
```

## Advanced Examples

### [player_trends.py](player_trends.py)

Analyze player scoring trends over the last 2 weeks. Shows which players are heating up or cooling down by comparing their early vs recent scoring averages. Demonstrates the `get_many()` pattern with `request_delay` for rate-limit-friendly batch requests.

```bash
uv run python examples/player_trends.py
```

### [three_two_one.py](three_two_one.py)

Apply an NHL-style 3-2-1 point system to NBA standings using Polars DataFrames:
- 3 points for a regulation win
- 2 points for an overtime win
- 1 point for an overtime loss

Demonstrates the `to_polars()` mixin for DataFrame conversion and complex data transformations.

```bash
uv run python examples/three_two_one.py
```
