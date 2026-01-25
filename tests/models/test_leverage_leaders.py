"""Tests for leverage leaders models."""

import pytest

from fastbreak.models import LeverageLeader, LeverageLeadersResponse


class TestLeverageLeader:
    """Tests for LeverageLeader model."""

    @pytest.fixture
    def sample_leader_data(self) -> dict:
        """Sample leverage leader data from the API."""
        return {
            "PLAYERID": 1628983,
            "FIRSTNAME": "Shai",
            "LASTNAME": "Gilgeous-Alexander",
            "TEAMID": 1610612760,
            "TEAMABBREVIATION": "OKC",
            "TEAMNAME": "Thunder",
            "TEAMCITY": "Oklahoma City",
            "OFFENSE": 0.1845972727,
            "DEFENSE": 0.2053440909,
            "FULL": 0.3899368181,
            "SHOOTING": 0.1148425,
            "TURNOVERS": -0.0940386363,
            "REBOUNDS": 0.0432472727,
            "CREATION": 0.2041731818,
            "ONBALLDEF": 0.063093409,
            "GAMESPLAYED": 44,
            "MINUTES": 33.4,
            "PTS": 32.3,
            "REB": 4.4,
            "AST": 6.2,
        }

    def test_parse_leverage_leader(self, sample_leader_data: dict):
        """LeverageLeader parses API data correctly."""
        leader = LeverageLeader.model_validate(sample_leader_data)

        assert leader.player_id == 1628983
        assert leader.first_name == "Shai"
        assert leader.last_name == "Gilgeous-Alexander"
        assert leader.team_id == 1610612760
        assert leader.team_abbreviation == "OKC"
        assert leader.team_name == "Thunder"
        assert leader.team_city == "Oklahoma City"
        assert leader.offense == pytest.approx(0.1845972727)
        assert leader.defense == pytest.approx(0.2053440909)
        assert leader.full == pytest.approx(0.3899368181)
        assert leader.shooting == pytest.approx(0.1148425)
        assert leader.turnovers == pytest.approx(-0.0940386363)
        assert leader.rebounds == pytest.approx(0.0432472727)
        assert leader.creation == pytest.approx(0.2041731818)
        assert leader.on_ball_def == pytest.approx(0.063093409)
        assert leader.games_played == 44
        assert leader.minutes == pytest.approx(33.4)
        assert leader.pts == pytest.approx(32.3)
        assert leader.reb == pytest.approx(4.4)
        assert leader.ast == pytest.approx(6.2)


class TestLeverageLeadersResponse:
    """Tests for LeverageLeadersResponse model."""

    @pytest.fixture
    def sample_response_data(self) -> dict:
        """Sample API response with params and leaders."""
        return {
            "params": {
                "leagueId": "00",
                "seasonType": "Regular Season",
                "seasonYear": "2025-26",
            },
            "leaders": [
                {
                    "PLAYERID": 1628983,
                    "FIRSTNAME": "Shai",
                    "LASTNAME": "Gilgeous-Alexander",
                    "TEAMID": 1610612760,
                    "TEAMABBREVIATION": "OKC",
                    "TEAMNAME": "Thunder",
                    "TEAMCITY": "Oklahoma City",
                    "OFFENSE": 0.1845972727,
                    "DEFENSE": 0.2053440909,
                    "FULL": 0.3899368181,
                    "SHOOTING": 0.1148425,
                    "TURNOVERS": -0.0940386363,
                    "REBOUNDS": 0.0432472727,
                    "CREATION": 0.2041731818,
                    "ONBALLDEF": 0.063093409,
                    "GAMESPLAYED": 44,
                    "MINUTES": 33.4,
                    "PTS": 32.3,
                    "REB": 4.4,
                    "AST": 6.2,
                },
                {
                    "PLAYERID": 1630178,
                    "FIRSTNAME": "Tyrese",
                    "LASTNAME": "Maxey",
                    "TEAMID": 1610612755,
                    "TEAMABBREVIATION": "PHI",
                    "TEAMNAME": "76ers",
                    "TEAMCITY": "Philadelphia",
                    "OFFENSE": 0.0516378048,
                    "DEFENSE": 0.2569426829,
                    "FULL": 0.3085585365,
                    "SHOOTING": 0.0489714634,
                    "TURNOVERS": -0.1462239024,
                    "REBOUNDS": 0.0445158536,
                    "CREATION": 0.2066892682,
                    "ONBALLDEF": 0.0936102439,
                    "GAMESPLAYED": 41,
                    "MINUTES": 39.6,
                    "PTS": 30.1,
                    "REB": 4.3,
                    "AST": 6.8,
                },
            ],
        }

    def test_parse_response(self, sample_response_data: dict):
        """LeverageLeadersResponse parses full API response."""
        response = LeverageLeadersResponse.model_validate(sample_response_data)

        assert response.params == {
            "leagueId": "00",
            "seasonType": "Regular Season",
            "seasonYear": "2025-26",
        }
        assert len(response.leaders) == 2
        assert response.leaders[0].first_name == "Shai"
        assert response.leaders[1].first_name == "Tyrese"

    def test_parse_empty_leaders(self):
        """LeverageLeadersResponse handles empty leaders list."""
        data = {
            "params": {
                "leagueId": "00",
                "seasonType": "Playoffs",
                "seasonYear": "2025-26",
            },
            "leaders": [],
        }

        response = LeverageLeadersResponse.model_validate(data)

        assert response.params["seasonType"] == "Playoffs"
        assert response.leaders == []
