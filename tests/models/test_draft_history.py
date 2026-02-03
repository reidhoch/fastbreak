"""Tests for draft history models."""

from fastbreak.models.draft_history import (
    DraftHistoryResponse,
    DraftPick,
)


class TestDraftPick:
    """Tests for DraftPick model."""

    def test_parse_draft_pick(self):
        """DraftPick parses API data correctly."""
        data = {
            "PERSON_ID": 203999,
            "PLAYER_NAME": "Zion Williamson",
            "SEASON": "2019",
            "ROUND_NUMBER": 1,
            "ROUND_PICK": 1,
            "OVERALL_PICK": 1,
            "DRAFT_TYPE": "Draft",
            "TEAM_ID": 1610612740,
            "TEAM_CITY": "New Orleans",
            "TEAM_NAME": "Pelicans",
            "TEAM_ABBREVIATION": "NOP",
            "ORGANIZATION": "Duke",
            "ORGANIZATION_TYPE": "College/University",
            "PLAYER_PROFILE_FLAG": 1,
        }

        pick = DraftPick.model_validate(data)

        assert pick.person_id == 203999
        assert pick.player_name == "Zion Williamson"
        assert pick.season == "2019"
        assert pick.round_number == 1
        assert pick.overall_pick == 1
        assert pick.organization == "Duke"


class TestDraftHistoryResponse:
    """Tests for DraftHistoryResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "DraftHistory",
                    "headers": [
                        "PERSON_ID",
                        "PLAYER_NAME",
                        "SEASON",
                        "ROUND_NUMBER",
                        "ROUND_PICK",
                        "OVERALL_PICK",
                        "DRAFT_TYPE",
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "TEAM_ABBREVIATION",
                        "ORGANIZATION",
                        "ORGANIZATION_TYPE",
                        "PLAYER_PROFILE_FLAG",
                    ],
                    "rowSet": [
                        [
                            203999,
                            "Zion Williamson",
                            "2019",
                            1,
                            1,
                            1,
                            "Draft",
                            1610612740,
                            "New Orleans",
                            "Pelicans",
                            "NOP",
                            "Duke",
                            "College/University",
                            1,
                        ],
                        [
                            1629630,
                            "Ja Morant",
                            "2019",
                            1,
                            2,
                            2,
                            "Draft",
                            1610612763,
                            "Memphis",
                            "Grizzlies",
                            "MEM",
                            "Murray State",
                            "College/University",
                            1,
                        ],
                    ],
                }
            ]
        }

        response = DraftHistoryResponse.model_validate(data)

        assert len(response.picks) == 2
        assert response.picks[0].player_name == "Zion Williamson"
        assert response.picks[1].player_name == "Ja Morant"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "DraftHistory",
                    "headers": ["PERSON_ID"],
                    "rowSet": [],
                }
            ]
        }

        response = DraftHistoryResponse.model_validate(data)

        assert response.picks == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"picks": []}

        response = DraftHistoryResponse.model_validate(data)

        assert response.picks == []
