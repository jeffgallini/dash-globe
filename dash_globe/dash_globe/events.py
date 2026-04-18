"""Helpers for working with Dash Globe callback event payloads."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def event_coords(event: Mapping[str, Any] | None) -> dict[str, float] | None:
    """Extract geographic coordinates from an interaction payload.

    Parameters
    ----------
    event : mapping or None
        Dash Globe callback payload such as ``clickData`` or ``hoverData``.

    Returns
    -------
    dict[str, float] or None
        A dictionary containing at least ``lat`` and ``lng``. ``altitude`` is
        included when present and coercible to ``float``. Returns ``None`` when
        the payload does not contain valid coordinate data.

    Notes
    -----
    This helper normalises the nested ``coords`` field exposed by the React
    wrapper so callback code can work with a compact, predictable structure.
    """

    if not isinstance(event, Mapping):
        return None

    coords = event.get("coords")
    if not isinstance(coords, Mapping):
        return None

    extracted: dict[str, float] = {}
    for key in ("lat", "lng", "altitude"):
        value = coords.get(key)
        if value is None:
            continue

        try:
            extracted[key] = float(value)
        except (TypeError, ValueError):
            return None

    if "lat" not in extracted or "lng" not in extracted:
        return None

    return extracted
