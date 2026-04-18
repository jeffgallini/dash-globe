import React, {useEffect, useMemo, useRef, useState} from 'react';
import Globe from 'react-globe.gl';
import {
    BackSide,
    DoubleSide,
    FrontSide,
    Mesh,
    MeshBasicMaterial,
    MeshLambertMaterial,
    MeshPhongMaterial,
    MeshStandardMaterial,
    ShaderMaterial,
    SphereGeometry,
    TextureLoader,
    Vector2
} from 'three';

const INTERNAL_PROP_NAMES = new Set([
    'id',
    'className',
    'style',
    'responsive',
    'cameraPosition',
    'cameraTransitionDuration',
    'animationPaused',
    'clearGlobeTileCacheKey',
    'dayNightCycle',
    'dayNightCycleDayImageUrl',
    'dayNightCycleNightImageUrl',
    'dayNightCycleTime',
    'dayNightCycleAnimate',
    'dayNightCycleMinutesPerSecond',
    'autoRotate',
    'autoRotateSpeed',
    'clouds',
    'cloudsImageUrl',
    'cloudsAltitude',
    'cloudsRotationSpeed',
    'cloudsOpacity',
    'polygonHoverKey',
    'polygonHoverAltitude',
    'polygonHoverCapColor',
    'polygonHoverSideColor',
    'polygonHoverStrokeColor',
    'clickData',
    'rightClickData',
    'hoverData',
    'currentView',
    'globeReady',
    'lastInteraction',
    'setProps'
]);

const DEFAULT_DAY_NIGHT_CYCLE_DAY_IMAGE_URL = 'https://unpkg.com/three-globe@2.45.2/example/img/earth-day.jpg';
const DEFAULT_DAY_NIGHT_CYCLE_NIGHT_IMAGE_URL = 'https://unpkg.com/three-globe@2.45.2/example/img/earth-night.jpg';
const DEFAULT_CLOUDS_IMAGE_URL = 'https://unpkg.com/globe.gl/example/clouds/clouds.png';
const MILLISECONDS_PER_DAY = 864e5;

function omitInternalProps(props) {
    return Object.keys(props).reduce((acc, key) => {
        if (!INTERNAL_PROP_NAMES.has(key) && props[key] !== undefined) {
            acc[key] = props[key];
        }
        return acc;
    }, {});
}

function buildEventPayload(type, layer, data, coords, previousData) {
    return {
        type,
        layer,
        data: data === undefined ? null : data,
        coords: coords === undefined ? null : coords,
        previousData: previousData === undefined ? null : previousData,
        timestamp: Date.now()
    };
}

const HOVER_SIGNATURE_KEYS = [
    'id',
    'countryId',
    'routeId',
    'airportId',
    'iata',
    'isoA2',
    'ISO_A2',
    'name',
    'label',
    'lat',
    'lng',
    'startLat',
    'startLng',
    'endLat',
    'endLng'
];

function buildHoverSignatureValue(value) {
    if (value === undefined || value === null) {
        return value;
    }

    if (Array.isArray(value)) {
        return value.slice(0, 8).map((item) => buildHoverSignatureValue(item));
    }

    if (typeof value !== 'object') {
        return value;
    }

    const preferredSummary = HOVER_SIGNATURE_KEYS.reduce((acc, key) => {
        if (Object.prototype.hasOwnProperty.call(value, key)) {
            acc[key] = value[key];
        }
        return acc;
    }, {});

    if (Object.keys(preferredSummary).length > 0) {
        return preferredSummary;
    }

    const primitiveSummary = Object.keys(value)
        .sort()
        .reduce((acc, key) => {
            if (Object.keys(acc).length >= 8) {
                return acc;
            }

            const item = value[key];
            if (
                item === null ||
                typeof item === 'string' ||
                typeof item === 'number' ||
                typeof item === 'boolean'
            ) {
                acc[key] = item;
            }
            return acc;
        }, {});

    if (Object.keys(primitiveSummary).length > 0) {
        return primitiveSummary;
    }

    return {
        __keys: Object.keys(value).sort().slice(0, 8)
    };
}

const MATERIAL_TYPES = {
    basic: MeshBasicMaterial,
    lambert: MeshLambertMaterial,
    phong: MeshPhongMaterial,
    standard: MeshStandardMaterial
};

const MATERIAL_SIDES = {
    back: BackSide,
    double: DoubleSide,
    front: FrontSide
};

function isPlainObject(value) {
    if (value === null || typeof value !== 'object') {
        return false;
    }

    const prototype = Object.getPrototypeOf(value);
    return prototype === Object.prototype || prototype === null;
}

function buildThreeMaterial(accessor) {
    if (!isPlainObject(accessor)) {
        return accessor;
    }

    if (accessor.isMaterial) {
        return accessor;
    }

    const {type, side, ...options} = accessor;
    const MaterialCtor = MATERIAL_TYPES[type];

    if (!MaterialCtor) {
        return accessor;
    }

    const materialOptions = {...options};
    if (typeof side === 'string') {
        materialOptions.side = MATERIAL_SIDES[side.toLowerCase()] || FrontSide;
    }

    return new MaterialCtor(materialOptions);
}

function disposeMaterial(material) {
    if (material && material.isMaterial && typeof material.dispose === 'function') {
        material.dispose();
    }
}

function getMaterialCacheKey(value) {
    if (!isPlainObject(value)) {
        return null;
    }

    try {
        return JSON.stringify(value);
    } catch (_error) {
        return null;
    }
}

function resolveThreeMaterial(value, cacheRef) {
    if (!isPlainObject(value)) {
        return value;
    }

    const cacheKey = getMaterialCacheKey(value);
    if (cacheKey && cacheRef?.current?.has(cacheKey)) {
        return cacheRef.current.get(cacheKey);
    }

    const material = buildThreeMaterial(value);
    if (cacheKey && material && material.isMaterial) {
        cacheRef.current.set(cacheKey, material);
    }

    return material;
}

function buildMaterialAccessor(accessor, cacheRef) {
    if (accessor === undefined) {
        return accessor;
    }

    if (typeof accessor === 'string' || typeof accessor === 'function') {
        return (datum) => resolveThreeMaterial(resolveAccessorValue(accessor, datum), cacheRef);
    }

    return resolveThreeMaterial(accessor, cacheRef);
}

function disposeMaterialCache(cacheRef) {
    if (!cacheRef?.current) {
        return;
    }

    cacheRef.current.forEach((material) => disposeMaterial(material));
    cacheRef.current.clear();
}

const DAY_NIGHT_SHADER = {
    vertexShader: `
        varying vec3 vNormal;
        varying vec2 vUv;

        void main() {
            vNormal = normalize(normalMatrix * normal);
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        #define PI 3.141592653589793

        uniform sampler2D dayTexture;
        uniform sampler2D nightTexture;
        uniform vec2 sunPosition;
        uniform vec2 globeRotation;

        varying vec3 vNormal;
        varying vec2 vUv;

        float toRad(in float angle) {
            return angle * PI / 180.0;
        }

        vec3 polarToCartesian(in vec2 coords) { // [lng, lat]
            float theta = toRad(90.0 - coords.x);
            float phi = toRad(90.0 - coords.y);

            return vec3(
                sin(phi) * cos(theta),
                cos(phi),
                sin(phi) * sin(theta)
            );
        }

        void main() {
            float invLon = toRad(globeRotation.x);
            float invLat = -toRad(globeRotation.y);

            mat3 rotX = mat3(
                1, 0, 0,
                0, cos(invLat), -sin(invLat),
                0, sin(invLat), cos(invLat)
            );

            mat3 rotY = mat3(
                cos(invLon), 0, sin(invLon),
                0, 1, 0,
                -sin(invLon), 0, cos(invLon)
            );

            vec3 rotatedSunDirection = rotX * rotY * polarToCartesian(sunPosition);
            float intensity = dot(normalize(vNormal), normalize(rotatedSunDirection));
            vec4 dayColor = texture2D(dayTexture, vUv);
            vec4 nightColor = texture2D(nightTexture, vUv);
            float blendFactor = smoothstep(-0.1, 0.1, intensity);

            gl_FragColor = mix(nightColor, dayColor, blendFactor);
        }
    `
};

function normaliseDegrees(value) {
    return ((value % 360) + 360) % 360;
}

function toRadians(value) {
    return value * Math.PI / 180;
}

function toDegrees(value) {
    return value * 180 / Math.PI;
}

function getJulianDate(timestamp) {
    return timestamp / MILLISECONDS_PER_DAY + 2440587.5;
}

function getJulianCentury(timestamp) {
    return (getJulianDate(timestamp) - 2451545.0) / 36525;
}

function getSunPosition(timestamp) {
    const dayStart = new Date(timestamp).setUTCHours(0, 0, 0, 0);
    const t = getJulianCentury(timestamp);
    const geomMeanLongSun = normaliseDegrees(280.46646 + t * (36000.76983 + t * 0.0003032));
    const geomMeanAnomalySun = 357.52911 + t * (35999.05029 - 0.0001537 * t);
    const eccentricityEarthOrbit = 0.016708634 - t * (0.000042037 + 0.0000001267 * t);
    const sunEquationOfCenter =
        Math.sin(toRadians(geomMeanAnomalySun)) * (1.914602 - t * (0.004817 + 0.000014 * t)) +
        Math.sin(toRadians(2 * geomMeanAnomalySun)) * (0.019993 - 0.000101 * t) +
        Math.sin(toRadians(3 * geomMeanAnomalySun)) * 0.000289;
    const sunTrueLongitude = geomMeanLongSun + sunEquationOfCenter;
    const omega = 125.04 - 1934.136 * t;
    const sunApparentLongitude = sunTrueLongitude - 0.00569 - 0.00478 * Math.sin(toRadians(omega));
    const meanObliquity =
        23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - 0.001813 * t))) / 60) / 60;
    const obliquityCorrection = meanObliquity + 0.00256 * Math.cos(toRadians(omega));
    const solarDeclination = toDegrees(
        Math.asin(
            Math.sin(toRadians(obliquityCorrection)) *
            Math.sin(toRadians(sunApparentLongitude))
        )
    );
    const y = Math.tan(toRadians(obliquityCorrection / 2)) ** 2;
    const equationOfTime = 4 * toDegrees(
        y * Math.sin(2 * toRadians(geomMeanLongSun)) -
        2 * eccentricityEarthOrbit * Math.sin(toRadians(geomMeanAnomalySun)) +
        4 * eccentricityEarthOrbit * y *
            Math.sin(toRadians(geomMeanAnomalySun)) *
            Math.cos(2 * toRadians(geomMeanLongSun)) -
        0.5 * y * y * Math.sin(4 * toRadians(geomMeanLongSun)) -
        1.25 * eccentricityEarthOrbit * eccentricityEarthOrbit *
            Math.sin(2 * toRadians(geomMeanAnomalySun))
    );
    const subsolarLongitude = (dayStart - timestamp) / MILLISECONDS_PER_DAY * 360 - 180;

    return [subsolarLongitude - equationOfTime / 4, solarDeclination];
}

function parseDayNightCycleTime(value) {
    if (typeof value === 'number' && Number.isFinite(value)) {
        return value;
    }

    if (typeof value === 'string' && value) {
        const parsed = new Date(value).getTime();
        if (!Number.isNaN(parsed)) {
            return parsed;
        }
    }

    return Date.now();
}

function disposeDayNightMaterial(material) {
    if (!material) {
        return;
    }

    if (material.uniforms.dayTexture?.value) {
        material.uniforms.dayTexture.value.dispose();
    }

    if (material.uniforms.nightTexture?.value) {
        material.uniforms.nightTexture.value.dispose();
    }

    disposeMaterial(material);
}

function disposeCloudsMesh(mesh) {
    if (!mesh) {
        return;
    }

    if (mesh.parent) {
        mesh.parent.remove(mesh);
    }

    if (mesh.material?.map) {
        mesh.material.map.dispose();
    }

    disposeMaterial(mesh.material);

    if (mesh.geometry?.dispose) {
        mesh.geometry.dispose();
    }
}

function buildHoverSignature(payload) {
    return JSON.stringify({
        type: payload.type,
        layer: payload.layer,
        data: buildHoverSignatureValue(payload.data)
    });
}

const COLOR_PARSER_CONTEXT = (
    typeof document !== 'undefined'
        ? document.createElement('canvas').getContext('2d')
        : null
);

function clamp(value, minValue, maxValue) {
    return Math.max(minValue, Math.min(maxValue, value));
}

function parseHexColor(value) {
    const hex = value.replace('#', '').trim();
    if (![3, 4, 6, 8].includes(hex.length)) {
        return null;
    }

    const expanded = hex.length <= 4
        ? hex.split('').map((part) => `${part}${part}`).join('')
        : hex;

    const hasAlpha = expanded.length === 8;
    const red = parseInt(expanded.slice(0, 2), 16);
    const green = parseInt(expanded.slice(2, 4), 16);
    const blue = parseInt(expanded.slice(4, 6), 16);
    const alpha = hasAlpha ? parseInt(expanded.slice(6, 8), 16) / 255 : 1;

    if ([red, green, blue, alpha].some((part) => Number.isNaN(part))) {
        return null;
    }

    return {red, green, blue, alpha};
}

function parseRgbColor(value) {
    const match = value.match(/^rgba?\((.+)\)$/i);
    if (!match) {
        return null;
    }

    const channels = match[1]
        .split(',')
        .map((part) => part.trim())
        .filter(Boolean);

    if (channels.length < 3 || channels.length > 4) {
        return null;
    }

    const toChannel = (part) => (
        part.endsWith('%')
            ? clamp(parseFloat(part) * 2.55, 0, 255)
            : clamp(parseFloat(part), 0, 255)
    );

    const red = toChannel(channels[0]);
    const green = toChannel(channels[1]);
    const blue = toChannel(channels[2]);
    const alpha = channels[3] === undefined ? 1 : clamp(parseFloat(channels[3]), 0, 1);

    if ([red, green, blue, alpha].some((part) => Number.isNaN(part))) {
        return null;
    }

    return {red, green, blue, alpha};
}

function parseCssColor(color) {
    if (typeof color !== 'string' || !color.trim()) {
        return null;
    }

    const normalisedColor = color.trim().toLowerCase();
    if (normalisedColor.startsWith('#')) {
        return parseHexColor(normalisedColor);
    }

    if (normalisedColor.startsWith('rgb')) {
        return parseRgbColor(normalisedColor);
    }

    if (!COLOR_PARSER_CONTEXT) {
        return null;
    }

    COLOR_PARSER_CONTEXT.fillStyle = '#000000';
    COLOR_PARSER_CONTEXT.fillStyle = color;
    return parseCssColor(COLOR_PARSER_CONTEXT.fillStyle);
}

function rgbaToCssString({red, green, blue, alpha}) {
    return `rgba(${Math.round(red)}, ${Math.round(green)}, ${Math.round(blue)}, ${clamp(alpha, 0, 1)})`;
}

function isRingColorInterpolatorSpec(value) {
    return isPlainObject(value) && value.type === 'ring-color-interpolator';
}

function applyRingColorEasing(progress, easing) {
    const remaining = 1 - clamp(progress, 0, 1);

    switch (easing) {
        case 'linear':
            return remaining;
        case 'square':
            return remaining ** 2;
        case 'cubic':
            return remaining ** 3;
        case 'sqrt':
        default:
            return Math.sqrt(remaining);
    }
}

function buildRingColorInterpolator(spec) {
    const startColor = parseCssColor(spec.color);
    if (!startColor) {
        return spec.color;
    }

    const fadeColor = parseCssColor(spec.fadeColor || spec.color) || startColor;
    const startAlpha = spec.opacity === undefined ? startColor.alpha : clamp(spec.opacity, 0, 1);
    const fadeAlpha = spec.fadeOpacity === undefined ? 0 : clamp(spec.fadeOpacity, 0, 1);
    const easing = typeof spec.easing === 'string' ? spec.easing.toLowerCase() : 'sqrt';

    return (progress) => {
        const mixFactor = 1 - applyRingColorEasing(progress, easing);
        return rgbaToCssString({
            red: startColor.red + (fadeColor.red - startColor.red) * mixFactor,
            green: startColor.green + (fadeColor.green - startColor.green) * mixFactor,
            blue: startColor.blue + (fadeColor.blue - startColor.blue) * mixFactor,
            alpha: startAlpha + (fadeAlpha - startAlpha) * mixFactor
        });
    };
}

function resolveRingColorValue(value) {
    return isRingColorInterpolatorSpec(value)
        ? buildRingColorInterpolator(value)
        : value;
}

function buildRingColorAccessor(accessor) {
    if (typeof accessor === 'function') {
        return accessor;
    }

    if (typeof accessor === 'string') {
        return (datum) => resolveRingColorValue(resolveAccessorValue(accessor, datum));
    }

    const resolvedValue = resolveRingColorValue(accessor);
    return () => resolvedValue;
}

function resolveAccessorValue(accessor, datum) {
    if (typeof accessor === 'function') {
        return accessor(datum);
    }

    if (
        typeof accessor === 'string' &&
        datum !== null &&
        typeof datum === 'object' &&
        Object.prototype.hasOwnProperty.call(datum, accessor)
    ) {
        return datum[accessor];
    }

    return accessor;
}

function buildSerializableAccessor(accessor, resolveValue = (value) => value) {
    if (typeof accessor === 'function') {
        return accessor;
    }

    if (typeof accessor === 'string') {
        return (datum) => resolveValue(resolveAccessorValue(accessor, datum));
    }

    return resolveValue(accessor);
}

function buildPolygonHoverMatchSignature(datum, hoverKeyAccessor) {
    if (datum === undefined || datum === null) {
        return null;
    }

    if (hoverKeyAccessor !== undefined && hoverKeyAccessor !== null) {
        const hoverKeyValue = resolveAccessorValue(hoverKeyAccessor, datum);
        if (hoverKeyValue !== undefined && hoverKeyValue !== null) {
            return `custom:${JSON.stringify(buildHoverSignatureValue(hoverKeyValue))}`;
        }
    }

    const summaryValue = buildHoverSignatureValue(datum);
    if (summaryValue !== undefined && summaryValue !== null) {
        return `summary:${JSON.stringify(summaryValue)}`;
    }

    return null;
}

export default function DashGlobe(props) {
    const {
        id,
        className,
        style,
        responsive,
        width,
        height,
        cameraPosition,
        cameraTransitionDuration,
        animationPaused,
        clearGlobeTileCacheKey,
        dayNightCycle,
        dayNightCycleDayImageUrl,
        dayNightCycleNightImageUrl,
        dayNightCycleTime,
        dayNightCycleAnimate,
        dayNightCycleMinutesPerSecond,
        autoRotate,
        autoRotateSpeed,
        clouds,
        cloudsImageUrl,
        cloudsAltitude,
        cloudsRotationSpeed,
        cloudsOpacity,
        globeReady,
        polygonHoverKey,
        polygonHoverAltitude,
        polygonHoverCapColor,
        polygonHoverSideColor,
        polygonHoverStrokeColor,
        setProps
    } = props;

    const wrapperRef = useRef(null);
    const globeRef = useRef(null);
    const lastCameraKeyRef = useRef(null);
    const lastAnimationStateRef = useRef(null);
    const lastTileCacheKeyRef = useRef(null);
    const lastEventSignatureRef = useRef({});
    const hoveredPolygonRef = useRef(null);
    const dayNightMaterialRef = useRef(null);
    const dayNightAnimationFrameRef = useRef(null);
    const dayNightClockRef = useRef(null);
    const dayNightFrameTimestampRef = useRef(null);
    const cloudsMeshRef = useRef(null);
    const cloudsAnimationFrameRef = useRef(null);
    const tileMaterialCacheRef = useRef(new Map());
    const [containerSize, setContainerSize] = useState({width: null, height: null});
    const [hoveredPolygonSignature, setHoveredPolygonSignature] = useState(null);
    const [dayNightMaterial, setDayNightMaterial] = useState(null);
    const polygonCapMaterial = useMemo(
        () => buildThreeMaterial(props.polygonCapMaterial),
        [props.polygonCapMaterial]
    );
    const polygonSideMaterial = useMemo(
        () => buildThreeMaterial(props.polygonSideMaterial),
        [props.polygonSideMaterial]
    );
    const tileMaterial = useMemo(
        () => buildMaterialAccessor(props.tileMaterial, tileMaterialCacheRef),
        [props.tileMaterial]
    );

    const syncDayNightGlobeRotation = (pointOfViewOverride) => {
        const material = dayNightMaterialRef.current;
        const globe = globeRef.current;
        if (!material || !globe) {
            return;
        }

        const pointOfView = pointOfViewOverride || globe.pointOfView();
        if (
            pointOfView &&
            Number.isFinite(pointOfView.lng) &&
            Number.isFinite(pointOfView.lat)
        ) {
            material.uniforms.globeRotation.value.set(pointOfView.lng, pointOfView.lat);
        }
    };

    useEffect(() => {
        dayNightClockRef.current = parseDayNightCycleTime(dayNightCycleTime);
        dayNightFrameTimestampRef.current = null;
    }, [dayNightCycleTime]);

    useEffect(() => {
        let cancelled = false;

        disposeDayNightMaterial(dayNightMaterialRef.current);
        dayNightMaterialRef.current = null;
        setDayNightMaterial(null);

        if (!dayNightCycle) {
            return undefined;
        }

        const dayTextureUrl = dayNightCycleDayImageUrl || DEFAULT_DAY_NIGHT_CYCLE_DAY_IMAGE_URL;
        const nightTextureUrl = dayNightCycleNightImageUrl || DEFAULT_DAY_NIGHT_CYCLE_NIGHT_IMAGE_URL;

        Promise.all([
            new TextureLoader().loadAsync(dayTextureUrl),
            new TextureLoader().loadAsync(nightTextureUrl)
        ])
            .then(([dayTexture, nightTexture]) => {
                if (cancelled) {
                    dayTexture.dispose();
                    nightTexture.dispose();
                    return;
                }

                const material = new ShaderMaterial({
                    uniforms: {
                        dayTexture: {value: dayTexture},
                        nightTexture: {value: nightTexture},
                        sunPosition: {value: new Vector2()},
                        globeRotation: {value: new Vector2()}
                    },
                    vertexShader: DAY_NIGHT_SHADER.vertexShader,
                    fragmentShader: DAY_NIGHT_SHADER.fragmentShader
                });

                dayNightMaterialRef.current = material;
                setDayNightMaterial(material);
            })
            .catch(() => {
                if (!cancelled) {
                    dayNightMaterialRef.current = null;
                    setDayNightMaterial(null);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [dayNightCycle, dayNightCycleDayImageUrl, dayNightCycleNightImageUrl]);

    useEffect(() => {
        if (!dayNightMaterialRef.current) {
            return;
        }

        const timestamp = dayNightClockRef.current || Date.now();
        dayNightMaterialRef.current.uniforms.sunPosition.value.set(...getSunPosition(timestamp));
        syncDayNightGlobeRotation();
    }, [dayNightMaterial, dayNightCycleTime]);

    useEffect(() => {
        if (!globeRef.current) {
            return;
        }

        const controls = globeRef.current.controls();
        if (!controls) {
            return;
        }

        if (autoRotate !== undefined && autoRotate !== null) {
            controls.autoRotate = autoRotate;
        }

        if (autoRotateSpeed !== undefined && autoRotateSpeed !== null) {
            controls.autoRotateSpeed = autoRotateSpeed;
        }
    }, [autoRotate, autoRotateSpeed, globeReady]);

    useEffect(() => {
        if (cloudsAnimationFrameRef.current) {
            cancelAnimationFrame(cloudsAnimationFrameRef.current);
            cloudsAnimationFrameRef.current = null;
        }

        disposeCloudsMesh(cloudsMeshRef.current);
        cloudsMeshRef.current = null;

        if (!clouds || !globeRef.current) {
            return undefined;
        }

        const globeRadius = globeRef.current.getGlobeRadius?.();
        if (!Number.isFinite(globeRadius) || globeRadius <= 0) {
            return undefined;
        }

        const resolvedAltitude = Number.isFinite(cloudsAltitude) ? cloudsAltitude : 0.004;
        const resolvedOpacity = Number.isFinite(cloudsOpacity) ? clamp(cloudsOpacity, 0, 1) : 1;
        const resolvedRotationSpeed = Number.isFinite(cloudsRotationSpeed) ? cloudsRotationSpeed : -0.006;
        const mesh = new Mesh(
            new SphereGeometry(globeRadius * (1 + resolvedAltitude), 75, 75),
            new MeshPhongMaterial({
                transparent: true,
                opacity: resolvedOpacity
            })
        );

        globeRef.current.scene().add(mesh);
        cloudsMeshRef.current = mesh;

        let cancelled = false;

        new TextureLoader()
            .loadAsync(cloudsImageUrl || DEFAULT_CLOUDS_IMAGE_URL)
            .then((texture) => {
                if (cancelled) {
                    texture.dispose();
                    return;
                }

                mesh.material.map = texture;
                mesh.material.needsUpdate = true;
            })
            .catch(() => {});

        if (!animationPaused && resolvedRotationSpeed !== 0) {
            const rotateClouds = () => {
                if (cancelled) {
                    return;
                }

                mesh.rotation.y += resolvedRotationSpeed * Math.PI / 180;
                cloudsAnimationFrameRef.current = requestAnimationFrame(rotateClouds);
            };

            cloudsAnimationFrameRef.current = requestAnimationFrame(rotateClouds);
        }

        return () => {
            cancelled = true;

            if (cloudsAnimationFrameRef.current) {
                cancelAnimationFrame(cloudsAnimationFrameRef.current);
                cloudsAnimationFrameRef.current = null;
            }

            if (cloudsMeshRef.current === mesh) {
                cloudsMeshRef.current = null;
            }

            disposeCloudsMesh(mesh);
        };
    }, [
        animationPaused,
        clouds,
        cloudsAltitude,
        cloudsImageUrl,
        cloudsOpacity,
        cloudsRotationSpeed,
        globeReady
    ]);

    useEffect(() => () => {
        if (cloudsAnimationFrameRef.current) {
            cancelAnimationFrame(cloudsAnimationFrameRef.current);
        }

        disposeCloudsMesh(cloudsMeshRef.current);
    }, []);

    useEffect(() => {
        if (!responsive || !wrapperRef.current || typeof ResizeObserver === 'undefined') {
            return undefined;
        }

        const observer = new ResizeObserver((entries) => {
            const entry = entries[0];
            if (!entry) {
                return;
            }

            const nextWidth = Math.round(entry.contentRect.width);
            const nextHeight = Math.round(entry.contentRect.height);

            setContainerSize((current) => {
                if (
                    current.width === nextWidth &&
                    current.height === nextHeight
                ) {
                    return current;
                }

                return {
                    width: nextWidth,
                    height: nextHeight
                };
            });
        });

        observer.observe(wrapperRef.current);
        return () => observer.disconnect();
    }, [responsive]);

    useEffect(() => {
        if (!globeRef.current || !cameraPosition) {
            return;
        }

        const nextKey = JSON.stringify({
            cameraPosition,
            cameraTransitionDuration
        });

        if (nextKey === lastCameraKeyRef.current) {
            return;
        }

        globeRef.current.pointOfView(cameraPosition, cameraTransitionDuration || 0);
        lastCameraKeyRef.current = nextKey;
        syncDayNightGlobeRotation(cameraPosition);
    }, [cameraPosition, cameraTransitionDuration]);

    useEffect(() => {
        if (!globeRef.current || animationPaused === undefined || animationPaused === null) {
            return;
        }

        if (animationPaused === lastAnimationStateRef.current) {
            return;
        }

        if (animationPaused) {
            globeRef.current.pauseAnimation();
        } else {
            globeRef.current.resumeAnimation();
        }

        lastAnimationStateRef.current = animationPaused;
    }, [animationPaused]);

    useEffect(() => {
        if (
            !globeRef.current ||
            clearGlobeTileCacheKey === undefined ||
            clearGlobeTileCacheKey === lastTileCacheKeyRef.current
        ) {
            return;
        }

        globeRef.current.globeTileEngineClearCache();
        lastTileCacheKeyRef.current = clearGlobeTileCacheKey;
    }, [clearGlobeTileCacheKey]);

    useEffect(() => {
        if (dayNightAnimationFrameRef.current) {
            cancelAnimationFrame(dayNightAnimationFrameRef.current);
            dayNightAnimationFrameRef.current = null;
        }

        dayNightFrameTimestampRef.current = null;

        if (!dayNightCycle || !dayNightCycleAnimate) {
            return undefined;
        }

        const minutesPerSecond = Number.isFinite(dayNightCycleMinutesPerSecond)
            ? dayNightCycleMinutesPerSecond
            : 60;

        const tick = (frameTimestamp) => {
            if (dayNightFrameTimestampRef.current === null) {
                dayNightFrameTimestampRef.current = frameTimestamp;
            } else {
                const deltaMilliseconds = frameTimestamp - dayNightFrameTimestampRef.current;
                dayNightFrameTimestampRef.current = frameTimestamp;
                dayNightClockRef.current = (dayNightClockRef.current || Date.now()) +
                    deltaMilliseconds * minutesPerSecond * 60;

                if (dayNightMaterialRef.current) {
                    dayNightMaterialRef.current.uniforms.sunPosition.value.set(
                        ...getSunPosition(dayNightClockRef.current)
                    );
                }
            }

            dayNightAnimationFrameRef.current = requestAnimationFrame(tick);
        };

        dayNightAnimationFrameRef.current = requestAnimationFrame(tick);
        return () => {
            if (dayNightAnimationFrameRef.current) {
                cancelAnimationFrame(dayNightAnimationFrameRef.current);
                dayNightAnimationFrameRef.current = null;
            }
            dayNightFrameTimestampRef.current = null;
        };
    }, [dayNightCycle, dayNightCycleAnimate, dayNightCycleMinutesPerSecond]);

    useEffect(() => () => {
        if (dayNightAnimationFrameRef.current) {
            cancelAnimationFrame(dayNightAnimationFrameRef.current);
        }
        disposeDayNightMaterial(dayNightMaterialRef.current);
    }, []);

    useEffect(() => () => disposeMaterial(polygonCapMaterial), [polygonCapMaterial]);
    useEffect(() => () => disposeMaterial(polygonSideMaterial), [polygonSideMaterial]);
    useEffect(() => () => {
        disposeMaterialCache(tileMaterialCacheRef);
        tileMaterialCacheRef.current = new Map();
    }, [props.tileMaterial]);

    const emitEvent = (propName, payload, options = {}) => {
        if (!setProps) {
            return;
        }

        if (options.dedupe) {
            const signature = options.signature || buildHoverSignature(payload);
            if (lastEventSignatureRef.current[propName] === signature) {
                return;
            }
            lastEventSignatureRef.current[propName] = signature;
        }

        setProps({
            [propName]: payload,
            lastInteraction: payload
        });
    };

    const handleObjectEvent = (type, layer) => (data, event, coords) => {
        emitEvent(
            type === 'click' ? 'clickData' : 'rightClickData',
            buildEventPayload(type, layer, data, coords)
        );
    };

    const handleHoverEvent = (layer) => (data, previousData) => {
        // Dash callbacks often restyle the hovered layer, which can recreate the
        // hovered object while the pointer is still over it. Deduping by a small
        // semantic signature prevents repeated network round-trips for the same hover target.
        emitEvent('hoverData', buildEventPayload('hover', layer, data, null, previousData), {dedupe: true});
    };

    const handlePolygonHover = (data, previousData) => {
        hoveredPolygonRef.current = data || null;
        const nextSignature = buildPolygonHoverMatchSignature(data, polygonHoverKey);
        setHoveredPolygonSignature((current) => (current === nextSignature ? current : nextSignature));
        handleHoverEvent('polygon')(data, previousData);
    };

    const handleZoom = (pointOfView) => {
        syncDayNightGlobeRotation(pointOfView);

        if (!setProps) {
            return;
        }

        setProps({
            currentView: {
                ...pointOfView,
                timestamp: Date.now()
            }
        });
    };

    const wrapperStyle = {
        position: 'relative',
        width: '100%',
        height: height ? `${height}px` : 600,
        ...style
    };

    const resolvedWidth = responsive ? (containerSize.width || width) : width;
    const resolvedHeight = responsive ? (containerSize.height || height || 600) : height;

    const shouldApplyPolygonHoverOverride = (
        polygonHoverAltitude !== undefined ||
        polygonHoverCapColor !== undefined ||
        polygonHoverSideColor !== undefined ||
        polygonHoverStrokeColor !== undefined
    );

    const isHoveredPolygon = (polygon) => {
        if (!shouldApplyPolygonHoverOverride || polygon === undefined || polygon === null) {
            return false;
        }

        const polygonSignature = buildPolygonHoverMatchSignature(polygon, polygonHoverKey);
        if (hoveredPolygonSignature !== null && polygonSignature !== null) {
            return polygonSignature === hoveredPolygonSignature;
        }

        return hoveredPolygonRef.current === polygon;
    };

    const buildPolygonHoverAccessor = (baseAccessor, hoverAccessor) => {
        if (hoverAccessor === undefined) {
            return baseAccessor;
        }

        return (polygon) => (
            isHoveredPolygon(polygon)
                ? resolveAccessorValue(hoverAccessor, polygon)
                : resolveAccessorValue(baseAccessor, polygon)
        );
    };

    const globeProps = {
        ...omitInternalProps(props),
        onGlobeReady: () => setProps && setProps({globeReady: true}),
        onGlobeClick: (coords) => emitEvent('clickData', buildEventPayload('click', 'globe', null, coords)),
        onGlobeRightClick: (coords) => emitEvent('rightClickData', buildEventPayload('rightClick', 'globe', null, coords)),
        onPointClick: handleObjectEvent('click', 'point'),
        onPointRightClick: handleObjectEvent('rightClick', 'point'),
        onPointHover: handleHoverEvent('point'),
        onArcClick: handleObjectEvent('click', 'arc'),
        onArcRightClick: handleObjectEvent('rightClick', 'arc'),
        onArcHover: handleHoverEvent('arc'),
        onPolygonClick: handleObjectEvent('click', 'polygon'),
        onPolygonRightClick: handleObjectEvent('rightClick', 'polygon'),
        onPolygonHover: handlePolygonHover,
        onPathClick: handleObjectEvent('click', 'path'),
        onPathRightClick: handleObjectEvent('rightClick', 'path'),
        onPathHover: handleHoverEvent('path'),
        onHeatmapClick: handleObjectEvent('click', 'heatmap'),
        onHeatmapRightClick: handleObjectEvent('rightClick', 'heatmap'),
        onHeatmapHover: handleHoverEvent('heatmap'),
        onHexClick: handleObjectEvent('click', 'hex'),
        onHexRightClick: handleObjectEvent('rightClick', 'hex'),
        onHexHover: handleHoverEvent('hex'),
        onHexPolygonClick: handleObjectEvent('click', 'hexPolygon'),
        onHexPolygonRightClick: handleObjectEvent('rightClick', 'hexPolygon'),
        onHexPolygonHover: handleHoverEvent('hexPolygon'),
        onTileClick: handleObjectEvent('click', 'tile'),
        onTileRightClick: handleObjectEvent('rightClick', 'tile'),
        onTileHover: handleHoverEvent('tile'),
        onParticleClick: handleObjectEvent('click', 'particle'),
        onParticleRightClick: handleObjectEvent('rightClick', 'particle'),
        onParticleHover: handleHoverEvent('particle'),
        onLabelClick: handleObjectEvent('click', 'label'),
        onLabelRightClick: handleObjectEvent('rightClick', 'label'),
        onLabelHover: handleHoverEvent('label'),
        onZoom: handleZoom
    };

    if (shouldApplyPolygonHoverOverride) {
        globeProps.polygonAltitude = buildPolygonHoverAccessor(props.polygonAltitude, polygonHoverAltitude);
        globeProps.polygonCapColor = buildPolygonHoverAccessor(props.polygonCapColor, polygonHoverCapColor);
        globeProps.polygonSideColor = buildPolygonHoverAccessor(props.polygonSideColor, polygonHoverSideColor);
        globeProps.polygonStrokeColor = buildPolygonHoverAccessor(props.polygonStrokeColor, polygonHoverStrokeColor);
    }

    if (polygonCapMaterial !== undefined) {
        globeProps.polygonCapMaterial = polygonCapMaterial;
    }

    if (polygonSideMaterial !== undefined) {
        globeProps.polygonSideMaterial = polygonSideMaterial;
    }

    if (dayNightMaterial !== undefined && dayNightMaterial !== null) {
        globeProps.globeMaterial = dayNightMaterial;
    }

    if (props.arcColor !== undefined) {
        globeProps.arcColor = buildSerializableAccessor(props.arcColor);
    }

    if (props.ringColor !== undefined) {
        globeProps.ringColor = buildRingColorAccessor(props.ringColor);
    }

    if (tileMaterial !== undefined) {
        globeProps.tileMaterial = tileMaterial;
    }

    if (resolvedWidth !== undefined && resolvedWidth !== null) {
        globeProps.width = resolvedWidth;
    }

    if (resolvedHeight !== undefined && resolvedHeight !== null) {
        globeProps.height = resolvedHeight;
    }

    return (
        <div id={id} className={className} style={wrapperStyle} ref={wrapperRef}>
            <Globe ref={globeRef} {...globeProps} />
        </div>
    );
}
