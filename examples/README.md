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

### [game_ids.py](game_ids.py)

Fetch game IDs with various filters: by season, by team, by season type (regular/playoffs), and by date range.

```bash
uv run python examples/game_ids.py
```

### [player_lookup.py](player_lookup.py)

Search and look up players using `fastbreak.players`: search by partial name, look up by numeric ID or full name, get a player's game log for the current season.

```bash
uv run python examples/player_lookup.py
```

### [team_lookup.py](team_lookup.py)

Search for teams and fetch game logs using `fastbreak.teams`. Team search is synchronous (no API call needed); game log fetching is async.

```bash
uv run python examples/team_lookup.py
```

## Advanced Examples

### [player_trends.py](player_trends.py)

Analyze player scoring trends over the last 2 weeks. Shows which players are heating up or cooling down by comparing their early vs recent scoring averages. Demonstrates the `get_many()` pattern with `request_delay` for rate-limit-friendly batch requests.

```bash
uv run python examples/player_trends.py
```

### [player_stats.py](player_stats.py)

Fetch career stats (season-by-season), hustle stats, and league leaders using `fastbreak.players`. Shows how to pull scoring and assist leaders for the current season.

```bash
uv run python examples/player_stats.py
```

### [team_stats.py](team_stats.py)

Fetch team season stats and lineup analysis using `fastbreak.teams`. Covers 5-man lineup plus/minus and two-man combination minutes.

```bash
uv run python examples/team_stats.py
```

### [play_by_play.py](play_by_play.py)

Fetch and analyze play-by-play data using `fastbreak.games`. Breaks down action types, isolates 4th-quarter plays, and lists the last five made shots of the game.

```bash
uv run python examples/play_by_play.py
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
