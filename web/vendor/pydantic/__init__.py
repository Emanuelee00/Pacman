"""Minimal pure-Python subset of pydantic's API, for the WASM/browser build.

pydantic-core (the real pydantic v2 engine) is a compiled Rust extension with
no Emscripten/WASM build published on PyPI, so it cannot run under pygbag.
This module implements just enough of pydantic's BaseModel / Field /
ConfigDict / field_validator surface to satisfy pacman.parser unchanged, for
the web target only. The desktop build keeps depending on real pydantic;
this package is never installed there - it is only vendored into web/.
"""

from __future__ import annotations

import copy
from typing import Any, Literal, get_args, get_origin, get_type_hints

_MISSING = object()


class ValidationError(Exception):
    """Raised when a value fails validation, mirroring pydantic's exception."""

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        """Store the list of validation error dicts."""
        self._errors = errors
        message = "; ".join(f"{e['loc']}: {e['msg']}" for e in errors)
        super().__init__(message)

    def errors(self) -> list[dict[str, Any]]:
        """Return the raw list of error dicts."""
        return self._errors


class FieldInfo:
    """Holds the default value and constraints declared via Field(...)."""

    def __init__(
        self,
        default: Any = _MISSING,
        default_factory: Any = None,
        ge: float | None = None,
        le: float | None = None,
        gt: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        """Store the default value and constraints for one field."""
        self.default = default
        self.default_factory = default_factory
        self.ge = ge
        self.le = le
        self.gt = gt
        self.min_length = min_length
        self.max_length = max_length

    def build_default(self) -> Any:
        """Produce a fresh default value for one model instance."""
        if self.default_factory is not None:
            return self.default_factory()
        if self.default is _MISSING:
            return _MISSING
        return copy.deepcopy(self.default)


def Field(
    default: Any = _MISSING,
    *,
    default_factory: Any = None,
    ge: float | None = None,
    le: float | None = None,
    gt: float | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    **_ignored: Any,
) -> FieldInfo:
    """Declare a model field with a default value and/or constraints."""
    return FieldInfo(
        default, default_factory, ge, le, gt, min_length, max_length
    )


class ConfigDict(dict):
    """Plain dict subclass, only used for `model_config = ConfigDict(...)`."""


def field_validator(*field_names: str, mode: str = "after") -> Any:
    """Register a before-validator for the given field names.

    Only mode="before" is implemented: it is the only mode pacman.parser
    uses. Works whether @classmethod is applied above or below it.
    """
    def decorator(func: Any) -> Any:
        target = func.__func__ if isinstance(func, classmethod) else func
        target.__pyd_validates__ = (field_names, mode)
        return func if isinstance(func, classmethod) else classmethod(target)
    return decorator


def _check_constraints(loc: str, value: Any, info: FieldInfo) -> None:
    """Apply the numeric/length constraints declared on a FieldInfo, if any."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if info.ge is not None and value < info.ge:
            raise ValidationError(
                [{"loc": loc, "msg": f"must be >= {info.ge}"}]
            )
        if info.gt is not None and value <= info.gt:
            raise ValidationError(
                [{"loc": loc, "msg": f"must be > {info.gt}"}]
            )
        if info.le is not None and value > info.le:
            raise ValidationError(
                [{"loc": loc, "msg": f"must be <= {info.le}"}]
            )
    if isinstance(value, str):
        if info.min_length is not None and len(value) < info.min_length:
            raise ValidationError(
                [{"loc": loc, "msg": f"length must be >= {info.min_length}"}]
            )
        if info.max_length is not None and len(value) > info.max_length:
            raise ValidationError(
                [{"loc": loc, "msg": f"length must be <= {info.max_length}"}]
            )


def _coerce_scalar(loc: str, value: Any, annotation: Any) -> Any:
    """Coerce a raw JSON value to a plain int/float/str/bool annotation."""
    is_bool_mismatch = annotation is int and isinstance(value, bool)
    if isinstance(value, annotation) and not is_bool_mismatch:
        return value
    if annotation is float and isinstance(value, int):
        return float(value)
    try:
        return annotation(value)
    except (TypeError, ValueError):
        raise ValidationError(
            [{"loc": loc, "msg": f"expected {annotation.__name__}"}]
        )


def _validate_value(loc: str, value: Any, annotation: Any) -> Any:
    """Validate/coerce one raw value against its declared annotation."""
    origin = get_origin(annotation)

    if origin is Literal:
        choices = get_args(annotation)
        if value not in choices:
            raise ValidationError(
                [{"loc": loc, "msg": f"must be one of {choices}"}]
            )
        return value

    if origin is list:
        if not isinstance(value, list):
            raise ValidationError([{"loc": loc, "msg": "expected a list"}])
        (item_type,) = get_args(annotation) or (Any,)
        return [
            _validate_value(f"{loc}[{i}]", item, item_type)
            for i, item in enumerate(value)
        ]

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        if isinstance(value, annotation):
            return value
        if isinstance(value, dict):
            return annotation.model_validate(value)
        raise ValidationError(
            [{"loc": loc, "msg": f"expected {annotation.__name__} or dict"}]
        )

    if annotation in (int, float, str, bool):
        return _coerce_scalar(loc, value, annotation)

    return value


def _dump_value(value: Any) -> Any:
    """Recursively unwrap BaseModel instances/lists for model_dump()."""
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_dump_value(v) for v in value]
    return value


class BaseModel:
    """Stand-in for pydantic.BaseModel: annotation-driven validation only."""

    model_config: ConfigDict = ConfigDict()

    def __init__(self, **data: Any) -> None:
        """Validate and assign every annotated field from data."""
        hints = get_type_hints(type(self))
        hints.pop("model_config", None)
        validators = self._collect_before_validators()

        for name, annotation in hints.items():
            raw = data.get(name, _MISSING)
            if name in validators and raw is not _MISSING:
                raw = validators[name](raw)
            if raw is _MISSING:
                raw = self._default_for(name)
                if raw is _MISSING:
                    raise ValidationError(
                        [{"loc": name, "msg": "field required"}]
                    )
            else:
                raw = _validate_value(name, raw, annotation)
                _check_constraints(name, raw, self._field_info(name))
            setattr(self, name, raw)

    @classmethod
    def _collect_before_validators(cls) -> dict[str, Any]:
        found: dict[str, Any] = {}
        for klass in cls.__mro__:
            for attr in vars(klass).values():
                func = getattr(attr, "__func__", None)
                spec = getattr(func, "__pyd_validates__", None)
                if spec and spec[1] == "before":
                    for field_name in spec[0]:
                        found.setdefault(
                            field_name, lambda v, f=func, c=cls: f(c, v)
                        )
        return found

    @classmethod
    def _field_info(cls, name: str) -> FieldInfo:
        raw_default = getattr(cls, name, _MISSING)
        if isinstance(raw_default, FieldInfo):
            return raw_default
        return FieldInfo(default=raw_default)

    @classmethod
    def _default_for(cls, name: str) -> Any:
        return cls._field_info(name).build_default()

    @classmethod
    def model_validate(cls, data: dict[str, Any]) -> "BaseModel":
        """Build and validate a model instance from a raw dict."""
        if not isinstance(data, dict):
            raise ValidationError(
                [{"loc": cls.__name__, "msg": "expected a dict"}]
            )
        return cls(**data)

    def model_dump(self) -> dict[str, Any]:
        """Recursively convert this model back into plain dicts/lists."""
        hints = get_type_hints(type(self))
        return {
            name: _dump_value(getattr(self, name))
            for name in hints
            if name != "model_config"
        }
