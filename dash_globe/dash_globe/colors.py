"""Color helpers for effects that normally require JavaScript callbacks."""

from __future__ import annotations


_VALID_RING_COLOR_EASINGS = {"linear", "sqrt", "square", "cubic"}


def ring_color_interpolator(
    color: str,
    *,
    fade_color: str | None = None,
    opacity: float | None = None,
    fade_opacity: float = 0.0,
    easing: str = "sqrt",
) -> dict[str, str | float]:
    """Build a serialisable ring-color interpolator specification.

    Parameters
    ----------
    color : str
        Base CSS color for the ring.
    fade_color : str, optional
        Target CSS color used as the ring fades out. When omitted, the client
        reuses ``color`` and only changes opacity.
    opacity : float, optional
        Starting opacity between ``0`` and ``1``.
    fade_opacity : float, default 0.0
        Ending opacity between ``0`` and ``1``.
    easing : {"linear", "sqrt", "square", "cubic"}, default "sqrt"
        Easing curve used while interpolating the ring fade.

    Returns
    -------
    dict[str, str | float]
        A small dictionary recognised by the Dash Globe frontend and converted
        into a clientside ``ringColor`` function.

    Raises
    ------
    ValueError
        If a color string is empty or an opacity or easing value is invalid.

    Notes
    -----
    ``react-globe.gl`` expects a JavaScript callback for animated ring colors.
    This helper provides a Python-native alternative that remains fully
    serialisable through Dash.
    """

    normalized_color = color.strip()
    if not normalized_color:
        raise ValueError("color must be a non-empty CSS color string.")

    normalized_easing = easing.strip().lower()
    if normalized_easing not in _VALID_RING_COLOR_EASINGS:
        raise ValueError(
            f"Unsupported ring color easing: {easing!r}. "
            f"Expected one of {sorted(_VALID_RING_COLOR_EASINGS)}."
        )

    if opacity is not None and not 0 <= opacity <= 1:
        raise ValueError("opacity must be between 0 and 1.")

    if not 0 <= fade_opacity <= 1:
        raise ValueError("fade_opacity must be between 0 and 1.")

    spec: dict[str, str | float] = {
        "type": "ring-color-interpolator",
        "color": normalized_color,
    }

    if fade_color is not None:
        normalized_fade_color = fade_color.strip()
        if not normalized_fade_color:
            raise ValueError("fade_color must be a non-empty CSS color string when provided.")
        spec["fadeColor"] = normalized_fade_color

    if opacity is not None:
        spec["opacity"] = opacity

    if fade_opacity != 0:
        spec["fadeOpacity"] = fade_opacity

    if normalized_easing != "sqrt":
        spec["easing"] = normalized_easing

    return spec
