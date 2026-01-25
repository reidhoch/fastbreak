"""Tests for shot quality leaders models."""

import pytest

from fastbreak.models import ShotQualityLeader, ShotQualityLeadersResponse


class TestShotQualityLeader:
    """Tests for ShotQualityLeader model."""

    @pytest.fixture
    def sample_leader_data(self) -> dict:
        """Sample shot quality leader data from the API."""
        return {
            "PLAYERID": 1629627,
            "FIRSTNAME": "Zion",
            "LASTNAME": "Williamson",
            "PLAYERNAME": "Zion Williamson",
            "TEAMID": 1610612740,
            "TEAMCITY": "New Orleans",
            "TEAMNAME": "Pelicans",
            "TEAMABBREVIATION": "NOP",
            "AVGSHOTQUALITY": 0.539,
            "AVGMADESHOTQUALITY": 0.606,
            "AVGMISSEDSHOTQUALITY": 0.435,
            "MINSHOTQUALITYONMAKE": 0.023,
            "AVGSHOTQUALITY2PT": 0.54,
            "AVGMADESHOTQUALITY2PT": 0.606,
            "AVGMISSEDSHOTQUALITY2PT": 0.437,
            "AVGSHOTQUALITY3PT": 0.361,
            "AVGMADESHOTQUALITY3PT": 0.0,
            "AVGMISSEDSHOTQUALITY3PT": 0.361,
            "FG2M": 253,
            "FG2M_RANK": 24,
            "FG2A": 433,
            "FG2A_RANK": 24,
            "FG3M": 0,
            "FG3M_RANK": 132,
            "FG3A": 3,
            "FG3A_RANK": 132,
            "FGM": 253,
            "FGM_RANK": 53,
            "FGA": 436,
            "FGA_RANK": 89,
            "FGPCT": 0.58,
            "FGPCTABOVEEXPECTED": 0.041,
            "FG3PCT": 0.0,
            "FG3PCTABOVEEXPECTED": -0.361,
            "AVGDEFENSIVEHANDHEIGHT": 90.661,
            "AVGDEFENDERBALLDISTANCE": 32.9,
            "AVGSHOOTERSPEED": 7.487,
            "AVGROTATIONDEGREES": 0.0,
            "AVGDEFENDERPRESSURESCORE": 0.877,
            "AVGSHOTQUALITY_RANK": 15,
            "AVGMADESHOTQUALITY_RANK": 20,
            "AVGMISSEDSHOTQUALITY_RANK": 20,
            "MINSHOTQUALITYONMAKE_RANK": 3,
            "AVGSHOTQUALITY2PT_RANK": 55,
            "AVGMADESHOTQUALITY2PT_RANK": 67,
            "AVGMISSEDSHOTQUALITY2PT_RANK": 75,
            "AVGSHOTQUALITY3PT_RANK": 65,
            "AVGMADESHOTQUALITY3PT_RANK": 132,
            "AVGMISSEDSHOTQUALITY3PT_RANK": 55,
            "FGPCT_RANK": 11,
            "FGPCTABOVEEXPECTED_RANK": 29,
            "FG3PCT_RANK": 132,
            "FG3PCTABOVEEXPECTED_RANK": 132,
            "AVGDEFENSIVEHANDHEIGHT_RANK": 16,
            "AVGDEFENDERBALLDISTANCE_RANK": 58,
            "AVGSHOOTERSPEED_RANK": 4,
            "AVGROTATIONDEGREES_RANK": 1,
            "AVGDEFENDERPRESSURESCORE_RANK": 1,
        }

    def test_parse_shot_quality_leader(self, sample_leader_data: dict):
        """ShotQualityLeader parses API data correctly."""
        leader = ShotQualityLeader.model_validate(sample_leader_data)

        # Player info
        assert leader.player_id == 1629627
        assert leader.first_name == "Zion"
        assert leader.last_name == "Williamson"
        assert leader.player_name == "Zion Williamson"
        assert leader.team_id == 1610612740
        assert leader.team_abbreviation == "NOP"

        # Shot quality metrics
        assert leader.avg_shot_quality == pytest.approx(0.539)
        assert leader.avg_made_shot_quality == pytest.approx(0.606)
        assert leader.avg_missed_shot_quality == pytest.approx(0.435)
        assert leader.min_shot_quality_on_make == pytest.approx(0.023)

        # 2PT/3PT breakdown
        assert leader.avg_shot_quality_2pt == pytest.approx(0.54)
        assert leader.avg_shot_quality_3pt == pytest.approx(0.361)

        # FG stats
        assert leader.fg2m == 253
        assert leader.fg3m == 0
        assert leader.fgm == 253
        assert leader.fga == 436
        assert leader.fg_pct == pytest.approx(0.58)
        assert leader.fg_pct_above_expected == pytest.approx(0.041)

        # Defender metrics
        assert leader.avg_defensive_hand_height == pytest.approx(90.661)
        assert leader.avg_defender_ball_distance == pytest.approx(32.9)
        assert leader.avg_shooter_speed == pytest.approx(7.487)
        assert leader.avg_defender_pressure_score == pytest.approx(0.877)

        # Ranks
        assert leader.avg_shot_quality_rank == 15
        assert leader.fg_pct_above_expected_rank == 29


class TestShotQualityLeadersResponse:
    """Tests for ShotQualityLeadersResponse model."""

    @pytest.fixture
    def sample_response_data(self) -> dict:
        """Sample API response with params and shots."""
        return {
            "params": {
                "leagueId": "00",
                "seasonType": "Regular Season",
                "seasonYear": "2025-26",
            },
            "shots": [
                {
                    "PLAYERID": 1629627,
                    "FIRSTNAME": "Zion",
                    "LASTNAME": "Williamson",
                    "PLAYERNAME": "Zion Williamson",
                    "TEAMID": 1610612740,
                    "TEAMCITY": "New Orleans",
                    "TEAMNAME": "Pelicans",
                    "TEAMABBREVIATION": "NOP",
                    "AVGSHOTQUALITY": 0.539,
                    "AVGMADESHOTQUALITY": 0.606,
                    "AVGMISSEDSHOTQUALITY": 0.435,
                    "MINSHOTQUALITYONMAKE": 0.023,
                    "AVGSHOTQUALITY2PT": 0.54,
                    "AVGMADESHOTQUALITY2PT": 0.606,
                    "AVGMISSEDSHOTQUALITY2PT": 0.437,
                    "AVGSHOTQUALITY3PT": 0.361,
                    "AVGMADESHOTQUALITY3PT": 0.0,
                    "AVGMISSEDSHOTQUALITY3PT": 0.361,
                    "FG2M": 253,
                    "FG2M_RANK": 24,
                    "FG2A": 433,
                    "FG2A_RANK": 24,
                    "FG3M": 0,
                    "FG3M_RANK": 132,
                    "FG3A": 3,
                    "FG3A_RANK": 132,
                    "FGM": 253,
                    "FGM_RANK": 53,
                    "FGA": 436,
                    "FGA_RANK": 89,
                    "FGPCT": 0.58,
                    "FGPCTABOVEEXPECTED": 0.041,
                    "FG3PCT": 0.0,
                    "FG3PCTABOVEEXPECTED": -0.361,
                    "AVGDEFENSIVEHANDHEIGHT": 90.661,
                    "AVGDEFENDERBALLDISTANCE": 32.9,
                    "AVGSHOOTERSPEED": 7.487,
                    "AVGROTATIONDEGREES": 0.0,
                    "AVGDEFENDERPRESSURESCORE": 0.877,
                    "AVGSHOTQUALITY_RANK": 15,
                    "AVGMADESHOTQUALITY_RANK": 20,
                    "AVGMISSEDSHOTQUALITY_RANK": 20,
                    "MINSHOTQUALITYONMAKE_RANK": 3,
                    "AVGSHOTQUALITY2PT_RANK": 55,
                    "AVGMADESHOTQUALITY2PT_RANK": 67,
                    "AVGMISSEDSHOTQUALITY2PT_RANK": 75,
                    "AVGSHOTQUALITY3PT_RANK": 65,
                    "AVGMADESHOTQUALITY3PT_RANK": 132,
                    "AVGMISSEDSHOTQUALITY3PT_RANK": 55,
                    "FGPCT_RANK": 11,
                    "FGPCTABOVEEXPECTED_RANK": 29,
                    "FG3PCT_RANK": 132,
                    "FG3PCTABOVEEXPECTED_RANK": 132,
                    "AVGDEFENSIVEHANDHEIGHT_RANK": 16,
                    "AVGDEFENDERBALLDISTANCE_RANK": 58,
                    "AVGSHOOTERSPEED_RANK": 4,
                    "AVGROTATIONDEGREES_RANK": 1,
                    "AVGDEFENDERPRESSURESCORE_RANK": 1,
                },
            ],
        }

    def test_parse_response(self, sample_response_data: dict):
        """ShotQualityLeadersResponse parses full API response."""
        response = ShotQualityLeadersResponse.model_validate(sample_response_data)

        assert response.params == {
            "leagueId": "00",
            "seasonType": "Regular Season",
            "seasonYear": "2025-26",
        }
        assert len(response.shots) == 1
        assert response.shots[0].first_name == "Zion"
        assert response.shots[0].last_name == "Williamson"

    def test_parse_empty_shots(self):
        """ShotQualityLeadersResponse handles empty shots list."""
        data = {
            "params": {
                "leagueId": "00",
                "seasonType": "Playoffs",
                "seasonYear": "2025-26",
            },
            "shots": [],
        }

        response = ShotQualityLeadersResponse.model_validate(data)

        assert response.params["seasonType"] == "Playoffs"
        assert response.shots == []
