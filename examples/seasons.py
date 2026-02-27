"""Example: Season utility functions from fastbreak.seasons."""

from datetime import date

from fastbreak.seasons import (
    get_season_from_date,
    season_start_year,
    season_to_season_id,
)

# ── get_season_from_date ─────────────────────────────────────────────
# Returns the NBA season string for a given calendar date.
# Season starts in October: Oct-Dec belong to the season starting that year;
# Jan-Sep belong to the season that started the prior year.

print("=" * 60)
print("get_season_from_date — season for a given calendar date")
print("=" * 60)

sample_dates = [
    date(2024, 10, 22),  # Opening Night 2024-25
    date(2025, 2, 27),  # Mid-season
    date(2025, 6, 15),  # Finals
    date(2025, 10, 1),  # Pre-season 2025-26
]

for d in sample_dates:
    season = get_season_from_date(d)
    print(f"  {d}  →  {season}")

current = get_season_from_date()
print(f"\n  Current season (today): {current}")
print()

# ── season_start_year ────────────────────────────────────────────────
# Extracts the four-digit start year from a season string.

print("=" * 60)
print("season_start_year — extract start year from season string")
print("=" * 60)

for season in ["2022-23", "2023-24", "2024-25", "2025-26"]:
    year = season_start_year(season)
    print(f"  {season}  →  {year}")
print()

# ── season_to_season_id ──────────────────────────────────────────────
# Converts a season string to the numeric season ID used by some
# NBA Stats API endpoints (e.g. "2024-25" → "22024").

print("=" * 60)
print("season_to_season_id — convert to API season ID")
print("=" * 60)

for season in ["2022-23", "2023-24", "2024-25", "2025-26"]:
    sid = season_to_season_id(season)
    print(f"  {season}  →  {sid}")
print()
