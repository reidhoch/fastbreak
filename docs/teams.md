# fastbreak.teams

The `fastbreak.teams` module provides two categories of functionality:

- **Sync lookup functions** backed by a static in-memory registry of all 30 NBA teams. These require no network I/O and no `NBAClient` instance.
- **Async API functions** that call the NBA Stats API and return structured Pydantic models. All async functions take a `NBAClient` as their first argument.

```python
from fastbreak.teams import (
    # Static registry
    TEAMS, TeamID, TeamInfo,
    # Sync lookups
    get_team, get_team_id, search_teams,
    teams_by_conference, teams_by_division,
    # Async API helpers
    get_team_game_log, get_team_stats, get_lineup_stats,
    get_lineup_net_ratings, get_league_averages, get_team_playtypes,
    get_team_roster, get_team_coaches,
)
```

---

## Static Team Registry

### `TEAMS: dict[int, TeamInfo]`

A dictionary mapping integer team ID to `TeamInfo` for all 30 current NBA teams. Keys are the same values defined in the `TeamID` enum.

```python
from fastbreak.teams import TEAMS

# Iterate all teams
for team_id, team in TEAMS.items():
    print(f"{team.abbreviation:3s}  {team.full_name}")

# Direct lookup by integer ID
lakers = TEAMS[1610612747]
print(lakers.full_name)   # "Los Angeles Lakers"
```

### `TeamInfo`

A frozen dataclass (`frozen=True, slots=True`) representing static metadata for one NBA team.

| Field          | Type         | Example                    |
|----------------|--------------|----------------------------|
| `id`           | `TeamID`     | `TeamID.LAKERS` (1610612747) |
| `abbreviation` | `str`        | `"LAL"`                    |
| `city`         | `str`        | `"Los Angeles"`            |
| `name`         | `str`        | `"Lakers"`                 |
| `full_name`    | `str`        | `"Los Angeles Lakers"`     |
| `conference`   | `Conference` | `"West"`                   |
| `division`     | `Division`   | `"Pacific"`                |

`Conference` is `Literal["East", "West"]` and `Division` is one of `"Atlantic"`, `"Central"`, `"Southeast"`, `"Northwest"`, `"Pacific"`, `"Southwest"`.

### `TeamID`

An `IntEnum` with a member for every NBA team, organized by conference and division. Use it for readable constants instead of raw integers.

```python
from fastbreak.teams import TeamID

print(TeamID.CELTICS)       # 1610612738
print(TeamID.LAKERS)        # 1610612747
print(TeamID.PACERS)        # 1610612754

# Works anywhere an int is accepted
team = TEAMS[TeamID.WARRIORS]
```

All 30 members:

**Eastern Conference**
- Atlantic: `CELTICS`, `NETS`, `KNICKS`, `SIXERS`, `RAPTORS`
- Central: `BULLS`, `CAVALIERS`, `PISTONS`, `PACERS`, `BUCKS`
- Southeast: `HAWKS`, `HORNETS`, `HEAT`, `MAGIC`, `WIZARDS`

**Western Conference**
- Northwest: `NUGGETS`, `TIMBERWOLVES`, `THUNDER`, `TRAIL_BLAZERS`, `JAZZ`
- Pacific: `WARRIORS`, `CLIPPERS`, `LAKERS`, `SUNS`, `KINGS`
- Southwest: `MAVERICKS`, `ROCKETS`, `GRIZZLIES`, `PELICANS`, `SPURS`

---

## Sync Lookup Functions

These functions operate entirely on the in-memory `TEAMS` registry. No `NBAClient` or `await` needed.

### `get_team(identifier) -> TeamInfo | None`

Look up a team by integer ID, abbreviation, nickname, or city. Matching is case-insensitive.

```python
def get_team(identifier: int | str) -> TeamInfo | None: ...
```

**Lookup priority (string input):**
1. Abbreviation match (e.g., `"LAL"`, `"BOS"`)
2. Nickname match (e.g., `"Lakers"`, `"Celtics"`)
3. City match (e.g., `"Los Angeles"`, `"Boston"`)

Returns `None` if no team matches.

```python
from fastbreak.teams import get_team

# By integer ID
get_team(1610612747)              # TeamInfo for Los Angeles Lakers

# By abbreviation (case-insensitive)
get_team("LAL")                   # TeamInfo for Los Angeles Lakers
get_team("lal")                   # same result

# By nickname
get_team("Lakers")                # TeamInfo for Los Angeles Lakers
get_team("celtics")               # TeamInfo for Boston Celtics

# By city — returns the first match when multiple teams share a city
get_team("Los Angeles")           # TeamInfo for Los Angeles Lakers (city dict key)

# No match
get_team("Heatles")               # None
```

> Note: The city lookup uses an exact dict match against `team.city`. Los Angeles has two teams (`Clippers` and `Lakers`); the city dict retains only one. LAL (Lakers) appears after LAC (Clippers) in the registry, so Lakers wins the `"los angeles"` key. Prefer abbreviation or nickname for Los Angeles teams to avoid ambiguity.

### `get_team_id(identifier) -> TeamID | None`

Shortcut that calls `get_team()` and returns the integer `TeamID`, or `None` if not found.

```python
def get_team_id(identifier: str) -> TeamID | None: ...
```

```python
from fastbreak.teams import get_team_id

get_team_id("LAL")      # 1610612747
get_team_id("Lakers")   # 1610612747
get_team_id("Unknown")  # None
```

### `search_teams(query, *, limit=5) -> list[TeamInfo]`

Fuzzy partial-match search across abbreviation, nickname, city, and full name. Results are sorted by relevance (exact > full match > prefix > substring), then alphabetically by abbreviation within each tier.

```python
def search_teams(query: str, *, limit: int = 5) -> list[TeamInfo]: ...
```

**Parameters:**
- `query` — search string (partial abbreviation, city, or name)
- `limit` — maximum results to return (default `5`, must be >= 1)

Returns an empty list for blank queries. Raises `ValueError` if `limit < 1`.

```python
from fastbreak.teams import search_teams

search_teams("LAL")     # [TeamInfo(LAL, Los Angeles Lakers)]
search_teams("lakers")  # [TeamInfo(LAL, Los Angeles Lakers)]
search_teams("New")     # [TeamInfo(NOP, New Orleans Pelicans), TeamInfo(NYK, New York Knicks)]
search_teams("Los")     # [TeamInfo(LAC, ...), TeamInfo(LAL, ...)]
search_teams("")        # []
```

### `teams_by_conference(conference) -> list[TeamInfo]`

Return all 15 teams in the specified conference.

```python
def teams_by_conference(conference: str) -> list[TeamInfo]: ...
```

`conference` is case-insensitive and is normalized via `.capitalize()` before matching. Accepts `"East"` or `"West"` (or lower-case equivalents). Raises `ValueError` for unrecognized values.

```python
from fastbreak.teams import teams_by_conference

east = teams_by_conference("East")    # 15 Eastern Conference teams
west = teams_by_conference("west")    # 15 Western Conference teams, case-insensitive
```

### `teams_by_division(division) -> list[TeamInfo]`

Return all 5 teams in the specified division.

```python
def teams_by_division(division: str) -> list[TeamInfo]: ...
```

`division` is case-insensitive and normalized via `.capitalize()`. Valid values:
`"Atlantic"`, `"Central"`, `"Southeast"`, `"Northwest"`, `"Pacific"`, `"Southwest"`.
Raises `ValueError` for unrecognized values.

```python
from fastbreak.teams import teams_by_division

atlantic = teams_by_division("Atlantic")    # BOS, BKN, NYK, PHI, TOR
southwest = teams_by_division("southwest")  # case-insensitive
```

---

## Async API Functions

All async functions require an active `NBAClient` and must be called with `await` inside an async context. The `season` parameter defaults to the current season (from `fastbreak.seasons.get_season_from_date()`) when omitted.

### `get_team_game_log`

```python
async def get_team_game_log(
    client: NBAClient,
    *,
    team_id: int | TeamID,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[TeamGameLogEntry]: ...
```

Returns one `TeamGameLogEntry` per game played in the season, in the order returned by the API (generally most-recent first).

**Parameters:**
- `client` — active `NBAClient`
- `team_id` — NBA team ID (integer or `TeamID` enum member)
- `season` — season string in `YYYY-YY` format, e.g. `"2025-26"`; defaults to current season
- `season_type` — `"Regular Season"` (default), `"Playoffs"`, `"Pre Season"`, `"All Star"`, or `"PlayIn"`

**`TeamGameLogEntry` fields:**

| Field       | Type          | Description                          |
|-------------|---------------|--------------------------------------|
| `team_id`   | `int`         | Team ID                              |
| `game_id`   | `str`         | NBA game ID                          |
| `game_date` | `str`         | Date string (e.g., `"JAN 15, 2026"`) |
| `matchup`   | `str`         | Matchup string (e.g., `"IND vs. LAL"`) |
| `wl`        | `str \| None` | `"W"` or `"L"`                       |
| `wins`      | `int`         | Running season win total             |
| `losses`    | `int`         | Running season loss total            |
| `win_pct`   | `float`       | Running win percentage               |
| `minutes`   | `int`         | Minutes played                       |
| `fgm`       | `int`         | Field goals made                     |
| `fga`       | `int`         | Field goals attempted                |
| `fg_pct`    | `float \| None` | Field goal percentage              |
| `fg3m`      | `int`         | Three-pointers made                  |
| `fg3a`      | `int`         | Three-pointers attempted             |
| `fg3_pct`   | `float \| None` | Three-point percentage             |
| `ftm`       | `int`         | Free throws made                     |
| `fta`       | `int`         | Free throws attempted                |
| `ft_pct`    | `float \| None` | Free throw percentage              |
| `oreb`      | `int`         | Offensive rebounds                   |
| `dreb`      | `int`         | Defensive rebounds                   |
| `reb`       | `int`         | Total rebounds                       |
| `ast`       | `int`         | Assists                              |
| `stl`       | `int`         | Steals                               |
| `blk`       | `int`         | Blocks                               |
| `tov`       | `int`         | Turnovers                            |
| `pf`        | `int`         | Personal fouls                       |
| `pts`       | `int`         | Points scored                        |

`TeamGameLogEntry` supports `.to_pandas()` and `.to_polars()` via the `PandasMixin` / `PolarsMixin`.

### `get_team_stats`

```python
async def get_team_stats(
    client: NBAClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> list[LeagueDashTeamStatsRow]: ...
```

Returns one `LeagueDashTeamStatsRow` for each of the 30 NBA teams. The list order matches the API default (typically ranked by wins).

**Parameters:**
- `client` — active `NBAClient`
- `season` — defaults to current season
- `season_type` — defaults to `"Regular Season"`
- `per_mode` — aggregation mode; common values: `"PerGame"` (default), `"Totals"`, `"Per36"`, `"Per100Possessions"`

**`LeagueDashTeamStatsRow` key fields:**

| Field         | Type           | Description                  |
|---------------|----------------|------------------------------|
| `team_id`     | `int`          | Team ID                      |
| `team_name`   | `str`          | Team name                    |
| `gp`          | `int`          | Games played                 |
| `w`           | `int`          | Wins                         |
| `losses`      | `int`          | Losses                       |
| `w_pct`       | `float \| None`| Win percentage               |
| `min`         | `float`        | Minutes (per game or totals) |
| `fgm`         | `float`        | Field goals made             |
| `fga`         | `float`        | Field goals attempted        |
| `fg_pct`      | `float \| None`| FG percentage                |
| `fg3m`        | `float`        | Three-pointers made          |
| `fg3a`        | `float`        | Three-pointers attempted     |
| `fg3_pct`     | `float \| None`| 3PT percentage               |
| `ftm`         | `float`        | Free throws made             |
| `fta`         | `float`        | Free throws attempted        |
| `ft_pct`      | `float \| None`| FT percentage                |
| `oreb`        | `float`        | Offensive rebounds           |
| `dreb`        | `float`        | Defensive rebounds           |
| `reb`         | `float`        | Total rebounds               |
| `ast`         | `float`        | Assists                      |
| `tov`         | `float`        | Turnovers                    |
| `stl`         | `float`        | Steals                       |
| `blk`         | `float`        | Blocks                       |
| `blka`        | `float`        | Blocked field goal attempts  |
| `pf`          | `float`        | Personal fouls               |
| `pfd`         | `float`        | Personal fouls drawn         |
| `pts`         | `float`        | Points                       |
| `plus_minus`  | `float`        | Plus/minus                   |

Each row also carries a corresponding `_rank` field for every stat (e.g. `pts_rank`, `ast_rank`), giving the team's rank among all 30 teams for that category.

### `get_lineup_stats`

```python
async def get_lineup_stats(
    client: NBAClient,
    team_id: int | TeamID,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    group_quantity: int = 5,
) -> list[LineupStats]: ...
```

Returns lineup combination stats for a team. Defaults to 5-man lineups (`group_quantity=5`); use `2`–`4` for smaller groupings.

The API returns lineups sorted by total minutes played (descending) by default.

> **Important:** `lineup.min` is the **per-game average minutes** the lineup was on the floor, not total accumulated minutes. This naming is misleading — do not sum it across lineups.

**`LineupStats` key fields:**

| Field            | Type          | Description                                    |
|------------------|---------------|------------------------------------------------|
| `group_set`      | `str`         | Grouping label (e.g., `"Lineups"`)             |
| `group_id`       | `str`         | Pipe-delimited player IDs                      |
| `group_name`     | `str`         | Player names (e.g., `"LeBron - AD - ..."`)     |
| `gp`             | `int`         | Games played together                          |
| `w`              | `int`         | Wins                                           |
| `losses`         | `int`         | Losses                                         |
| `w_pct`          | `float`       | Win percentage                                 |
| `min`            | `float`       | **Per-game average minutes** (not total)       |
| `fgm`–`pfd`      | `float`       | Standard box score stats (per-game or totals)  |
| `pts`            | `float`       | Points                                         |
| `plus_minus`     | `float`       | Net point differential                         |
| `sum_time_played`| `int`         | Raw total seconds played                       |

### `get_lineup_net_ratings`

```python
async def get_lineup_net_ratings(
    client: NBAClient,
    team_id: int | TeamID,
    season: Season | None = None,
    *,
    min_minutes: float = 10.0,
) -> list[tuple[LineupStats, float]]: ...
```

Wraps `get_lineup_stats()` and computes a net rating for each lineup. Returns tuples of `(LineupStats, net_rtg)` sorted best-first (highest net rating first).

Net rating formula: `plus_minus / min * 48` — the lineup's net point differential scaled to 48 minutes.

**Parameters:**
- `client` — active `NBAClient`
- `team_id` — NBA team ID
- `season` — defaults to current season
- `min_minutes` — exclude lineups averaging fewer than this many minutes per game (default `10.0`). Raises the minimum sample threshold to filter noise.

Lineups where `min == 0` (no meaningful time) are also excluded regardless of `min_minutes`.

### `get_league_averages`

```python
async def get_league_averages(
    client: NBAClient,
    season: Season | None = None,
) -> LeagueAverages: ...
```

Computes league-wide per-game averages across all 30 teams by calling `get_team_stats()` with `per_mode="PerGame"` and aggregating with `statistics.fmean`.

Returns a `LeagueAverages` dataclass from `fastbreak.metrics`, used as input to the metrics functions `relative_ts()`, `relative_efg()`, `pace_adjusted_per()`, and `per()`.

Raises `ValueError` if the API returns no rows.

**`LeagueAverages` fields:**

| Field      | Description                                      |
|------------|--------------------------------------------------|
| `lg_pts`   | League average points per team per game          |
| `lg_fga`   | League average field goal attempts               |
| `lg_fta`   | League average free throw attempts               |
| `lg_ftm`   | League average free throws made                  |
| `lg_oreb`  | League average offensive rebounds                |
| `lg_treb`  | League average total rebounds                    |
| `lg_ast`   | League average assists                           |
| `lg_fgm`   | League average field goals made                  |
| `lg_fg3m`  | League average three-pointers made               |
| `lg_tov`   | League average turnovers                         |
| `lg_pf`    | League average personal fouls                    |
| `lg_pace`  | Estimated league average possessions per game    |

Pace is estimated as `mean(fga - oreb + tov + 0.44 * fta)` across all 30 teams.

`LeagueAverages` also exposes computed properties: `vop` (value of a possession), `drb_pct` (defensive rebound rate), `factor` (assist factor for PER), `ts` (league TS%), and `efg` (league eFG%).

### `get_team_playtypes`

```python
async def get_team_playtypes(
    client: NBAClient,
    team_id: int,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
    type_grouping: str = "offensive",
) -> list[TeamSynergyPlaytype]: ...
```

Returns play-type breakdown stats for a single team, filtered from the full Synergy playtypes response.

**Parameters:**
- `client` — active `NBAClient`
- `team_id` — NBA team ID (integer only; `TeamID` values work since they are `int` subclasses)
- `season` — defaults to current season
- `season_type` — defaults to `"Regular Season"`
- `type_grouping` — `"offensive"` (default) or `"defensive"`

> **Caveat:** The `SynergyPlaytypes` endpoint always returns 0 rows on the public NBA Stats API. This is a known restriction — play-type data is not available without authentication. `get_team_playtypes()` will return an empty list and will not raise an error.

**`TeamSynergyPlaytype` fields:**

| Field             | Type    | Description                            |
|-------------------|---------|----------------------------------------|
| `season_id`       | `str`   | Season identifier                      |
| `team_id`         | `int`   | Team ID                                |
| `team_abbreviation`| `str`  | Team abbreviation                      |
| `team_name`       | `str`   | Team name                              |
| `play_type`       | `str`   | Play type (e.g., `"Isolation"`)        |
| `type_grouping`   | `str`   | `"offensive"` or `"defensive"`         |
| `percentile`      | `float` | Percentile rank                        |
| `gp`              | `int`   | Games played                           |
| `poss_pct`        | `float` | Share of team possessions              |
| `ppp`             | `float` | Points per possession                  |
| `fg_pct`          | `float` | Field goal percentage                  |
| `ft_poss_pct`     | `float` | Free throw possession rate             |
| `tov_poss_pct`    | `float` | Turnover possession rate               |
| `score_poss_pct`  | `float` | Scoring possession rate                |
| `efg_pct`         | `float` | Effective FG percentage                |
| `poss`            | `float` | Total possessions                      |
| `pts`             | `float` | Points scored                          |
| `fgm`             | `float` | Field goals made                       |
| `fga`             | `float` | Field goals attempted                  |
| `fgmx`            | `float` | Missed field goals                     |

---

### `get_team_roster`

```python
async def get_team_roster(
    client: NBAClient,
    team_id: int,
    season: Season | None = None,
) -> list[RosterPlayer]
```

Returns the current roster players for a team using the `CommonTeamRoster` endpoint.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `client` | `NBAClient` | required | Active NBA client |
| `team_id` | `int` | required | NBA team ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |

**Returns:** `list[RosterPlayer]`

Key fields on `RosterPlayer`:

| Field | Type | Description |
|---|---|---|
| `player_id` | `int` | NBA player ID |
| `player` | `str` | Player full name |
| `num` | `str` | Jersey number |
| `position` | `str` | Position abbreviation (e.g. `"G"`, `"F"`, `"C"`, `"G-F"`) |
| `height` | `str` | Height string (e.g. `"6-6"`) |
| `weight` | `str` | Weight in pounds (e.g. `"215"`) |
| `birth_date` | `str` | Birth date string |
| `age` | `float` | Age at start of season |
| `exp` | `str` | Years of NBA experience (`"R"` for rookie) |
| `school` | `str` | College attended |
| `how_acquired` | `str \| None` | How the player joined the team |

```python
players = await get_team_roster(client, team_id=1610612754)
for p in players:
    print(f"  #{p.num:<3} {p.player:<25} {p.position:<5} {p.height}  {p.weight} lbs")
```

---

### `get_team_coaches`

```python
async def get_team_coaches(
    client: NBAClient,
    team_id: int,
    season: Season | None = None,
) -> list[Coach]
```

Returns the coaching staff for a team. Uses the same `CommonTeamRoster` endpoint as
`get_team_roster()` — both roster and coaches are returned in a single API call.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `client` | `NBAClient` | required | Active NBA client |
| `team_id` | `int` | required | NBA team ID |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |

**Returns:** `list[Coach]` — includes head coach and all assistant coaches.

Key fields on `Coach`:

| Field | Type | Description |
|---|---|---|
| `coach_id` | `int` | Coach ID |
| `first_name` | `str` | First name |
| `last_name` | `str` | Last name |
| `coach_name` | `str` | Full name |
| `is_assistant` | `int` | `0` = head coach, `1` = assistant |
| `coach_type` | `str` | Role description (e.g. `"Head Coach"`, `"Assistant Coach"`) |
| `sort_sequence` | `int \| None` | Display sort order |

```python
coaches = await get_team_coaches(client, team_id=1610612754)
for c in coaches:
    role = "Head Coach" if c.is_assistant == 0 else f"Assistant ({c.coach_type})"
    print(f"  {c.coach_name:<30}  {role}")
```

> **Note:** `get_team_roster()` and `get_team_coaches()` each make a separate API request
> to the same `CommonTeamRoster` endpoint. If you need both the roster and coaching staff,
> call `CommonTeamRoster` directly once and read both `response.players` and `response.coaches`
> from the single response.

---

## Examples

### Sync lookups — no async needed

```python
from fastbreak.teams import (
    get_team, get_team_id, search_teams,
    teams_by_conference, teams_by_division,
    TeamID, TEAMS,
)

# Lookup by abbreviation, nickname, or ID
celtics = get_team("BOS")
lakers  = get_team("Lakers")
pacers  = get_team(1610612754)

print(celtics.full_name)   # Boston Celtics
print(lakers.division)     # Pacific
print(pacers.abbreviation) # IND

# Get just the numeric ID
tid = get_team_id("GSW")   # 1610612744

# Partial-match search
results = search_teams("New")
for team in results:
    print(team.full_name)
# New Orleans Pelicans
# New York Knicks

# Using the TeamID enum constant
print(TeamID.CELTICS == 1610612738)  # True
```

### Browse teams by conference and division

```python
from fastbreak.teams import teams_by_conference, teams_by_division

# All Western Conference teams
west = teams_by_conference("West")
print(f"Western Conference ({len(west)} teams):")
for t in sorted(west, key=lambda t: t.division):
    print(f"  [{t.division:10s}] {t.abbreviation}  {t.full_name}")

# All teams in the Southwest Division
southwest = teams_by_division("Southwest")
for t in southwest:
    print(t.full_name)
# Dallas Mavericks
# Houston Rockets
# Memphis Grizzlies
# New Orleans Pelicans
# San Antonio Spurs
```

### Choosing between get_team() overloads

| Situation | Recommended approach |
|-----------|----------------------|
| You have a well-known abbreviation | `get_team("LAL")` — fastest, unambiguous |
| You have a display name from the user | `get_team("Lakers")` — nickname match |
| You have a city string | Prefer abbreviation or nickname; city lookup is exact and ambiguous for LA |
| You have a raw integer team ID | `get_team(1610612747)` — direct dict lookup |
| You need to search partial user input | `search_teams("Los")` — fuzzy match |
| You want a readable constant in code | `TeamID.LAKERS` — self-documenting |

### Fetch a team's game log

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.teams import get_team_game_log, TeamID

async def main() -> None:
    async with NBAClient() as client:
        games = await get_team_game_log(
            client,
            team_id=TeamID.PACERS,
            season="2025-26",
        )

    print(f"Games played: {len(games)}")
    for game in games[:5]:
        result = game.wl or "?"
        print(f"  {game.game_date:20s}  {game.matchup:25s}  {result}  {game.pts} pts")

asyncio.run(main())
```

### Rank all 30 teams by offensive rating

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.teams import get_team_stats
from fastbreak.metrics import ortg

async def main() -> None:
    async with NBAClient() as client:
        teams = await get_team_stats(client, season="2025-26", per_mode="PerGame")

    # Compute offensive rating for each team and sort descending
    ranked = []
    for t in teams:
        rating = ortg(
            pts=t.pts,
            fga=t.fga,
            oreb=t.oreb,
            tov=t.tov,
            fta=t.fta,
        )
        if rating is not None:
            ranked.append((t.team_name, rating))

    ranked.sort(key=lambda x: x[1], reverse=True)

    print("Offensive Rating (pts per 100 possessions)")
    print(f"{'Rank':4s}  {'Team':<30s}  {'ORtg':>6s}")
    for rank, (name, rating) in enumerate(ranked, 1):
        print(f"{rank:4d}  {name:<30s}  {rating:6.1f}")

asyncio.run(main())
```

### 5-man lineup net ratings

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.teams import get_lineup_net_ratings, TeamID

async def main() -> None:
    async with NBAClient() as client:
        # Get lineups averaging at least 10 minutes per game
        results = await get_lineup_net_ratings(
            client,
            team_id=TeamID.CELTICS,
            season="2025-26",
            min_minutes=10.0,
        )

    print(f"Qualifying lineups: {len(results)}")
    print(f"\n{'Net Rtg':>8s}  {'Min/G':>6s}  {'GP':>4s}  Lineup")
    for lineup, net_rtg in results[:10]:
        print(
            f"{net_rtg:+8.1f}"
            f"  {lineup.min:6.1f}"
            f"  {lineup.gp:4d}"
            f"  {lineup.group_name}"
        )

asyncio.run(main())
```

> Remember: `lineup.min` is the **per-game average** minutes on the floor, not a season total.

### Computing relative stats with `get_league_averages()`

`get_league_averages()` aggregates per-game stats across all 30 teams into a `LeagueAverages` dataclass. Pass it to metrics functions from `fastbreak.metrics` to compute context-relative efficiency numbers.

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.teams import get_team_stats, get_league_averages
from fastbreak.metrics import true_shooting, relative_ts, effective_fg_pct, relative_efg

async def main() -> None:
    async with NBAClient() as client:
        teams, lg = await asyncio.gather(
            get_team_stats(client, season="2025-26"),
            get_league_averages(client, season="2025-26"),
        )

    print(f"League avg TS%:  {lg.ts:.3f}")
    print(f"League avg eFG%: {lg.efg:.3f}")
    print(f"Estimated pace:  {lg.lg_pace:.1f} poss/game")
    print()

    # Relative shooting efficiency for every team
    results = []
    for t in teams:
        ts  = true_shooting(pts=t.pts, fga=t.fga, fta=t.fta)
        efg = effective_fg_pct(fgm=t.fgm, fg3m=t.fg3m, fga=t.fga)
        rel_ts  = relative_ts(ts, lg)
        rel_efg = relative_efg(efg, lg)
        results.append((t.team_name, ts, rel_ts, efg, rel_efg))

    results.sort(key=lambda x: (x[2] or 0.0), reverse=True)

    print(f"{'Team':<30s}  {'TS%':>6s}  {'Rel TS':>8s}  {'eFG%':>6s}  {'Rel eFG':>9s}")
    for name, ts, rel_ts, efg, rel_efg in results:
        ts_s      = f"{ts:.3f}"      if ts      is not None else "  N/A"
        rel_ts_s  = f"{rel_ts:+.3f}" if rel_ts  is not None else "    N/A"
        efg_s     = f"{efg:.3f}"     if efg     is not None else "  N/A"
        rel_efg_s = f"{rel_efg:+.3f}" if rel_efg is not None else "     N/A"
        print(f"{name:<30s}  {ts_s:>6s}  {rel_ts_s:>8s}  {efg_s:>6s}  {rel_efg_s:>9s}")

asyncio.run(main())
```

**Common metrics that accept `LeagueAverages`:**

| Function           | What it computes                                    |
|--------------------|-----------------------------------------------------|
| `relative_ts(ts, lg)` | Player/team TS% minus league average TS%        |
| `relative_efg(efg, lg)` | Player/team eFG% minus league average eFG%    |
| `pace_adjusted_per(...)` | First step toward full PER (aPER)            |
| `per(aper, lg_aper)` | Normalised PER with 15.0 = league average        |

See [fastbreak.metrics](metrics.md) for the full reference.

---

## Type Reference

Types used across `fastbreak.teams` are imported from `fastbreak.types`:

| Type         | Values                                                                    |
|--------------|---------------------------------------------------------------------------|
| `Season`     | `str` validated as `YYYY-YY`, e.g. `"2025-26"`                           |
| `SeasonType` | `"Regular Season"`, `"Playoffs"`, `"Pre Season"`, `"All Star"`, `"PlayIn"` |
| `PerMode`    | `"PerGame"`, `"Totals"`, `"Per36"`, `"Per100Possessions"`, and more       |
| `Conference` | `"East"`, `"West"`                                                        |
| `Division`   | `"Atlantic"`, `"Central"`, `"Southeast"`, `"Northwest"`, `"Pacific"`, `"Southwest"` |
