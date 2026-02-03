"""Tests for franchise leaders models."""

from fastbreak.models.franchise_leaders import (
    FranchiseLeader,
    FranchiseLeadersResponse,
    StatLeader,
)


class TestStatLeader:
    """Tests for StatLeader model."""

    def test_parse_stat_leader(self):
        """StatLeader parses basic data correctly."""
        leader = StatLeader(value=33643, person_id=2544, player="LeBron James")

        assert leader.value == 33643
        assert leader.person_id == 2544
        assert leader.player == "LeBron James"


class TestFranchiseLeader:
    """Tests for FranchiseLeader model."""

    def test_parse_franchise_leader(self):
        """FranchiseLeader parses nested StatLeader objects."""
        data = {
            "TEAM_ID": 1610612747,
            "pts": StatLeader(value=33643, person_id=2544, player="LeBron James"),
            "ast": StatLeader(value=10141, person_id=893, player="Magic Johnson"),
            "reb": StatLeader(value=11463, person_id=427, player="Kareem Abdul-Jabbar"),
            "blk": StatLeader(value=2694, person_id=427, player="Kareem Abdul-Jabbar"),
            "stl": StatLeader(value=1724, person_id=893, player="Magic Johnson"),
        }

        leader = FranchiseLeader.model_validate(data)

        assert leader.team_id == 1610612747
        assert leader.pts.player == "LeBron James"
        assert leader.ast.player == "Magic Johnson"
        assert leader.reb.player == "Kareem Abdul-Jabbar"


class TestFranchiseLeadersResponse:
    """Tests for FranchiseLeadersResponse model."""

    def test_parse_tabular_response(self):
        """FranchiseLeadersResponse parses tabular resultSets format."""
        data = {
            "resultSets": [
                {
                    "name": "FranchiseLeaders",
                    "headers": [
                        "TEAM_ID",
                        "PTS",
                        "PTS_PERSON_ID",
                        "PTS_PLAYER",
                        "AST",
                        "AST_PERSON_ID",
                        "AST_PLAYER",
                        "REB",
                        "REB_PERSON_ID",
                        "REB_PLAYER",
                        "BLK",
                        "BLK_PERSON_ID",
                        "BLK_PLAYER",
                        "STL",
                        "STL_PERSON_ID",
                        "STL_PLAYER",
                    ],
                    "rowSet": [
                        [
                            1610612747,
                            33643,
                            2544,
                            "LeBron James",
                            10141,
                            893,
                            "Magic Johnson",
                            11463,
                            427,
                            "Kareem Abdul-Jabbar",
                            2694,
                            427,
                            "Kareem Abdul-Jabbar",
                            1724,
                            893,
                            "Magic Johnson",
                        ],
                    ],
                }
            ]
        }

        response = FranchiseLeadersResponse.model_validate(data)

        assert len(response.leaders) == 1
        assert response.leaders[0].team_id == 1610612747
        assert response.leaders[0].pts.value == 33643
        assert response.leaders[0].pts.player == "LeBron James"
        assert response.leaders[0].ast.player == "Magic Johnson"
        assert response.leaders[0].reb.player == "Kareem Abdul-Jabbar"
        assert response.leaders[0].blk.player == "Kareem Abdul-Jabbar"
        assert response.leaders[0].stl.player == "Magic Johnson"

    def test_parse_multiple_teams(self):
        """FranchiseLeadersResponse parses multiple team records."""
        data = {
            "resultSets": [
                {
                    "name": "FranchiseLeaders",
                    "headers": [
                        "TEAM_ID",
                        "PTS",
                        "PTS_PERSON_ID",
                        "PTS_PLAYER",
                        "AST",
                        "AST_PERSON_ID",
                        "AST_PLAYER",
                        "REB",
                        "REB_PERSON_ID",
                        "REB_PLAYER",
                        "BLK",
                        "BLK_PERSON_ID",
                        "BLK_PLAYER",
                        "STL",
                        "STL_PERSON_ID",
                        "STL_PLAYER",
                    ],
                    "rowSet": [
                        [
                            1610612747,
                            33643,
                            2544,
                            "LeBron James",
                            10141,
                            893,
                            "Magic Johnson",
                            11463,
                            427,
                            "Kareem Abdul-Jabbar",
                            2694,
                            427,
                            "Kareem Abdul-Jabbar",
                            1724,
                            893,
                            "Magic Johnson",
                        ],
                        [
                            1610612738,
                            26395,
                            78049,
                            "John Havlicek",
                            4305,
                            1449,
                            "Bob Cousy",
                            21620,
                            121,
                            "Bill Russell",
                            1703,
                            121,
                            "Bill Russell",
                            1556,
                            78049,
                            "John Havlicek",
                        ],
                    ],
                }
            ]
        }

        response = FranchiseLeadersResponse.model_validate(data)

        assert len(response.leaders) == 2
        assert response.leaders[0].team_id == 1610612747
        assert response.leaders[1].team_id == 1610612738
        assert response.leaders[1].pts.player == "John Havlicek"

    def test_parse_empty_response(self):
        """FranchiseLeadersResponse handles empty result set."""
        data = {
            "resultSets": [
                {
                    "name": "FranchiseLeaders",
                    "headers": [
                        "TEAM_ID",
                        "PTS",
                        "PTS_PERSON_ID",
                        "PTS_PLAYER",
                        "AST",
                        "AST_PERSON_ID",
                        "AST_PLAYER",
                        "REB",
                        "REB_PERSON_ID",
                        "REB_PLAYER",
                        "BLK",
                        "BLK_PERSON_ID",
                        "BLK_PLAYER",
                        "STL",
                        "STL_PERSON_ID",
                        "STL_PLAYER",
                    ],
                    "rowSet": [],
                }
            ]
        }

        response = FranchiseLeadersResponse.model_validate(data)

        assert response.leaders == []

    def test_parse_non_tabular_data(self):
        """FranchiseLeadersResponse handles pre-parsed dict data."""
        data = {"leaders": []}

        response = FranchiseLeadersResponse.model_validate(data)

        assert response.leaders == []
