import React from 'react';
import PropTypes from 'prop-types';
import { DashGlobe as RealComponent } from '../LazyLoader';

/**
 * Dash wrapper around react-globe.gl.
 *
 * The component focuses on the JSON-serialisable portion of the upstream API so
 * it can be configured naturally from Python.
 */
const DashGlobe = (props) => (
    <React.Suspense fallback={null}>
        <RealComponent {...props} />
    </React.Suspense>
);

DashGlobe.defaultProps = {
    responsive: true,
    waitForGlobeReady: true,
    animateIn: true,
    showGlobe: true,
    showAtmosphere: true,
    dayNightCycleAnimate: true,
    dayNightCycleMinutesPerSecond: 60,
    cloudsAltitude: 0.004,
    cloudsRotationSpeed: -0.006,
    cloudsOpacity: 1,
    cameraTransitionDuration: 0,
    animationPaused: false,
    currentViewReportInterval: 250
};

DashGlobe.propTypes = {
    /**
     * Dash components rendered as geo-anchored HTML overlays. Children are
     * matched to htmlElementsData by index.
     */
    children: PropTypes.node,

    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),

    /**
     * CSS class applied to the outer wrapper.
     */
    className: PropTypes.string,

    /**
     * Inline styles for the outer wrapper.
     */
    style: PropTypes.object,

    /**
     * Automatically size the globe from its container with ResizeObserver.
     */
    responsive: PropTypes.bool,

    /**
     * Canvas width in pixels.
     */
    width: PropTypes.number,

    /**
     * Canvas height in pixels.
     */
    height: PropTypes.number,

    /**
     * Position offset of the globe relative to the canvas centre.
     */
    globeOffset: PropTypes.array,
    backgroundColor: PropTypes.string,
    backgroundImageUrl: PropTypes.string,
    waitForGlobeReady: PropTypes.bool,
    animateIn: PropTypes.bool,
    globeImageUrl: PropTypes.string,
    bumpImageUrl: PropTypes.string,
    showGlobe: PropTypes.bool,
    showGraticules: PropTypes.bool,
    showAtmosphere: PropTypes.bool,
    atmosphereColor: PropTypes.string,
    atmosphereAltitude: PropTypes.number,
    globeCurvatureResolution: PropTypes.number,
    dayNightCycle: PropTypes.bool,
    dayNightCycleDayImageUrl: PropTypes.string,
    dayNightCycleNightImageUrl: PropTypes.string,
    dayNightCycleTime: PropTypes.any,
    dayNightCycleAnimate: PropTypes.bool,
    dayNightCycleMinutesPerSecond: PropTypes.number,
    autoRotate: PropTypes.bool,
    autoRotateSpeed: PropTypes.number,
    clouds: PropTypes.bool,
    cloudsImageUrl: PropTypes.string,
    cloudsAltitude: PropTypes.number,
    cloudsRotationSpeed: PropTypes.number,
    cloudsOpacity: PropTypes.number,

    /**
     * Target camera position in geographic coordinates.
     */
    cameraPosition: PropTypes.object,
    cameraTransitionDuration: PropTypes.number,
    animationPaused: PropTypes.bool,
    clearGlobeTileCacheKey: PropTypes.any,
    rendererConfig: PropTypes.object,
    enablePointerInteraction: PropTypes.bool,
    lineHoverPrecision: PropTypes.number,
    showPointerCursor: PropTypes.bool,
    currentViewReportInterval: PropTypes.number,

    /**
     * Point layer data and accessors.
     */
    pointsData: PropTypes.array,
    pointLabel: PropTypes.any,
    pointLat: PropTypes.any,
    pointLng: PropTypes.any,
    pointColor: PropTypes.any,
    pointAltitude: PropTypes.any,
    pointRadius: PropTypes.any,
    pointResolution: PropTypes.number,
    pointsMerge: PropTypes.bool,
    pointsTransitionDuration: PropTypes.number,

    /**
     * Arc layer data and accessors.
     */
    arcsData: PropTypes.array,
    arcLabel: PropTypes.any,
    arcStartLat: PropTypes.any,
    arcStartLng: PropTypes.any,
    arcStartAltitude: PropTypes.any,
    arcEndLat: PropTypes.any,
    arcEndLng: PropTypes.any,
    arcEndAltitude: PropTypes.any,
    arcColor: PropTypes.any,
    arcAltitude: PropTypes.any,
    arcAltitudeAutoScale: PropTypes.any,
    arcStroke: PropTypes.any,
    arcCurveResolution: PropTypes.number,
    arcCircularResolution: PropTypes.number,
    arcDashLength: PropTypes.any,
    arcDashGap: PropTypes.any,
    arcDashInitialGap: PropTypes.any,
    arcDashAnimateTime: PropTypes.any,
    arcsTransitionDuration: PropTypes.number,

    /**
     * Polygon layer data and accessors.
     */
    polygonsData: PropTypes.array,
    polygonLabel: PropTypes.any,
    polygonGeoJsonGeometry: PropTypes.any,
    polygonCapMaterial: PropTypes.any,
    polygonCapColor: PropTypes.any,
    polygonSideMaterial: PropTypes.any,
    polygonSideColor: PropTypes.any,
    polygonStrokeColor: PropTypes.any,
    polygonAltitude: PropTypes.any,
    polygonHoverKey: PropTypes.any,
    polygonHoverAltitude: PropTypes.any,
    polygonHoverCapColor: PropTypes.any,
    polygonHoverSideColor: PropTypes.any,
    polygonHoverStrokeColor: PropTypes.any,
    polygonCapCurvatureResolution: PropTypes.any,
    polygonsTransitionDuration: PropTypes.number,

    /**
     * Path layer data and accessors.
     */
    pathsData: PropTypes.array,
    pathLabel: PropTypes.any,
    pathPoints: PropTypes.any,
    pathPointLat: PropTypes.any,
    pathPointLng: PropTypes.any,
    pathPointAlt: PropTypes.any,
    pathResolution: PropTypes.number,
    pathColor: PropTypes.any,
    pathStroke: PropTypes.any,
    pathDashLength: PropTypes.any,
    pathDashGap: PropTypes.any,
    pathDashInitialGap: PropTypes.any,
    pathDashAnimateTime: PropTypes.any,
    pathTransitionDuration: PropTypes.number,

    /**
     * Heatmap layer data and accessors.
     */
    heatmapsData: PropTypes.array,
    heatmapPoints: PropTypes.any,
    heatmapPointLat: PropTypes.any,
    heatmapPointLng: PropTypes.any,
    heatmapPointWeight: PropTypes.any,
    heatmapBandwidth: PropTypes.any,
    heatmapColorSaturation: PropTypes.any,
    heatmapBaseAltitude: PropTypes.any,
    heatmapTopAltitude: PropTypes.any,
    heatmapsTransitionDuration: PropTypes.number,

    /**
     * Hex bin layer data and accessors.
     */
    hexBinPointsData: PropTypes.array,
    hexLabel: PropTypes.any,
    hexBinPointLat: PropTypes.any,
    hexBinPointLng: PropTypes.any,
    hexBinPointWeight: PropTypes.any,
    hexBinResolution: PropTypes.number,
    hexMargin: PropTypes.any,
    hexAltitude: PropTypes.any,
    hexTopCurvatureResolution: PropTypes.number,
    hexTopColor: PropTypes.any,
    hexSideColor: PropTypes.any,
    hexBinMerge: PropTypes.bool,
    hexTransitionDuration: PropTypes.number,

    /**
     * Hexed polygon layer data and accessors.
     */
    hexPolygonsData: PropTypes.array,
    hexPolygonLabel: PropTypes.any,
    hexPolygonGeoJsonGeometry: PropTypes.any,
    hexPolygonColor: PropTypes.any,
    hexPolygonAltitude: PropTypes.any,
    hexPolygonResolution: PropTypes.any,
    hexPolygonMargin: PropTypes.any,
    hexPolygonUseDots: PropTypes.any,
    hexPolygonCurvatureResolution: PropTypes.any,
    hexPolygonDotResolution: PropTypes.any,
    hexPolygonsTransitionDuration: PropTypes.number,

    /**
     * Tile layer data and accessors.
     */
    tilesData: PropTypes.array,
    tileLabel: PropTypes.any,
    tileLat: PropTypes.any,
    tileLng: PropTypes.any,
    tileAltitude: PropTypes.any,
    tileWidth: PropTypes.any,
    tileHeight: PropTypes.any,
    tileMaterial: PropTypes.any,
    tileUseGlobeProjection: PropTypes.any,
    tileCurvatureResolution: PropTypes.any,
    tilesTransitionDuration: PropTypes.number,

    /**
     * Particle layer data and accessors.
     */
    particlesData: PropTypes.array,
    particlesList: PropTypes.any,
    particleLabel: PropTypes.any,
    particleLat: PropTypes.any,
    particleLng: PropTypes.any,
    particleAltitude: PropTypes.any,
    particlesSize: PropTypes.any,
    particlesSizeAttenuation: PropTypes.any,
    particlesColor: PropTypes.any,

    /**
     * Ring layer data and accessors.
     */
    ringsData: PropTypes.array,
    ringLat: PropTypes.any,
    ringLng: PropTypes.any,
    ringAltitude: PropTypes.any,
    ringColor: PropTypes.any,
    ringResolution: PropTypes.number,
    ringMaxRadius: PropTypes.any,
    ringPropagationSpeed: PropTypes.any,
    ringRepeatPeriod: PropTypes.any,

    /**
     * Label layer data and accessors.
     */
    labelsData: PropTypes.array,
    labelLabel: PropTypes.any,
    labelLat: PropTypes.any,
    labelLng: PropTypes.any,
    labelText: PropTypes.any,
    labelColor: PropTypes.any,
    labelAltitude: PropTypes.any,
    labelSize: PropTypes.any,
    labelRotation: PropTypes.any,
    labelResolution: PropTypes.number,
    labelIncludeDot: PropTypes.any,
    labelDotRadius: PropTypes.any,
    labelDotOrientation: PropTypes.any,
    labelsTransitionDuration: PropTypes.number,

    /**
     * Geo-anchored HTML overlay data. Children are projected onto the globe by
     * matching each child to a data item with the same index.
     */
    htmlElementsData: PropTypes.array,
    htmlElementLat: PropTypes.any,
    htmlElementLng: PropTypes.any,
    htmlElementAltitude: PropTypes.any,
    htmlElementKey: PropTypes.any,
    htmlElementOffsetX: PropTypes.any,
    htmlElementOffsetY: PropTypes.any,
    htmlElementPointerEvents: PropTypes.any,
    htmlElementHidden: PropTypes.any,
    htmlElementScreenX: PropTypes.any,
    htmlElementScreenY: PropTypes.any,
    htmlElementScreenSide: PropTypes.any,
    htmlElementTether: PropTypes.any,
    htmlElementTetherColor: PropTypes.any,
    htmlElementTetherWidth: PropTypes.any,
    htmlElementTetherAttach: PropTypes.any,

    /**
     * Last click event payload emitted by any supported layer.
     */
    clickData: PropTypes.object,

    /**
     * Last right click event payload emitted by any supported layer.
     */
    rightClickData: PropTypes.object,

    /**
     * Last hover event payload emitted by any supported layer.
     */
    hoverData: PropTypes.object,

    /**
     * Current point of view reported by zoom and rotation interactions.
     */
    currentView: PropTypes.object,

    /**
     * Whether the globe has finished initialising.
     */
    globeReady: PropTypes.bool,

    /**
     * The most recent interaction payload emitted by the component.
     */
    lastInteraction: PropTypes.object,

    /**
     * Dash-assigned callback used to report prop changes back to Python.
     */
    setProps: PropTypes.func
};

export default DashGlobe;

export const defaultProps = DashGlobe.defaultProps;
export const propTypes = DashGlobe.propTypes;
