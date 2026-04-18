"""High-level Python helpers for configuring :class:`dash_globe.DashGlobe`.

This module layers a small, chainable API on top of the generated Dash
component so applications can be written in an imperative, figure-like style.
The helpers focus on JSON-serialisable settings and layer data that map cleanly
to Dash callbacks and component props.
"""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Iterable, Mapping, Sequence

from .DashGlobe import DashGlobe as _DashGlobeBase


def _coerce_items(items: Sequence[Any]) -> list[Any]:
    if len(items) == 1 and isinstance(items[0], list):
        return list(items[0])
    return list(items)


def _coerce_children(children: Any) -> list[Any]:
    if children is None:
        return []
    if isinstance(children, list):
        return list(children)
    if isinstance(children, tuple):
        return list(children)
    return [children]


def _snake_to_camel(name: str) -> str:
    head, *tail = name.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in tail if part)


class DashGlobe(_DashGlobeBase):
    """Chainable wrapper around the generated Dash Globe component.

    The wrapper preserves the full underlying Dash prop surface while exposing
    convenience methods for the most common globe configuration tasks:
    scene layout, textures, view state, interaction settings, and layer data.

    Parameters
    ----------
    *args
        Positional arguments accepted by the generated Dash component.
    **kwargs
        Keyword arguments accepted by the generated Dash component. If
        ``responsive`` is not provided, it defaults to ``True``.

    Notes
    -----
    The high-level helpers intentionally focus on JSON-serialisable values.
    Features that require JavaScript callbacks, DOM nodes, or raw Three.js
    objects remain available through the base component props instead of the
    convenience API.

    Examples
    --------
    >>> globe = (
    ...     DashGlobe(id="demo")
    ...     .update_layout(height=480)
    ...     .update_globe(globe_image_url="https://example.com/earth.jpg")
    ...     .update_view(lat=20, lng=-30, altitude=2)
    ... )
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise a globe component with responsive layout enabled by default."""
        kwargs.setdefault("responsive", True)
        super().__init__(*args, **kwargs)

    def _normalise_prop_name(self, key: str) -> str:
        available = set(getattr(self, "available_properties", []))
        if key in available or "_" not in key:
            return key

        alias = _snake_to_camel(key)
        return alias if alias in available else key

    def update(self, **kwargs: Any) -> "DashGlobe":
        """Update component properties in place.

        Parameters
        ----------
        **kwargs
            Component properties to set. Snake-case aliases are accepted for
            props exposed by the generated component in camelCase.

        Returns
        -------
        DashGlobe
            The same instance, which allows fluent chaining.
        """
        for key, value in kwargs.items():
            setattr(self, self._normalise_prop_name(key), value)
        return self

    def update_layout(
        self,
        *,
        width: float | None = None,
        height: float | None = None,
        responsive: bool | None = None,
        background_color: str | None = None,
        background_image_url: str | None = None,
        globe_offset: list[float] | tuple[float, float] | None = None,
        wait_for_globe_ready: bool | None = None,
        animate_in: bool | None = None,
        renderer_config: Mapping[str, Any] | None = None,
        style: Mapping[str, Any] | None = None,
        class_name: str | None = None,
    ) -> "DashGlobe":
        """Update outer layout and renderer settings.

        Parameters
        ----------
        width, height : float, optional
            Explicit canvas dimensions in pixels.
        responsive : bool, optional
            Whether the globe should resize with its container.
        background_color : str, optional
            CSS color used behind the canvas.
        background_image_url : str, optional
            Image URL rendered behind the globe.
        globe_offset : list[float] or tuple[float, float], optional
            Horizontal and vertical globe offset relative to the canvas center.
        wait_for_globe_ready : bool, optional
            Whether the component should defer animation until globe assets are
            ready.
        animate_in : bool, optional
            Whether the initial globe entrance animation should run.
        renderer_config : mapping, optional
            Extra renderer options forwarded to the underlying implementation.
        style : mapping, optional
            Inline CSS styles applied to the wrapper element.
        class_name : str, optional
            CSS class applied to the wrapper element.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = {}
        if width is not None:
            updates["width"] = width
        if height is not None:
            updates["height"] = height
        if responsive is not None:
            updates["responsive"] = responsive
        if background_color is not None:
            updates["backgroundColor"] = background_color
        if background_image_url is not None:
            updates["backgroundImageUrl"] = background_image_url
        if globe_offset is not None:
            updates["globeOffset"] = list(globe_offset)
        if wait_for_globe_ready is not None:
            updates["waitForGlobeReady"] = wait_for_globe_ready
        if animate_in is not None:
            updates["animateIn"] = animate_in
        if renderer_config is not None:
            updates["rendererConfig"] = dict(renderer_config)
        if style is not None:
            updates["style"] = dict(style)
        if class_name is not None:
            updates["className"] = class_name
        return self.update(**updates)

    def update_globe(
        self,
        *,
        globe_image_url: str | None = None,
        bump_image_url: str | None = None,
        show_globe: bool | None = None,
        show_graticules: bool | None = None,
        show_atmosphere: bool | None = None,
        atmosphere_color: str | None = None,
        atmosphere_altitude: float | None = None,
        curvature_resolution: float | None = None,
    ) -> "DashGlobe":
        """Update globe shell appearance and geometry settings.

        Parameters
        ----------
        globe_image_url : str, optional
            Base globe texture image.
        bump_image_url : str, optional
            Bump-map texture used for surface relief.
        show_globe : bool, optional
            Whether the base globe sphere is visible.
        show_graticules : bool, optional
            Whether latitude and longitude grid lines are shown.
        show_atmosphere : bool, optional
            Whether the atmospheric halo is shown.
        atmosphere_color : str, optional
            CSS color for the atmosphere.
        atmosphere_altitude : float, optional
            Atmosphere thickness relative to globe radius.
        curvature_resolution : float, optional
            Globe mesh curvature resolution.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = {}
        if globe_image_url is not None:
            updates["globeImageUrl"] = globe_image_url
        if bump_image_url is not None:
            updates["bumpImageUrl"] = bump_image_url
        if show_globe is not None:
            updates["showGlobe"] = show_globe
        if show_graticules is not None:
            updates["showGraticules"] = show_graticules
        if show_atmosphere is not None:
            updates["showAtmosphere"] = show_atmosphere
        if atmosphere_color is not None:
            updates["atmosphereColor"] = atmosphere_color
        if atmosphere_altitude is not None:
            updates["atmosphereAltitude"] = atmosphere_altitude
        if curvature_resolution is not None:
            updates["globeCurvatureResolution"] = curvature_resolution
        return self.update(**updates)

    def update_view(
        self,
        *,
        lat: float | None = None,
        lng: float | None = None,
        altitude: float | None = None,
        transition_duration: float | None = None,
    ) -> "DashGlobe":
        """Update the target camera position.

        Parameters
        ----------
        lat, lng : float, optional
            Geographic camera target in degrees.
        altitude : float, optional
            Camera altitude relative to globe radius.
        transition_duration : float, optional
            Camera transition duration in milliseconds.

        Returns
        -------
        DashGlobe
            The updated globe instance.

        Notes
        -----
        Only the provided coordinates are changed. Existing camera values are
        preserved for omitted fields.
        """
        camera_position = dict(getattr(self, "cameraPosition", None) or {})
        if lat is not None:
            camera_position["lat"] = lat
        if lng is not None:
            camera_position["lng"] = lng
        if altitude is not None:
            camera_position["altitude"] = altitude

        updates = {}
        if camera_position:
            updates["cameraPosition"] = camera_position
        if transition_duration is not None:
            updates["cameraTransitionDuration"] = transition_duration
        return self.update(**updates)

    def update_interaction(
        self,
        *,
        enable_pointer_interaction: bool | None = None,
        show_pointer_cursor: bool | None = None,
        line_hover_precision: float | None = None,
        animation_paused: bool | None = None,
        current_view_report_interval: float | None = None,
    ) -> "DashGlobe":
        """Update interaction-related component settings.

        Parameters
        ----------
        enable_pointer_interaction : bool, optional
            Whether hover and click picking should be enabled.
        show_pointer_cursor : bool, optional
            Whether the cursor should switch to a pointer over interactive
            objects.
        line_hover_precision : float, optional
            Hover picking precision for line-like layers.
        animation_paused : bool, optional
            Whether globe animation should pause.
        current_view_report_interval : float, optional
            Minimum interval in milliseconds between reported ``currentView``
            prop updates.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = {}
        if enable_pointer_interaction is not None:
            updates["enablePointerInteraction"] = enable_pointer_interaction
        if show_pointer_cursor is not None:
            updates["showPointerCursor"] = show_pointer_cursor
        if line_hover_precision is not None:
            updates["lineHoverPrecision"] = line_hover_precision
        if animation_paused is not None:
            updates["animationPaused"] = animation_paused
        if current_view_report_interval is not None:
            updates["currentViewReportInterval"] = current_view_report_interval
        return self.update(**updates)

    def update_controls(
        self,
        *,
        auto_rotate: bool | None = None,
        auto_rotate_speed: float | None = None,
    ) -> "DashGlobe":
        """Update orbit-control behavior.

        Parameters
        ----------
        auto_rotate : bool, optional
            Whether the globe should rotate automatically.
        auto_rotate_speed : float, optional
            Automatic rotation speed.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = {}
        if auto_rotate is not None:
            updates["autoRotate"] = auto_rotate
        if auto_rotate_speed is not None:
            updates["autoRotateSpeed"] = auto_rotate_speed
        return self.update(**updates)

    def update_day_night_cycle(
        self,
        *,
        enabled: bool | None = True,
        day_image_url: str | None = None,
        night_image_url: str | None = None,
        time: Any | None = None,
        animate: bool | None = None,
        minutes_per_second: float | None = None,
    ) -> "DashGlobe":
        """Configure the built-in day and night globe shader.

        Parameters
        ----------
        enabled : bool, optional
            Whether the day/night shader should be enabled.
        day_image_url, night_image_url : str, optional
            Texture URLs for the lit and dark sides of the globe.
        time : Any, optional
            Time value forwarded to the component's day/night shader logic.
        animate : bool, optional
            Whether the solar position should animate automatically.
        minutes_per_second : float, optional
            Speed of the simulated clock when animation is enabled.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = {}
        if enabled is not None:
            updates["dayNightCycle"] = enabled
        if day_image_url is not None:
            updates["dayNightCycleDayImageUrl"] = day_image_url
        if night_image_url is not None:
            updates["dayNightCycleNightImageUrl"] = night_image_url
        if time is not None:
            updates["dayNightCycleTime"] = time
        if animate is not None:
            updates["dayNightCycleAnimate"] = animate
        if minutes_per_second is not None:
            updates["dayNightCycleMinutesPerSecond"] = minutes_per_second
        return self.update(**updates)

    def update_clouds(
        self,
        *,
        enabled: bool | None = True,
        image_url: str | None = None,
        altitude: float | None = None,
        rotation_speed: float | None = None,
        opacity: float | None = None,
    ) -> "DashGlobe":
        """Configure the optional rotating cloud shell.

        Parameters
        ----------
        enabled : bool, optional
            Whether the cloud layer should be enabled.
        image_url : str, optional
            Cloud texture image URL.
        altitude : float, optional
            Cloud sphere altitude relative to globe radius.
        rotation_speed : float, optional
            Rotation speed for the cloud shell.
        opacity : float, optional
            Cloud shell opacity.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = {}
        if enabled is not None:
            updates["clouds"] = enabled
        if image_url is not None:
            updates["cloudsImageUrl"] = image_url
        if altitude is not None:
            updates["cloudsAltitude"] = altitude
        if rotation_speed is not None:
            updates["cloudsRotationSpeed"] = rotation_speed
        if opacity is not None:
            updates["cloudsOpacity"] = opacity
        return self.update(**updates)

    def clear_tile_cache(self) -> "DashGlobe":
        """Invalidate cached globe tiles.

        Returns
        -------
        DashGlobe
            The updated globe instance.

        Notes
        -----
        This increments ``clearGlobeTileCacheKey`` so the client can detect that
        any tile cache should be refreshed.
        """
        current = getattr(self, "clearGlobeTileCacheKey", 0) or 0
        return self.update(clearGlobeTileCacheKey=current + 1)

    def _extend_data(self, prop_name: str, items: Sequence[Any]) -> "DashGlobe":
        existing = list(getattr(self, prop_name, None) or [])
        existing.extend(_coerce_items(items))
        return self.update(**{prop_name: existing})

    def _extend_children(self, children: Any) -> "DashGlobe":
        existing = _coerce_children(getattr(self, "children", None))
        existing.extend(_coerce_children(children))
        return self.update(children=existing)

    def _update_layer(self, data_prop: str, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        updates = dict(props)
        if data is not None:
            updates[data_prop] = list(data)
        return self.update(**updates)

    def add_points(self, *points: Any) -> "DashGlobe":
        """Append one or more point records to ``pointsData``.

        Parameters
        ----------
        *points
            Point records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("pointsData", points)

    def update_points(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the points layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``pointsData`` payload.
        **props
            Additional point-layer props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("pointsData", data, **props)

    def add_arcs(self, *arcs: Any) -> "DashGlobe":
        """Append one or more arc records to ``arcsData``.

        Parameters
        ----------
        *arcs
            Arc records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("arcsData", arcs)

    def update_arcs(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the arc layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``arcsData`` payload.
        **props
            Additional arc-layer props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("arcsData", data, **props)

    def add_polygons(self, *polygons: Any) -> "DashGlobe":
        """Append one or more polygon records to ``polygonsData``.

        Parameters
        ----------
        *polygons
            Polygon records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("polygonsData", polygons)

    def update_polygons(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the polygon layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``polygonsData`` payload.
        **props
            Additional polygon-layer props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("polygonsData", data, **props)

    def add_paths(self, *paths: Any) -> "DashGlobe":
        """Append one or more path records to ``pathsData``.

        Parameters
        ----------
        *paths
            Path records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("pathsData", paths)

    def update_paths(
        self,
        data: Iterable[Any] | None = None,
        *,
        path_label: Any | None = None,
        path_points: Any | None = None,
        path_point_lat: Any | None = None,
        path_point_lng: Any | None = None,
        path_point_alt: Any | None = None,
        path_resolution: float | None = None,
        path_color: Any | None = None,
        path_stroke: Any | None = None,
        path_dash_length: Any | None = None,
        path_dash_gap: Any | None = None,
        path_dash_initial_gap: Any | None = None,
        path_dash_animate_time: Any | None = None,
        path_transition_duration: float | None = None,
        **props: Any,
    ) -> "DashGlobe":
        """Replace or reconfigure the path layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``pathsData`` payload.
        path_label, path_points, path_point_lat, path_point_lng, path_point_alt : Any, optional
            Friendly aliases for the corresponding path accessors.
        path_resolution : float, optional
            Path interpolation resolution.
        path_color, path_stroke : Any, optional
            Color and stroke accessors or constant values.
        path_dash_length, path_dash_gap, path_dash_initial_gap, path_dash_animate_time : Any, optional
            Dash animation settings for path rendering.
        path_transition_duration : float, optional
            Layer transition duration in milliseconds.
        **props
            Additional path-layer props or raw accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = dict(props)
        if path_label is not None:
            updates["path_label"] = path_label
        if path_points is not None:
            updates["path_points"] = path_points
        if path_point_lat is not None:
            updates["path_point_lat"] = path_point_lat
        if path_point_lng is not None:
            updates["path_point_lng"] = path_point_lng
        if path_point_alt is not None:
            updates["path_point_alt"] = path_point_alt
        if path_resolution is not None:
            updates["path_resolution"] = path_resolution
        if path_color is not None:
            updates["path_color"] = path_color
        if path_stroke is not None:
            updates["path_stroke"] = path_stroke
        if path_dash_length is not None:
            updates["path_dash_length"] = path_dash_length
        if path_dash_gap is not None:
            updates["path_dash_gap"] = path_dash_gap
        if path_dash_initial_gap is not None:
            updates["path_dash_initial_gap"] = path_dash_initial_gap
        if path_dash_animate_time is not None:
            updates["path_dash_animate_time"] = path_dash_animate_time
        if path_transition_duration is not None:
            updates["path_transition_duration"] = path_transition_duration
        return self._update_layer("pathsData", data, **updates)

    def _coerce_heatmap_dataset(self, heatmap: Any) -> Any:
        if isinstance(heatmap, MappingABC):
            return dict(heatmap)
        return list(heatmap)

    def add_heatmap(self, points: Any) -> "DashGlobe":
        """Append a single heatmap dataset.

        Parameters
        ----------
        points : Any
            A heatmap dataset, typically a sequence of weighted point records or
            an already-structured mapping.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        existing = list(getattr(self, "heatmapsData", None) or [])
        existing.append(self._coerce_heatmap_dataset(points))
        return self.update(heatmapsData=existing)

    def add_heatmaps(self, *heatmaps: Any) -> "DashGlobe":
        """Append multiple heatmap datasets.

        Parameters
        ----------
        *heatmaps
            Heatmap datasets to append.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        existing = list(getattr(self, "heatmapsData", None) or [])
        existing.extend(self._coerce_heatmap_dataset(heatmap) for heatmap in heatmaps)
        return self.update(heatmapsData=existing)

    def update_heatmap(self, data: Any | None = None, **props: Any) -> "DashGlobe":
        """Replace the globe with a single heatmap dataset.

        Parameters
        ----------
        data : Any, optional
            Replacement dataset. When provided, it is wrapped as a single-item
            ``heatmapsData`` list.
        **props
            Additional heatmap-layer props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = dict(props)
        if data is not None:
            updates["heatmapsData"] = [self._coerce_heatmap_dataset(data)]
        return self.update(**updates)

    def update_heatmaps(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the heatmaps layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``heatmapsData`` payload.
        **props
            Additional heatmap-layer props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("heatmapsData", data, **props)

    def add_hex_bins(self, *points: Any) -> "DashGlobe":
        """Append point records to the hex-bin layer input.

        Parameters
        ----------
        *points
            Point records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("hexBinPointsData", points)

    def update_hex_bins(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the hex-bin layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``hexBinPointsData`` payload.
        **props
            Additional hex-bin props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("hexBinPointsData", data, **props)

    def add_hex_polygons(self, *polygons: Any) -> "DashGlobe":
        """Append records to the hex-polygon layer.

        Parameters
        ----------
        *polygons
            Hex-polygon records to append. A single list may be passed instead
            of multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("hexPolygonsData", polygons)

    def update_hex_polygons(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the hex-polygon layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``hexPolygonsData`` payload.
        **props
            Additional hex-polygon props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("hexPolygonsData", data, **props)

    def add_tiles(self, *tiles: Any) -> "DashGlobe":
        """Append one or more tile records to ``tilesData``.

        Parameters
        ----------
        *tiles
            Tile records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("tilesData", tiles)

    def update_tiles(
        self,
        data: Iterable[Any] | None = None,
        *,
        tile_label: Any | None = None,
        tile_lat: Any | None = None,
        tile_lng: Any | None = None,
        tile_altitude: Any | None = None,
        tile_width: Any | None = None,
        tile_height: Any | None = None,
        tile_material: Any | None = None,
        tile_use_globe_projection: Any | None = None,
        tile_curvature_resolution: Any | None = None,
        tiles_transition_duration: float | None = None,
        **props: Any,
    ) -> "DashGlobe":
        """Replace or reconfigure the tile layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``tilesData`` payload.
        tile_label, tile_lat, tile_lng, tile_altitude : Any, optional
            Friendly aliases for tile accessors.
        tile_width, tile_height : Any, optional
            Tile size accessors or constant values.
        tile_material : Any, optional
            Material accessor or constant JSON material spec.
        tile_use_globe_projection : Any, optional
            Whether tiles should conform to the globe surface.
        tile_curvature_resolution : Any, optional
            Curvature resolution accessor or constant value.
        tiles_transition_duration : float, optional
            Layer transition duration in milliseconds.
        **props
            Additional tile-layer props or raw accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = dict(props)
        if tile_label is not None:
            updates["tile_label"] = tile_label
        if tile_lat is not None:
            updates["tile_lat"] = tile_lat
        if tile_lng is not None:
            updates["tile_lng"] = tile_lng
        if tile_altitude is not None:
            updates["tile_altitude"] = tile_altitude
        if tile_width is not None:
            updates["tile_width"] = tile_width
        if tile_height is not None:
            updates["tile_height"] = tile_height
        if tile_material is not None:
            updates["tile_material"] = tile_material
        if tile_use_globe_projection is not None:
            updates["tile_use_globe_projection"] = tile_use_globe_projection
        if tile_curvature_resolution is not None:
            updates["tile_curvature_resolution"] = tile_curvature_resolution
        if tiles_transition_duration is not None:
            updates["tiles_transition_duration"] = tiles_transition_duration
        return self._update_layer("tilesData", data, **updates)

    def add_particle_sets(self, *particle_sets: Any) -> "DashGlobe":
        """Append one or more particle datasets to ``particlesData``.

        Parameters
        ----------
        *particle_sets
            Particle datasets to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("particlesData", particle_sets)

    def update_particles(self, data: Iterable[Any] | None = None, **props: Any) -> "DashGlobe":
        """Replace or reconfigure the particles layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``particlesData`` payload.
        **props
            Additional particle-layer props or accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._update_layer("particlesData", data, **props)

    def add_rings(self, *rings: Any) -> "DashGlobe":
        """Append one or more ring records to ``ringsData``.

        Parameters
        ----------
        *rings
            Ring records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("ringsData", rings)

    def update_rings(
        self,
        data: Iterable[Any] | None = None,
        *,
        ring_lat: Any | None = None,
        ring_lng: Any | None = None,
        ring_altitude: Any | None = None,
        ring_color: Any | None = None,
        ring_resolution: float | None = None,
        ring_max_radius: Any | None = None,
        ring_propagation_speed: Any | None = None,
        ring_repeat_period: Any | None = None,
        **props: Any,
    ) -> "DashGlobe":
        """Replace or reconfigure the rings layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``ringsData`` payload.
        ring_lat, ring_lng, ring_altitude, ring_color : Any, optional
            Friendly aliases for ring accessors.
        ring_resolution : float, optional
            Ring mesh resolution.
        ring_max_radius, ring_propagation_speed, ring_repeat_period : Any, optional
            Accessors or constant values controlling ring animation.
        **props
            Additional ring-layer props or raw accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = dict(props)
        if ring_lat is not None:
            updates["ring_lat"] = ring_lat
        if ring_lng is not None:
            updates["ring_lng"] = ring_lng
        if ring_altitude is not None:
            updates["ring_altitude"] = ring_altitude
        if ring_color is not None:
            updates["ring_color"] = ring_color
        if ring_resolution is not None:
            updates["ring_resolution"] = ring_resolution
        if ring_max_radius is not None:
            updates["ring_max_radius"] = ring_max_radius
        if ring_propagation_speed is not None:
            updates["ring_propagation_speed"] = ring_propagation_speed
        if ring_repeat_period is not None:
            updates["ring_repeat_period"] = ring_repeat_period
        return self._update_layer("ringsData", data, **updates)

    def add_labels(self, *labels: Any) -> "DashGlobe":
        """Append one or more label records to ``labelsData``.

        Parameters
        ----------
        *labels
            Label records to append. A single list may be passed instead of
            multiple positional items.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        return self._extend_data("labelsData", labels)

    def update_labels(
        self,
        data: Iterable[Any] | None = None,
        *,
        label_label: Any | None = None,
        label_lat: Any | None = None,
        label_lng: Any | None = None,
        label_text: Any | None = None,
        label_color: Any | None = None,
        label_altitude: Any | None = None,
        label_size: Any | None = None,
        label_rotation: Any | None = None,
        label_resolution: float | None = None,
        label_include_dot: Any | None = None,
        label_dot_radius: Any | None = None,
        label_dot_orientation: Any | None = None,
        labels_transition_duration: float | None = None,
        **props: Any,
    ) -> "DashGlobe":
        """Replace or reconfigure the labels layer.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``labelsData`` payload.
        label_label, label_lat, label_lng, label_text : Any, optional
            Friendly aliases for label accessors.
        label_color, label_altitude, label_size, label_rotation : Any, optional
            Accessors or constant values controlling label appearance.
        label_resolution : float, optional
            Label geometry resolution.
        label_include_dot, label_dot_radius, label_dot_orientation : Any, optional
            Accessors or constant values controlling the optional marker dot.
        labels_transition_duration : float, optional
            Layer transition duration in milliseconds.
        **props
            Additional label-layer props or raw accessors.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = dict(props)
        if label_label is not None:
            updates["label_label"] = label_label
        if label_lat is not None:
            updates["label_lat"] = label_lat
        if label_lng is not None:
            updates["label_lng"] = label_lng
        if label_text is not None:
            updates["label_text"] = label_text
        if label_color is not None:
            updates["label_color"] = label_color
        if label_altitude is not None:
            updates["label_altitude"] = label_altitude
        if label_size is not None:
            updates["label_size"] = label_size
        if label_rotation is not None:
            updates["label_rotation"] = label_rotation
        if label_resolution is not None:
            updates["label_resolution"] = label_resolution
        if label_include_dot is not None:
            updates["label_include_dot"] = label_include_dot
        if label_dot_radius is not None:
            updates["label_dot_radius"] = label_dot_radius
        if label_dot_orientation is not None:
            updates["label_dot_orientation"] = label_dot_orientation
        if labels_transition_duration is not None:
            updates["labels_transition_duration"] = labels_transition_duration
        return self._update_layer("labelsData", data, **updates)

    def add_html_elements(self, *elements: Any, children: Any | None = None) -> "DashGlobe":
        """Append geo-anchored HTML overlay records.

        Parameters
        ----------
        *elements
            Overlay data records to append. A single list may be passed instead
            of multiple positional items.
        children : Any, optional
            Dash component children rendered as tethered overlays. Children are
            matched to ``htmlElementsData`` by index.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        self._extend_data("htmlElementsData", elements)
        if children is not None:
            self._extend_children(children)
        return self

    def update_html_elements(
        self,
        data: Iterable[Any] | None = None,
        *,
        children: Any | None = None,
        html_element_lat: Any | None = None,
        html_element_lng: Any | None = None,
        html_element_altitude: Any | None = None,
        html_element_key: Any | None = None,
        html_element_offset_x: Any | None = None,
        html_element_offset_y: Any | None = None,
        html_element_pointer_events: Any | None = None,
        html_element_hidden: Any | None = None,
        html_element_screen_x: Any | None = None,
        html_element_screen_y: Any | None = None,
        html_element_screen_side: Any | None = None,
        html_element_tether: Any | None = None,
        html_element_tether_color: Any | None = None,
        html_element_tether_width: Any | None = None,
        html_element_tether_attach: Any | None = None,
        **props: Any,
    ) -> "DashGlobe":
        """Replace or reconfigure geo-anchored HTML overlays.

        Parameters
        ----------
        data : iterable, optional
            Replacement ``htmlElementsData`` payload.
        children : Any, optional
            Dash component children rendered as tethered overlays. Children are
            matched to ``htmlElementsData`` by index.
        html_element_lat, html_element_lng, html_element_altitude : Any, optional
            Friendly aliases for geographic overlay accessors.
        html_element_key : Any, optional
            Accessor or constant key used to stabilise overlay identity.
        html_element_offset_x, html_element_offset_y : Any, optional
            Pixel offsets applied after projection.
        html_element_pointer_events : Any, optional
            Accessor or constant CSS pointer-events value.
        html_element_hidden : Any, optional
            Accessor or constant value controlling whether an overlay is hidden.
        html_element_screen_x, html_element_screen_y : Any, optional
            Accessors or constant values for pinning overlays to screen-space
            coordinates instead of the projected globe point.
        html_element_screen_side : Any, optional
            Accessor or constant side hint (``"left"``, ``"right"``, or
            ``"center"``) used when resolving ``html_element_screen_x``.
        html_element_tether : Any, optional
            Accessor or constant value controlling whether a live screen-space
            tether line should connect the overlay to its tracked lat/lng.
        html_element_tether_color : Any, optional
            Accessor or constant stroke color for the tether line.
        html_element_tether_width : Any, optional
            Accessor or constant stroke width for the tether line.
        html_element_tether_attach : Any, optional
            Accessor or constant side of the overlay card where the tether
            should land. Accepted values are ``"auto"``, ``"left"``,
            ``"right"``, ``"top"``, and ``"bottom"``.
        **props
            Additional raw component props.

        Returns
        -------
        DashGlobe
            The updated globe instance.
        """
        updates = dict(props)
        if children is not None:
            updates["children"] = _coerce_children(children)
        if html_element_lat is not None:
            updates["html_element_lat"] = html_element_lat
        if html_element_lng is not None:
            updates["html_element_lng"] = html_element_lng
        if html_element_altitude is not None:
            updates["html_element_altitude"] = html_element_altitude
        if html_element_key is not None:
            updates["html_element_key"] = html_element_key
        if html_element_offset_x is not None:
            updates["html_element_offset_x"] = html_element_offset_x
        if html_element_offset_y is not None:
            updates["html_element_offset_y"] = html_element_offset_y
        if html_element_pointer_events is not None:
            updates["html_element_pointer_events"] = html_element_pointer_events
        if html_element_hidden is not None:
            updates["html_element_hidden"] = html_element_hidden
        if html_element_screen_x is not None:
            updates["html_element_screen_x"] = html_element_screen_x
        if html_element_screen_y is not None:
            updates["html_element_screen_y"] = html_element_screen_y
        if html_element_screen_side is not None:
            updates["html_element_screen_side"] = html_element_screen_side
        if html_element_tether is not None:
            updates["html_element_tether"] = html_element_tether
        if html_element_tether_color is not None:
            updates["html_element_tether_color"] = html_element_tether_color
        if html_element_tether_width is not None:
            updates["html_element_tether_width"] = html_element_tether_width
        if html_element_tether_attach is not None:
            updates["html_element_tether_attach"] = html_element_tether_attach
        return self._update_layer("htmlElementsData", data, **updates)
