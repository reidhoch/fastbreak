"""Tests for type aliases and validators in fastbreak.types.

Uses hypothesis for property-based testing to ensure validators handle
arbitrary invalid inputs correctly.
"""

import re
import string

import pytest
from hypothesis import given, settings, strategies as st
from pydantic import BaseModel, ValidationError

from fastbreak.types import (
    Conference,
    ContextMeasure,
    Date,
    DistanceRange,
    Division,
    GameSegment,
    ISODate,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    Period,
    PerMode,
    PlayerExperience,
    PlayerOrTeam,
    PlayerOrTeamAbbreviation,
    PlayerPosition,
    PlayType,
    PtMeasureType,
    Scope,
    Season,
    SeasonSegment,
    SeasonType,
    Section,
    ShotClockRange,
    StarterBench,
    StatCategoryAbbreviation,
    YesNo,
    _validate_date,
    _validate_season,
    validate_iso_date,
)

# =============================================================================
# Helper Models for Testing Annotated Types
# =============================================================================


class SeasonModel(BaseModel):
    """Test model for Season type."""

    season: Season


class DateModel(BaseModel):
    """Test model for Date type."""

    date: Date


class ISODateModel(BaseModel):
    """Test model for ISODate type."""

    date: ISODate


class LeagueIDModel(BaseModel):
    """Test model for LeagueID type."""

    league_id: LeagueID


class SeasonTypeModel(BaseModel):
    """Test model for SeasonType type."""

    season_type: SeasonType


class PerModeModel(BaseModel):
    """Test model for PerMode type."""

    per_mode: PerMode


class ConferenceModel(BaseModel):
    """Test model for Conference type."""

    conference: Conference


class DivisionModel(BaseModel):
    """Test model for Division type."""

    division: Division


class OutcomeModel(BaseModel):
    """Test model for Outcome type."""

    outcome: Outcome


class LocationModel(BaseModel):
    """Test model for Location type."""

    location: Location


class PeriodModel(BaseModel):
    """Test model for Period type."""

    period: Period


class YesNoModel(BaseModel):
    """Test model for YesNo type."""

    value: YesNo


# =============================================================================
# Season Validation Tests
# =============================================================================


class TestSeasonValidation:
    """Tests for Season type validation."""

    def test_valid_season_format_current(self):
        """Valid current season format is accepted."""
        model = SeasonModel(season="2024-25")
        assert model.season == "2024-25"

    def test_valid_season_format_historical(self):
        """Historical season formats are accepted."""
        model = SeasonModel(season="1999-00")
        assert model.season == "1999-00"

    def test_valid_season_format_future(self):
        """Future season formats are accepted."""
        model = SeasonModel(season="2030-31")
        assert model.season == "2030-31"

    def test_invalid_season_four_digit_year_only(self):
        """Season with only four digit year raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="2024")

    def test_invalid_season_full_years(self):
        """Season with two full years raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="2024-2025")

    def test_invalid_season_wrong_separator_slash(self):
        """Season with slash separator raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="2024/25")

    def test_invalid_season_wrong_separator_underscore(self):
        """Season with underscore separator raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="2024_25")

    def test_invalid_season_no_separator(self):
        """Season without separator raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="202425")

    def test_invalid_season_empty_string(self):
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="")

    def test_invalid_season_letters(self):
        """Season with letters raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="YYYY-YY")

    def test_invalid_season_extra_characters(self):
        """Season with extra characters raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="2024-25-26")

    def test_invalid_season_leading_space(self):
        """Season with leading space raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season=" 2024-25")

    def test_invalid_season_trailing_space(self):
        """Season with trailing space raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-YY format"):
            SeasonModel(season="2024-25 ")

    @given(
        year=st.integers(min_value=1000, max_value=9998),
    )
    def test_valid_season_formats_fuzzed(self, year):
        """Valid seasons have correct year continuity (YYYY-YY where YY = (YYYY+1) % 100)."""
        suffix = (year + 1) % 100
        season = f"{year:04d}-{suffix:02d}"
        model = SeasonModel(season=season)
        assert model.season == season

    @given(data=st.text(max_size=20))
    @settings(max_examples=200)
    def test_invalid_season_random_strings(self, data):
        """Random strings that don't match YYYY-YY should fail."""
        if re.match(r"^\d{4}-\d{2}$", data):
            return  # Skip valid patterns

        with pytest.raises(ValidationError):
            SeasonModel(season=data)


class TestSeasonValidatorFunction:
    """Direct tests for _validate_season function."""

    def test_returns_valid_season_unchanged(self):
        """Valid season is returned unchanged."""
        assert _validate_season("2024-25") == "2024-25"

    def test_raises_value_error_for_invalid(self):
        """Invalid season raises ValueError."""
        with pytest.raises(ValueError, match="YYYY-YY format"):
            _validate_season("invalid")

    def test_raises_value_error_for_wrong_suffix(self):
        """Season with correct format but mismatched year suffix raises ValueError."""
        with pytest.raises(ValueError, match="suffix should be"):
            _validate_season("2024-26")

    @given(data=st.text(max_size=50))
    @settings(max_examples=300)
    def test_never_crashes_on_any_string(self, data):
        """Function should never crash - either return value or raise ValueError."""
        try:
            result = _validate_season(data)
            assert result == data
            assert re.match(r"^\d{4}-\d{2}$", result)
        except ValueError as e:
            assert "YYYY-YY format" in str(e)


# =============================================================================
# Date Validation Tests
# =============================================================================


class TestDateValidation:
    """Tests for Date type validation."""

    def test_valid_date_format(self):
        """Valid MM/DD/YYYY format is accepted."""
        model = DateModel(date="01/15/2025")
        assert model.date == "01/15/2025"

    def test_valid_date_end_of_year(self):
        """End of year date is accepted."""
        model = DateModel(date="12/31/2024")
        assert model.date == "12/31/2024"

    def test_valid_date_beginning_of_year(self):
        """Beginning of year date is accepted."""
        model = DateModel(date="01/01/2024")
        assert model.date == "01/01/2024"

    def test_invalid_date_iso_format(self):
        """ISO format (YYYY-MM-DD) raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="2025-01-15")

    def test_invalid_date_european_format(self):
        """European format (DD/MM/YYYY) with invalid month is rejected."""
        # 15/01/2025 has month=15 which is invalid
        with pytest.raises(ValidationError) as exc_info:
            DateModel(date="15/01/2025")
        assert "Date must be a valid date" in str(
            exc_info.value
        )  # Format valid, semantic validation is external

    def test_invalid_date_wrong_separator_dash(self):
        """Date with dash separator raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="01-15-2025")

    def test_invalid_date_wrong_separator_dot(self):
        """Date with dot separator raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="01.15.2025")

    def test_invalid_date_two_digit_year(self):
        """Date with two digit year raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="01/15/25")

    def test_invalid_date_single_digit_month(self):
        """Date with single digit month raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="1/15/2025")

    def test_invalid_date_empty_string(self):
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="")

    def test_invalid_date_letters(self):
        """Date with letters raises ValidationError."""
        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            DateModel(date="Jan/15/2025")

    @given(
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),
        year=st.integers(min_value=1900, max_value=2100),
    )
    def test_valid_date_formats_fuzzed(self, month, day, year):
        """Valid dates in MM/DD/YYYY format should be accepted."""
        date = f"{month:02d}/{day:02d}/{year:04d}"
        model = DateModel(date=date)
        assert model.date == date

    @given(data=st.text(max_size=20))
    @settings(max_examples=200)
    def test_invalid_date_random_strings(self, data):
        """Random strings that don't match MM/DD/YYYY should fail."""
        if re.match(r"^\d{2}/\d{2}/\d{4}$", data):
            return  # Skip valid patterns

        with pytest.raises(ValidationError):
            DateModel(date=data)


class TestDateValidatorFunction:
    """Direct tests for _validate_date function."""

    def test_returns_valid_date_unchanged(self):
        """Valid date is returned unchanged."""
        assert _validate_date("01/15/2025") == "01/15/2025"

    def test_raises_value_error_for_invalid(self):
        """Invalid date raises ValueError."""
        with pytest.raises(ValueError, match="MM/DD/YYYY format"):
            _validate_date("invalid")

    @given(data=st.text(max_size=50))
    @settings(max_examples=300)
    def test_never_crashes_on_any_string(self, data):
        """Function should never crash - either return value or raise ValueError."""
        try:
            result = _validate_date(data)
            assert result == data
            assert re.match(r"^\d{2}/\d{2}/\d{4}$", result)
        except ValueError as e:
            assert "MM/DD/YYYY format" in str(e)


# =============================================================================
# ISODate Validation Tests
# =============================================================================


class TestISODateValidation:
    """Tests for ISODate type validation."""

    def test_valid_iso_date_format(self):
        """Valid YYYY-MM-DD format is accepted."""
        model = ISODateModel(date="2025-01-15")
        assert model.date == "2025-01-15"

    def test_valid_iso_date_end_of_year(self):
        """End of year ISO date is accepted."""
        model = ISODateModel(date="2024-12-31")
        assert model.date == "2024-12-31"

    def test_valid_iso_date_beginning_of_year(self):
        """Beginning of year ISO date is accepted."""
        model = ISODateModel(date="2024-01-01")
        assert model.date == "2024-01-01"

    def test_valid_iso_date_leap_day(self):
        """Leap day in a leap year is accepted."""
        model = ISODateModel(date="2024-02-29")
        assert model.date == "2024-02-29"

    def test_invalid_iso_date_mm_dd_yyyy_format(self):
        """MM/DD/YYYY format (the NBA API Date type) raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="01/15/2025")

    def test_invalid_iso_date_slash_separator(self):
        """ISO date with slash separator raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="2025/01/15")

    def test_invalid_iso_date_two_digit_year(self):
        """ISO date with two-digit year raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="25-01-15")

    def test_invalid_iso_date_single_digit_month(self):
        """ISO date with single-digit month raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="2025-1-15")

    def test_invalid_iso_date_single_digit_day(self):
        """ISO date with single-digit day raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="2025-01-5")

    def test_invalid_iso_date_month_overflow(self):
        """Month 13 raises ValidationError with calendar-specific message."""
        with pytest.raises(ValidationError, match="valid calendar date"):
            ISODateModel(date="2025-13-01")

    def test_invalid_iso_date_non_leap_day(self):
        """Feb 29 in a non-leap year raises ValidationError with calendar-specific message."""
        with pytest.raises(ValidationError, match="valid calendar date"):
            ISODateModel(date="2025-02-29")

    def test_invalid_iso_date_empty_string(self):
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="")

    def test_invalid_iso_date_partial_date(self):
        """Partial date (year-month only) raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD format"):
            ISODateModel(date="2025-01")

    @given(
        year=st.integers(min_value=1900, max_value=2100),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),
    )
    def test_valid_iso_date_formats_fuzzed(self, year, month, day):
        """Valid dates in YYYY-MM-DD format are accepted."""
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        model = ISODateModel(date=date_str)
        assert model.date == date_str

    @given(data=st.text(max_size=20))
    @settings(max_examples=200)
    def test_invalid_iso_date_random_strings(self, data):
        """Random strings that don't match YYYY-MM-DD should fail."""
        if re.match(r"^\d{4}-\d{2}-\d{2}$", data):
            return  # Skip valid-format strings

        with pytest.raises(ValidationError):
            ISODateModel(date=data)


class TestISODateValidatorFunction:
    """Direct tests for validate_iso_date function."""

    def test_returns_valid_date_unchanged(self):
        """Valid ISO date is returned unchanged."""
        assert validate_iso_date("2025-01-15") == "2025-01-15"

    def test_raises_value_error_for_mm_dd_yyyy(self):
        """MM/DD/YYYY format raises ValueError."""
        with pytest.raises(ValueError, match="YYYY-MM-DD format"):
            validate_iso_date("01/15/2025")

    def test_raises_value_error_for_month_overflow(self):
        """Semantically invalid date raises ValueError with calendar-specific message."""
        with pytest.raises(ValueError, match="valid calendar date"):
            validate_iso_date("2025-13-01")

    def test_raises_specific_message_for_calendar_invalid_date(self):
        """Structurally-valid but calendar-invalid date gives a distinct error message."""
        with pytest.raises(ValueError, match="valid calendar date"):
            validate_iso_date("2025-02-30")

    def test_calendar_invalid_date_preserves_cause_as_chain(self):
        """ValueError for a calendar-invalid date preserves the original parse error as __cause__."""
        with pytest.raises(ValueError) as exc_info:
            validate_iso_date("2025-02-30")
        assert exc_info.value.__cause__ is not None

    @given(data=st.text(max_size=50))
    @settings(max_examples=300)
    def test_never_crashes_on_any_string(self, data):
        """Function should never crash - either return value or raise ValueError."""
        try:
            result = validate_iso_date(data)
            assert result == data
        except ValueError as e:
            assert "YYYY-MM-DD format" in str(e) or "valid calendar date" in str(e)


# =============================================================================
# Literal Type Validation Tests
# =============================================================================


class TestLeagueIDValidation:
    """Tests for LeagueID Literal type."""

    @pytest.mark.parametrize(
        "league_id",
        ["00", "01", "10", "15", "20"],
    )
    def test_valid_league_ids(self, league_id):
        """All valid league IDs are accepted."""
        model = LeagueIDModel(league_id=league_id)
        assert model.league_id == league_id

    @pytest.mark.parametrize(
        "league_id",
        ["0", "000", "02", "99", "NBA", ""],
    )
    def test_invalid_league_ids(self, league_id):
        """Invalid league IDs raise ValidationError."""
        with pytest.raises(ValidationError):
            LeagueIDModel(league_id=league_id)

    @given(data=st.text(max_size=10))
    @settings(max_examples=100)
    def test_random_strings_rejected(self, data):
        """Random strings not in the Literal are rejected."""
        valid = {"00", "01", "10", "15", "20"}
        if data in valid:
            return

        with pytest.raises(ValidationError):
            LeagueIDModel(league_id=data)


class TestSeasonTypeValidation:
    """Tests for SeasonType Literal type."""

    @pytest.mark.parametrize(
        "season_type",
        ["Regular Season", "Playoffs", "Pre Season", "All Star", "PlayIn"],
    )
    def test_valid_season_types(self, season_type):
        """All valid season types are accepted."""
        model = SeasonTypeModel(season_type=season_type)
        assert model.season_type == season_type

    @pytest.mark.parametrize(
        "season_type",
        ["regular season", "PLAYOFFS", "Preseason", "All-Star", "Play-In", ""],
    )
    def test_invalid_season_types_case_sensitive(self, season_type):
        """Season types are case-sensitive."""
        with pytest.raises(ValidationError):
            SeasonTypeModel(season_type=season_type)


class TestPerModeValidation:
    """Tests for PerMode Literal type."""

    @pytest.mark.parametrize(
        "per_mode",
        [
            "Totals",
            "PerGame",
            "Per36",
            "Per40",
            "Per48",
            "PerMinute",
            "PerPossession",
            "PerPlay",
            "Per100Possessions",
            "Per100Plays",
            "MinutesPer",
        ],
    )
    def test_valid_per_modes(self, per_mode):
        """All valid per modes are accepted."""
        model = PerModeModel(per_mode=per_mode)
        assert model.per_mode == per_mode

    @pytest.mark.parametrize(
        "per_mode",
        ["pergame", "TOTALS", "Per Game", "per_game", ""],
    )
    def test_invalid_per_modes(self, per_mode):
        """Invalid per modes raise ValidationError."""
        with pytest.raises(ValidationError):
            PerModeModel(per_mode=per_mode)


class TestConferenceValidation:
    """Tests for Conference Literal type."""

    @pytest.mark.parametrize("conference", ["East", "West"])
    def test_valid_conferences(self, conference):
        """Valid conferences are accepted."""
        model = ConferenceModel(conference=conference)
        assert model.conference == conference

    @pytest.mark.parametrize("conference", ["east", "WEST", "Eastern", "Western", ""])
    def test_invalid_conferences(self, conference):
        """Invalid conferences raise ValidationError."""
        with pytest.raises(ValidationError):
            ConferenceModel(conference=conference)


class TestDivisionValidation:
    """Tests for Division Literal type."""

    @pytest.mark.parametrize(
        "division",
        ["Atlantic", "Central", "Southeast", "Northwest", "Pacific", "Southwest"],
    )
    def test_valid_divisions(self, division):
        """All valid divisions are accepted."""
        model = DivisionModel(division=division)
        assert model.division == division

    @pytest.mark.parametrize(
        "division",
        ["atlantic", "CENTRAL", "North", "South", ""],
    )
    def test_invalid_divisions(self, division):
        """Invalid divisions raise ValidationError."""
        with pytest.raises(ValidationError):
            DivisionModel(division=division)


class TestOutcomeValidation:
    """Tests for Outcome Literal type."""

    @pytest.mark.parametrize("outcome", ["W", "L"])
    def test_valid_outcomes(self, outcome):
        """Valid outcomes are accepted."""
        model = OutcomeModel(outcome=outcome)
        assert model.outcome == outcome

    @pytest.mark.parametrize("outcome", ["w", "l", "Win", "Loss", ""])
    def test_invalid_outcomes(self, outcome):
        """Invalid outcomes raise ValidationError."""
        with pytest.raises(ValidationError):
            OutcomeModel(outcome=outcome)


class TestLocationValidation:
    """Tests for Location Literal type."""

    @pytest.mark.parametrize("location", ["Home", "Road"])
    def test_valid_locations(self, location):
        """Valid locations are accepted."""
        model = LocationModel(location=location)
        assert model.location == location

    @pytest.mark.parametrize("location", ["home", "Away", "ROAD", ""])
    def test_invalid_locations(self, location):
        """Invalid locations raise ValidationError."""
        with pytest.raises(ValidationError):
            LocationModel(location=location)


class TestPeriodValidation:
    """Tests for Period Literal type (integers 0-4)."""

    @pytest.mark.parametrize("period", [0, 1, 2, 3, 4])
    def test_valid_periods(self, period):
        """Valid periods are accepted."""
        model = PeriodModel(period=period)
        assert model.period == period

    @pytest.mark.parametrize("period", [-1, 5, 10, 100])
    def test_invalid_period_integers(self, period):
        """Invalid period integers raise ValidationError."""
        with pytest.raises(ValidationError):
            PeriodModel(period=period)


class TestYesNoValidation:
    """Tests for YesNo Literal type."""

    @pytest.mark.parametrize("value", ["Y", "N"])
    def test_valid_yes_no(self, value):
        """Valid Y/N values are accepted."""
        model = YesNoModel(value=value)
        assert model.value == value

    @pytest.mark.parametrize("value", ["y", "n", "Yes", "No", "1", "0", ""])
    def test_invalid_yes_no(self, value):
        """Invalid Y/N values raise ValidationError."""
        with pytest.raises(ValidationError):
            YesNoModel(value=value)


# =============================================================================
# Additional Literal Type Tests (Fuzzing)
# =============================================================================


class TestLiteralTypeFuzzing:
    """Fuzzing tests for Literal type validation."""

    @given(data=st.text(alphabet=string.ascii_letters + string.digits, max_size=20))
    @settings(max_examples=100)
    def test_league_id_fuzz(self, data):
        """Fuzz LeagueID with random alphanumeric strings."""
        valid = {"00", "01", "10", "15", "20"}
        try:
            model = LeagueIDModel(league_id=data)
            assert data in valid
            assert model.league_id == data
        except ValidationError:
            assert data not in valid

    @given(data=st.text(max_size=30))
    @settings(max_examples=100)
    def test_conference_fuzz(self, data):
        """Fuzz Conference with random strings."""
        valid = {"East", "West"}
        try:
            model = ConferenceModel(conference=data)
            assert data in valid
            assert model.conference == data
        except ValidationError:
            assert data not in valid

    @given(data=st.integers())
    @settings(max_examples=100)
    def test_period_fuzz(self, data):
        """Fuzz Period with random integers."""
        valid = {0, 1, 2, 3, 4}
        try:
            model = PeriodModel(period=data)
            assert data in valid
            assert model.period == data
        except ValidationError:
            assert data not in valid


# =============================================================================
# Integration Tests with Real Endpoints
# =============================================================================


class TestTypesInEndpoints:
    """Test type validation in actual endpoint models."""

    def test_season_validation_in_endpoint(self):
        """Season type validates correctly when used in endpoint."""
        from fastbreak.endpoints import PlayerGameLog

        # PlayerGameLog expects player_id as string
        endpoint = PlayerGameLog(player_id="2544", season="2024-25")
        assert endpoint.season == "2024-25"

    def test_invalid_season_in_endpoint(self):
        """Invalid season raises ValidationError in endpoint."""
        from fastbreak.endpoints import PlayerGameLog

        with pytest.raises(ValidationError, match="YYYY-YY format"):
            PlayerGameLog(player_id="2544", season="2024")

    def test_league_id_validation_in_endpoint(self):
        """LeagueID validates correctly in endpoint."""
        from fastbreak.endpoints import LeagueStandings

        endpoint = LeagueStandings(league_id="00", season="2024-25")
        assert endpoint.league_id == "00"

    def test_invalid_league_id_in_endpoint(self):
        """Invalid LeagueID raises ValidationError in endpoint."""
        from fastbreak.endpoints import LeagueStandings

        with pytest.raises(ValidationError):
            LeagueStandings(league_id="99", season="2024-25")

    def test_per_mode_validation_in_endpoint(self):
        """PerMode validates correctly in endpoint."""
        from fastbreak.endpoints import PlayerDashboardByGeneralSplits

        endpoint = PlayerDashboardByGeneralSplits(player_id=2544, per_mode="PerGame")
        assert endpoint.per_mode == "PerGame"

    def test_invalid_per_mode_in_endpoint(self):
        """Invalid PerMode raises ValidationError in endpoint."""
        from fastbreak.endpoints import PlayerDashboardByGeneralSplits

        with pytest.raises(ValidationError):
            PlayerDashboardByGeneralSplits(player_id=2544, per_mode="invalid")

    def test_date_validation_in_endpoint(self):
        """Date validates correctly in dashboard endpoint."""
        from fastbreak.endpoints import PlayerDashboardByGeneralSplits

        endpoint = PlayerDashboardByGeneralSplits(
            player_id=2544, date_from="01/01/2025", date_to="01/31/2025"
        )
        assert endpoint.date_from == "01/01/2025"
        assert endpoint.date_to == "01/31/2025"

    def test_invalid_date_in_endpoint(self):
        """Invalid Date raises ValidationError in endpoint."""
        from fastbreak.endpoints import PlayerDashboardByGeneralSplits

        with pytest.raises(ValidationError, match="MM/DD/YYYY format"):
            PlayerDashboardByGeneralSplits(player_id=2544, date_from="2025-01-01")
