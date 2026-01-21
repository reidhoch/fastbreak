import pytest

from fastbreak.models import (
    AssistLeadersResponse,
    PlayerAssistLeader,
    TeamAssistLeader,
)


class TestTeamAssistLeader:
    """Tests for TeamAssistLeader model."""

    def test_parse_valid_entry(self):
        """TeamAssistLeader parses valid data."""
        data = {
            "RANK": 1,
            "TEAM_ID": 1610612743,
            "TEAM_ABBREVIATION": "DEN",
            "TEAM_NAME": "Denver Nuggets",
            "AST": 31.0,
        }

        entry = TeamAssistLeader.model_validate(data)

        assert entry.rank == 1
        assert entry.team_id == 1610612743
        assert entry.team_abbreviation == "DEN"
        assert entry.team_name == "Denver Nuggets"
        assert entry.ast == 31.0

    def test_parse_float_ast(self):
        """TeamAssistLeader handles float AST values."""
        data = {
            "RANK": 2,
            "TEAM_ID": 1610612737,
            "TEAM_ABBREVIATION": "ATL",
            "TEAM_NAME": "Atlanta Hawks",
            "AST": 29.6,
        }

        entry = TeamAssistLeader.model_validate(data)

        assert entry.ast == pytest.approx(29.6)


class TestPlayerAssistLeader:
    """Tests for PlayerAssistLeader model."""

    def test_parse_valid_entry(self):
        """PlayerAssistLeader parses valid data."""
        data = {
            "RANK": 1,
            "PLAYER_ID": 1629027,
            "PLAYER": "Trae Young",
            "TEAM_ID": 1610612737,
            "TEAM_ABBREVIATION": "ATL",
            "TEAM_NAME": "Atlanta Hawks",
            "JERSEY_NUM": "11",
            "PLAYER_POSITION": "G",
            "AST": 11.6,
        }

        entry = PlayerAssistLeader.model_validate(data)

        assert entry.rank == 1
        assert entry.player_id == 1629027
        assert entry.player == "Trae Young"
        assert entry.team_id == 1610612737
        assert entry.team_abbreviation == "ATL"
        assert entry.team_name == "Atlanta Hawks"
        assert entry.jersey_num == "11"
        assert entry.player_position == "G"
        assert entry.ast == pytest.approx(11.6)

    def test_parse_center_position(self):
        """PlayerAssistLeader handles center position."""
        data = {
            "RANK": 2,
            "PLAYER_ID": 203999,
            "PLAYER": "Nikola Jokić",
            "TEAM_ID": 1610612743,
            "TEAM_ABBREVIATION": "DEN",
            "TEAM_NAME": "Denver Nuggets",
            "JERSEY_NUM": "15",
            "PLAYER_POSITION": "C",
            "AST": 10.2,
        }

        entry = PlayerAssistLeader.model_validate(data)

        assert entry.player_position == "C"
        assert entry.player == "Nikola Jokić"


class TestAssistLeadersResponse:
    """Tests for AssistLeadersResponse model."""

    def test_parse_team_result_sets_format(self):
        """AssistLeadersResponse parses team data correctly."""
        data = {
            "resource": "assistleaders",
            "parameters": {
                "LeagueID": "00",
                "Season": "2024-25",
                "SeasonType": "Regular Season",
                "PerMode": "PerGame",
                "PlayerOrTeam": "Team",
            },
            "resultSets": [
                {
                    "name": "AssistLeaders",
                    "headers": [
                        "RANK",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "AST",
                    ],
                    "rowSet": [
                        [1, 1610612743, "DEN", "Denver Nuggets", 31.0],
                        [2, 1610612737, "ATL", "Atlanta Hawks", 29.6],
                        [3, 1610612754, "IND", "Indiana Pacers", 29.2],
                    ],
                }
            ],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert len(response.team_leaders) == 3
        assert len(response.player_leaders) == 0
        assert response.team_leaders[0].team_name == "Denver Nuggets"
        assert response.team_leaders[0].ast == 31.0
        assert response.team_leaders[1].team_abbreviation == "ATL"
        assert response.team_leaders[2].rank == 3

    def test_parse_player_result_sets_format(self):
        """AssistLeadersResponse parses player data correctly."""
        data = {
            "resource": "assistleaders",
            "parameters": {
                "LeagueID": "00",
                "Season": "2024-25",
                "SeasonType": "Regular Season",
                "PerMode": "PerGame",
                "PlayerOrTeam": "Player",
            },
            "resultSets": [
                {
                    "name": "AssistLeaders",
                    "headers": [
                        "RANK",
                        "PLAYER_ID",
                        "PLAYER",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "JERSEY_NUM",
                        "PLAYER_POSITION",
                        "AST",
                    ],
                    "rowSet": [
                        [
                            1,
                            1629027,
                            "Trae Young",
                            1610612737,
                            "ATL",
                            "Atlanta Hawks",
                            "11",
                            "G",
                            11.6,
                        ],
                        [
                            2,
                            203999,
                            "Nikola Jokić",
                            1610612743,
                            "DEN",
                            "Denver Nuggets",
                            "15",
                            "C",
                            10.2,
                        ],
                        [
                            3,
                            1630169,
                            "Tyrese Haliburton",
                            1610612754,
                            "IND",
                            "Indiana Pacers",
                            "0",
                            "G",
                            9.2,
                        ],
                    ],
                }
            ],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert len(response.player_leaders) == 3
        assert len(response.team_leaders) == 0
        assert response.player_leaders[0].player == "Trae Young"
        assert response.player_leaders[0].ast == pytest.approx(11.6)
        assert response.player_leaders[1].player == "Nikola Jokić"
        assert response.player_leaders[1].player_position == "C"
        assert response.player_leaders[2].jersey_num == "0"

    def test_handles_empty_result_set(self):
        """AssistLeadersResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "AssistLeaders",
                    "headers": [
                        "RANK",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "AST",
                    ],
                    "rowSet": [],
                }
            ],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert len(response.team_leaders) == 0
        assert len(response.player_leaders) == 0

    def test_handles_tied_ranks(self):
        """AssistLeadersResponse preserves tied rankings."""
        data = {
            "resultSets": [
                {
                    "name": "AssistLeaders",
                    "headers": [
                        "RANK",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "AST",
                    ],
                    "rowSet": [
                        [4, 1610612741, "CHI", "Chicago Bulls", 29.1],
                        [4, 1610612744, "GSW", "Golden State Warriors", 29.1],
                    ],
                }
            ],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert response.team_leaders[0].rank == 4
        assert response.team_leaders[1].rank == 4
        assert response.team_leaders[0].ast == response.team_leaders[1].ast

    def test_preserves_order_from_api(self):
        """AssistLeadersResponse maintains order from API response."""
        data = {
            "resultSets": [
                {
                    "name": "AssistLeaders",
                    "headers": [
                        "RANK",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "AST",
                    ],
                    "rowSet": [
                        [1, 1, "FIR", "First Team", 30.0],
                        [2, 2, "SEC", "Second Team", 28.0],
                        [3, 3, "THI", "Third Team", 26.0],
                    ],
                }
            ],
        }

        response = AssistLeadersResponse.model_validate(data)

        assert response.team_leaders[0].team_name == "First Team"
        assert response.team_leaders[1].team_name == "Second Team"
        assert response.team_leaders[2].team_name == "Third Team"
