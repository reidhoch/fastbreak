"""Tests for team details models."""

import pytest

from fastbreak.models import (
    TeamBackground,
    TeamDetailsResponse,
    TeamRetiredJersey,
)


class TestTeamBackground:
    """Tests for TeamBackground model."""

    @pytest.fixture
    def sample_background_data(self) -> dict:
        """Sample team background data from the API."""
        return {
            "TEAM_ID": 1610612747,
            "ABBREVIATION": "LAL",
            "NICKNAME": "Lakers",
            "YEARFOUNDED": 1948,
            "CITY": "Los Angeles",
            "ARENA": "Crypto.com Arena",
            "ARENACAPACITY": 18997,
            "OWNER": "Jeanie Buss",
            "GENERALMANAGER": "Rob Pelinka",
            "HEADCOACH": "JJ Redick",
            "DLEAGUEAFFILIATION": "South Bay Lakers",
        }

    def test_parse_background(self, sample_background_data: dict):
        """TeamBackground parses API data correctly."""
        background = TeamBackground.model_validate(sample_background_data)

        assert background.team_id == 1610612747
        assert background.abbreviation == "LAL"
        assert background.nickname == "Lakers"
        assert background.year_founded == 1948
        assert background.city == "Los Angeles"
        assert background.arena == "Crypto.com Arena"
        assert background.arena_capacity == 18997


class TestTeamRetiredJersey:
    """Tests for TeamRetiredJersey model."""

    @pytest.fixture
    def sample_retired_jersey_data(self) -> dict:
        """Sample retired jersey data for a player."""
        return {
            "PLAYERID": 893,
            "PLAYER": "Kobe Bryant",
            "POSITION": "G",
            "JERSEY": "8",
            "SEASONSWITHTEAM": "1996-2016",
            "YEAR": 2017,
        }

    def test_parse_retired_jersey(self, sample_retired_jersey_data: dict):
        """TeamRetiredJersey parses API data correctly."""
        jersey = TeamRetiredJersey.model_validate(sample_retired_jersey_data)

        assert jersey.player_id == 893
        assert jersey.player == "Kobe Bryant"
        assert jersey.position == "G"
        assert jersey.jersey == "8"
        assert jersey.seasons_with_team == "1996-2016"
        assert jersey.year == 2017

    def test_parse_retired_jersey_for_non_player(self):
        """TeamRetiredJersey handles null player_id for non-players.

        Teams sometimes retire jerseys for non-players like broadcasters,
        coaches, or owners who don't have NBA player IDs.
        """
        data = {
            "PLAYERID": None,  # Non-player (e.g., broadcaster)
            "PLAYER": "Chick Hearn",
            "POSITION": None,
            "JERSEY": "CHICK",
            "SEASONSWITHTEAM": "1961-2002",
            "YEAR": 2001,
        }

        jersey = TeamRetiredJersey.model_validate(data)

        assert jersey.player_id is None
        assert jersey.player == "Chick Hearn"
        assert jersey.jersey == "CHICK"
        assert jersey.position is None


class TestTeamDetailsResponse:
    """Tests for TeamDetailsResponse model."""

    def test_parse_tabular_response(self):
        """TeamDetailsResponse parses tabular resultSets format."""
        data = {
            "resultSets": [
                {
                    "name": "TeamBackground",
                    "headers": [
                        "TEAM_ID",
                        "ABBREVIATION",
                        "NICKNAME",
                        "YEARFOUNDED",
                        "CITY",
                        "ARENA",
                        "ARENACAPACITY",
                        "OWNER",
                        "GENERALMANAGER",
                        "HEADCOACH",
                        "DLEAGUEAFFILIATION",
                    ],
                    "rowSet": [
                        [
                            1610612747,
                            "LAL",
                            "Lakers",
                            1948,
                            "Los Angeles",
                            "Crypto.com Arena",
                            18997,
                            "Jeanie Buss",
                            "Rob Pelinka",
                            "JJ Redick",
                            "South Bay Lakers",
                        ]
                    ],
                },
                {
                    "name": "TeamHistory",
                    "headers": [
                        "TEAM_ID",
                        "CITY",
                        "NICKNAME",
                        "YEARFOUNDED",
                        "YEARACTIVETILL",
                    ],
                    "rowSet": [],
                },
                {"name": "TeamSocialSites", "headers": [], "rowSet": []},
                {"name": "TeamAwardsChampionships", "headers": [], "rowSet": []},
                {"name": "TeamAwardsConf", "headers": [], "rowSet": []},
                {"name": "TeamAwardsDiv", "headers": [], "rowSet": []},
                {"name": "TeamHof", "headers": [], "rowSet": []},
                {
                    "name": "TeamRetired",
                    "headers": [
                        "PLAYERID",
                        "PLAYER",
                        "POSITION",
                        "JERSEY",
                        "SEASONSWITHTEAM",
                        "YEAR",
                    ],
                    "rowSet": [
                        [893, "Kobe Bryant", "G", "8", "1996-2016", 2017],
                        [None, "Chick Hearn", None, "CHICK", "1961-2002", 2001],
                    ],
                },
            ]
        }

        response = TeamDetailsResponse.model_validate(data)

        assert response.background is not None
        assert response.background.nickname == "Lakers"
        assert len(response.retired_jerseys) == 2
        # Player with ID
        assert response.retired_jerseys[0].player_id == 893
        assert response.retired_jerseys[0].player == "Kobe Bryant"
        # Non-player without ID
        assert response.retired_jerseys[1].player_id is None
        assert response.retired_jerseys[1].player == "Chick Hearn"

    def test_parse_empty_response(self):
        """TeamDetailsResponse handles empty lists."""
        data = {
            "resultSets": [
                {
                    "name": "TeamBackground",
                    "headers": [
                        "TEAM_ID",
                        "ABBREVIATION",
                        "NICKNAME",
                        "YEARFOUNDED",
                        "CITY",
                        "ARENA",
                        "ARENACAPACITY",
                        "OWNER",
                        "GENERALMANAGER",
                        "HEADCOACH",
                        "DLEAGUEAFFILIATION",
                    ],
                    "rowSet": [],
                },
                {"name": "TeamHistory", "headers": [], "rowSet": []},
                {"name": "TeamSocialSites", "headers": [], "rowSet": []},
                {"name": "TeamAwardsChampionships", "headers": [], "rowSet": []},
                {"name": "TeamAwardsConf", "headers": [], "rowSet": []},
                {"name": "TeamAwardsDiv", "headers": [], "rowSet": []},
                {"name": "TeamHof", "headers": [], "rowSet": []},
                {"name": "TeamRetired", "headers": [], "rowSet": []},
            ]
        }

        response = TeamDetailsResponse.model_validate(data)

        assert response.background is None
        assert response.retired_jerseys == []
