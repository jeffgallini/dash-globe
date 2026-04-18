"""Serializable material helpers for material-backed globe layers."""

from __future__ import annotations

from typing import Any


_VALID_MATERIAL_TYPES = {"basic", "lambert", "phong", "standard"}
_VALID_MATERIAL_SIDES = {"front", "back", "double"}


def material_spec(material_type: str, /, **options: Any) -> dict[str, Any]:
    """Build a JSON-serialisable material specification.

    Parameters
    ----------
    material_type : str
        Material type supported by the Dash Globe wrapper. Supported values are
        ``"basic"``, ``"lambert"``, ``"phong"``, and ``"standard"``.
    **options
        Additional material properties forwarded to the client. ``side`` is
        validated separately and may be ``"front"``, ``"back"``, or
        ``"double"``.

    Returns
    -------
    dict[str, Any]
        A small dictionary that the React wrapper converts into a Three.js
        material on the client.

    Raises
    ------
    ValueError
        If ``material_type`` or ``side`` is not supported.

    Notes
    -----
    ``None``-valued options are omitted from the returned mapping so specs stay
    compact and serialisable.
    """

    normalized_type = material_type.strip().lower()
    if normalized_type not in _VALID_MATERIAL_TYPES:
        raise ValueError(
            f"Unsupported material type: {material_type!r}. "
            f"Expected one of {sorted(_VALID_MATERIAL_TYPES)}."
        )

    material = {"type": normalized_type}
    side = options.pop("side", None)
    if side is not None:
        normalized_side = str(side).strip().lower()
        if normalized_side not in _VALID_MATERIAL_SIDES:
            raise ValueError(
                f"Unsupported material side: {side!r}. "
                f"Expected one of {sorted(_VALID_MATERIAL_SIDES)}."
            )
        material["side"] = normalized_side

    material.update({key: value for key, value in options.items() if value is not None})
    return material


def lambert_material(*, color: str | None = None, side: str | None = None, **options: Any) -> dict[str, Any]:
    """Build a Lambert material specification.

    Parameters
    ----------
    color : str, optional
        CSS color passed to the generated material.
    side : str, optional
        Triangle side mode: ``"front"``, ``"back"``, or ``"double"``.
    **options
        Additional Lambert material properties.

    Returns
    -------
    dict[str, Any]
        A JSON-serialisable Lambert material specification.
    """

    return material_spec("lambert", color=color, side=side, **options)
