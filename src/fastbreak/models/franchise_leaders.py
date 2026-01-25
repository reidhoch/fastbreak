"""Models for the franchise leaders endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class StatLeader(BaseModel):
    """A single statistical category leader."""

    value: int
    person_id: int
    player: str


class FranchiseLeader(BaseModel):
    """Franchise all-time leaders for a single team."""

    team_id: int = Field(alias="TEAM_ID")
    pts: StatLeader
    ast: StatLeader
    reb: StatLeader
    blk: StatLeader
    stl: StatLeader


class FranchiseLeadersResponse(BaseModel):
    """Response from the franchise leaders endpoint."""

    leaders: list[FranchiseLeader] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        if not rows:
            return {"leaders": []}

        # Transform the flat row format into nested StatLeader objects
        transformed: list[dict[str, Any]] = [
            {
                "TEAM_ID": row["TEAM_ID"],
                "pts": StatLeader(
                    value=row["PTS"],
                    person_id=row["PTS_PERSON_ID"],
                    player=row["PTS_PLAYER"],
                ),
                "ast": StatLeader(
                    value=row["AST"],
                    person_id=row["AST_PERSON_ID"],
                    player=row["AST_PLAYER"],
                ),
                "reb": StatLeader(
                    value=row["REB"],
                    person_id=row["REB_PERSON_ID"],
                    player=row["REB_PLAYER"],
                ),
                "blk": StatLeader(
                    value=row["BLK"],
                    person_id=row["BLK_PERSON_ID"],
                    player=row["BLK_PLAYER"],
                ),
                "stl": StatLeader(
                    value=row["STL"],
                    person_id=row["STL_PERSON_ID"],
                    player=row["STL_PLAYER"],
                ),
            }
            for row in rows
        ]

        return {"leaders": transformed}
