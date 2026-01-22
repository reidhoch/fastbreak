"""Tests for model validator early-exit (dict passthrough) behavior.

These tests cover the early-exit paths in model validators when data
is already in parsed dict form rather than raw NBA API tabular format.

The validators check `if not is_tabular_response(data): return data`
to allow models to be instantiated directly from dicts without
re-processing through the tabular parser.
"""

from fastbreak.models import (
    AllTimeLeadersResponse,
    AssistLeadersResponse,
    CommonPlayoffSeriesResponse,
    LeaderEntry,
    PlayerAssistLeader,
    PlayoffSeriesGame,
    TeamAssistLeader,
)


class TestAllTimeLeadersResponsePassthrough:
    """Tests for AllTimeLeadersResponse dict passthrough."""

    def test_from_dict_bypasses_tabular_parsing(self):
        """AllTimeLeadersResponse accepts pre-parsed dict directly."""
        # Pre-parsed dict format (not tabular resultSets format)
        data = {
            "gp_leaders": [
                {
                    "PLAYER_ID": 2544,
                    "PLAYER_NAME": "LeBron James",
                    "rank": 1,
                    "value": 1500.0,
                    "is_active": True,
                }
            ],
            "pts_leaders": [
                {
                    "PLAYER_ID": 893,
                    "PLAYER_NAME": "Michael Jordan",
                    "rank": 1,
                    "value": 30.1,
                    "is_active": False,
                }
            ],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        assert len(response.gp_leaders) == 1
        assert response.gp_leaders[0].player_name == "LeBron James"
        assert response.gp_leaders[0].is_active is True
        assert len(response.pts_leaders) == 1
        assert response.pts_leaders[0].player_name == "Michael Jordan"

    def test_from_dict_with_empty_lists(self):
        """AllTimeLeadersResponse accepts dict with empty leader lists."""
        data = {
            "gp_leaders": [],
            "pts_leaders": [],
            "ast_leaders": [],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        assert len(response.gp_leaders) == 0
        assert len(response.pts_leaders) == 0
        assert len(response.ast_leaders) == 0

    def test_from_dict_with_leader_entry_objects(self):
        """AllTimeLeadersResponse works with LeaderEntry objects directly."""
        # LeaderEntry uses aliases for PLAYER_ID and PLAYER_NAME
        entry = LeaderEntry.model_validate(
            {
                "PLAYER_ID": 2544,
                "PLAYER_NAME": "LeBron James",
                "rank": 1,
                "value": 1500.0,
                "is_active": True,
            }
        )
        data = {"gp_leaders": [entry.model_dump(by_alias=True)]}

        response = AllTimeLeadersResponse.model_validate(data)

        assert response.gp_leaders[0].player_id == 2544


class TestAssistLeadersResponsePassthrough:
    """Tests for AssistLeadersResponse dict passthrough."""

    def test_from_dict_with_team_leaders(self):
        """AssistLeadersResponse accepts pre-parsed team leaders dict."""
        data = {
            "team_leaders": [
                {
                    "RANK": 1,
                    "TEAM_ID": 1610612743,
                    "TEAM_ABBREVIATION": "DEN",
                    "TEAM_NAME": "Denver Nuggets",
                    "AST": 31.0,
                },
                {
                    "RANK": 2,
                    "TEAM_ID": 1610612737,
                    "TEAM_ABBREVIATION": "ATL",
                    "TEAM_NAME": "Atlanta Hawks",
                    "AST": 29.6,
                },
            ],
            "player_leaders": [],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert len(response.team_leaders) == 2
        assert len(response.player_leaders) == 0
        assert response.team_leaders[0].team_name == "Denver Nuggets"
        assert response.team_leaders[1].ast == 29.6

    def test_from_dict_with_player_leaders(self):
        """AssistLeadersResponse accepts pre-parsed player leaders dict."""
        data = {
            "team_leaders": [],
            "player_leaders": [
                {
                    "RANK": 1,
                    "PLAYER_ID": 1629027,
                    "PLAYER": "Trae Young",
                    "TEAM_ID": 1610612737,
                    "TEAM_ABBREVIATION": "ATL",
                    "TEAM_NAME": "Atlanta Hawks",
                    "JERSEY_NUM": "11",
                    "PLAYER_POSITION": "G",
                    "AST": 11.6,
                },
            ],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert len(response.player_leaders) == 1
        assert response.player_leaders[0].player == "Trae Young"

    def test_from_dict_with_empty_lists(self):
        """AssistLeadersResponse accepts dict with empty lists."""
        data = {
            "team_leaders": [],
            "player_leaders": [],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert len(response.team_leaders) == 0
        assert len(response.player_leaders) == 0

    def test_from_dict_with_model_objects(self):
        """AssistLeadersResponse works with model objects directly."""
        # TeamAssistLeader uses aliases for all fields
        team_entry = TeamAssistLeader.model_validate(
            {
                "RANK": 1,
                "TEAM_ID": 1610612743,
                "TEAM_ABBREVIATION": "DEN",
                "TEAM_NAME": "Denver Nuggets",
                "AST": 31.0,
            }
        )
        data = {"team_leaders": [team_entry.model_dump(by_alias=True)]}

        response = AssistLeadersResponse.model_validate(data)

        assert response.team_leaders[0].team_id == 1610612743


class TestCommonPlayoffSeriesResponsePassthrough:
    """Tests for CommonPlayoffSeriesResponse dict passthrough."""

    def test_from_dict_bypasses_tabular_parsing(self):
        """CommonPlayoffSeriesResponse accepts pre-parsed dict directly."""
        data = {
            "games": [
                {
                    "GAME_ID": "0042400101",
                    "HOME_TEAM_ID": 1610612739,
                    "VISITOR_TEAM_ID": 1610612748,
                    "SERIES_ID": "004240010",
                    "GAME_NUM": 1,
                },
                {
                    "GAME_ID": "0042400102",
                    "HOME_TEAM_ID": 1610612739,
                    "VISITOR_TEAM_ID": 1610612748,
                    "SERIES_ID": "004240010",
                    "GAME_NUM": 2,
                },
            ]
        }

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert len(response.games) == 2
        assert response.games[0].game_id == "0042400101"
        assert response.games[1].game_num == 2

    def test_from_dict_with_empty_games(self):
        """CommonPlayoffSeriesResponse accepts dict with empty games list."""
        data = {"games": []}

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert len(response.games) == 0

    def test_from_dict_with_model_objects(self):
        """CommonPlayoffSeriesResponse works with model objects directly."""
        # PlayoffSeriesGame uses aliases for all fields
        game = PlayoffSeriesGame.model_validate(
            {
                "GAME_ID": "0042400101",
                "HOME_TEAM_ID": 1610612739,
                "VISITOR_TEAM_ID": 1610612748,
                "SERIES_ID": "004240010",
                "GAME_NUM": 1,
            }
        )
        data = {"games": [game.model_dump(by_alias=True)]}

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert response.games[0].game_id == "0042400101"


class TestTabularValidatorPassthrough:
    """Tests for tabular_validator early-exit in result_set.py."""

    def test_league_standings_from_dict(self):
        """LeagueStandingsResponse accepts pre-parsed dict directly."""
        from fastbreak.models import LeagueStandingsResponse

        # Pre-parsed format with standings list directly
        data = {
            "standings": [
                {
                    "LeagueID": "00",
                    "SeasonID": "22025",
                    "TeamID": 1610612760,
                    "TeamCity": "Oklahoma City",
                    "TeamName": "Thunder",
                    "TeamSlug": "thunder",
                    "Conference": "West",
                    "ConferenceRecord": "28-6",
                    "PlayoffRank": 1,
                    "ClinchIndicator": "",
                    "Division": "Northwest",
                    "DivisionRecord": "7-2",
                    "DivisionRank": 1,
                    "WINS": 36,
                    "LOSSES": 8,
                    "WinPCT": 0.818,
                    "Record": "36-8",
                    "HOME": "20-2",
                    "ROAD": "16-5",
                    "L10": "7-3",
                    "Last10Home": "8-2",
                    "Last10Road": "6-4",
                    "OT": "3-0",
                    "ThreePTSOrLess": "2-4",
                    "TenPTSOrMore": "27-3",
                    "LongHomeStreak": 14,
                    "strLongHomeStreak": "W 14",
                    "LongRoadStreak": 8,
                    "strLongRoadStreak": "W 8",
                    "LongWinStreak": 16,
                    "LongLossStreak": 2,
                    "CurrentHomeStreak": 3,
                    "strCurrentHomeStreak": "W 3",
                    "CurrentRoadStreak": 1,
                    "strCurrentRoadStreak": "W 1",
                    "CurrentStreak": 1,
                    "strCurrentStreak": "W 1",
                    "ConferenceGamesBack": 0.0,
                    "DivisionGamesBack": 0.0,
                    "ClinchedPlayIn": 0,
                    "AheadAtHalf": "30-3",
                    "BehindAtHalf": "5-5",
                    "TiedAtHalf": "1-0",
                    "AheadAtThird": "32-2",
                    "BehindAtThird": "3-6",
                    "TiedAtThird": "1-0",
                    "Score100PTS": "33-7",
                    "OppScore100PTS": "23-8",
                    "OppOver500": "17-5",
                    "LeadInFGPCT": "28-2",
                    "LeadInReb": "26-3",
                    "FewerTurnovers": "21-4",
                    "PointsPG": 120.5,
                    "OppPointsPG": 106.3,
                    "DiffPointsPG": 14.2,
                    "vsEast": "8-2",
                    "vsAtlantic": "3-1",
                    "vsCentral": "2-1",
                    "vsSoutheast": "3-0",
                    "vsWest": "28-6",
                    "vsNorthwest": "7-2",
                    "vsPacific": "10-2",
                    "vsSouthwest": "11-2",
                    "Jan": "10-2",
                    "Feb": "0-0",
                    "Mar": "0-0",
                    "Apr": "0-0",
                    "May": "0-0",
                    "Jun": "0-0",
                    "Jul": "0-0",
                    "Aug": "0-0",
                    "Sep": "0-0",
                    "Oct": "3-0",
                    "Nov": "13-3",
                    "Dec": "10-3",
                    "Score_80_Plus": "36-8",
                    "Opp_Score_80_Plus": "35-8",
                    "Score_Below_80": "0-0",
                    "Opp_Score_Below_80": "1-0",
                    "TotalPoints": 5302,
                    "OppTotalPoints": 4677,
                    "DiffTotalPoints": 625,
                    "LeagueGamesBack": 0.0,
                    "ClinchedPostSeason": 0,
                    "NEUTRAL": "0-1",
                }
            ]
        }

        response = LeagueStandingsResponse.model_validate(data)

        assert len(response.standings) == 1
        assert response.standings[0].team_name == "Thunder"
        assert response.standings[0].wins == 36
