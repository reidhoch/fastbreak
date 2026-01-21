from fastbreak.models import CommonTeamYearsResponse, TeamYear


class TestTeamYear:
    """Tests for TeamYear model."""

    def test_parse_active_team(self):
        """TeamYear parses active team data."""
        data = {
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610612745,
            "MIN_YEAR": "1967",
            "MAX_YEAR": "2025",
            "ABBREVIATION": "HOU",
        }

        team = TeamYear.model_validate(data)

        assert team.league_id == "00"
        assert team.team_id == 1610612745
        assert team.min_year == "1967"
        assert team.max_year == "2025"
        assert team.abbreviation == "HOU"

    def test_parse_defunct_team(self):
        """TeamYear handles defunct teams with null abbreviation."""
        data = {
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610610023,
            "MIN_YEAR": "1949",
            "MAX_YEAR": "1949",
            "ABBREVIATION": None,
        }

        team = TeamYear.model_validate(data)

        assert team.team_id == 1610610023
        assert team.min_year == "1949"
        assert team.max_year == "1949"
        assert team.abbreviation is None

    def test_parse_long_running_franchise(self):
        """TeamYear handles franchises with long history."""
        data = {
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610612738,
            "MIN_YEAR": "1946",
            "MAX_YEAR": "2025",
            "ABBREVIATION": "BOS",
        }

        team = TeamYear.model_validate(data)

        assert team.abbreviation == "BOS"
        assert team.min_year == "1946"


class TestCommonTeamYearsResponse:
    """Tests for CommonTeamYearsResponse model."""

    def test_parse_result_sets_format(self):
        """CommonTeamYearsResponse parses tabular data correctly."""
        data = {
            "resource": "commonteamyears",
            "parameters": {"LeagueID": "00"},
            "resultSets": [
                {
                    "name": "TeamYears",
                    "headers": [
                        "LEAGUE_ID",
                        "TEAM_ID",
                        "MIN_YEAR",
                        "MAX_YEAR",
                        "ABBREVIATION",
                    ],
                    "rowSet": [
                        ["00", 1610612745, "1967", "2025", "HOU"],
                        ["00", 1610612747, "1948", "2025", "LAL"],
                        ["00", 1610610023, "1949", "1949", None],
                    ],
                }
            ],
        }

        response = CommonTeamYearsResponse.model_validate(data)

        assert len(response.teams) == 3
        assert response.teams[0].abbreviation == "HOU"
        assert response.teams[1].abbreviation == "LAL"
        assert response.teams[2].abbreviation is None

    def test_handles_empty_result_set(self):
        """CommonTeamYearsResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "TeamYears",
                    "headers": [
                        "LEAGUE_ID",
                        "TEAM_ID",
                        "MIN_YEAR",
                        "MAX_YEAR",
                        "ABBREVIATION",
                    ],
                    "rowSet": [],
                }
            ],
        }

        response = CommonTeamYearsResponse.model_validate(data)

        assert len(response.teams) == 0

    def test_preserves_order_from_api(self):
        """CommonTeamYearsResponse maintains order from API response."""
        data = {
            "resultSets": [
                {
                    "name": "TeamYears",
                    "headers": [
                        "LEAGUE_ID",
                        "TEAM_ID",
                        "MIN_YEAR",
                        "MAX_YEAR",
                        "ABBREVIATION",
                    ],
                    "rowSet": [
                        ["00", 1610612738, "1946", "2025", "BOS"],
                        ["00", 1610612747, "1948", "2025", "LAL"],
                        ["00", 1610612744, "1946", "2025", "GSW"],
                    ],
                }
            ],
        }

        response = CommonTeamYearsResponse.model_validate(data)

        assert response.teams[0].abbreviation == "BOS"
        assert response.teams[1].abbreviation == "LAL"
        assert response.teams[2].abbreviation == "GSW"

    def test_mixed_active_and_defunct_teams(self):
        """CommonTeamYearsResponse handles mix of active and defunct teams."""
        data = {
            "resultSets": [
                {
                    "name": "TeamYears",
                    "headers": [
                        "LEAGUE_ID",
                        "TEAM_ID",
                        "MIN_YEAR",
                        "MAX_YEAR",
                        "ABBREVIATION",
                    ],
                    "rowSet": [
                        ["00", 1610610024, "1947", "1954", None],
                        ["00", 1610612752, "1946", "2025", "NYK"],
                        ["00", 1610610026, "1946", "1946", None],
                    ],
                }
            ],
        }

        response = CommonTeamYearsResponse.model_validate(data)

        active = [t for t in response.teams if t.abbreviation is not None]
        defunct = [t for t in response.teams if t.abbreviation is None]
        assert len(active) == 1
        assert len(defunct) == 2
