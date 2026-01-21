from fastbreak.models import AssistTrackerResponse


class TestAssistTrackerResponse:
    """Tests for AssistTrackerResponse model."""

    def test_parse_result_sets_format(self):
        """AssistTrackerResponse parses tabular resultSets format."""
        data = {
            "resource": "assisttracker",
            "parameters": {
                "LeagueID": "00",
                "Season": "2024-25",
                "SeasonType": "Regular Season",
                "PerMode": "Per36",
            },
            "resultSets": [
                {
                    "name": "AssistTracker",
                    "headers": ["ASSISTS"],
                    "rowSet": [[69114]],
                }
            ],
        }

        response = AssistTrackerResponse.model_validate(data)

        assert response.assists == 69114

    def test_parse_smaller_value(self):
        """AssistTrackerResponse parses smaller assist counts."""
        data = {
            "resultSets": [
                {
                    "name": "AssistTracker",
                    "headers": ["ASSISTS"],
                    "rowSet": [[1234]],
                }
            ],
        }

        response = AssistTrackerResponse.model_validate(data)

        assert response.assists == 1234

    def test_handles_empty_result_set(self):
        """AssistTrackerResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "AssistTracker",
                    "headers": ["ASSISTS"],
                    "rowSet": [],
                }
            ],
        }

        response = AssistTrackerResponse.model_validate(data)

        assert response.assists == 0

    def test_handles_zero_assists(self):
        """AssistTrackerResponse handles zero assists."""
        data = {
            "resultSets": [
                {
                    "name": "AssistTracker",
                    "headers": ["ASSISTS"],
                    "rowSet": [[0]],
                }
            ],
        }

        response = AssistTrackerResponse.model_validate(data)

        assert response.assists == 0

    def test_parse_direct_dict(self):
        """AssistTrackerResponse parses direct dict format."""
        data = {"assists": 5000}

        response = AssistTrackerResponse.model_validate(data)

        assert response.assists == 5000
