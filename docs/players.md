# fastbreak.players

High-level async helpers for working with NBA player data. These functions wrap the underlying endpoints so you never have to know which endpoint to call, what parameters it accepts, or how to parse the response.

All functions are async and take an `NBAClient` instance as the first argument. The `season` parameter defaults to the current season when omitted.

```python
from fastbreak.players import (
    search_players,
    get_player,
    get_player_id,
    get_player_game_log,
    get_player_stats,
    get_league_leaders,
    get_hustle_stats,
    get_career_game_logs,
    get_on_off_splits,
    get_player_playtypes,
)
```

---

## Function Reference

### `search_players`

```python
async def search_players(
    client: NBAClient,
    query: str,
    *,
    season: Season | None = None,
    limit: int = 10,
) -> list[PlayerIndexEntry]
```

Fuzzy search across all players in a given season by partial name match. The search is case-insensitive and matches against first name, last name, or full name.

Results are sorted by relevance tier, then alphabetically by last name within each tier:

| Priority | Match condition |
|----------|----------------|
| 0 | Exact full-name match |
| 1 | Last name starts with query |
| 2 | First name starts with query |
| 3 | Query appears anywhere in first, last, or full name |

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `query` | `str` | required | Search string — partial or full name |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `limit` | `int` | `10` | Maximum number of results to return |

**Returns** `list[PlayerIndexEntry]` — matching player entries, ordered by relevance

**Raises** `ValueError` if `limit < 1`

Returns an empty list if `query` is empty or whitespace.

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import search_players

async def main():
    async with NBAClient() as client:
        results = await search_players(client, "curry")
        for p in results:
            print(p.person_id, p.player_first_name, p.player_last_name, p.team_abbreviation)

asyncio.run(main())
```

---

### `get_player`

```python
async def get_player(
    client: NBAClient,
    identifier: int | str,
    *,
    season: Season | None = None,
) -> PlayerIndexEntry | None
```

Look up a single player by their NBA player ID (integer) or exact full name (string).

- **Integer lookup** — searches the player index for a matching `person_id`. Logs a warning if no match is found (unexpected for valid IDs).
- **String lookup** — delegates to `search_players` with `limit=1` and requires the full name to match exactly (case-insensitive). Logs a debug message if not found.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `identifier` | `int \| str` | required | Player ID (`int`) or exact full name (`str`) |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |

**Returns** `PlayerIndexEntry | None` — the player entry, or `None` if not found

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player

async def main():
    async with NBAClient() as client:
        # Look up by player ID
        player = await get_player(client, 201939)
        if player:
            print(f"Found by ID: {player.player_first_name} {player.player_last_name}")

        # Look up by exact name
        player = await get_player(client, "Stephen Curry")
        if player:
            print(f"Found by name: #{player.jersey_number}, {player.team_abbreviation}")
            print(f"  {player.pts:.1f} pts / {player.reb:.1f} reb / {player.ast:.1f} ast")

asyncio.run(main())
```

---

### `get_player_id`

```python
async def get_player_id(
    client: NBAClient,
    name: str,
    *,
    season: Season | None = None,
) -> int | None
```

Convenience shortcut that returns just the integer `person_id` for a player found by exact name. Equivalent to calling `get_player` and accessing `.person_id`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `name` | `str` | required | Exact full name of the player |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |

**Returns** `int | None` — the player ID, or `None` if not found

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_id

async def main():
    async with NBAClient() as client:
        player_id = await get_player_id(client, "Giannis Antetokounmpo")
        if player_id:
            print(f"Giannis player ID: {player_id}")
        else:
            print("Player not found")

asyncio.run(main())
```

---

### `get_player_game_log`

```python
async def get_player_game_log(
    client: NBAClient,
    *,
    player_id: int,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerGameLogEntry]
```

Fetch a player's game-by-game box score statistics for a single season. Returns one `PlayerGameLogEntry` per game played.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, `"Pre Season"`, `"All Star"`, or `"PlayIn"` |

**Returns** `list[PlayerGameLogEntry]`

Each entry has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `game_id` | `str` | NBA game ID |
| `game_date` | `str` | Date string (e.g. `"OCT 22, 2024"`) |
| `matchup` | `str` | Matchup string (e.g. `"GSW vs. LAL"`) |
| `wl` | `str \| None` | Win/loss result (`"W"` or `"L"`) |
| `minutes` | `int \| None` | Minutes played |
| `pts` | `int` | Points scored |
| `reb` | `int` | Total rebounds |
| `ast` | `int` | Assists |
| `stl` | `int` | Steals |
| `blk` | `int` | Blocks |
| `tov` | `int` | Turnovers |
| `fgm` / `fga` / `fg_pct` | `int / int / float \| None` | Field goals |
| `fg3m` / `fg3a` / `fg3_pct` | `int / int / float \| None` | Three-pointers |
| `ftm` / `fta` / `ft_pct` | `int / int / float \| None` | Free throws |
| `oreb` / `dreb` | `int` | Offensive / defensive rebounds |
| `plus_minus` | `int \| None` | Plus/minus |

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_game_log

async def main():
    async with NBAClient() as client:
        # LeBron James (ID: 2544) current season game log
        games = await get_player_game_log(client, player_id=2544)

        print(f"Games played: {len(games)}")
        for game in games[:5]:
            result = game.wl or "?"
            print(
                f"  {game.game_date:<15} {game.matchup:<20} "
                f"{result}  {game.pts:>3} pts  {game.reb:>2} reb  {game.ast:>2} ast"
            )

        # Playoff game log
        playoff_games = await get_player_game_log(
            client,
            player_id=2544,
            season="2024-25",
            season_type="Playoffs",
        )
        print(f"Playoff games: {len(playoff_games)}")

asyncio.run(main())
```

---

### `get_player_stats`

```python
async def get_player_stats(
    client: NBAClient,
    player_id: int,
    *,
    per_mode: PerMode = "PerGame",
) -> PlayerCareerStatsResponse
```

Fetch career statistics for a player, including season-by-season totals, career totals, rankings, and stat highs. This wraps the `PlayerCareerStats` endpoint.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `per_mode` | `PerMode` | `"PerGame"` | Aggregation mode — see table below |

**`per_mode` values**

| Value | Description |
|-------|-------------|
| `"PerGame"` | Per-game averages |
| `"Totals"` | Raw season totals |
| `"Per36"` | Per-36-minutes rates |
| `"Per40"` | Per-40-minutes rates |
| `"Per48"` | Per-48-minutes rates |
| `"Per100Possessions"` | Per-100-possessions rates |

**Returns** `PlayerCareerStatsResponse` with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `season_totals_regular_season` | `list[SeasonTotals]` | One row per season in the regular season |
| `career_totals_regular_season` | `list[CareerTotals]` | Aggregate career regular season totals |
| `season_totals_post_season` | `list[SeasonTotals]` | One row per playoff season |
| `career_totals_post_season` | `list[CareerTotals]` | Aggregate career playoff totals |
| `season_totals_all_star` | `list[SeasonTotals]` | All-Star game appearances by season |
| `career_totals_all_star` | `list[CareerTotals]` | Aggregate career All-Star totals |
| `season_totals_college` | `list[CollegeSeasonTotals]` | College season stats (if available) |
| `career_totals_college` | `list[CollegeCareerTotals]` | Aggregate college career totals (if available) |
| `season_totals_showcase` | `list[SeasonTotals]` | NBA G League Showcase stats by season |
| `career_totals_showcase` | `list[CareerTotals]` | Aggregate career G League Showcase totals |
| `season_rankings_regular_season` | `list[SeasonRankings]` | Per-season stat rankings (regular season) |
| `season_rankings_post_season` | `list[SeasonRankings]` | Per-season stat rankings (playoffs) |
| `season_highs` | `list[StatHigh]` | Single-game season highs |
| `career_highs` | `list[StatHigh]` | Career single-game highs |

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_stats

async def main():
    async with NBAClient() as client:
        # Stephen Curry (ID: 201939) career per-game stats
        stats = await get_player_stats(client, 201939)

        print("Season-by-season averages:")
        for season in stats.season_totals_regular_season:
            print(
                f"  {season.season_id}  {season.team_abbreviation:<4} "
                f"{season.gp:>3} GP  {season.pts:.1f} pts  "
                f"{season.ast:.1f} ast  {season.fg3_pct:.3f} 3P%"
            )

        career = stats.career_totals_regular_season
        if career:
            c = career[0]
            print(f"\nCareer: {c.gp} GP  {c.pts:.1f} pts  {c.ast:.1f} ast")

        # Career highs
        print("\nCareer highs:")
        for high in stats.career_highs:
            print(f"  {high.stat}: {high.stat_value} vs {high.vs_team_abbreviation} ({high.game_date})")

asyncio.run(main())
```

---

### `get_league_leaders`

```python
async def get_league_leaders(
    client: NBAClient,
    *,
    season: Season | None = None,
    stat_category: StatCategoryAbbreviation = "PTS",
    season_type: SeasonType = "Regular Season",
    limit: int | None = None,
) -> list[LeagueLeader]
```

Fetch the league leaders ranked by a statistical category. Results are pre-sorted by rank (ascending) as returned by the NBA Stats API.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `stat_category` | `StatCategoryAbbreviation` | `"PTS"` | Stat to rank by — see table below |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, etc. |
| `limit` | `int \| None` | `None` (all) | Cap the number of results returned |

**`stat_category` values**

`"PTS"`, `"FGM"`, `"FGA"`, `"FG_PCT"`, `"FG3M"`, `"FG3A"`, `"FG3_PCT"`, `"FTM"`, `"FTA"`, `"OREB"`, `"DREB"`, `"REB"`, `"AST"`, `"STL"`, `"BLK"`, `"TOV"`

**Returns** `list[LeagueLeader]`

Each `LeagueLeader` entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `rank` | `int` | League rank (1 = best) |
| `player_id` | `int` | NBA player ID |
| `player` | `str` | Player name |
| `team_id` | `int` | Team ID |
| `team` | `str` | Team abbreviation |
| `gp` | `int` | Games played |
| `min` | `float` | Minutes per game |
| `pts` | `float` | Points |
| `reb` | `float` | Rebounds |
| `ast` | `float` | Assists |
| `stl` | `float` | Steals |
| `blk` | `float` | Blocks |
| `tov` | `float` | Turnovers |
| `fg_pct` | `float \| None` | Field goal percentage |
| `fg3_pct` | `float \| None` | Three-point percentage |
| `ft_pct` | `float \| None` | Free throw percentage |
| `eff` | `float` | Efficiency rating |

**Raises** `ValueError` if `limit < 1`

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_league_leaders

async def main():
    async with NBAClient() as client:
        # Top 10 scorers
        scorers = await get_league_leaders(client, stat_category="PTS", limit=10)
        print("Top 10 scorers:")
        for leader in scorers:
            print(f"  {leader.rank:>2}. {leader.player:<25} {leader.team:<4} {leader.pts:.1f} ppg")

        # Top 5 assist leaders
        assisters = await get_league_leaders(client, stat_category="AST", limit=5)
        print("\nTop 5 assist leaders:")
        for leader in assisters:
            print(f"  {leader.rank:>2}. {leader.player:<25} {leader.team:<4} {leader.ast:.1f} apg")

        # Playoff rebounding leaders
        rebounders = await get_league_leaders(
            client,
            stat_category="REB",
            season_type="Playoffs",
            limit=5,
        )
        print("\nPlayoff rebounding leaders:")
        for leader in rebounders:
            print(f"  {leader.rank:>2}. {leader.player:<25} {leader.reb:.1f} rpg")

asyncio.run(main())
```

---

### `get_hustle_stats`

```python
async def get_hustle_stats(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> LeagueHustlePlayer | None
```

Fetch season hustle statistics for a single player. The function fetches the full league-wide hustle stats response and filters to the given `player_id`.

Hustle stats capture effort plays that do not appear in the traditional box score: contested shots, deflections, charges drawn, screen assists, loose balls recovered, and box outs.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"` or `"Playoffs"` |

**Returns** `LeagueHustlePlayer | None` — the player's hustle row, or `None` if not found. Logs a warning when the player is not present in the response (e.g., too few games played to qualify).

**`LeagueHustlePlayer` fields**

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Player name |
| `team_id` | `int` | Team ID |
| `team_abbreviation` | `str` | Team abbreviation |
| `age` | `float \| None` | Player age |
| `g` | `int` | Games played |
| `min` | `float` | Minutes per game |
| `contested_shots` | `float` | Total contested shots per game |
| `contested_shots_2pt` | `float` | Contested 2-point shots per game |
| `contested_shots_3pt` | `float` | Contested 3-point shots per game |
| `deflections` | `float` | Deflections per game |
| `charges_drawn` | `float` | Charges drawn per game |
| `screen_assists` | `float` | Screen assists per game |
| `screen_ast_pts` | `float` | Points scored off screen assists per game |
| `loose_balls_recovered` | `float` | Loose balls recovered per game |
| `off_loose_balls_recovered` | `float` | Offensive loose balls recovered per game |
| `def_loose_balls_recovered` | `float` | Defensive loose balls recovered per game |
| `box_outs` | `float` | Box outs per game |
| `off_boxouts` | `float` | Offensive box outs per game |
| `def_boxouts` | `float` | Defensive box outs per game |

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_hustle_stats

async def main():
    async with NBAClient() as client:
        # Stephen Curry hustle stats
        hustle = await get_hustle_stats(client, player_id=201939)
        if hustle:
            print(f"{hustle.player_name} ({hustle.team_abbreviation})")
            print(f"  Contested shots: {hustle.contested_shots:.1f}/game")
            print(f"  Deflections:     {hustle.deflections:.1f}/game")
            print(f"  Screen assists:  {hustle.screen_assists:.1f}/game")
            print(f"  Charges drawn:   {hustle.charges_drawn:.1f}/game")
            print(f"  Box outs:        {hustle.box_outs:.1f}/game")
            print(f"  Loose balls:     {hustle.loose_balls_recovered:.1f}/game")
        else:
            print("Player not found in hustle stats (may not qualify)")

asyncio.run(main())
```

---

### `get_career_game_logs`

```python
async def get_career_game_logs(
    client: NBAClient,
    player_id: int,
    *,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerGameLogEntry]
```

Fetch every game log entry across a player's entire career in a single call. Internally, this function:

1. Calls `PlayerCareerStats` to discover all seasons the player has appeared in.
2. Fires one `PlayerGameLog` request per season, concurrently via `client.get_many()`.
3. Flattens all responses into a single list and returns it.

The seasons are processed in the order returned by `PlayerCareerStats` (typically chronological). Within each season the entries appear in the order returned by `PlayerGameLog` (typically reverse-chronological — most recent game first).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"` or `"Playoffs"` |

**Returns** `list[PlayerGameLogEntry]` — flat list of all game entries across the player's career. Returns an empty list if the player has no seasons on record for the given `season_type`.

**Note on concurrency** — all per-season requests run concurrently. For a long-tenured player like LeBron James, this fires 20+ requests simultaneously. Use `NBAClient(request_delay=...)` or `NBAClient(cache_ttl=...)` if you need to be more conservative with rate limits.

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_career_game_logs

async def main():
    async with NBAClient() as client:
        # LeBron James (ID: 2544) — entire career
        games = await get_career_game_logs(client, player_id=2544)

        print(f"Total career games: {len(games)}")

        wins = sum(1 for g in games if g.wl == "W")
        losses = sum(1 for g in games if g.wl == "L")
        print(f"Career record: {wins}W - {losses}L")

        avg_pts = sum(g.pts for g in games) / len(games) if games else 0
        print(f"Career scoring average: {avg_pts:.1f} pts/game")

        # 40-point games
        games_40 = [g for g in games if g.pts >= 40]
        print(f"40+ point games: {len(games_40)}")

        # Career playoff game log
        playoff_games = await get_career_game_logs(
            client, player_id=2544, season_type="Playoffs"
        )
        print(f"Total playoff games: {len(playoff_games)}")

asyncio.run(main())
```

---

### `get_on_off_splits`

```python
async def get_on_off_splits(
    client: NBAClient,
    player_id: int,
    team_id: int,
    season: Season | None = None,
    *,
    per_mode: PerMode = "PerGame",
    season_type: SeasonType = "Regular Season",
) -> dict[str, list[PlayerOnCourtDetail]]
```

Fetch team performance splits based on whether a specific player is on or off the court. Returns a dictionary with two keys: `"on"` and `"off"`, each containing a list of `PlayerOnCourtDetail` rows.

The data represents **team** statistics (points scored, field goal percentage, net rating, etc.) aggregated over all possessions where the player was on or off the floor — not the player's individual statistics.

`team_id` is required because the underlying `LeaguePlayerOnDetails` endpoint is scoped to a team.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `team_id` | `int` | required | NBA team ID the player currently plays for |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `per_mode` | `PerMode` | `"PerGame"` | `"PerGame"`, `"Per36"`, `"Totals"`, etc. |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, etc. |

**Returns** `dict[str, list[PlayerOnCourtDetail]]` — a dict with keys `"on"` and `"off"`

**Important caveat** — the `pts` field in each `PlayerOnCourtDetail` row is the **team's** points per game while the player is on or off the court. It is not the individual player's scoring output.

**`PlayerOnCourtDetail` fields (selected)**

| Field | Type | Description |
|-------|------|-------------|
| `court_status` | `str` | `"On"` or `"Off"` |
| `vs_player_id` | `int` | The tracked player's ID |
| `vs_player_name` | `str` | The tracked player's name |
| `team_id` | `int` | Team ID |
| `team_abbreviation` | `str` | Team abbreviation |
| `gp` | `int` | Games played |
| `w` / `losses` | `int` | Wins / losses |
| `w_pct` | `float` | Win percentage |
| `min` | `float` | Minutes per game |
| `pts` | `float` | Team points per game (not player's individual points) |
| `reb` / `ast` / `stl` / `blk` | `float` | Team stats per game |
| `fg_pct` / `fg3_pct` / `ft_pct` | `float \| None` | Team shooting percentages |
| `plus_minus` | `float` | Team net rating |

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_on_off_splits

async def main():
    async with NBAClient() as client:
        # LeBron James (2544) on the Los Angeles Lakers (1610612747)
        splits = await get_on_off_splits(
            client,
            player_id=2544,
            team_id=1610612747,
        )

        on_rows = splits["on"]
        off_rows = splits["off"]

        if on_rows:
            on = on_rows[0]
            print(f"With LeBron ON court:")
            print(f"  Team pts/game: {on.pts:.1f}")
            print(f"  Team FG%:      {on.fg_pct:.3f}" if on.fg_pct else "  Team FG%: N/A")
            print(f"  Net rating:    {on.plus_minus:+.1f}")

        if off_rows:
            off = off_rows[0]
            print(f"\nWith LeBron OFF court:")
            print(f"  Team pts/game: {off.pts:.1f}")
            print(f"  Team FG%:      {off.fg_pct:.3f}" if off.fg_pct else "  Team FG%: N/A")
            print(f"  Net rating:    {off.plus_minus:+.1f}")

        if on_rows and off_rows:
            diff = on_rows[0].pts - off_rows[0].pts
            print(f"\nImpact (on - off pts/game): {diff:+.1f}")

asyncio.run(main())
```

---

### `get_player_playtypes`

```python
async def get_player_playtypes(
    client: NBAClient,
    player_id: int,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
    type_grouping: str = "offensive",
) -> list[PlayerSynergyPlaytype]
```

Fetch Synergy play-type breakdown statistics for a player. Returns one `PlayerSynergyPlaytype` row per play type (isolation, pick-and-roll, post-up, spot-up, etc.).

**IMPORTANT CAVEAT** — The `SynergyPlaytypes` endpoint returns 0 rows on the public NBA Stats API. Play-type data from Synergy is restricted and not available through the public endpoint. This function will always return an empty list. It is not a bug in fastbreak.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `NBAClient` | required | Active NBA API client |
| `player_id` | `int` | required | NBA player ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"` or `"Playoffs"` |
| `type_grouping` | `str` | `"offensive"` | `"offensive"` or `"defensive"` |

**Returns** `list[PlayerSynergyPlaytype]` — one entry per play type. Returns an empty list if no data is available (currently always the case on the public API).

**`PlayerSynergyPlaytype` fields**

| Field | Type | Description |
|-------|------|-------------|
| `season_id` | `str` | Season ID |
| `player_id` | `int` | NBA player ID |
| `player_name` | `str` | Player name |
| `team_id` | `int` | Team ID |
| `team_abbreviation` | `str` | Team abbreviation |
| `team_name` | `str` | Team name |
| `play_type` | `str` | Play type name (e.g. `"Isolation"`, `"PRBallHandler"`) |
| `type_grouping` | `str` | `"offensive"` or `"defensive"` |
| `gp` | `int` | Games played |
| `poss` | `float` | Total possessions |
| `poss_pct` | `float` | Share of team possessions |
| `ppp` | `float` | Points per possession |
| `pts` | `float` | Total points |
| `fgm` | `float` | Field goals made |
| `fga` | `float` | Field goals attempted |
| `fgmx` | `float` | Missed field goals |
| `fg_pct` | `float` | Field goal percentage |
| `score_poss_pct` | `float` | Percentage of possessions resulting in a score |
| `tov_poss_pct` | `float` | Turnover rate |
| `ft_poss_pct` | `float` | Free throw rate |
| `sf_poss_pct` | `float` | Shooting foul rate |
| `plusone_poss_pct` | `float` | And-one rate |
| `efg_pct` | `float` | Effective field goal percentage |
| `percentile` | `float` | Percentile rank vs. league |

**Play type values**

`"Isolation"`, `"Transition"`, `"PRBallHandler"`, `"PRRollman"`, `"Postup"`, `"Spotup"`, `"Handoff"`, `"Cut"`, `"OffScreen"`, `"OffRebound"`, `"Misc"`

**Example**

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_playtypes

async def main():
    async with NBAClient() as client:
        # NOTE: This will return an empty list — Synergy data is restricted
        # on the public NBA Stats API. The example shows the intended usage
        # for when/if the endpoint becomes accessible.
        plays = await get_player_playtypes(client, player_id=2544)

        if plays:
            print("Offensive play-type breakdown (sorted by possessions):")
            for p in sorted(plays, key=lambda x: x.poss, reverse=True):
                print(
                    f"  {p.play_type:<20} "
                    f"{p.poss:>6.0f} poss  "
                    f"{p.ppp:.3f} ppp  "
                    f"{p.poss_pct:.1%} of possessions"
                )
        else:
            print("No play-type data available (endpoint restricted on public API)")

asyncio.run(main())
```

---

## Complete Examples

### Player lookup and profile display

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player, search_players

async def main():
    async with NBAClient() as client:
        # Search by partial name
        results = await search_players(client, "ant")
        print(f"Found {len(results)} matches for 'ant':")
        for p in results:
            team = p.team_abbreviation or "FA"
            print(f"  {p.person_id}  {p.player_first_name} {p.player_last_name}  ({team})")

        print()

        # Exact lookup
        player = await get_player(client, "Anthony Edwards")
        if player:
            print(f"Anthony Edwards profile:")
            print(f"  ID:       {player.person_id}")
            print(f"  Team:     {player.team_city} {player.team_name} ({player.team_abbreviation})")
            print(f"  Position: {player.position}")
            print(f"  Height:   {player.height}")
            print(f"  College:  {player.college}")
            if player.pts is not None:
                print(f"  Stats:    {player.pts:.1f} pts / {player.reb:.1f} reb / {player.ast:.1f} ast")

asyncio.run(main())
```

### Season analysis: recent form

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_game_log

async def main():
    async with NBAClient() as client:
        # Stephen Curry last 10 games
        games = await get_player_game_log(client, player_id=201939)
        recent = games[:10]

        print(f"Stephen Curry — last {len(recent)} games")
        print(f"{'Date':<15} {'Matchup':<22} {'W/L':<4} {'PTS':>4} {'REB':>4} {'AST':>4} {'3PM':>4}")
        print("-" * 65)
        for g in recent:
            result = g.wl or " "
            print(
                f"{g.game_date:<15} {g.matchup:<22} {result:<4} "
                f"{g.pts:>4} {g.reb:>4} {g.ast:>4} {g.fg3m:>4}"
            )

        avg_pts = sum(g.pts for g in recent) / len(recent)
        avg_3pm = sum(g.fg3m for g in recent) / len(recent)
        print(f"\nAverage over last {len(recent)} games: {avg_pts:.1f} pts, {avg_3pm:.1f} 3PM")

asyncio.run(main())
```

### Career scoring trajectory

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_player_stats

async def main():
    async with NBAClient() as client:
        stats = await get_player_stats(client, 2544)  # LeBron James

        print("LeBron James — career scoring by season")
        print(f"{'Season':<10} {'Team':<5} {'GP':>4} {'PTS':>6} {'AST':>5} {'REB':>5} {'FG%':>6}")
        print("-" * 45)
        for s in stats.season_totals_regular_season:
            print(
                f"{s.season_id:<10} {s.team_abbreviation:<5} "
                f"{s.gp:>4} {s.pts:>6.1f} {s.ast:>5.1f} {s.reb:>5.1f} {s.fg_pct:>6.3f}"
            )

asyncio.run(main())
```

### League leaders dashboard

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_league_leaders

async def main():
    async with NBAClient() as client:
        categories = [
            ("PTS", "Points"),
            ("REB", "Rebounds"),
            ("AST", "Assists"),
            ("STL", "Steals"),
            ("BLK", "Blocks"),
        ]

        for stat, label in categories:
            leaders = await get_league_leaders(client, stat_category=stat, limit=3)
            print(f"\nTop 3 {label}:")
            for leader in leaders:
                value = getattr(leader, stat.lower(), None)
                if value is None:
                    # percentage fields have different attr names
                    value = getattr(leader, stat.lower().replace("_pct", "_pct"), 0.0)
                print(f"  {leader.rank}. {leader.player:<25} {leader.team:<5} {value:.1f}")

asyncio.run(main())
```

### Career game log with filtering

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.players import get_career_game_logs

async def main():
    async with NBAClient(cache_ttl=600) as client:
        # Fetch every game LeBron has ever played
        all_games = await get_career_game_logs(client, player_id=2544)

        total = len(all_games)
        wins = sum(1 for g in all_games if g.wl == "W")
        avg_pts = sum(g.pts for g in all_games) / total if total else 0

        print(f"LeBron James career game log")
        print(f"  Total games:  {total}")
        print(f"  Record:       {wins}W - {total - wins}L")
        print(f"  Scoring avg:  {avg_pts:.2f} pts/game")

        # Triple-doubles
        triple_doubles = [
            g for g in all_games
            if g.pts >= 10 and g.reb >= 10 and g.ast >= 10
        ]
        print(f"  Triple-doubles: {len(triple_doubles)}")

        # Playoff career log
        playoff_games = await get_career_game_logs(
            client, player_id=2544, season_type="Playoffs"
        )
        avg_playoff_pts = sum(g.pts for g in playoff_games) / len(playoff_games) if playoff_games else 0
        print(f"  Playoff games:  {len(playoff_games)}  ({avg_playoff_pts:.1f} pts avg)")

asyncio.run(main())
```

---

## Helpers vs. Raw Endpoints

The helpers in `fastbreak.players` cover the most common workflows. Use them when you want to get data quickly without knowing the endpoint names or parameter structures.

Use raw endpoints directly when you need access to parameters not exposed by the helpers:

| Need | Use helper | Use raw endpoint |
|------|-----------|-----------------|
| Current season game log | `get_player_game_log` | `PlayerGameLog` (date range filtering) |
| Season averages | `get_player_stats` | `PlayerDashboardByGeneralSplits` (home/away/win/loss splits with date range) |
| League leaders | `get_league_leaders` | `LeagueLeaders` (scope, per-game vs. totals mode) |
| Hustle stats for one player | `get_hustle_stats` | `LeagueHustleStatsPlayer` (positional filters, age filters) |
| Career game logs | `get_career_game_logs` | `PlayerCareerStats` + `PlayerGameLog` (subset of seasons) |
| On/off splits | `get_on_off_splits` | `LeaguePlayerOnDetails` (full team roster at once) |

Example — using a raw endpoint for date-range filtering not available through the helper:

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.endpoints import PlayerGameLog

async def main():
    async with NBAClient() as client:
        # Raw endpoint access: date_from / date_to params not exposed by the helper
        endpoint = PlayerGameLog(
            player_id=201939,
            season="2024-25",
            season_type="Regular Season",
            date_from="01/01/2025",
            date_to="03/01/2025",
        )
        response = await client.get(endpoint)
        print(f"Games in date range: {len(response.games)}")
        for g in response.games:
            print(f"  {g.game_date}  {g.matchup}  {g.pts} pts")

asyncio.run(main())
```
