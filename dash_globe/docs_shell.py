"""Dash Mantine AppShell layout for the dash-globe documentation gallery.

Imported by ``usage.py`` so the hosted example can look and navigate like
https://www.dash-mantine-components.com/ while globe builders stay in usage.py.
"""

from __future__ import annotations

from typing import Any, Callable

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


DOC_NAV_GROUPS = [
    {
        "label": "Documentation",
        "links": [
            {"path": "/getting-started", "label": "Usage", "icon": "tabler:rocket"},
            {"path": "/api-overview", "label": "Overview", "icon": "tabler:map"},
            {"path": "/helper-guides", "label": "Helper Guides", "icon": "tabler:book"},
            {"path": "/layer-reference", "label": "Layer Reference", "icon": "tabler:layers-intersect"},
            {"path": "/utilities", "label": "Utilities", "icon": "tabler:tools"},
            {"path": "/callbacks", "label": "Callbacks", "icon": "tabler:click"},
            {"path": "/api-reference", "label": "API Reference", "icon": "tabler:list-details"},
        ],
    },
    {
        "label": "Examples",
        "links": [
            {"path": "/examples", "label": "Live Examples", "icon": "tabler:layout-grid"},
        ],
    },
]

# Backward-compatible flat section list used by older tests/helpers.
DOC_SECTIONS = [
    (link["path"].strip("/").replace("/", "-"), link["label"])
    for group in DOC_NAV_GROUPS
    for link in group["links"]
]


def nav_icon(name: str):
    return DashIconify(icon=name, width=16)


def code_block(code: str, *, language: str = "python"):
    return dmc.CodeHighlight(code=code.strip("\n"), language=language, style={"borderRadius": 8})


def page_header(title: str, description: str, *, eyebrow: str | None = None):
    return dmc.Stack(
        [
            dmc.Text(eyebrow or "Dash Globe", size="sm", c="dimmed", tt="uppercase", fw=700, lts=1),
            dmc.Title(title, order=1),
            dmc.Text(description, c="dimmed", maw=820, style={"lineHeight": 1.7}),
        ],
        gap="xs",
        mb="xl",
    )


def doc_card(title: str, description: str, *children):
    return dmc.Paper(
        [
            dmc.Title(title, order=3, mb=6),
            dmc.Text(description, c="dimmed", mb="md", style={"lineHeight": 1.7}),
            *children,
        ],
        withBorder=True,
        radius="md",
        p="lg",
        shadow="xs",
    )


def build_badge_row(items):
    return dmc.Group(
        [dmc.Badge(item, variant="light", color="gray", size="lg", radius="sm") for item in items],
        gap="xs",
        mt="sm",
    )


def build_reference_table(headers, rows):
    return dmc.Table(
        striped=True,
        highlightOnHover=True,
        withTableBorder=True,
        withColumnBorders=False,
        verticalSpacing="sm",
        horizontalSpacing="md",
        children=[
            html.Thead(html.Tr([html.Th(header) for header in headers])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                dmc.Code(str(cell)) if index == 0 else cell,
                                style={"verticalAlign": "top", "lineHeight": 1.55},
                            )
                            for index, cell in enumerate(row)
                        ]
                    )
                    for row in rows
                ]
            ),
        ],
    )


def build_parameter_table(parameters):
    return build_reference_table(["Parameter", "Type", "Description"], parameters)


def build_note_list(items):
    if not items:
        return None
    return dmc.List(
        [dmc.ListItem(item) for item in items],
        size="sm",
        c="dimmed",
        spacing="xs",
        mt="sm",
    )


def build_api_reference_item(item):
    return dmc.Paper(
        [
            dmc.Group(
                [
                    dmc.Text(item["name"], fw=700),
                    dmc.Badge("API", variant="light", color="blue"),
                ],
                justify="space-between",
                mb="sm",
            ),
            code_block(item["signature"]),
            dmc.Text(item["summary"], c="dimmed", mt="md", style={"lineHeight": 1.7}),
            dmc.Space(h=12),
            build_parameter_table(item["parameters"]),
            dmc.Text("Returns", fw=700, mt="md", mb=4),
            dmc.Text(item["returns"], c="dimmed"),
            dmc.Text("Notes", fw=700, mt="md", mb=4) if item.get("notes") else None,
            build_note_list(item.get("notes") or []),
        ],
        withBorder=True,
        radius="md",
        p="lg",
        shadow="xs",
    )


def build_api_reference_list(items):
    return dmc.Stack([build_api_reference_item(item) for item in items], gap="md")


def build_helper_guide_item(item):
    return dmc.Paper(
        [
            dmc.Group(
                [
                    dmc.Title(item["title"], order=3),
                    dmc.Badge("Helper", variant="outline", color="gray"),
                ],
                justify="space-between",
                mb="xs",
            ),
            dmc.Text(item["description"], c="dimmed", style={"lineHeight": 1.7}),
            dmc.Group(
                [dmc.Badge(name, variant="light", color="blue") for name in item["related"]],
                gap=6,
                mt="sm",
                mb="md",
            ),
            code_block(item["code"]),
        ],
        withBorder=True,
        radius="md",
        p="lg",
        shadow="xs",
        id=f"helper-{item['title']}",
    )


def build_navbar(pathname: str, example_links: list[dict[str, str]]):
    groups = []
    for group in DOC_NAV_GROUPS:
        links = list(group["links"])
        if group["label"] == "Examples":
            links.extend(example_links)

        groups.append(
            dmc.Stack(
                [
                    dmc.Text(group["label"], size="xs", tt="uppercase", fw=700, c="dimmed", lts=1),
                    *[
                        dmc.NavLink(
                            label=link["label"],
                            href=link["path"],
                            active=pathname == link["path"]
                            or (link["path"] != "/examples" and pathname.startswith(link["path"] + "/")),
                            leftSection=nav_icon(link.get("icon", "tabler:circle")),
                            variant="light",
                        )
                        for link in links
                    ],
                ],
                gap=4,
            )
        )

    return dmc.AppShellNavbar(
        id="docs-navbar",
        children=[
            dmc.Stack(
                [
                    dmc.Text("On This Page", size="sm", fw=700),
                    dmc.Text(
                        "API guides and runnable react-globe.gl ports for Dash.",
                        size="sm",
                        c="dimmed",
                        style={"lineHeight": 1.55},
                    ),
                ],
                gap=4,
                mb="md",
            ),
            dmc.ScrollArea(
                dmc.Stack(groups, gap="lg"),
                h="calc(100vh - 140px)",
                type="hover",
            ),
        ],
        p="md",
    )


def build_header(version: str):
    return dmc.AppShellHeader(
        dmc.Group(
            [
                dmc.Group(
                    [
                        dmc.Burger(id="docs-burger", size="sm", hiddenFrom="sm", opened=False),
                        dmc.ThemeIcon(DashIconify(icon="tabler:globe", width=18), variant="light", color="blue", radius="md"),
                        dmc.Stack(
                            [
                                dmc.Text("Dash Globe", fw=700, lh=1.1),
                                dmc.Text("Interactive globe docs & examples", size="xs", c="dimmed", lh=1.1),
                            ],
                            gap=2,
                        ),
                    ],
                    gap="sm",
                ),
                dmc.Group(
                    [
                        dmc.Badge(f"v{version}", variant="light", color="gray"),
                        dmc.Anchor("react-globe.gl", href="https://github.com/vasturiano/react-globe.gl", target="_blank", size="sm"),
                        dmc.Anchor("GitHub", href="https://github.com/plotly/dash-globe", target="_blank", size="sm"),
                    ],
                    gap="md",
                    visibleFrom="sm",
                ),
            ],
            justify="space-between",
            h="100%",
            px="md",
        )
    )


def build_appshell(*, version: str, pathname: str, example_links: list[dict[str, str]], page_content):
    return dmc.MantineProvider(
        [
            dcc.Location(id="docs-location", refresh=False),
            dmc.AppShell(
                [
                    build_header(version),
                    build_navbar(pathname, example_links),
                    dmc.AppShellMain(
                        dmc.Container(
                            id="docs-page-content",
                            children=page_content,
                            size="lg",
                            px="md",
                            py="xl",
                        )
                    ),
                ],
                header={"height": 64},
                navbar={
                    "width": 300,
                    "breakpoint": "sm",
                    "collapsed": {"mobile": True},
                },
                padding="md",
                id="docs-appshell",
            ),
        ],
        forceColorScheme="light",
        theme={
            "primaryColor": "blue",
            "fontFamily": "Inter, Segoe UI, system-ui, sans-serif",
            "headings": {"fontFamily": "Inter, Segoe UI, system-ui, sans-serif"},
            "defaultRadius": "md",
        },
        id="docs-mantine-provider",
    )


def example_index_card(example: dict[str, Any]):
    return dmc.Card(
        [
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Badge(example["group"], variant="light", color="blue"),
                            dmc.Badge("Interactive", variant="outline", color="gray"),
                        ],
                        gap="xs",
                    ),
                    dmc.Title(example["title"], order=3),
                    dmc.Text(example["description"], c="dimmed", size="sm", style={"lineHeight": 1.6}),
                    dmc.Anchor("Open example →", href=example["path"], size="sm", fw=600),
                ],
                gap="sm",
            )
        ],
        withBorder=True,
        shadow="xs",
        radius="md",
        padding="lg",
    )


def build_examples_index(examples: list[dict[str, Any]]):
    groups: dict[str, list[dict[str, Any]]] = {}
    for example in examples:
        groups.setdefault(example["group"], []).append(example)

    sections = []
    for group_name, group_examples in groups.items():
        sections.append(
            dmc.Stack(
                [
                    dmc.Title(group_name, order=2),
                    dmc.SimpleGrid(
                        [example_index_card(example) for example in group_examples],
                        cols={"base": 1, "sm": 2},
                        spacing="md",
                    ),
                ],
                gap="md",
            )
        )

    return dmc.Stack(
        [
            page_header(
                "Live Examples",
                "Runnable ports of upstream react-globe.gl demos plus package-specific helpers. "
                "Open one example at a time so heavier scenes stay responsive.",
                eyebrow="Examples",
            ),
            *sections,
            html.Div(id="gallery-footer"),
        ],
        gap="xl",
        id="examples",
    )


def build_example_page(
    example: dict[str, Any],
    *,
    stage: Any,
    event_panel: Any | None = None,
):
    tabs = [
        dmc.TabsTab("Demo", value="demo"),
        dmc.TabsTab("Code", value="code"),
    ]
    panels = [
        dmc.TabsPanel(
            dmc.Stack(
                [
                    dmc.Paper(stage, withBorder=True, radius="md", p="sm", shadow="xs"),
                    event_panel,
                ],
                gap="md",
            ),
            value="demo",
            pt="md",
        ),
        dmc.TabsPanel(code_block(example["code"]), value="code", pt="md"),
    ]

    return dmc.Stack(
        [
            dmc.Anchor("← All examples", href="/examples", size="sm", mb=4),
            page_header(example["title"], example["description"], eyebrow=example["group"]),
            dmc.Alert(
                "Only the active example page mounts a WebGL globe. Navigate away to release it.",
                title="Performance tip",
                color="blue",
                variant="light",
            ),
            dmc.Tabs(
                [
                    dmc.TabsList(tabs),
                    *panels,
                ],
                value="demo",
                variant="outline",
            ),
        ],
        gap="md",
        id="examples",
    )


def build_getting_started_page(*, installation_code: str, quick_start_code: str):
    return dmc.Stack(
        [
            page_header(
                "Usage",
                "Dash Globe is a Dash wrapper around react-globe.gl. Create a component, configure the scene, "
                "add data layers, then map your fields with layer accessors.",
                eyebrow="Getting Started",
            ),
            dmc.SimpleGrid(
                [
                    doc_card(
                        "Installation",
                        "Install the package, import dash_globe, and start with the chainable DashGlobe helper.",
                        code_block(installation_code),
                    ),
                    doc_card(
                        "Basic Usage",
                        "A minimal app only needs a Dash layout and a single globe configured with points, textures, and camera position.",
                        code_block(quick_start_code),
                    ),
                ],
                cols={"base": 1, "md": 2},
                spacing="md",
            ),
            doc_card(
                "What the Package Covers",
                "The wrapper focuses on the JSON-serialisable features from react-globe.gl and exposes them through Python helpers plus direct Dash props.",
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
        ],
        gap="lg",
        id="getting-started",
    )


def build_appshell_static_layout(*, version: str, example_links: list[dict[str, str]], initial_page):
    """Initial layout shell; page body is swapped by the docs-location callback."""
    return build_appshell(
        version=version,
        pathname="/getting-started",
        example_links=example_links,
        page_content=initial_page,
    )
