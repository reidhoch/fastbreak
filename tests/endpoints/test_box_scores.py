"""Tests for box score endpoint paths.

Construction and params() invariants are covered by the parametrized property
test in tests/test_models_properties.py. Only the API path ClassVar is checked
here since it cannot vary and is not exercised by model_strategy().
"""

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
    def test_path_is_correct(self, endpoint_class, expected_path):
        assert endpoint_class.path == expected_path
