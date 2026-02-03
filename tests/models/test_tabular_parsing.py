"""Tests for tabular resultSets parsing paths to reach 100% branch coverage."""

from fastbreak.models.franchise_players import FranchisePlayersResponse
from fastbreak.models.infographic_fanduel_player import InfographicFanDuelPlayerResponse
from fastbreak.models.league_dash_lineups import LeagueDashLineupsResponse
from fastbreak.models.league_dash_team_shot_locations import (
    LeagueDashTeamShotLocationsResponse,
    _parse_shot_locations,
)
from fastbreak.models.league_game_finder import LeagueGameFinderResponse
from fastbreak.models.league_game_log import LeagueGameLogResponse
from fastbreak.models.league_hustle_stats_player import LeagueHustleStatsPlayerResponse
from fastbreak.models.league_hustle_stats_team import LeagueHustleStatsTeamResponse
from fastbreak.models.league_leaders import LeagueLeadersResponse
from fastbreak.models.league_lineup_viz import LeagueLineupVizResponse
from fastbreak.models.league_season_matchups import LeagueSeasonMatchupsResponse
from fastbreak.models.player_career_by_college import PlayerCareerByCollegeResponse
from fastbreak.models.player_career_by_college_rollup import (
    PlayerCareerByCollegeRollupResponse,
)
from fastbreak.models.player_career_stats import (
    PlayerCareerStatsResponse,
    SeasonRankings,
)
from fastbreak.models.shot_chart_lineup_detail import ShotChartLineupDetailResponse
from fastbreak.models.team_and_players_vs_players import (
    TeamAndPlayersVsPlayersResponse,
)
from fastbreak.models.team_dash_lineups import TeamDashLineupsResponse
from fastbreak.models.team_dash_pt_pass import TeamDashPtPassResponse
from fastbreak.models.team_dash_pt_reb import TeamDashPtRebResponse
from fastbreak.models.team_dash_pt_shots import TeamDashPtShotsResponse
from fastbreak.models.team_dashboard_by_general_splits import (
    TeamDashboardByGeneralSplitsResponse,
)
from fastbreak.models.team_dashboard_by_shooting_splits import (
    TeamDashboardByShootingSplitsResponse,
)
from fastbreak.models.team_details import TeamDetailsResponse
from fastbreak.models.team_game_log import TeamGameLogResponse
from fastbreak.models.team_game_logs import TeamGameLogsResponse
from fastbreak.models.team_info_common import TeamInfoCommonResponse
from fastbreak.models.team_player_dashboard import TeamPlayerDashboardResponse
from fastbreak.models.team_player_on_off_details import TeamPlayerOnOffDetailsResponse
from fastbreak.models.team_player_on_off_summary import TeamPlayerOnOffSummaryResponse
from fastbreak.models.team_vs_player import TeamVsPlayerResponse
from fastbreak.models.team_year_by_year_stats import TeamYearByYearStatsResponse
from fastbreak.models.video_status import VideoStatusResponse


class TestPlayerCareerByCollegeTabular:
    """Tests for PlayerCareerByCollegeResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {
                    "name": "Results",
                    "headers": ["PLAYER_ID", "PLAYER_NAME", "COLLEGE"],
                    "rowSet": [],
                }
            ]
        }
        response = PlayerCareerByCollegeResponse.model_validate(data)
        assert response.players == []


class TestPlayerCareerByCollegeRollupTabular:
    """Tests for PlayerCareerByCollegeRollupResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {
                    "name": "Results",
                    "headers": ["ORG_ID", "ORGANIZATION"],
                    "rowSet": [],
                }
            ]
        }
        response = PlayerCareerByCollegeRollupResponse.model_validate(data)
        assert response.entries == []


class TestPlayerCareerStatsTabular:
    """Tests for PlayerCareerStatsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "SeasonTotalsRegularSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsRegularSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsPostSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsPostSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsAllStarSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsAllStarSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsCollegeSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsCollegeSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsShowcaseSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsShowcaseSeason", "headers": [], "rowSet": []},
                {"name": "SeasonRankingsRegularSeason", "headers": [], "rowSet": []},
                {"name": "SeasonRankingsPostSeason", "headers": [], "rowSet": []},
                {"name": "SeasonHighs", "headers": [], "rowSet": []},
                {"name": "CareerHighs", "headers": [], "rowSet": []},
            ]
        }
        response = PlayerCareerStatsResponse.model_validate(data)
        assert response.season_totals_regular_season == []

    def test_parse_tabular_data_full(self):
        """Response parses all result sets from tabular format."""
        data = {
            "resultSets": [
                {"name": "SeasonTotalsRegularSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsRegularSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsPostSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsPostSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsAllStarSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsAllStarSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsCollegeSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsCollegeSeason", "headers": [], "rowSet": []},
                {"name": "SeasonTotalsShowcaseSeason", "headers": [], "rowSet": []},
                {"name": "CareerTotalsShowcaseSeason", "headers": [], "rowSet": []},
                {"name": "SeasonRankingsRegularSeason", "headers": [], "rowSet": []},
                {"name": "SeasonRankingsPostSeason", "headers": [], "rowSet": []},
                {"name": "SeasonHighs", "headers": [], "rowSet": []},
                {"name": "CareerHighs", "headers": [], "rowSet": []},
            ]
        }
        response = PlayerCareerStatsResponse.model_validate(data)
        assert response.season_totals_regular_season == []
        assert response.career_totals_regular_season == []
        assert response.season_highs == []
        assert response.career_highs == []


class TestShotChartLineupDetailTabular:
    """Tests for ShotChartLineupDetailResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "ShotChartLineupDetail", "headers": [], "rowSet": []},
                {"name": "ShotChartLineupLeagueAverage", "headers": [], "rowSet": []},
            ]
        }
        response = ShotChartLineupDetailResponse.model_validate(data)
        assert response.shots == []


class TestTeamAndPlayersVsPlayersTabular:
    """Tests for TeamAndPlayersVsPlayersResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "PlayersVsPlayers", "headers": [], "rowSet": []},
                {"name": "TeamPlayersVsPlayersOff", "headers": [], "rowSet": []},
                {"name": "TeamPlayersVsPlayersOn", "headers": [], "rowSet": []},
                {"name": "TeamVsPlayers", "headers": [], "rowSet": []},
                {"name": "TeamVsPlayersOff", "headers": [], "rowSet": []},
            ]
        }
        response = TeamAndPlayersVsPlayersResponse.model_validate(data)
        assert response.players_vs_players == []


class TestTeamDashLineupsTabular:
    """Tests for TeamDashLineupsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "Overall", "headers": [], "rowSet": []},
                {"name": "Lineups", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDashLineupsResponse.model_validate(data)
        assert response.lineups == []


class TestTeamDashPtPassTabular:
    """Tests for TeamDashPtPassResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "PassesMade", "headers": [], "rowSet": []},
                {"name": "PassesReceived", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDashPtPassResponse.model_validate(data)
        assert response.passes_made == []


class TestTeamDashPtRebTabular:
    """Tests for TeamDashPtRebResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "OverallRebounding", "headers": [], "rowSet": []},
                {"name": "ShotTypeRebounding", "headers": [], "rowSet": []},
                {"name": "NumContestedRebounding", "headers": [], "rowSet": []},
                {"name": "ShotDistanceRebounding", "headers": [], "rowSet": []},
                {"name": "RebDistanceRebounding", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDashPtRebResponse.model_validate(data)
        assert response.by_shot_type == []


class TestTeamDashPtShotsTabular:
    """Tests for TeamDashPtShotsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "GeneralShooting", "headers": [], "rowSet": []},
                {"name": "ShotClockShooting", "headers": [], "rowSet": []},
                {"name": "DribbleShooting", "headers": [], "rowSet": []},
                {"name": "ClosestDefenderShooting", "headers": [], "rowSet": []},
                {
                    "name": "ClosestDefender10ftPlusShooting",
                    "headers": [],
                    "rowSet": [],
                },
                {"name": "TouchTimeShooting", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDashPtShotsResponse.model_validate(data)
        assert response.general_shooting == []


class TestTeamDashboardByGeneralSplitsTabular:
    """Tests for TeamDashboardByGeneralSplitsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "OverallTeamDashboard", "headers": [], "rowSet": []},
                {"name": "LocationTeamDashboard", "headers": [], "rowSet": []},
                {"name": "WinsLossesTeamDashboard", "headers": [], "rowSet": []},
                {"name": "MonthTeamDashboard", "headers": [], "rowSet": []},
                {"name": "PrePostAllStarTeamDashboard", "headers": [], "rowSet": []},
                {"name": "DaysRestTeamDashboard", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDashboardByGeneralSplitsResponse.model_validate(data)
        assert response.by_location == []


class TestTeamDashboardByShootingSplitsTabular:
    """Tests for TeamDashboardByShootingSplitsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "OverallTeamDashboard", "headers": [], "rowSet": []},
                {"name": "Shot5FTTeamDashboard", "headers": [], "rowSet": []},
                {"name": "Shot8FTTeamDashboard", "headers": [], "rowSet": []},
                {"name": "ShotAreaTeamDashboard", "headers": [], "rowSet": []},
                {"name": "AssitedShotTeamDashboard", "headers": [], "rowSet": []},
                {"name": "ShotTypeTeamDashboard", "headers": [], "rowSet": []},
                {"name": "AssistedBy", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDashboardByShootingSplitsResponse.model_validate(data)
        assert response.overall is None


class TestTeamDetailsTabular:
    """Tests for TeamDetailsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "TeamBackground", "headers": [], "rowSet": []},
                {"name": "TeamHistory", "headers": [], "rowSet": []},
                {"name": "TeamSocialSites", "headers": [], "rowSet": []},
                {"name": "TeamAwardsChampionships", "headers": [], "rowSet": []},
                {"name": "TeamAwardsConf", "headers": [], "rowSet": []},
                {"name": "TeamAwardsDiv", "headers": [], "rowSet": []},
                {"name": "TeamHof", "headers": [], "rowSet": []},
                {"name": "TeamRetired", "headers": [], "rowSet": []},
            ]
        }
        response = TeamDetailsResponse.model_validate(data)
        assert response.history == []


class TestTeamGameLogTabular:
    """Tests for TeamGameLogResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "TeamGameLog", "headers": [], "rowSet": []},
            ]
        }
        response = TeamGameLogResponse.model_validate(data)
        assert response.games == []


class TestTeamGameLogsTabular:
    """Tests for TeamGameLogsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "TeamGameLogs", "headers": [], "rowSet": []},
            ]
        }
        response = TeamGameLogsResponse.model_validate(data)
        assert response.games == []


class TestTeamInfoCommonTabular:
    """Tests for TeamInfoCommonResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "TeamInfoCommon", "headers": [], "rowSet": []},
                {"name": "TeamSeasonRanks", "headers": [], "rowSet": []},
                {"name": "AvailableSeasons", "headers": [], "rowSet": []},
            ]
        }
        response = TeamInfoCommonResponse.model_validate(data)
        assert response.available_seasons == []


class TestTeamPlayerDashboardTabular:
    """Tests for TeamPlayerDashboardResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "TeamOverall", "headers": [], "rowSet": []},
                {"name": "PlayersSeasonTotals", "headers": [], "rowSet": []},
            ]
        }
        response = TeamPlayerDashboardResponse.model_validate(data)
        assert response.players == []


class TestTeamPlayerOnOffDetailsTabular:
    """Tests for TeamPlayerOnOffDetailsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "OverallTeamPlayerOnOffDetails", "headers": [], "rowSet": []},
                {
                    "name": "PlayersOnCourtTeamPlayerOnOffDetails",
                    "headers": [],
                    "rowSet": [],
                },
                {
                    "name": "PlayersOffCourtTeamPlayerOnOffDetails",
                    "headers": [],
                    "rowSet": [],
                },
            ]
        }
        response = TeamPlayerOnOffDetailsResponse.model_validate(data)
        assert response.players_on_court == []


class TestTeamPlayerOnOffSummaryTabular:
    """Tests for TeamPlayerOnOffSummaryResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "OverallTeamPlayerOnOffSummary", "headers": [], "rowSet": []},
                {
                    "name": "PlayersOnCourtTeamPlayerOnOffSummary",
                    "headers": [],
                    "rowSet": [],
                },
                {
                    "name": "PlayersOffCourtTeamPlayerOnOffSummary",
                    "headers": [],
                    "rowSet": [],
                },
            ]
        }
        response = TeamPlayerOnOffSummaryResponse.model_validate(data)
        assert response.players_on_court == []


class TestTeamVsPlayerTabular:
    """Tests for TeamVsPlayerResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "Overall", "headers": [], "rowSet": []},
                {"name": "vsPlayerOverall", "headers": [], "rowSet": []},
                {"name": "OnOffCourt", "headers": [], "rowSet": []},
                {"name": "ShotDistanceOverall", "headers": [], "rowSet": []},
                {"name": "ShotAreaOverall", "headers": [], "rowSet": []},
            ]
        }
        response = TeamVsPlayerResponse.model_validate(data)
        assert response.overall == []


class TestTeamYearByYearStatsTabular:
    """Tests for TeamYearByYearStatsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "TeamStats", "headers": [], "rowSet": []},
            ]
        }
        response = TeamYearByYearStatsResponse.model_validate(data)
        assert response.seasons == []

    def test_parse_tabular_with_data(self):
        """Response parses tabular resultSets format with actual data."""
        data = {
            "resultSets": [
                {
                    "name": "TeamStats",
                    "headers": [
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "YEAR",
                        "GP",
                        "WINS",
                        "LOSSES",
                        "WIN_PCT",
                        "CONF_RANK",
                        "DIV_RANK",
                        "PO_WINS",
                        "PO_LOSSES",
                        "CONF_COUNT",
                        "DIV_COUNT",
                        "NBA_FINALS_APPEARANCE",
                        "FGM",
                        "FGA",
                        "FG_PCT",
                        "FG3M",
                        "FG3A",
                        "FG3_PCT",
                        "FTM",
                        "FTA",
                        "FT_PCT",
                        "OREB",
                        "DREB",
                        "REB",
                        "AST",
                        "PF",
                        "STL",
                        "TOV",
                        "BLK",
                        "PTS",
                        "PTS_RANK",
                    ],
                    "rowSet": [],
                }
            ]
        }
        response = TeamYearByYearStatsResponse.model_validate(data)
        assert response.seasons == []


class TestVideoStatusTabular:
    """Tests for VideoStatusResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "VideoStatus", "headers": [], "rowSet": []},
            ]
        }
        response = VideoStatusResponse.model_validate(data)
        assert response.games == []


# Tests merged from test_tabular_parsing_final.py


class TestFranchisePlayersTabular:
    """Tests for FranchisePlayersResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "FranchisePlayers", "headers": [], "rowSet": []},
            ]
        }
        response = FranchisePlayersResponse.model_validate(data)
        assert response.players == []


class TestInfographicFanDuelPlayerTabular:
    """Tests for InfographicFanDuelPlayerResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "FanDuelPlayer", "headers": [], "rowSet": []},
            ]
        }
        response = InfographicFanDuelPlayerResponse.model_validate(data)
        assert response.players == []


class TestLeagueDashLineupsTabular:
    """Tests for LeagueDashLineupsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "Lineups", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueDashLineupsResponse.model_validate(data)
        assert response.lineups == []


# Tests merged from test_tabular_parsing_additional.py


class TestLeagueGameFinderTabular:
    """Tests for LeagueGameFinderResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "LeagueGameFinderResults", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueGameFinderResponse.model_validate(data)
        assert response.games == []


class TestLeagueGameLogTabular:
    """Tests for LeagueGameLogResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "LeagueGameLog", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueGameLogResponse.model_validate(data)
        assert response.games == []


class TestLeagueHustleStatsPlayerTabular:
    """Tests for LeagueHustleStatsPlayerResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "HustleStatsPlayer", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueHustleStatsPlayerResponse.model_validate(data)
        assert response.players == []


class TestLeagueHustleStatsTeamTabular:
    """Tests for LeagueHustleStatsTeamResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "HustleStatsTeam", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueHustleStatsTeamResponse.model_validate(data)
        assert response.teams == []


class TestLeagueLeadersTabular:
    """Tests for LeagueLeadersResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "LeagueLeaders", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueLeadersResponse.model_validate(data)
        assert response.leaders == []


class TestLeagueLineupVizTabular:
    """Tests for LeagueLineupVizResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "LeagueLineupViz", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueLineupVizResponse.model_validate(data)
        assert response.lineups == []


class TestLeagueSeasonMatchupsTabular:
    """Tests for LeagueSeasonMatchupsResponse tabular parsing."""

    def test_parse_tabular_data(self):
        """Response parses tabular resultSets format."""
        data = {
            "resultSets": [
                {"name": "SeasonMatchups", "headers": [], "rowSet": []},
            ]
        }
        response = LeagueSeasonMatchupsResponse.model_validate(data)
        assert response.matchups == []


class TestLeagueDashTeamShotLocationsErrorHandling:
    """Tests for LeagueDashTeamShotLocationsResponse error handling."""

    def test_parse_invalid_row_set_type(self):
        """Response handles invalid rowSet type gracefully."""
        # Create data with invalid rowSet type (string instead of list)
        data = {
            "resultSets": [
                {
                    "name": "ShotLocations",
                    "headers": ["TEAM_ID", "TEAM_NAME"],
                    "rowSet": "invalid",  # Should be a list
                }
            ]
        }
        response = LeagueDashTeamShotLocationsResponse.model_validate(data)
        assert response.teams == []

    def test_parse_shot_locations_directly_invalid_type(self):
        """_parse_shot_locations handles invalid rowSet type."""
        data = {
            "resultSets": [
                {
                    "name": "ShotLocations",
                    "headers": ["TEAM_ID"],
                    "rowSet": "not_a_list",
                }
            ]
        }
        result = _parse_shot_locations(data)
        assert result == []


class TestSeasonRankingsNRCoercion:
    """Tests for SeasonRankings NR coercion."""

    def test_coerce_nr_to_none(self):
        """SeasonRankings coerces 'NR' strings to None."""
        data = {
            "PLAYER_ID": 12345,
            "SEASON_ID": "2024-25",
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610612737,
            "TEAM_ABBREVIATION": "ATL",
            "PLAYER_AGE": "NR",  # Test NR coercion
            "GP": 10,
            "GS": 5,
            "RANK_PG_MIN": 1,
            "RANK_PG_FGM": 1,
            "RANK_PG_FGA": 1,
            "RANK_FG_PCT": 1,
            "RANK_PG_FG3M": 1,
            "RANK_PG_FG3A": 1,
            "RANK_FG3_PCT": 1,
            "RANK_PG_FTM": 1,
            "RANK_PG_FTA": 1,
            "RANK_FT_PCT": 1,
            "RANK_PG_OREB": 1,
            "RANK_PG_DREB": 1,
            "RANK_PG_REB": 1,
            "RANK_PG_AST": 1,
            "RANK_PG_STL": 1,
            "RANK_PG_BLK": 1,
            "RANK_PG_TOV": 1,
            "RANK_PG_PTS": 1,
            "RANK_PG_EFF": 1,
        }
        rankings = SeasonRankings.model_validate(data)
        assert rankings.player_age is None

    def test_normal_int_value_passes_through(self):
        """SeasonRankings passes through normal integer values."""
        data = {
            "PLAYER_ID": 12345,
            "SEASON_ID": "2024-25",
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610612737,
            "TEAM_ABBREVIATION": "ATL",
            "PLAYER_AGE": 25,  # Normal int value
            "GP": 10,
            "GS": 5,
            "RANK_PG_MIN": 1,
            "RANK_PG_FGM": 1,
            "RANK_PG_FGA": 1,
            "RANK_FG_PCT": 1,
            "RANK_PG_FG3M": 1,
            "RANK_PG_FG3A": 1,
            "RANK_FG3_PCT": 1,
            "RANK_PG_FTM": 1,
            "RANK_PG_FTA": 1,
            "RANK_FT_PCT": 1,
            "RANK_PG_OREB": 1,
            "RANK_PG_DREB": 1,
            "RANK_PG_REB": 1,
            "RANK_PG_AST": 1,
            "RANK_PG_STL": 1,
            "RANK_PG_BLK": 1,
            "RANK_PG_TOV": 1,
            "RANK_PG_PTS": 1,
            "RANK_PG_EFF": 1,
        }
        rankings = SeasonRankings.model_validate(data)
        assert rankings.player_age == 25
