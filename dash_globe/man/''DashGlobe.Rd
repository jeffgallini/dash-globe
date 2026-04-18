% Auto-generated: do not edit by hand
\name{''DashGlobe}

\alias{''DashGlobe}

\title{DashGlobe component}

\description{
Dash wrapper around react-globe.gl.  The component focuses on the JSON-serialisable portion of the upstream API so it can be configured naturally from Python.
}

\usage{
''DashGlobe(children=NULL, id=NULL, animateIn=NULL,
animationPaused=NULL, arcAltitude=NULL,
arcAltitudeAutoScale=NULL, arcCircularResolution=NULL,
arcColor=NULL, arcCurveResolution=NULL,
arcDashAnimateTime=NULL, arcDashGap=NULL,
arcDashInitialGap=NULL, arcDashLength=NULL,
arcEndAltitude=NULL, arcEndLat=NULL, arcEndLng=NULL,
arcLabel=NULL, arcStartAltitude=NULL, arcStartLat=NULL,
arcStartLng=NULL, arcStroke=NULL, arcsData=NULL,
arcsTransitionDuration=NULL, atmosphereAltitude=NULL,
atmosphereColor=NULL, autoRotate=NULL, autoRotateSpeed=NULL,
backgroundColor=NULL, backgroundImageUrl=NULL,
bumpImageUrl=NULL, cameraPosition=NULL,
cameraTransitionDuration=NULL, className=NULL,
clearGlobeTileCacheKey=NULL, clickData=NULL, clouds=NULL,
cloudsAltitude=NULL, cloudsImageUrl=NULL,
cloudsOpacity=NULL, cloudsRotationSpeed=NULL,
currentView=NULL, dayNightCycle=NULL,
dayNightCycleAnimate=NULL, dayNightCycleDayImageUrl=NULL,
dayNightCycleMinutesPerSecond=NULL,
dayNightCycleNightImageUrl=NULL, dayNightCycleTime=NULL,
enablePointerInteraction=NULL,
globeCurvatureResolution=NULL, globeImageUrl=NULL,
globeOffset=NULL, globeReady=NULL, heatmapBandwidth=NULL,
heatmapBaseAltitude=NULL, heatmapColorSaturation=NULL,
heatmapPointLat=NULL, heatmapPointLng=NULL,
heatmapPointWeight=NULL, heatmapPoints=NULL,
heatmapTopAltitude=NULL, heatmapsData=NULL,
heatmapsTransitionDuration=NULL, height=NULL,
hexAltitude=NULL, hexBinMerge=NULL, hexBinPointLat=NULL,
hexBinPointLng=NULL, hexBinPointWeight=NULL,
hexBinPointsData=NULL, hexBinResolution=NULL, hexLabel=NULL,
hexMargin=NULL, hexPolygonAltitude=NULL,
hexPolygonColor=NULL, hexPolygonCurvatureResolution=NULL,
hexPolygonDotResolution=NULL,
hexPolygonGeoJsonGeometry=NULL, hexPolygonLabel=NULL,
hexPolygonMargin=NULL, hexPolygonResolution=NULL,
hexPolygonUseDots=NULL, hexPolygonsData=NULL,
hexPolygonsTransitionDuration=NULL, hexSideColor=NULL,
hexTopColor=NULL, hexTopCurvatureResolution=NULL,
hexTransitionDuration=NULL, hoverData=NULL,
htmlElementAltitude=NULL, htmlElementHidden=NULL,
htmlElementKey=NULL, htmlElementLat=NULL,
htmlElementLng=NULL, htmlElementOffsetX=NULL,
htmlElementOffsetY=NULL, htmlElementPointerEvents=NULL,
htmlElementsData=NULL, labelAltitude=NULL, labelColor=NULL,
labelDotOrientation=NULL, labelDotRadius=NULL,
labelIncludeDot=NULL, labelLabel=NULL, labelLat=NULL,
labelLng=NULL, labelResolution=NULL, labelRotation=NULL,
labelSize=NULL, labelText=NULL, labelsData=NULL,
labelsTransitionDuration=NULL, lastInteraction=NULL,
lineHoverPrecision=NULL, particleAltitude=NULL,
particleLabel=NULL, particleLat=NULL, particleLng=NULL,
particlesColor=NULL, particlesData=NULL, particlesList=NULL,
particlesSize=NULL, particlesSizeAttenuation=NULL,
pathColor=NULL, pathDashAnimateTime=NULL, pathDashGap=NULL,
pathDashInitialGap=NULL, pathDashLength=NULL,
pathLabel=NULL, pathPointAlt=NULL, pathPointLat=NULL,
pathPointLng=NULL, pathPoints=NULL, pathResolution=NULL,
pathStroke=NULL, pathTransitionDuration=NULL,
pathsData=NULL, pointAltitude=NULL, pointColor=NULL,
pointLabel=NULL, pointLat=NULL, pointLng=NULL,
pointRadius=NULL, pointResolution=NULL, pointsData=NULL,
pointsMerge=NULL, pointsTransitionDuration=NULL,
polygonAltitude=NULL, polygonCapColor=NULL,
polygonCapCurvatureResolution=NULL, polygonCapMaterial=NULL,
polygonGeoJsonGeometry=NULL, polygonHoverAltitude=NULL,
polygonHoverCapColor=NULL, polygonHoverKey=NULL,
polygonHoverSideColor=NULL, polygonHoverStrokeColor=NULL,
polygonLabel=NULL, polygonSideColor=NULL,
polygonSideMaterial=NULL, polygonStrokeColor=NULL,
polygonsData=NULL, polygonsTransitionDuration=NULL,
rendererConfig=NULL, responsive=NULL, rightClickData=NULL,
ringAltitude=NULL, ringColor=NULL, ringLat=NULL,
ringLng=NULL, ringMaxRadius=NULL, ringPropagationSpeed=NULL,
ringRepeatPeriod=NULL, ringResolution=NULL, ringsData=NULL,
showAtmosphere=NULL, showGlobe=NULL, showGraticules=NULL,
showPointerCursor=NULL, style=NULL, tileAltitude=NULL,
tileCurvatureResolution=NULL, tileHeight=NULL,
tileLabel=NULL, tileLat=NULL, tileLng=NULL,
tileMaterial=NULL, tileUseGlobeProjection=NULL,
tileWidth=NULL, tilesData=NULL,
tilesTransitionDuration=NULL, waitForGlobeReady=NULL,
width=NULL)
}

\arguments{
\item{children}{A list of or a singular dash component, string or number. Dash components rendered as geo-anchored HTML overlays. Children are
matched to htmlElementsData by index.}

\item{id}{Character | named list. The ID used to identify this component in Dash callbacks.}

\item{animateIn}{Logical. }

\item{animationPaused}{Logical. }

\item{arcAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{arcAltitudeAutoScale}{Logical | numeric | character | named list | unnamed list. }

\item{arcCircularResolution}{Numeric. }

\item{arcColor}{Logical | numeric | character | named list | unnamed list. }

\item{arcCurveResolution}{Numeric. }

\item{arcDashAnimateTime}{Logical | numeric | character | named list | unnamed list. }

\item{arcDashGap}{Logical | numeric | character | named list | unnamed list. }

\item{arcDashInitialGap}{Logical | numeric | character | named list | unnamed list. }

\item{arcDashLength}{Logical | numeric | character | named list | unnamed list. }

\item{arcEndAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{arcEndLat}{Logical | numeric | character | named list | unnamed list. }

\item{arcEndLng}{Logical | numeric | character | named list | unnamed list. }

\item{arcLabel}{Logical | numeric | character | named list | unnamed list. }

\item{arcStartAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{arcStartLat}{Logical | numeric | character | named list | unnamed list. }

\item{arcStartLng}{Logical | numeric | character | named list | unnamed list. }

\item{arcStroke}{Logical | numeric | character | named list | unnamed list. }

\item{arcsData}{Unnamed list. Arc layer data and accessors.}

\item{arcsTransitionDuration}{Numeric. }

\item{atmosphereAltitude}{Numeric. }

\item{atmosphereColor}{Character. }

\item{autoRotate}{Logical. }

\item{autoRotateSpeed}{Numeric. }

\item{backgroundColor}{Character. }

\item{backgroundImageUrl}{Character. }

\item{bumpImageUrl}{Character. }

\item{cameraPosition}{Named list. Target camera position in geographic coordinates.}

\item{cameraTransitionDuration}{Numeric. }

\item{className}{Character. CSS class applied to the outer wrapper.}

\item{clearGlobeTileCacheKey}{Logical | numeric | character | named list | unnamed list. }

\item{clickData}{Named list. Last click event payload emitted by any supported layer.}

\item{clouds}{Logical. }

\item{cloudsAltitude}{Numeric. }

\item{cloudsImageUrl}{Character. }

\item{cloudsOpacity}{Numeric. }

\item{cloudsRotationSpeed}{Numeric. }

\item{currentView}{Named list. Current point of view reported by zoom and rotation interactions.}

\item{dayNightCycle}{Logical. }

\item{dayNightCycleAnimate}{Logical. }

\item{dayNightCycleDayImageUrl}{Character. }

\item{dayNightCycleMinutesPerSecond}{Numeric. }

\item{dayNightCycleNightImageUrl}{Character. }

\item{dayNightCycleTime}{Logical | numeric | character | named list | unnamed list. }

\item{enablePointerInteraction}{Logical. }

\item{globeCurvatureResolution}{Numeric. }

\item{globeImageUrl}{Character. }

\item{globeOffset}{Unnamed list. Position offset of the globe relative to the canvas centre.}

\item{globeReady}{Logical. Whether the globe has finished initialising.}

\item{heatmapBandwidth}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapBaseAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapColorSaturation}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapPointLat}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapPointLng}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapPointWeight}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapPoints}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapTopAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{heatmapsData}{Unnamed list. Heatmap layer data and accessors.}

\item{heatmapsTransitionDuration}{Numeric. }

\item{height}{Numeric. Canvas height in pixels.}

\item{hexAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{hexBinMerge}{Logical. }

\item{hexBinPointLat}{Logical | numeric | character | named list | unnamed list. }

\item{hexBinPointLng}{Logical | numeric | character | named list | unnamed list. }

\item{hexBinPointWeight}{Logical | numeric | character | named list | unnamed list. }

\item{hexBinPointsData}{Unnamed list. Hex bin layer data and accessors.}

\item{hexBinResolution}{Numeric. }

\item{hexLabel}{Logical | numeric | character | named list | unnamed list. }

\item{hexMargin}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonColor}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonCurvatureResolution}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonDotResolution}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonGeoJsonGeometry}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonLabel}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonMargin}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonResolution}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonUseDots}{Logical | numeric | character | named list | unnamed list. }

\item{hexPolygonsData}{Unnamed list. Hexed polygon layer data and accessors.}

\item{hexPolygonsTransitionDuration}{Numeric. }

\item{hexSideColor}{Logical | numeric | character | named list | unnamed list. }

\item{hexTopColor}{Logical | numeric | character | named list | unnamed list. }

\item{hexTopCurvatureResolution}{Numeric. }

\item{hexTransitionDuration}{Numeric. }

\item{hoverData}{Named list. Last hover event payload emitted by any supported layer.}

\item{htmlElementAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementHidden}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementKey}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementLat}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementLng}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementOffsetX}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementOffsetY}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementPointerEvents}{Logical | numeric | character | named list | unnamed list. }

\item{htmlElementsData}{Unnamed list. Geo-anchored HTML overlay data. Children are projected onto the globe by
matching each child to a data item with the same index.}

\item{labelAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{labelColor}{Logical | numeric | character | named list | unnamed list. }

\item{labelDotOrientation}{Logical | numeric | character | named list | unnamed list. }

\item{labelDotRadius}{Logical | numeric | character | named list | unnamed list. }

\item{labelIncludeDot}{Logical | numeric | character | named list | unnamed list. }

\item{labelLabel}{Logical | numeric | character | named list | unnamed list. }

\item{labelLat}{Logical | numeric | character | named list | unnamed list. }

\item{labelLng}{Logical | numeric | character | named list | unnamed list. }

\item{labelResolution}{Numeric. }

\item{labelRotation}{Logical | numeric | character | named list | unnamed list. }

\item{labelSize}{Logical | numeric | character | named list | unnamed list. }

\item{labelText}{Logical | numeric | character | named list | unnamed list. }

\item{labelsData}{Unnamed list. Label layer data and accessors.}

\item{labelsTransitionDuration}{Numeric. }

\item{lastInteraction}{Named list. The most recent interaction payload emitted by the component.}

\item{lineHoverPrecision}{Numeric. }

\item{particleAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{particleLabel}{Logical | numeric | character | named list | unnamed list. }

\item{particleLat}{Logical | numeric | character | named list | unnamed list. }

\item{particleLng}{Logical | numeric | character | named list | unnamed list. }

\item{particlesColor}{Logical | numeric | character | named list | unnamed list. }

\item{particlesData}{Unnamed list. Particle layer data and accessors.}

\item{particlesList}{Logical | numeric | character | named list | unnamed list. }

\item{particlesSize}{Logical | numeric | character | named list | unnamed list. }

\item{particlesSizeAttenuation}{Logical | numeric | character | named list | unnamed list. }

\item{pathColor}{Logical | numeric | character | named list | unnamed list. }

\item{pathDashAnimateTime}{Logical | numeric | character | named list | unnamed list. }

\item{pathDashGap}{Logical | numeric | character | named list | unnamed list. }

\item{pathDashInitialGap}{Logical | numeric | character | named list | unnamed list. }

\item{pathDashLength}{Logical | numeric | character | named list | unnamed list. }

\item{pathLabel}{Logical | numeric | character | named list | unnamed list. }

\item{pathPointAlt}{Logical | numeric | character | named list | unnamed list. }

\item{pathPointLat}{Logical | numeric | character | named list | unnamed list. }

\item{pathPointLng}{Logical | numeric | character | named list | unnamed list. }

\item{pathPoints}{Logical | numeric | character | named list | unnamed list. }

\item{pathResolution}{Numeric. }

\item{pathStroke}{Logical | numeric | character | named list | unnamed list. }

\item{pathTransitionDuration}{Numeric. }

\item{pathsData}{Unnamed list. Path layer data and accessors.}

\item{pointAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{pointColor}{Logical | numeric | character | named list | unnamed list. }

\item{pointLabel}{Logical | numeric | character | named list | unnamed list. }

\item{pointLat}{Logical | numeric | character | named list | unnamed list. }

\item{pointLng}{Logical | numeric | character | named list | unnamed list. }

\item{pointRadius}{Logical | numeric | character | named list | unnamed list. }

\item{pointResolution}{Numeric. }

\item{pointsData}{Unnamed list. Point layer data and accessors.}

\item{pointsMerge}{Logical. }

\item{pointsTransitionDuration}{Numeric. }

\item{polygonAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{polygonCapColor}{Logical | numeric | character | named list | unnamed list. }

\item{polygonCapCurvatureResolution}{Logical | numeric | character | named list | unnamed list. }

\item{polygonCapMaterial}{Logical | numeric | character | named list | unnamed list. }

\item{polygonGeoJsonGeometry}{Logical | numeric | character | named list | unnamed list. }

\item{polygonHoverAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{polygonHoverCapColor}{Logical | numeric | character | named list | unnamed list. }

\item{polygonHoverKey}{Logical | numeric | character | named list | unnamed list. }

\item{polygonHoverSideColor}{Logical | numeric | character | named list | unnamed list. }

\item{polygonHoverStrokeColor}{Logical | numeric | character | named list | unnamed list. }

\item{polygonLabel}{Logical | numeric | character | named list | unnamed list. }

\item{polygonSideColor}{Logical | numeric | character | named list | unnamed list. }

\item{polygonSideMaterial}{Logical | numeric | character | named list | unnamed list. }

\item{polygonStrokeColor}{Logical | numeric | character | named list | unnamed list. }

\item{polygonsData}{Unnamed list. Polygon layer data and accessors.}

\item{polygonsTransitionDuration}{Numeric. }

\item{rendererConfig}{Named list. }

\item{responsive}{Logical. Automatically size the globe from its container with ResizeObserver.}

\item{rightClickData}{Named list. Last right click event payload emitted by any supported layer.}

\item{ringAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{ringColor}{Logical | numeric | character | named list | unnamed list. }

\item{ringLat}{Logical | numeric | character | named list | unnamed list. }

\item{ringLng}{Logical | numeric | character | named list | unnamed list. }

\item{ringMaxRadius}{Logical | numeric | character | named list | unnamed list. }

\item{ringPropagationSpeed}{Logical | numeric | character | named list | unnamed list. }

\item{ringRepeatPeriod}{Logical | numeric | character | named list | unnamed list. }

\item{ringResolution}{Numeric. }

\item{ringsData}{Unnamed list. Ring layer data and accessors.}

\item{showAtmosphere}{Logical. }

\item{showGlobe}{Logical. }

\item{showGraticules}{Logical. }

\item{showPointerCursor}{Logical. }

\item{style}{Named list. Inline styles for the outer wrapper.}

\item{tileAltitude}{Logical | numeric | character | named list | unnamed list. }

\item{tileCurvatureResolution}{Logical | numeric | character | named list | unnamed list. }

\item{tileHeight}{Logical | numeric | character | named list | unnamed list. }

\item{tileLabel}{Logical | numeric | character | named list | unnamed list. }

\item{tileLat}{Logical | numeric | character | named list | unnamed list. }

\item{tileLng}{Logical | numeric | character | named list | unnamed list. }

\item{tileMaterial}{Logical | numeric | character | named list | unnamed list. }

\item{tileUseGlobeProjection}{Logical | numeric | character | named list | unnamed list. }

\item{tileWidth}{Logical | numeric | character | named list | unnamed list. }

\item{tilesData}{Unnamed list. Tile layer data and accessors.}

\item{tilesTransitionDuration}{Numeric. }

\item{waitForGlobeReady}{Logical. }

\item{width}{Numeric. Canvas width in pixels.}
}

\value{named list of JSON elements corresponding to React.js properties and their values}

