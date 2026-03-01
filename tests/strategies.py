"""Shared Hypothesis strategies for fastbreak property-based tests."""

from __future__ import annotations

import types as _types
import typing
from datetime import date as _date
from typing import Any

from hypothesis import strategies as st
from pydantic import AfterValidator, BaseModel

from fastbreak.types import _validate_date, _validate_season, validate_iso_date

# ---------------------------------------------------------------------------
# Concrete strategies for validated Annotated string types.
# These are generated directly instead of relying on st.from_type() because
# AfterValidator-based types are opaque to Hypothesis's type inference.
# ---------------------------------------------------------------------------

season_st: st.SearchStrategy[str] = st.integers(min_value=1990, max_value=2030).map(
    lambda y: f"{y}-{(y + 1) % 100:02d}"
)

iso_date_st: st.SearchStrategy[str] = st.dates(
    min_value=_date(2000, 1, 1),
    max_value=_date(2030, 12, 31),
).map(lambda d: d.isoformat())

date_st: st.SearchStrategy[str] = st.dates(
    min_value=_date(2000, 1, 1),
    max_value=_date(2030, 12, 31),
).map(lambda d: d.strftime("%m/%d/%Y"))

# Mapping from AfterValidator function → its strategy, used when inspecting
# FieldInfo.metadata (Pydantic strips AfterValidator out of the annotation
# itself and stores it in the metadata list instead).
_VALIDATOR_STRATS: dict[Any, st.SearchStrategy[str]] = {
    _validate_season: season_st,
    validate_iso_date: iso_date_st,
    _validate_date: date_st,
}


# ---------------------------------------------------------------------------
# Recursive field strategy builder
# ---------------------------------------------------------------------------

_PRIMITIVE_STRATS: dict[type, st.SearchStrategy[Any]] = {
    str: st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126), max_size=30
    ),
    int: st.integers(min_value=-10_000, max_value=100_000),
    float: st.floats(
        min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False
    ),
    bool: st.booleans(),
}


def _validator_strategy(metadata: Any) -> st.SearchStrategy[Any] | None:
    """Return the first matching AfterValidator strategy from a metadata list."""
    for m in metadata:
        if isinstance(m, AfterValidator) and m.func in _VALIDATOR_STRATS:
            return _VALIDATOR_STRATS[m.func]
    return None


def _strategy_for_field(
    ann: object,
    metadata: Any = (),
) -> st.SearchStrategy[Any]:
    """Return a Hypothesis strategy for the given type annotation.

    ``metadata`` should be the ``FieldInfo.metadata`` list so that
    AfterValidator-constrained string types (Season, ISODate, Date) receive
    their hand-crafted strategy rather than falling back to plain ``st.text``.
    """
    if strat := _validator_strategy(metadata):
        return strat

    origin = typing.get_origin(ann)
    args = typing.get_args(ann)

    # Both 3.10+ union syntax (int | None) and typing.Union / Optional[X]
    if isinstance(ann, _types.UnionType) or origin is typing.Union:
        return st.one_of(
            *(st.none() if a is type(None) else _strategy_for_field(a) for a in args)
        )

    # typing.Annotated — unwrap and check inner metadata for AfterValidators
    if origin is typing.Annotated:
        if strat := _validator_strategy(args[1:]):
            return strat
        return _strategy_for_field(args[0])

    # typing.Literal — sample from its allowed values
    if origin is typing.Literal:
        return st.sampled_from(list(args))

    # list[T]
    if origin is list:
        return st.lists(_strategy_for_field(args[0] if args else str), max_size=3)

    # Primitives and safe fallback for unrecognised annotations
    return _PRIMITIVE_STRATS.get(ann, st.none())  # type: ignore[arg-type]


def model_strategy(cls: type[BaseModel]) -> st.SearchStrategy[Any]:
    """Return a Hypothesis strategy that builds valid instances of *cls*.

    Generates a ``dict`` keyed by field aliases (or field names when no alias
    is set), then calls ``cls.model_validate()`` so Pydantic's full validation
    pipeline runs — validators, cross-field checks, etc.

    Works with both response models (plain-typed fields with aliases) and
    endpoint models (fields using type aliases with AfterValidators).
    """
    field_strats: dict[str, st.SearchStrategy[Any]] = {
        (field.alias or name): _strategy_for_field(field.annotation, field.metadata)
        for name, field in cls.model_fields.items()
    }
    return st.fixed_dictionaries(field_strats).map(cls.model_validate)
