import pytest
from dash import html

from dash_globe import DashGlobe, event_coords, lambert_material, material_spec, ring_color_interpolator


def test_update_accepts_snake_case_aliases():
    globe = (
        DashGlobe(id="alias-globe")
        .update(background_color="#010203", line_hover_precision=0.25)
        .update_arcs(
            data=[{"startLat": 1, "startLng": 2, "endLat": 3, "endLng": 4}],
            arc_start_lat="startLat",
            arc_start_lng="startLng",
            arc_end_lat="endLat",
            arc_end_lng="endLng",
            arc_dash_animate_time=1500,
            arcs_transition_duration=0,
        )
        .update_paths(
            data=[{"coords": [{"lat": 1, "lng": 2}, {"lat": 3, "lng": 4}]}],
            path_points="coords",
            path_point_lat="lat",
            path_point_lng="lng",
            path_color="color",
            path_dash_length=0.1,
            path_dash_gap=0.02,
            path_dash_animate_time=12000,
            path_transition_duration=0,
        )
        .update_points(
            point_lat="lat",
            point_lng="lng",
            point_altitude=0,
            points_merge=True,
        )
        .update_rings(
            ring_lat="lat",
            ring_lng="lng",
            ring_color=ring_color_interpolator("#ff6432"),
            ring_max_radius="maxR",
            ring_propagation_speed="speed",
            ring_repeat_period="repeatPeriod",
        )
        .update_labels(
            label_label="labelHtml",
            label_lat="lat",
            label_lng="lng",
            label_text="name",
            label_size="size",
            label_dot_radius="dotRadius",
            label_resolution=2,
        )
        .update_polygons(
            polygon_cap_material=lambert_material(color="darkslategrey", side="double"),
            polygon_hover_key="countryId",
            polygon_hover_altitude=0.12,
            polygon_hover_cap_color="steelblue",
            polygon_hover_side_color="rgba(0, 100, 0, 0.15)",
            polygon_hover_stroke_color="#111",
        )
    )

    assert globe.backgroundColor == "#010203"
    assert globe.lineHoverPrecision == 0.25
    assert globe.arcStartLat == "startLat"
    assert globe.arcStartLng == "startLng"
    assert globe.arcEndLat == "endLat"
    assert globe.arcEndLng == "endLng"
    assert globe.arcDashAnimateTime == 1500
    assert globe.arcsTransitionDuration == 0
    assert globe.pathPoints == "coords"
    assert globe.pathPointLat == "lat"
    assert globe.pathPointLng == "lng"
    assert globe.pathColor == "color"
    assert globe.pathDashLength == 0.1
    assert globe.pathDashGap == 0.02
    assert globe.pathDashAnimateTime == 12000
    assert globe.pathTransitionDuration == 0
    assert globe.pointLat == "lat"
    assert globe.pointLng == "lng"
    assert globe.pointAltitude == 0
    assert globe.pointsMerge is True
    assert globe.ringLat == "lat"
    assert globe.ringLng == "lng"
    assert globe.ringColor == {"type": "ring-color-interpolator", "color": "#ff6432"}
    assert globe.ringMaxRadius == "maxR"
    assert globe.ringPropagationSpeed == "speed"
    assert globe.ringRepeatPeriod == "repeatPeriod"
    assert globe.labelLabel == "labelHtml"
    assert globe.labelLat == "lat"
    assert globe.labelLng == "lng"
    assert globe.labelText == "name"
    assert globe.labelSize == "size"
    assert globe.labelDotRadius == "dotRadius"
    assert globe.labelResolution == 2
    assert globe.polygonCapMaterial == {"type": "lambert", "color": "darkslategrey", "side": "double"}
    assert globe.polygonHoverKey == "countryId"
    assert globe.polygonHoverAltitude == 0.12
    assert globe.polygonHoverCapColor == "steelblue"
    assert globe.polygonHoverSideColor == "rgba(0, 100, 0, 0.15)"
    assert globe.polygonHoverStrokeColor == "#111"


def test_material_helpers_build_json_serialisable_specs():
    assert material_spec("standard", color="#fff", metalness=0.2) == {
        "type": "standard",
        "color": "#fff",
        "metalness": 0.2,
    }
    assert lambert_material(color="darkslategrey", side="double", transparent=True, opacity=0.85) == {
        "type": "lambert",
        "color": "darkslategrey",
        "side": "double",
        "transparent": True,
        "opacity": 0.85,
    }

    assert ring_color_interpolator("#ff6432") == {
        "type": "ring-color-interpolator",
        "color": "#ff6432",
    }
    assert ring_color_interpolator(
        "#ff6432",
        fade_color="#110900",
        opacity=0.9,
        fade_opacity=0.15,
        easing="linear",
    ) == {
        "type": "ring-color-interpolator",
        "color": "#ff6432",
        "fadeColor": "#110900",
        "opacity": 0.9,
        "fadeOpacity": 0.15,
        "easing": "linear",
    }


def test_material_helpers_validate_type_and_side():
    with pytest.raises(ValueError):
        material_spec("toon")

    with pytest.raises(ValueError):
        lambert_material(side="inside-out")

    with pytest.raises(ValueError):
        ring_color_interpolator("", easing="sqrt")

    with pytest.raises(ValueError):
        ring_color_interpolator("#fff", easing="bounce")

    with pytest.raises(ValueError):
        ring_color_interpolator("#fff", opacity=1.2)

    with pytest.raises(ValueError):
        ring_color_interpolator("#fff", fade_opacity=-0.1)


def test_event_coords_extracts_globe_click_coordinates():
    assert event_coords(
        {
            "layer": "globe",
            "coords": {"lat": 12.5, "lng": "-99.25", "altitude": 1},
        }
    ) == {
        "lat": 12.5,
        "lng": -99.25,
        "altitude": 1.0,
    }

    assert event_coords(None) is None
    assert event_coords({"coords": {"lat": 5}}) is None
    assert event_coords({"coords": {"lat": "north", "lng": 20}}) is None


def test_heatmap_helpers_preserve_dataset_grouping_and_single_dataset_access():
    primary_points = [{"lat": 10, "lng": 20, "weight": 0.4}, {"lat": 15, "lng": 25, "weight": 0.9}]
    secondary_points = [{"lat": -10, "lng": -20, "weight": 0.2}]

    globe = (
        DashGlobe(id="heatmap-globe")
        .add_heatmap(primary_points)
        .add_heatmaps(secondary_points)
        .update_heatmap(
            primary_points,
            heatmap_point_lat="lat",
            heatmap_point_lng="lng",
            heatmap_point_weight="weight",
            heatmap_top_altitude=0.7,
        )
    )

    assert globe.heatmapsData == [primary_points]
    assert globe.heatmapPointLat == "lat"
    assert globe.heatmapPointLng == "lng"
    assert globe.heatmapPointWeight == "weight"
    assert globe.heatmapTopAltitude == 0.7

    grouped_globe = DashGlobe(id="heatmap-grouped").add_heatmaps(primary_points, secondary_points)

    assert grouped_globe.heatmapsData == [primary_points, secondary_points]


def test_update_tiles_supports_material_accessors_and_aliases():
    tiles = [
        {
            "lat": 10,
            "lng": 20,
            "material": lambert_material(color="red", transparent=True, opacity=0.6),
        }
    ]

    globe = (
        DashGlobe(id="tiles-globe")
        .add_tiles(tiles)
        .update_tiles(
            tile_label="labelHtml",
            tile_lat="lat",
            tile_lng="lng",
            tile_width=5.65,
            tile_height=8.65,
            tile_material="material",
            tile_use_globe_projection=False,
            tile_curvature_resolution=3,
            tiles_transition_duration=0,
        )
    )

    assert globe.tilesData == tiles
    assert globe.tileLabel == "labelHtml"
    assert globe.tileLat == "lat"
    assert globe.tileLng == "lng"
    assert globe.tileWidth == 5.65
    assert globe.tileHeight == 8.65
    assert globe.tileMaterial == "material"
    assert globe.tileUseGlobeProjection is False
    assert globe.tileCurvatureResolution == 3
    assert globe.tilesTransitionDuration == 0


def test_update_day_night_cycle_sets_serialisable_props():
    globe = DashGlobe(id="day-night").update_day_night_cycle(
        day_image_url="https://example.com/day.jpg",
        night_image_url="https://example.com/night.jpg",
        time="2026-04-17T12:00:00Z",
        animate=False,
        minutes_per_second=24,
    )

    assert globe.dayNightCycle is True
    assert globe.dayNightCycleDayImageUrl == "https://example.com/day.jpg"
    assert globe.dayNightCycleNightImageUrl == "https://example.com/night.jpg"
    assert globe.dayNightCycleTime == "2026-04-17T12:00:00Z"
    assert globe.dayNightCycleAnimate is False
    assert globe.dayNightCycleMinutesPerSecond == 24


def test_html_element_helpers_keep_overlay_data_and_children_in_sync():
    overlay_a = html.Div("Alpha", id="overlay-a")
    overlay_b = html.Div("Beta", id="overlay-b")
    elements = [
        {
            "storyId": "alpha",
            "lat": 10,
            "lng": 20,
            "altitude": 0.2,
            "offsetX": 18,
            "offsetY": -12,
            "screenSide": "left",
            "screenX": 18,
            "screenY": 64,
            "tether": True,
            "tetherColor": "#67e8f9",
            "tetherWidth": 2.25,
            "tetherAttach": "right",
        },
        {
            "storyId": "beta",
            "lat": -5,
            "lng": 120,
            "altitude": 0.28,
            "offsetX": -24,
            "offsetY": 8,
            "screenSide": "right",
            "screenX": 18,
            "screenY": 92,
            "tether": True,
            "tetherColor": "#67e8f9",
            "tetherWidth": 1.75,
            "tetherAttach": "left",
        },
    ]

    globe = (
        DashGlobe(id="html-overlays")
        .add_html_elements(elements, children=[overlay_a, overlay_b])
        .update_html_elements(
            html_element_lat="lat",
            html_element_lng="lng",
            html_element_altitude="altitude",
            html_element_key="storyId",
            html_element_offset_x="offsetX",
            html_element_offset_y="offsetY",
            html_element_pointer_events="auto",
            html_element_hidden=False,
            html_element_screen_side="screenSide",
            html_element_screen_x="screenX",
            html_element_screen_y="screenY",
            html_element_tether="tether",
            html_element_tether_color="tetherColor",
            html_element_tether_width="tetherWidth",
            html_element_tether_attach="tetherAttach",
        )
    )

    assert globe.htmlElementsData == elements
    assert globe.children == [overlay_a, overlay_b]
    assert globe.htmlElementLat == "lat"
    assert globe.htmlElementLng == "lng"
    assert globe.htmlElementAltitude == "altitude"
    assert globe.htmlElementKey == "storyId"
    assert globe.htmlElementOffsetX == "offsetX"
    assert globe.htmlElementOffsetY == "offsetY"
    assert globe.htmlElementPointerEvents == "auto"
    assert globe.htmlElementHidden is False
    assert globe.htmlElementScreenSide == "screenSide"
    assert globe.htmlElementScreenX == "screenX"
    assert globe.htmlElementScreenY == "screenY"
    assert globe.htmlElementTether == "tether"
    assert globe.htmlElementTetherColor == "tetherColor"
    assert globe.htmlElementTetherWidth == "tetherWidth"
    assert globe.htmlElementTetherAttach == "tetherAttach"


def test_update_html_elements_can_replace_overlay_children():
    replacement_child = html.Div("Replacement", id="replacement-overlay")

    globe = DashGlobe(id="html-overlays-replace").update_html_elements(
        data=[{"lat": 51.5, "lng": -0.1}],
        children=replacement_child,
        html_element_lat="lat",
        html_element_lng="lng",
    )

    assert globe.htmlElementsData == [{"lat": 51.5, "lng": -0.1}]
    assert globe.children == [replacement_child]
    assert globe.htmlElementLat == "lat"
    assert globe.htmlElementLng == "lng"
