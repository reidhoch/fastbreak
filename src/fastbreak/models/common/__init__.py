"""Common/shared model components.

This module contains:
- Parsing utilities for NBA API tabular format (result_set)
- DataFrame conversion mixins (dataframe)
- Shared statistics models used by box scores
- Entity models (Player, Team, Arena, etc.)
- Response metadata (Meta)
"""

# Parsing utilities
from fastbreak.models.common.advanced_statistics import AdvancedStatistics
from fastbreak.models.common.arena import Arena
from fastbreak.models.common.broadcaster import Broadcaster
from fastbreak.models.common.chart import Charts, ChartTeam

# DataFrame mixins
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.four_factors_statistics import FourFactorsStatistics
from fastbreak.models.common.matchup_statistics import MatchupStatistics
from fastbreak.models.common.meeting import Meeting

# Response metadata
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.misc_statistics import MiscStatistics
from fastbreak.models.common.official import Official
from fastbreak.models.common.period import Period

# Entity models
from fastbreak.models.common.player import Player
from fastbreak.models.common.player_track_statistics import PlayerTrackStatistics
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    ValidatorFunc,
    is_tabular_response,
    named_result_sets_validator,
    parse_result_set,
    parse_result_set_by_name,
    parse_single_result_set,
    tabular_validator,
)
from fastbreak.models.common.scoring_statistics import ScoringStatistics
from fastbreak.models.common.summary_player import SummaryPlayer
from fastbreak.models.common.summary_team import SummaryTeam
from fastbreak.models.common.team import Team

# Statistics models (used by box scores)
from fastbreak.models.common.traditional_statistics import TraditionalStatistics
from fastbreak.models.common.usage_statistics import UsageStatistics

__all__ = [
    "AdvancedStatistics",
    "Arena",
    "Broadcaster",
    "ChartTeam",
    "Charts",
    "FourFactorsStatistics",
    # Response base classes
    "FrozenResponse",
    "MatchupStatistics",
    "Meeting",
    # Metadata
    "Meta",
    "MiscStatistics",
    "Official",
    # DataFrame
    "PandasMixin",
    "Period",
    # Entities
    "Player",
    "PlayerTrackStatistics",
    "PolarsMixin",
    "ScoringStatistics",
    "SummaryPlayer",
    "SummaryTeam",
    "Team",
    # Statistics
    "TraditionalStatistics",
    "UsageStatistics",
    # Parsing
    "ValidatorFunc",
    "is_tabular_response",
    "named_result_sets_validator",
    "parse_result_set",
    "parse_result_set_by_name",
    "parse_single_result_set",
    "tabular_validator",
]
