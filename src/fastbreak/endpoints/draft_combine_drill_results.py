"""Endpoint for fetching NBA draft combine athletic drill results."""

from typing import ClassVar

from fastbreak.endpoints.base import DraftCombineEndpoint
from fastbreak.models.draft_combine_drill_results import (
    DraftCombineDrillResultsResponse,
)


class DraftCombineDrillResults(DraftCombineEndpoint[DraftCombineDrillResultsResponse]):
    """Fetch NBA draft combine athletic drill results.

    Includes vertical leap, agility, sprint, and strength testing.
    """

    path: ClassVar[str] = "draftcombinedrillresults"
    response_model: ClassVar[type[DraftCombineDrillResultsResponse]] = (
        DraftCombineDrillResultsResponse
    )
