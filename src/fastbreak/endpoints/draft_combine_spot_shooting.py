"""Endpoint for fetching NBA draft combine spot shooting results."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import DraftCombineEndpoint
from fastbreak.models.draft_combine_spot_shooting import (
    DraftCombineSpotShootingResponse,
)


@dataclass(frozen=True)
class DraftCombineSpotShooting(DraftCombineEndpoint[DraftCombineSpotShootingResponse]):
    """Fetch NBA draft combine spot shooting results."""

    path: ClassVar[str] = "draftcombinespotshooting"
    response_model: ClassVar[type[DraftCombineSpotShootingResponse]] = (
        DraftCombineSpotShootingResponse
    )
