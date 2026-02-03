"""Tests for video status models."""

from fastbreak.models.video_status import (
    VideoStatusResponse,
)


class TestVideoStatusResponse:
    """Tests for VideoStatusResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"games": []}

        response = VideoStatusResponse.model_validate(data)

        assert response.games == []
