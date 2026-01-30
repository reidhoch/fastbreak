"""Endpoint for fetching NBA draft combine non-stationary shooting results."""

from typing import ClassVar

from fastbreak.endpoints.base import DraftCombineEndpoint
from fastbreak.models.draft_combine_nonstationary_shooting import (
    DraftCombineNonstationaryShootingResponse,
)


class DraftCombineNonstationaryShooting(
    DraftCombineEndpoint[DraftCombineNonstationaryShootingResponse]
):
    """Fetch NBA draft combine non-stationary shooting results.

    Includes off-dribble and on-the-move shooting drill results.
    """

    path: ClassVar[str] = "draftcombinenonstationaryshooting"
    response_model: ClassVar[type[DraftCombineNonstationaryShootingResponse]] = (
        DraftCombineNonstationaryShootingResponse
    )
