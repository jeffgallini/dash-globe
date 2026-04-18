# AUTO GENERATED FILE - DO NOT EDIT

export ''_dashglobe

"""
    ''_dashglobe(;kwargs...)
    ''_dashglobe(children::Any;kwargs...)
    ''_dashglobe(children_maker::Function;kwargs...)


A DashGlobe component.
Dash wrapper around react-globe.gl.

The component focuses on the JSON-serialisable portion of the upstream API so
it can be configured naturally from Python.
Keyword arguments:
- `children` (a list of or a singular dash component, string or number; optional): Dash components rendered as geo-anchored HTML overlays. Children are
matched to htmlElementsData by index.
- `id` (String | Dict; optional): The ID used to identify this component in Dash callbacks.
- `animateIn` (Bool; optional)
- `animationPaused` (Bool; optional)
- `arcAltitude` (Bool | Real | String | Dict | Array; optional)
- `arcAltitudeAutoScale` (Bool | Real | String | Dict | Array; optional)
- `arcCircularResolution` (Real; optional)
- `arcColor` (Bool | Real | String | Dict | Array; optional)
- `arcCurveResolution` (Real; optional)
- `arcDashAnimateTime` (Bool | Real | String | Dict | Array; optional)
- `arcDashGap` (Bool | Real | String | Dict | Array; optional)
- `arcDashInitialGap` (Bool | Real | String | Dict | Array; optional)
- `arcDashLength` (Bool | Real | String | Dict | Array; optional)
- `arcEndAltitude` (Bool | Real | String | Dict | Array; optional)
- `arcEndLat` (Bool | Real | String | Dict | Array; optional)
- `arcEndLng` (Bool | Real | String | Dict | Array; optional)
- `arcLabel` (Bool | Real | String | Dict | Array; optional)
- `arcStartAltitude` (Bool | Real | String | Dict | Array; optional)
- `arcStartLat` (Bool | Real | String | Dict | Array; optional)
- `arcStartLng` (Bool | Real | String | Dict | Array; optional)
- `arcStroke` (Bool | Real | String | Dict | Array; optional)
- `arcsData` (Array; optional): Arc layer data and accessors.
- `arcsTransitionDuration` (Real; optional)
- `atmosphereAltitude` (Real; optional)
- `atmosphereColor` (String; optional)
- `autoRotate` (Bool; optional)
- `autoRotateSpeed` (Real; optional)
- `backgroundColor` (String; optional)
- `backgroundImageUrl` (String; optional)
- `bumpImageUrl` (String; optional)
- `cameraPosition` (Dict; optional): Target camera position in geographic coordinates.
- `cameraTransitionDuration` (Real; optional)
- `className` (String; optional): CSS class applied to the outer wrapper.
- `clearGlobeTileCacheKey` (Bool | Real | String | Dict | Array; optional)
- `clickData` (Dict; optional): Last click event payload emitted by any supported layer.
- `clouds` (Bool; optional)
- `cloudsAltitude` (Real; optional)
- `cloudsImageUrl` (String; optional)
- `cloudsOpacity` (Real; optional)
- `cloudsRotationSpeed` (Real; optional)
- `currentView` (Dict; optional): Current point of view reported by zoom and rotation interactions.
- `dayNightCycle` (Bool; optional)
- `dayNightCycleAnimate` (Bool; optional)
- `dayNightCycleDayImageUrl` (String; optional)
- `dayNightCycleMinutesPerSecond` (Real; optional)
- `dayNightCycleNightImageUrl` (String; optional)
- `dayNightCycleTime` (Bool | Real | String | Dict | Array; optional)
- `enablePointerInteraction` (Bool; optional)
- `globeCurvatureResolution` (Real; optional)
- `globeImageUrl` (String; optional)
- `globeOffset` (Array; optional): Position offset of the globe relative to the canvas centre.
- `globeReady` (Bool; optional): Whether the globe has finished initialising.
- `heatmapBandwidth` (Bool | Real | String | Dict | Array; optional)
- `heatmapBaseAltitude` (Bool | Real | String | Dict | Array; optional)
- `heatmapColorSaturation` (Bool | Real | String | Dict | Array; optional)
- `heatmapPointLat` (Bool | Real | String | Dict | Array; optional)
- `heatmapPointLng` (Bool | Real | String | Dict | Array; optional)
- `heatmapPointWeight` (Bool | Real | String | Dict | Array; optional)
- `heatmapPoints` (Bool | Real | String | Dict | Array; optional)
- `heatmapTopAltitude` (Bool | Real | String | Dict | Array; optional)
- `heatmapsData` (Array; optional): Heatmap layer data and accessors.
- `heatmapsTransitionDuration` (Real; optional)
- `height` (Real; optional): Canvas height in pixels.
- `hexAltitude` (Bool | Real | String | Dict | Array; optional)
- `hexBinMerge` (Bool; optional)
- `hexBinPointLat` (Bool | Real | String | Dict | Array; optional)
- `hexBinPointLng` (Bool | Real | String | Dict | Array; optional)
- `hexBinPointWeight` (Bool | Real | String | Dict | Array; optional)
- `hexBinPointsData` (Array; optional): Hex bin layer data and accessors.
- `hexBinResolution` (Real; optional)
- `hexLabel` (Bool | Real | String | Dict | Array; optional)
- `hexMargin` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonAltitude` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonColor` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonCurvatureResolution` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonDotResolution` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonGeoJsonGeometry` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonLabel` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonMargin` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonResolution` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonUseDots` (Bool | Real | String | Dict | Array; optional)
- `hexPolygonsData` (Array; optional): Hexed polygon layer data and accessors.
- `hexPolygonsTransitionDuration` (Real; optional)
- `hexSideColor` (Bool | Real | String | Dict | Array; optional)
- `hexTopColor` (Bool | Real | String | Dict | Array; optional)
- `hexTopCurvatureResolution` (Real; optional)
- `hexTransitionDuration` (Real; optional)
- `hoverData` (Dict; optional): Last hover event payload emitted by any supported layer.
- `htmlElementAltitude` (Bool | Real | String | Dict | Array; optional)
- `htmlElementHidden` (Bool | Real | String | Dict | Array; optional)
- `htmlElementKey` (Bool | Real | String | Dict | Array; optional)
- `htmlElementLat` (Bool | Real | String | Dict | Array; optional)
- `htmlElementLng` (Bool | Real | String | Dict | Array; optional)
- `htmlElementOffsetX` (Bool | Real | String | Dict | Array; optional)
- `htmlElementOffsetY` (Bool | Real | String | Dict | Array; optional)
- `htmlElementPointerEvents` (Bool | Real | String | Dict | Array; optional)
- `htmlElementsData` (Array; optional): Geo-anchored HTML overlay data. Children are projected onto the globe by
matching each child to a data item with the same index.
- `labelAltitude` (Bool | Real | String | Dict | Array; optional)
- `labelColor` (Bool | Real | String | Dict | Array; optional)
- `labelDotOrientation` (Bool | Real | String | Dict | Array; optional)
- `labelDotRadius` (Bool | Real | String | Dict | Array; optional)
- `labelIncludeDot` (Bool | Real | String | Dict | Array; optional)
- `labelLabel` (Bool | Real | String | Dict | Array; optional)
- `labelLat` (Bool | Real | String | Dict | Array; optional)
- `labelLng` (Bool | Real | String | Dict | Array; optional)
- `labelResolution` (Real; optional)
- `labelRotation` (Bool | Real | String | Dict | Array; optional)
- `labelSize` (Bool | Real | String | Dict | Array; optional)
- `labelText` (Bool | Real | String | Dict | Array; optional)
- `labelsData` (Array; optional): Label layer data and accessors.
- `labelsTransitionDuration` (Real; optional)
- `lastInteraction` (Dict; optional): The most recent interaction payload emitted by the component.
- `lineHoverPrecision` (Real; optional)
- `particleAltitude` (Bool | Real | String | Dict | Array; optional)
- `particleLabel` (Bool | Real | String | Dict | Array; optional)
- `particleLat` (Bool | Real | String | Dict | Array; optional)
- `particleLng` (Bool | Real | String | Dict | Array; optional)
- `particlesColor` (Bool | Real | String | Dict | Array; optional)
- `particlesData` (Array; optional): Particle layer data and accessors.
- `particlesList` (Bool | Real | String | Dict | Array; optional)
- `particlesSize` (Bool | Real | String | Dict | Array; optional)
- `particlesSizeAttenuation` (Bool | Real | String | Dict | Array; optional)
- `pathColor` (Bool | Real | String | Dict | Array; optional)
- `pathDashAnimateTime` (Bool | Real | String | Dict | Array; optional)
- `pathDashGap` (Bool | Real | String | Dict | Array; optional)
- `pathDashInitialGap` (Bool | Real | String | Dict | Array; optional)
- `pathDashLength` (Bool | Real | String | Dict | Array; optional)
- `pathLabel` (Bool | Real | String | Dict | Array; optional)
- `pathPointAlt` (Bool | Real | String | Dict | Array; optional)
- `pathPointLat` (Bool | Real | String | Dict | Array; optional)
- `pathPointLng` (Bool | Real | String | Dict | Array; optional)
- `pathPoints` (Bool | Real | String | Dict | Array; optional)
- `pathResolution` (Real; optional)
- `pathStroke` (Bool | Real | String | Dict | Array; optional)
- `pathTransitionDuration` (Real; optional)
- `pathsData` (Array; optional): Path layer data and accessors.
- `pointAltitude` (Bool | Real | String | Dict | Array; optional)
- `pointColor` (Bool | Real | String | Dict | Array; optional)
- `pointLabel` (Bool | Real | String | Dict | Array; optional)
- `pointLat` (Bool | Real | String | Dict | Array; optional)
- `pointLng` (Bool | Real | String | Dict | Array; optional)
- `pointRadius` (Bool | Real | String | Dict | Array; optional)
- `pointResolution` (Real; optional)
- `pointsData` (Array; optional): Point layer data and accessors.
- `pointsMerge` (Bool; optional)
- `pointsTransitionDuration` (Real; optional)
- `polygonAltitude` (Bool | Real | String | Dict | Array; optional)
- `polygonCapColor` (Bool | Real | String | Dict | Array; optional)
- `polygonCapCurvatureResolution` (Bool | Real | String | Dict | Array; optional)
- `polygonCapMaterial` (Bool | Real | String | Dict | Array; optional)
- `polygonGeoJsonGeometry` (Bool | Real | String | Dict | Array; optional)
- `polygonHoverAltitude` (Bool | Real | String | Dict | Array; optional)
- `polygonHoverCapColor` (Bool | Real | String | Dict | Array; optional)
- `polygonHoverKey` (Bool | Real | String | Dict | Array; optional)
- `polygonHoverSideColor` (Bool | Real | String | Dict | Array; optional)
- `polygonHoverStrokeColor` (Bool | Real | String | Dict | Array; optional)
- `polygonLabel` (Bool | Real | String | Dict | Array; optional)
- `polygonSideColor` (Bool | Real | String | Dict | Array; optional)
- `polygonSideMaterial` (Bool | Real | String | Dict | Array; optional)
- `polygonStrokeColor` (Bool | Real | String | Dict | Array; optional)
- `polygonsData` (Array; optional): Polygon layer data and accessors.
- `polygonsTransitionDuration` (Real; optional)
- `rendererConfig` (Dict; optional)
- `responsive` (Bool; optional): Automatically size the globe from its container with ResizeObserver.
- `rightClickData` (Dict; optional): Last right click event payload emitted by any supported layer.
- `ringAltitude` (Bool | Real | String | Dict | Array; optional)
- `ringColor` (Bool | Real | String | Dict | Array; optional)
- `ringLat` (Bool | Real | String | Dict | Array; optional)
- `ringLng` (Bool | Real | String | Dict | Array; optional)
- `ringMaxRadius` (Bool | Real | String | Dict | Array; optional)
- `ringPropagationSpeed` (Bool | Real | String | Dict | Array; optional)
- `ringRepeatPeriod` (Bool | Real | String | Dict | Array; optional)
- `ringResolution` (Real; optional)
- `ringsData` (Array; optional): Ring layer data and accessors.
- `showAtmosphere` (Bool; optional)
- `showGlobe` (Bool; optional)
- `showGraticules` (Bool; optional)
- `showPointerCursor` (Bool; optional)
- `style` (Dict; optional): Inline styles for the outer wrapper.
- `tileAltitude` (Bool | Real | String | Dict | Array; optional)
- `tileCurvatureResolution` (Bool | Real | String | Dict | Array; optional)
- `tileHeight` (Bool | Real | String | Dict | Array; optional)
- `tileLabel` (Bool | Real | String | Dict | Array; optional)
- `tileLat` (Bool | Real | String | Dict | Array; optional)
- `tileLng` (Bool | Real | String | Dict | Array; optional)
- `tileMaterial` (Bool | Real | String | Dict | Array; optional)
- `tileUseGlobeProjection` (Bool | Real | String | Dict | Array; optional)
- `tileWidth` (Bool | Real | String | Dict | Array; optional)
- `tilesData` (Array; optional): Tile layer data and accessors.
- `tilesTransitionDuration` (Real; optional)
- `waitForGlobeReady` (Bool; optional)
- `width` (Real; optional): Canvas width in pixels.
"""
function ''_dashglobe(; kwargs...)
        available_props = Symbol[:children, :id, :animateIn, :animationPaused, :arcAltitude, :arcAltitudeAutoScale, :arcCircularResolution, :arcColor, :arcCurveResolution, :arcDashAnimateTime, :arcDashGap, :arcDashInitialGap, :arcDashLength, :arcEndAltitude, :arcEndLat, :arcEndLng, :arcLabel, :arcStartAltitude, :arcStartLat, :arcStartLng, :arcStroke, :arcsData, :arcsTransitionDuration, :atmosphereAltitude, :atmosphereColor, :autoRotate, :autoRotateSpeed, :backgroundColor, :backgroundImageUrl, :bumpImageUrl, :cameraPosition, :cameraTransitionDuration, :className, :clearGlobeTileCacheKey, :clickData, :clouds, :cloudsAltitude, :cloudsImageUrl, :cloudsOpacity, :cloudsRotationSpeed, :currentView, :dayNightCycle, :dayNightCycleAnimate, :dayNightCycleDayImageUrl, :dayNightCycleMinutesPerSecond, :dayNightCycleNightImageUrl, :dayNightCycleTime, :enablePointerInteraction, :globeCurvatureResolution, :globeImageUrl, :globeOffset, :globeReady, :heatmapBandwidth, :heatmapBaseAltitude, :heatmapColorSaturation, :heatmapPointLat, :heatmapPointLng, :heatmapPointWeight, :heatmapPoints, :heatmapTopAltitude, :heatmapsData, :heatmapsTransitionDuration, :height, :hexAltitude, :hexBinMerge, :hexBinPointLat, :hexBinPointLng, :hexBinPointWeight, :hexBinPointsData, :hexBinResolution, :hexLabel, :hexMargin, :hexPolygonAltitude, :hexPolygonColor, :hexPolygonCurvatureResolution, :hexPolygonDotResolution, :hexPolygonGeoJsonGeometry, :hexPolygonLabel, :hexPolygonMargin, :hexPolygonResolution, :hexPolygonUseDots, :hexPolygonsData, :hexPolygonsTransitionDuration, :hexSideColor, :hexTopColor, :hexTopCurvatureResolution, :hexTransitionDuration, :hoverData, :htmlElementAltitude, :htmlElementHidden, :htmlElementKey, :htmlElementLat, :htmlElementLng, :htmlElementOffsetX, :htmlElementOffsetY, :htmlElementPointerEvents, :htmlElementsData, :labelAltitude, :labelColor, :labelDotOrientation, :labelDotRadius, :labelIncludeDot, :labelLabel, :labelLat, :labelLng, :labelResolution, :labelRotation, :labelSize, :labelText, :labelsData, :labelsTransitionDuration, :lastInteraction, :lineHoverPrecision, :particleAltitude, :particleLabel, :particleLat, :particleLng, :particlesColor, :particlesData, :particlesList, :particlesSize, :particlesSizeAttenuation, :pathColor, :pathDashAnimateTime, :pathDashGap, :pathDashInitialGap, :pathDashLength, :pathLabel, :pathPointAlt, :pathPointLat, :pathPointLng, :pathPoints, :pathResolution, :pathStroke, :pathTransitionDuration, :pathsData, :pointAltitude, :pointColor, :pointLabel, :pointLat, :pointLng, :pointRadius, :pointResolution, :pointsData, :pointsMerge, :pointsTransitionDuration, :polygonAltitude, :polygonCapColor, :polygonCapCurvatureResolution, :polygonCapMaterial, :polygonGeoJsonGeometry, :polygonHoverAltitude, :polygonHoverCapColor, :polygonHoverKey, :polygonHoverSideColor, :polygonHoverStrokeColor, :polygonLabel, :polygonSideColor, :polygonSideMaterial, :polygonStrokeColor, :polygonsData, :polygonsTransitionDuration, :rendererConfig, :responsive, :rightClickData, :ringAltitude, :ringColor, :ringLat, :ringLng, :ringMaxRadius, :ringPropagationSpeed, :ringRepeatPeriod, :ringResolution, :ringsData, :showAtmosphere, :showGlobe, :showGraticules, :showPointerCursor, :style, :tileAltitude, :tileCurvatureResolution, :tileHeight, :tileLabel, :tileLat, :tileLng, :tileMaterial, :tileUseGlobeProjection, :tileWidth, :tilesData, :tilesTransitionDuration, :waitForGlobeReady, :width]
        wild_props = Symbol[]
        return Component("''_dashglobe", "DashGlobe", "dash_globe", available_props, wild_props; kwargs...)
end

''_dashglobe(children::Any; kwargs...) = ''_dashglobe(;kwargs..., children = children)
''_dashglobe(children_maker::Function; kwargs...) = ''_dashglobe(children_maker(); kwargs...)

