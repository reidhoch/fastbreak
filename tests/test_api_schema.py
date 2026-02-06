"""Live API schema validation tests.

These tests hit the actual NBA API to detect when the API schema changes
(new fields added). Run with: pytest -m live_api

By default, these tests are skipped in regular test runs.
"""

import pytest

from fastbreak.clients.nba import NBAClient
from fastbreak.endpoints import (  # No required params (39 endpoints); game_id required (13 endpoints); player_id required (22 endpoints); team_id required (26 endpoints); Special cases
    AllTimeLeadersGrids,
    AssistLeaders,
    AssistTracker,
    BoxScoreAdvanced,
    BoxScoreFourFactors,
    BoxScoreMatchups,
    BoxScoreMisc,
    BoxScorePlayerTrack,
    BoxScoreScoring,
    BoxScoreSummary,
    BoxScoreTraditional,
    BoxScoreUsage,
    CommonAllPlayers,
    CommonPlayerInfo,
    CommonPlayoffSeries,
    CommonTeamRoster,
    CommonTeamYears,
    CumeStatsPlayer,
    CumeStatsPlayerGames,
    CumeStatsTeam,
    CumeStatsTeamGames,
    DraftCombineDrillResults,
    DraftCombineNonstationaryShooting,
    DraftCombinePlayerAnthro,
    DraftCombineSpotShooting,
    DraftCombineStats,
    DraftHistory,
    DunkScoreLeaders,
    FranchiseHistory,
    FranchiseLeaders,
    FranchisePlayers,
    GameRotation,
    GravityLeaders,
    HustleStatsBoxscore,
    InfographicFanDuelPlayer,
    IstStandings,
    LeagueDashLineups,
    LeagueDashPtStats,
    LeagueDashTeamClutch,
    LeagueDashTeamShotLocations,
    LeagueGameFinder,
    LeagueGameLog,
    LeagueHustleStatsPlayer,
    LeagueHustleStatsTeam,
    LeagueLeaders,
    LeagueLineupViz,
    LeaguePlayerOnDetails,
    LeagueSeasonMatchups,
    LeagueStandings,
    LeverageLeaders,
    MatchupsRollup,
    PlayByPlay,
    PlayerAwards,
    PlayerCareerByCollege,
    PlayerCareerByCollegeRollup,
    PlayerCareerStats,
    PlayerCompare,
    PlayerDashboardByClutch,
    PlayerDashboardByGameSplits,
    PlayerDashboardByGeneralSplits,
    PlayerDashboardByLastNGames,
    PlayerDashboardByShootingSplits,
    PlayerDashboardByTeamPerformance,
    PlayerDashboardByYearOverYear,
    PlayerDashPtPass,
    PlayerDashPtReb,
    PlayerDashPtShotDefend,
    PlayerDashPtShots,
    PlayerEstimatedMetrics,
    PlayerFantasyProfileBarGraph,
    PlayerGameLog,
    PlayerGameLogs,
    PlayerGameStreakFinder,
    PlayerIndex,
    PlayerNextNGames,
    PlayerProfileV2,
    PlayerVsPlayer,
    PlayoffPicture,
    ScheduleLeagueV2,
    ScheduleLeagueV2Int,
    ScoreboardV3,
    ShotChartDetail,
    ShotChartLeaguewide,
    ShotChartLineupDetail,
    ShotQualityLeaders,
    SynergyPlaytypes,
    TeamAndPlayersVsPlayers,
    TeamDashboardByGeneralSplits,
    TeamDashboardByShootingSplits,
    TeamDashLineups,
    TeamDashPtPass,
    TeamDashPtReb,
    TeamDashPtShots,
    TeamDetails,
    TeamEstimatedMetrics,
    TeamGameLog,
    TeamGameLogs,
    TeamInfoCommon,
    TeamPlayerDashboard,
    TeamPlayerOnOffDetails,
    TeamPlayerOnOffSummary,
    TeamVsPlayer,
    TeamYearByYearStats,
    VideoStatus,
)
from fastbreak.models.common.response import FrozenResponse

# Sample IDs for testing
GAME_ID = "0022400001"  # First game of 2024-25 season
PLAYER_ID = 2544  # LeBron James
PLAYER_ID_2 = 201566  # Demarcus Cousins (for vs comparisons)
TEAM_ID = 1610612747  # Lakers
TEAM_ID_2 = 1610612744  # Warriors (for vs comparisons)
COLLEGE = "Duke"


def get_strict_response_model(endpoint):
    """Get the strict version of an endpoint's response model."""
    response_model = endpoint.response_model
    if issubclass(response_model, FrozenResponse):
        return response_model.strict()
    return response_model


# =============================================================================
# Endpoints with no required parameters (39 endpoints)
# =============================================================================
NO_PARAMS_ENDPOINTS = [
    AllTimeLeadersGrids,
    AssistLeaders,
    AssistTracker,
    CommonAllPlayers,
    CommonPlayoffSeries,
    CommonTeamYears,
    DraftCombineDrillResults,
    DraftCombineNonstationaryShooting,
    DraftCombinePlayerAnthro,
    DraftCombineSpotShooting,
    DraftCombineStats,
    DraftHistory,
    DunkScoreLeaders,
    FranchiseHistory,
    GravityLeaders,
    IstStandings,
    LeagueDashTeamClutch,
    LeagueGameFinder,
    LeagueGameLog,
    LeagueHustleStatsPlayer,
    LeagueHustleStatsTeam,
    LeagueLeaders,
    LeagueSeasonMatchups,
    LeagueStandings,
    LeverageLeaders,
    MatchupsRollup,
    PlayerCareerByCollegeRollup,
    PlayerCompare,
    PlayerEstimatedMetrics,
    PlayerIndex,
    PlayoffPicture,
    ScheduleLeagueV2,
    ScheduleLeagueV2Int,
    ScoreboardV3,
    ShotChartLeaguewide,
    ShotQualityLeaders,
    SynergyPlaytypes,
    TeamEstimatedMetrics,
    VideoStatus,
]

# =============================================================================
# Endpoints requiring game_id (13 endpoints)
# =============================================================================
GAME_ID_ENDPOINTS = [
    BoxScoreAdvanced,
    BoxScoreFourFactors,
    BoxScoreMatchups,
    BoxScoreMisc,
    BoxScorePlayerTrack,
    BoxScoreScoring,
    BoxScoreSummary,
    BoxScoreTraditional,
    BoxScoreUsage,
    GameRotation,
    HustleStatsBoxscore,
    InfographicFanDuelPlayer,
    PlayByPlay,
]

# =============================================================================
# Endpoints requiring player_id (22 endpoints)
# =============================================================================
PLAYER_ID_ENDPOINTS = [
    CommonPlayerInfo,
    CumeStatsPlayer,
    CumeStatsPlayerGames,
    PlayerAwards,
    PlayerCareerStats,
    PlayerDashPtPass,
    PlayerDashPtReb,
    PlayerDashPtShotDefend,
    PlayerDashPtShots,
    PlayerDashboardByClutch,
    PlayerDashboardByGameSplits,
    PlayerDashboardByGeneralSplits,
    PlayerDashboardByLastNGames,
    PlayerDashboardByShootingSplits,
    PlayerDashboardByTeamPerformance,
    PlayerDashboardByYearOverYear,
    PlayerFantasyProfileBarGraph,
    PlayerGameLog,
    PlayerGameLogs,
    PlayerGameStreakFinder,
    PlayerNextNGames,
    PlayerProfileV2,
]

# =============================================================================
# Endpoints requiring team_id (26 endpoints)
# =============================================================================
TEAM_ID_ENDPOINTS = [
    CommonTeamRoster,
    CumeStatsTeam,
    CumeStatsTeamGames,
    FranchiseLeaders,
    FranchisePlayers,
    LeagueDashLineups,
    LeagueDashPtStats,
    LeagueDashTeamShotLocations,
    LeagueLineupViz,
    LeaguePlayerOnDetails,
    ShotChartDetail,
    ShotChartLineupDetail,
    TeamDashLineups,
    TeamDashPtPass,
    TeamDashPtReb,
    TeamDashPtShots,
    TeamDashboardByGeneralSplits,
    TeamDashboardByShootingSplits,
    TeamDetails,
    TeamGameLog,
    TeamGameLogs,
    TeamInfoCommon,
    TeamPlayerDashboard,
    TeamPlayerOnOffDetails,
    TeamPlayerOnOffSummary,
    TeamYearByYearStats,
]


@pytest.mark.live_api
class TestApiSchemaUnchanged:
    """Validate that API responses match our models.

    These tests detect when the NBA API adds new fields that our models
    don't capture. Run periodically to stay up-to-date with API changes.

    Total: 104 endpoints covered.
    """

    @pytest.mark.parametrize("endpoint_class", NO_PARAMS_ENDPOINTS)
    async def test_no_params_endpoint_schema(self, endpoint_class):
        """Test endpoints that don't require specific IDs (39 endpoints)."""
        async with NBAClient() as client:
            endpoint = endpoint_class()
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    @pytest.mark.parametrize("endpoint_class", GAME_ID_ENDPOINTS)
    async def test_game_id_endpoint_schema(self, endpoint_class):
        """Test endpoints requiring game_id (13 endpoints)."""
        async with NBAClient() as client:
            endpoint = endpoint_class(game_id=GAME_ID)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    @pytest.mark.parametrize("endpoint_class", PLAYER_ID_ENDPOINTS)
    async def test_player_id_endpoint_schema(self, endpoint_class):
        """Test endpoints requiring player_id (22 endpoints)."""
        async with NBAClient() as client:
            endpoint = endpoint_class(player_id=PLAYER_ID)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    @pytest.mark.parametrize("endpoint_class", TEAM_ID_ENDPOINTS)
    async def test_team_id_endpoint_schema(self, endpoint_class):
        """Test endpoints requiring team_id (26 endpoints)."""
        async with NBAClient() as client:
            endpoint = endpoint_class(team_id=TEAM_ID)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    async def test_college_endpoint_schema(self):
        """Test PlayerCareerByCollege endpoint (requires college)."""
        async with NBAClient() as client:
            endpoint = PlayerCareerByCollege(college=COLLEGE)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    async def test_player_vs_player_schema(self):
        """Test PlayerVsPlayer endpoint (requires player_id and vs_player_id)."""
        async with NBAClient() as client:
            endpoint = PlayerVsPlayer(player_id=PLAYER_ID, vs_player_id=PLAYER_ID_2)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    async def test_team_vs_player_schema(self):
        """Test TeamVsPlayer endpoint (requires team_id and vs_player_id)."""
        async with NBAClient() as client:
            endpoint = TeamVsPlayer(team_id=TEAM_ID, vs_player_id=PLAYER_ID_2)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())

    async def test_team_and_players_vs_players_schema(self):
        """Test TeamAndPlayersVsPlayers endpoint (requires team_id and vs_team_id)."""
        async with NBAClient() as client:
            endpoint = TeamAndPlayersVsPlayers(team_id=TEAM_ID, vs_team_id=TEAM_ID_2)
            response = await client.get(endpoint)

            StrictModel = get_strict_response_model(endpoint)
            StrictModel.model_validate(response.model_dump())
