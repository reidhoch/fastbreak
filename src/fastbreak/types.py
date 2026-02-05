"""
Type aliases for NBA API parameters.
"""

import re
from typing import Annotated, Literal

from pydantic import AfterValidator, Field


def _validate_season(value: str) -> str:
    """Validate season format is YYYY-YY (e.g., '2024-25')."""
    if not re.match(r"^\d{4}-\d{2}$", value):
        msg = "Season must be in YYYY-YY format (e.g., '2024-25')"
        raise ValueError(msg)
    return value


def _validate_date(value: str) -> str:
    """Validate date format is MM/DD/YYYY (e.g., '01/15/2025')."""
    if not re.match(r"^\d{2}/\d{2}/\d{4}$", value):
        msg = "Date must be in MM/DD/YYYY format (e.g., '01/15/2025')"
        raise ValueError(msg)
    return value


Conference = Annotated[
    Literal["East", "West"],
    Field(description="NBA conference"),
]

ContextMeasure = Annotated[
    Literal[
        "FGA",
        "FGM",
        "FG3A",
        "FG3M",
        "FTA",
        "FTM",
        "PTS",
        "PTS_FB",
        "PTS_OFF_TOV",
        "PTS_2ND_CHANCE",
        "PF",
        "EFG_PCT",
        "TS_PCT",
    ],
    Field(description="Shot chart context measure"),
]

Date = Annotated[
    str,
    AfterValidator(_validate_date),
    Field(description="Date in MM/DD/YYYY format (e.g., '01/15/2025')"),
]

DistanceRange = Annotated[
    Literal["5ft Range", "8ft Range", "By Zone"],
    Field(description="Shot distance range grouping"),
]

Division = Annotated[
    Literal["Atlantic", "Central", "Southeast", "Northwest", "Pacific", "Southwest"],
    Field(description="NBA division"),
]

GameSegment = Annotated[
    Literal["First Half", "Second Half", "Overtime"],
    Field(description="Segment of a game"),
]

# League ID reference:
# "00" = NBA, "01" = ABA, "10" = WNBA, "15" = G-League, "20" = Summer League
LeagueID = Annotated[
    Literal["00", "01", "10", "15", "20"],
    Field(description="NBA Stats API League ID"),
]

Location = Annotated[
    Literal["Home", "Road"],
    Field(description="Game location"),
]

MeasureType = Annotated[
    Literal[
        "Base",
        "Advanced",
        "Misc",
        "Scoring",
        "Usage",
        "Four Factors",
        "Opponent",
        "Defense",
    ],
    Field(description="Type of statistical measure"),
]

Outcome = Annotated[
    Literal["W", "L"],
    Field(description="Game outcome"),
]

PerMode = Annotated[
    Literal[
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
    Field(description="Statistical aggregation mode"),
]

Period = Annotated[
    Literal[0, 1, 2, 3, 4],
    Field(description="Period of the game (0=All, 1-4=Quarters)"),
]

PlayerExperience = Annotated[
    Literal["Rookie", "Sophomore", "Veteran"],
    Field(description="Player experience level"),
]

PlayerOrTeam = Annotated[
    Literal["Player", "Team"],
    Field(description="Whether to retrieve player or team statistics"),
]

PlayerOrTeamAbbreviation = Annotated[
    Literal["P", "T"],
    Field(description="Abbreviation for Player or Team search mode"),
]

PlayerPosition = Annotated[
    Literal["G", "F", "C", "G-F", "F-G", "F-C", "C-F"],
    Field(description="Player position"),
]

PlayType = Annotated[
    Literal[
        "Isolation",
        "Transition",
        "PRBallHandler",
        "PRRollman",
        "Postup",
        "Spotup",
        "Handoff",
        "Cut",
        "OffScreen",
        "OffRebound",
        "Misc",
    ],
    Field(description="Synergy play type"),
]

PtMeasureType = Annotated[
    Literal[
        "Drives",
        "Defense",
        "CatchShoot",
        "Passing",
        "Possessions",
        "PullUpShot",
        "Rebounding",
        "Efficiency",
        "SpeedDistance",
        "ElbowTouch",
        "PostTouch",
        "PaintTouch",
    ],
    Field(description="Player tracking measure type"),
]

Scope = Annotated[
    Literal["S", "RS", "Rookies"],
    Field(description="Player scope"),
]

Season = Annotated[
    str,
    AfterValidator(_validate_season),
    Field(description="NBA season in YYYY-YY format (e.g., '2024-25')"),
]

SeasonSegment = Annotated[
    Literal["Pre All-Star", "Post All-Star"],
    Field(description="Segment of a season"),
]

SeasonType = Annotated[
    Literal["Regular Season", "Playoffs", "Pre Season", "All Star", "PlayIn"],
    Field(description="Type of NBA season"),
]

Section = Annotated[
    Literal["group", "wildcard"],
    Field(description="IST section"),
]

ShotClockRange = Annotated[
    Literal[
        "24-22",
        "22-18 Very Early",
        "18-15 Early",
        "15-7 Average",
        "7-4 Late",
        "4-0 Very Late",
        "ShotClock Off",
    ],
    Field(description="Shot clock range filter"),
]

StarterBench = Annotated[
    Literal["Starter", "Bench"],
    Field(description="Starter or bench player"),
]

StatCategoryAbbreviation = Annotated[
    Literal[
        "PTS",
        "FGM",
        "FGA",
        "FG_PCT",
        "FG3M",
        "FG3A",
        "FG3_PCT",
        "FTM",
        "FTA",
        "OREB",
        "DREB",
        "AST",
        "STL",
        "BLK",
        "TOV",
        "REB",
    ],
    Field(description="Statistical category abbreviation"),
]

YesNo = Annotated[
    Literal["Y", "N"],
    Field(description="Yes or No flag"),
]

AheadBehind = Annotated[
    Literal["Ahead or Behind", "Ahead or Tied", "Behind or Tied"],
    Field(description="Clutch game situation filter"),
]

ClutchTime = Annotated[
    Literal[
        "Last 5 Minutes",
        "Last 4 Minutes",
        "Last 3 Minutes",
        "Last 2 Minutes",
        "Last 1 Minute",
        "Last 30 Seconds",
        "Last 10 Seconds",
    ],
    Field(description="Time remaining in clutch situations"),
]
