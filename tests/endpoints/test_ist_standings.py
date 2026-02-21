"""Tests for IstStandings endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import IstStandings
from fastbreak.models import IstStandingsResponse
from fastbreak.utils import get_season_from_date


class TestIstStandings:
    """Tests for IstStandings endpoint."""

    def test_init_with_defaults(self):
        """IstStandings uses sensible defaults."""
        endpoint = IstStandings()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.section == "group"

    def test_init_with_custom_season(self):
        """IstStandings accepts custom season."""
        endpoint = IstStandings(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_section(self):
        """IstStandings accepts custom section."""
        endpoint = IstStandings(section="wildcard")

        assert endpoint.section == "wildcard"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = IstStandings(
            league_id="00",
            season="2024-25",
            section="group",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "Section": "group",
        }

    def test_path_is_correct(self):
        """IstStandings has correct API path."""
        endpoint = IstStandings()

        assert endpoint.path == "iststandings"

    def test_response_model_is_correct(self):
        """IstStandings uses IstStandingsResponse model."""
        endpoint = IstStandings()

        assert endpoint.response_model is IstStandingsResponse

    def test_endpoint_is_frozen(self):
        """IstStandings is immutable (frozen dataclass)."""
        endpoint = IstStandings()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestIstStandingsResponse:
    """Tests for IstStandingsResponse model."""

    def test_parse_nested_response(self):
        """Response parses nested JSON format correctly."""
        raw_response = {
            "leagueId": "00",
            "seasonYear": "2024-25",
            "unixTimeStamp": 1759244818,
            "timeStampUtc": "2025-09-30T15:06:58.85",
            "teams": [
                {
                    "teamId": 1610612737,
                    "teamCity": "Atlanta",
                    "teamName": "Hawks",
                    "teamAbbreviation": "ATL",
                    "teamSlug": "hawks",
                    "conference": "East",
                    "istGroup": "East Group C",
                    "clinchIndicator": " -x",
                    "clinchedIstKnockout": 0,
                    "clinchedIstGroup": 1,
                    "clinchedIstWildcard": 0,
                    "istWildcardRank": 3,
                    "istGroupRank": 1,
                    "istKnockoutRank": 3,
                    "wins": 3,
                    "losses": 1,
                    "pct": 0.75,
                    "istGroupGb": 0.0,
                    "istWildcardGb": None,
                    "diff": 15,
                    "pts": 485,
                    "oppPts": 470,
                    "games": [
                        {
                            "gameId": "0022400001",
                            "gameNumber": 1,
                            "opponentTeamAbbreviation": "BOS",
                            "location": "A",
                            "gameStatus": 3,
                            "gameStatusText": "Final",
                            "outcome": "W",
                        },
                        {
                            "gameId": "0022400012",
                            "gameNumber": 2,
                            "opponentTeamAbbreviation": "WAS",
                            "location": "H",
                            "gameStatus": 3,
                            "gameStatusText": "Final",
                            "outcome": "W",
                        },
                    ],
                },
            ],
        }

        response = IstStandingsResponse.model_validate(raw_response)

        assert response.league_id == "00"
        assert response.season_year == "2024-25"
        assert len(response.teams) == 1

        hawks = response.teams[0]
        assert hawks.team_name == "Hawks"
        assert hawks.team_abbreviation == "ATL"
        assert hawks.ist_group == "East Group C"
        assert hawks.clinched_ist_group == 1
        assert hawks.wins == 3
        assert hawks.losses == 1
        assert hawks.pct == 0.75

        assert len(hawks.games) == 2
        game1 = hawks.games[0]
        assert game1.game_id == "0022400001"
        assert game1.opponent_team_abbreviation == "BOS"
        assert game1.outcome == "W"

    def test_parse_empty_teams(self):
        """Response handles empty teams list."""
        raw_response = {
            "leagueId": "00",
            "seasonYear": "2024-25",
            "unixTimeStamp": 0,
            "timeStampUtc": "",
            "teams": [],
        }

        response = IstStandingsResponse.model_validate(raw_response)

        assert response.teams == []

    def test_handles_null_ranks(self):
        """Response handles null rank values."""
        raw_response = {
            "leagueId": "00",
            "seasonYear": "2024-25",
            "unixTimeStamp": 0,
            "timeStampUtc": "",
            "teams": [
                {
                    "teamId": 1610612738,
                    "teamCity": "Boston",
                    "teamName": "Celtics",
                    "teamAbbreviation": "BOS",
                    "teamSlug": "celtics",
                    "conference": "East",
                    "istGroup": "East Group C",
                    "clinchIndicator": " -o",
                    "clinchedIstKnockout": 0,
                    "clinchedIstGroup": 0,
                    "clinchedIstWildcard": 0,
                    "istWildcardRank": None,
                    "istGroupRank": None,
                    "istKnockoutRank": None,
                    "wins": 0,
                    "losses": 0,
                    "pct": 0.0,
                    "istGroupGb": None,
                    "istWildcardGb": None,
                    "diff": 0,
                    "pts": 0,
                    "oppPts": 0,
                    "games": [],
                },
            ],
        }

        response = IstStandingsResponse.model_validate(raw_response)

        celtics = response.teams[0]
        assert celtics.ist_wildcard_rank is None
        assert celtics.ist_group_rank is None
        assert celtics.ist_knockout_rank is None
        assert celtics.ist_group_gb is None
