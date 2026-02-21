"""Tests for VideoEvents endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import VideoEvents
from fastbreak.models import VideoEventsResponse


class TestVideoEvents:
    """Tests for VideoEvents endpoint."""

    def test_init_with_required_params(self):
        """VideoEvents requires game_id and game_event_id."""
        endpoint = VideoEvents(game_id="0022400001", game_event_id=10)

        assert endpoint.game_id == "0022400001"
        assert endpoint.game_event_id == 10

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = VideoEvents(game_id="0022400001", game_event_id=10)

        params = endpoint.params()

        assert params == {"GameID": "0022400001", "GameEventID": "10"}

    def test_path_is_correct(self):
        """VideoEvents has correct API path."""
        endpoint = VideoEvents(game_id="0022400001", game_event_id=10)

        assert endpoint.path == "videoevents"

    def test_response_model_is_correct(self):
        """VideoEvents uses VideoEventsResponse model."""
        endpoint = VideoEvents(game_id="0022400001", game_event_id=10)

        assert endpoint.response_model is VideoEventsResponse

    def test_endpoint_is_frozen(self):
        """VideoEvents is immutable (frozen dataclass)."""
        endpoint = VideoEvents(game_id="0022400001", game_event_id=10)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.game_id = "0022400000"  # type: ignore[misc]


class TestVideoEventsResponse:
    """Tests for VideoEventsResponse model."""

    def test_parse_response_with_video_data(self):
        """Response parses video events data correctly."""
        raw_response = {
            "resource": "videoevents",
            "parameters": {"GameID": "0022400001", "GameEventID": 10},
            "resultSets": {
                "Meta": {
                    "videoUrls": [
                        {
                            "uuid": "4549dfbf-fde2-4dcc-8065-afade5ada267",
                            "dur": 5000,
                            "stt": "image/jpeg",
                            "stp": "/thumb/small/video123.jpg",
                            "sth": 90,
                            "stw": 160,
                            "mtt": "image/jpeg",
                            "mtp": "/thumb/medium/video123.jpg",
                            "mth": 180,
                            "mtw": 320,
                            "ltt": "image/jpeg",
                            "ltp": "/thumb/large/video123.jpg",
                            "lth": 360,
                            "ltw": 640,
                        }
                    ]
                },
                "playlist": [
                    {
                        "gi": "0022400001",
                        "ei": 10,
                        "y": 2024,
                        "m": "11",
                        "d": "12",
                        "gc": "2024-11-12/ATLBOS",
                        "p": 1,
                        "dsc": "MISS Johnson 14' Driving Floating Bank Jump Shot",
                        "ha": "BOS",
                        "va": "ATL",
                        "hpb": 0,
                        "hpa": 0,
                        "vpb": 0,
                        "vpa": 0,
                        "pta": 0,
                    }
                ],
            },
        }

        response = VideoEventsResponse.model_validate(raw_response)

        assert response.resource == "videoevents"
        assert response.parameters["GameID"] == "0022400001"

        # Verify meta/video URLs
        meta = response.result_sets.meta
        assert len(meta.video_urls) == 1
        video_url = meta.video_urls[0]
        assert video_url.uuid == "4549dfbf-fde2-4dcc-8065-afade5ada267"
        assert video_url.dur == 5000
        assert video_url.sth == 90
        assert video_url.ltp == "/thumb/large/video123.jpg"

        # Verify playlist
        playlist = response.result_sets.playlist
        assert len(playlist) == 1
        item = playlist[0]
        assert item.game_id == "0022400001"
        assert item.event_id == 10
        assert item.description == "MISS Johnson 14' Driving Floating Bank Jump Shot"
        assert item.home_abbreviation == "BOS"
        assert item.visitor_abbreviation == "ATL"
        assert item.period == 1

    def test_parse_response_with_null_video_fields(self):
        """Response handles null video URL fields."""
        raw_response = {
            "resource": "videoevents",
            "parameters": {"GameID": "0022400001", "GameEventID": 10},
            "resultSets": {
                "Meta": {
                    "videoUrls": [
                        {
                            "uuid": "test-uuid",
                            "dur": None,
                            "stt": None,
                            "stp": None,
                            "sth": None,
                            "stw": None,
                            "mtt": None,
                            "mtp": None,
                            "mth": None,
                            "mtw": None,
                            "ltt": None,
                            "ltp": None,
                            "lth": None,
                            "ltw": None,
                        }
                    ]
                },
                "playlist": [
                    {
                        "gi": "0022400001",
                        "ei": 10,
                        "y": 2024,
                        "m": "11",
                        "d": "12",
                        "gc": "2024-11-12/ATLBOS",
                        "p": 1,
                        "dsc": "Test play",
                        "ha": "BOS",
                        "va": "ATL",
                        "hpb": 0,
                        "hpa": 0,
                        "vpb": 0,
                        "vpa": 0,
                        "pta": 0,
                    }
                ],
            },
        }

        response = VideoEventsResponse.model_validate(raw_response)

        video_url = response.result_sets.meta.video_urls[0]
        assert video_url.uuid == "test-uuid"
        assert video_url.dur is None
        assert video_url.stt is None
        assert video_url.ltp is None

    def test_parse_empty_playlist(self):
        """Response handles empty playlist."""
        raw_response = {
            "resource": "videoevents",
            "parameters": {"GameID": "0022400001", "GameEventID": 2},
            "resultSets": {"Meta": {"videoUrls": []}, "playlist": []},
        }

        response = VideoEventsResponse.model_validate(raw_response)

        assert response.result_sets.meta.video_urls == []
        assert response.result_sets.playlist == []
