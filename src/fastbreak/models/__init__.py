"""NBA API response models.

This module auto-exports all public symbols from submodules.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

# Type alias defined here (not in a submodule)
type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None

# Explicit imports for type checkers (mypy, pyright, etc.)
# These are redundant at runtime but needed for static analysis
if TYPE_CHECKING:
    from fastbreak.models.advanced_statistics import (
        AdvancedStatistics as AdvancedStatistics,
        AdvancedTeamStatistics as AdvancedTeamStatistics,
    )
    from fastbreak.models.all_time_leaders import (
        AllTimeLeadersResponse as AllTimeLeadersResponse,
        LeaderEntry as LeaderEntry,
    )
    from fastbreak.models.arena import Arena as Arena
    from fastbreak.models.assist_leaders import (
        AssistLeadersResponse as AssistLeadersResponse,
        PlayerAssistLeader as PlayerAssistLeader,
        TeamAssistLeader as TeamAssistLeader,
    )
    from fastbreak.models.assist_tracker import (
        AssistTrackerResponse as AssistTrackerResponse,
    )
    from fastbreak.models.box_score_advanced import (
        AdvancedPlayer as AdvancedPlayer,
        AdvancedTeam as AdvancedTeam,
        BoxScoreAdvancedData as BoxScoreAdvancedData,
        BoxScoreAdvancedResponse as BoxScoreAdvancedResponse,
    )
    from fastbreak.models.box_score_four_factors import (
        BoxScoreFourFactorsData as BoxScoreFourFactorsData,
        BoxScoreFourFactorsResponse as BoxScoreFourFactorsResponse,
        FourFactorsPlayer as FourFactorsPlayer,
        FourFactorsTeam as FourFactorsTeam,
    )
    from fastbreak.models.box_score_matchups import (
        BoxScoreMatchupsData as BoxScoreMatchupsData,
        BoxScoreMatchupsResponse as BoxScoreMatchupsResponse,
        MatchupOpponent as MatchupOpponent,
        MatchupsPlayer as MatchupsPlayer,
        MatchupsTeam as MatchupsTeam,
    )
    from fastbreak.models.box_score_misc import (
        BoxScoreMiscData as BoxScoreMiscData,
        BoxScoreMiscResponse as BoxScoreMiscResponse,
        MiscPlayer as MiscPlayer,
        MiscTeam as MiscTeam,
    )
    from fastbreak.models.box_score_player_track import (
        BoxScorePlayerTrackData as BoxScorePlayerTrackData,
        BoxScorePlayerTrackResponse as BoxScorePlayerTrackResponse,
        PlayerTrackPlayer as PlayerTrackPlayer,
        PlayerTrackTeam as PlayerTrackTeam,
    )
    from fastbreak.models.box_score_scoring import (
        BoxScoreScoringData as BoxScoreScoringData,
        BoxScoreScoringResponse as BoxScoreScoringResponse,
        ScoringPlayer as ScoringPlayer,
        ScoringTeam as ScoringTeam,
    )
    from fastbreak.models.box_score_summary import (
        BoxScoreSummaryData as BoxScoreSummaryData,
        BoxScoreSummaryResponse as BoxScoreSummaryResponse,
    )
    from fastbreak.models.box_score_traditional import (
        BoxScoreTraditionalData as BoxScoreTraditionalData,
        BoxScoreTraditionalResponse as BoxScoreTraditionalResponse,
        TraditionalPlayer as TraditionalPlayer,
        TraditionalTeam as TraditionalTeam,
    )
    from fastbreak.models.box_score_usage import (
        BoxScoreUsageData as BoxScoreUsageData,
        BoxScoreUsageResponse as BoxScoreUsageResponse,
        UsagePlayer as UsagePlayer,
        UsageTeam as UsageTeam,
    )
    from fastbreak.models.broadcaster import (
        Broadcaster as Broadcaster,
        Broadcasters as Broadcasters,
    )
    from fastbreak.models.chart import Charts as Charts, ChartTeam as ChartTeam
    from fastbreak.models.common_all_players import (
        CommonAllPlayersResponse as CommonAllPlayersResponse,
        CommonPlayer as CommonPlayer,
    )
    from fastbreak.models.common_player_info import (
        AvailableSeason as AvailableSeason,
        CommonPlayerInfoResponse as CommonPlayerInfoResponse,
        PlayerHeadlineStats as PlayerHeadlineStats,
        PlayerInfo as PlayerInfo,
    )
    from fastbreak.models.common_playoff_series import (
        CommonPlayoffSeriesResponse as CommonPlayoffSeriesResponse,
        PlayoffSeriesGame as PlayoffSeriesGame,
    )
    from fastbreak.models.common_team_roster import (
        Coach as Coach,
        CommonTeamRosterResponse as CommonTeamRosterResponse,
        RosterPlayer as RosterPlayer,
    )
    from fastbreak.models.common_team_years import (
        CommonTeamYearsResponse as CommonTeamYearsResponse,
        TeamYear as TeamYear,
    )
    from fastbreak.models.cume_stats_player import (
        CumeStatsPlayerResponse as CumeStatsPlayerResponse,
        GameByGameStat as GameByGameStat,
        TotalPlayerStat as TotalPlayerStat,
    )
    from fastbreak.models.cume_stats_player_games import (
        CumeStatsPlayerGamesResponse as CumeStatsPlayerGamesResponse,
        PlayerGame as PlayerGame,
    )
    from fastbreak.models.cume_stats_team import (
        CumeStatsTeamResponse as CumeStatsTeamResponse,
        TeamPlayerStat as TeamPlayerStat,
        TotalTeamStat as TotalTeamStat,
    )
    from fastbreak.models.cume_stats_team_games import (
        CumeStatsTeamGamesResponse as CumeStatsTeamGamesResponse,
        TeamGame as TeamGame,
    )
    from fastbreak.models.dataframe import (
        PandasMixin as PandasMixin,
        PolarsMixin as PolarsMixin,
    )
    from fastbreak.models.draft_combine_drill_results import (
        DraftCombineDrillResultsResponse as DraftCombineDrillResultsResponse,
        DrillResultsPlayer as DrillResultsPlayer,
    )
    from fastbreak.models.draft_combine_nonstationary_shooting import (
        DraftCombineNonstationaryShootingResponse as DraftCombineNonstationaryShootingResponse,
        NonstationaryShootingPlayer as NonstationaryShootingPlayer,
    )
    from fastbreak.models.draft_combine_player_anthro import (
        AnthroPlayer as AnthroPlayer,
        DraftCombinePlayerAnthroResponse as DraftCombinePlayerAnthroResponse,
    )
    from fastbreak.models.draft_combine_spot_shooting import (
        DraftCombineSpotShootingResponse as DraftCombineSpotShootingResponse,
        SpotShootingPlayer as SpotShootingPlayer,
    )
    from fastbreak.models.draft_combine_stats import (
        CombinePlayer as CombinePlayer,
        DraftCombineStatsResponse as DraftCombineStatsResponse,
    )
    from fastbreak.models.draft_history import (
        DraftHistoryResponse as DraftHistoryResponse,
        DraftPick as DraftPick,
    )
    from fastbreak.models.dunk_score_leaders import (
        Dunk as Dunk,
        DunkScoreLeadersResponse as DunkScoreLeadersResponse,
    )
    from fastbreak.models.four_factors_statistics import (
        FourFactorsStatistics as FourFactorsStatistics,
    )
    from fastbreak.models.franchise_history import (
        Franchise as Franchise,
        FranchiseHistoryResponse as FranchiseHistoryResponse,
    )
    from fastbreak.models.franchise_leaders import (
        FranchiseLeader as FranchiseLeader,
        FranchiseLeadersResponse as FranchiseLeadersResponse,
        StatLeader as StatLeader,
    )
    from fastbreak.models.franchise_players import (
        FranchisePlayer as FranchisePlayer,
        FranchisePlayersResponse as FranchisePlayersResponse,
    )
    from fastbreak.models.gravity_leaders import (
        GravityLeader as GravityLeader,
        GravityLeadersResponse as GravityLeadersResponse,
    )
    from fastbreak.models.league_standings import (
        LeagueStandingsResponse as LeagueStandingsResponse,
        TeamStanding as TeamStanding,
    )
    from fastbreak.models.matchup_statistics import (
        MatchupStatistics as MatchupStatistics,
    )
    from fastbreak.models.meeting import (
        LastFiveMeetings as LastFiveMeetings,
        Meeting as Meeting,
        MeetingTeam as MeetingTeam,
    )
    from fastbreak.models.meta import Meta as Meta
    from fastbreak.models.misc_statistics import MiscStatistics as MiscStatistics
    from fastbreak.models.official import Official as Official
    from fastbreak.models.period import Period as Period
    from fastbreak.models.play_by_play import (
        PlayByPlayAction as PlayByPlayAction,
        PlayByPlayGame as PlayByPlayGame,
        PlayByPlayResponse as PlayByPlayResponse,
    )
    from fastbreak.models.player import Player as Player
    from fastbreak.models.player_track_statistics import (
        PlayerTrackStatistics as PlayerTrackStatistics,
        TeamPlayerTrackStatistics as TeamPlayerTrackStatistics,
    )
    from fastbreak.models.result_set import (
        ValidatorFunc as ValidatorFunc,
        is_tabular_response as is_tabular_response,
        named_result_sets_validator as named_result_sets_validator,
        parse_result_set as parse_result_set,
        parse_result_set_by_name as parse_result_set_by_name,
        tabular_validator as tabular_validator,
    )
    from fastbreak.models.scoring_statistics import (
        ScoringStatistics as ScoringStatistics,
    )
    from fastbreak.models.summary_player import (
        InactivePlayer as InactivePlayer,
        SummaryPlayer as SummaryPlayer,
    )
    from fastbreak.models.summary_team import SummaryTeam as SummaryTeam
    from fastbreak.models.team import Team as Team
    from fastbreak.models.traditional_statistics import (
        TraditionalGroupStatistics as TraditionalGroupStatistics,
        TraditionalStatistics as TraditionalStatistics,
    )
    from fastbreak.models.usage_statistics import UsageStatistics as UsageStatistics

# Auto-discover and import all submodules at runtime
_package_dir = Path(__file__).parent
_public_names: list[str] = ["JSON"]

for _module_info in pkgutil.iter_modules([str(_package_dir)]):
    if _module_info.name.startswith("_"):
        continue

    _module = importlib.import_module(f".{_module_info.name}", __package__)

    # Get exportable names from module
    if hasattr(_module, "__all__"):
        _names = _module.__all__
    else:
        _names = [n for n in dir(_module) if not n.startswith("_")]

    # Import names into this namespace and track them
    for _name in _names:
        if hasattr(_module, _name):
            globals()[_name] = getattr(_module, _name)
            _public_names.append(_name)

__all__ = sorted(set(_public_names))  # noqa: PLE0605

# Clean up module-level temporaries
del importlib, pkgutil, Path
del _package_dir, _module_info, _module, _names, _name, _public_names
