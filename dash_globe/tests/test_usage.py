import importlib.util
import time

import pytest
import usage


HAS_DASH_TESTING_EXTRAS = importlib.util.find_spec("multiprocess") is not None


def _walk_components(component):
    if isinstance(component, (list, tuple)):
        for item in component:
            yield from _walk_components(item)
        return

    if component is None or not hasattr(component, "children"):
        return

    yield component
    yield from _walk_components(component.children)


def test_demo_debug_toggle_defaults_off(monkeypatch):
    monkeypatch.delenv(usage.DEBUG_ENV_VAR, raising=False)

    assert usage.is_demo_debug_enabled() is False
    assert usage.get_demo_run_kwargs()["debug"] is False


def test_demo_debug_toggle_accepts_truthy_env(monkeypatch):
    monkeypatch.setenv(usage.DEBUG_ENV_VAR, "1")

    assert usage.is_demo_debug_enabled() is True
    assert usage.get_demo_run_kwargs()["debug"] is True


def test_gallery_footer_uses_html_instead_of_markdown():
    footer = usage.build_gallery_footer()

    assert footer.id == "gallery-footer"
    assert footer.__class__.__name__ == "P"
    assert not any(component.__class__.__name__ == "Markdown" for component in _walk_components(usage.app.layout))


def test_choropleth_hover_callback_no_longer_rewrites_polygons():
    assert not any(
        "choropleth-countries-globe.polygonsData" in callback_id
        for callback_id in usage.app.callback_map
    )
    assert any(
        "choropleth-countries-event.children" in callback_id
        for callback_id in usage.app.callback_map
    )


def test_hollow_globe_gallery_entry_uses_double_sided_polygon_material():
    assert "hollow-globe" in usage.GLOBE_IDS
    assert "hollow-globe" in usage.GLOBE_BUILDERS
    assert "lambert_material" in usage.HOLLOW_GLOBE_EXAMPLE_CODE

    globe = usage.build_hollow_globe()

    assert globe.showGlobe is False
    assert globe.showAtmosphere is False
    assert globe.polygonCapMaterial == {"type": "lambert", "color": "darkslategrey", "side": "double"}
    assert globe.polygonStrokeColor is False


def test_day_night_cycle_gallery_entry_uses_new_helper():
    assert "day-night-cycle-globe" in usage.GLOBE_IDS
    assert "day-night-cycle-globe" in usage.GLOBE_BUILDERS
    assert "update_day_night_cycle" in usage.DAY_NIGHT_CYCLE_EXAMPLE_CODE

    globe = usage.build_day_night_cycle_globe()

    assert globe.backgroundImageUrl == usage.dash_globe.PRESETS.NIGHT_SKY
    assert globe.showAtmosphere is False
    assert globe.dayNightCycle is True
    assert globe.dayNightCycleDayImageUrl == usage.dash_globe.PRESETS.EARTH
    assert globe.dayNightCycleNightImageUrl == usage.dash_globe.PRESETS.EARTH_NIGHT
    assert globe.dayNightCycleTime == "2026-04-17T12:00:00Z"
    assert globe.dayNightCycleMinutesPerSecond == 60


def test_random_rings_gallery_entry_uses_ring_color_interpolator_helper():
    assert "random-rings-example-globe" in usage.GLOBE_IDS
    assert "random-rings-example-globe" in usage.GLOBE_BUILDERS
    assert "ring_color_interpolator" in usage.RANDOM_RINGS_EXAMPLE_CODE

    globe = usage.build_random_rings_example_globe()

    assert globe.backgroundColor == "#000000"
    assert globe.globeImageUrl == usage.dash_globe.PRESETS.EARTH_NIGHT
    assert globe.ringsData == usage.RANDOM_RINGS_EXAMPLE_DATA
    assert globe.ringColor == usage.dash_globe.ring_color_interpolator("#ff6432")
    assert globe.ringMaxRadius == "maxR"
    assert globe.ringPropagationSpeed == "propagationSpeed"
    assert globe.ringRepeatPeriod == "repeatPeriod"


def test_emit_arcs_on_click_gallery_entry_uses_event_helper_and_transient_store():
    assert usage.EMIT_ARCS_GLOBE_ID in usage.GLOBE_IDS
    assert usage.EMIT_ARCS_GLOBE_ID in usage.GLOBE_BUILDERS
    assert "event_coords" in usage.EMIT_ARCS_ON_CLICK_EXAMPLE_CODE
    assert "dcc.Interval" in usage.EMIT_ARCS_ON_CLICK_EXAMPLE_CODE

    stage = usage.build_emit_arcs_on_click_globe()
    globe, store, interval = stage.children

    assert globe.id == usage.EMIT_ARCS_GLOBE_ID
    assert globe.backgroundColor == "#000000"
    assert globe.globeImageUrl == usage.dash_globe.PRESETS.EARTH_NIGHT
    assert globe.arcStartLat == "startLat"
    assert globe.arcStartLng == "startLng"
    assert globe.arcEndLat == "endLat"
    assert globe.arcEndLng == "endLng"
    assert globe.arcColor == "color"
    assert globe.arcAltitude == "altitude"
    assert globe.arcStroke == "stroke"
    assert globe.arcDashLength == "dashLength"
    assert globe.arcDashGap == "dashGap"
    assert globe.arcDashInitialGap == "dashInitialGap"
    assert globe.arcDashAnimateTime == "dashAnimateTime"
    assert globe.ringColor == usage.dash_globe.ring_color_interpolator("rgb(255, 100, 50)")
    assert globe.ringMaxRadius == usage.EMIT_ARCS_RINGS_MAX_R
    assert globe.ringPropagationSpeed == usage.EMIT_ARCS_RING_PROPAGATION_SPEED
    assert globe.ringRepeatPeriod == usage.EMIT_ARCS_RING_REPEAT_PERIOD
    assert store.id == usage.EMIT_ARCS_STORE_ID
    assert store.data == usage.build_emit_arcs_state()
    assert interval.id == usage.EMIT_ARCS_INTERVAL_ID
    assert interval.disabled is True


def test_emit_arcs_helpers_emit_and_prune_transient_arc_state():
    first_click_data = {
        "layer": "globe",
        "coords": {"lat": 12.5, "lng": -99.25},
    }
    second_click_data = {
        "layer": "globe",
        "coords": {"lat": 33.0, "lng": 18.25},
    }

    state_after_first = usage.append_emit_arc_click(None, first_click_data, now_ms=1_000)
    first_state_now, first_arcs_now, first_rings_now = usage.build_emit_arcs_snapshot(state_after_first, now_ms=1_000)

    assert first_state_now["previousCoords"] == {"lat": 12.5, "lng": -99.25}
    assert first_arcs_now == []
    assert first_rings_now == [{"lat": 12.5, "lng": -99.25}]

    state = usage.append_emit_arc_click(state_after_first, second_click_data, now_ms=2_000)
    state_now, arcs_now, rings_now = usage.build_emit_arcs_snapshot(state, now_ms=2_000)

    assert state_now["previousCoords"] == {"lat": 33.0, "lng": 18.25}
    assert arcs_now == [
        {
            "startLat": 12.5,
            "startLng": -99.25,
            "endLat": 33.0,
            "endLng": 18.25,
            "color": "rgba(255, 140, 0, 0.25)",
            "altitude": 0.2,
            "stroke": 0.12,
            "dashLength": 1,
            "dashGap": 0,
            "dashInitialGap": 0,
            "dashAnimateTime": 0,
        },
        {
            "startLat": 12.5,
            "startLng": -99.25,
            "endLat": 33.0,
            "endLng": 18.25,
            "color": "darkOrange",
            "altitude": 0.2,
            "stroke": 0.22,
            "dashLength": usage.EMIT_ARCS_ARC_REL_LEN,
            "dashGap": 2,
            "dashInitialGap": 1.0,
            "dashAnimateTime": 0,
        }
    ]
    assert rings_now == [{"lat": 12.5, "lng": -99.25}]

    _, arcs_midflight, rings_midflight = usage.build_emit_arcs_snapshot(state, now_ms=2_500)
    assert len(arcs_midflight) == 2
    assert arcs_midflight[1]["dashInitialGap"] == 0.5
    assert rings_midflight == []

    _, arcs_arriving, rings_arriving = usage.build_emit_arcs_snapshot(state, now_ms=3_000)
    assert len(arcs_arriving) == 2
    assert arcs_arriving[1]["dashInitialGap"] == 0.0
    assert rings_arriving == [{"lat": 33.0, "lng": 18.25}]

    state_complete, arcs_complete, rings_complete = usage.build_emit_arcs_snapshot(state, now_ms=4_001)
    assert arcs_complete == []
    assert rings_complete == []
    assert state_complete["arcs"] == []
    assert state_complete["rings"] == []


def test_world_cities_gallery_entry_uses_label_helper():
    assert "world-cities-globe" in usage.GLOBE_IDS
    assert "world-cities-globe" in usage.GLOBE_BUILDERS
    assert "label_dot_radius" in usage.WORLD_CITIES_EXAMPLE_CODE

    globe = usage.build_world_cities_globe()

    assert globe.backgroundImageUrl == usage.dash_globe.PRESETS.NIGHT_SKY
    assert globe.globeImageUrl == usage.dash_globe.PRESETS.EARTH_NIGHT
    assert globe.labelsData == usage.WORLD_CITIES
    assert globe.labelLabel == "labelHtml"
    assert globe.labelLat == "lat"
    assert globe.labelLng == "lng"
    assert globe.labelText == "name"
    assert globe.labelSize == "size"
    assert globe.labelColor == "color"
    assert globe.labelIncludeDot is True
    assert globe.labelDotRadius == "dotRadius"
    assert globe.labelResolution == 2


def test_submarine_cables_gallery_entry_uses_path_helper():
    assert "submarine-cables-globe" in usage.GLOBE_IDS
    assert "submarine-cables-globe" in usage.GLOBE_BUILDERS
    assert "update_paths" in usage.SUBMARINE_CABLES_EXAMPLE_CODE
    assert "path_points" in usage.SUBMARINE_CABLES_EXAMPLE_CODE

    globe = usage.build_submarine_cables_globe()

    assert globe.backgroundImageUrl == usage.dash_globe.PRESETS.NIGHT_SKY
    assert globe.globeImageUrl == usage.dash_globe.PRESETS.EARTH_DARK
    assert globe.bumpImageUrl == usage.dash_globe.PRESETS.EARTH_TOPOGRAPHY
    assert globe.pathsData == usage.SUBMARINE_CABLE_PATHS
    assert globe.pathLabel == "labelHtml"
    assert globe.pathPoints == "coords"
    assert globe.pathPointLat == "lat"
    assert globe.pathPointLng == "lng"
    assert globe.pathColor == "color"
    assert globe.pathDashLength == 0.1
    assert globe.pathDashGap == 0.008
    assert globe.pathDashAnimateTime == 12000
    assert globe.pathTransitionDuration == 0


def test_tiles_gallery_entry_uses_tile_material_helper():
    assert "tiles-example-globe" in usage.GLOBE_IDS
    assert "tiles-example-globe" in usage.GLOBE_BUILDERS
    assert "tile_material" in usage.TILES_EXAMPLE_CODE
    assert "lambert_material" in usage.TILES_EXAMPLE_CODE

    globe = usage.build_tiles_example_globe()

    assert globe.backgroundColor == "#000000"
    assert globe.tilesData == usage.TILES_EXAMPLE_DATA
    assert globe.tileLabel == "labelHtml"
    assert globe.tileLat == "lat"
    assert globe.tileLng == "lng"
    assert globe.tileWidth == usage.TILES_EXAMPLE_TILE_WIDTH - usage.TILE_MARGIN
    assert globe.tileHeight == usage.TILES_EXAMPLE_TILE_HEIGHT - usage.TILE_MARGIN
    assert globe.tileMaterial == "material"


def test_heatmap_gallery_entry_uses_single_dataset_helper():
    assert "heatmap-example-globe" in usage.GLOBE_IDS
    assert "heatmap-example-globe" in usage.GLOBE_BUILDERS
    assert "add_heatmap" in usage.HEATMAP_EXAMPLE_CODE

    globe = usage.build_heatmap_example_globe()

    assert globe.enablePointerInteraction is False
    assert globe.globeImageUrl == usage.dash_globe.PRESETS.EARTH_DARK
    assert globe.heatmapsData == [usage.HEATMAP_EXAMPLE_DATA]
    assert globe.heatmapPointLat == "lat"
    assert globe.heatmapPointLng == "lng"
    assert globe.heatmapPointWeight == "weight"
    assert globe.heatmapTopAltitude == 0.7
    assert globe.heatmapsTransitionDuration == 3000


def test_situation_room_gallery_entry_uses_html_element_helper_and_side_selection():
    assert usage.SITUATION_ROOM_GLOBE_ID in usage.GLOBE_IDS
    assert usage.SITUATION_ROOM_GLOBE_ID in usage.GLOBE_BUILDERS
    assert "html.Img" in usage.SITUATION_ROOM_EXAMPLE_CODE
    assert "forward_angle" in usage.SITUATION_ROOM_EXAMPLE_CODE
    assert "update_html_elements" in usage.SITUATION_ROOM_EXAMPLE_CODE
    assert "html_element_tether" in usage.SITUATION_ROOM_EXAMPLE_CODE
    assert "currentView" in usage.SITUATION_ROOM_EXAMPLE_CODE
    assert usage.SITUATION_ROOM_NEWS_PAYLOAD["count"] == len(usage.SITUATION_ROOM_STORIES) == 20
    assert any(
        story["location"]["name"] == "Global" and (story["location"]["lat"] != 0 or story["location"]["lng"] != 0)
        for story in usage.SITUATION_ROOM_STORIES
    )

    stage_container = usage.build_globe_stage(usage.SITUATION_ROOM_GLOBE_ID)
    stage = usage.build_situation_room_globe()
    globe, selection_store, header, status = stage.children
    snapshots = usage.SITUATION_ROOM_VISIBLE_SNAPSHOTS

    assert stage_container.style["minHeight"] == usage.SITUATION_ROOM_STAGE_MIN_HEIGHT
    assert globe.id == usage.SITUATION_ROOM_GLOBE_ID
    assert selection_store.id == usage.SITUATION_ROOM_SELECTION_STORE_ID
    assert selection_store.data == usage.build_situation_room_selection_signature(snapshots)
    assert globe.pointsData == usage.SITUATION_ROOM_STORY_POINTS
    assert len(globe.pointsData) == len(usage.SITUATION_ROOM_STORIES)
    assert globe.currentViewReportInterval == usage.SITUATION_ROOM_CURRENT_VIEW_REPORT_INTERVAL
    assert globe.ringsData == [snapshot["ring"] for snapshot in snapshots]
    assert globe.htmlElementsData == [snapshot["overlay"] for snapshot in snapshots]
    assert len(globe.children) == len(snapshots)
    first_card = globe.children[0]
    assert first_card.children[1].src == snapshots[0]["story"]["image"]
    assert first_card.children[2].children.href == snapshots[0]["story"]["url"]
    assert first_card.children[4].children[0].children == snapshots[0]["story"]["source"]
    assert first_card.children[5].children == usage.format_demo_timestamp(snapshots[0]["story"]["publishedAt"])
    assert header.id == usage.SITUATION_ROOM_HEADER_ID
    assert status.id == usage.SITUATION_ROOM_STATUS_ID


def test_situation_room_visible_story_selection_chooses_two_most_forward_stories():
    snapshots = usage.build_situation_room_visible_story_snapshots(cycle_step=0)
    candidates = usage.build_situation_room_story_candidates(usage.build_situation_room_live_view(0))

    assert len(snapshots) <= 2
    assert [snapshot["side"] for snapshot in snapshots] == sorted(
        [snapshot["side"] for snapshot in snapshots],
        key=usage.SITUATION_ROOM_SIDE_ORDER.index,
    )
    assert len(candidates) >= len(snapshots)

    expected_story_ids = [
        snapshot["story"]["id"]
        for snapshot in candidates[: len(snapshots)]
    ]
    actual_story_ids = sorted(snapshot["story"]["id"] for snapshot in snapshots)
    assert actual_story_ids == sorted(expected_story_ids)

    for snapshot in snapshots:
        assert usage.is_situation_room_story_visible(snapshot["story"], usage.build_situation_room_live_view(0))
        assert snapshot["overlay"]["screenSide"] == snapshot["side"]
        assert snapshot["overlay"]["tether"] is True
        assert "forwardAngle" in snapshot
        assert "relativeLng" in snapshot


def test_situation_room_scene_callback_refreshes_tethered_cards():
    snapshots = usage.build_situation_room_visible_story_snapshots(cycle_step=0)

    signature, rings, html_elements, card_children, header, status = usage.sync_situation_room_scene(
        None,
        None,
    )

    assert signature == usage.build_situation_room_selection_signature(snapshots)
    assert rings == [snapshot["ring"] for snapshot in snapshots]
    assert html_elements == [snapshot["overlay"] for snapshot in snapshots]
    assert len(card_children) == len(snapshots)
    assert header.children[0].children == "Situation Room"
    assert "Monitoring" in status.children[0].children


def test_situation_room_story_selection_updates_as_auto_rotate_view_moves():
    cycle_zero = usage.build_situation_room_visible_story_snapshots(cycle_step=0)
    cycle_later = usage.build_situation_room_visible_story_snapshots(cycle_step=40)
    live_view = usage.build_situation_room_live_view(40)

    assert live_view["lng"] != usage.SITUATION_ROOM_INITIAL_VIEW["lng"]
    assert [snapshot["story"]["id"] for snapshot in cycle_zero] != [
        snapshot["story"]["id"] for snapshot in cycle_later
    ]


def test_situation_room_scene_callback_tracks_manual_current_view():
    manual_view = {"lat": 35, "lng": 128, "altitude": 2.15}
    expected = usage.build_situation_room_visible_story_snapshots(current_view=manual_view, cycle_step=0)

    signature, rings, html_elements, card_children, _header, _status = usage.sync_situation_room_scene(
        manual_view,
        None,
    )

    assert signature == usage.build_situation_room_selection_signature(expected)
    assert rings == [snapshot["ring"] for snapshot in expected]
    assert html_elements == [snapshot["overlay"] for snapshot in expected]
    assert len(card_children) == len(expected)
    assert [child.children[2].children.children for child in card_children] == [
        snapshot["story"]["title"] for snapshot in expected
    ]


def test_situation_room_scene_callback_skips_rebuild_when_selection_is_unchanged():
    snapshots = usage.build_situation_room_visible_story_snapshots(cycle_step=0)
    signature = usage.build_situation_room_selection_signature(snapshots)

    result = usage.sync_situation_room_scene(None, signature)

    assert result == (
        usage.no_update,
        usage.no_update,
        usage.no_update,
        usage.no_update,
        usage.no_update,
        usage.no_update,
    )


def test_usage_page_replaces_old_custom_examples_with_reference_docs():
    assert "city-globe" not in usage.GLOBE_IDS
    assert "route-globe" not in usage.GLOBE_IDS
    assert "region-globe" not in usage.GLOBE_IDS
    assert "density-globe" not in usage.GLOBE_IDS
    assert usage.QUICK_START_CODE.startswith("from dash import Dash, html")
    assert any("Usage" in str(getattr(component, "children", "")) for component in _walk_components(usage.app.layout))
    assert any("Overview" in str(getattr(component, "children", "")) for component in _walk_components(usage.app.layout))
    assert any("Helper Guides" in str(getattr(component, "children", "")) for component in _walk_components(usage.app.layout))
    assert any("API Reference" in str(getattr(component, "children", "")) for component in _walk_components(usage.app.layout))
    assert any("On This Page" in str(getattr(component, "children", "")) for component in _walk_components(usage.app.layout))


@pytest.mark.skipif(not HAS_DASH_TESTING_EXTRAS, reason="dash[testing] extras are not installed")
def test_render_component_gallery(dash_duo):
    from dash.testing.application_runners import import_app
    from selenium.webdriver import ActionChains

    app = import_app("usage")
    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#examples h2", "Live Examples")

    assert len(dash_duo.find_elements("canvas")) == 0

    dash_duo.find_element("#basic-example-globe-run-button").click()
    dash_duo.wait_for_element("#basic-example-globe canvas")

    assert dash_duo.find_element("#basic-example-globe canvas")
    assert len(dash_duo.find_elements("canvas")) == 1

    dash_duo.find_element("#choropleth-countries-globe-run-button").click()
    dash_duo.wait_for_element("#choropleth-countries-globe canvas")
    dash_duo.wait_for_element("#gallery-footer")

    assert len(dash_duo.find_elements("canvas")) == 1
    assert dash_duo.find_element("#choropleth-countries-globe canvas")

    choropleth_event = "#choropleth-countries-event"
    placeholder_text = "Click Run to mount this globe, then hover a country to inspect the latest hover payload."
    canvas = dash_duo.find_element("#choropleth-countries-globe canvas")
    dash_duo.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", canvas)
    canvas_rect = canvas.rect

    candidate_offsets = [
        (int(canvas_rect["width"] * x_ratio), int(canvas_rect["height"] * y_ratio))
        for x_ratio, y_ratio in [
            (0.32, 0.32),
            (0.45, 0.28),
            (0.58, 0.32),
            (0.66, 0.42),
            (0.52, 0.46),
            (0.38, 0.50),
        ]
    ]

    hovered_payload = None
    for x_offset, y_offset in candidate_offsets:
        ActionChains(dash_duo.driver).move_to_element_with_offset(canvas, x_offset, y_offset).perform()
        time.sleep(0.35)
        hovered_payload = dash_duo.find_element(choropleth_event).text
        if hovered_payload != placeholder_text and '"layer": "polygon"' in hovered_payload:
            break

    assert hovered_payload is not None
    assert hovered_payload != placeholder_text
    assert '"layer": "polygon"' in hovered_payload

    time.sleep(0.9)
    assert dash_duo.find_element(choropleth_event).text == hovered_payload
