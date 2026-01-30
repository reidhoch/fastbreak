"""Endpoint for fetching NBA draft combine statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import DraftCombineEndpoint
from fastbreak.models.draft_combine_stats import DraftCombineStatsResponse


class DraftCombineStats(DraftCombineEndpoint[DraftCombineStatsResponse]):
    """Fetch NBA draft combine statistics."""

    path: ClassVar[str] = "draftcombinestats"
    response_model: ClassVar[type[DraftCombineStatsResponse]] = (
        DraftCombineStatsResponse
    )
