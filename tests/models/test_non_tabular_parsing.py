"""Final non-tabular data path tests to reach 100% branch coverage."""

from fastbreak.models.franchise_players import FranchisePlayersResponse
from fastbreak.models.infographic_fanduel_player import InfographicFanDuelPlayerResponse
from fastbreak.models.league_game_finder import LeagueGameFinderResponse
from fastbreak.models.league_game_log import LeagueGameLogResponse
from fastbreak.models.league_hustle_stats_player import LeagueHustleStatsPlayerResponse
from fastbreak.models.league_hustle_stats_team import LeagueHustleStatsTeamResponse
from fastbreak.models.league_lineup_viz import LeagueLineupVizResponse
from fastbreak.models.player_career_stats import PlayerCareerStatsResponse
from fastbreak.models.team_details import TeamDetailsResponse
from fastbreak.models.team_year_by_year_stats import TeamYearByYearStatsResponse


class TestFranchisePlayersNonTabular:
    """Tests for FranchisePlayersResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}
        response = FranchisePlayersResponse.model_validate(data)
        assert response.players == []


class TestInfographicFanDuelPlayerNonTabular:
    """Tests for InfographicFanDuelPlayerResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}
        response = InfographicFanDuelPlayerResponse.model_validate(data)
        assert response.players == []


class TestLeagueGameFinderNonTabular:
    """Tests for LeagueGameFinderResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"games": []}
        response = LeagueGameFinderResponse.model_validate(data)
        assert response.games == []


class TestLeagueGameLogNonTabular:
    """Tests for LeagueGameLogResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"games": []}
        response = LeagueGameLogResponse.model_validate(data)
        assert response.games == []


class TestLeagueHustleStatsPlayerNonTabular:
    """Tests for LeagueHustleStatsPlayerResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"players": []}
        response = LeagueHustleStatsPlayerResponse.model_validate(data)
        assert response.players == []


class TestLeagueHustleStatsTeamNonTabular:
    """Tests for LeagueHustleStatsTeamResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"teams": []}
        response = LeagueHustleStatsTeamResponse.model_validate(data)
        assert response.teams == []


class TestLeagueLineupVizNonTabular:
    """Tests for LeagueLineupVizResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"lineups": []}
        response = LeagueLineupVizResponse.model_validate(data)
        assert response.lineups == []


class TestPlayerCareerStatsNonTabular:
    """Tests for PlayerCareerStatsResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "season_totals_regular_season": [],
            "career_totals_regular_season": [],
            "season_totals_post_season": [],
            "career_totals_post_season": [],
            "season_totals_all_star": [],
            "career_totals_all_star": [],
            "season_totals_college": [],
            "career_totals_college": [],
            "season_totals_showcase": [],
            "career_totals_showcase": [],
            "season_rankings_regular_season": [],
            "season_rankings_post_season": [],
            "season_highs": [],
            "career_highs": [],
        }
        response = PlayerCareerStatsResponse.model_validate(data)
        assert response.season_totals_regular_season == []


class TestTeamDetailsNonTabular:
    """Tests for TeamDetailsResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {
            "background": None,
            "history": [],
            "social_sites": [],
            "championships": [],
            "conference_titles": [],
            "division_titles": [],
            "hof_players": [],
            "retired_jerseys": [],
        }
        response = TeamDetailsResponse.model_validate(data)
        assert response.history == []


class TestTeamYearByYearStatsNonTabular:
    """Tests for TeamYearByYearStatsResponse non-tabular path."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"seasons": []}
        response = TeamYearByYearStatsResponse.model_validate(data)
        assert response.seasons == []
