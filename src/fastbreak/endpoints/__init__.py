"""NBA API endpoint definitions.

This module auto-exports all public symbols from submodules.
Runtime uses dynamic auto-discovery; TYPE_CHECKING provides static analysis support.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

# Explicit imports for type checkers (mypy, pyright, IDEs)
# These are not executed at runtime but enable autocomplete and type checking.
# The `as X` syntax explicitly marks these as public re-exports.
if TYPE_CHECKING:
    # Base classes
    # League-wide endpoints
    from fastbreak.endpoints.all_time_leaders import (
        AllTimeLeadersGrids as AllTimeLeadersGrids,
    )
    from fastbreak.endpoints.assist_leaders import AssistLeaders as AssistLeaders
    from fastbreak.endpoints.assist_tracker import AssistTracker as AssistTracker
    from fastbreak.endpoints.base import (
        DashboardEndpoint as DashboardEndpoint,
        DraftCombineEndpoint as DraftCombineEndpoint,
        Endpoint as Endpoint,
        GameIdEndpoint as GameIdEndpoint,
        PlayerDashboardEndpoint as PlayerDashboardEndpoint,
        TeamDashboardEndpoint as TeamDashboardEndpoint,
    )

    # Box score endpoints
    from fastbreak.endpoints.box_score_advanced import (
        BoxScoreAdvanced as BoxScoreAdvanced,
    )

    # V2 Box score endpoints
    from fastbreak.endpoints.box_score_defensive import (
        BoxScoreDefensive as BoxScoreDefensive,
    )
    from fastbreak.endpoints.box_score_four_factors import (
        BoxScoreFourFactors as BoxScoreFourFactors,
    )
    from fastbreak.endpoints.box_score_hustle import BoxScoreHustle as BoxScoreHustle
    from fastbreak.endpoints.box_score_matchups import (
        BoxScoreMatchups as BoxScoreMatchups,
    )
    from fastbreak.endpoints.box_score_misc import BoxScoreMisc as BoxScoreMisc
    from fastbreak.endpoints.box_score_player_track import (
        BoxScorePlayerTrack as BoxScorePlayerTrack,
    )
    from fastbreak.endpoints.box_score_scoring import BoxScoreScoring as BoxScoreScoring
    from fastbreak.endpoints.box_score_summary import BoxScoreSummary as BoxScoreSummary
    from fastbreak.endpoints.box_score_traditional import (
        BoxScoreTraditional as BoxScoreTraditional,
    )
    from fastbreak.endpoints.box_score_usage import BoxScoreUsage as BoxScoreUsage

    # V3 Box score endpoints (consolidated)
    from fastbreak.endpoints.box_scores_v3 import (
        BoxScoreAdvancedV3 as BoxScoreAdvancedV3,
        BoxScoreFourFactorsV3 as BoxScoreFourFactorsV3,
        BoxScoreMatchupsV3 as BoxScoreMatchupsV3,
        BoxScoreMiscV3 as BoxScoreMiscV3,
        BoxScorePlayerTrackV3 as BoxScorePlayerTrackV3,
        BoxScoreScoringV3 as BoxScoreScoringV3,
        BoxScoreSummaryV3 as BoxScoreSummaryV3,
        BoxScoreTraditionalV3 as BoxScoreTraditionalV3,
        BoxScoreUsageV3 as BoxScoreUsageV3,
    )

    # Common endpoints
    from fastbreak.endpoints.common_all_players import (
        CommonAllPlayers as CommonAllPlayers,
    )
    from fastbreak.endpoints.common_player_info import (
        CommonPlayerInfo as CommonPlayerInfo,
    )
    from fastbreak.endpoints.common_playoff_series import (
        CommonPlayoffSeries as CommonPlayoffSeries,
    )
    from fastbreak.endpoints.common_team_roster import (
        CommonTeamRoster as CommonTeamRoster,
    )
    from fastbreak.endpoints.common_team_years import CommonTeamYears as CommonTeamYears

    # Cumulative stats endpoints
    from fastbreak.endpoints.cume_stats_player import CumeStatsPlayer as CumeStatsPlayer
    from fastbreak.endpoints.cume_stats_player_games import (
        CumeStatsPlayerGames as CumeStatsPlayerGames,
    )
    from fastbreak.endpoints.cume_stats_team import CumeStatsTeam as CumeStatsTeam
    from fastbreak.endpoints.cume_stats_team_games import (
        CumeStatsTeamGames as CumeStatsTeamGames,
    )

    # Draft combine endpoints
    from fastbreak.endpoints.draft_combine_drill_results import (
        DraftCombineDrillResults as DraftCombineDrillResults,
    )
    from fastbreak.endpoints.draft_combine_nonstationary_shooting import (
        DraftCombineNonstationaryShooting as DraftCombineNonstationaryShooting,
    )
    from fastbreak.endpoints.draft_combine_player_anthro import (
        DraftCombinePlayerAnthro as DraftCombinePlayerAnthro,
    )
    from fastbreak.endpoints.draft_combine_spot_shooting import (
        DraftCombineSpotShooting as DraftCombineSpotShooting,
    )
    from fastbreak.endpoints.draft_combine_stats import (
        DraftCombineStats as DraftCombineStats,
    )
    from fastbreak.endpoints.draft_history import DraftHistory as DraftHistory
    from fastbreak.endpoints.dunk_score_leaders import (
        DunkScoreLeaders as DunkScoreLeaders,
    )

    # Franchise endpoints
    from fastbreak.endpoints.franchise_history import (
        FranchiseHistory as FranchiseHistory,
    )
    from fastbreak.endpoints.franchise_leaders import (
        FranchiseLeaders as FranchiseLeaders,
    )
    from fastbreak.endpoints.franchise_players import (
        FranchisePlayers as FranchisePlayers,
    )

    # Game endpoints
    from fastbreak.endpoints.game_rotation import GameRotation as GameRotation
    from fastbreak.endpoints.gravity_leaders import GravityLeaders as GravityLeaders
    from fastbreak.endpoints.homepage_leaders import (
        HomepageLeaders as HomepageLeaders,
    )
    from fastbreak.endpoints.homepage_v2 import HomepageV2 as HomepageV2
    from fastbreak.endpoints.hustle_stats_boxscore import (
        HustleStatsBoxscore as HustleStatsBoxscore,
    )

    # Player endpoints
    from fastbreak.endpoints.infographic_fanduel_player import (
        InfographicFanDuelPlayer as InfographicFanDuelPlayer,
    )

    # Schedule and scoreboard endpoints
    from fastbreak.endpoints.ist_standings import IstStandings as IstStandings
    from fastbreak.endpoints.leaders_tiles import LeadersTiles as LeadersTiles
    from fastbreak.endpoints.league_dash_lineups import (
        LeagueDashLineups as LeagueDashLineups,
    )

    # Tracking shot endpoints
    from fastbreak.endpoints.league_dash_opp_pt_shot import (
        LeagueDashOppPtShot as LeagueDashOppPtShot,
    )

    # Bio stats endpoint
    from fastbreak.endpoints.league_dash_player_bio_stats import (
        LeagueDashPlayerBioStats as LeagueDashPlayerBioStats,
    )
    from fastbreak.endpoints.league_dash_player_clutch import (
        LeagueDashPlayerClutch as LeagueDashPlayerClutch,
    )
    from fastbreak.endpoints.league_dash_player_stats import (
        LeagueDashPlayerStats as LeagueDashPlayerStats,
    )
    from fastbreak.endpoints.league_dash_pt_stats import (
        LeagueDashPtStats as LeagueDashPtStats,
    )
    from fastbreak.endpoints.league_dash_pt_team_defend import (
        LeagueDashPtTeamDefend as LeagueDashPtTeamDefend,
    )
    from fastbreak.endpoints.league_dash_team_clutch import (
        LeagueDashTeamClutch as LeagueDashTeamClutch,
    )
    from fastbreak.endpoints.league_dash_team_pt_shot import (
        LeagueDashTeamPtShot as LeagueDashTeamPtShot,
    )
    from fastbreak.endpoints.league_dash_team_shot_locations import (
        LeagueDashTeamShotLocations as LeagueDashTeamShotLocations,
    )
    from fastbreak.endpoints.league_dash_team_stats import (
        LeagueDashTeamStats as LeagueDashTeamStats,
    )
    from fastbreak.endpoints.league_game_finder import (
        LeagueGameFinder as LeagueGameFinder,
    )
    from fastbreak.endpoints.league_game_log import LeagueGameLog as LeagueGameLog
    from fastbreak.endpoints.league_hustle_stats_player import (
        LeagueHustleStatsPlayer as LeagueHustleStatsPlayer,
    )
    from fastbreak.endpoints.league_hustle_stats_team import (
        LeagueHustleStatsTeam as LeagueHustleStatsTeam,
    )
    from fastbreak.endpoints.league_leaders import LeagueLeaders as LeagueLeaders
    from fastbreak.endpoints.league_lineup_viz import LeagueLineupViz as LeagueLineupViz
    from fastbreak.endpoints.league_player_on_details import (
        LeaguePlayerOnDetails as LeaguePlayerOnDetails,
    )
    from fastbreak.endpoints.league_season_matchups import (
        LeagueSeasonMatchups as LeagueSeasonMatchups,
    )
    from fastbreak.endpoints.league_standings import LeagueStandings as LeagueStandings

    # League standings V3
    from fastbreak.endpoints.league_standings_v3 import (
        LeagueStandingsV3 as LeagueStandingsV3,
    )
    from fastbreak.endpoints.leverage_leaders import LeverageLeaders as LeverageLeaders
    from fastbreak.endpoints.matchups_rollup import MatchupsRollup as MatchupsRollup
    from fastbreak.endpoints.play_by_play import PlayByPlay as PlayByPlay
    from fastbreak.endpoints.player_awards import PlayerAwards as PlayerAwards
    from fastbreak.endpoints.player_career_by_college_rollup import (
        PlayerCareerByCollegeRollup as PlayerCareerByCollegeRollup,
    )
    from fastbreak.endpoints.player_career_stats import (
        PlayerCareerStats as PlayerCareerStats,
    )
    from fastbreak.endpoints.player_compare import PlayerCompare as PlayerCompare
    from fastbreak.endpoints.player_dash_pt_pass import (
        PlayerDashPtPass as PlayerDashPtPass,
    )
    from fastbreak.endpoints.player_dash_pt_reb import (
        PlayerDashPtReb as PlayerDashPtReb,
    )
    from fastbreak.endpoints.player_dash_pt_shot_defend import (
        PlayerDashPtShotDefend as PlayerDashPtShotDefend,
    )
    from fastbreak.endpoints.player_dash_pt_shots import (
        PlayerDashPtShots as PlayerDashPtShots,
    )

    # Player dashboard endpoints
    from fastbreak.endpoints.player_dashboard_by_clutch import (
        PlayerDashboardByClutch as PlayerDashboardByClutch,
    )
    from fastbreak.endpoints.player_dashboard_by_game_splits import (
        PlayerDashboardByGameSplits as PlayerDashboardByGameSplits,
    )
    from fastbreak.endpoints.player_dashboard_by_general_splits import (
        PlayerDashboardByGeneralSplits as PlayerDashboardByGeneralSplits,
    )
    from fastbreak.endpoints.player_dashboard_by_last_n_games import (
        PlayerDashboardByLastNGames as PlayerDashboardByLastNGames,
    )
    from fastbreak.endpoints.player_dashboard_by_shooting_splits import (
        PlayerDashboardByShootingSplits as PlayerDashboardByShootingSplits,
    )
    from fastbreak.endpoints.player_dashboard_by_team_performance import (
        PlayerDashboardByTeamPerformance as PlayerDashboardByTeamPerformance,
    )
    from fastbreak.endpoints.player_dashboard_by_year_over_year import (
        PlayerDashboardByYearOverYear as PlayerDashboardByYearOverYear,
    )
    from fastbreak.endpoints.player_estimated_metrics import (
        PlayerEstimatedMetrics as PlayerEstimatedMetrics,
    )
    from fastbreak.endpoints.player_fantasy_profile_bar_graph import (
        PlayerFantasyProfileBarGraph as PlayerFantasyProfileBarGraph,
    )
    from fastbreak.endpoints.player_game_log import PlayerGameLog as PlayerGameLog
    from fastbreak.endpoints.player_game_logs import PlayerGameLogs as PlayerGameLogs
    from fastbreak.endpoints.player_game_streak_finder import (
        PlayerGameStreakFinder as PlayerGameStreakFinder,
    )
    from fastbreak.endpoints.player_index import PlayerIndex as PlayerIndex
    from fastbreak.endpoints.player_next_n_games import (
        PlayerNextNGames as PlayerNextNGames,
    )
    from fastbreak.endpoints.player_profile_v2 import PlayerProfileV2 as PlayerProfileV2
    from fastbreak.endpoints.player_vs_player import PlayerVsPlayer as PlayerVsPlayer
    from fastbreak.endpoints.playoff_picture import PlayoffPicture as PlayoffPicture
    from fastbreak.endpoints.schedule_league_v2 import (
        ScheduleLeagueV2 as ScheduleLeagueV2,
    )
    from fastbreak.endpoints.schedule_league_v2_int import (
        ScheduleLeagueV2Int as ScheduleLeagueV2Int,
    )
    from fastbreak.endpoints.scoreboard_v3 import ScoreboardV3 as ScoreboardV3

    # Shot chart endpoints
    from fastbreak.endpoints.shot_chart_detail import ShotChartDetail as ShotChartDetail
    from fastbreak.endpoints.shot_chart_leaguewide import (
        ShotChartLeaguewide as ShotChartLeaguewide,
    )
    from fastbreak.endpoints.shot_chart_lineup_detail import (
        ShotChartLineupDetail as ShotChartLineupDetail,
    )
    from fastbreak.endpoints.shot_quality_leaders import (
        ShotQualityLeaders as ShotQualityLeaders,
    )

    # Synergy endpoints
    from fastbreak.endpoints.synergy_playtypes import (
        SynergyPlaytypes as SynergyPlaytypes,
    )

    # Team endpoints
    from fastbreak.endpoints.team_dash_lineups import TeamDashLineups as TeamDashLineups
    from fastbreak.endpoints.team_dash_pt_pass import TeamDashPtPass as TeamDashPtPass
    from fastbreak.endpoints.team_dash_pt_reb import TeamDashPtReb as TeamDashPtReb
    from fastbreak.endpoints.team_dash_pt_shots import (
        TeamDashPtShots as TeamDashPtShots,
    )
    from fastbreak.endpoints.team_dashboard_by_general_splits import (
        TeamDashboardByGeneralSplits as TeamDashboardByGeneralSplits,
    )
    from fastbreak.endpoints.team_dashboard_by_shooting_splits import (
        TeamDashboardByShootingSplits as TeamDashboardByShootingSplits,
    )
    from fastbreak.endpoints.team_details import TeamDetails as TeamDetails
    from fastbreak.endpoints.team_estimated_metrics import (
        TeamEstimatedMetrics as TeamEstimatedMetrics,
    )
    from fastbreak.endpoints.team_game_log import TeamGameLog as TeamGameLog
    from fastbreak.endpoints.team_game_logs import TeamGameLogs as TeamGameLogs
    from fastbreak.endpoints.team_info_common import TeamInfoCommon as TeamInfoCommon
    from fastbreak.endpoints.team_player_dashboard import (
        TeamPlayerDashboard as TeamPlayerDashboard,
    )
    from fastbreak.endpoints.team_player_on_off_details import (
        TeamPlayerOnOffDetails as TeamPlayerOnOffDetails,
    )
    from fastbreak.endpoints.team_player_on_off_summary import (
        TeamPlayerOnOffSummary as TeamPlayerOnOffSummary,
    )
    from fastbreak.endpoints.team_vs_player import TeamVsPlayer as TeamVsPlayer
    from fastbreak.endpoints.team_year_by_year_stats import (
        TeamYearByYearStats as TeamYearByYearStats,
    )

    # Video endpoints
    from fastbreak.endpoints.video_events import VideoEvents as VideoEvents
    from fastbreak.endpoints.video_status import VideoStatus as VideoStatus

# Auto-discover and import all submodules at runtime
_package_dir = Path(__file__).parent
_public_names: list[str] = []

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
