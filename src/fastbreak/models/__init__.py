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
    # Common/shared models
    # Endpoint-specific response models
    from fastbreak.models.all_time_leaders import (
        AllTimeLeadersResponse as AllTimeLeadersResponse,
        LeaderEntry as LeaderEntry,
    )
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
    from fastbreak.models.common.advanced_statistics import (
        AdvancedStatistics as AdvancedStatistics,
        AdvancedTeamStatistics as AdvancedTeamStatistics,
    )
    from fastbreak.models.common.arena import Arena as Arena
    from fastbreak.models.common.broadcaster import (
        Broadcaster as Broadcaster,
        Broadcasters as Broadcasters,
    )
    from fastbreak.models.common.chart import Charts as Charts, ChartTeam as ChartTeam
    from fastbreak.models.common.dataframe import (
        PandasMixin as PandasMixin,
        PolarsMixin as PolarsMixin,
    )
    from fastbreak.models.common.four_factors_statistics import (
        FourFactorsStatistics as FourFactorsStatistics,
    )
    from fastbreak.models.common.matchup_statistics import (
        MatchupStatistics as MatchupStatistics,
    )
    from fastbreak.models.common.meeting import (
        LastFiveMeetings as LastFiveMeetings,
        Meeting as Meeting,
        MeetingTeam as MeetingTeam,
    )
    from fastbreak.models.common.meta import Meta as Meta
    from fastbreak.models.common.misc_statistics import (
        MiscStatistics as MiscStatistics,
    )
    from fastbreak.models.common.official import Official as Official
    from fastbreak.models.common.period import Period as Period
    from fastbreak.models.common.player import Player as Player
    from fastbreak.models.common.player_track_statistics import (
        PlayerTrackStatistics as PlayerTrackStatistics,
        TeamPlayerTrackStatistics as TeamPlayerTrackStatistics,
    )
    from fastbreak.models.common.result_set import (
        ValidatorFunc as ValidatorFunc,
        is_tabular_response as is_tabular_response,
        named_result_sets_validator as named_result_sets_validator,
        parse_result_set as parse_result_set,
        parse_result_set_by_name as parse_result_set_by_name,
        parse_single_result_set as parse_single_result_set,
        tabular_validator as tabular_validator,
    )
    from fastbreak.models.common.scoring_statistics import (
        ScoringStatistics as ScoringStatistics,
    )
    from fastbreak.models.common.summary_player import (
        InactivePlayer as InactivePlayer,
        SummaryPlayer as SummaryPlayer,
    )
    from fastbreak.models.common.summary_team import SummaryTeam as SummaryTeam
    from fastbreak.models.common.team import Team as Team
    from fastbreak.models.common.traditional_statistics import (
        TraditionalGroupStatistics as TraditionalGroupStatistics,
        TraditionalStatistics as TraditionalStatistics,
    )
    from fastbreak.models.common.usage_statistics import (
        UsageStatistics as UsageStatistics,
    )
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
    from fastbreak.models.game_rotation import (
        GameRotationResponse as GameRotationResponse,
        RotationEntry as RotationEntry,
    )
    from fastbreak.models.gravity_leaders import (
        GravityLeader as GravityLeader,
        GravityLeadersResponse as GravityLeadersResponse,
    )
    from fastbreak.models.hustle_stats_boxscore import (
        HustleStatsAvailable as HustleStatsAvailable,
        HustleStatsBoxscoreResponse as HustleStatsBoxscoreResponse,
        HustleStatsPlayer as HustleStatsPlayer,
        HustleStatsTeam as HustleStatsTeam,
    )
    from fastbreak.models.infographic_fanduel_player import (
        FanDuelPlayer as FanDuelPlayer,
        InfographicFanDuelPlayerResponse as InfographicFanDuelPlayerResponse,
    )
    from fastbreak.models.ist_standings import (
        IstGame as IstGame,
        IstStandingsResponse as IstStandingsResponse,
        IstTeamStanding as IstTeamStanding,
    )
    from fastbreak.models.league_dash_lineups import (
        LeagueDashLineupsResponse as LeagueDashLineupsResponse,
        LeagueLineup as LeagueLineup,
    )
    from fastbreak.models.league_dash_pt_stats import (
        LeagueDashPtStatsResponse as LeagueDashPtStatsResponse,
        PlayerPtStats as PlayerPtStats,
        TeamPtStats as TeamPtStats,
    )
    from fastbreak.models.league_dash_team_shot_locations import (
        LeagueDashTeamShotLocationsResponse as LeagueDashTeamShotLocationsResponse,
        ShotRange as ShotRange,
        TeamShotLocations as TeamShotLocations,
    )
    from fastbreak.models.league_game_finder import (
        GameFinderResult as GameFinderResult,
        LeagueGameFinderResponse as LeagueGameFinderResponse,
    )
    from fastbreak.models.league_game_log import (
        GameLogEntry as GameLogEntry,
        LeagueGameLogResponse as LeagueGameLogResponse,
    )
    from fastbreak.models.league_hustle_stats_player import (
        LeagueHustlePlayer as LeagueHustlePlayer,
        LeagueHustleStatsPlayerResponse as LeagueHustleStatsPlayerResponse,
    )
    from fastbreak.models.league_hustle_stats_team import (
        LeagueHustleStatsTeamResponse as LeagueHustleStatsTeamResponse,
        LeagueHustleTeam as LeagueHustleTeam,
    )
    from fastbreak.models.league_leaders import (
        LeagueLeader as LeagueLeader,
        LeagueLeadersResponse as LeagueLeadersResponse,
    )
    from fastbreak.models.league_lineup_viz import (
        LeagueLineupVizResponse as LeagueLineupVizResponse,
        LineupViz as LineupViz,
    )
    from fastbreak.models.league_player_on_details import (
        LeaguePlayerOnDetailsResponse as LeaguePlayerOnDetailsResponse,
        PlayerOnCourtDetail as PlayerOnCourtDetail,
    )
    from fastbreak.models.league_season_matchups import (
        LeagueSeasonMatchupsResponse as LeagueSeasonMatchupsResponse,
        SeasonMatchup as SeasonMatchup,
    )
    from fastbreak.models.league_standings import (
        LeagueStandingsResponse as LeagueStandingsResponse,
        TeamStanding as TeamStanding,
    )
    from fastbreak.models.leverage_leaders import (
        LeverageLeader as LeverageLeader,
        LeverageLeadersResponse as LeverageLeadersResponse,
    )
    from fastbreak.models.matchups_rollup import (
        MatchupRollupEntry as MatchupRollupEntry,
        MatchupsRollupResponse as MatchupsRollupResponse,
    )
    from fastbreak.models.play_by_play import (
        PlayByPlayAction as PlayByPlayAction,
        PlayByPlayGame as PlayByPlayGame,
        PlayByPlayResponse as PlayByPlayResponse,
    )
    from fastbreak.models.player_awards import (
        PlayerAward as PlayerAward,
        PlayerAwardsResponse as PlayerAwardsResponse,
    )
    from fastbreak.models.player_career_by_college import (
        CollegePlayerCareer as CollegePlayerCareer,
        PlayerCareerByCollegeResponse as PlayerCareerByCollegeResponse,
    )
    from fastbreak.models.player_career_by_college_rollup import (
        CollegeRollupEntry as CollegeRollupEntry,
        PlayerCareerByCollegeRollupResponse as PlayerCareerByCollegeRollupResponse,
    )
    from fastbreak.models.player_career_stats import (
        CareerTotals as CareerTotals,
        CollegeCareerTotals as CollegeCareerTotals,
        CollegeSeasonTotals as CollegeSeasonTotals,
        PlayerCareerStatsResponse as PlayerCareerStatsResponse,
        SeasonRankings as SeasonRankings,
        SeasonTotals as SeasonTotals,
        StatHigh as StatHigh,
    )
    from fastbreak.models.player_compare import (
        PlayerCompareResponse as PlayerCompareResponse,
        PlayerCompareStats as PlayerCompareStats,
    )
    from fastbreak.models.player_dash_pt_pass import (
        PassMade as PassMade,
        PassReceived as PassReceived,
        PlayerDashPtPassResponse as PlayerDashPtPassResponse,
    )
    from fastbreak.models.player_dash_pt_reb import (
        NumContestedRebounding as NumContestedRebounding,
        OverallRebounding as OverallRebounding,
        PlayerDashPtRebResponse as PlayerDashPtRebResponse,
        RebDistanceRebounding as RebDistanceRebounding,
        ShotDistanceRebounding as ShotDistanceRebounding,
        ShotTypeRebounding as ShotTypeRebounding,
    )
    from fastbreak.models.player_dash_pt_shot_defend import (
        DefendingShots as DefendingShots,
        PlayerDashPtShotDefendResponse as PlayerDashPtShotDefendResponse,
    )
    from fastbreak.models.player_dash_pt_shots import (
        ClosestDefenderStats as ClosestDefenderStats,
        DribbleStats as DribbleStats,
        PlayerDashPtShotsResponse as PlayerDashPtShotsResponse,
        ShotClockStats as ShotClockStats,
        ShotTypeStats as ShotTypeStats,
        TouchTimeStats as TouchTimeStats,
    )
    from fastbreak.models.player_dashboard_by_clutch import (
        ClutchStats as ClutchStats,
        PlayerDashboardByClutchResponse as PlayerDashboardByClutchResponse,
    )
    from fastbreak.models.player_dashboard_by_game_splits import (
        GameSplitStats as GameSplitStats,
        PlayerDashboardByGameSplitsResponse as PlayerDashboardByGameSplitsResponse,
    )
    from fastbreak.models.player_dashboard_by_general_splits import (
        PlayerDashboardByGeneralSplitsResponse as PlayerDashboardByGeneralSplitsResponse,
    )
    from fastbreak.models.player_dashboard_by_last_n_games import (
        PlayerDashboardByLastNGamesResponse as PlayerDashboardByLastNGamesResponse,
    )
    from fastbreak.models.player_dashboard_by_shooting_splits import (
        AssistedByStats as AssistedByStats,
        PlayerDashboardByShootingSplitsResponse as PlayerDashboardByShootingSplitsResponse,
        ShootingSplitStats as ShootingSplitStats,
        ShootingSplitStatsWithRank as ShootingSplitStatsWithRank,
    )
    from fastbreak.models.player_dashboard_by_team_performance import (
        PlayerDashboardByTeamPerformanceResponse as PlayerDashboardByTeamPerformanceResponse,
        TeamPerformanceStats as TeamPerformanceStats,
    )
    from fastbreak.models.player_dashboard_by_year_over_year import (
        PlayerDashboardByYearOverYearResponse as PlayerDashboardByYearOverYearResponse,
        YearOverYearStats as YearOverYearStats,
    )
    from fastbreak.models.player_estimated_metrics import (
        PlayerEstimatedMetric as PlayerEstimatedMetric,
        PlayerEstimatedMetricsResponse as PlayerEstimatedMetricsResponse,
    )
    from fastbreak.models.player_fantasy_profile_bar_graph import (
        FantasyStats as FantasyStats,
        PlayerFantasyProfileBarGraphResponse as PlayerFantasyProfileBarGraphResponse,
    )
    from fastbreak.models.player_game_log import (
        PlayerGameLogEntry as PlayerGameLogEntry,
        PlayerGameLogResponse as PlayerGameLogResponse,
    )
    from fastbreak.models.player_game_logs import (
        PlayerGameLogsEntry as PlayerGameLogsEntry,
        PlayerGameLogsResponse as PlayerGameLogsResponse,
    )
    from fastbreak.models.player_game_streak_finder import (
        PlayerGameStreak as PlayerGameStreak,
        PlayerGameStreakFinderResponse as PlayerGameStreakFinderResponse,
    )
    from fastbreak.models.player_index import (
        PlayerIndexEntry as PlayerIndexEntry,
        PlayerIndexResponse as PlayerIndexResponse,
    )
    from fastbreak.models.player_next_n_games import (
        NextGame as NextGame,
        PlayerNextNGamesResponse as PlayerNextNGamesResponse,
    )
    from fastbreak.models.player_profile_v2 import (
        PlayerProfileV2Response as PlayerProfileV2Response,
        ProfileCareerTotals as ProfileCareerTotals,
        ProfileCollegeCareerTotals as ProfileCollegeCareerTotals,
        ProfileCollegeSeasonTotals as ProfileCollegeSeasonTotals,
        ProfileNextGame as ProfileNextGame,
        ProfileSeasonRankings as ProfileSeasonRankings,
        ProfileSeasonTotals as ProfileSeasonTotals,
        ProfileStatHigh as ProfileStatHigh,
    )
    from fastbreak.models.player_vs_player import (
        PlayerVsPlayerOnOffCourtStats as PlayerVsPlayerOnOffCourtStats,
        PlayerVsPlayerOverallStats as PlayerVsPlayerOverallStats,
        PlayerVsPlayerPlayerInfo as PlayerVsPlayerPlayerInfo,
        PlayerVsPlayerResponse as PlayerVsPlayerResponse,
        PlayerVsPlayerShotAreaOnOffStats as PlayerVsPlayerShotAreaOnOffStats,
        PlayerVsPlayerShotAreaStats as PlayerVsPlayerShotAreaStats,
        PlayerVsPlayerShotDistanceOnOffStats as PlayerVsPlayerShotDistanceOnOffStats,
        PlayerVsPlayerShotDistanceStats as PlayerVsPlayerShotDistanceStats,
    )
    from fastbreak.models.playoff_picture import (
        PlayoffMatchup as PlayoffMatchup,
        PlayoffPictureResponse as PlayoffPictureResponse,
        PlayoffStanding as PlayoffStanding,
        RemainingGames as RemainingGames,
    )
    from fastbreak.models.schedule_league_v2 import (
        GameBroadcasters as GameBroadcasters,
        GameDate as GameDate,
        LeagueSchedule as LeagueSchedule,
        PointsLeader as PointsLeader,
        ScheduleBroadcaster as ScheduleBroadcaster,
        ScheduledGame as ScheduledGame,
        ScheduleLeagueV2Response as ScheduleLeagueV2Response,
        ScheduleTeam as ScheduleTeam,
        ScheduleWeek as ScheduleWeek,
    )
    from fastbreak.models.schedule_league_v2_int import (
        IntlBroadcasterInfo as IntlBroadcasterInfo,
        IntlGameBroadcasters as IntlGameBroadcasters,
        IntlGameDate as IntlGameDate,
        IntlLeagueSchedule as IntlLeagueSchedule,
        IntlPointsLeader as IntlPointsLeader,
        IntlScheduleBroadcaster as IntlScheduleBroadcaster,
        IntlScheduledGame as IntlScheduledGame,
        IntlScheduleTeam as IntlScheduleTeam,
        IntlScheduleWeek as IntlScheduleWeek,
        ScheduleLeagueV2IntResponse as ScheduleLeagueV2IntResponse,
    )
    from fastbreak.models.scoreboard_v3 import (
        GameLeader as GameLeader,
        GameLeaders as GameLeaders,
        PeriodScore as PeriodScore,
        Scoreboard as Scoreboard,
        ScoreboardBroadcaster as ScoreboardBroadcaster,
        ScoreboardBroadcasters as ScoreboardBroadcasters,
        ScoreboardGame as ScoreboardGame,
        ScoreboardTeam as ScoreboardTeam,
        ScoreboardV3Response as ScoreboardV3Response,
        TeamLeader as TeamLeader,
        TeamLeaders as TeamLeaders,
    )
    from fastbreak.models.shot_chart_detail import (
        LeagueAverage as LeagueAverage,
        Shot as Shot,
        ShotChartDetailResponse as ShotChartDetailResponse,
    )
    from fastbreak.models.shot_chart_leaguewide import (
        LeagueWideShotZone as LeagueWideShotZone,
        ShotChartLeaguewideResponse as ShotChartLeaguewideResponse,
    )
    from fastbreak.models.shot_chart_lineup_detail import (
        LineupLeagueAverage as LineupLeagueAverage,
        LineupShot as LineupShot,
        ShotChartLineupDetailResponse as ShotChartLineupDetailResponse,
    )
    from fastbreak.models.shot_quality_leaders import (
        ShotQualityLeader as ShotQualityLeader,
        ShotQualityLeadersResponse as ShotQualityLeadersResponse,
    )
    from fastbreak.models.synergy_playtypes import (
        PlayerSynergyPlaytype as PlayerSynergyPlaytype,
        SynergyPlaytypesResponse as SynergyPlaytypesResponse,
        TeamSynergyPlaytype as TeamSynergyPlaytype,
    )
    from fastbreak.models.team_and_players_vs_players import (
        PlayerVsPlayersStats as PlayerVsPlayersStats,
        TeamAndPlayersVsPlayersResponse as TeamAndPlayersVsPlayersResponse,
        VsPlayersStats as VsPlayersStats,
    )
    from fastbreak.models.team_dash_lineups import (
        LineupStats as LineupStats,
        TeamDashLineupsResponse as TeamDashLineupsResponse,
        TeamLineupOverall as TeamLineupOverall,
    )
    from fastbreak.models.team_dash_pt_pass import (
        TeamDashPtPassResponse as TeamDashPtPassResponse,
        TeamPassMade as TeamPassMade,
        TeamPassReceived as TeamPassReceived,
    )
    from fastbreak.models.team_dash_pt_reb import (
        TeamDashPtRebResponse as TeamDashPtRebResponse,
        TeamNumContestedRebounding as TeamNumContestedRebounding,
        TeamOverallRebounding as TeamOverallRebounding,
        TeamRebDistanceRebounding as TeamRebDistanceRebounding,
        TeamShotDistanceRebounding as TeamShotDistanceRebounding,
        TeamShotTypeRebounding as TeamShotTypeRebounding,
    )
    from fastbreak.models.team_dash_pt_shots import (
        TeamClosestDefenderStats as TeamClosestDefenderStats,
        TeamDashPtShotsResponse as TeamDashPtShotsResponse,
        TeamDribbleStats as TeamDribbleStats,
        TeamShotClockStats as TeamShotClockStats,
        TeamShotTypeStats as TeamShotTypeStats,
        TeamTouchTimeStats as TeamTouchTimeStats,
    )
    from fastbreak.models.team_dashboard_by_general_splits import (
        TeamDashboardByGeneralSplitsResponse as TeamDashboardByGeneralSplitsResponse,
        TeamSplitStats as TeamSplitStats,
    )
    from fastbreak.models.team_dashboard_by_shooting_splits import (
        TeamDashboardByShootingSplitsResponse as TeamDashboardByShootingSplitsResponse,
    )
    from fastbreak.models.team_details import (
        TeamAward as TeamAward,
        TeamBackground as TeamBackground,
        TeamDetailsResponse as TeamDetailsResponse,
        TeamHistory as TeamHistory,
        TeamHofPlayer as TeamHofPlayer,
        TeamRetiredJersey as TeamRetiredJersey,
        TeamSocialSite as TeamSocialSite,
    )
    from fastbreak.models.team_estimated_metrics import (
        TeamEstimatedMetric as TeamEstimatedMetric,
        TeamEstimatedMetricsResponse as TeamEstimatedMetricsResponse,
    )
    from fastbreak.models.team_game_log import (
        TeamGameLogEntry as TeamGameLogEntry,
        TeamGameLogResponse as TeamGameLogResponse,
    )
    from fastbreak.models.team_game_logs import (
        TeamGameLogsEntry as TeamGameLogsEntry,
        TeamGameLogsResponse as TeamGameLogsResponse,
    )
    from fastbreak.models.team_info_common import (
        TeamInfoCommon as TeamInfoCommon,
        TeamInfoCommonResponse as TeamInfoCommonResponse,
        TeamSeasonRanks as TeamSeasonRanks,
    )
    from fastbreak.models.team_player_dashboard import (
        PlayerSeasonTotals as PlayerSeasonTotals,
        TeamOverall as TeamOverall,
        TeamPlayerDashboardResponse as TeamPlayerDashboardResponse,
    )
    from fastbreak.models.team_player_on_off_details import (
        PlayerOnOffDetails as PlayerOnOffDetails,
        TeamOnOffOverall as TeamOnOffOverall,
        TeamPlayerOnOffDetailsResponse as TeamPlayerOnOffDetailsResponse,
    )
    from fastbreak.models.team_player_on_off_summary import (
        PlayerOnOffSummary as PlayerOnOffSummary,
        TeamOnOffSummaryOverall as TeamOnOffSummaryOverall,
        TeamPlayerOnOffSummaryResponse as TeamPlayerOnOffSummaryResponse,
    )
    from fastbreak.models.team_vs_player import (
        ShotAreaStats as ShotAreaStats,
        ShotDistanceStats as ShotDistanceStats,
        TeamVsPlayerOnOff as TeamVsPlayerOnOff,
        TeamVsPlayerResponse as TeamVsPlayerResponse,
        TeamVsPlayerTeamStats as TeamVsPlayerTeamStats,
        VsPlayerStats as VsPlayerStats,
    )
    from fastbreak.models.team_year_by_year_stats import (
        TeamYearByYearStatsResponse as TeamYearByYearStatsResponse,
        TeamYearStats as TeamYearStats,
    )
    from fastbreak.models.video_status import (
        GameVideoStatus as GameVideoStatus,
        VideoStatusResponse as VideoStatusResponse,
    )

# Auto-discover and import all submodules at runtime
_package_dir = Path(__file__).parent
_public_names: list[str] = ["JSON"]

# Import from common/ subpackage first
_common_module = importlib.import_module(".common", __package__)
if hasattr(_common_module, "__all__"):
    _common_names = _common_module.__all__
else:
    _common_names = [n for n in dir(_common_module) if not n.startswith("_")]
for _name in _common_names:
    if hasattr(_common_module, _name):
        globals()[_name] = getattr(_common_module, _name)
        _public_names.append(_name)

# Then import from other submodules
for _module_info in pkgutil.iter_modules([str(_package_dir)]):
    if _module_info.name.startswith("_") or _module_info.name == "common":
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
del _package_dir, _common_module, _common_names, _module_info, _module, _names, _name
del _public_names
