"""Tests that V3 box score team/player statistics may be absent.

Pre-1951 games predate advanced analytics (offensive rating, PIE, pace, etc.),
so the NBA API returns ``statistics: null`` at the team level and an empty
``players`` list for those games (e.g. game 0024700041 from 1947-48). The
shared V3 base models must tolerate this rather than discarding the game.
"""

from fastbreak.models.box_score_advanced_v3 import (
    AdvancedStatisticsV3,
    BoxScoreAdvancedV3Response,
)
from fastbreak.models.common.box_score_v3 import BoxScorePlayerV3, BoxScoreTeamV3


def _team_payload(*, statistics, players):
    return {
        "teamId": 1610610035,
        "teamCity": "Baltimore",
        "teamName": "Bullets",
        "teamTricode": "BAL",
        "teamSlug": None,
        "players": players,
        "statistics": statistics,
    }


def _advanced_response(*, home_statistics, away_statistics, players):
    return {
        "meta": {"version": 1, "request": "x", "time": "x", "code": 200},
        "boxScoreAdvanced": {
            "gameId": "0024700041",
            "awayTeamId": 1610610035,
            "homeTeamId": 1610610036,
            "homeTeam": _team_payload(statistics=home_statistics, players=players),
            "awayTeam": _team_payload(statistics=away_statistics, players=players),
        },
    }


class TestV3OptionalStatistics:
    """The shared V3 base tolerates null team/player statistics."""

    def test_team_statistics_may_be_none(self):
        """A V3 team with statistics == None parses (statistics is None)."""
        team = BoxScoreTeamV3[AdvancedStatisticsV3].model_validate(
            _team_payload(statistics=None, players=[])
        )
        assert team.statistics is None
        assert team.players == []

    def test_player_statistics_may_be_none(self):
        """A V3 player with statistics == None parses (statistics is None)."""
        player = BoxScorePlayerV3[AdvancedStatisticsV3].model_validate(
            {
                "personId": 1,
                "firstName": "A",
                "familyName": "B",
                "nameI": "A. B",
                "playerSlug": "a-b",
                "position": "",
                "comment": "",
                "jerseyNum": "0",
                "statistics": None,
            }
        )
        assert player.statistics is None

    def test_pre_1951_advanced_box_score_parses(self):
        """Game 0024700041's null-stats, zero-player advanced box score parses."""
        response = BoxScoreAdvancedV3Response.model_validate(
            _advanced_response(home_statistics=None, away_statistics=None, players=[])
        )
        assert response.box_score_advanced.home_team.statistics is None
        assert response.box_score_advanced.away_team.statistics is None
        assert response.box_score_advanced.home_team.players == []
