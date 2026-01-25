"""Enums for NBA API parameters.

These enums provide type safety and IDE autocomplete for common API parameters.
All enums inherit from StrEnum so they can be used directly as string values.
"""

from enum import StrEnum


class SeasonType(StrEnum):
    """Type of NBA season."""

    REGULAR_SEASON = "Regular Season"
    PLAYOFFS = "Playoffs"
    PRE_SEASON = "Pre Season"
    ALL_STAR = "All Star"
    PLAY_IN = "PlayIn"


class PerMode(StrEnum):
    """Statistical aggregation mode."""

    TOTALS = "Totals"
    PER_GAME = "PerGame"
    PER_36 = "Per36"
    PER_40 = "Per40"
    PER_48 = "Per48"
    PER_MINUTE = "PerMinute"
    PER_POSSESSION = "PerPossession"
    PER_PLAY = "PerPlay"
    PER_100_POSSESSIONS = "Per100Possessions"
    PER_100_PLAYS = "Per100Plays"
    MINUTES_PER = "MinutesPer"


class MeasureType(StrEnum):
    """Type of statistical measure."""

    BASE = "Base"
    ADVANCED = "Advanced"
    MISC = "Misc"
    SCORING = "Scoring"
    USAGE = "Usage"
    FOUR_FACTORS = "Four Factors"
    OPPONENT = "Opponent"
    DEFENSE = "Defense"


class PtMeasureType(StrEnum):
    """Player tracking measure type."""

    DRIVES = "Drives"
    DEFENSE = "Defense"
    CATCH_SHOOT = "CatchShoot"
    PASSING = "Passing"
    POSSESSIONS = "Possessions"
    PULL_UP_SHOT = "PullUpShot"
    REBOUNDING = "Rebounding"
    EFFICIENCY = "Efficiency"
    SPEED_DISTANCE = "SpeedDistance"
    ELBOW_TOUCH = "ElbowTouch"
    POST_TOUCH = "PostTouch"
    PAINT_TOUCH = "PaintTouch"


class PlayerOrTeam(StrEnum):
    """Whether to retrieve player or team statistics."""

    PLAYER = "Player"
    TEAM = "Team"


class LeagueID(StrEnum):
    """NBA league identifier."""

    NBA = "00"
    WNBA = "10"
    G_LEAGUE = "20"


class Conference(StrEnum):
    """NBA conference."""

    EAST = "East"
    WEST = "West"


class Location(StrEnum):
    """Game location (home or away)."""

    HOME = "Home"
    ROAD = "Road"


class Outcome(StrEnum):
    """Game outcome (win or loss)."""

    WIN = "W"
    LOSS = "L"


class GameSegment(StrEnum):
    """Segment of a game."""

    FIRST_HALF = "First Half"
    SECOND_HALF = "Second Half"
    OVERTIME = "Overtime"


class SeasonSegment(StrEnum):
    """Segment of a season."""

    PRE_ALL_STAR = "Pre All-Star"
    POST_ALL_STAR = "Post All-Star"


class PlayerExperience(StrEnum):
    """Player experience level."""

    ROOKIE = "Rookie"
    SOPHOMORE = "Sophomore"
    VETERAN = "Veteran"


class PlayerPosition(StrEnum):
    """Player position."""

    GUARD = "G"
    FORWARD = "F"
    CENTER = "C"
    GUARD_FORWARD = "G-F"
    FORWARD_GUARD = "F-G"
    FORWARD_CENTER = "F-C"
    CENTER_FORWARD = "C-F"


class StarterBench(StrEnum):
    """Starter or bench player."""

    STARTER = "Starter"
    BENCH = "Bench"


class DistanceRange(StrEnum):
    """Shot distance range grouping."""

    FIVE_FEET = "5ft Range"
    EIGHT_FEET = "8ft Range"
    BY_ZONE = "By Zone"


class Division(StrEnum):
    """NBA division."""

    ATLANTIC = "Atlantic"
    CENTRAL = "Central"
    SOUTHEAST = "Southeast"
    NORTHWEST = "Northwest"
    PACIFIC = "Pacific"
    SOUTHWEST = "Southwest"
