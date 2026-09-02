const DATA_URL_TYPE = 'dash-globe-data-url';

const LAYER_DATA_PROP_NAMES = [
    'pointsData',
    'arcsData',
    'polygonsData',
    'pathsData',
    'heatmapsData',
    'hexBinPointsData',
    'hexPolygonsData',
    'tilesData',
    'particlesData',
    'ringsData',
    'labelsData',
    'htmlElementsData'
];

const EVENT_FEEDBACK_PROP_NAMES = new Set([
    'clickData',
    'rightClickData',
    'hoverData',
    'currentView',
    'lastInteraction',
    'globeReady',
    'setProps'
]);

const GEOMETRY_KEYS = new Set([
    'geometry',
    'coordinates',
    'coords',
    'path',
    'paths',
    'points',
    'polygon',
    'polygons',
    'geojson',
    'geoJson',
    'features'
]);

function isPlainObject(value) {
    if (value === null || typeof value !== 'object') {
        return false;
    }

    const prototype = Object.getPrototypeOf(value);
    return prototype === Object.prototype || prototype === null;
}

function isDataUrlSpec(value) {
    if (typeof value === 'string' && /^(https?:)?\/\//.test(value.trim())) {
        return true;
    }

    return (
        isPlainObject(value)
        && value.type === DATA_URL_TYPE
        && typeof value.url === 'string'
        && value.url.trim().length > 0
    );
}

function normaliseDataUrlSpec(value) {
    if (typeof value === 'string') {
        return {
            type: DATA_URL_TYPE,
            url: value.trim(),
            unwrapFeatures: true
        };
    }

    return {
        type: DATA_URL_TYPE,
        url: value.url.trim(),
        unwrapFeatures: value.unwrapFeatures !== false
    };
}

function unwrapFetchedLayerData(payload, unwrapFeatures) {
    if (
        unwrapFeatures
        && isPlainObject(payload)
        && payload.type === 'FeatureCollection'
        && Array.isArray(payload.features)
    ) {
        return payload.features;
    }

    return payload;
}

async function fetchLayerData(spec, signal) {
    const response = await fetch(spec.url, {signal});
    if (!response.ok) {
        throw new Error(`Failed to fetch globe data (${response.status}): ${spec.url}`);
    }

    const payload = await response.json();
    return unwrapFetchedLayerData(payload, spec.unwrapFeatures);
}

function summariseEventValue(value, depth = 0) {
    if (value === null || value === undefined) {
        return value === undefined ? null : value;
    }

    if (typeof value !== 'object') {
        return value;
    }

    if (Array.isArray(value)) {
        if (depth >= 1 || value.length > 12) {
            return {
                __type: 'array',
                length: value.length
            };
        }

        return value.map((item) => summariseEventValue(item, depth + 1));
    }

    if (depth >= 2) {
        return {
            __type: 'object',
            keys: Object.keys(value).slice(0, 12)
        };
    }

    const summary = {};
    Object.keys(value).forEach((key) => {
        if (GEOMETRY_KEYS.has(key)) {
            const nested = value[key];
            if (Array.isArray(nested)) {
                summary[key] = {__omitted: 'array', length: nested.length};
            } else if (isPlainObject(nested)) {
                summary[key] = {
                    __omitted: 'object',
                    type: nested.type || undefined,
                    keys: Object.keys(nested).slice(0, 8)
                };
            } else if (nested !== undefined) {
                summary[key] = {__omitted: typeof nested};
            }
            return;
        }

        summary[key] = summariseEventValue(value[key], depth + 1);
    });

    return summary;
}

function compactEventData(data, mode) {
    if (mode === 'full' || data === null || data === undefined) {
        return data === undefined ? null : data;
    }

    return summariseEventValue(data);
}

function fingerprintLayerData(value) {
    if (value === null || value === undefined) {
        return String(value);
    }

    if (typeof value !== 'object') {
        return `${typeof value}:${String(value)}`;
    }

    if (isDataUrlSpec(value)) {
        const spec = normaliseDataUrlSpec(value);
        return `data-url:${spec.url}:${spec.unwrapFeatures ? 1 : 0}`;
    }

    if (Array.isArray(value)) {
        if (value.length === 0) {
            return 'array:0';
        }

        const first = value[0];
        const middle = value[Math.floor(value.length / 2)];
        const last = value[value.length - 1];
        const sample = [first, middle, last].map((item) => {
            if (item === null || item === undefined) {
                return String(item);
            }
            if (typeof item !== 'object') {
                return String(item);
            }
            try {
                return JSON.stringify(item).slice(0, 240);
            } catch (_error) {
                return Object.keys(item).slice(0, 8).join(',');
            }
        });

        return `array:${value.length}:${sample.join('|')}`;
    }

    try {
        return `object:${JSON.stringify(value).slice(0, 480)}`;
    } catch (_error) {
        return `object:${Object.keys(value).sort().join(',')}`;
    }
}

function applyLargeDataModeDefaults(props) {
    if (!props.largeDataMode) {
        return props;
    }

    const next = {...props};

    if (next.eventDataMode === undefined || next.eventDataMode === null) {
        next.eventDataMode = 'summary';
    }

    if (next.pointsMerge === undefined) {
        next.pointsMerge = true;
    }

    if (next.hexBinMerge === undefined) {
        next.hexBinMerge = true;
    }

    const transitionDefaults = {
        pointsTransitionDuration: 0,
        arcsTransitionDuration: 0,
        polygonsTransitionDuration: 0,
        pathTransitionDuration: 0,
        heatmapsTransitionDuration: 0,
        hexTransitionDuration: 0,
        hexPolygonsTransitionDuration: 0,
        tilesTransitionDuration: 0,
        labelsTransitionDuration: 0
    };

    Object.keys(transitionDefaults).forEach((key) => {
        if (next[key] === undefined) {
            next[key] = transitionDefaults[key];
        }
    });

    if (next.currentViewReportInterval === undefined || next.currentViewReportInterval === 250) {
        next.currentViewReportInterval = 400;
    }

    return next;
}

export {
    DATA_URL_TYPE,
    LAYER_DATA_PROP_NAMES,
    EVENT_FEEDBACK_PROP_NAMES,
    applyLargeDataModeDefaults,
    compactEventData,
    fetchLayerData,
    fingerprintLayerData,
    isDataUrlSpec,
    normaliseDataUrlSpec
};
