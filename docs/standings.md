# fastbreak.standings

Helpers for league and conference standings. `get_standings` and
`get_conference_standings` are async and require an `NBAClient` instance.
`magic_number` is a sync utility that requires no client.

```python
from fastbreak.standings import get_standings, get_conference_standings, magic_number
```

---

## Function reference

### `magic_number`

```python
def magic_number(my_wins: int, opp_wins: int, opp_games_remaining: int) -> int
```

Clinching magic number for the leading team over a specific opponent.

Returns the combined count of (leading team wins + opponent losses) needed for the leading team to guarantee finishing ahead. Returns 0 when already clinched.

```python
# Opponent's games remaining from a TeamStanding:
opp_remaining = 82 - opp.wins - opp.losses

m = magic_number(
    my_wins=leader.wins,
    opp_wins=opp.wins,
    opp_games_remaining=opp_remaining,
)
print(f"Magic number: {m}")  # 0 = already clinched
```

---

### `get_standings`

```python
async def get_standings(
    client: NBAClient,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
) -> list[TeamStanding]
```

Returns standings for all 30 teams in the order returned by the NBA Stats API
(typically sorted by conference rank within each conference, not overall league rank).

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `client` | `NBAClient` | required | Active NBA client |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |

**Returns:** `list[TeamStanding]` — one entry per team.

```python
standings = await get_standings(client)
for s in standings:
    print(f"{s.team_name:<25} {s.wins}-{s.losses}  {s.win_pct:.3f}")
```

---

### `get_conference_standings`

```python
async def get_conference_standings(
    client: NBAClient,
    conference: str,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
) -> list[TeamStanding]
```

Returns standings for one conference, sorted ascending by `playoff_rank` (1 = best seed).
Filters the full league standings returned by `get_standings()` to the requested conference.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `client` | `NBAClient` | required | Active NBA client |
| `conference` | `str` | required | `"East"` or `"West"` |
| `season` | `Season \| None` | current season | Season in `YYYY-YY` format |
| `season_type` | `SeasonType` | `"Regular Season"` | `"Regular Season"`, `"Playoffs"`, or `"Pre Season"` |

**Returns:** `list[TeamStanding]` — up to 15 entries, sorted by `playoff_rank`.

```python
east = await get_conference_standings(client, "East")
print(f"1-seed: {east[0].team_name}  ({east[0].wins}-{east[0].losses})")
```

---

## `TeamStanding` fields

`TeamStanding` is returned by both helpers. Selected fields:

| Field | Type | Description |
|---|---|---|
| `team_id` | `int` | NBA team ID |
| `team_city` | `str` | City name, e.g. `"Indiana"` |
| `team_name` | `str` | Franchise name, e.g. `"Pacers"` |
| `team_slug` | `str` | URL-friendly team name, e.g. `"pacers"` |
| `conference` | `str` | `"East"` or `"West"` |
| `division` | `str` | Division name, e.g. `"Central"` |
| `wins` | `int` | Season wins |
| `losses` | `int` | Season losses |
| `win_pct` | `float` | Win percentage (0.0–1.0) |
| `record` | `str` | Win-loss string, e.g. `"41-28"` |
| `conference_record` | `str` | Conference record, e.g. `"28-14"` |
| `division_record` | `str` | Division record |
| `home` | `str` | Home record, e.g. `"22-10"` |
| `road` | `str` | Road record |
| `l10` | `str` | Last 10 games record |
| `playoff_rank` | `int` | Playoff seeding position within conference |
| `division_rank` | `int` | Rank within division |
| `league_rank` | `int \| None` | Overall league rank |
| `conference_games_back` | `float` | Games behind the conference leader |
| `division_games_back` | `float` | Games behind the division leader |
| `league_games_back` | `float` | Games behind the league leader |
| `clinch_indicator` | `str` | Clinch status indicator (e.g. `"x"`, `"y"`, `"z"`, `""`) |
| `clinched_post_season` | `int` | `1` if clinched a playoff spot |
| `clinched_play_in` | `int` | `1` if clinched play-in eligibility |
| `str_current_streak` | `str` | Current streak string, e.g. `"W5"` or `"L2"` |
| `long_win_streak` | `int` | Longest winning streak of the season |
| `long_loss_streak` | `int` | Longest losing streak of the season |
| `points_pg` | `float` | Team points scored per game |
| `opp_points_pg` | `float` | Opponent points allowed per game |
| `diff_points_pg` | `float` | Point differential per game |

`TeamStanding` also implements `to_pandas()` and `to_polars()` via DataFrame mixins.

---

## Complete example

```python
import asyncio
from fastbreak.clients import NBAClient
from fastbreak.standings import get_conference_standings, get_standings


async def main() -> None:
    async with NBAClient() as client:
        # All 30 teams
        standings = await get_standings(client)
        print(f"{'#':>3}  {'Team':<24} {'W':>3} {'L':>3}  {'W%':>6}  Streak")
        print("  " + "-" * 46)
        for s in standings:
            print(
                f"  {s.playoff_rank:>3}  {s.team_name:<24}"
                f" {s.wins:>3} {s.losses:>3}"
                f"  {s.win_pct:>6.3f}"
                f"  {s.str_current_streak}"
            )

        # Eastern Conference only
        print("\nEastern Conference:")
        east = await get_conference_standings(client, "East")
        for s in east:
            print(f"  {s.playoff_rank:>2}. {s.team_city} {s.team_name:<18}  {s.wins}-{s.losses}")


if __name__ == "__main__":
    asyncio.run(main())
```

See also: [`examples/standings.py`](../examples/standings.py),
[`examples/three_two_one.py`](../examples/three_two_one.py)
