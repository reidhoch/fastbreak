"""Tests for FrozenResponse base class."""

import logging

import pytest
from pydantic import ValidationError

from fastbreak.models.common.response import FrozenResponse


class ExampleResponse(FrozenResponse):
    """Example response model for testing."""

    name: str
    value: int


class TestFrozenResponse:
    """Tests for FrozenResponse base class."""

    def test_frozen_prevents_mutation(self):
        """Frozen config prevents attribute mutation."""
        response = ExampleResponse(name="test", value=42)
        with pytest.raises(ValidationError):
            response.name = "changed"

    def test_extra_fields_ignored(self):
        """Extra fields are silently ignored in normal mode."""
        response = ExampleResponse(name="test", value=42, unknown_field="ignored")
        assert response.name == "test"
        assert response.value == 42
        assert not hasattr(response, "unknown_field")

    def test_warns_on_extra_fields(self, caplog):
        """Logs warning when extra fields are present."""
        with caplog.at_level(logging.WARNING):
            ExampleResponse(name="test", value=42, new_api_field="detected")

        assert len(caplog.records) == 1
        assert "ExampleResponse received unknown fields" in caplog.text
        assert "new_api_field" in caplog.text
        assert "Consider updating the model" in caplog.text

    def test_no_warning_without_extra_fields(self, caplog):
        """No warning when all fields are known."""
        with caplog.at_level(logging.WARNING):
            ExampleResponse(name="test", value=42)

        assert len(caplog.records) == 0


class TestStrictMode:
    """Tests for strict() classmethod."""

    def test_strict_returns_new_class(self):
        """strict() returns a new class, not the original."""
        StrictExample = ExampleResponse.strict()
        assert StrictExample is not ExampleResponse
        assert StrictExample.__name__ == "StrictExampleResponse"

    def test_strict_inherits_from_original(self):
        """Strict class inherits from original."""
        StrictExample = ExampleResponse.strict()
        assert issubclass(StrictExample, ExampleResponse)

    def test_strict_has_forbid_config(self):
        """Strict class has extra='forbid' config."""
        StrictExample = ExampleResponse.strict()
        assert StrictExample.model_config.get("extra") == "forbid"

    def test_strict_rejects_extra_fields(self):
        """Strict mode raises ValidationError on extra fields."""
        StrictExample = ExampleResponse.strict()
        with pytest.raises(ValidationError) as exc_info:
            StrictExample(name="test", value=42, unknown="rejected")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "extra_forbidden"
        assert errors[0]["loc"] == ("unknown",)

    def test_strict_accepts_valid_data(self):
        """Strict mode accepts data with only known fields."""
        StrictExample = ExampleResponse.strict()
        response = StrictExample(name="test", value=42)
        assert response.name == "test"
        assert response.value == 42
