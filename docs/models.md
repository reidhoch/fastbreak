# Response Models

Reference for fastbreak's Pydantic response model system: the two NBA API JSON shapes, `FrozenResponse`, result-set validators, DataFrame mixins, and custom validators. Includes a guide for writing and testing your own models.

---

## Overview

The NBA Stats API returns data in two distinct JSON shapes:

**Shape 1 — Tabular (v1)**: Used by the vast majority of endpoints. The response is a flat wrapper with a `resultSets` array. Each result set has a `headers` list and a `rowSet` list-of-lists. Every row is a positional array that must be zipped against the headers to produce dictionaries.

```json
{
  "resource": "leaguestandings",
  "parameters": {"LeagueID": "00", "SeasonYear": "2025-26"},
  "resultSets": [
    {
      "name": "Standings",
      "headers": ["TeamID", "TeamName", "WINS", "LOSSES"],
      "rowSet": [
        [1610612760, "Thunder", 36, 8],
        [1610612765, "Pistons", 31, 10]
      ]
    }
  ]
}
```

**Shape 2 — Nested JSON (v3)**: Used by newer endpoints (box score summaries, play-by-play v3, etc.). The response is a proper nested object with camelCase keys. No header/row transformation is required.

```json
{
  "meta": {"version": 1, "request": "...", "time": "..."},
  "boxScoreSummary": {
    "gameId": "0022500571",
    "gameStatus": 3,
    "homeTeam": {"teamId": 1610612738, "teamTricode": "BOS", "score": 112},
    "awayTeam": {"teamId": 1610612760, "teamTricode": "OKC", "score": 108}
  }
}
```

All response models—regardless of which shape they consume—inherit from `FrozenResponse` and are fully immutable once validated.

---

## FrozenResponse Base Class

**Location**: `fastbreak.models.common.response`

`FrozenResponse` is the base class for every top-level API response model in fastbreak.

```python
from fastbreak.models.common.response import FrozenResponse
```

### Configuration

```python
model_config = ConfigDict(frozen=True, extra="ignore")
```

- `frozen=True`: Instances are immutable after creation. Attempting to set any attribute raises `ValidationError`. This prevents accidental mutation of cached API responses.
- `extra="ignore"`: Fields present in the raw API data that are not declared in the model are silently discarded. This makes models forward-compatible—if the NBA API adds a new field tomorrow, existing code will not break.

### Unknown Field Warnings

Even though extra fields are ignored, `FrozenResponse` logs a `WARNING` when it receives any field not declared in the model. This allows you to detect API schema changes without crashing production code.

The `_warn_on_extra_fields` model validator runs before field validation. It compares the incoming dictionary keys against all declared field names and their aliases. The standard NBA wrapper fields (`resource`, `parameters`, `resultSet`, `resultSets`) are excluded from this check because they are consumed by transformation validators before reaching the model.

A warning looks like:

```
WARNING  unknown_fields_received  model=LeagueStandingsResponse  fields=['newApiField']
```

### `strict()` Classmethod

`strict()` returns a new subclass with `extra="forbid"` instead of `extra="ignore"`. Use it in tests to detect API schema drift:

```python
def test_standings_schema_unchanged():
    StrictResponse = LeagueStandingsResponse.strict()
    # If the API adds a new field, this will raise ValidationError
    StrictResponse.model_validate(api_data)
```

The strict class is named `Strict<OriginalName>` (e.g., `StrictLeagueStandingsResponse`) and inherits all fields and validators from the original.

```python
StrictExample = ExampleResponse.strict()
assert StrictExample.__name__ == "StrictExampleResponse"
assert issubclass(StrictExample, ExampleResponse)
assert StrictExample.model_config["extra"] == "forbid"
```

---

## The Two JSON Shapes

### Shape Detection: `is_tabular_response()`

**Location**: `fastbreak.models.common.result_set`

```python
from fastbreak.models.common.result_set import is_tabular_response
```

`is_tabular_response(data)` is a `TypeGuard` that returns `True` if `data` is a dict containing a `"resultSets"` key. The three `resultSets`-based factories — `tabular_validator`, `named_tabular_validator`, and `named_result_sets_validator` — call this function at the top of their generated validators. The fourth factory, `singular_result_set_validator`, handles endpoints that return `"resultSet"` (singular) instead of `"resultSets"` and performs its own `"resultSet" in data` check directly without calling `is_tabular_response()`.

If the data is not tabular (i.e., it is v3 nested JSON, or it is already a pre-transformed dict from a nested validator), the validators return `data` unchanged. This pass-through behavior is what allows the same `model_validator(mode="before")` pattern to work both when the validator is called on raw API data and when it is called during nested model construction.

```python
# Shape 1 — tabular
is_tabular_response({"resultSets": [...]})   # True

# Shape 2 — nested v3
is_tabular_response({"meta": {...}, "boxScoreSummary": {...}})  # False

# Pre-transformed dict (already processed by validator)
is_tabular_response({"standings": [...]})  # False
```

### Shape 1: Parsing Tabular Data

The parsing path for tabular data:

1. Raw API response arrives as `{"resultSets": [{"name": "...", "headers": [...], "rowSet": [[...], ...]}, ...]}`
2. The `model_validator(mode="before")` on the response class calls `is_tabular_response()`, which returns `True`
3. The appropriate validator function calls `parse_result_set()` or `parse_result_set_by_name()`, which zips each `rowSet` row against the `headers` list to produce a list of dicts
4. The validator returns a new dict mapping model field names to their parsed row lists
5. Pydantic then validates that dict against the response model's declared fields

### Shape 2: Nested v3 Models

For v3 endpoints, no transformation is needed. The raw JSON structure maps directly to the nested Pydantic models. `is_tabular_response()` returns `False`, so any result set validators pass through unchanged. Pydantic's built-in nested model parsing handles everything using `Field(alias=...)` to map camelCase JSON keys to snake_case Python attributes.

---

## Result Set Validators

All four factory functions are importable from `fastbreak.models.common.result_set`:

```python
from fastbreak.models.common.result_set import (
    tabular_validator,
    named_tabular_validator,
    named_result_sets_validator,
    singular_result_set_validator,
)
```

Each returns a callable suitable for wrapping with `model_validator(mode="before")`. The assignment pattern used throughout the codebase is:

```python
from_result_sets = model_validator(mode="before")(tabular_validator("field_name"))
```

This is equivalent to decorating a method, but avoids the need to define a named method for what is purely boilerplate.

---

### `tabular_validator(field_name, index=0)`

Use when the response has a single list field populated from one result set, identified by its position in the `resultSets` array (default: index 0).

**Signature**:
```python
def tabular_validator(field_name: str, index: int = 0) -> ValidatorFunc
```

**Example** — `LeagueStandingsResponse`:

```python
from pydantic import BaseModel, Field, model_validator
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class TeamStanding(PandasMixin, PolarsMixin, BaseModel):
    team_id: int = Field(alias="TeamID")
    team_city: str = Field(alias="TeamCity")
    team_name: str = Field(alias="TeamName")
    wins: int = Field(alias="WINS")
    losses: int = Field(alias="LOSSES")
    win_pct: float = Field(alias="WinPCT")
    conference: str = Field(alias="Conference")
    playoff_rank: int = Field(alias="PlayoffRank")


class LeagueStandingsResponse(FrozenResponse):
    standings: list[TeamStanding]

    from_result_sets = model_validator(mode="before")(tabular_validator("standings"))
```

**Input** (using a minimal model to illustrate the transformation — the real `TeamStanding` has 90+ fields):
```python
from pydantic import BaseModel, model_validator
from fastbreak.models.common.frozen import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator

class TeamRecord(BaseModel):
    team_id: int
    team_name: str
    wins: int

class TeamRecordResponse(FrozenResponse):
    teams: list[TeamRecord]
    from_result_sets = model_validator(mode="before")(tabular_validator("teams"))

data = {
    "resultSets": [{
        "name": "Teams",
        "headers": ["TeamID", "TeamName", "WINS"],
        "rowSet": [
            [1610612760, "Thunder", 36],
            [1610612765, "Pistons", 31],
        ]
    }]
}

response = TeamRecordResponse.model_validate(data)
assert response.teams[0].team_name == "Thunder"
assert response.teams[0].wins == 36
```

To parse a result set at a specific index other than 0, pass `index=N`:

```python
# Parse the second result set (index 1)
from_result_sets = model_validator(mode="before")(tabular_validator("items", index=1))
```

---

### `named_tabular_validator(field_name, result_set_name)`

Use when the response has a single list field populated from one named result set. Looks up the result set by its `"name"` field rather than by position. Raises `ValueError` if the named result set is not present.

**Signature**:
```python
def named_tabular_validator(field_name: str, result_set_name: str) -> ValidatorFunc
```

**Example** — parsing a named shooting stats result set:

```python
from pydantic import BaseModel, Field, model_validator
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_tabular_validator


class TeamShotStats(BaseModel):
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    fga_frequency: float = Field(alias="FGA_FREQUENCY")
    fg_pct: float = Field(alias="FG_PCT")
    efg_pct: float = Field(alias="EFG_PCT")


class LeagueDashTeamShotsResponse(FrozenResponse):
    teams: list[TeamShotStats]

    from_result_sets = model_validator(mode="before")(
        named_tabular_validator("teams", "LeagueDashPTShots")
    )
```

**Input**:
```python
data = {
    "resultSets": [
        {
            "name": "SomethingElse",
            "headers": ["TEAM_ID"],
            "rowSet": []
        },
        {
            "name": "LeagueDashPTShots",
            "headers": ["TEAM_ID", "TEAM_ABBREVIATION", "FGA_FREQUENCY", "FG_PCT", "EFG_PCT"],
            "rowSet": [
                [1610612738, "BOS", 0.45, 0.512, 0.587],
            ]
        }
    ]
}

response = LeagueDashTeamShotsResponse.model_validate(data)
assert response.teams[0].team_abbreviation == "BOS"
```

---

### `named_result_sets_validator(mappings, *, ignore_missing=False)`

Use when the response has multiple fields populated from different named result sets. The `mappings` dict maps model field names to result set configuration.

**Signature**:
```python
def named_result_sets_validator(
    mappings: dict[str, tuple[str, bool] | str],
    *,
    ignore_missing: bool = False,
) -> ValidatorFunc
```

**`mappings` value formats**:

| Value format | Result |
|---|---|
| `"ResultSetName"` | `list[T]` — all rows from the named result set |
| `("ResultSetName", True)` | `T \| None` — first row of the result set, or `None` if empty |

**`ignore_missing=False`** (default): Raises `ValueError` if a named result set is absent from the response. Use this for result sets that are always expected.

**`ignore_missing=True`**: Returns an empty list or `None` for missing result sets instead of raising. Use this for result sets that are legitimately optional depending on query parameters.

**Example** — `PlayerCareerStatsResponse` with 14 result sets:

```python
from pydantic import BaseModel, Field, model_validator
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class SeasonTotals(BaseModel):
    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    gp: int = Field(alias="GP")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")


class CareerTotals(BaseModel):
    player_id: int = Field(alias="PLAYER_ID")
    gp: int = Field(alias="GP")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")


class StatHigh(BaseModel):
    player_id: int = Field(alias="PLAYER_ID")
    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    stat: str = Field(alias="STAT")
    stat_value: int = Field(alias="STAT_VALUE")


class PlayerCareerStatsResponse(FrozenResponse):
    season_totals_regular_season: list[SeasonTotals] = Field(default_factory=list)
    career_totals_regular_season: list[CareerTotals] = Field(default_factory=list)
    season_totals_post_season: list[SeasonTotals] = Field(default_factory=list)
    career_totals_post_season: list[CareerTotals] = Field(default_factory=list)
    season_totals_all_star: list[SeasonTotals] = Field(default_factory=list)
    career_totals_all_star: list[CareerTotals] = Field(default_factory=list)
    season_highs: list[StatHigh] = Field(default_factory=list)
    career_highs: list[StatHigh] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "season_totals_regular_season": "SeasonTotalsRegularSeason",
                "career_totals_regular_season": "CareerTotalsRegularSeason",
                "season_totals_post_season": "SeasonTotalsPostSeason",
                "career_totals_post_season": "CareerTotalsPostSeason",
                "season_totals_all_star": "SeasonTotalsAllStarSeason",
                "career_totals_all_star": "CareerTotalsAllStarSeason",
                "season_highs": "SeasonHighs",
                "career_highs": "CareerHighs",
            }
        )
    )
```

**Example** — single-row result set with `("ResultSetName", True)`:

```python
class GameByGameStat(BaseModel):
    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    pts: int = Field(alias="PTS")
    reb: int = Field(alias="REB")
    ast: int = Field(alias="AST")


class TotalPlayerStat(BaseModel):
    player_id: int = Field(alias="PLAYER_ID")
    gp: int = Field(alias="GP")
    pts: float = Field(alias="PTS")


class CumeStatsPlayerResponse(FrozenResponse):
    game_by_game_stats: list[GameByGameStat]
    total_player_stats: TotalPlayerStat | None = None

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "game_by_game_stats": "GameByGameStats",
                # True means: take only the first row, return T | None
                "total_player_stats": ("TotalPlayerStats", True),
            }
        )
    )
```

**Example** — `ignore_missing=True` for optional result sets:

```python
class PlayerDashboardResponse(FrozenResponse):
    overall: list[OverallStats] = Field(default_factory=list)
    by_location: list[LocationStats] = Field(default_factory=list)
    # This result set is only returned for certain season types
    pre_post_all_star: list[AllStarStats] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": "OverallPlayerDashboard",
                "by_location": "LocationPlayerDashboard",
                "pre_post_all_star": "PrePostAllStarPlayerDashboard",
            },
            ignore_missing=True,  # pre_post_all_star may not be present
        )
    )
```

---

### `singular_result_set_validator(mappings)` (Rare)

A small number of NBA API endpoints return `"resultSet"` (singular) instead of `"resultSets"` (plural). This validator handles that variant. The API is otherwise identical to `named_result_sets_validator` except all values must be plain strings (no single-row tuple syntax).

```python
from fastbreak.models.common.result_set import singular_result_set_validator

class LeadersTilesResponse(FrozenResponse):
    leaders: list[LeaderTile]
    all_time_high: list[AllTimeHigh]

    from_result_set = model_validator(mode="before")(
        singular_result_set_validator(
            {
                "leaders": "LeadersTiles",
                "all_time_high": "AllTimeSeasonHigh",
            }
        )
    )
```

---

## v3 Nested Models

v3 endpoints return structured JSON with camelCase keys. No result set transformation is needed—Pydantic's nested model parsing handles everything via `Field(alias=...)`.

### Structure Pattern

A v3 response model follows this structure:

```python
class MyV3Response(FrozenResponse):
    meta: Meta
    data: MyV3Data = Field(alias="myData")
```

The top-level response inherits `FrozenResponse`. All nested models use plain `BaseModel`. The `Meta` class (from `fastbreak.models.common.meta`) is common to all v3 responses and carries request diagnostics.

### `Meta` Model

```python
from fastbreak.models.common.meta import Meta

class Meta(PandasMixin, PolarsMixin, BaseModel):
    version: int | None = None
    request: str | None = None
    time: str | None = None
```

### Full Example: `BoxScoreSummaryV3Response`

This is the actual structure from `fastbreak.models.box_score_summary_v3`:

```python
from pydantic import BaseModel, Field
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class ArenaV3(BaseModel):
    arena_id: int = Field(alias="arenaId")
    arena_name: str = Field(alias="arenaName")
    arena_city: str = Field(alias="arenaCity")
    arena_state: str = Field(alias="arenaState")
    arena_country: str = Field(alias="arenaCountry")
    arena_timezone: str = Field(alias="arenaTimezone")
    arena_street_address: str = Field(alias="arenaStreetAddress")
    arena_postal_code: str = Field(alias="arenaPostalCode")


class OfficialV3(BaseModel):
    person_id: int = Field(alias="personId")
    name: str
    name_i: str = Field(alias="nameI")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    jersey_num: str = Field(alias="jerseyNum")
    assignment: str


class BroadcasterV3(BaseModel):
    broadcaster_id: int = Field(alias="broadcasterId")
    broadcast_display: str = Field(alias="broadcastDisplay")
    broadcaster_display: str = Field(alias="broadcasterDisplay")
    broadcaster_video_link: str = Field(alias="broadcasterVideoLink")
    broadcaster_description: str = Field(alias="broadcasterDescription")
    broadcaster_team_id: int = Field(alias="broadcasterTeamId")
    region_id: int = Field(alias="regionId")


class BroadcastersV3(BaseModel):
    international_broadcasters: list[BroadcasterV3] = Field(
        alias="internationalBroadcasters", default_factory=list
    )
    international_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="internationalRadioBroadcasters", default_factory=list
    )
    international_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="internationalOttBroadcasters", default_factory=list
    )
    national_broadcasters: list[BroadcasterV3] = Field(
        alias="nationalBroadcasters", default_factory=list
    )
    national_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="nationalRadioBroadcasters", default_factory=list
    )
    national_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="nationalOttBroadcasters", default_factory=list
    )
    home_tv_broadcasters: list[BroadcasterV3] = Field(
        alias="homeTvBroadcasters", default_factory=list
    )
    home_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="homeRadioBroadcasters", default_factory=list
    )
    home_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="homeOttBroadcasters", default_factory=list
    )
    away_tv_broadcasters: list[BroadcasterV3] = Field(
        alias="awayTvBroadcasters", default_factory=list
    )
    away_radio_broadcasters: list[BroadcasterV3] = Field(
        alias="awayRadioBroadcasters", default_factory=list
    )
    away_ott_broadcasters: list[BroadcasterV3] = Field(
        alias="awayOttBroadcasters", default_factory=list
    )


class SummaryTeamV3(BaseModel):
    team_id: int = Field(alias="teamId")
    team_city: str | None = Field(None, alias="teamCity")
    team_name: str | None = Field(None, alias="teamName")
    team_tricode: str | None = Field(None, alias="teamTricode")
    team_slug: str | None = Field(None, alias="teamSlug")
    team_wins: int = Field(alias="teamWins")
    team_losses: int = Field(alias="teamLosses")
    score: int
    seed: int | None = None
    inactive_players: list[dict[str, object]] = Field(
        alias="inactivePlayers", default_factory=list
    )


class BoxScoreSummaryV3Data(BaseModel):
    game_id: str = Field(alias="gameId")
    game_code: str = Field(alias="gameCode")
    game_status: int = Field(alias="gameStatus")
    game_status_text: str = Field(alias="gameStatusText")
    period: int
    game_clock: str = Field(alias="gameClock")
    game_time_utc: str = Field(alias="gameTimeUTC")
    game_et: str = Field(alias="gameEt")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    duration: str
    attendance: int
    sellout: int
    series_game_number: str = Field(alias="seriesGameNumber")
    game_label: str = Field(alias="gameLabel")
    game_sub_label: str = Field(alias="gameSubLabel")
    series_text: str = Field(alias="seriesText")
    if_necessary: bool = Field(alias="ifNecessary")
    is_neutral: bool = Field(alias="isNeutral")
    arena: ArenaV3
    officials: list[OfficialV3]
    broadcasters: BroadcastersV3
    home_team: SummaryTeamV3 = Field(alias="homeTeam")
    away_team: SummaryTeamV3 = Field(alias="awayTeam")


class BoxScoreSummaryV3Response(FrozenResponse):
    meta: Meta
    box_score_summary: BoxScoreSummaryV3Data = Field(alias="boxScoreSummary")
```

**Input**:
```python
data = {
    "meta": {"version": 1, "request": "https://...", "time": "2025-01-15T20:00:00Z"},
    "boxScoreSummary": {
        "gameId": "0022500571",
        "gameCode": "20250115/OKCBOS",
        "gameStatus": 3,
        "gameStatusText": "Final",
        "period": 4,
        "gameClock": "PT00M00.00S",
        "gameTimeUTC": "2025-01-15T00:00:00Z",
        "gameEt": "2025-01-14T19:30:00-05:00",
        "awayTeamId": 1610612760,
        "homeTeamId": 1610612738,
        "duration": "2:14",
        "attendance": 19156,
        "sellout": 1,
        "seriesGameNumber": "",
        "gameLabel": "",
        "gameSubLabel": "",
        "seriesText": "",
        "ifNecessary": False,
        "isNeutral": False,
        "arena": {
            "arenaId": 15,
            "arenaName": "TD Garden",
            "arenaCity": "Boston",
            "arenaState": "MA",
            "arenaCountry": "US",
            "arenaTimezone": "America/New_York",
            "arenaStreetAddress": "100 Legends Way",
            "arenaPostalCode": "02114"
        },
        "officials": [
            {
                "personId": 202051,
                "name": "Tony Brothers",
                "nameI": "T. Brothers",
                "firstName": "Tony",
                "familyName": "Brothers",
                "jerseyNum": "25",
                "assignment": "Crew Chief"
            }
        ],
        "broadcasters": {},
        "homeTeam": {
            "teamId": 1610612738,
            "teamCity": "Boston",
            "teamName": "Celtics",
            "teamTricode": "BOS",
            "teamWins": 32,
            "teamLosses": 12,
            "score": 112,
            "seed": None
        },
        "awayTeam": {
            "teamId": 1610612760,
            "teamCity": "Oklahoma City",
            "teamName": "Thunder",
            "teamTricode": "OKC",
            "teamWins": 36,
            "teamLosses": 8,
            "score": 108,
            "seed": None
        }
    }
}

response = BoxScoreSummaryV3Response.model_validate(data)
assert response.box_score_summary.game_id == "0022500571"
assert response.box_score_summary.home_team.team_tricode == "BOS"
assert response.box_score_summary.arena.arena_name == "TD Garden"
assert response.meta.version == 1
```

---

## Field Aliases

### v1 Tabular: SCREAMING_SNAKE_CASE

v1 endpoints return column names in `SCREAMING_SNAKE_CASE` (e.g., `TEAM_ID`, `WIN_PCT`, `PLAYER_AGE`). Some fields use mixed case (e.g., `TeamID`, `WinPCT`, `PlayoffRank`). Map each to a snake_case Python attribute with `Field(alias="...")`:

```python
class SeasonTotals(BaseModel):
    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    gp: int = Field(alias="GP")
    fg_pct: float = Field(alias="FG_PCT")
    pts: float = Field(alias="PTS")
```

### v3 Nested: camelCase

v3 endpoints return keys in `camelCase`. Map each to a snake_case Python attribute:

```python
class BoxScoreSummaryV3Data(BaseModel):
    game_id: str = Field(alias="gameId")
    game_status: int = Field(alias="gameStatus")
    game_time_utc: str = Field(alias="gameTimeUTC")
    if_necessary: bool = Field(alias="ifNecessary")
    is_neutral: bool = Field(alias="isNeutral")
```

Fields whose camelCase and snake_case representations are identical (e.g., `period`, `attendance`, `name`) do not need an alias.

---

## DataFrame Mixins

**Location**: `fastbreak.models.common.dataframe`

`PandasMixin` and `PolarsMixin` add class-level `to_pandas()` and `to_polars()` methods to any Pydantic model. They are available on most response row models (`TeamStanding`, `SeasonTotals`, `PlayerGameLogEntry`, etc.) but not on the top-level response models themselves.

### Mixin Order

When using both mixins, always list them before `BaseModel`:

```python
from pydantic import BaseModel
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin

class MyRow(PandasMixin, PolarsMixin, BaseModel):
    player_id: int
    pts: float
    reb: float
    ast: float
```

### `PandasMixin.to_pandas(models, *, flatten=True, sep=".")`

Converts a list of model instances to a `pandas.DataFrame`. Requires `pandas` to be installed.

```python
import pandas as pd
from fastbreak.models.player_career_stats import SeasonTotals

rows: list[SeasonTotals] = response.season_totals_regular_season
df: pd.DataFrame = SeasonTotals.to_pandas(rows)

# With nested models, flatten=True (default) produces dot-separated columns:
# e.g., "statistics.points", "statistics.rebounds"
df_flat = MyRow.to_pandas(rows, flatten=True, sep=".")

# flatten=False keeps nested models as dict columns
df_raw = MyRow.to_pandas(rows, flatten=False)
```

- If `models` is an empty list, returns an empty `pd.DataFrame()`.
- Raises `ImportError` if pandas is not installed.

### `PolarsMixin.to_polars(models, *, flatten=True, sep=".")`

Converts a list of model instances to a `polars.DataFrame`. Requires `polars` to be installed.

```python
import polars as pl
from fastbreak.models.player_career_stats import SeasonTotals

rows: list[SeasonTotals] = response.season_totals_regular_season
df: pl.DataFrame = SeasonTotals.to_polars(rows)
```

- `flatten=True` (default): Struct columns are recursively unnested into dot-separated columns.
- `flatten=False`: Nested models remain as Polars struct columns.
- If `models` is an empty list, returns an empty `pl.DataFrame()`.
- Raises `ImportError` if polars is not installed.

### Practical Example

```python
from fastbreak.games import get_box_scores
from fastbreak.models.box_score_traditional import TraditionalPlayer

async with NBAClient() as client:
    boxes = await get_box_scores(client, ["0022500571"])

box = boxes["0022500571"]  # BoxScoreTraditionalData
home_players = box.homeTeam.players  # camelCase
df = TraditionalPlayer.to_pandas(home_players)
# columns: personId, firstName, familyName, nameI, position, jerseyNum, ...
```

---

## Custom Validators for Dirty API Data

The NBA Stats API occasionally returns invalid or inconsistent values for certain fields. Use Pydantic validators to coerce these before model validation.

### `@field_validator` — Field-Level Coercion

Use `mode="before"` to intercept the raw value before Pydantic's type coercion. This is the correct place to handle strings that should be `None` or integers.

**Example** — coercing `"NR"` (Not Ranked) strings to `None`:

The `SeasonRankings` model in `playercareerstats` receives `"NR"` for `player_age`, `gp`, and `gs` in seasons where those stats are not ranked:

```python
from pydantic import BaseModel, Field, field_validator


class SeasonRankings(BaseModel):
    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    player_age: float | None = Field(alias="PLAYER_AGE")
    gp: int | None = Field(alias="GP")
    gs: int | None = Field(alias="GS")
    rank_pts: int | None = Field(alias="RANK_PG_PTS")
    rank_reb: int | None = Field(alias="RANK_PG_REB")
    rank_ast: int | None = Field(alias="RANK_PG_AST")

    @field_validator("player_age", "gp", "gs", mode="before")
    @classmethod
    def coerce_nr_to_none(cls, v: str | int | None) -> int | None:
        """Coerce 'NR' (Not Ranked) strings to None."""
        if v == "NR":
            return None
        return v  # type: ignore[return-value]
```

```python
# API may return "NR" for unranked stats
data = {"PLAYER_ID": 2544, "SEASON_ID": "2003-04", ..., "PLAYER_AGE": "NR", "GP": 79}
rankings = SeasonRankings.model_validate(data)
assert rankings.player_age is None
assert rankings.gp == 79
```

### `@model_validator(mode="before")` — Shape Normalization

Use a model-level `mode="before"` validator for cases where the incoming shape needs to be restructured before any field validation occurs. This is how all the result set parsing works. You can also use it to handle other shape variations:

```python
from pydantic import BaseModel, model_validator
from typing import Any


class FlexibleResponse(FrozenResponse):
    items: list[Item]

    @model_validator(mode="before")
    @classmethod
    def normalize_shape(cls, data: Any) -> dict[str, Any]:
        # Handle both {"items": [...]} and {"data": {"items": [...]}} shapes
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
```

---

## Writing a Custom Model

This section demonstrates writing a complete response model from scratch, including all the patterns described above.

**Scenario**: A new endpoint `playerseasonstats` returns two result sets—per-game stats for each season, and a single-row career average summary.

### Step 1: Define the Row Models

```python
# src/fastbreak/models/player_season_stats.py

from pydantic import BaseModel, Field, field_validator, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class SeasonPerGameStats(PandasMixin, PolarsMixin, BaseModel):
    """Per-game stats for one season."""

    player_id: int = Field(alias="PLAYER_ID")
    season_id: str = Field(alias="SEASON_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    age: float | None = Field(alias="PLAYER_AGE")
    gp: int = Field(alias="GP")
    min: float = Field(alias="MIN")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    fg_pct: float = Field(alias="FG_PCT")
    fg3_pct: float = Field(alias="FG3_PCT")
    ft_pct: float = Field(alias="FT_PCT")

    @field_validator("age", mode="before")
    @classmethod
    def coerce_nr_to_none(cls, v: object) -> object:
        """Coerce 'NR' string to None for unranked/unavailable ages."""
        if v == "NR":
            return None
        return v


class CareerAverages(BaseModel):
    """Single-row career averages summary."""

    player_id: int = Field(alias="PLAYER_ID")
    gp: int = Field(alias="GP")
    min: float = Field(alias="MIN")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    fg_pct: float = Field(alias="FG_PCT")
```

### Step 2: Define the Response Model

```python
class PlayerSeasonStatsResponse(FrozenResponse):
    """Response from the playerseasonstats endpoint."""

    seasons: list[SeasonPerGameStats] = Field(default_factory=list)
    career_averages: CareerAverages | None = None

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "seasons": "PlayerSeasonStats",
                # True = single row (T | None), not a list
                "career_averages": ("CareerAverages", True),
            }
        )
    )
```

### Step 3: Use It

```python
data = {
    "resultSets": [
        {
            "name": "PlayerSeasonStats",
            "headers": [
                "PLAYER_ID", "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION",
                "PLAYER_AGE", "GP", "MIN", "PTS", "REB", "AST",
                "STL", "BLK", "TOV", "FG_PCT", "FG3_PCT", "FT_PCT"
            ],
            "rowSet": [
                [2544, "2003-04", 1610612739, "CLE", 19.0, 79, 39.5, 20.9, 5.5, 7.2, 1.6, 0.7, 3.5, 0.417, 0.290, 0.754],
                [2544, "2004-05", 1610612739, "CLE", 20.0, 80, 42.4, 27.2, 7.4, 7.2, 2.2, 0.7, 3.3, 0.472, 0.351, 0.750],
            ]
        },
        {
            "name": "CareerAverages",
            "headers": ["PLAYER_ID", "GP", "MIN", "PTS", "REB", "AST", "FG_PCT"],
            "rowSet": [
                [2544, 1492, 38.1, 27.1, 7.5, 7.4, 0.504],
            ]
        }
    ]
}

response = PlayerSeasonStatsResponse.model_validate(data)

assert len(response.seasons) == 2
assert response.seasons[0].team_abbreviation == "CLE"
assert response.seasons[0].pts == 20.9

assert response.career_averages is not None
assert response.career_averages.pts == 27.1

# DataFrame conversion
df = SeasonPerGameStats.to_pandas(response.seasons)
print(df[["season_id", "pts", "reb", "ast"]])
```

---

## Testing Models

### Test Strategy

fastbreak model tests follow a consistent pattern:

1. **Unit test the row model** with a single dict matching one row of API data
2. **Integration test the response model** with a full `resultSets` structure, including `resource` and `parameters` wrapper fields
3. **Use `strict()`** to verify no unknown fields sneak past in production fixture data

### Testing with `strict()`

`strict()` is the primary guard against API schema drift. In tests, use it to validate against real API responses or carefully constructed fixtures:

```python
import pytest
from pydantic import ValidationError
from fastbreak.models.player_season_stats import PlayerSeasonStatsResponse


def test_schema_unchanged():
    """Strict mode catches any new fields from the API."""
    data = {
        "resultSets": [
            {
                "name": "PlayerSeasonStats",
                "headers": [
                    "PLAYER_ID", "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION",
                    "PLAYER_AGE", "GP", "MIN", "PTS", "REB", "AST",
                    "STL", "BLK", "TOV", "FG_PCT", "FG3_PCT", "FT_PCT"
                ],
                "rowSet": [
                    [2544, "2024-25", 1610612739, "CLE", 40.0, 70, 35.1, 24.3, 7.1, 8.5,
                     1.3, 0.6, 3.2, 0.521, 0.401, 0.748],
                ]
            },
            {
                "name": "CareerAverages",
                "headers": ["PLAYER_ID", "GP", "MIN", "PTS", "REB", "AST", "FG_PCT"],
                "rowSet": [[2544, 1492, 38.1, 27.1, 7.5, 7.4, 0.504]]
            }
        ]
    }
    StrictResponse = PlayerSeasonStatsResponse.strict()
    response = StrictResponse.model_validate(data)
    assert response.seasons[0].pts == 24.3


def test_strict_rejects_unknown_fields():
    """strict() raises ValidationError when the API adds new fields."""
    StrictResponse = PlayerSeasonStatsResponse.strict()
    with pytest.raises(ValidationError) as exc_info:
        StrictResponse.model_validate({"new_top_level_field": "unexpected", "resultSets": []})

    errors = exc_info.value.errors()
    assert any(e["type"] == "extra_forbidden" for e in errors)
```

### Testing That Unknown Fields Log Warnings But Don't Fail

In normal (non-strict) mode, unknown fields are ignored but logged as warnings. Test that the warning fires without the model failing:

```python
from fastbreak.models.common.response import FrozenResponse
from pydantic import BaseModel


class MyResponse(FrozenResponse):
    name: str
    value: int


def test_unknown_fields_are_ignored_but_warned(capsys):
    """Extra fields are silently ignored; a warning is logged."""
    response = MyResponse(name="test", value=42, new_api_field="detected")

    # Model parses successfully
    assert response.name == "test"
    assert response.value == 42
    assert not hasattr(response, "new_api_field")

    # Warning was logged
    captured = capsys.readouterr()
    assert "unknown_fields_received" in captured.out
    assert "MyResponse" in captured.out
    assert "new_api_field" in captured.out
```

### Fixture JSON for Tests

Structure test fixtures to match the full raw API response shape. The `resource` and `parameters` keys are accepted by the model (they are in `_API_WRAPPER_FIELDS`) and will not trigger unknown-field warnings:

```python
FIXTURE_PLAYER_SEASON_STATS = {
    "resource": "playerseasonstats",
    "parameters": {
        "PlayerID": 2544,
        "Season": "2024-25",
        "SeasonType": "Regular Season",
        "PerMode": "PerGame",
    },
    "resultSets": [
        {
            "name": "PlayerSeasonStats",
            "headers": [
                "PLAYER_ID", "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION",
                "PLAYER_AGE", "GP", "MIN", "PTS", "REB", "AST",
                "STL", "BLK", "TOV", "FG_PCT", "FG3_PCT", "FT_PCT"
            ],
            "rowSet": [
                [2544, "2024-25", 1610612739, "CLE", 40.0, 70, 35.1,
                 24.3, 7.1, 8.5, 1.3, 0.6, 3.2, 0.521, 0.401, 0.748],
            ]
        },
        {
            "name": "CareerAverages",
            "headers": ["PLAYER_ID", "GP", "MIN", "PTS", "REB", "AST", "FG_PCT"],
            "rowSet": [[2544, 1492, 38.1, 27.1, 7.5, 7.4, 0.504]]
        }
    ]
}


def test_response_parses_full_fixture():
    response = PlayerSeasonStatsResponse.model_validate(FIXTURE_PLAYER_SEASON_STATS)
    assert len(response.seasons) == 1
    assert response.seasons[0].pts == 24.3
    assert response.career_averages is not None
    assert response.career_averages.gp == 1492
```

### Testing Immutability

```python
import pytest
from pydantic import ValidationError


def test_response_is_immutable():
    """FrozenResponse instances cannot be mutated after creation."""
    response = PlayerSeasonStatsResponse.model_validate(FIXTURE_PLAYER_SEASON_STATS)
    with pytest.raises(ValidationError):
        response.seasons = []  # type: ignore[misc]
```

### Testing the NR Coercion Validator

```python
def test_coerce_nr_age_to_none():
    """SeasonPerGameStats coerces 'NR' player age to None."""
    row = {
        "PLAYER_ID": 12345,
        "SEASON_ID": "2003-04",
        "TEAM_ID": 1610612739,
        "TEAM_ABBREVIATION": "CLE",
        "PLAYER_AGE": "NR",  # Not ranked
        "GP": 35,
        "MIN": 22.4,
        "PTS": 8.1,
        "REB": 3.2,
        "AST": 2.1,
        "STL": 0.8,
        "BLK": 0.3,
        "TOV": 1.5,
        "FG_PCT": 0.431,
        "FG3_PCT": 0.312,
        "FT_PCT": 0.712,
    }
    stats = SeasonPerGameStats.model_validate(row)
    assert stats.age is None


def test_normal_age_passes_through():
    """SeasonPerGameStats passes through a normal age value."""
    row = {**base_row, "PLAYER_AGE": 25}
    stats = SeasonPerGameStats.model_validate(row)
    assert stats.age == 25.0
```
