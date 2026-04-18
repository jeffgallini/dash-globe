# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DashGlobe(Component):
    """A DashGlobe component.
Dash wrapper around react-globe.gl.

The component focuses on the JSON-serialisable portion of the upstream API so
it can be configured naturally from Python.

Keyword arguments:

- id (string | dict; optional):
    The ID used to identify this component in Dash callbacks.

- animateIn (boolean; default True)

- animationPaused (boolean; default False)

- arcAltitude (boolean | number | string | dict | list; optional)

- arcAltitudeAutoScale (boolean | number | string | dict | list; optional)

- arcCircularResolution (number; optional)

- arcColor (boolean | number | string | dict | list; optional)

- arcCurveResolution (number; optional)

- arcDashAnimateTime (boolean | number | string | dict | list; optional)

- arcDashGap (boolean | number | string | dict | list; optional)

- arcDashInitialGap (boolean | number | string | dict | list; optional)

- arcDashLength (boolean | number | string | dict | list; optional)

- arcEndAltitude (boolean | number | string | dict | list; optional)

- arcEndLat (boolean | number | string | dict | list; optional)

- arcEndLng (boolean | number | string | dict | list; optional)

- arcLabel (boolean | number | string | dict | list; optional)

- arcStartAltitude (boolean | number | string | dict | list; optional)

- arcStartLat (boolean | number | string | dict | list; optional)

- arcStartLng (boolean | number | string | dict | list; optional)

- arcStroke (boolean | number | string | dict | list; optional)

- arcsData (list; optional):
    Arc layer data and accessors.

- arcsTransitionDuration (number; optional)

- atmosphereAltitude (number; optional)

- atmosphereColor (string; optional)

- autoRotate (boolean; optional)

- autoRotateSpeed (number; optional)

- backgroundColor (string; optional)

- backgroundImageUrl (string; optional)

- bumpImageUrl (string; optional)

- cameraPosition (dict; optional):
    Target camera position in geographic coordinates.

- cameraTransitionDuration (number; default 0)

- className (string; optional):
    CSS class applied to the outer wrapper.

- clearGlobeTileCacheKey (boolean | number | string | dict | list; optional)

- clickData (dict; optional):
    Last click event payload emitted by any supported layer.

- clouds (boolean; optional)

- cloudsAltitude (number; default 0.004)

- cloudsImageUrl (string; optional)

- cloudsOpacity (number; default 1)

- cloudsRotationSpeed (number; default -0.006)

- currentView (dict; optional):
    Current point of view reported by zoom and rotation interactions.

- dayNightCycle (boolean; optional)

- dayNightCycleAnimate (boolean; default True)

- dayNightCycleDayImageUrl (string; optional)

- dayNightCycleMinutesPerSecond (number; default 60)

- dayNightCycleNightImageUrl (string; optional)

- dayNightCycleTime (boolean | number | string | dict | list; optional)

- enablePointerInteraction (boolean; optional)

- globeCurvatureResolution (number; optional)

- globeImageUrl (string; optional)

- globeOffset (list; optional):
    Position offset of the globe relative to the canvas centre.

- globeReady (boolean; optional):
    Whether the globe has finished initialising.

- heatmapBandwidth (boolean | number | string | dict | list; optional)

- heatmapBaseAltitude (boolean | number | string | dict | list; optional)

- heatmapColorSaturation (boolean | number | string | dict | list; optional)

- heatmapPointLat (boolean | number | string | dict | list; optional)

- heatmapPointLng (boolean | number | string | dict | list; optional)

- heatmapPointWeight (boolean | number | string | dict | list; optional)

- heatmapPoints (boolean | number | string | dict | list; optional)

- heatmapTopAltitude (boolean | number | string | dict | list; optional)

- heatmapsData (list; optional):
    Heatmap layer data and accessors.

- heatmapsTransitionDuration (number; optional)

- height (number; optional):
    Canvas height in pixels.

- hexAltitude (boolean | number | string | dict | list; optional)

- hexBinMerge (boolean; optional)

- hexBinPointLat (boolean | number | string | dict | list; optional)

- hexBinPointLng (boolean | number | string | dict | list; optional)

- hexBinPointWeight (boolean | number | string | dict | list; optional)

- hexBinPointsData (list; optional):
    Hex bin layer data and accessors.

- hexBinResolution (number; optional)

- hexLabel (boolean | number | string | dict | list; optional)

- hexMargin (boolean | number | string | dict | list; optional)

- hexPolygonAltitude (boolean | number | string | dict | list; optional)

- hexPolygonColor (boolean | number | string | dict | list; optional)

- hexPolygonCurvatureResolution (boolean | number | string | dict | list; optional)

- hexPolygonDotResolution (boolean | number | string | dict | list; optional)

- hexPolygonGeoJsonGeometry (boolean | number | string | dict | list; optional)

- hexPolygonLabel (boolean | number | string | dict | list; optional)

- hexPolygonMargin (boolean | number | string | dict | list; optional)

- hexPolygonResolution (boolean | number | string | dict | list; optional)

- hexPolygonUseDots (boolean | number | string | dict | list; optional)

- hexPolygonsData (list; optional):
    Hexed polygon layer data and accessors.

- hexPolygonsTransitionDuration (number; optional)

- hexSideColor (boolean | number | string | dict | list; optional)

- hexTopColor (boolean | number | string | dict | list; optional)

- hexTopCurvatureResolution (number; optional)

- hexTransitionDuration (number; optional)

- hoverData (dict; optional):
    Last hover event payload emitted by any supported layer.

- labelAltitude (boolean | number | string | dict | list; optional)

- labelColor (boolean | number | string | dict | list; optional)

- labelDotOrientation (boolean | number | string | dict | list; optional)

- labelDotRadius (boolean | number | string | dict | list; optional)

- labelIncludeDot (boolean | number | string | dict | list; optional)

- labelLabel (boolean | number | string | dict | list; optional)

- labelLat (boolean | number | string | dict | list; optional)

- labelLng (boolean | number | string | dict | list; optional)

- labelResolution (number; optional)

- labelRotation (boolean | number | string | dict | list; optional)

- labelSize (boolean | number | string | dict | list; optional)

- labelText (boolean | number | string | dict | list; optional)

- labelsData (list; optional):
    Label layer data and accessors.

- labelsTransitionDuration (number; optional)

- lastInteraction (dict; optional):
    The most recent interaction payload emitted by the component.

- lineHoverPrecision (number; optional)

- particleAltitude (boolean | number | string | dict | list; optional)

- particleLabel (boolean | number | string | dict | list; optional)

- particleLat (boolean | number | string | dict | list; optional)

- particleLng (boolean | number | string | dict | list; optional)

- particlesColor (boolean | number | string | dict | list; optional)

- particlesData (list; optional):
    Particle layer data and accessors.

- particlesList (boolean | number | string | dict | list; optional)

- particlesSize (boolean | number | string | dict | list; optional)

- particlesSizeAttenuation (boolean | number | string | dict | list; optional)

- pathColor (boolean | number | string | dict | list; optional)

- pathDashAnimateTime (boolean | number | string | dict | list; optional)

- pathDashGap (boolean | number | string | dict | list; optional)

- pathDashInitialGap (boolean | number | string | dict | list; optional)

- pathDashLength (boolean | number | string | dict | list; optional)

- pathLabel (boolean | number | string | dict | list; optional)

- pathPointAlt (boolean | number | string | dict | list; optional)

- pathPointLat (boolean | number | string | dict | list; optional)

- pathPointLng (boolean | number | string | dict | list; optional)

- pathPoints (boolean | number | string | dict | list; optional)

- pathResolution (number; optional)

- pathStroke (boolean | number | string | dict | list; optional)

- pathTransitionDuration (number; optional)

- pathsData (list; optional):
    Path layer data and accessors.

- pointAltitude (boolean | number | string | dict | list; optional)

- pointColor (boolean | number | string | dict | list; optional)

- pointLabel (boolean | number | string | dict | list; optional)

- pointLat (boolean | number | string | dict | list; optional)

- pointLng (boolean | number | string | dict | list; optional)

- pointRadius (boolean | number | string | dict | list; optional)

- pointResolution (number; optional)

- pointsData (list; optional):
    Point layer data and accessors.

- pointsMerge (boolean; optional)

- pointsTransitionDuration (number; optional)

- polygonAltitude (boolean | number | string | dict | list; optional)

- polygonCapColor (boolean | number | string | dict | list; optional)

- polygonCapCurvatureResolution (boolean | number | string | dict | list; optional)

- polygonCapMaterial (boolean | number | string | dict | list; optional)

- polygonGeoJsonGeometry (boolean | number | string | dict | list; optional)

- polygonHoverAltitude (boolean | number | string | dict | list; optional)

- polygonHoverCapColor (boolean | number | string | dict | list; optional)

- polygonHoverKey (boolean | number | string | dict | list; optional)

- polygonHoverSideColor (boolean | number | string | dict | list; optional)

- polygonHoverStrokeColor (boolean | number | string | dict | list; optional)

- polygonLabel (boolean | number | string | dict | list; optional)

- polygonSideColor (boolean | number | string | dict | list; optional)

- polygonSideMaterial (boolean | number | string | dict | list; optional)

- polygonStrokeColor (boolean | number | string | dict | list; optional)

- polygonsData (list; optional):
    Polygon layer data and accessors.

- polygonsTransitionDuration (number; optional)

- rendererConfig (dict; optional)

- responsive (boolean; default True):
    Automatically size the globe from its container with
    ResizeObserver.

- rightClickData (dict; optional):
    Last right click event payload emitted by any supported layer.

- ringAltitude (boolean | number | string | dict | list; optional)

- ringColor (boolean | number | string | dict | list; optional)

- ringLat (boolean | number | string | dict | list; optional)

- ringLng (boolean | number | string | dict | list; optional)

- ringMaxRadius (boolean | number | string | dict | list; optional)

- ringPropagationSpeed (boolean | number | string | dict | list; optional)

- ringRepeatPeriod (boolean | number | string | dict | list; optional)

- ringResolution (number; optional)

- ringsData (list; optional):
    Ring layer data and accessors.

- showAtmosphere (boolean; default True)

- showGlobe (boolean; default True)

- showGraticules (boolean; optional)

- showPointerCursor (boolean; optional)

- tileAltitude (boolean | number | string | dict | list; optional)

- tileCurvatureResolution (boolean | number | string | dict | list; optional)

- tileHeight (boolean | number | string | dict | list; optional)

- tileLabel (boolean | number | string | dict | list; optional)

- tileLat (boolean | number | string | dict | list; optional)

- tileLng (boolean | number | string | dict | list; optional)

- tileMaterial (boolean | number | string | dict | list; optional)

- tileUseGlobeProjection (boolean | number | string | dict | list; optional)

- tileWidth (boolean | number | string | dict | list; optional)

- tilesData (list; optional):
    Tile layer data and accessors.

- tilesTransitionDuration (number; optional)

- waitForGlobeReady (boolean; default True)

- width (number; optional):
    Canvas width in pixels."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_globe'
    _type = 'DashGlobe'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        responsive: typing.Optional[bool] = None,
        width: typing.Optional[NumberType] = None,
        height: typing.Optional[NumberType] = None,
        globeOffset: typing.Optional[typing.Sequence] = None,
        backgroundColor: typing.Optional[str] = None,
        backgroundImageUrl: typing.Optional[str] = None,
        waitForGlobeReady: typing.Optional[bool] = None,
        animateIn: typing.Optional[bool] = None,
        globeImageUrl: typing.Optional[str] = None,
        bumpImageUrl: typing.Optional[str] = None,
        showGlobe: typing.Optional[bool] = None,
        showGraticules: typing.Optional[bool] = None,
        showAtmosphere: typing.Optional[bool] = None,
        atmosphereColor: typing.Optional[str] = None,
        atmosphereAltitude: typing.Optional[NumberType] = None,
        globeCurvatureResolution: typing.Optional[NumberType] = None,
        dayNightCycle: typing.Optional[bool] = None,
        dayNightCycleDayImageUrl: typing.Optional[str] = None,
        dayNightCycleNightImageUrl: typing.Optional[str] = None,
        dayNightCycleTime: typing.Optional[typing.Any] = None,
        dayNightCycleAnimate: typing.Optional[bool] = None,
        dayNightCycleMinutesPerSecond: typing.Optional[NumberType] = None,
        autoRotate: typing.Optional[bool] = None,
        autoRotateSpeed: typing.Optional[NumberType] = None,
        clouds: typing.Optional[bool] = None,
        cloudsImageUrl: typing.Optional[str] = None,
        cloudsAltitude: typing.Optional[NumberType] = None,
        cloudsRotationSpeed: typing.Optional[NumberType] = None,
        cloudsOpacity: typing.Optional[NumberType] = None,
        cameraPosition: typing.Optional[dict] = None,
        cameraTransitionDuration: typing.Optional[NumberType] = None,
        animationPaused: typing.Optional[bool] = None,
        clearGlobeTileCacheKey: typing.Optional[typing.Any] = None,
        rendererConfig: typing.Optional[dict] = None,
        enablePointerInteraction: typing.Optional[bool] = None,
        lineHoverPrecision: typing.Optional[NumberType] = None,
        showPointerCursor: typing.Optional[bool] = None,
        pointsData: typing.Optional[typing.Sequence] = None,
        pointLabel: typing.Optional[typing.Any] = None,
        pointLat: typing.Optional[typing.Any] = None,
        pointLng: typing.Optional[typing.Any] = None,
        pointColor: typing.Optional[typing.Any] = None,
        pointAltitude: typing.Optional[typing.Any] = None,
        pointRadius: typing.Optional[typing.Any] = None,
        pointResolution: typing.Optional[NumberType] = None,
        pointsMerge: typing.Optional[bool] = None,
        pointsTransitionDuration: typing.Optional[NumberType] = None,
        arcsData: typing.Optional[typing.Sequence] = None,
        arcLabel: typing.Optional[typing.Any] = None,
        arcStartLat: typing.Optional[typing.Any] = None,
        arcStartLng: typing.Optional[typing.Any] = None,
        arcStartAltitude: typing.Optional[typing.Any] = None,
        arcEndLat: typing.Optional[typing.Any] = None,
        arcEndLng: typing.Optional[typing.Any] = None,
        arcEndAltitude: typing.Optional[typing.Any] = None,
        arcColor: typing.Optional[typing.Any] = None,
        arcAltitude: typing.Optional[typing.Any] = None,
        arcAltitudeAutoScale: typing.Optional[typing.Any] = None,
        arcStroke: typing.Optional[typing.Any] = None,
        arcCurveResolution: typing.Optional[NumberType] = None,
        arcCircularResolution: typing.Optional[NumberType] = None,
        arcDashLength: typing.Optional[typing.Any] = None,
        arcDashGap: typing.Optional[typing.Any] = None,
        arcDashInitialGap: typing.Optional[typing.Any] = None,
        arcDashAnimateTime: typing.Optional[typing.Any] = None,
        arcsTransitionDuration: typing.Optional[NumberType] = None,
        polygonsData: typing.Optional[typing.Sequence] = None,
        polygonLabel: typing.Optional[typing.Any] = None,
        polygonGeoJsonGeometry: typing.Optional[typing.Any] = None,
        polygonCapMaterial: typing.Optional[typing.Any] = None,
        polygonCapColor: typing.Optional[typing.Any] = None,
        polygonSideMaterial: typing.Optional[typing.Any] = None,
        polygonSideColor: typing.Optional[typing.Any] = None,
        polygonStrokeColor: typing.Optional[typing.Any] = None,
        polygonAltitude: typing.Optional[typing.Any] = None,
        polygonHoverKey: typing.Optional[typing.Any] = None,
        polygonHoverAltitude: typing.Optional[typing.Any] = None,
        polygonHoverCapColor: typing.Optional[typing.Any] = None,
        polygonHoverSideColor: typing.Optional[typing.Any] = None,
        polygonHoverStrokeColor: typing.Optional[typing.Any] = None,
        polygonCapCurvatureResolution: typing.Optional[typing.Any] = None,
        polygonsTransitionDuration: typing.Optional[NumberType] = None,
        pathsData: typing.Optional[typing.Sequence] = None,
        pathLabel: typing.Optional[typing.Any] = None,
        pathPoints: typing.Optional[typing.Any] = None,
        pathPointLat: typing.Optional[typing.Any] = None,
        pathPointLng: typing.Optional[typing.Any] = None,
        pathPointAlt: typing.Optional[typing.Any] = None,
        pathResolution: typing.Optional[NumberType] = None,
        pathColor: typing.Optional[typing.Any] = None,
        pathStroke: typing.Optional[typing.Any] = None,
        pathDashLength: typing.Optional[typing.Any] = None,
        pathDashGap: typing.Optional[typing.Any] = None,
        pathDashInitialGap: typing.Optional[typing.Any] = None,
        pathDashAnimateTime: typing.Optional[typing.Any] = None,
        pathTransitionDuration: typing.Optional[NumberType] = None,
        heatmapsData: typing.Optional[typing.Sequence] = None,
        heatmapPoints: typing.Optional[typing.Any] = None,
        heatmapPointLat: typing.Optional[typing.Any] = None,
        heatmapPointLng: typing.Optional[typing.Any] = None,
        heatmapPointWeight: typing.Optional[typing.Any] = None,
        heatmapBandwidth: typing.Optional[typing.Any] = None,
        heatmapColorSaturation: typing.Optional[typing.Any] = None,
        heatmapBaseAltitude: typing.Optional[typing.Any] = None,
        heatmapTopAltitude: typing.Optional[typing.Any] = None,
        heatmapsTransitionDuration: typing.Optional[NumberType] = None,
        hexBinPointsData: typing.Optional[typing.Sequence] = None,
        hexLabel: typing.Optional[typing.Any] = None,
        hexBinPointLat: typing.Optional[typing.Any] = None,
        hexBinPointLng: typing.Optional[typing.Any] = None,
        hexBinPointWeight: typing.Optional[typing.Any] = None,
        hexBinResolution: typing.Optional[NumberType] = None,
        hexMargin: typing.Optional[typing.Any] = None,
        hexAltitude: typing.Optional[typing.Any] = None,
        hexTopCurvatureResolution: typing.Optional[NumberType] = None,
        hexTopColor: typing.Optional[typing.Any] = None,
        hexSideColor: typing.Optional[typing.Any] = None,
        hexBinMerge: typing.Optional[bool] = None,
        hexTransitionDuration: typing.Optional[NumberType] = None,
        hexPolygonsData: typing.Optional[typing.Sequence] = None,
        hexPolygonLabel: typing.Optional[typing.Any] = None,
        hexPolygonGeoJsonGeometry: typing.Optional[typing.Any] = None,
        hexPolygonColor: typing.Optional[typing.Any] = None,
        hexPolygonAltitude: typing.Optional[typing.Any] = None,
        hexPolygonResolution: typing.Optional[typing.Any] = None,
        hexPolygonMargin: typing.Optional[typing.Any] = None,
        hexPolygonUseDots: typing.Optional[typing.Any] = None,
        hexPolygonCurvatureResolution: typing.Optional[typing.Any] = None,
        hexPolygonDotResolution: typing.Optional[typing.Any] = None,
        hexPolygonsTransitionDuration: typing.Optional[NumberType] = None,
        tilesData: typing.Optional[typing.Sequence] = None,
        tileLabel: typing.Optional[typing.Any] = None,
        tileLat: typing.Optional[typing.Any] = None,
        tileLng: typing.Optional[typing.Any] = None,
        tileAltitude: typing.Optional[typing.Any] = None,
        tileWidth: typing.Optional[typing.Any] = None,
        tileHeight: typing.Optional[typing.Any] = None,
        tileMaterial: typing.Optional[typing.Any] = None,
        tileUseGlobeProjection: typing.Optional[typing.Any] = None,
        tileCurvatureResolution: typing.Optional[typing.Any] = None,
        tilesTransitionDuration: typing.Optional[NumberType] = None,
        particlesData: typing.Optional[typing.Sequence] = None,
        particlesList: typing.Optional[typing.Any] = None,
        particleLabel: typing.Optional[typing.Any] = None,
        particleLat: typing.Optional[typing.Any] = None,
        particleLng: typing.Optional[typing.Any] = None,
        particleAltitude: typing.Optional[typing.Any] = None,
        particlesSize: typing.Optional[typing.Any] = None,
        particlesSizeAttenuation: typing.Optional[typing.Any] = None,
        particlesColor: typing.Optional[typing.Any] = None,
        ringsData: typing.Optional[typing.Sequence] = None,
        ringLat: typing.Optional[typing.Any] = None,
        ringLng: typing.Optional[typing.Any] = None,
        ringAltitude: typing.Optional[typing.Any] = None,
        ringColor: typing.Optional[typing.Any] = None,
        ringResolution: typing.Optional[NumberType] = None,
        ringMaxRadius: typing.Optional[typing.Any] = None,
        ringPropagationSpeed: typing.Optional[typing.Any] = None,
        ringRepeatPeriod: typing.Optional[typing.Any] = None,
        labelsData: typing.Optional[typing.Sequence] = None,
        labelLabel: typing.Optional[typing.Any] = None,
        labelLat: typing.Optional[typing.Any] = None,
        labelLng: typing.Optional[typing.Any] = None,
        labelText: typing.Optional[typing.Any] = None,
        labelColor: typing.Optional[typing.Any] = None,
        labelAltitude: typing.Optional[typing.Any] = None,
        labelSize: typing.Optional[typing.Any] = None,
        labelRotation: typing.Optional[typing.Any] = None,
        labelResolution: typing.Optional[NumberType] = None,
        labelIncludeDot: typing.Optional[typing.Any] = None,
        labelDotRadius: typing.Optional[typing.Any] = None,
        labelDotOrientation: typing.Optional[typing.Any] = None,
        labelsTransitionDuration: typing.Optional[NumberType] = None,
        clickData: typing.Optional[dict] = None,
        rightClickData: typing.Optional[dict] = None,
        hoverData: typing.Optional[dict] = None,
        currentView: typing.Optional[dict] = None,
        globeReady: typing.Optional[bool] = None,
        lastInteraction: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'animateIn', 'animationPaused', 'arcAltitude', 'arcAltitudeAutoScale', 'arcCircularResolution', 'arcColor', 'arcCurveResolution', 'arcDashAnimateTime', 'arcDashGap', 'arcDashInitialGap', 'arcDashLength', 'arcEndAltitude', 'arcEndLat', 'arcEndLng', 'arcLabel', 'arcStartAltitude', 'arcStartLat', 'arcStartLng', 'arcStroke', 'arcsData', 'arcsTransitionDuration', 'atmosphereAltitude', 'atmosphereColor', 'autoRotate', 'autoRotateSpeed', 'backgroundColor', 'backgroundImageUrl', 'bumpImageUrl', 'cameraPosition', 'cameraTransitionDuration', 'className', 'clearGlobeTileCacheKey', 'clickData', 'clouds', 'cloudsAltitude', 'cloudsImageUrl', 'cloudsOpacity', 'cloudsRotationSpeed', 'currentView', 'dayNightCycle', 'dayNightCycleAnimate', 'dayNightCycleDayImageUrl', 'dayNightCycleMinutesPerSecond', 'dayNightCycleNightImageUrl', 'dayNightCycleTime', 'enablePointerInteraction', 'globeCurvatureResolution', 'globeImageUrl', 'globeOffset', 'globeReady', 'heatmapBandwidth', 'heatmapBaseAltitude', 'heatmapColorSaturation', 'heatmapPointLat', 'heatmapPointLng', 'heatmapPointWeight', 'heatmapPoints', 'heatmapTopAltitude', 'heatmapsData', 'heatmapsTransitionDuration', 'height', 'hexAltitude', 'hexBinMerge', 'hexBinPointLat', 'hexBinPointLng', 'hexBinPointWeight', 'hexBinPointsData', 'hexBinResolution', 'hexLabel', 'hexMargin', 'hexPolygonAltitude', 'hexPolygonColor', 'hexPolygonCurvatureResolution', 'hexPolygonDotResolution', 'hexPolygonGeoJsonGeometry', 'hexPolygonLabel', 'hexPolygonMargin', 'hexPolygonResolution', 'hexPolygonUseDots', 'hexPolygonsData', 'hexPolygonsTransitionDuration', 'hexSideColor', 'hexTopColor', 'hexTopCurvatureResolution', 'hexTransitionDuration', 'hoverData', 'labelAltitude', 'labelColor', 'labelDotOrientation', 'labelDotRadius', 'labelIncludeDot', 'labelLabel', 'labelLat', 'labelLng', 'labelResolution', 'labelRotation', 'labelSize', 'labelText', 'labelsData', 'labelsTransitionDuration', 'lastInteraction', 'lineHoverPrecision', 'particleAltitude', 'particleLabel', 'particleLat', 'particleLng', 'particlesColor', 'particlesData', 'particlesList', 'particlesSize', 'particlesSizeAttenuation', 'pathColor', 'pathDashAnimateTime', 'pathDashGap', 'pathDashInitialGap', 'pathDashLength', 'pathLabel', 'pathPointAlt', 'pathPointLat', 'pathPointLng', 'pathPoints', 'pathResolution', 'pathStroke', 'pathTransitionDuration', 'pathsData', 'pointAltitude', 'pointColor', 'pointLabel', 'pointLat', 'pointLng', 'pointRadius', 'pointResolution', 'pointsData', 'pointsMerge', 'pointsTransitionDuration', 'polygonAltitude', 'polygonCapColor', 'polygonCapCurvatureResolution', 'polygonCapMaterial', 'polygonGeoJsonGeometry', 'polygonHoverAltitude', 'polygonHoverCapColor', 'polygonHoverKey', 'polygonHoverSideColor', 'polygonHoverStrokeColor', 'polygonLabel', 'polygonSideColor', 'polygonSideMaterial', 'polygonStrokeColor', 'polygonsData', 'polygonsTransitionDuration', 'rendererConfig', 'responsive', 'rightClickData', 'ringAltitude', 'ringColor', 'ringLat', 'ringLng', 'ringMaxRadius', 'ringPropagationSpeed', 'ringRepeatPeriod', 'ringResolution', 'ringsData', 'showAtmosphere', 'showGlobe', 'showGraticules', 'showPointerCursor', 'style', 'tileAltitude', 'tileCurvatureResolution', 'tileHeight', 'tileLabel', 'tileLat', 'tileLng', 'tileMaterial', 'tileUseGlobeProjection', 'tileWidth', 'tilesData', 'tilesTransitionDuration', 'waitForGlobeReady', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'animateIn', 'animationPaused', 'arcAltitude', 'arcAltitudeAutoScale', 'arcCircularResolution', 'arcColor', 'arcCurveResolution', 'arcDashAnimateTime', 'arcDashGap', 'arcDashInitialGap', 'arcDashLength', 'arcEndAltitude', 'arcEndLat', 'arcEndLng', 'arcLabel', 'arcStartAltitude', 'arcStartLat', 'arcStartLng', 'arcStroke', 'arcsData', 'arcsTransitionDuration', 'atmosphereAltitude', 'atmosphereColor', 'autoRotate', 'autoRotateSpeed', 'backgroundColor', 'backgroundImageUrl', 'bumpImageUrl', 'cameraPosition', 'cameraTransitionDuration', 'className', 'clearGlobeTileCacheKey', 'clickData', 'clouds', 'cloudsAltitude', 'cloudsImageUrl', 'cloudsOpacity', 'cloudsRotationSpeed', 'currentView', 'dayNightCycle', 'dayNightCycleAnimate', 'dayNightCycleDayImageUrl', 'dayNightCycleMinutesPerSecond', 'dayNightCycleNightImageUrl', 'dayNightCycleTime', 'enablePointerInteraction', 'globeCurvatureResolution', 'globeImageUrl', 'globeOffset', 'globeReady', 'heatmapBandwidth', 'heatmapBaseAltitude', 'heatmapColorSaturation', 'heatmapPointLat', 'heatmapPointLng', 'heatmapPointWeight', 'heatmapPoints', 'heatmapTopAltitude', 'heatmapsData', 'heatmapsTransitionDuration', 'height', 'hexAltitude', 'hexBinMerge', 'hexBinPointLat', 'hexBinPointLng', 'hexBinPointWeight', 'hexBinPointsData', 'hexBinResolution', 'hexLabel', 'hexMargin', 'hexPolygonAltitude', 'hexPolygonColor', 'hexPolygonCurvatureResolution', 'hexPolygonDotResolution', 'hexPolygonGeoJsonGeometry', 'hexPolygonLabel', 'hexPolygonMargin', 'hexPolygonResolution', 'hexPolygonUseDots', 'hexPolygonsData', 'hexPolygonsTransitionDuration', 'hexSideColor', 'hexTopColor', 'hexTopCurvatureResolution', 'hexTransitionDuration', 'hoverData', 'labelAltitude', 'labelColor', 'labelDotOrientation', 'labelDotRadius', 'labelIncludeDot', 'labelLabel', 'labelLat', 'labelLng', 'labelResolution', 'labelRotation', 'labelSize', 'labelText', 'labelsData', 'labelsTransitionDuration', 'lastInteraction', 'lineHoverPrecision', 'particleAltitude', 'particleLabel', 'particleLat', 'particleLng', 'particlesColor', 'particlesData', 'particlesList', 'particlesSize', 'particlesSizeAttenuation', 'pathColor', 'pathDashAnimateTime', 'pathDashGap', 'pathDashInitialGap', 'pathDashLength', 'pathLabel', 'pathPointAlt', 'pathPointLat', 'pathPointLng', 'pathPoints', 'pathResolution', 'pathStroke', 'pathTransitionDuration', 'pathsData', 'pointAltitude', 'pointColor', 'pointLabel', 'pointLat', 'pointLng', 'pointRadius', 'pointResolution', 'pointsData', 'pointsMerge', 'pointsTransitionDuration', 'polygonAltitude', 'polygonCapColor', 'polygonCapCurvatureResolution', 'polygonCapMaterial', 'polygonGeoJsonGeometry', 'polygonHoverAltitude', 'polygonHoverCapColor', 'polygonHoverKey', 'polygonHoverSideColor', 'polygonHoverStrokeColor', 'polygonLabel', 'polygonSideColor', 'polygonSideMaterial', 'polygonStrokeColor', 'polygonsData', 'polygonsTransitionDuration', 'rendererConfig', 'responsive', 'rightClickData', 'ringAltitude', 'ringColor', 'ringLat', 'ringLng', 'ringMaxRadius', 'ringPropagationSpeed', 'ringRepeatPeriod', 'ringResolution', 'ringsData', 'showAtmosphere', 'showGlobe', 'showGraticules', 'showPointerCursor', 'style', 'tileAltitude', 'tileCurvatureResolution', 'tileHeight', 'tileLabel', 'tileLat', 'tileLng', 'tileMaterial', 'tileUseGlobeProjection', 'tileWidth', 'tilesData', 'tilesTransitionDuration', 'waitForGlobeReady', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashGlobe, self).__init__(**args)

setattr(DashGlobe, "__init__", _explicitize_args(DashGlobe.__init__))
