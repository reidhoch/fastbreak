# Examples

This directory contains example scripts demonstrating how to use the fastbreak library.

## Running Examples

```bash
# From the repository root
uv run python examples/<example_name>.py
```

## Simple Examples

### [todays_games.py](todays_games.py)

Fetch today's games with tip-off times, yesterday's results, and a full game summary
(arena, officials, attendance) for the first completed game of the previous day.

```bash
uv run python examples/todays_games.py
```

### [seasons.py](seasons.py)

Demonstrate the three sync season utilities from `fastbreak.seasons` — no API call needed:
`get_season_from_date`, `season_start_year`, and `season_to_season_id`.

```bash
uv run python examples/seasons.py
```

### [gravity.py](gravity.py)

Fetch the top 10 gravity leaders for a season. Gravity measures how much defensive attention a player draws based on defender proximity.

```bash
uv run python examples/gravity.py
```

### [standings.py](standings.py)

Display league-wide and conference-filtered standings using `fastbreak.standings`:
`get_standings` (all 30 teams with win%, streak, conference games back) and
`get_conference_standings` (East or West, sorted by playoff rank).

```bash
uv run python examples/standings.py
```

### [boxscores.py](boxscores.py)

Fetch box scores for yesterday's games using the `get_yesterdays_games` convenience helper,
then demonstrate all four box score flavors via concurrent `get_many()` requests:
standard (`get_box_scores`), advanced/pace (`get_box_scores_advanced`),
hustle/effort (`get_box_scores_hustle`), and scoring distribution (`get_box_scores_scoring`).

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

Search for teams and explore the static team registry using `fastbreak.teams`: look up by abbreviation,
name, city, or numeric ID with `get_team` (returns `TeamInfo`) and `get_team_id` (returns `TeamID`),
browse all 30 teams via `TEAMS`, filter by conference/division with `teams_by_conference` and
`teams_by_division`. Also fetches a team's game log (async).

```bash
uv run python examples/team_lookup.py
```

### [metrics.py](metrics.py)

Compute derived metrics from `fastbreak.metrics` across four pure-computation demos and two live-API demos:

- **Part 1** — basic efficiency: `game_score`, `true_shooting`, `effective_fg_pct`, `relative_ts/efg`, `is_double/triple_double`
- **Part 2** — rate stats: `per_36`, `free_throw_rate`, `three_point_rate`, `ast_to_tov` across three player archetypes
- **Part 3** — on-floor impact: `usage_pct`, `ast_pct`, `oreb_pct`, `dreb_pct`, `stl_pct`, `blk_pct` with fabricated team context
- **Part 4** — full PER pipeline: `pace_adjusted_per` → weighted lg_aPER → `per` for a five-player lineup
- **Part 5** *(live API)* — Game Score leaderboard for yesterday's games
- **Part 6** *(live API)* — usage%, AST%, pts/36, and A/TO from real box score data
- **Part 7** — team ratings: `ortg`, `drtg`, `net_rtg` for blowout and close-game scenarios
- **Part 8** — rolling averages: `rolling_avg` over a 10-game sequence with warm-up and DNP handling

```bash
uv run python examples/metrics.py
```

### [schedule.py](schedule.py)

Fetch a team's full season schedule using `get_team_schedule`, detect back-to-back games with
`is_back_to_back`, and inspect rest days between games with `days_rest_before_game`.

```bash
uv run python examples/schedule.py
```

## Advanced Examples

### [player_advanced.py](player_advanced.py)

Advanced player analytics: career game log across all seasons (`get_career_game_logs`),
on/off court splits (`get_on_off_splits`), and offensive play-type breakdown by possessions
(`get_player_playtypes`). Uses Andrew Nembhard as the example player.

```bash
uv run python examples/player_advanced.py
```

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

Fetch team season stats, lineup analysis, current roster, and coaching staff using `fastbreak.teams`.
Covers 5-man lineup plus/minus, two-man combination minutes, `get_team_roster`, and `get_team_coaches`.

```bash
uv run python examples/team_stats.py
```

### [team_advanced.py](team_advanced.py)

Advanced team analytics: live league-average stats via `get_league_averages`, offensive
play-type breakdown with `get_team_playtypes`, and 5-man lineup net ratings from
`get_lineup_net_ratings`. Uses the Indiana Pacers as the example team.

```bash
uv run python examples/team_advanced.py
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
