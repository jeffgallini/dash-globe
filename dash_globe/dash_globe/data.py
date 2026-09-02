"""Helpers for loading large globe datasets without bloating Dash layouts."""

from __future__ import annotations

from typing import Any


DATA_URL_TYPE = "dash-globe-data-url"


def data_url(url: str, *, unwrap_features: bool = True) -> dict[str, Any]:
    """Build a client-side data source reference for large layer payloads.

    Parameters
    ----------
    url : str
        Absolute or app-relative URL that returns JSON layer data. GeoJSON
        ``FeatureCollection`` responses can be unwrapped to ``.features``.
    unwrap_features : bool, optional
        When ``True`` (default), a fetched GeoJSON FeatureCollection is reduced
        to its ``features`` array before being passed to the globe layer.

    Returns
    -------
    dict[str, Any]
        A compact, JSON-serialisable marker that the React wrapper fetches in
        the browser. The Dash layout stays small even when the remote dataset is
        large.

    Examples
    --------
    >>> DashGlobe(id="countries").update_polygons(
    ...     data=data_url("https://example.com/countries.geojson"),
    ...     polygon_cap_color="steelblue",
    ... )
    """

    if not isinstance(url, str) or not url.strip():
        raise ValueError("data_url() requires a non-empty URL string.")

    return {
        "type": DATA_URL_TYPE,
        "url": url.strip(),
        "unwrapFeatures": bool(unwrap_features),
    }


def is_data_url(value: Any) -> bool:
    """Return ``True`` when ``value`` is a :func:`data_url` marker."""

    return (
        isinstance(value, dict)
        and value.get("type") == DATA_URL_TYPE
        and isinstance(value.get("url"), str)
        and bool(value.get("url"))
    )
