"""Endpoint for fetching NBA draft combine player anthropometric data."""

from typing import ClassVar

from fastbreak.endpoints.base import DraftCombineEndpoint
from fastbreak.models.draft_combine_player_anthro import (
    DraftCombinePlayerAnthroResponse,
)


class DraftCombinePlayerAnthro(DraftCombineEndpoint[DraftCombinePlayerAnthroResponse]):
    """Fetch NBA draft combine player anthropometric measurements."""

    path: ClassVar[str] = "draftcombineplayeranthro"
    response_model: ClassVar[type[DraftCombinePlayerAnthroResponse]] = (
        DraftCombinePlayerAnthroResponse
    )
