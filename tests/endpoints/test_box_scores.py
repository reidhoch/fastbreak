"""Tests for box score endpoint instantiation and params."""

import pytest

from fastbreak.endpoints import (
    BoxScoreAdvanced,
    BoxScoreFourFactors,
    BoxScoreMatchups,
    BoxScoreMisc,
    BoxScorePlayerTrack,
    BoxScoreScoring,
    BoxScoreSummary,
    BoxScoreTraditional,
    BoxScoreUsage,
)

GAME_ID = "0022500571"

BOX_SCORE_ENDPOINTS = [
    (BoxScoreAdvanced, "boxscoreadvancedv3"),
    (BoxScoreFourFactors, "boxscorefourfactorsv3"),
    (BoxScoreMatchups, "boxscorematchupsv3"),
    (BoxScoreMisc, "boxscoremiscv3"),
    (BoxScorePlayerTrack, "boxscoreplayertrackv3"),
    (BoxScoreScoring, "boxscorescoringv3"),
    (BoxScoreSummary, "boxscoresummaryv3"),
    (BoxScoreTraditional, "boxscoretraditionalv3"),
    (BoxScoreUsage, "boxscoreusagev3"),
]


@pytest.mark.parametrize("endpoint_class,expected_path", BOX_SCORE_ENDPOINTS)
class TestBoxScoreEndpoints:
    """Tests for all box score endpoints."""

    def test_init_stores_game_id(self, endpoint_class, expected_path):
        endpoint = endpoint_class(GAME_ID)
        assert endpoint.game_id == GAME_ID

    def test_params_returns_game_id(self, endpoint_class, expected_path):
        endpoint = endpoint_class(GAME_ID)
        assert endpoint.params() == {"GameID": GAME_ID}

    def test_path_is_correct(self, endpoint_class, expected_path):
        endpoint = endpoint_class(GAME_ID)
        assert endpoint.path == expected_path
