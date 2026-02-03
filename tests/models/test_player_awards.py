"""Tests for player awards models."""

from fastbreak.models.player_awards import (
    PlayerAward,
    PlayerAwardsResponse,
)


class TestPlayerAward:
    """Tests for PlayerAward model."""

    def test_parse_award(self):
        """PlayerAward parses API data correctly."""
        data = {
            "PERSON_ID": 2544,
            "FIRST_NAME": "LeBron",
            "LAST_NAME": "James",
            "TEAM": "Los Angeles Lakers",
            "DESCRIPTION": "All-NBA First Team",
            "ALL_NBA_TEAM_NUMBER": "1",
            "SEASON": "2023-24",
            "MONTH": None,
            "WEEK": None,
            "CONFERENCE": "West",
            "TYPE": "All-NBA",
            "SUBTYPE1": "First Team",
            "SUBTYPE2": None,
            "SUBTYPE3": None,
        }

        award = PlayerAward.model_validate(data)

        assert award.person_id == 2544
        assert award.first_name == "LeBron"
        assert award.last_name == "James"
        assert award.description == "All-NBA First Team"
        assert award.season == "2023-24"
        assert award.type == "All-NBA"


class TestPlayerAwardsResponse:
    """Tests for PlayerAwardsResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "PlayerAwards",
                    "headers": [
                        "PERSON_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "TEAM",
                        "DESCRIPTION",
                        "ALL_NBA_TEAM_NUMBER",
                        "SEASON",
                        "MONTH",
                        "WEEK",
                        "CONFERENCE",
                        "TYPE",
                        "SUBTYPE1",
                        "SUBTYPE2",
                        "SUBTYPE3",
                    ],
                    "rowSet": [
                        [
                            2544,
                            "LeBron",
                            "James",
                            "Lakers",
                            "MVP",
                            None,
                            "2023-24",
                            None,
                            None,
                            "West",
                            "MVP",
                            None,
                            None,
                            None,
                        ],
                        [
                            2544,
                            "LeBron",
                            "James",
                            "Lakers",
                            "All-NBA First Team",
                            "1",
                            "2023-24",
                            None,
                            None,
                            "West",
                            "All-NBA",
                            "First Team",
                            None,
                            None,
                        ],
                    ],
                }
            ]
        }

        response = PlayerAwardsResponse.model_validate(data)

        assert len(response.awards) == 2
        assert response.awards[0].description == "MVP"
        assert response.awards[1].description == "All-NBA First Team"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "PlayerAwards",
                    "headers": ["PERSON_ID"],
                    "rowSet": [],
                }
            ]
        }

        response = PlayerAwardsResponse.model_validate(data)

        assert response.awards == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"awards": []}

        response = PlayerAwardsResponse.model_validate(data)

        assert response.awards == []
