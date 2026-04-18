import os
import csv
import io
import json
import math
import time
from pathlib import Path
from random import Random
from urllib.request import urlopen

import dash_globe
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update


DEBUG_ENV_VAR = "DASH_GLOBE_DEBUG"
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}


def is_demo_debug_enabled():
    return os.getenv(DEBUG_ENV_VAR, "").strip().lower() in TRUTHY_ENV_VALUES


def get_demo_run_kwargs():
    debug_enabled = is_demo_debug_enabled()
    return {
        "debug": debug_enabled,
        "dev_tools_ui": debug_enabled,
        "dev_tools_props_check": debug_enabled,
        "dev_tools_hot_reload": debug_enabled,
    }


def build_random_points(count, seed):
    rng = Random(seed)
    palette = ["red", "white", "blue", "green"]
    return [
        {
            "lat": (rng.random() - 0.5) * 180,
            "lng": (rng.random() - 0.5) * 360,
            "size": round(rng.random() / 3, 4),
            "color": palette[rng.randrange(len(palette))],
        }
        for _ in range(count)
    ]


def build_random_arcs(count, seed):
    rng = Random(seed)
    palette = ["red", "white", "blue", "green"]
    return [
        {
            "startLat": round((rng.random() - 0.5) * 180, 4),
            "startLng": round((rng.random() - 0.5) * 360, 4),
            "endLat": round((rng.random() - 0.5) * 180, 4),
            "endLng": round((rng.random() - 0.5) * 360, 4),
            "color": [palette[rng.randrange(len(palette))], palette[rng.randrange(len(palette))]],
            "dashLength": round(rng.random(), 4),
            "dashGap": round(rng.random(), 4),
            "dashTime": round(rng.random() * 4000 + 500, 2),
        }
        for _ in range(count)
    ]


def build_random_rings(count, seed):
    rng = Random(seed)
    return [
        {
            "lat": round((rng.random() - 0.5) * 180, 4),
            "lng": round((rng.random() - 0.5) * 360, 4),
            "maxR": round(rng.random() * 20 + 3, 4),
            "propagationSpeed": round((rng.random() - 0.5) * 20 + 1, 4),
            "repeatPeriod": round(rng.random() * 2000 + 200, 2),
        }
        for _ in range(count)
    ]


def build_heatmap_points(count, seed):
    rng = Random(seed)
    return [
        {
            "lat": round((rng.random() - 0.5) * 160, 4),
            "lng": round((rng.random() - 0.5) * 360, 4),
            "weight": round(rng.random(), 4),
        }
        for _ in range(count)
    ]


def current_time_millis():
    return int(round(time.time() * 1000))


def normalise_emit_arcs_state(state):
    if not isinstance(state, dict):
        return build_emit_arcs_state()

    return build_emit_arcs_state(
        previous_coords=state.get("previousCoords"),
        arcs=state.get("arcs"),
        rings=state.get("rings"),
    )


def build_emit_arcs_state(previous_coords=None, arcs=None, rings=None):
    return {
        "previousCoords": dict(previous_coords) if previous_coords else None,
        "arcs": [dict(arc) for arc in (arcs or [])],
        "rings": [dict(ring) for ring in (rings or [])],
    }


def build_emit_arc_entry(start_coords, end_coords, now_ms):
    return {
        "startLat": start_coords["lat"],
        "startLng": start_coords["lng"],
        "endLat": end_coords["lat"],
        "endLng": end_coords["lng"],
        "createdAt": now_ms,
        "expiresAt": now_ms + EMIT_ARCS_FLIGHT_TIME * 2,
    }


def build_emit_ring_entry(coords, *, visible_from, now_ms):
    return {
        "lat": coords["lat"],
        "lng": coords["lng"],
        "visibleFrom": visible_from,
        "expiresAt": visible_from + int(EMIT_ARCS_FLIGHT_TIME * EMIT_ARCS_ARC_REL_LEN),
        "createdAt": now_ms,
    }


def append_emit_arc_click(state, click_data, now_ms):
    next_state = normalise_emit_arcs_state(state)
    if not click_data or click_data.get("layer") != "globe":
        return next_state

    coords = dash_globe.event_coords(click_data)
    if coords is None:
        return next_state

    previous_coords = next_state.get("previousCoords")
    next_state["previousCoords"] = dict(coords)

    if previous_coords is None:
        next_state["rings"].append(
            build_emit_ring_entry(
                coords,
                visible_from=now_ms,
                now_ms=now_ms,
            )
        )
        return next_state

    start_coords = dict(previous_coords)
    next_state["arcs"].append(build_emit_arc_entry(start_coords, coords, now_ms))
    next_state["rings"].append(build_emit_ring_entry(start_coords, visible_from=now_ms, now_ms=now_ms))
    next_state["rings"].append(
        build_emit_ring_entry(
            coords,
            visible_from=now_ms + EMIT_ARCS_FLIGHT_TIME,
            now_ms=now_ms,
        )
    )
    return next_state


def build_emit_arcs_snapshot(state, now_ms):
    next_state = normalise_emit_arcs_state(state)

    active_arcs = []
    retained_arcs = []
    for arc in next_state["arcs"]:
        created_at = arc.get("createdAt", now_ms)
        expires_at = arc.get("expiresAt", 0)
        if expires_at <= now_ms:
            continue

        retained_arcs.append(arc)
        arc_coords = {
            key: value
            for key, value in arc.items()
            if key not in {"createdAt", "expiresAt"}
        }
        pulse_progress = max(0.0, min((now_ms - created_at) / EMIT_ARCS_FLIGHT_TIME, 1.0))
        active_arcs.append(
            {
                **arc_coords,
                "color": "rgba(255, 140, 0, 0.25)",
                "altitude": 0.2,
                "stroke": 0.12,
                "dashLength": 1,
                "dashGap": 0,
                "dashInitialGap": 0,
                "dashAnimateTime": 0,
            }
        )
        active_arcs.append(
            {
                **arc_coords,
                "color": "darkOrange",
                "altitude": 0.2,
                "stroke": 0.22,
                "dashLength": EMIT_ARCS_ARC_REL_LEN,
                "dashGap": 2,
                "dashInitialGap": 1 - pulse_progress,
                "dashAnimateTime": 0,
            }
        )

    active_rings = []
    retained_rings = []
    for ring in next_state["rings"]:
        visible_from = ring.get("visibleFrom", 0)
        expires_at = ring.get("expiresAt", 0)
        if expires_at <= now_ms:
            continue

        retained_rings.append(ring)
        if visible_from <= now_ms:
            active_rings.append(
                {
                    key: value
                    for key, value in ring.items()
                    if key not in {"visibleFrom", "expiresAt", "createdAt"}
                }
            )

    next_state["arcs"] = retained_arcs
    next_state["rings"] = retained_rings
    return next_state, active_arcs, active_rings


def build_portugal_route(route_id, src_iata, dst_iata, airline, airports_by_iata):
    src_airport = airports_by_iata[src_iata]
    dst_airport = airports_by_iata[dst_iata]
    return {
        "routeId": route_id,
        "airline": airline,
        "srcIata": src_iata,
        "dstIata": dst_iata,
        "srcAirport": src_airport,
        "dstAirport": dst_airport,
        "label": f"{airline}: {src_iata} -> {dst_iata}",
        "startLat": src_airport["lat"],
        "startLng": src_airport["lng"],
        "endLat": dst_airport["lat"],
        "endLng": dst_airport["lng"],
    }


def build_airline_route_styles(hovered_route_id=None):
    hovered = hovered_route_id is not None
    styled_routes = []

    for route in PORTUGAL_ROUTES:
        opacity = AIRLINE_ROUTE_BASE_OPACITY
        if hovered:
            opacity = AIRLINE_ROUTE_HIGHLIGHT_OPACITY if route["routeId"] == hovered_route_id else AIRLINE_ROUTE_BASE_OPACITY / 4

        styled_routes.append(
            {
                **route,
                "color": [
                    f"rgba(0, 255, 0, {opacity:.3f})",
                    f"rgba(255, 0, 0, {opacity:.3f})",
                ],
            }
        )

    return styled_routes


def fetch_openflights_rows(url, timeout=10):
    with urlopen(url, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return list(csv.reader(io.StringIO(payload)))


def parse_openflights_airport(row):
    if len(row) < 8:
        return None

    iata = row[4].strip()
    if not iata or iata == r"\N":
        return None

    try:
        lat = float(row[6])
        lng = float(row[7])
    except (TypeError, ValueError):
        return None

    return {
        "airportId": row[0],
        "name": row[1],
        "city": row[2],
        "country": row[3],
        "iata": iata,
        "lat": lat,
        "lng": lng,
        "color": "orange",
        "label": f"{row[2]} ({iata})",
    }


def parse_openflights_route(row):
    if len(row) < 8:
        return None

    src_iata = row[2].strip()
    dst_iata = row[4].strip()
    if not src_iata or not dst_iata or src_iata == r"\N" or dst_iata == r"\N":
        return None

    return {
        "airline": row[0] or "Unknown airline",
        "srcIata": src_iata,
        "dstIata": dst_iata,
        "stops": row[7],
    }


def load_openflights_portugal_data():
    try:
        airports_rows = fetch_openflights_rows(OPENFLIGHTS_AIRPORTS_URL)
        routes_rows = fetch_openflights_rows(OPENFLIGHTS_ROUTES_URL)

        airports = [
            airport
            for airport in (parse_openflights_airport(row) for row in airports_rows)
            if airport and airport["country"] == AIRLINE_ROUTE_COUNTRY
        ]
        airports_by_iata = {airport["iata"]: airport for airport in airports}

        routes = []
        for index, row in enumerate(routes_rows):
            route = parse_openflights_route(row)
            if not route or route["stops"] != "0":
                continue

            src_airport = airports_by_iata.get(route["srcIata"])
            dst_airport = airports_by_iata.get(route["dstIata"])
            if not src_airport or not dst_airport:
                continue

            routes.append(
                {
                    "routeId": f"{route['srcIata'].lower()}-{route['dstIata'].lower()}-{index}",
                    "airline": route["airline"],
                    "srcIata": route["srcIata"],
                    "dstIata": route["dstIata"],
                    "srcAirport": src_airport,
                    "dstAirport": dst_airport,
                    "label": f"{route['airline']}: {route['srcIata']} -> {route['dstIata']}",
                    "startLat": src_airport["lat"],
                    "startLng": src_airport["lng"],
                    "endLat": dst_airport["lat"],
                    "endLng": dst_airport["lng"],
                }
            )

        if airports and routes:
            return airports, routes
    except Exception:
        pass

    return FALLBACK_PORTUGAL_AIRPORTS, FALLBACK_PORTUGAL_ROUTES


def fetch_json_resource(url, timeout=5):
    with urlopen(url, timeout=timeout) as response:
        return json.load(response)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(clamp(int(round(channel)), 0, 255) for channel in rgb))


def interpolate_palette(value, max_value, palette):
    if not palette:
        return "#cccccc"
    if len(palette) == 1 or max_value <= 0:
        return palette[-1]

    scaled = clamp(value / max_value, 0, 1) * (len(palette) - 1)
    lower_index = int(scaled)
    upper_index = min(lower_index + 1, len(palette) - 1)
    fraction = scaled - lower_index

    lower_rgb = hex_to_rgb(palette[lower_index])
    upper_rgb = hex_to_rgb(palette[upper_index])
    mixed = tuple(
        lower_channel + (upper_channel - lower_channel) * fraction
        for lower_channel, upper_channel in zip(lower_rgb, upper_rgb)
    )
    return rgb_to_hex(mixed)


def get_country_metric(feature):
    return feature["gdp"] / max(1e5, feature["population"])


def build_country_label(feature):
    return (
        f"<div><b>{feature['name']} ({feature['isoA2']}):</b></div>"
        f"<div>GDP: <i>{feature['gdp']:,.0f}</i> M$</div>"
        f"<div>Population: <i>{feature['population']:,.0f}</i></div>"
    )


def build_population_country_label(feature):
    population_millions = round(feature["population"] / 1e4) / 1e2
    return (
        f"<b>{feature['name']} ({feature['isoA2']})</b> <br />"
        f"Population: <i>{population_millions:,.2f}M</i>"
    )


def get_population_altitude(feature):
    return max(0.1, feature["population"] ** 0.5 * 7e-5)


def parse_country_feature(feature):
    properties = feature.get("properties") or {}
    iso_a2 = properties.get("ISO_A2")
    geometry = feature.get("geometry")

    if not iso_a2 or iso_a2 == "AQ" or not geometry:
        return None

    try:
        gdp = float(properties.get("GDP_MD_EST") or 0)
        population = float(properties.get("POP_EST") or 0)
    except (TypeError, ValueError):
        return None

    country = {
        "countryId": iso_a2,
        "isoA2": iso_a2,
        "name": properties.get("ADMIN") or properties.get("NAME") or iso_a2,
        "gdp": gdp,
        "population": population,
        "geometry": geometry,
    }
    country["labelHtml"] = build_country_label(country)
    country["populationLabelHtml"] = build_population_country_label(country)
    country["populationAltitude"] = get_population_altitude(country)
    country["metric"] = get_country_metric(country)
    return country


def load_choropleth_countries():
    try:
        feature_collection = fetch_json_resource(CHOROPLETH_COUNTRIES_URL)
        countries = [
            country
            for country in (parse_country_feature(feature) for feature in feature_collection.get("features", []))
            if country
        ]
        if countries:
            return countries
    except Exception:
        pass

    return [parse_country_feature(feature) for feature in FALLBACK_CHOROPLETH_FEATURES]


def build_choropleth_country_styles():
    return [
        {
            **country,
            "altitude": 0.06,
            "capColor": interpolate_palette(country["metric"], CHOROPLETH_MAX_METRIC, CHOROPLETH_PALETTE),
            "sideColor": "rgba(0, 100, 0, 0.15)",
            "strokeColor": "#111",
        }
        for country in CHOROPLETH_COUNTRIES
    ]


def build_population_country_styles():
    return [
        {
            **country,
            "capColor": "rgba(200, 0, 0, 0.6)",
            "sideColor": "rgba(0, 100, 0, 0.05)",
        }
        for country in CHOROPLETH_COUNTRIES
    ]


def build_tiles_example_data(grid_size=(60, 20), seed=41):
    lng_steps, lat_steps = grid_size
    tile_width = 360 / lng_steps
    tile_height = 180 / lat_steps
    rng = Random(seed)
    colors = ["red", "green", "yellow", "blue", "orange", "pink", "brown", "purple", "magenta"]
    materials = [
        dash_globe.lambert_material(color=color, opacity=0.6, transparent=True)
        for color in colors
    ]
    materials_by_color = {material["color"]: material for material in materials}

    tiles = []
    for lng_index in range(lng_steps):
        for lat_index in range(lat_steps):
            lat = -90 + (lat_index + 0.5) * tile_height
            lng = -180 + lng_index * tile_width
            color_name = colors[rng.randrange(len(colors))]
            tiles.append(
                {
                    "tileId": f"{lng_index}-{lat_index}",
                    "lat": lat,
                    "lng": lng,
                    "material": materials_by_color[color_name],
                    "colorName": color_name,
                    "labelHtml": (
                        f"<div><b>{color_name.title()} tile</b></div>"
                        f"<div>lat: <i>{lat:.1f}</i>, lng: <i>{lng:.1f}</i></div>"
                    ),
                }
            )

    return tiles, tile_width, tile_height


def get_world_city_size(population):
    return max(0, population) ** 0.5 * 4e-4


def build_world_city(name, country, lat, lng, pop_max):
    size = get_world_city_size(pop_max)
    return {
        "cityId": f"{country.lower()}-{name.lower().replace(' ', '-')}",
        "name": name,
        "country": country,
        "lat": lat,
        "lng": lng,
        "popMax": pop_max,
        "size": size,
        "dotRadius": size,
        "color": "rgba(255, 165, 0, 0.75)",
        "labelHtml": (
            f"<div><b>{name}, {country}</b></div>"
            f"<div>Population: <i>{pop_max:,.0f}</i></div>"
        ),
    }


def parse_world_city_feature(feature):
    properties = feature.get("properties") or {}

    name = properties.get("name")
    country = properties.get("adm0name") or properties.get("sov0name") or "Unknown"
    try:
        lat = float(properties.get("latitude"))
        lng = float(properties.get("longitude"))
        pop_max = float(properties.get("pop_max") or 0)
    except (TypeError, ValueError):
        return None

    if not name:
        return None

    return build_world_city(name, country, lat, lng, pop_max)


def load_world_cities():
    try:
        feature_collection = fetch_json_resource(WORLD_CITIES_URL)
        cities = [
            city
            for city in (parse_world_city_feature(feature) for feature in feature_collection.get("features", []))
            if city
        ]
        if cities:
            return cities
    except Exception:
        pass

    return FALLBACK_WORLD_CITIES


def build_submarine_cable_label(name, owners, cable_id, segment_index):
    owners_text = owners or "Unknown owner"
    return (
        f"<div><b>{name}</b></div>"
        f"<div>Owners: <i>{owners_text}</i></div>"
        f"<div>Segment: <i>{segment_index + 1}</i> | ID: <i>{cable_id}</i></div>"
    )


def build_submarine_cable_segment(coords, properties, segment_index):
    points = []
    for coord in coords:
        if not isinstance(coord, (list, tuple)) or len(coord) < 2:
            continue

        try:
            lng = float(coord[0])
            lat = float(coord[1])
        except (TypeError, ValueError):
            continue

        point = {
            "lng": round(lng, 4),
            "lat": round(lat, 4),
        }
        if len(coord) > 2:
            try:
                point["altitude"] = round(float(coord[2]), 5)
            except (TypeError, ValueError):
                pass
        points.append(point)

    if len(points) < 2:
        return None

    name = properties.get("name") or properties.get("slug") or "Unnamed cable"
    cable_id = str(properties.get("id") or properties.get("slug") or name.lower().replace(" ", "-"))
    color = properties.get("color") or "#4cc9f0"
    owners = properties.get("owners")

    return {
        "segmentId": f"{cable_id}-{segment_index}",
        "cableId": cable_id,
        "name": name,
        "owners": owners,
        "color": color,
        "coords": points,
        "labelHtml": build_submarine_cable_label(name, owners, cable_id, segment_index),
    }


def parse_submarine_cable_feature(feature):
    geometry = feature.get("geometry") or {}
    properties = feature.get("properties") or {}
    coordinates = geometry.get("coordinates") or []

    if geometry.get("type") == "LineString":
        segments = [coordinates]
    elif geometry.get("type") == "MultiLineString":
        segments = coordinates
    else:
        return []

    return [
        segment
        for segment in (
            build_submarine_cable_segment(coords, properties, segment_index)
            for segment_index, coords in enumerate(segments)
        )
        if segment
    ]


def load_submarine_cable_paths():
    try:
        feature_collection = fetch_json_resource(SUBMARINE_CABLES_URL, timeout=15)
        paths = []
        for feature in feature_collection.get("features", []):
            paths.extend(parse_submarine_cable_feature(feature))

        if paths:
            return paths
    except Exception:
        pass

    return FALLBACK_SUBMARINE_CABLE_PATHS


def format_demo_timestamp(timestamp):
    return str(timestamp).replace("T", " ").replace("Z", " UTC")


def normalize_demo_longitude(lng):
    return ((lng + 180) % 360) - 180


def build_situation_room_random_global_location(story_seed):
    rng = Random(f"situation-room-global:{story_seed}")
    return {
        "name": "Global",
        "lat": round(rng.uniform(-58, 58), 4),
        "lng": round(rng.uniform(-180, 180), 4),
    }


def normalize_situation_room_story(story):
    source_story = dict(story or {})
    source_meta = dict(source_story.get("meta") or {})
    source_location = dict(source_story.get("location") or {})
    topics = [
        str(topic).strip()
        for topic in (source_meta.get("topics") or [])
        if str(topic).strip()
    ]
    primary_topic = str(source_meta.get("topic") or (topics[0] if topics else "news")).strip().lower() or "news"
    location_name = str(source_location.get("name") or "Unknown location").strip() or "Unknown location"
    story_seed = source_story.get("id") or source_story.get("title") or location_name
    location = {
        "name": location_name,
        "lat": float(source_location.get("lat") or 0),
        "lng": float(source_location.get("lng") or 0),
    }

    if location_name.lower() == "global":
        location = build_situation_room_random_global_location(story_seed)

    return {
        "id": str(source_story.get("id") or story_seed),
        "title": source_story.get("title") or "Untitled story",
        "description": source_story.get("description") or "",
        "image": source_story.get("image"),
        "publishedAt": source_story.get("publishedAt") or "",
        "source": source_story.get("source") or "Unknown source",
        "url": source_story.get("url"),
        "location": location,
        "meta": {
            **source_meta,
            "country": source_meta.get("country"),
            "topic": primary_topic,
            "topics": topics or [primary_topic],
        },
    }


def load_situation_room_news_payload():
    news_path = Path(__file__).resolve().parents[1] / "public" / "news.json"
    with news_path.open("r", encoding="utf-8") as news_file:
        payload = json.load(news_file)

    stories = [
        normalize_situation_room_story(story)
        for story in payload.get("stories", [])
    ]
    return {
        "updatedAt": payload.get("updatedAt", ""),
        "count": len(stories),
        "stories": stories,
    }


def get_demo_angular_distance(lat_a, lng_a, lat_b, lng_b):
    start_lat = math.radians(lat_a)
    start_lng = math.radians(lng_a)
    end_lat = math.radians(lat_b)
    end_lng = math.radians(lng_b)
    cosine = (
        math.sin(start_lat) * math.sin(end_lat)
        + math.cos(start_lat) * math.cos(end_lat) * math.cos(start_lng - end_lng)
    )
    return math.acos(clamp(cosine, -1, 1))


def build_situation_room_story_label(story):
    location = story.get("location") or {}
    meta = story.get("meta") or {}
    return (
        f"<div><b>{story.get('title', 'Untitled story')}</b></div>"
        f"<div>{story.get('source', 'Unknown source')} | {location.get('name', 'Unknown location')}</div>"
        f"<div>{meta.get('topic', 'news').title()}</div>"
    )


def build_situation_room_story_point(story):
    topic = ((story.get("meta") or {}).get("topic") or "").lower()
    radius_by_topic = {
        "politics": 0.18,
        "disaster": 0.24,
        "economy": 0.2,
    }
    location = story["location"]
    return {
        "storyId": story["id"],
        "lat": location["lat"],
        "lng": location["lng"],
        "radius": radius_by_topic.get(topic, 0.18),
        "altitude": 0.015,
        "color": "rgba(103, 232, 249, 0.95)",
        "labelHtml": build_situation_room_story_label(story),
    }


def build_situation_room_story_ring(story, index):
    location = story["location"]
    return {
        "storyId": story["id"],
        "lat": location["lat"],
        "lng": location["lng"],
        "maxR": 4.6 + index * 0.8,
        "propagationSpeed": 1.9 + index * 0.35,
        "repeatPeriod": 1500 + index * 180,
    }


def build_situation_room_story_panel(story, layout_style=None):
    meta = story.get("meta") or {}
    location = story.get("location") or {}
    topic = (meta.get("topic") or "news").upper()
    country = meta.get("country") or "GLOBAL"
    title_link = html.A(
        story.get("title", "Untitled story"),
        href=story.get("url"),
        target="_blank",
        rel="noreferrer",
        style={
            "color": "#f8fafc",
            "textDecoration": "none",
        },
    )
    return html.Div(
        [
            html.Div(
                [
                    html.Span(topic, style=SITUATION_ROOM_TOPIC_STYLE),
                    html.Span(country, style=SITUATION_ROOM_COUNTRY_STYLE),
                ],
                style={"display": "flex", "justifyContent": "space-between", "gap": "10px", "alignItems": "center"},
            ),
            html.Img(
                src=story.get("image"),
                alt=story.get("title", "Story image"),
                style=SITUATION_ROOM_CARD_IMAGE_STYLE,
            ),
            html.H4(
                title_link,
                style={"margin": 0, "fontSize": "0.98rem", "lineHeight": 1.35, "color": "#f8fafc"},
            ),
            html.P(
                story.get("description", ""),
                style=SITUATION_ROOM_CARD_DESCRIPTION_STYLE,
            ),
            html.Div(
                [
                    html.Span(story.get("source", "Unknown source"), style={"fontWeight": 700, "color": "#67e8f9"}),
                    html.Span(location.get("name", "Unknown location"), style={"color": "#cbd5e1"}),
                ],
                style={"display": "flex", "justifyContent": "space-between", "gap": "10px", "fontSize": "0.76rem", "marginTop": "auto"},
            ),
            html.Div(
                format_demo_timestamp(story.get("publishedAt", "")),
                style={"fontSize": "0.73rem", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7dd3fc"},
            ),
        ],
        style={**SITUATION_ROOM_CARD_STYLE, **(layout_style or {})},
    )


def build_situation_room_story_points():
    return [
        build_situation_room_story_point(story)
        for story in SITUATION_ROOM_STORIES
    ]


def build_situation_room_live_view(cycle_step=0):
    elapsed_seconds = max(0, cycle_step or 0) * (SITUATION_ROOM_STORY_DURATION_MS / 1000)
    rotation_degrees = elapsed_seconds * SITUATION_ROOM_AUTO_ROTATE_SPEED * 6
    return {
        **SITUATION_ROOM_INITIAL_VIEW,
        "lng": normalize_demo_longitude(SITUATION_ROOM_INITIAL_VIEW["lng"] - rotation_degrees),
    }


def get_situation_room_story_forward_angle(story, current_view=None):
    view = {
        **SITUATION_ROOM_INITIAL_VIEW,
        **(current_view or build_situation_room_live_view()),
    }
    location = story["location"]
    return get_demo_angular_distance(
        location["lat"],
        location["lng"],
        view["lat"],
        view["lng"],
    )


def get_situation_room_story_side(story, current_view=None):
    view = {
        **SITUATION_ROOM_INITIAL_VIEW,
        **(current_view or build_situation_room_live_view()),
    }
    relative_lng = normalize_demo_longitude(story["location"]["lng"] - view["lng"])
    return "right" if relative_lng >= 0 else "left"


def get_situation_room_story_relative_lng(story, current_view=None):
    view = {
        **SITUATION_ROOM_INITIAL_VIEW,
        **(current_view or build_situation_room_live_view()),
    }
    return normalize_demo_longitude(story["location"]["lng"] - view["lng"])


def build_situation_room_story_overlay(story, side):
    location = story["location"]
    return {
        "storyId": story["id"],
        "lat": location["lat"],
        "lng": location["lng"],
        "altitude": 0.015,
        "screenSide": side,
        "screenX": SITUATION_ROOM_CARD_SCREEN_X_BY_SIDE.get(side, 16),
        "screenY": SITUATION_ROOM_CARD_SCREEN_Y,
        "tether": True,
        "tetherColor": "rgba(103, 232, 249, 0.95)",
        "tetherWidth": 1.9,
        "tetherAttach": "right" if side == "left" else "left",
    }


def is_situation_room_story_visible(story, current_view=None):
    return get_situation_room_story_forward_angle(story, current_view) <= math.radians(
        SITUATION_ROOM_VISIBLE_HEMISPHERE_DEGREES
    )


def build_situation_room_story_snapshot(story, index, side, current_view=None):
    return {
        "index": index,
        "side": side,
        "story": story,
        "point": build_situation_room_story_point(story),
        "ring": build_situation_room_story_ring(story, index),
        "overlay": build_situation_room_story_overlay(story, side),
        "card": build_situation_room_story_panel(story),
        "forwardAngle": get_situation_room_story_forward_angle(story, current_view),
        "relativeLng": get_situation_room_story_relative_lng(story, current_view),
    }


def build_situation_room_story_candidates(current_view=None):
    candidates = []

    for index, story in enumerate(SITUATION_ROOM_STORIES):
        if not is_situation_room_story_visible(story, current_view):
            continue

        candidates.append(
            build_situation_room_story_snapshot(
                story,
                index,
                get_situation_room_story_side(story, current_view),
                current_view,
            )
        )

    candidates.sort(key=lambda snapshot: (snapshot["forwardAngle"], abs(snapshot["relativeLng"]), snapshot["index"]))
    return candidates


def build_situation_room_visible_story_snapshots(current_view=None, cycle_step=0):
    view = {
        **build_situation_room_live_view(cycle_step),
        **(current_view or {}),
    }
    selected = build_situation_room_story_candidates(view)[:2]
    if not selected:
        return []

    selected.sort(key=lambda snapshot: (snapshot["relativeLng"], snapshot["forwardAngle"], snapshot["index"]))

    if len(selected) == 1:
        assigned_sides = ["right" if selected[0]["relativeLng"] >= 0 else "left"]
    else:
        assigned_sides = list(SITUATION_ROOM_SIDE_ORDER)

    snapshots = [
        build_situation_room_story_snapshot(
            snapshot["story"],
            snapshot["index"],
            side,
            view,
        )
        for snapshot, side in zip(selected, assigned_sides)
    ]
    snapshots.sort(key=lambda snapshot: (SITUATION_ROOM_SIDE_ORDER.index(snapshot["side"]), snapshot["index"]))
    return snapshots


def build_situation_room_header(snapshots):
    return html.Div(
        [
            html.Div("Situation Room", style={"fontSize": "0.8rem", "fontWeight": 700, "letterSpacing": "0.18em", "textTransform": "uppercase", "color": "#67e8f9"}),
            html.Div(
                [
                    html.Span(f"{len(snapshots)} front-most stories"),
                    html.Span(f"Refreshes every {SITUATION_ROOM_STORY_DURATION_MS / 1000:.1f}s"),
                    html.Span(format_demo_timestamp(SITUATION_ROOM_NEWS_PAYLOAD["updatedAt"])),
                ],
                style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "justifyContent": "center", "fontSize": "0.74rem", "color": "#cbd5e1"},
            ),
        ],
        style=SITUATION_ROOM_HEADER_STYLE,
    )


def build_situation_room_story_status(snapshots):
    summary_children = [
        html.Span(
            f"Monitoring {len(SITUATION_ROOM_STORIES)} stories",
            style={"fontWeight": 700, "color": "#e2e8f0"},
        )
    ]
    for snapshot in snapshots:
        summary_children.append(
            html.Span(
                f"{snapshot['side'].title()}: {snapshot['story']['location']['name']}",
                style={"fontWeight": 700},
            )
        )
        summary_children.append(html.Span(snapshot["story"].get("source", "Unknown source")))
    if not snapshots:
        summary_children.append(html.Span("No visible side stories in the current view"))

    return html.Div(
        summary_children,
        style={
            "position": "absolute",
            "right": "16px",
            "bottom": "16px",
            "display": "flex",
            "gap": "10px",
            "flexWrap": "wrap",
            "padding": "10px 12px",
            "border": "1px solid rgba(103, 232, 249, 0.24)",
            "borderRadius": "999px",
            "background": "rgba(2, 6, 23, 0.72)",
            "boxShadow": "0 0 24px rgba(34, 211, 238, 0.1)",
            "fontSize": "0.72rem",
            "color": "#cbd5e1",
            "zIndex": 1,
            "pointerEvents": "none",
        },
    )


def build_situation_room_story_cards(snapshots):
    snapshots_by_side = {snapshot["side"]: snapshot for snapshot in snapshots}
    return [
        snapshots_by_side[side]["card"]
        for side in SITUATION_ROOM_SIDE_ORDER
        if side in snapshots_by_side
    ]


def build_situation_room_selection_signature(snapshots):
    return [
        {
            "storyId": snapshot["story"]["id"],
            "side": snapshot["side"],
        }
        for snapshot in snapshots
    ]


BASIC_EXAMPLE_POINTS = build_random_points(300, seed=7)
RANDOM_ARCS_EXAMPLE_DATA = build_random_arcs(20, seed=17)
RANDOM_RINGS_EXAMPLE_DATA = build_random_rings(10, seed=23)
HEATMAP_EXAMPLE_DATA = build_heatmap_points(900, seed=29)
EMIT_ARCS_GLOBE_ID = "emit-arcs-on-click-globe"
EMIT_ARCS_STORE_ID = "emit-arcs-on-click-state"
EMIT_ARCS_INTERVAL_ID = "emit-arcs-on-click-interval"
EMIT_ARCS_ARC_REL_LEN = 0.4
EMIT_ARCS_FLIGHT_TIME = 1000
EMIT_ARCS_NUM_RINGS = 3
EMIT_ARCS_RINGS_MAX_R = 5
EMIT_ARCS_RING_PROPAGATION_SPEED = 5
EMIT_ARCS_RING_REPEAT_PERIOD = EMIT_ARCS_FLIGHT_TIME * EMIT_ARCS_ARC_REL_LEN / EMIT_ARCS_NUM_RINGS
EMIT_ARCS_TICK_INTERVAL = 100
EMIT_ARCS_EVENT_PLACEHOLDER = (
    "Click Run to mount this globe, click once to set the anchor point, "
    "then click again to emit an arc and ripple rings to the new location."
)
OPENFLIGHTS_AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
OPENFLIGHTS_ROUTES_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
WORLD_CITIES_URL = (
    "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/"
    "ne_110m_populated_places_simple.geojson"
)
SUBMARINE_CABLES_URL = "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json"
CHOROPLETH_COUNTRIES_URL = (
    "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/"
    "ne_110m_admin_0_countries.geojson"
)
CHOROPLETH_BACKGROUND_IMAGE_URL = "https://unpkg.com/three-globe@2.45.2/example/img/night-sky.png"
CHOROPLETH_PALETTE = ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#f03b20", "#bd0026"]
AIRLINE_ROUTE_COUNTRY = "Portugal"
FALLBACK_PORTUGAL_AIRPORTS = [
    {
        "airportId": "LIS",
        "name": "Humberto Delgado Airport",
        "city": "Lisbon",
        "country": "Portugal",
        "iata": "LIS",
        "lat": 38.7742,
        "lng": -9.1342,
        "color": "orange",
        "label": "Lisbon (LIS)",
    },
    {
        "airportId": "OPO",
        "name": "Francisco Sa Carneiro Airport",
        "city": "Porto",
        "country": "Portugal",
        "iata": "OPO",
        "lat": 41.2481,
        "lng": -8.6814,
        "color": "orange",
        "label": "Porto (OPO)",
    },
    {
        "airportId": "FAO",
        "name": "Faro Airport",
        "city": "Faro",
        "country": "Portugal",
        "iata": "FAO",
        "lat": 37.0144,
        "lng": -7.9659,
        "color": "orange",
        "label": "Faro (FAO)",
    },
    {
        "airportId": "FNC",
        "name": "Cristiano Ronaldo International Airport",
        "city": "Funchal",
        "country": "Portugal",
        "iata": "FNC",
        "lat": 32.6979,
        "lng": -16.7745,
        "color": "orange",
        "label": "Funchal (FNC)",
    },
    {
        "airportId": "PDL",
        "name": "Joao Paulo II Airport",
        "city": "Ponta Delgada",
        "country": "Portugal",
        "iata": "PDL",
        "lat": 37.7412,
        "lng": -25.6979,
        "color": "orange",
        "label": "Ponta Delgada (PDL)",
    },
    {
        "airportId": "HOR",
        "name": "Horta Airport",
        "city": "Horta",
        "country": "Portugal",
        "iata": "HOR",
        "lat": 38.5199,
        "lng": -28.7159,
        "color": "orange",
        "label": "Horta (HOR)",
    },
]
FALLBACK_PORTUGAL_AIRPORTS_BY_IATA = {airport["iata"]: airport for airport in FALLBACK_PORTUGAL_AIRPORTS}
FALLBACK_PORTUGAL_ROUTES = [
    build_portugal_route("lis-opo", "LIS", "OPO", "TAP Air Portugal", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
    build_portugal_route("lis-fao", "LIS", "FAO", "TAP Air Portugal", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
    build_portugal_route("lis-fnc", "LIS", "FNC", "TAP Air Portugal", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
    build_portugal_route("lis-pdl", "LIS", "PDL", "TAP Air Portugal", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
    build_portugal_route("lis-hor", "LIS", "HOR", "TAP Air Portugal", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
    build_portugal_route("opo-fnc", "OPO", "FNC", "TAP Air Portugal", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
    build_portugal_route("opo-pdl", "OPO", "PDL", "Azores Airlines", FALLBACK_PORTUGAL_AIRPORTS_BY_IATA),
]
PORTUGAL_AIRPORTS, PORTUGAL_ROUTES = load_openflights_portugal_data()
AIRLINE_ROUTE_BASE_OPACITY = 0.3
AIRLINE_ROUTE_HIGHLIGHT_OPACITY = 0.9
FALLBACK_WORLD_CITIES = [
    build_world_city("Tokyo", "Japan", 35.6762, 139.6503, 37339804),
    build_world_city("Delhi", "India", 28.6139, 77.2090, 29399141),
    build_world_city("Shanghai", "China", 31.2304, 121.4737, 26317104),
    build_world_city("Sao Paulo", "Brazil", -23.5505, -46.6333, 21846507),
    build_world_city("Mexico City", "Mexico", 19.4326, -99.1332, 21671908),
    build_world_city("Cairo", "Egypt", 30.0444, 31.2357, 20076002),
    build_world_city("Mumbai", "India", 19.0760, 72.8777, 19980000),
    build_world_city("Beijing", "China", 39.9042, 116.4074, 19612368),
    build_world_city("New York", "United States", 40.7128, -74.0060, 18804000),
    build_world_city("London", "United Kingdom", 51.5072, -0.1276, 9540576),
    build_world_city("Sydney", "Australia", -33.8688, 151.2093, 5367206),
]
FALLBACK_SUBMARINE_CABLE_PATHS = [
    {
        "segmentId": "marea-0",
        "cableId": "marea",
        "name": "MAREA",
        "owners": "Meta, Microsoft, Telxius",
        "color": "#ff8fab",
        "coords": [
            {"lat": 40.9701, "lng": -5.6635},
            {"lat": 43.2, "lng": -20.5},
            {"lat": 44.4, "lng": -35.8},
            {"lat": 40.7143, "lng": -74.0060},
        ],
        "labelHtml": build_submarine_cable_label("MAREA", "Meta, Microsoft, Telxius", "marea", 0),
    },
    {
        "segmentId": "jupiter-0",
        "cableId": "jupiter",
        "name": "JUPITER",
        "owners": "Google and partners",
        "color": "#4cc9f0",
        "coords": [
            {"lat": 35.6762, "lng": 139.6503},
            {"lat": 39.0, "lng": 160.0},
            {"lat": 37.7749, "lng": -122.4194},
        ],
        "labelHtml": build_submarine_cable_label("JUPITER", "Google and partners", "jupiter", 0),
    },
    {
        "segmentId": "sea-me-we-3-0",
        "cableId": "sea-me-we-3",
        "name": "SEA-ME-WE 3",
        "owners": "International consortium",
        "color": "#ffd166",
        "coords": [
            {"lat": 1.3521, "lng": 103.8198},
            {"lat": 13.7563, "lng": 100.5018},
            {"lat": 19.0760, "lng": 72.8777},
            {"lat": 25.2048, "lng": 55.2708},
            {"lat": 31.2001, "lng": 29.9187},
            {"lat": 37.9838, "lng": 23.7275},
            {"lat": 43.2965, "lng": 5.3698},
        ],
        "labelHtml": build_submarine_cable_label("SEA-ME-WE 3", "International consortium", "sea-me-we-3", 0),
    },
]
FALLBACK_CHOROPLETH_FEATURES = [
    {
        "type": "Feature",
        "properties": {"ADMIN": "United States", "ISO_A2": "US", "GDP_MD_EST": 19485394, "POP_EST": 325084756},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-125, 24], [-66, 24], [-66, 49], [-125, 49], [-125, 24]]],
        },
    },
    {
        "type": "Feature",
        "properties": {"ADMIN": "Brazil", "ISO_A2": "BR", "GDP_MD_EST": 2055500, "POP_EST": 207353391},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-74, -34], [-34, -34], [-34, 6], [-74, 6], [-74, -34]]],
        },
    },
    {
        "type": "Feature",
        "properties": {"ADMIN": "France", "ISO_A2": "FR", "GDP_MD_EST": 2699000, "POP_EST": 67106161},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-5, 42], [8, 42], [8, 51], [-5, 51], [-5, 42]]],
        },
    },
    {
        "type": "Feature",
        "properties": {"ADMIN": "India", "ISO_A2": "IN", "GDP_MD_EST": 2651000, "POP_EST": 1281935911},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[68, 8], [97, 8], [97, 35], [68, 35], [68, 8]]],
        },
    },
    {
        "type": "Feature",
        "properties": {"ADMIN": "China", "ISO_A2": "CN", "GDP_MD_EST": 12237700, "POP_EST": 1379302771},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[73, 18], [135, 18], [135, 53], [73, 53], [73, 18]]],
        },
    },
    {
        "type": "Feature",
        "properties": {"ADMIN": "Australia", "ISO_A2": "AU", "GDP_MD_EST": 1323421, "POP_EST": 23232413},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[113, -44], [154, -44], [154, -10], [113, -10], [113, -44]]],
        },
    },
]
WORLD_CITIES = load_world_cities()
SUBMARINE_CABLE_PATHS = load_submarine_cable_paths()
CHOROPLETH_COUNTRIES = load_choropleth_countries()
CHOROPLETH_MAX_METRIC = max((country["metric"] for country in CHOROPLETH_COUNTRIES), default=1)
HOLLOW_GLOBE_LAND_POLYGONS = [{"geometry": country["geometry"], "name": country["name"]} for country in CHOROPLETH_COUNTRIES]
TILE_MARGIN = 0.35
TILES_EXAMPLE_DATA, TILES_EXAMPLE_TILE_WIDTH, TILES_EXAMPLE_TILE_HEIGHT = build_tiles_example_data()
SITUATION_ROOM_NEWS_PAYLOAD = load_situation_room_news_payload()
SITUATION_ROOM_STORIES = SITUATION_ROOM_NEWS_PAYLOAD["stories"]
SITUATION_ROOM_GLOBE_ID = "situation-room-globe"
SITUATION_ROOM_HEADER_ID = "situation-room-header"
SITUATION_ROOM_STATUS_ID = "situation-room-status"
SITUATION_ROOM_SELECTION_STORE_ID = "situation-room-selection-store"
SITUATION_ROOM_STAGE_MIN_HEIGHT = "540px"
SITUATION_ROOM_GLOBE_HEIGHT = 540
SITUATION_ROOM_INITIAL_VIEW = {"lat": 25, "lng": 12, "altitude": 2.15}
SITUATION_ROOM_AUTO_ROTATE_SPEED = 0.32
SITUATION_ROOM_VISIBLE_HEMISPHERE_DEGREES = 96
SITUATION_ROOM_STORY_DURATION_MS = 1200
SITUATION_ROOM_CURRENT_VIEW_REPORT_INTERVAL = 450
SITUATION_ROOM_CARD_SCREEN_X_BY_SIDE = {"left": 0, "right": 0}
SITUATION_ROOM_CARD_SCREEN_Y = 84
SITUATION_ROOM_SIDE_ORDER = ["left", "right"]

BASIC_EXAMPLE_CODE = """import dash_globe

basic_globe = (
    dash_globe.DashGlobe(id="basic-example")
    .update_layout(height=420)
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_NIGHT
    )
    .add_points(BASIC_EXAMPLE_POINTS)
    .update_points(
        pointAltitude="size",
        pointColor="color",
    )
)"""

RANDOM_ARCS_EXAMPLE_CODE = """import dash_globe

random_arcs_globe = (
    dash_globe.DashGlobe(id="random-arcs-example")
    .update_layout(height=420)
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_NIGHT
    )
    .add_arcs(RANDOM_ARCS_EXAMPLE_DATA)
    .update_arcs(
        arcColor="color",
        arcDashLength="dashLength",
        arcDashGap="dashGap",
        arcDashAnimateTime="dashTime",
    )
)"""

EMIT_ARCS_ON_CLICK_EXAMPLE_CODE = """import time

import dash_globe
from dash import Input, Output, State, ctx, dcc, html


ARC_REL_LEN = 0.4
FLIGHT_TIME = 1000
NUM_RINGS = 3
RINGS_MAX_R = 5
RING_PROPAGATION_SPEED = 5


def build_emit_arcs_state(previous_coords=None, arcs=None, rings=None):
    return {
        "previousCoords": dict(previous_coords) if previous_coords else None,
        "arcs": [dict(arc) for arc in (arcs or [])],
        "rings": [dict(ring) for ring in (rings or [])],
    }


emit_arcs_globe = html.Div(
    [
        dash_globe.DashGlobe(id="emit-arcs-on-click-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .update_arcs(
            [],
            arc_start_lat="startLat",
            arc_start_lng="startLng",
            arc_end_lat="endLat",
            arc_end_lng="endLng",
            arc_color="color",
            arc_altitude="altitude",
            arc_stroke="stroke",
            arc_dash_length="dashLength",
            arc_dash_gap="dashGap",
            arc_dash_initial_gap="dashInitialGap",
            arc_dash_animate_time="dashAnimateTime",
            arcs_transition_duration=0,
        )
        .update_rings(
            [],
            ring_color=dash_globe.ring_color_interpolator("rgb(255, 100, 50)"),
            ring_max_radius=RINGS_MAX_R,
            ring_propagation_speed=RING_PROPAGATION_SPEED,
            ring_repeat_period=FLIGHT_TIME * ARC_REL_LEN / NUM_RINGS,
        ),
        dcc.Store(id="emit-arcs-on-click-state", data=build_emit_arcs_state()),
        dcc.Interval(id="emit-arcs-on-click-interval", interval=100, disabled=True),
    ]
)


@app.callback(
    Output("emit-arcs-on-click-state", "data"),
    Output("emit-arcs-on-click-globe", "arcsData"),
    Output("emit-arcs-on-click-globe", "ringsData"),
    Output("emit-arcs-on-click-interval", "disabled"),
    Input("emit-arcs-on-click-globe", "clickData"),
    Input("emit-arcs-on-click-interval", "n_intervals"),
    State("emit-arcs-on-click-state", "data"),
)
def sync_emit_arcs(click_data, _n_intervals, state):
    now_ms = int(round(time.time() * 1000))
    next_state = build_emit_arcs_state(
        previous_coords=(state or {}).get("previousCoords"),
        arcs=(state or {}).get("arcs"),
        rings=(state or {}).get("rings"),
    )

    if ctx.triggered_id == "emit-arcs-on-click-globe" and click_data and click_data.get("layer") == "globe":
        end_coords = dash_globe.event_coords(click_data)
        if end_coords is not None:
            start_coords = next_state["previousCoords"]
            next_state["previousCoords"] = dict(end_coords)
            if start_coords is None:
                next_state["rings"].append(
                    {
                        "lat": end_coords["lat"],
                        "lng": end_coords["lng"],
                        "visibleFrom": now_ms,
                        "expiresAt": now_ms + FLIGHT_TIME * ARC_REL_LEN,
                    }
                )
            else:
                next_state["arcs"].append(
                    {
                        "startLat": start_coords["lat"],
                        "startLng": start_coords["lng"],
                        "endLat": end_coords["lat"],
                        "endLng": end_coords["lng"],
                        "createdAt": now_ms,
                        "expiresAt": now_ms + FLIGHT_TIME * 2,
                    }
                )
                next_state["rings"].append(
                    {
                        "lat": start_coords["lat"],
                        "lng": start_coords["lng"],
                        "visibleFrom": now_ms,
                        "expiresAt": now_ms + FLIGHT_TIME * ARC_REL_LEN,
                    }
                )
                next_state["rings"].append(
                    {
                        "lat": end_coords["lat"],
                        "lng": end_coords["lng"],
                        "visibleFrom": now_ms + FLIGHT_TIME,
                        "expiresAt": now_ms + FLIGHT_TIME + FLIGHT_TIME * ARC_REL_LEN,
                    }
                )

    next_state["arcs"] = [arc for arc in next_state["arcs"] if arc["expiresAt"] > now_ms]
    next_state["rings"] = [ring for ring in next_state["rings"] if ring["expiresAt"] > now_ms]
    arcs_data = []
    for arc in next_state["arcs"]:
        progress = max(0, min((now_ms - arc["createdAt"]) / FLIGHT_TIME, 1))
        arc_coords = {
            key: value
            for key, value in arc.items()
            if key not in {"createdAt", "expiresAt"}
        }
        arcs_data.append(
            {
                **arc_coords,
                "color": "rgba(255, 140, 0, 0.25)",
                "altitude": 0.2,
                "stroke": 0.12,
                "dashLength": 1,
                "dashGap": 0,
                "dashInitialGap": 0,
                "dashAnimateTime": 0,
            }
        )
        arcs_data.append(
            {
                **arc_coords,
                "color": "darkOrange",
                "altitude": 0.2,
                "stroke": 0.22,
                "dashLength": ARC_REL_LEN,
                "dashGap": 2,
                "dashInitialGap": 1 - progress,
                "dashAnimateTime": 0,
            }
        )
    rings_data = [
        {key: value for key, value in ring.items() if key not in {"visibleFrom", "expiresAt"}}
        for ring in next_state["rings"]
        if ring["visibleFrom"] <= now_ms
    ]
    return next_state, arcs_data, rings_data, not next_state["arcs"] and not next_state["rings"]
"""

RANDOM_RINGS_EXAMPLE_CODE = """import dash_globe

random_rings_globe = (
    dash_globe.DashGlobe(id="random-rings-example")
    .update_layout(height=420)
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_NIGHT
    )
    .add_rings(RANDOM_RINGS_EXAMPLE_DATA)
    .update_rings(
        ring_color=dash_globe.ring_color_interpolator("#ff6432"),
        ring_max_radius="maxR",
        ring_propagation_speed="propagationSpeed",
        ring_repeat_period="repeatPeriod",
    )
)"""

HEATMAP_EXAMPLE_CODE = """import random

import dash_globe


rng = random.Random(29)
heatmap_points = [
    {
        "lat": (rng.random() - 0.5) * 160,
        "lng": (rng.random() - 0.5) * 360,
        "weight": rng.random(),
    }
    for _ in range(900)
]

heatmap_globe = (
    dash_globe.DashGlobe(id="heatmap-example")
    .update_layout(height=420)
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_DARK)
    .update_interaction(enable_pointer_interaction=False)
    .add_heatmap(heatmap_points)
    .update_heatmaps(
        heatmap_point_lat="lat",
        heatmap_point_lng="lng",
        heatmap_point_weight="weight",
        heatmap_top_altitude=0.7,
        heatmaps_transition_duration=3000,
    )
)"""

DAY_NIGHT_CYCLE_EXAMPLE_CODE = """import dash_globe

day_night_cycle_globe = (
    dash_globe.DashGlobe(id="day-night-cycle-globe")
    .update_layout(
        height=420,
        background_image_url=dash_globe.PRESETS.NIGHT_SKY,
    )
    .update_globe(show_atmosphere=False)
    .update_view(lat=12, lng=-38, altitude=2.2, transition_duration=0)
    .update_day_night_cycle(
        day_image_url=dash_globe.PRESETS.EARTH,
        night_image_url=dash_globe.PRESETS.EARTH_NIGHT,
        time="2026-04-17T12:00:00Z",
        minutes_per_second=60,
    )
)"""

CLOUDS_EXAMPLE_CODE = """import dash_globe

clouds_globe = (
    dash_globe.DashGlobe(id="clouds-globe")
    .update_layout(height=420)
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_DAY,
        bump_image_url=dash_globe.PRESETS.EARTH_TOPOGRAPHY,
        show_atmosphere=False,
    )
    .update_controls(auto_rotate=True, auto_rotate_speed=0.35)
    .update_clouds(
        image_url=dash_globe.PRESETS.CLOUDS,
        altitude=0.004,
        rotation_speed=-0.006,
    )
)"""

WORLD_CITIES_EXAMPLE_CODE = """import json
from urllib.request import urlopen

import dash_globe


WORLD_CITIES_URL = (
    "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/"
    "ne_110m_populated_places_simple.geojson"
)


def load_world_cities():
    with urlopen(WORLD_CITIES_URL, timeout=5) as response:
        feature_collection = json.load(response)

    cities = []
    for feature in feature_collection["features"]:
        properties = feature["properties"]
        population = float(properties["pop_max"])
        label_size = population ** 0.5 * 4e-4
        cities.append(
            {
                "name": properties["name"],
                "lat": float(properties["latitude"]),
                "lng": float(properties["longitude"]),
                "labelHtml": (
                    f"<div><b>{properties['name']}, {properties['adm0name']}</b></div>"
                    f"<div>Population: <i>{population:,.0f}</i></div>"
                ),
                "size": label_size,
                "dotRadius": label_size,
                "color": "rgba(255, 165, 0, 0.75)",
            }
        )

    return cities


world_cities_globe = (
    dash_globe.DashGlobe(id="world-cities-globe")
    .update_layout(
        height=420,
        background_image_url=dash_globe.PRESETS.NIGHT_SKY,
    )
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
    .add_labels(load_world_cities())
    .update_labels(
        label_label="labelHtml",
        label_lat="lat",
        label_lng="lng",
        label_text="name",
        label_size="size",
        label_color="color",
        label_include_dot=True,
        label_dot_radius="dotRadius",
        label_resolution=2,
    )
)"""

SUBMARINE_CABLES_EXAMPLE_CODE = """import json
from urllib.request import urlopen

import dash_globe
from dash import Input, Output


SUBMARINE_CABLES_URL = "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json"


def load_submarine_cable_paths():
    with urlopen(SUBMARINE_CABLES_URL, timeout=15) as response:
        feature_collection = json.load(response)

    cable_paths = []
    for feature in feature_collection["features"]:
        properties = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []

        segments = coordinates if geometry.get("type") == "MultiLineString" else [coordinates]
        for segment_index, coords in enumerate(segments):
            cable_paths.append(
                {
                    "name": properties.get("name", "Unnamed cable"),
                    "color": properties.get("color", "#4cc9f0"),
                    "coords": [{"lng": lng, "lat": lat} for lng, lat, *_ in coords],
                    "labelHtml": (
                        f"<div><b>{properties.get('name', 'Unnamed cable')}</b></div>"
                        f"<div>Segment: <i>{segment_index + 1}</i></div>"
                    ),
                }
            )

    return cable_paths


submarine_cables_globe = (
    dash_globe.DashGlobe(id="submarine-cables-globe")
    .update_layout(
        height=420,
        background_image_url=dash_globe.PRESETS.NIGHT_SKY,
    )
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_DARK,
        bump_image_url=dash_globe.PRESETS.EARTH_TOPOGRAPHY,
    )
    .add_paths(load_submarine_cable_paths())
    .update_paths(
        path_label="labelHtml",
        path_points="coords",
        path_point_lat="lat",
        path_point_lng="lng",
        path_color="color",
        path_dash_length=0.1,
        path_dash_gap=0.008,
        path_dash_animate_time=12000,
        path_transition_duration=0,
    )
)


@app.callback(
    Output("submarine-cables-event", "children"),
    Input("submarine-cables-globe", "hoverData"),
)
def describe_submarine_cable_hover(hover_data):
    if hover_data is None:
        return "Hover a cable segment to inspect the latest path payload."
    return json.dumps(hover_data, indent=2)
"""

TILES_EXAMPLE_CODE = """import random

import dash_globe


TILE_MARGIN = 0.35
GRID_SIZE = (60, 20)
COLORS = ["red", "green", "yellow", "blue", "orange", "pink", "brown", "purple", "magenta"]


def build_tiles(seed=41):
    lng_steps, lat_steps = GRID_SIZE
    tile_width = 360 / lng_steps
    tile_height = 180 / lat_steps
    rng = random.Random(seed)

    materials = [
        dash_globe.lambert_material(color=color, opacity=0.6, transparent=True)
        for color in COLORS
    ]
    materials_by_color = {material["color"]: material for material in materials}

    tiles = []
    for lng_index in range(lng_steps):
        for lat_index in range(lat_steps):
            color_name = COLORS[rng.randrange(len(COLORS))]
            tiles.append(
                {
                    "lat": -90 + (lat_index + 0.5) * tile_height,
                    "lng": -180 + lng_index * tile_width,
                    "material": materials_by_color[color_name],
                }
            )

    return tiles, tile_width, tile_height


tiles_data, tile_width, tile_height = build_tiles()

tiles_globe = (
    dash_globe.DashGlobe(id="tiles-example-globe")
    .update_layout(height=420)
    .add_tiles(tiles_data)
    .update_tiles(
        tile_lat="lat",
        tile_lng="lng",
        tile_width=tile_width - TILE_MARGIN,
        tile_height=tile_height - TILE_MARGIN,
        tile_material="material",
    )
)"""

AIRLINE_ROUTES_EXAMPLE_CODE = """import dash_globe
from dash import Input, Output
from urllib.request import urlopen
import csv
import io


OPENFLIGHTS_AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
OPENFLIGHTS_ROUTES_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"


def load_openflights_portugal_data():
    with urlopen(OPENFLIGHTS_AIRPORTS_URL, timeout=10) as response:
        airports_rows = list(csv.reader(io.StringIO(response.read().decode("utf-8"))))
    with urlopen(OPENFLIGHTS_ROUTES_URL, timeout=10) as response:
        routes_rows = list(csv.reader(io.StringIO(response.read().decode("utf-8"))))

    airports = []
    for row in airports_rows:
        if len(row) < 8 or row[3] != "Portugal" or row[4] in ("", r"\\N"):
            continue
        airports.append(
            {
                "airportId": row[0],
                "name": row[1],
                "city": row[2],
                "country": row[3],
                "iata": row[4],
                "lat": float(row[6]),
                "lng": float(row[7]),
                "color": "orange",
                "label": f"{row[2]} ({row[4]})",
            }
        )

    airports_by_iata = {airport["iata"]: airport for airport in airports}
    routes = []
    for index, row in enumerate(routes_rows):
        if len(row) < 8 or row[2] in ("", r"\\N") or row[4] in ("", r"\\N") or row[7] != "0":
            continue
        src_airport = airports_by_iata.get(row[2])
        dst_airport = airports_by_iata.get(row[4])
        if not src_airport or not dst_airport:
            continue
        routes.append(
            {
                "routeId": f"{row[2].lower()}-{row[4].lower()}-{index}",
                "airline": row[0] or "Unknown airline",
                "srcIata": row[2],
                "dstIata": row[4],
                "srcAirport": src_airport,
                "dstAirport": dst_airport,
                "label": f"{row[0] or 'Unknown airline'}: {row[2]} -> {row[4]}",
                "startLat": src_airport["lat"],
                "startLng": src_airport["lng"],
                "endLat": dst_airport["lat"],
                "endLng": dst_airport["lng"],
            }
        )

    return airports, routes


def build_airline_route_styles(routes, hovered_route_id=None):
    base_opacity = 0.3
    highlight_opacity = 0.9
    hovered = hovered_route_id is not None
    return [
        {
            **route,
            "color": [
                f"rgba(0, 255, 0, {highlight_opacity if hovered and route['routeId'] == hovered_route_id else base_opacity / 4 if hovered else base_opacity:.3f})",
                f"rgba(255, 0, 0, {highlight_opacity if hovered and route['routeId'] == hovered_route_id else base_opacity / 4 if hovered else base_opacity:.3f})",
            ],
        }
        for route in routes
    ]


airports_data, routes_data = load_openflights_portugal_data()

airline_routes_globe = (
    dash_globe.DashGlobe(id="airline-routes-globe")
    .update_layout(height=420, background_color="#000000")
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
    .update_view(lat=37.6, lng=-16.6, altitude=0.42, transition_duration=0)
    .add_arcs(build_airline_route_styles(routes_data))
    .update_arcs(
        arc_label="label",
        arc_start_lat="startLat",
        arc_start_lng="startLng",
        arc_end_lat="endLat",
        arc_end_lng="endLng",
        arc_color="color",
        arc_dash_length=0.4,
        arc_dash_gap=0.2,
        arc_dash_animate_time=1500,
        arcs_transition_duration=0,
    )
    .add_points(airports_data)
    .update_points(
        point_lat="lat",
        point_lng="lng",
        point_color="color",
        point_label="label",
        point_altitude=0,
        point_radius=0.04,
        points_merge=True,
    )
)

@app.callback(
    Output("airline-routes-globe", "arcsData"),
    Input("airline-routes-globe", "hoverData"),
)
def highlight_airline_route(hover_data):
    hovered_route_id = (
        hover_data["data"]["routeId"]
        if hover_data and hover_data.get("layer") == "arc" and hover_data.get("data")
        else None
    )
    return build_airline_route_styles(routes_data, hovered_route_id)
"""

CHOROPLETH_COUNTRIES_EXAMPLE_CODE = """import json
from urllib.request import urlopen

import dash_globe
from dash import Input, Output


COUNTRIES_URL = (
    "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/"
    "ne_110m_admin_0_countries.geojson"
)


def load_countries():
    with urlopen(COUNTRIES_URL, timeout=5) as response:
        feature_collection = json.load(response)

    countries = []
    for feature in feature_collection["features"]:
        properties = feature["properties"]
        if properties["ISO_A2"] == "AQ":
            continue

        countries.append(
            {
                "countryId": properties["ISO_A2"],
                "name": properties["ADMIN"],
                "geometry": feature["geometry"],
                "metric": properties["GDP_MD_EST"] / max(1e5, properties["POP_EST"]),
                "labelHtml": (
                    f"<div><b>{properties['ADMIN']} ({properties['ISO_A2']}):</b></div>"
                    f"<div>GDP: <i>{properties['GDP_MD_EST']:,.0f}</i> M$</div>"
                    f"<div>Population: <i>{properties['POP_EST']:,.0f}</i></div>"
                ),
            }
        )

    return countries


countries = load_countries()
max_metric = max(country["metric"] for country in countries)


def style_countries():
    palette = ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#f03b20", "#bd0026"]

    def color_for(metric):
        ratio = metric / max_metric if max_metric else 0
        index = min(int(ratio * (len(palette) - 1)), len(palette) - 1)
        return palette[index]

    return [
        {
            **country,
            "altitude": 0.06,
            "capColor": color_for(country["metric"]),
            "sideColor": "rgba(0, 100, 0, 0.15)",
            "strokeColor": "#111",
        }
        for country in countries
    ]


choropleth_globe = (
    dash_globe.DashGlobe(id="choropleth-countries-globe")
    .update_layout(height=420, background_image_url="https://unpkg.com/three-globe@2.45.2/example/img/night-sky.png")
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
    .update_interaction(line_hover_precision=0)
    .add_polygons(style_countries())
    .update_polygons(
        polygon_geo_json_geometry="geometry",
        polygon_cap_color="capColor",
        polygon_side_color="sideColor",
        polygon_stroke_color="strokeColor",
        polygon_altitude="altitude",
        polygon_hover_key="countryId",
        polygon_hover_altitude=0.12,
        polygon_hover_cap_color="steelblue",
        polygon_label="labelHtml",
        polygons_transition_duration=300,
    )
)


@app.callback(
    Output("choropleth-countries-event", "children"),
    Input("choropleth-countries-globe", "hoverData"),
)
def highlight_country(hover_data):
    if hover_data is None:
        return "Hover a country to highlight it and inspect the latest hover payload."
    return json.dumps(hover_data, indent=2)
"""

HOLLOW_GLOBE_EXAMPLE_CODE = """import json
from urllib.request import urlopen

import dash_globe


COUNTRIES_URL = (
    "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/"
    "ne_110m_admin_0_countries.geojson"
)


def load_land_polygons():
    with urlopen(COUNTRIES_URL, timeout=5) as response:
        feature_collection = json.load(response)

    return [
        {
            "geometry": feature["geometry"],
            "name": feature["properties"]["ADMIN"],
        }
        for feature in feature_collection["features"]
        if feature["properties"]["ISO_A2"] != "AQ"
    ]


hollow_globe = (
    dash_globe.DashGlobe(id="hollow-globe")
    .update_layout(height=420, background_color="rgba(0, 0, 0, 0)")
    .update_globe(show_globe=False, show_atmosphere=False)
    .update_view(lat=18, lng=12, altitude=2.05, transition_duration=0)
    .update_interaction(enable_pointer_interaction=False)
    .add_polygons(load_land_polygons())
    .update_polygons(
        polygon_geo_json_geometry="geometry",
        polygon_cap_material=dash_globe.lambert_material(
            color="darkslategrey",
            side="double",
        ),
        polygon_side_color="rgba(0, 0, 0, 0)",
        polygon_stroke_color=False,
    )
)
"""

COUNTRIES_POPULATION_EXAMPLE_CODE = """import json
from urllib.request import urlopen

import dash_globe
from dash import Input, Output


COUNTRIES_URL = (
    "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/"
    "ne_110m_admin_0_countries.geojson"
)


def load_countries():
    with urlopen(COUNTRIES_URL, timeout=5) as response:
        feature_collection = json.load(response)

    countries = []
    for feature in feature_collection["features"]:
        properties = feature["properties"]
        if properties["ISO_A2"] == "AQ":
            continue

        population = float(properties["POP_EST"])
        countries.append(
            {
                "countryId": properties["ISO_A2"],
                "name": properties["ADMIN"],
                "geometry": feature["geometry"],
                "labelHtml": (
                    f"<b>{properties['ADMIN']} ({properties['ISO_A2']})</b> <br />"
                    f"Population: <i>{round(population / 1e4) / 1e2:,.2f}M</i>"
                ),
                "altitude": max(0.1, population ** 0.5 * 7e-5),
                "capColor": "rgba(200, 0, 0, 0.6)",
                "sideColor": "rgba(0, 100, 0, 0.05)",
            }
        )

    return countries


countries = load_countries()

population_globe = (
    dash_globe.DashGlobe(id="countries-population-globe")
    .update_layout(height=420, background_color="#000000")
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_DARK)
    .update_view(altitude=4, transition_duration=5000)
    .update_interaction(line_hover_precision=0)
    .add_polygons(countries)
    .update_polygons(
        polygon_geo_json_geometry="geometry",
        polygon_cap_color="capColor",
        polygon_side_color="sideColor",
        polygon_altitude="altitude",
        polygon_label="labelHtml",
        polygons_transition_duration=4000,
    )
)


@app.callback(
    Output("countries-population-event", "children"),
    Input("countries-population-globe", "hoverData"),
)
def describe_country_hover(hover_data):
    if hover_data is None:
        return "Hover a country to inspect the latest population-polygon payload."
    return json.dumps(hover_data, indent=2)
"""

SITUATION_ROOM_EXAMPLE_CODE = """import json
import math
from pathlib import Path
from random import Random

import dash_globe
from dash import Dash, Input, Output, dcc, html


app = Dash(__name__)


with (Path(__file__).resolve().parent / "public" / "news.json").open("r", encoding="utf-8") as news_file:
    news_payload = json.load(news_file)

initial_view = {"lat": 25, "lng": 12, "altitude": 2.15}
story_refresh_ms = 1200
auto_rotate_speed = 0.32
side_order = ("left", "right")


def resolve_location(story):
    location = dict(story.get("location") or {})
    location_name = (location.get("name") or "Unknown location").strip() or "Unknown location"
    if location_name.lower() != "global":
        return {
            "name": location_name,
            "lat": float(location.get("lat") or 0),
            "lng": float(location.get("lng") or 0),
        }

    rng = Random(f"situation-room-global:{story.get('id') or story.get('title')}")
    return {
        "name": "Global",
        "lat": round(rng.uniform(-58, 58), 4),
        "lng": round(rng.uniform(-180, 180), 4),
    }


def normalize_story(story):
    meta = dict(story.get("meta") or {})
    topics = [topic for topic in (meta.get("topics") or []) if topic]
    return {
        **story,
        "location": resolve_location(story),
        "meta": {
            **meta,
            "topic": (meta.get("topic") or (topics[0] if topics else "news")).lower(),
            "topics": topics,
        },
    }


news_payload["stories"] = [normalize_story(story) for story in news_payload.get("stories", [])]
news_payload["count"] = len(news_payload["stories"])


def forward_angle(story, current_view):
    start_lat = math.radians(story["location"]["lat"])
    start_lng = math.radians(story["location"]["lng"])
    view_lat = math.radians(current_view["lat"])
    view_lng = math.radians(current_view["lng"])
    cosine = (
        math.sin(start_lat) * math.sin(view_lat)
        + math.cos(start_lat) * math.cos(view_lat) * math.cos(start_lng - view_lng)
    )
    return math.acos(max(-1, min(cosine, 1)))


def story_side(story, current_view):
    relative_lng = ((story["location"]["lng"] - current_view["lng"] + 180) % 360) - 180
    return "right" if relative_lng >= 0 else "left"


def live_view(cycle_step):
    elapsed_seconds = (cycle_step or 0) * story_refresh_ms / 1000
    rotation_degrees = elapsed_seconds * auto_rotate_speed * 6
    return {
        **initial_view,
        "lng": ((initial_view["lng"] - rotation_degrees + 180) % 360) - 180,
    }


def build_story_panel(story):
    return html.Div(
        [
            html.Div([html.Span(story["meta"]["topic"].upper()), html.Span(story["meta"]["country"])]),
            html.Img(src=story["image"]),
            html.H4(html.A(story["title"], href=story["url"], target="_blank", rel="noreferrer")),
            html.P(story["description"]),
            html.Div([html.Span(story["source"]), html.Span(story["location"]["name"])]),
            html.Div(story["publishedAt"]),
        ],
        style={"width": "210px"},
    )


def build_story_overlay(story, side):
    return {
        "storyId": story["id"],
        "lat": story["location"]["lat"],
        "lng": story["location"]["lng"],
        "altitude": 0.015,
        "screenSide": side,
        "screenX": 0,
        "screenY": 84,
        "tether": True,
        "tetherColor": "rgba(103, 232, 249, 0.95)",
        "tetherWidth": 1.9,
        "tetherAttach": "right" if side == "left" else "left",
    }


def pick_active_snapshots(cycle_step, current_view=None):
    view = {
        **live_view(cycle_step),
        **(current_view or {}),
    }
    candidates = []

    for index, story in enumerate(news_payload["stories"]):
        angle = forward_angle(story, view)
        if angle > math.radians(96):
            continue

        relative_lng = ((story["location"]["lng"] - view["lng"] + 180) % 360) - 180
        candidates.append(
            {
                "index": index,
                "story": story,
                "forward_angle": angle,
                "relative_lng": relative_lng,
            }
        )

    selected = sorted(
        candidates,
        key=lambda item: (item["forward_angle"], abs(item["relative_lng"]), item["index"]),
    )[:2]
    selected.sort(key=lambda item: (item["relative_lng"], item["forward_angle"], item["index"]))

    if len(selected) == 1:
        assigned_sides = ["right" if selected[0]["relative_lng"] >= 0 else "left"]
    else:
        assigned_sides = list(side_order)

    return [
        {
            "side": side,
            "overlay": build_story_overlay(item["story"], side),
            "ring": {"lat": item["story"]["location"]["lat"], "lng": item["story"]["location"]["lng"], "maxR": 5, "propagationSpeed": 2.1, "repeatPeriod": 1600},
            "card": build_story_panel(item["story"]),
        }
        for item, side in zip(selected, assigned_sides)
    ]


snapshots = pick_active_snapshots(cycle_step=0)

situation_room_globe = html.Div(
    [
        dash_globe.DashGlobe(id="situation-room-globe")
        .update_layout(height=420, background_image_url=dash_globe.PRESETS.NIGHT_SKY)
        .update_globe(
            globe_image_url=dash_globe.PRESETS.EARTH_DARK,
            bump_image_url=dash_globe.PRESETS.EARTH_TOPOGRAPHY,
            show_graticules=True,
            atmosphere_color="#22d3ee",
            atmosphere_altitude=0.16,
        )
        .update_view(**initial_view, transition_duration=0)
        .update_controls(auto_rotate=True, auto_rotate_speed=auto_rotate_speed)
        .update_interaction(enable_pointer_interaction=False)
        .add_points(
            [
                {"lat": story["location"]["lat"], "lng": story["location"]["lng"], "radius": 0.2, "altitude": 0.015, "color": "rgba(103, 232, 249, 0.75)"}
                for story in news_payload["stories"]
            ]
        )
        .update_points(point_lat="lat", point_lng="lng", point_altitude="altitude", point_color="color", point_radius="radius")
        .add_rings([snapshot["ring"] for snapshot in snapshots])
        .update_rings(
            ring_lat="lat",
            ring_lng="lng",
            ring_color=dash_globe.ring_color_interpolator("#67e8f9"),
            ring_max_radius="maxR",
            ring_propagation_speed="propagationSpeed",
            ring_repeat_period="repeatPeriod",
        )
        .update_html_elements(
            [snapshot["overlay"] for snapshot in snapshots],
            children=[snapshot["card"] for snapshot in snapshots],
            html_element_lat="lat",
            html_element_lng="lng",
            html_element_altitude="altitude",
            html_element_key="storyId",
            html_element_screen_side="screenSide",
            html_element_screen_x="screenX",
            html_element_screen_y="screenY",
            html_element_tether="tether",
            html_element_tether_color="tetherColor",
            html_element_tether_width="tetherWidth",
            html_element_tether_attach="tetherAttach",
        ),
    ]
)


@app.callback(
    Output("situation-room-globe", "ringsData"),
    Output("situation-room-globe", "htmlElementsData"),
    Output("situation-room-globe", "children"),
    Input("situation-room-globe", "currentView"),
)
def sync_situation_room(current_view):
    snapshots = pick_active_snapshots(cycle_step=0, current_view=current_view)
    return (
        [snapshot["ring"] for snapshot in snapshots],
        [snapshot["overlay"] for snapshot in snapshots],
        [snapshot["card"] for snapshot in snapshots],
    )
"""

QUICK_START_CODE = """from dash import Dash, html
import dash_globe


cities = [
    {"name": "Tokyo", "lat": 35.6764, "lng": 139.65, "color": "#4cc9f0", "size": 0.24},
    {"name": "Sydney", "lat": -33.8688, "lng": 151.2093, "color": "#f72585", "size": 0.18},
]

globe = (
    dash_globe.DashGlobe(id="quick-start")
    .update_layout(height=460, background_color="#020817")
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_NIGHT,
        show_graticules=True,
        atmosphere_color="#5bc0eb",
    )
    .update_view(lat=20, lng=120, altitude=1.7, transition_duration=0)
    .add_points(cities)
    .update_points(
        point_lat="lat",
        point_lng="lng",
        point_color="color",
        point_altitude="size",
        point_radius=0.32,
        point_label="name",
    )
)

app = Dash(__name__)
app.layout = html.Div(globe)

if __name__ == "__main__":
    app.run(debug=True)
"""

BUILDER_PATTERN_CODE = """globe = (
    dash_globe.DashGlobe(id="builder-pattern")
    .update_layout(...)
    .update_globe(...)
    .update_view(...)
    .update_interaction(...)
    .update_controls(...)
    .add_points(data)
    .update_points(...)
    .add_arcs(data)
    .update_arcs(...)
)

# Every helper returns the same DashGlobe instance so you can keep chaining.
# Any raw prop is still available through the component constructor or update(...).
"""

ADVANCED_FEATURES_CODE = """globe = (
    dash_globe.DashGlobe(id="advanced")
    .update_layout(background_image_url=dash_globe.PRESETS.NIGHT_SKY)
    .update_day_night_cycle(
        day_image_url=dash_globe.PRESETS.EARTH_DAY,
        night_image_url=dash_globe.PRESETS.EARTH_NIGHT,
        time="2026-04-17T12:00:00Z",
        minutes_per_second=60,
    )
    .update_clouds(image_url=dash_globe.PRESETS.CLOUDS, opacity=0.35)
    .add_heatmap(weighted_points)
    .add_heatmaps(seasonal_dataset, anomaly_dataset)
    .add_hex_polygons(country_features)
    .update_hex_polygons(
        hex_polygon_geo_json_geometry="geometry",
        hex_polygon_color="color",
        hex_polygon_altitude="altitude",
    )
    .add_particle_sets(wind_particles)
    .update_particles(
        particles_list="particles",
        particle_lat="lat",
        particle_lng="lng",
        particles_color="color",
        particles_size=3,
    )
)

globe.clear_tile_cache()
globe.update(show_pointer_cursor=True, clear_globe_tile_cache_key=1)
"""

CALLBACKS_EXAMPLE_CODE = """from dash import Input, Output, State, callback
import dash_globe


@callback(
    Output("event-log", "children"),
    Output("emit-demo", "arcsData"),
    Input("emit-demo", "clickData"),
    State("emit-demo", "arcsData"),
)
def handle_globe_click(click_data, existing_arcs):
    coords = dash_globe.event_coords(click_data)
    if coords is None:
        return "Click the globe to emit an arc.", existing_arcs or []

    next_arc = {
        "startLat": coords["lat"],
        "startLng": coords["lng"],
        "endLat": 51.5072,
        "endLng": -0.1276,
        "color": ["#4cc9f0", "#ffd166"],
    }
    return click_data, [*(existing_arcs or []), next_arc]
"""

METHOD_REFERENCE = [
    {
        "group": "Scene and layout",
        "methods": [
            "update_layout",
            "update_globe",
            "update_view",
            "update_interaction",
            "update_controls",
        ],
        "summary": "Canvas sizing, background, globe textures, camera target, pointer behavior, and auto-rotation.",
    },
    {
        "group": "Globe effects",
        "methods": [
            "update_day_night_cycle",
            "update_clouds",
            "clear_tile_cache",
            "update",
        ],
        "summary": "Enable the day/night shader, add a rotating cloud shell, refresh globe tiles, or fall back to any raw prop.",
    },
    {
        "group": "Layer builders",
        "methods": [
            "add_points / update_points",
            "add_arcs / update_arcs",
            "add_polygons / update_polygons",
            "add_paths / update_paths",
            "add_heatmap / update_heatmap",
            "add_heatmaps / update_heatmaps",
            "add_hex_bins / update_hex_bins",
            "add_hex_polygons / update_hex_polygons",
            "add_tiles / update_tiles",
            "add_particle_sets / update_particles",
            "add_rings / update_rings",
            "add_labels / update_labels",
        ],
        "summary": "Append data incrementally, or replace the full layer and its accessors in one update call.",
    },
]

LAYER_REFERENCE_ROWS = [
    ("Points", "add_points / update_points", "point_lat, point_lng, point_color, point_altitude, point_radius", "Upstream Basic Example"),
    ("Arcs", "add_arcs / update_arcs", "arc_start_lat, arc_end_lat, arc_color, arc_dash_length, arc_dash_animate_time", "Random Arcs, Emit Arcs, Airline Routes"),
    ("Polygons", "add_polygons / update_polygons", "polygon_geo_json_geometry, polygon_cap_color, polygon_altitude, polygon_hover_*", "Countries Population, Choropleth, Hollow Globe"),
    ("Paths", "add_paths / update_paths", "path_points, path_point_lat, path_point_lng, path_color, path_dash_animate_time", "Submarine Cables"),
    ("Heatmaps", "add_heatmap / add_heatmaps / update_heatmap / update_heatmaps", "heatmap_point_lat, heatmap_point_lng, heatmap_point_weight, heatmap_top_altitude", "Upstream Heatmap"),
    ("Hex bins", "add_hex_bins / update_hex_bins", "hex_bin_point_lat, hex_bin_point_lng, hex_bin_point_weight, hex_top_color", "Documented below"),
    ("Hex polygons", "add_hex_polygons / update_hex_polygons", "hex_polygon_geo_json_geometry, hex_polygon_color, hex_polygon_altitude", "Documented below"),
    ("Tiles", "add_tiles / update_tiles", "tile_lat, tile_lng, tile_width, tile_height, tile_material", "Upstream Tiles"),
    ("Particles", "add_particle_sets / update_particles", "particles_list, particle_lat, particle_lng, particles_color, particles_size", "Documented below"),
    ("Rings", "add_rings / update_rings", "ring_lat, ring_lng, ring_color, ring_max_radius, ring_repeat_period", "Random Rings, Emit Arcs"),
    ("Labels", "add_labels / update_labels", "label_lat, label_lng, label_text, label_size, label_include_dot", "World Cities"),
]

UTILITY_REFERENCE_ROWS = [
    ("PRESETS", "Common earth, night-sky, topography, water, and cloud image URLs for quick starts and upstream parity demos."),
    ("event_coords", "Extract a clean {lat, lng, altitude?} dictionary from click payloads before building callback state."),
    ("ring_color_interpolator", "Create a serialisable color fade for ripple rings without shipping a JavaScript callback."),
    ("material_spec", "Build JSON material dictionaries for polygon caps/sides and tiles using basic, lambert, phong, or standard."),
    ("lambert_material", "Short-hand for the most common material-backed examples, including double-sided hollow globe caps."),
]

EVENT_REFERENCE_ROWS = [
    ("clickData", "Last click payload emitted by the globe surface or any interactive layer."),
    ("hoverData", "Last hover payload. Used in the airline-route, choropleth, countries-population, and submarine-cable demos."),
    ("rightClickData", "Right-click interaction payload when you need alternate selection behavior."),
    ("currentView", "Live camera report with the current latitude, longitude, and altitude."),
    ("globeReady", "Boolean flag that tells you when the scene has fully mounted."),
    ("lastInteraction", "Most recent interaction payload regardless of interaction type."),
]

INSTALLATION_CODE = """pip install dash-globe"""

DOC_SECTIONS = [
    ("getting-started", "Usage"),
    ("api-overview", "Overview"),
    ("helper-guides", "Helper Guides"),
    ("layer-reference", "Layer Reference"),
    ("utilities", "Utilities"),
    ("callbacks", "Callbacks"),
    ("api-reference", "API Reference"),
    ("examples", "Live Examples"),
]

API_REFERENCE_ITEMS = [
    {
        "name": "dash_globe.DashGlobe",
        "signature": "dash_globe.DashGlobe(id=None, className=None, style=None, ..., lastInteraction=None)",
        "summary": "Base Dash component wrapping react-globe.gl. Use it directly when you want the full generated prop surface, or use the higher-level helper methods on dash_globe.globe.DashGlobe.",
        "parameters": [
            ("id", "str | dict, optional", "Dash component identifier used in callbacks."),
            ("className / style", "str / dict, optional", "Root-level CSS class or inline styles."),
            ("responsive / width / height", "bool / number, optional", "Canvas sizing behavior."),
            ("pointsData / arcsData / ... / labelsData", "sequence, optional", "Layer datasets passed directly to the underlying component."),
            ("clickData / hoverData / rightClickData / currentView / globeReady / lastInteraction", "dict | bool, optional", "Read-only interaction and lifecycle props emitted by the component."),
        ],
        "returns": "DashGlobe",
        "notes": [
            "The helper subclass keeps the same prop surface, so constructor kwargs always remain available.",
            "Use update(...) when you want to set raw props after construction.",
        ],
    },
    {
        "name": "DashGlobe.update_layout",
        "signature": "DashGlobe.update_layout(*, width=None, height=None, responsive=None, background_color=None, background_image_url=None, globe_offset=None, wait_for_globe_ready=None, animate_in=None, renderer_config=None, style=None, class_name=None) -> DashGlobe",
        "summary": "Configure top-level canvas layout and render behavior.",
        "parameters": [
            ("width / height", "float, optional", "Explicit canvas size in pixels."),
            ("responsive", "bool, optional", "Use ResizeObserver-based automatic sizing."),
            ("background_color / background_image_url", "str, optional", "Background fill or image behind the globe."),
            ("globe_offset", "tuple[float, float] | list[float], optional", "Shift the globe relative to the canvas center."),
            ("wait_for_globe_ready / animate_in", "bool, optional", "Initial render behavior."),
            ("renderer_config", "mapping, optional", "Low-level renderer configuration passed through to the component."),
            ("style / class_name", "mapping / str, optional", "Root element styling hooks."),
        ],
        "returns": "DashGlobe",
        "notes": ["Returns the same instance for chaining."],
    },
    {
        "name": "DashGlobe.update_globe",
        "signature": "DashGlobe.update_globe(*, globe_image_url=None, bump_image_url=None, show_globe=None, show_graticules=None, show_atmosphere=None, atmosphere_color=None, atmosphere_altitude=None, curvature_resolution=None) -> DashGlobe",
        "summary": "Configure the earth surface, atmosphere, and baseline globe rendering.",
        "parameters": [
            ("globe_image_url / bump_image_url", "str, optional", "Surface and bump textures."),
            ("show_globe / show_graticules / show_atmosphere", "bool, optional", "Toggle core globe layers."),
            ("atmosphere_color / atmosphere_altitude", "str / float, optional", "Atmosphere appearance."),
            ("curvature_resolution", "float, optional", "Globe curvature tessellation."),
        ],
        "returns": "DashGlobe",
        "notes": ["Common presets are available on dash_globe.PRESETS."],
    },
    {
        "name": "DashGlobe.update_view",
        "signature": "DashGlobe.update_view(*, lat=None, lng=None, altitude=None, transition_duration=None) -> DashGlobe",
        "summary": "Set the camera target in geographic coordinates.",
        "parameters": [
            ("lat / lng / altitude", "float, optional", "Target camera position."),
            ("transition_duration", "float, optional", "Camera transition time in milliseconds."),
        ],
        "returns": "DashGlobe",
        "notes": ["Writes to cameraPosition and cameraTransitionDuration under the hood."],
    },
    {
        "name": "DashGlobe.update_interaction / update_controls",
        "signature": "DashGlobe.update_interaction(*, enable_pointer_interaction=None, show_pointer_cursor=None, line_hover_precision=None, animation_paused=None) -> DashGlobe\nDashGlobe.update_controls(*, auto_rotate=None, auto_rotate_speed=None) -> DashGlobe",
        "summary": "Tune pointer behavior, hover precision, animation pausing, and orbit-style auto-rotation.",
        "parameters": [
            ("enable_pointer_interaction / show_pointer_cursor", "bool, optional", "Interaction toggles."),
            ("line_hover_precision", "float, optional", "Hover hit testing precision for linear layers."),
            ("animation_paused", "bool, optional", "Pause active scene animations."),
            ("auto_rotate / auto_rotate_speed", "bool / float, optional", "Camera auto-rotation."),
        ],
        "returns": "DashGlobe",
        "notes": [],
    },
    {
        "name": "DashGlobe.update_day_night_cycle / update_clouds",
        "signature": "DashGlobe.update_day_night_cycle(*, enabled=True, day_image_url=None, night_image_url=None, time=None, animate=None, minutes_per_second=None) -> DashGlobe\nDashGlobe.update_clouds(*, enabled=True, image_url=None, altitude=None, rotation_speed=None, opacity=None) -> DashGlobe",
        "summary": "Enable first-class upstream effects exposed as Python helpers instead of raw Three.js configuration.",
        "parameters": [
            ("day_image_url / night_image_url", "str, optional", "Textures used by the day-night shader."),
            ("time / animate / minutes_per_second", "Any / bool / float, optional", "Controls the day-night cycle clock."),
            ("image_url / altitude / rotation_speed / opacity", "str / float, optional", "Cloud shell appearance and motion."),
        ],
        "returns": "DashGlobe",
        "notes": ["These helpers map to the component's dayNightCycle* and clouds* props."],
    },
    {
        "name": "DashGlobe.add_* / update_* layer helpers",
        "signature": "DashGlobe.add_points(*points) -> DashGlobe\nDashGlobe.update_points(data=None, **props) -> DashGlobe\n... equivalent helper pairs exist for arcs, polygons, paths, heatmaps, hex bins, hex polygons, tiles, particles, rings, and labels.",
        "summary": "Append data incrementally or replace a full layer while assigning data accessors in snake_case or camelCase.",
        "parameters": [
            ("data", "iterable, optional", "Replacement dataset for the target layer."),
            ("**props", "mapping", "Layer accessors and layer-specific settings such as point_lat, arc_color, or polygon_geo_json_geometry."),
        ],
        "returns": "DashGlobe",
        "notes": [
            "Helper aliases accept snake_case and are normalized to generated Dash prop names.",
            "add_heatmap() is a convenience for the single-dataset case; add_heatmaps() handles multiple datasets.",
        ],
    },
]

HELPER_GUIDE_ITEMS = [
    {
        "title": "update_layout",
        "description": "Use update_layout when you want to size the globe, control responsiveness, or define the presentation surface around the canvas.",
        "related": ["width", "height", "responsive", "background_color", "background_image_url", "style", "class_name"],
        "code": """globe = (
    dash_globe.DashGlobe(id="layout-demo")
    .update_layout(
        height=460,
        background_color="#020817",
        background_image_url=dash_globe.PRESETS.NIGHT_SKY,
        responsive=True,
    )
)""",
    },
    {
        "title": "update_globe and update_view",
        "description": "These helpers define what the globe looks like and where the camera is positioned. They are usually the first scene helpers you call after update_layout.",
        "related": ["globe_image_url", "bump_image_url", "show_graticules", "show_atmosphere", "atmosphere_color", "lat", "lng", "altitude"],
        "code": """globe = (
    dash_globe.DashGlobe(id="scene-demo")
    .update_globe(
        globe_image_url=dash_globe.PRESETS.EARTH_NIGHT,
        show_graticules=True,
        atmosphere_color="#5bc0eb",
    )
    .update_view(lat=22, lng=12, altitude=1.8, transition_duration=0)
)""",
    },
    {
        "title": "update_day_night_cycle and update_clouds",
        "description": "Dash Globe exposes the upstream globe effects as first-class Python helpers so you can keep advanced scene effects declarative and serialisable.",
        "related": ["day_image_url", "night_image_url", "time", "minutes_per_second", "image_url", "rotation_speed", "opacity"],
        "code": """globe = (
    dash_globe.DashGlobe(id="effects-demo")
    .update_day_night_cycle(
        day_image_url=dash_globe.PRESETS.EARTH_DAY,
        night_image_url=dash_globe.PRESETS.EARTH_NIGHT,
        time="2026-04-17T12:00:00Z",
    )
    .update_clouds(
        image_url=dash_globe.PRESETS.CLOUDS,
        opacity=0.35,
        rotation_speed=-0.006,
    )
)""",
    },
    {
        "title": "add_points and update_points",
        "description": "Points are a good default for markers, hubs, or simple presence indicators. Add records first, then tell the layer where latitude, longitude, and styling fields live.",
        "related": ["point_lat", "point_lng", "point_color", "point_altitude", "point_radius", "point_label"],
        "code": """cities = [
    {"name": "Tokyo", "lat": 35.6764, "lng": 139.65, "color": "#4cc9f0"},
    {"name": "Sydney", "lat": -33.8688, "lng": 151.2093, "color": "#f72585"},
]

globe = (
    dash_globe.DashGlobe(id="points-demo")
    .add_points(cities)
    .update_points(
        point_lat="lat",
        point_lng="lng",
        point_color="color",
        point_radius=0.3,
        point_label="name",
    )
)""",
    },
    {
        "title": "add_arcs and update_arcs",
        "description": "Arcs are ideal for flows, routes, and click-driven emissions. You can keep them static or add dash timing for motion.",
        "related": ["arc_start_lat", "arc_start_lng", "arc_end_lat", "arc_end_lng", "arc_color", "arc_dash_length", "arc_dash_animate_time"],
        "code": """routes = [
    {
        "startLat": 40.7128,
        "startLng": -74.0060,
        "endLat": 51.5072,
        "endLng": -0.1276,
        "color": ["#ff6b6b", "#ffd166"],
    }
]

globe = (
    dash_globe.DashGlobe(id="arcs-demo")
    .add_arcs(routes)
    .update_arcs(
        arc_start_lat="startLat",
        arc_start_lng="startLng",
        arc_end_lat="endLat",
        arc_end_lng="endLng",
        arc_color="color",
        arc_dash_length=0.4,
        arc_dash_animate_time=1800,
    )
)""",
    },
    {
        "title": "add_polygons and update_polygons",
        "description": "Polygons power choropleths, extrusions, geographic highlighting, and material-backed landmass effects.",
        "related": ["polygon_geo_json_geometry", "polygon_cap_color", "polygon_side_color", "polygon_altitude", "polygon_label", "polygon_hover_*"],
        "code": """regions = [
    {
        "name": "Region A",
        "geometry": {"type": "Polygon", "coordinates": [[[-10, 30], [10, 30], [10, 50], [-10, 50], [-10, 30]]]},
        "color": "#4cc9f0",
        "altitude": 0.08,
    }
]

globe = (
    dash_globe.DashGlobe(id="polygons-demo")
    .add_polygons(regions)
    .update_polygons(
        polygon_geo_json_geometry="geometry",
        polygon_cap_color="color",
        polygon_altitude="altitude",
        polygon_label="name",
    )
)""",
    },
    {
        "title": "add_paths and update_paths",
        "description": "Paths handle ordered coordinate sequences like cables, tracks, and geographic corridors.",
        "related": ["path_points", "path_point_lat", "path_point_lng", "path_color", "path_dash_length", "path_dash_animate_time"],
        "code": """paths = [
    {
        "name": "Cable segment",
        "coords": [{"lat": 38.72, "lng": -9.14}, {"lat": 40.64, "lng": -8.65}],
        "color": "#4cc9f0",
    }
]

globe = (
    dash_globe.DashGlobe(id="paths-demo")
    .add_paths(paths)
    .update_paths(
        path_points="coords",
        path_point_lat="lat",
        path_point_lng="lng",
        path_color="color",
        path_label="name",
    )
)""",
    },
    {
        "title": "add_heatmap and update_heatmaps",
        "description": "Use heatmaps for weighted density surfaces. add_heatmap is the ergonomic single-dataset shortcut, while add_heatmaps supports multiple datasets.",
        "related": ["heatmap_point_lat", "heatmap_point_lng", "heatmap_point_weight", "heatmap_top_altitude", "heatmaps_transition_duration"],
        "code": """weighted_points = [
    {"lat": 40.7128, "lng": -74.0060, "weight": 0.9},
    {"lat": 51.5072, "lng": -0.1276, "weight": 0.7},
]

globe = (
    dash_globe.DashGlobe(id="heatmap-demo")
    .add_heatmap(weighted_points)
    .update_heatmaps(
        heatmap_point_lat="lat",
        heatmap_point_lng="lng",
        heatmap_point_weight="weight",
        heatmap_top_altitude=0.6,
    )
)""",
    },
    {
        "title": "add_labels and update_labels",
        "description": "Labels are useful for city names, annotations, and named regions. They pair especially well with points or polygons when you want a readable layer on top.",
        "related": ["label_lat", "label_lng", "label_text", "label_color", "label_size", "label_include_dot", "label_dot_radius"],
        "code": """labels = [
    {"name": "Lisbon", "lat": 38.7223, "lng": -9.1393, "color": "#ffd166", "size": 0.9}
]

globe = (
    dash_globe.DashGlobe(id="labels-demo")
    .add_labels(labels)
    .update_labels(
        label_lat="lat",
        label_lng="lng",
        label_text="name",
        label_color="color",
        label_size="size",
        label_include_dot=True,
    )
)""",
    },
]

RAW_PROP_GROUPS = [
    {
        "title": "Layout and rendering",
        "description": "Canvas sizing, background treatment, render lifecycle, and low-level renderer settings.",
        "props": [
            "responsive",
            "width",
            "height",
            "backgroundColor",
            "backgroundImageUrl",
            "globeOffset",
            "animateIn",
            "waitForGlobeReady",
            "rendererConfig",
            "clearGlobeTileCacheKey",
        ],
    },
    {
        "title": "Globe surface and camera",
        "description": "Core globe textures and the camera target reported back to Dash.",
        "props": [
            "globeImageUrl",
            "bumpImageUrl",
            "showGlobe",
            "showGraticules",
            "showAtmosphere",
            "atmosphereColor",
            "atmosphereAltitude",
            "globeCurvatureResolution",
            "cameraPosition",
            "cameraTransitionDuration",
        ],
    },
    {
        "title": "Motion and built-in effects",
        "description": "Rotation, time-of-day shading, clouds, and animation controls.",
        "props": [
            "autoRotate",
            "autoRotateSpeed",
            "dayNightCycle*",
            "clouds*",
            "animationPaused",
        ],
    },
    {
        "title": "Interaction and status",
        "description": "Pointer settings plus the event props you can wire directly into callbacks.",
        "props": [
            "enablePointerInteraction",
            "showPointerCursor",
            "lineHoverPrecision",
            "clickData",
            "hoverData",
            "rightClickData",
            "currentView",
            "globeReady",
            "lastInteraction",
        ],
    },
    {
        "title": "Points, arcs, polygons, and paths",
        "description": "Geographic primitives for markers, flights, regions, and multi-point paths.",
        "props": [
            "pointsData",
            "point*",
            "arcsData",
            "arc*",
            "polygonsData",
            "polygon*",
            "pathsData",
            "path*",
        ],
    },
    {
        "title": "Heatmaps, hex layers, and tiles",
        "description": "Density and gridded representations for weighted points, polygon binning, and material-backed tiles.",
        "props": [
            "heatmapsData",
            "heatmap*",
            "hexBinPointsData",
            "hex*",
            "hexPolygonsData",
            "hexPolygon*",
            "tilesData",
            "tile*",
        ],
    },
    {
        "title": "Particles, rings, and labels",
        "description": "Animated particle sets, ripple overlays, and text annotations.",
        "props": [
            "particlesData",
            "particle*",
            "particles*",
            "ringsData",
            "ring*",
            "labelsData",
            "label*",
        ],
    },
]

SECTION_TITLE_STYLE = {"margin": "0 0 8px 0", "fontSize": "1.8rem", "color": "#182433"}
SECTION_BODY_STYLE = {"margin": 0, "maxWidth": "840px", "color": "#5f6b7a", "lineHeight": 1.7}
PANEL_STYLE = {
    "background": "#ffffff",
    "border": "1px solid #e4e9f0",
    "borderRadius": "16px",
    "padding": "20px",
    "boxShadow": "0 1px 2px rgba(16, 24, 40, 0.04)",
}


def globe_card(title, description, globe, footer):
    return html.Section(
        [
            html.Div(
                [
                    html.Span(
                        "Interactive Example",
                        style={
                            "display": "inline-block",
                            "marginBottom": "10px",
                            "padding": "4px 10px",
                            "borderRadius": "999px",
                            "background": "#eef4ff",
                            "color": "#3559b7",
                            "fontSize": "0.78rem",
                            "fontWeight": 700,
                            "letterSpacing": "0.04em",
                            "textTransform": "uppercase",
                        },
                    ),
                    html.H3(title, style={"margin": "0 0 8px 0", "color": "#182433"}),
                    html.P(description, style={"margin": 0, "color": "#5f6b7a", "lineHeight": 1.7}),
                ],
                style={"marginBottom": "18px"},
            ),
            html.Div(
                [
                    html.Div(globe, style={"minWidth": 0}),
                    html.Div(footer, style={"minWidth": 0}),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "18px",
                    "alignItems": "start",
                },
            ),
        ],
        style=PANEL_STYLE,
    )


def doc_card(title, description, *children):
    return html.Section(
        [
            html.H3(title, style={"margin": "0 0 8px 0", "color": "#182433"}),
            html.P(description, style={"margin": "0 0 14px 0", "color": "#5f6b7a", "lineHeight": 1.7}),
            *children,
        ],
        style=PANEL_STYLE,
    )


def build_badge_row(items):
    return html.Div(
        [
            html.Span(
                item,
                style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "padding": "6px 12px",
                    "borderRadius": "999px",
                    "background": "#f4f7fb",
                    "border": "1px solid #d9e3f0",
                    "fontSize": "0.88rem",
                    "color": "#41556b",
                },
            )
            for item in items
        ],
        style={"display": "flex", "flexWrap": "wrap", "gap": "8px", "marginTop": "14px"},
    )


def build_reference_table(headers, rows):
    return html.Div(
        html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th(
                                header,
                                style={
                                    "textAlign": "left",
                                    "padding": "10px 12px",
                                    "fontSize": "0.82rem",
                                    "letterSpacing": "0.08em",
                                    "textTransform": "uppercase",
                                    "color": "#738295",
                                    "borderBottom": "1px solid #e4e9f0",
                                },
                            )
                            for header in headers
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(
                                    cell,
                                    style={
                                        "padding": "12px",
                                        "verticalAlign": "top",
                                        "borderBottom": "1px solid #edf1f6",
                                        "lineHeight": 1.5,
                                        "color": "#37485b",
                                        "fontSize": "0.92rem",
                                    },
                                )
                                for cell in row
                            ]
                        )
                        for row in rows
                    ]
                ),
            ],
            style={"width": "100%", "borderCollapse": "collapse"},
        ),
        style={"overflowX": "auto"},
    )


def build_method_reference():
    return html.Div(
        [
            html.Div(
                [
                    html.H4(item["group"], style={"margin": "0 0 6px 0", "fontSize": "1rem"}),
                    html.P(item["summary"], style={"margin": "0 0 10px 0", "color": "#a9b8c7", "lineHeight": 1.6}),
                    html.Div(
                        [html.Code(method, style={"fontSize": "0.88rem"}) for method in item["methods"]],
                        style={"display": "flex", "flexWrap": "wrap", "gap": "8px"},
                    ),
                ],
                style={
                    "padding": "14px",
                    "borderRadius": "14px",
                    "background": "#f8fafc",
                    "border": "1px solid #e8edf3",
                },
            )
            for item in METHOD_REFERENCE
        ],
        style={"display": "grid", "gap": "12px"},
    )


def build_prop_group_reference():
    return html.Div(
        [
            html.Div(
                [
                    html.H4(item["title"], style={"margin": "0 0 6px 0", "color": "#182433"}),
                    html.P(item["description"], style={"margin": "0 0 12px 0", "color": "#5f6b7a", "lineHeight": 1.6}),
                    build_badge_row(item["props"]),
                ],
                style={
                    "padding": "16px",
                    "borderRadius": "14px",
                    "border": "1px solid #e8edf3",
                    "background": "#f8fafc",
                },
            )
            for item in RAW_PROP_GROUPS
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "14px"},
    )


def build_parameter_table(parameters):
    return build_reference_table(
        ["Parameter", "Type", "Description"],
        parameters,
    )


def build_note_list(items):
    return html.Ul(
        [html.Li(item, style={"marginBottom": "6px"}) for item in items],
        style={"margin": "12px 0 0 18px", "color": "#5f6b7a", "lineHeight": 1.7},
    )


def build_api_reference_item(item):
    children = [
        html.Div(item["name"], style={"fontWeight": 700, "fontSize": "1rem", "color": "#182433", "marginBottom": "10px"}),
        html.Pre(item["signature"], style=CODE_BLOCK_STYLE),
        html.P(item["summary"], style={"margin": "14px 0 0 0", "color": "#5f6b7a", "lineHeight": 1.7}),
        html.Div(style={"height": "14px"}),
        build_parameter_table(item["parameters"]),
        html.Div(
            [
                html.Div("Returns", style={"fontWeight": 700, "color": "#182433", "margin": "14px 0 6px 0"}),
                html.P(item["returns"], style={"margin": 0, "color": "#5f6b7a", "lineHeight": 1.7}),
            ]
        ),
    ]
    if item["notes"]:
        children.append(
            html.Div(
                [
                    html.Div("Notes", style={"fontWeight": 700, "color": "#182433", "margin": "14px 0 6px 0"}),
                    build_note_list(item["notes"]),
                ]
            )
        )

    return html.Div(
        children,
        style={**PANEL_STYLE, "padding": "18px"},
    )


def build_api_reference_list():
    return html.Div(
        [build_api_reference_item(item) for item in API_REFERENCE_ITEMS],
        style={"display": "grid", "gap": "18px"},
    )


def build_helper_guide_item(item):
    return doc_card(
        item["title"],
        item["description"],
        build_badge_row(item["related"]),
        html.Pre(item["code"], style={**CODE_BLOCK_STYLE, "marginTop": "14px"}),
    )


def build_helper_guides_grid():
    return html.Div(
        [build_helper_guide_item(item) for item in HELPER_GUIDE_ITEMS],
        style={"display": "grid", "gap": "18px"},
    )


def build_section_nav():
    return html.Nav(
        [
            html.Div(
                [
                    html.Div("Documentation", style={"fontSize": "0.78rem", "fontWeight": 700, "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#738295"}),
                    html.H2("On This Page", style={"margin": "8px 0 6px 0", "fontSize": "1.05rem", "color": "#182433"}),
                    html.P(
                        "A docs-first guide to the package API, helpers, and runnable examples.",
                        style={"margin": 0, "color": "#5f6b7a", "lineHeight": 1.6, "fontSize": "0.92rem"},
                    ),
                ],
                style={"marginBottom": "18px"},
            ),
            html.Div(
                [
                    html.A(
                        label,
                        href=f"#{section_id}",
                        style={
                            "display": "block",
                            "padding": "9px 12px",
                            "borderRadius": "10px",
                            "color": "#41556b",
                            "textDecoration": "none",
                            "fontWeight": 500,
                        },
                    )
                    for section_id, label in DOC_SECTIONS
                ],
                style={"display": "grid", "gap": "4px"},
            ),
        ],
        style={
            **PANEL_STYLE,
            "position": "sticky",
            "top": "24px",
            "width": "240px",
            "flex": "0 0 240px",
            "padding": "18px",
        },
    )


def build_doc_section(section_id, title, description, *children):
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        title.upper(),
                        style={
                            "fontSize": "0.76rem",
                            "fontWeight": 700,
                            "letterSpacing": "0.08em",
                            "textTransform": "uppercase",
                            "color": "#738295",
                            "marginBottom": "10px",
                        },
                    ),
                    html.H2(title, style=SECTION_TITLE_STYLE),
                    html.P(description, style=SECTION_BODY_STYLE),
                ],
                style={"marginBottom": "18px"},
            ),
            *children,
        ],
        id=section_id,
        style={"marginBottom": "36px", "scrollMarginTop": "24px"},
    )


def build_getting_started_section():
    return build_doc_section(
        "getting-started",
        "Getting Started",
        "Dash Globe is a Dash wrapper around react-globe.gl. The intended workflow mirrors figure-building in Plotly: create a component, configure the scene, add data layers, then map your data fields with layer accessors.",
        html.Div(
            [
                doc_card(
                    "Installation",
                    "Install the package, import dash_globe, and start with the chainable DashGlobe helper.",
                    html.Pre(INSTALLATION_CODE, style=CODE_BLOCK_STYLE),
                ),
                doc_card(
                    "Basic Usage",
                    "A minimal app only needs a Dash layout and a single globe configured with points, textures, and camera position.",
                    html.Pre(QUICK_START_CODE, style=CODE_BLOCK_STYLE),
                ),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))", "gap": "18px"},
        ),
        doc_card(
            "What the Package Covers",
            "The wrapper focuses on the JSON-serialisable features from react-globe.gl and exposes them through Python helpers plus direct Dash props when you need full control.",
            build_badge_row(
                [
                    "Chainable scene and camera helpers",
                    "All major geographic layers",
                    "Dash-native interaction props",
                    "Day/night cycle and clouds",
                    "Serializable materials and ring interpolation",
                ]
            ),
        ),
    )


def build_api_overview_section():
    return build_doc_section(
        "api-overview",
        "API Overview",
        "The high-level API is centered on dash_globe.globe.DashGlobe, which layers Pythonic convenience methods on top of the generated Dash component surface.",
        html.Div(
            [
                doc_card(
                    "Builder Pattern",
                    "Use update_layout, update_globe, update_view, and the add_* / update_* layer helpers to keep globe configuration readable as scenes grow.",
                    html.Pre(BUILDER_PATTERN_CODE, style=CODE_BLOCK_STYLE),
                    build_method_reference(),
                ),
                doc_card(
                    "Component Surface",
                    "You can always drop down to direct component props. The groups below organize the generated DashGlobe API the same way component documentation pages usually group props by concern.",
                    build_prop_group_reference(),
                ),
            ],
            style={"display": "grid", "gap": "18px"},
        ),
    )


def build_helper_guides_section():
    return build_doc_section(
        "helper-guides",
        "Helper Guides",
        "These mini-docs focus on the main builder helpers one at a time. Each subsection follows the same pattern as a component-doc page: short description, related props, and a dedicated example.",
        build_helper_guides_grid(),
    )


def build_layer_reference_section():
    return build_doc_section(
        "layer-reference",
        "Layer Reference",
        "Each supported layer follows the same pattern: append data with add_* helpers, then describe how to read your records with update_* accessors.",
        html.Div(
            [
                doc_card(
                    "Layer Helper Matrix",
                    "This is the quickest way to map a dataset to the right globe layer and discover the accessor names that matter most.",
                    build_reference_table(
                        ["Layer", "Helpers", "Common Accessors", "Live Example"],
                        LAYER_REFERENCE_ROWS,
                    ),
                ),
                doc_card(
                    "Advanced Layer Combinations",
                    "You can freely mix multiple layers on the same globe, or use raw props when you need an accessor that is not surfaced by a helper alias.",
                    html.Pre(ADVANCED_FEATURES_CODE, style=CODE_BLOCK_STYLE),
                ),
            ],
            style={"display": "grid", "gap": "18px"},
        ),
    )


def build_utilities_section():
    return build_doc_section(
        "utilities",
        "Utilities",
        "The package includes a small set of helper exports so common react-globe.gl patterns remain serialisable and ergonomic in Dash.",
        doc_card(
            "Utility Exports",
            "These helpers cover common texture presets, event normalisation, ring-color interpolation, and material-backed layer styling.",
            build_reference_table(
                ["Helper", "What It Does"],
                UTILITY_REFERENCE_ROWS,
            ),
        ),
    )


def build_callbacks_section():
    return build_doc_section(
        "callbacks",
        "Callbacks",
        "Dash Globe behaves like a regular Dash component: the same interaction props you inspect in the docs can be read and written inside callbacks.",
        html.Div(
            [
                doc_card(
                    "Interaction Props",
                    "These props make selection, hover highlighting, event logging, and camera-aware dashboards straightforward to implement.",
                    build_reference_table(
                        ["Prop", "Typical Use"],
                        EVENT_REFERENCE_ROWS,
                    ),
                ),
                doc_card(
                    "Callback Example",
                    "Use event_coords when you only care about geographic position instead of the full browser event payload shape.",
                    html.Pre(CALLBACKS_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                ),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))", "gap": "18px"},
        ),
    )


def build_api_reference_section():
    return build_doc_section(
        "api-reference",
        "API Reference",
        "This section follows a more reference-oriented format inspired by API docs such as pandas: each item shows a signature, parameter table, return value, and implementation notes.",
        build_api_reference_list(),
    )


CODE_BLOCK_STYLE = {
    "margin": 0,
    "whiteSpace": "pre-wrap",
    "fontFamily": "Consolas, monospace",
    "fontSize": "0.88rem",
    "color": "#233241",
    "background": "#f8fafc",
    "border": "1px solid #e7edf4",
    "padding": "12px",
    "borderRadius": "12px",
    "overflowX": "auto",
    "lineHeight": 1.55,
}

RUN_BUTTON_STYLE = {
    "position": "absolute",
    "top": "14px",
    "right": "14px",
    "zIndex": 2,
    "border": "1px solid #2f5bd2",
    "borderRadius": "999px",
    "padding": "9px 14px",
    "background": "#2f5bd2",
    "color": "#ffffff",
    "fontWeight": 600,
    "cursor": "pointer",
    "boxShadow": "0 6px 16px rgba(47, 91, 210, 0.18)",
}

PLACEHOLDER_BODY_STYLE = {
    "height": "420px",
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "center",
    "textAlign": "center",
    "padding": "24px",
    "borderRadius": "14px",
    "border": "1px dashed #cfd9e7",
    "background": "linear-gradient(180deg, #f8fbff 0%, #eef3f9 100%)",
    "color": "#41556b",
}

GLOBE_CONTAINER_STYLE = {
    "position": "relative",
    "minHeight": "420px",
}

SITUATION_ROOM_SCENE_STYLE = {
    "position": "relative",
    "minHeight": SITUATION_ROOM_STAGE_MIN_HEIGHT,
    "overflow": "hidden",
    "borderRadius": "14px",
    "border": "1px solid rgba(34, 211, 238, 0.22)",
    "background": "radial-gradient(circle at top, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 1) 60%, rgba(1, 3, 8, 1) 100%)",
    "boxShadow": "inset 0 0 60px rgba(34, 211, 238, 0.08)",
}

SITUATION_ROOM_HEADER_STYLE = {
    "position": "absolute",
    "top": "16px",
    "left": "50%",
    "transform": "translateX(-50%)",
    "display": "grid",
    "gap": "6px",
    "padding": "10px 16px",
    "border": "1px solid rgba(103, 232, 249, 0.32)",
    "borderRadius": "999px",
    "background": "rgba(2, 6, 23, 0.72)",
    "backdropFilter": "blur(10px)",
    "boxShadow": "0 0 32px rgba(34, 211, 238, 0.12)",
    "textAlign": "center",
    "zIndex": 1,
    "pointerEvents": "none",
}

SITUATION_ROOM_CARD_STYLE = {
    "display": "grid",
    "gap": "10px",
    "width": "210px",
    "maxWidth": "calc(100% - 28px)",
    "minHeight": "268px",
    "padding": "14px",
    "border": "1px solid rgba(103, 232, 249, 0.72)",
    "borderRadius": "14px",
    "background": "linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(2, 6, 23, 0.94) 100%)",
    "boxShadow": "0 0 30px rgba(34, 211, 238, 0.14)",
    "backdropFilter": "blur(12px)",
    "zIndex": 1,
    "pointerEvents": "auto",
    "overflow": "hidden",
}

SITUATION_ROOM_TOPIC_STYLE = {
    "display": "inline-flex",
    "alignItems": "center",
    "padding": "4px 8px",
    "borderRadius": "999px",
    "background": "rgba(34, 211, 238, 0.14)",
    "color": "#67e8f9",
    "fontSize": "0.68rem",
    "fontWeight": 700,
    "letterSpacing": "0.08em",
}

SITUATION_ROOM_COUNTRY_STYLE = {
    "fontSize": "0.72rem",
    "fontWeight": 700,
    "letterSpacing": "0.08em",
    "textTransform": "uppercase",
    "color": "#e2e8f0",
}

SITUATION_ROOM_CARD_IMAGE_STYLE = {
    "display": "block",
    "width": "100%",
    "height": "96px",
    "objectFit": "cover",
    "borderRadius": "10px",
    "border": "1px solid rgba(103, 232, 249, 0.24)",
    "background": "rgba(15, 23, 42, 0.78)",
}

SITUATION_ROOM_CARD_DESCRIPTION_STYLE = {
    "margin": 0,
    "fontSize": "0.82rem",
    "lineHeight": 1.55,
    "color": "#b6c2cf",
    "maxHeight": "78px",
    "overflow": "hidden",
}

SITUATION_ROOM_STORY_POINTS = build_situation_room_story_points()
SITUATION_ROOM_VISIBLE_SNAPSHOTS = build_situation_room_visible_story_snapshots()

GLOBE_IDS = [
    "basic-example-globe",
    "random-arcs-example-globe",
    EMIT_ARCS_GLOBE_ID,
    "random-rings-example-globe",
    "heatmap-example-globe",
    "day-night-cycle-globe",
    "clouds-globe",
    "submarine-cables-globe",
    "world-cities-globe",
    "tiles-example-globe",
    "airline-routes-globe",
    "countries-population-globe",
    "choropleth-countries-globe",
    "hollow-globe",
    "situation-room-globe",
]


def build_globe_placeholder(globe_id):
    return html.Div(
        html.Div(
            [
                html.Div("Idle", style={"fontSize": "0.78rem", "letterSpacing": "0.14em", "textTransform": "uppercase", "opacity": 0.7}),
                html.H4("Click Run to mount this globe", style={"margin": "10px 0 8px 0", "fontSize": "1.2rem"}),
                html.P(
                    "Only one globe is rendered at a time in this gallery so the browser stays responsive while you explore.",
                    style={"maxWidth": "320px", "margin": 0, "lineHeight": 1.6},
                ),
            ]
        ),
        id=f"{globe_id}-placeholder",
        style=PLACEHOLDER_BODY_STYLE,
    )


def build_globe_stage(globe_id):
    container_style = dict(GLOBE_CONTAINER_STYLE)
    if globe_id == SITUATION_ROOM_GLOBE_ID:
        container_style["minHeight"] = SITUATION_ROOM_STAGE_MIN_HEIGHT
    return html.Div(
        [
            html.Div(id=f"{globe_id}-mount", children=build_globe_placeholder(globe_id)),
            html.Button("Run", id=f"{globe_id}-run-button", n_clicks=0, style=RUN_BUTTON_STYLE),
        ],
        style=container_style,
    )


def build_gallery_footer():
    return html.P(
        [
            html.Code("clickData"),
            ", ",
            html.Code("hoverData"),
            ", ",
            html.Code("rightClickData"),
            ", and ",
            html.Code("currentView"),
            " are regular Dash props, so the globe participates in the same callback model as the rest of a Dash app. "
            "This gallery only mounts one globe at a time to keep browser performance healthy.",
        ],
        id="gallery-footer",
        style={"marginTop": "20px", "color": "#5f6b7a", "lineHeight": 1.7},
    )


def build_basic_example_globe():
    return (
        dash_globe.DashGlobe(id="basic-example-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .add_points(BASIC_EXAMPLE_POINTS)
        .update_points(
            pointAltitude="size",
            pointColor="color",
        )
    )


def build_random_arcs_example_globe():
    return (
        dash_globe.DashGlobe(id="random-arcs-example-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .add_arcs(RANDOM_ARCS_EXAMPLE_DATA)
        .update_arcs(
            arcColor="color",
            arcDashLength="dashLength",
            arcDashGap="dashGap",
            arcDashAnimateTime="dashTime",
        )
    )


def build_emit_arcs_on_click_globe():
    return html.Div(
        [
            dash_globe.DashGlobe(id=EMIT_ARCS_GLOBE_ID)
            .update_layout(height=420, background_color="#000000")
            .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
            .update_arcs(
                [],
                arc_start_lat="startLat",
                arc_start_lng="startLng",
                arc_end_lat="endLat",
                arc_end_lng="endLng",
                arc_color="color",
                arc_altitude="altitude",
                arc_stroke="stroke",
                arc_dash_length="dashLength",
                arc_dash_gap="dashGap",
                arc_dash_initial_gap="dashInitialGap",
                arc_dash_animate_time="dashAnimateTime",
                arcs_transition_duration=0,
            )
            .update_rings(
                [],
                ring_color=dash_globe.ring_color_interpolator("rgb(255, 100, 50)"),
                ring_max_radius=EMIT_ARCS_RINGS_MAX_R,
                ring_propagation_speed=EMIT_ARCS_RING_PROPAGATION_SPEED,
                ring_repeat_period=EMIT_ARCS_RING_REPEAT_PERIOD,
            ),
            dcc.Store(id=EMIT_ARCS_STORE_ID, data=build_emit_arcs_state()),
            dcc.Interval(id=EMIT_ARCS_INTERVAL_ID, interval=EMIT_ARCS_TICK_INTERVAL, disabled=True),
        ]
    )


def build_random_rings_example_globe():
    return (
        dash_globe.DashGlobe(id="random-rings-example-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .add_rings(RANDOM_RINGS_EXAMPLE_DATA)
        .update_rings(
            ring_color=dash_globe.ring_color_interpolator("#ff6432"),
            ring_max_radius="maxR",
            ring_propagation_speed="propagationSpeed",
            ring_repeat_period="repeatPeriod",
        )
    )


def build_heatmap_example_globe():
    return (
        dash_globe.DashGlobe(id="heatmap-example-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_DARK)
        .update_interaction(enable_pointer_interaction=False)
        .add_heatmap(HEATMAP_EXAMPLE_DATA)
        .update_heatmaps(
            heatmap_point_lat="lat",
            heatmap_point_lng="lng",
            heatmap_point_weight="weight",
            heatmap_top_altitude=0.7,
            heatmaps_transition_duration=3000,
        )
    )


def build_day_night_cycle_globe():
    return (
        dash_globe.DashGlobe(id="day-night-cycle-globe")
        .update_layout(height=420, background_image_url=dash_globe.PRESETS.NIGHT_SKY)
        .update_globe(show_atmosphere=False)
        .update_view(lat=12, lng=-38, altitude=2.2, transition_duration=0)
        .update_day_night_cycle(
            day_image_url=dash_globe.PRESETS.EARTH,
            night_image_url=dash_globe.PRESETS.EARTH_NIGHT,
            time="2026-04-17T12:00:00Z",
            minutes_per_second=60,
        )
    )


def build_clouds_globe():
    return (
        dash_globe.DashGlobe(id="clouds-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(
            globe_image_url=dash_globe.PRESETS.EARTH_DAY,
            bump_image_url=dash_globe.PRESETS.EARTH_TOPOGRAPHY,
            show_atmosphere=False,
        )
        .update_controls(auto_rotate=True, auto_rotate_speed=0.35)
        .update_clouds(
            image_url=dash_globe.PRESETS.CLOUDS,
            altitude=0.004,
            rotation_speed=-0.006,
        )
    )


def build_submarine_cables_globe():
    return (
        dash_globe.DashGlobe(id="submarine-cables-globe")
        .update_layout(height=420, background_image_url=dash_globe.PRESETS.NIGHT_SKY)
        .update_globe(
            globe_image_url=dash_globe.PRESETS.EARTH_DARK,
            bump_image_url=dash_globe.PRESETS.EARTH_TOPOGRAPHY,
        )
        .add_paths(SUBMARINE_CABLE_PATHS)
        .update_paths(
            path_label="labelHtml",
            path_points="coords",
            path_point_lat="lat",
            path_point_lng="lng",
            path_color="color",
            path_dash_length=0.1,
            path_dash_gap=0.008,
            path_dash_animate_time=12000,
            path_transition_duration=0,
        )
    )


def build_world_cities_globe():
    return (
        dash_globe.DashGlobe(id="world-cities-globe")
        .update_layout(height=420, background_image_url=dash_globe.PRESETS.NIGHT_SKY)
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .add_labels(WORLD_CITIES)
        .update_labels(
            label_label="labelHtml",
            label_lat="lat",
            label_lng="lng",
            label_text="name",
            label_size="size",
            label_color="color",
            label_include_dot=True,
            label_dot_radius="dotRadius",
            label_resolution=2,
        )
    )


def build_tiles_example_globe():
    return (
        dash_globe.DashGlobe(id="tiles-example-globe")
        .update_layout(height=420, background_color="#000000")
        .add_tiles(TILES_EXAMPLE_DATA)
        .update_tiles(
            tile_label="labelHtml",
            tile_lat="lat",
            tile_lng="lng",
            tile_width=TILES_EXAMPLE_TILE_WIDTH - TILE_MARGIN,
            tile_height=TILES_EXAMPLE_TILE_HEIGHT - TILE_MARGIN,
            tile_material="material",
        )
    )


def build_airline_routes_example_globe():
    return (
        dash_globe.DashGlobe(id="airline-routes-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .update_view(lat=37.6, lng=-16.6, altitude=0.42, transition_duration=0)
        .add_arcs(build_airline_route_styles())
        .update_arcs(
            arc_label="label",
            arc_start_lat="startLat",
            arc_start_lng="startLng",
            arc_end_lat="endLat",
            arc_end_lng="endLng",
            arc_color="color",
            arc_dash_length=0.4,
            arc_dash_gap=0.2,
            arc_dash_animate_time=1500,
            arcs_transition_duration=0,
        )
        .add_points(PORTUGAL_AIRPORTS)
        .update_points(
            point_lat="lat",
            point_lng="lng",
            point_color="color",
            point_label="label",
            point_altitude=0,
            point_radius=0.04,
            points_merge=True,
        )
    )


def build_choropleth_countries_globe():
    return (
        dash_globe.DashGlobe(id="choropleth-countries-globe")
        .update_layout(height=420, background_image_url=CHOROPLETH_BACKGROUND_IMAGE_URL)
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
        .update_interaction(line_hover_precision=0)
        .add_polygons(build_choropleth_country_styles())
        .update_polygons(
            polygon_geo_json_geometry="geometry",
            polygon_cap_color="capColor",
            polygon_side_color="sideColor",
            polygon_stroke_color="strokeColor",
            polygon_altitude="altitude",
            polygon_hover_key="countryId",
            polygon_hover_altitude=0.12,
            polygon_hover_cap_color="steelblue",
            polygon_label="labelHtml",
            polygons_transition_duration=300,
        )
    )


def build_hollow_globe():
    return (
        dash_globe.DashGlobe(id="hollow-globe")
        .update_layout(height=420, background_color="rgba(0, 0, 0, 0)")
        .update_globe(show_globe=False, show_atmosphere=False)
        .update_view(lat=18, lng=12, altitude=2.05, transition_duration=0)
        .update_interaction(enable_pointer_interaction=False, show_pointer_cursor=False)
        .add_polygons(HOLLOW_GLOBE_LAND_POLYGONS)
        .update_polygons(
            polygon_geo_json_geometry="geometry",
            polygon_cap_material=dash_globe.lambert_material(
                color="darkslategrey",
                side="double",
            ),
            polygon_side_color="rgba(0, 0, 0, 0)",
            polygon_stroke_color=False,
        )
    )


def build_countries_population_globe():
    return (
        dash_globe.DashGlobe(id="countries-population-globe")
        .update_layout(height=420, background_color="#000000")
        .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_DARK)
        .update_view(altitude=4, transition_duration=5000)
        .update_interaction(line_hover_precision=0)
        .add_polygons(build_population_country_styles())
        .update_polygons(
            polygon_geo_json_geometry="geometry",
            polygon_cap_color="capColor",
            polygon_side_color="sideColor",
            polygon_altitude="populationAltitude",
            polygon_label="populationLabelHtml",
            polygons_transition_duration=4000,
        )
    )


def build_situation_room_globe():
    snapshots = SITUATION_ROOM_VISIBLE_SNAPSHOTS
    globe = (
        dash_globe.DashGlobe(id=SITUATION_ROOM_GLOBE_ID)
        .update_layout(
            height=SITUATION_ROOM_GLOBE_HEIGHT,
            background_color="rgba(0, 0, 0, 0)",
            background_image_url=dash_globe.PRESETS.NIGHT_SKY,
        )
        .update_globe(
            globe_image_url=dash_globe.PRESETS.EARTH_DARK,
            bump_image_url=dash_globe.PRESETS.EARTH_TOPOGRAPHY,
            show_graticules=True,
            atmosphere_color="#22d3ee",
            atmosphere_altitude=0.16,
        )
        .update_view(**SITUATION_ROOM_INITIAL_VIEW, transition_duration=0)
        .update_controls(auto_rotate=True, auto_rotate_speed=SITUATION_ROOM_AUTO_ROTATE_SPEED)
        .update_interaction(
            enable_pointer_interaction=False,
            show_pointer_cursor=False,
            current_view_report_interval=SITUATION_ROOM_CURRENT_VIEW_REPORT_INTERVAL,
        )
        .add_points(SITUATION_ROOM_STORY_POINTS)
        .update_points(
            point_lat="lat",
            point_lng="lng",
            point_altitude="altitude",
            point_color="color",
            point_radius="radius",
            point_label="labelHtml",
            point_resolution=12,
        )
        .add_rings([snapshot["ring"] for snapshot in snapshots])
        .update_rings(
            ring_lat="lat",
            ring_lng="lng",
            ring_color=dash_globe.ring_color_interpolator("#67e8f9"),
            ring_max_radius="maxR",
            ring_propagation_speed="propagationSpeed",
            ring_repeat_period="repeatPeriod",
        )
        .update_html_elements(
            [snapshot["overlay"] for snapshot in snapshots],
            children=build_situation_room_story_cards(snapshots),
            html_element_lat="lat",
            html_element_lng="lng",
            html_element_altitude="altitude",
            html_element_key="storyId",
            html_element_screen_side="screenSide",
            html_element_screen_x="screenX",
            html_element_screen_y="screenY",
            html_element_tether="tether",
            html_element_tether_color="tetherColor",
            html_element_tether_width="tetherWidth",
            html_element_tether_attach="tetherAttach",
        )
    )
    return html.Div(
        [
            globe,
            dcc.Store(
                id=SITUATION_ROOM_SELECTION_STORE_ID,
                data=build_situation_room_selection_signature(snapshots),
            ),
            html.Div(build_situation_room_header(snapshots), id=SITUATION_ROOM_HEADER_ID),
            html.Div(build_situation_room_story_status(snapshots), id=SITUATION_ROOM_STATUS_ID),
        ],
        style=SITUATION_ROOM_SCENE_STYLE,
    )


GLOBE_BUILDERS = {
    "basic-example-globe": build_basic_example_globe,
    "random-arcs-example-globe": build_random_arcs_example_globe,
    EMIT_ARCS_GLOBE_ID: build_emit_arcs_on_click_globe,
    "random-rings-example-globe": build_random_rings_example_globe,
    "heatmap-example-globe": build_heatmap_example_globe,
    "day-night-cycle-globe": build_day_night_cycle_globe,
    "clouds-globe": build_clouds_globe,
    "submarine-cables-globe": build_submarine_cables_globe,
    "world-cities-globe": build_world_cities_globe,
    "tiles-example-globe": build_tiles_example_globe,
    "airline-routes-globe": build_airline_routes_example_globe,
    "countries-population-globe": build_countries_population_globe,
    "choropleth-countries-globe": build_choropleth_countries_globe,
    "hollow-globe": build_hollow_globe,
    "situation-room-globe": build_situation_room_globe,
}


def build_example_group(title, description, cards):
    return html.Div(
        [
            html.Div(
                [
                    html.H3(title, style={"margin": "0 0 8px 0", "color": "#182433"}),
                    html.P(description, style={"margin": 0, "color": "#5f6b7a", "lineHeight": 1.7}),
                ],
                style={"marginBottom": "16px"},
            ),
            html.Div(
                cards,
                style={
                    "display": "grid",
                    "gap": "22px",
                },
            ),
        ],
        style={"marginBottom": "30px"},
    )


def build_examples_grid():
    return html.Div(
        [
            build_example_group(
                "Core Layers",
                "These examples cover the most common starting points: points, arcs, animated click feedback, rings, and weighted heatmaps.",
                [
                    globe_card(
                        "Upstream Basic Example",
                        "This mirrors the official basic react-globe.gl demo: a night-earth texture plus 300 random colored points whose altitude comes from a size field.",
                        build_globe_stage("basic-example-globe"),
                        html.Pre(BASIC_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Random Arcs",
                        "This mirrors the official random-arcs demo by precomputing the per-arc dash length, gap, and animation time in Python.",
                        build_globe_stage("random-arcs-example-globe"),
                        html.Pre(RANDOM_ARCS_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Emit Arcs On Click",
                        "This ports the emit-arcs-on-click demo into Dash by listening to globe click payloads, extracting geographic coordinates with a small event helper, and pruning transient arcs and rings on a short interval.",
                        build_globe_stage(EMIT_ARCS_GLOBE_ID),
                        html.Div(
                            [
                                html.Pre(EMIT_ARCS_ON_CLICK_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                                html.Pre(
                                    id="emit-arcs-on-click-event",
                                    children=EMIT_ARCS_EVENT_PLACEHOLDER,
                                    style={**CODE_BLOCK_STYLE, "margin": "12px 0 0 0"},
                                ),
                            ]
                        ),
                    ),
                    globe_card(
                        "Upstream Ripple Rings",
                        "This mirrors the official random-rings demo and uses a serialisable ring color interpolator helper so Dash can recreate the fading ripple callback clientside.",
                        build_globe_stage("random-rings-example-globe"),
                        html.Pre(RANDOM_RINGS_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Heatmap",
                        "This mirrors the official heatmap demo with a single weighted dataset, and uses the package's single-heatmap helper so the Python API reads like a normal Dash layer setup.",
                        build_globe_stage("heatmap-example-globe"),
                        html.Pre(HEATMAP_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                ],
            ),
            build_example_group(
                "Scene Effects",
                "These examples focus on global presentation: day and night shading, atmospheric shells, and cloud overlays.",
                [
                    globe_card(
                        "Upstream Day Night Cycle",
                        "This ports the official day-night-cycle demo with a first-class shader mode, so Dash apps can blend day and night textures without constructing a raw Three.js material in Python.",
                        build_globe_stage("day-night-cycle-globe"),
                        html.Pre(DAY_NIGHT_CYCLE_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Clouds",
                        "This mirrors the official clouds demo with a first-class rotating cloud shell, so Dash apps can add the extra transparent sphere without dropping down into Three.js scene management.",
                        build_globe_stage("clouds-globe"),
                        html.Pre(CLOUDS_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Hollow Globe",
                        "This adapts the hollow-globe example with double-sided polygon caps, so land remains visible through the transparent shell without exposing raw Three.js materials in Python.",
                        build_globe_stage("hollow-globe"),
                        html.Pre(HOLLOW_GLOBE_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                ],
            ),
            build_example_group(
                "Geographic Features",
                "These examples demonstrate paths, labels, tiles, and polygon-driven storytelling datasets.",
                [
                    globe_card(
                        "Upstream Submarine Cables",
                        "This mirrors the linked submarine-cables demo by flattening the cable GeoJSON into serialisable path segments, then exposing them through a richer path helper instead of raw prop names.",
                        build_globe_stage("submarine-cables-globe"),
                        html.Div(
                            [
                                html.Pre(SUBMARINE_CABLES_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                                html.Pre(
                                    id="submarine-cables-event",
                                    children="Click Run to mount this globe, then hover a cable segment to inspect the latest path payload.",
                                    style={**CODE_BLOCK_STYLE, "margin": "12px 0 0 0"},
                                ),
                            ]
                        ),
                    ),
                    globe_card(
                        "Upstream World Cities",
                        "This mirrors the official world-cities demo by loading the same Natural Earth populated-places GeoJSON and sizing each city label and marker dot from the square root of its maximum population.",
                        build_globe_stage("world-cities-globe"),
                        html.Pre(WORLD_CITIES_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Tiles",
                        "This ports the official tiles demo with a first-class tile material accessor, so Python code can pass JSON material specs per tile instead of constructing raw Three.js materials in JavaScript.",
                        build_globe_stage("tiles-example-globe"),
                        html.Pre(TILES_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                ],
            ),
            build_example_group(
                "Interactive Data Stories",
                "These examples combine callbacks with richer datasets so hover and selection drive visual state.",
                [
                    globe_card(
                        "Situation Room Briefing",
                        "This package-specific advanced example turns a breaking-news payload into a dark-mode command-center scene with up to two tethered popups at once, always choosing the two stories closest to the live camera center and updating as the user drags the globe.",
                        build_globe_stage("situation-room-globe"),
                        html.Pre(SITUATION_ROOM_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                    ),
                    globe_card(
                        "Upstream Airline Routes Highlight",
                        "This ports the official highlight-links demo into Dash by loading the OpenFlights airport and route datasets at startup, filtering them to Portuguese domestic non-stop routes, and then highlighting the hovered arc.",
                        build_globe_stage("airline-routes-globe"),
                        html.Div(
                            [
                                html.Pre(AIRLINE_ROUTES_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                                html.Pre(
                                    id="airline-routes-event",
                                    children="Click Run to mount this globe, then hover a route to inspect the latest payload.",
                                    style={**CODE_BLOCK_STYLE, "margin": "12px 0 0 0"},
                                ),
                            ]
                        ),
                    ),
                    globe_card(
                        "Upstream Countries Population",
                        "This ports globe.gl's countries-population example by loading the same Natural Earth GeoJSON and extruding each country polygon by the square root of its population.",
                        build_globe_stage("countries-population-globe"),
                        html.Div(
                            [
                                html.Pre(COUNTRIES_POPULATION_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                                html.Pre(
                                    id="countries-population-event",
                                    children="Click Run to mount this globe, then hover a country to inspect the latest population-polygon payload.",
                                    style={**CODE_BLOCK_STYLE, "margin": "12px 0 0 0"},
                                ),
                            ]
                        ),
                    ),
                    globe_card(
                        "Upstream Choropleth Countries",
                        "This mirrors the choropleth-countries demo by loading the Natural Earth country GeoJSON, coloring countries by GDP per capita, and highlighting the hovered polygon clientside while still exposing hover payloads to Dash.",
                        build_globe_stage("choropleth-countries-globe"),
                        html.Div(
                            [
                                html.Pre(CHOROPLETH_COUNTRIES_EXAMPLE_CODE, style=CODE_BLOCK_STYLE),
                                html.Pre(
                                    id="choropleth-countries-event",
                                    children="Click Run to mount this globe, then hover a country to inspect the latest payload.",
                                    style={**CODE_BLOCK_STYLE, "margin": "12px 0 0 0"},
                                ),
                            ]
                        ),
                    ),
                ],
            ),
        ],
        style={"display": "grid", "gap": "8px"},
    )


app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    f"Dash Globe Documentation v{dash_globe.__version__}",
                    style={
                        "fontSize": "0.8rem",
                        "fontWeight": 700,
                        "letterSpacing": "0.08em",
                        "textTransform": "uppercase",
                        "color": "#738295",
                        "marginBottom": "10px",
                    },
                ),
                html.H1("Dash Globe", style={"margin": "0 0 12px 0", "fontSize": "2.9rem", "color": "#182433"}),
                html.P(
                    "Build interactive globe visualizations in Dash with a docs-first Python API: chainable scene helpers, full layer coverage, utility exports for common Three Globe patterns, and regular Dash callback props for interactivity.",
                    style={"maxWidth": "860px", "color": "#5f6b7a", "fontSize": "1.05rem", "lineHeight": 1.8, "margin": 0},
                ),
                build_badge_row(
                    [
                        "Chainable scene and camera helpers",
                        "Points, arcs, polygons, paths, heatmaps, hex bins, tiles, particles, rings, and labels",
                        "Day/night cycle and rotating clouds",
                        "Serializable materials and ring color helpers",
                        "clickData, hoverData, rightClickData, currentView, globeReady, lastInteraction",
                    ]
                ),
            ],
            style={**PANEL_STYLE, "marginBottom": "28px", "padding": "28px"},
        ),
        html.Div(
            [
                build_section_nav(),
                html.Main(
                    [
                        build_getting_started_section(),
                        build_api_overview_section(),
                        build_helper_guides_section(),
                        build_layer_reference_section(),
                        build_utilities_section(),
                        build_callbacks_section(),
                        build_api_reference_section(),
                        build_doc_section(
                            "examples",
                            "Live Examples",
                            "These runnable examples mirror upstream react-globe.gl demos and package-specific helpers. The gallery still mounts one globe at a time so heavier scenes stay responsive while you browse the docs.",
                            build_examples_grid(),
                            build_gallery_footer(),
                        ),
                    ],
                    style={"flex": "1 1 780px", "minWidth": 0},
                ),
            ],
            style={"display": "flex", "flexWrap": "wrap", "alignItems": "flex-start", "gap": "28px"},
        ),
    ],
    style={
        "minHeight": "100vh",
        "padding": "24px",
        "background": "#f6f8fb",
        "color": "#182433",
        "fontFamily": "Inter, Segoe UI, sans-serif",
    },
)


@app.callback(
    *(Output(f"{globe_id}-mount", "children") for globe_id in GLOBE_IDS),
    *(Input(f"{globe_id}-run-button", "n_clicks") for globe_id in GLOBE_IDS),
)
def render_selected_globe(*_):
    active_globe_id = ctx.triggered_id.removesuffix("-run-button") if ctx.triggered_id else None
    return [
        GLOBE_BUILDERS[globe_id]() if globe_id == active_globe_id else build_globe_placeholder(globe_id)
        for globe_id in GLOBE_IDS
    ]


@app.callback(
    Output("submarine-cables-event", "children"),
    Input("submarine-cables-globe", "hoverData"),
)
def describe_submarine_cable_hover(hover_data):
    payload_text = "Hover a cable segment to inspect the latest path payload."
    if hover_data is not None:
        payload_text = json.dumps(hover_data, indent=2)

    return payload_text


@app.callback(
    Output(EMIT_ARCS_STORE_ID, "data"),
    Output(EMIT_ARCS_GLOBE_ID, "arcsData"),
    Output(EMIT_ARCS_GLOBE_ID, "ringsData"),
    Output("emit-arcs-on-click-event", "children"),
    Output(EMIT_ARCS_INTERVAL_ID, "disabled"),
    Input(EMIT_ARCS_GLOBE_ID, "clickData"),
    Input(EMIT_ARCS_INTERVAL_ID, "n_intervals"),
    State(EMIT_ARCS_STORE_ID, "data"),
)
def sync_emit_arcs_on_click(click_data, _n_intervals, state):
    now_ms = current_time_millis()
    next_state = normalise_emit_arcs_state(state)

    if ctx.triggered_id == EMIT_ARCS_GLOBE_ID:
        next_state = append_emit_arc_click(next_state, click_data, now_ms)

    next_state, arcs_data, rings_data = build_emit_arcs_snapshot(next_state, now_ms)

    payload_text = EMIT_ARCS_EVENT_PLACEHOLDER
    if click_data is not None:
        payload_text = json.dumps(click_data, indent=2)

    interval_disabled = not next_state["arcs"] and not next_state["rings"]
    return next_state, arcs_data, rings_data, payload_text, interval_disabled


@app.callback(
    Output("airline-routes-globe", "arcsData"),
    Output("airline-routes-event", "children"),
    Input("airline-routes-globe", "hoverData"),
)
def highlight_airline_routes(hover_data):
    hovered_route_id = None
    if hover_data and hover_data.get("layer") == "arc" and hover_data.get("data"):
        hovered_route_id = hover_data["data"].get("routeId")

    payload_text = "Hover a route to highlight it and inspect the latest hover payload."
    if hover_data is not None:
        payload_text = json.dumps(hover_data, indent=2)

    return build_airline_route_styles(hovered_route_id), payload_text


@app.callback(
    Output("choropleth-countries-event", "children"),
    Input("choropleth-countries-globe", "hoverData"),
)
def highlight_choropleth_country(hover_data):
    payload_text = "Hover a country to highlight it and inspect the latest hover payload."
    if hover_data is not None:
        payload_text = json.dumps(hover_data, indent=2)

    return payload_text


@app.callback(
    Output("countries-population-event", "children"),
    Input("countries-population-globe", "hoverData"),
)
def describe_countries_population_hover(hover_data):
    payload_text = "Hover a country to inspect the latest population-polygon payload."
    if hover_data is not None:
        payload_text = json.dumps(hover_data, indent=2)

    return payload_text


@app.callback(
    Output(SITUATION_ROOM_SELECTION_STORE_ID, "data"),
    Output(SITUATION_ROOM_GLOBE_ID, "ringsData"),
    Output(SITUATION_ROOM_GLOBE_ID, "htmlElementsData"),
    Output(SITUATION_ROOM_GLOBE_ID, "children"),
    Output(SITUATION_ROOM_HEADER_ID, "children"),
    Output(SITUATION_ROOM_STATUS_ID, "children"),
    Input(SITUATION_ROOM_GLOBE_ID, "currentView"),
    State(SITUATION_ROOM_SELECTION_STORE_ID, "data"),
)
def sync_situation_room_scene(current_view=None, selection_signature=None):
    snapshots = build_situation_room_visible_story_snapshots(
        current_view=current_view,
        cycle_step=0,
    )
    next_signature = build_situation_room_selection_signature(snapshots)
    if selection_signature == next_signature:
        return no_update, no_update, no_update, no_update, no_update, no_update
    return (
        next_signature,
        [snapshot["ring"] for snapshot in snapshots],
        [snapshot["overlay"] for snapshot in snapshots],
        build_situation_room_story_cards(snapshots),
        build_situation_room_header(snapshots),
        build_situation_room_story_status(snapshots),
    )


if __name__ == "__main__":
    # Dash debug bundles currently surface upstream React defaultProps warnings.
    # Keep the gallery clean by default and make debug mode opt-in.
    app.run(**get_demo_run_kwargs())
