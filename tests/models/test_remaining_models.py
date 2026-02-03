"""Tests for remaining models - non-tabular data paths to reach 100% coverage."""

from fastbreak.models.hustle_stats_boxscore import HustleStatsBoxscoreResponse
from fastbreak.models.league_player_on_details import LeaguePlayerOnDetailsResponse
from fastbreak.models.player_compare import PlayerCompareResponse
from fastbreak.models.player_dash_pt_pass import PlayerDashPtPassResponse
from fastbreak.models.player_dash_pt_reb import PlayerDashPtRebResponse
from fastbreak.models.player_dash_pt_shot_defend import PlayerDashPtShotDefendResponse
from fastbreak.models.player_dash_pt_shots import PlayerDashPtShotsResponse
from fastbreak.models.player_dashboard_by_clutch import PlayerDashboardByClutchResponse
from fastbreak.models.player_dashboard_by_game_splits import (
    PlayerDashboardByGameSplitsResponse,
)
from fastbreak.models.player_dashboard_by_general_splits import (
    PlayerDashboardByGeneralSplitsResponse,
)
from fastbreak.models.player_dashboard_by_last_n_games import (
    PlayerDashboardByLastNGamesResponse,
)
from fastbreak.models.player_dashboard_by_shooting_splits import (
    PlayerDashboardByShootingSplitsResponse,
)
from fastbreak.models.player_dashboard_by_team_performance import (
    PlayerDashboardByTeamPerformanceResponse,
)
from fastbreak.models.player_dashboard_by_year_over_year import (
    PlayerDashboardByYearOverYearResponse,
)
from fastbreak.models.player_fantasy_profile_bar_graph import (
    PlayerFantasyProfileBarGraphResponse,
)
from fastbreak.models.player_game_log import PlayerGameLogResponse
from fastbreak.models.player_game_logs import PlayerGameLogsResponse
from fastbreak.models.player_game_streak_finder import PlayerGameStreakFinderResponse
from fastbreak.models.player_index import PlayerIndexResponse
from fastbreak.models.player_next_n_games import PlayerNextNGamesResponse
from fastbreak.models.player_profile_v2 import PlayerProfileV2Response
from fastbreak.models.player_vs_player import PlayerVsPlayerResponse
from fastbreak.models.playoff_picture import PlayoffPictureResponse
from fastbreak.models.shot_chart_detail import ShotChartDetailResponse


class TestHustleStatsBoxscoreResponse:
    def test_parse_non_tabular_data(self):
        data = {"player_stats": [], "team_stats": []}
        response = HustleStatsBoxscoreResponse.model_validate(data)
        assert response.player_stats == []


class TestLeaguePlayerOnDetailsResponse:
    def test_parse_non_tabular_data(self):
        data = {"details": []}
        response = LeaguePlayerOnDetailsResponse.model_validate(data)
        assert response.details == []


class TestPlayerCompareResponse:
    def test_parse_non_tabular_data(self):
        data = {"overall_compare": [], "individual": []}
        response = PlayerCompareResponse.model_validate(data)
        assert response.overall_compare == []


class TestPlayerDashPtPassResponse:
    def test_parse_non_tabular_data(self):
        data = {"passes_made": [], "passes_received": []}
        response = PlayerDashPtPassResponse.model_validate(data)
        assert response.passes_made == []


class TestPlayerDashPtRebResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "by_shot_type": [],
            "by_num_contested": [],
            "by_shot_distance": [],
            "by_reb_distance": [],
        }
        response = PlayerDashPtRebResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashPtShotDefendResponse:
    def test_parse_non_tabular_data(self):
        data = {"defending_shots": []}
        response = PlayerDashPtShotDefendResponse.model_validate(data)
        assert response.defending_shots == []


class TestPlayerDashPtShotsResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "general_shooting": [],
            "shot_clock_shooting": [],
            "dribble_shooting": [],
            "closest_defender_shooting": [],
            "closest_defender_10ft_plus_shooting": [],
            "touch_time_shooting": [],
        }
        response = PlayerDashPtShotsResponse.model_validate(data)
        assert response.general_shooting == []


class TestPlayerDashboardByClutchResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "last_5_min_plus_minus_5_point": [],
            "last_3_min_plus_minus_5_point": [],
            "last_1_min_plus_minus_5_point": [],
            "last_30_sec_plus_minus_5_point": [],
            "last_10_sec_plus_minus_5_point": [],
            "last_5_min_plus_minus_3_point": [],
            "last_3_min_plus_minus_3_point": [],
            "last_1_min_plus_minus_3_point": [],
        }
        response = PlayerDashboardByClutchResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashboardByGameSplitsResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "by_half": [],
            "by_period": [],
            "by_score_margin": [],
            "by_actual_margin": [],
        }
        response = PlayerDashboardByGameSplitsResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashboardByGeneralSplitsResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "by_location": [],
            "by_wins_losses": [],
            "by_month": [],
            "by_pre_post_all_star": [],
            "by_days_rest": [],
        }
        response = PlayerDashboardByGeneralSplitsResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashboardByLastNGamesResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "last_5": None,
            "last_10": None,
            "last_15": None,
            "last_20": None,
            "game_number": [],
        }
        response = PlayerDashboardByLastNGamesResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashboardByShootingSplitsResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "by_shot_distance_5ft": [],
            "by_shot_distance_8ft": [],
            "by_shot_area": [],
            "by_assisted": [],
            "by_shot_type": [],
            "assisted_by": [],
        }
        response = PlayerDashboardByShootingSplitsResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashboardByTeamPerformanceResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "by_score_differential": [],
            "by_points_scored": [],
            "by_opponent_points_scored": [],
        }
        response = PlayerDashboardByTeamPerformanceResponse.model_validate(data)
        assert response.overall is None


class TestPlayerDashboardByYearOverYearResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": None,
            "by_year": [],
        }
        response = PlayerDashboardByYearOverYearResponse.model_validate(data)
        assert response.overall is None


class TestPlayerFantasyProfileBarGraphResponse:
    def test_parse_non_tabular_data(self):
        data = {"season_avg": None, "last_five_games_avg": None}
        response = PlayerFantasyProfileBarGraphResponse.model_validate(data)
        assert response.season_avg is None


class TestPlayerGameLogResponse:
    def test_parse_non_tabular_data(self):
        data = {"games": []}
        response = PlayerGameLogResponse.model_validate(data)
        assert response.games == []


class TestPlayerGameLogsResponse:
    def test_parse_non_tabular_data(self):
        data = {"games": []}
        response = PlayerGameLogsResponse.model_validate(data)
        assert response.games == []


class TestPlayerGameStreakFinderResponse:
    def test_parse_non_tabular_data(self):
        data = {"streaks": []}
        response = PlayerGameStreakFinderResponse.model_validate(data)
        assert response.streaks == []


class TestPlayerIndexResponse:
    def test_parse_non_tabular_data(self):
        data = {"players": []}
        response = PlayerIndexResponse.model_validate(data)
        assert response.players == []


class TestPlayerNextNGamesResponse:
    def test_parse_non_tabular_data(self):
        data = {"games": []}
        response = PlayerNextNGamesResponse.model_validate(data)
        assert response.games == []


class TestPlayerProfileV2Response:
    def test_parse_non_tabular_data(self):
        data = {
            "season_totals_regular_season": [],
            "career_totals_regular_season": None,
            "season_totals_post_season": [],
            "career_totals_post_season": None,
            "season_rankings_regular_season": [],
            "season_rankings_post_season": [],
        }
        response = PlayerProfileV2Response.model_validate(data)
        assert response.season_totals_regular_season == []


class TestPlayerVsPlayerResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "overall": [],
            "on_off_court": [],
            "shot_distance_overall": [],
            "shot_distance_on_court": [],
            "shot_distance_off_court": [],
            "shot_area_overall": [],
            "shot_area_on_court": [],
            "shot_area_off_court": [],
            "player_info": [],
            "vs_player_info": [],
        }
        response = PlayerVsPlayerResponse.model_validate(data)
        assert response.overall == []


class TestPlayoffPictureResponse:
    def test_parse_non_tabular_data(self):
        data = {
            "east_conf_playoff_picture": [],
            "west_conf_playoff_picture": [],
            "east_conf_remaining_games": [],
            "west_conf_remaining_games": [],
            "east_conf_standings_by_day": [],
            "west_conf_standings_by_day": [],
        }
        response = PlayoffPictureResponse.model_validate(data)
        assert response.east_conf_playoff_picture == []


class TestShotChartDetailResponse:
    def test_parse_non_tabular_data(self):
        data = {"shots": [], "league_averages": []}
        response = ShotChartDetailResponse.model_validate(data)
        assert response.shots == []
