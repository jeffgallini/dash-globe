"""Public Python API for the Dash Globe package.

The package exposes a chainable :class:`DashGlobe` wrapper together with a
small set of serialisable helpers for common textures, materials, interaction
payloads, and animated ring colors.
"""

from __future__ import print_function as _

import os as _os
import sys as _sys
import json

import dash as _dash

# noinspection PyUnresolvedReferences
from ._imports_ import *
from ._imports_ import __all__

if not hasattr(_dash, '__plotly_dash') and not hasattr(_dash, 'development'):
    print('Dash was not successfully imported. '
          'Make sure you don\'t have a file '
          'named \n"dash.py" in your current directory.', file=_sys.stderr)
    _sys.exit(1)

_basepath = _os.path.dirname(__file__)
_filepath = _os.path.abspath(_os.path.join(_basepath, 'package-info.json'))
with open(_filepath) as f:
    package = json.load(f)

package_name = package['name'].replace(' ', '_').replace('-', '_')
__version__ = package['version']

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_this_module = _sys.modules[__name__]

async_resources = ["DashGlobe",]

_js_dist = []

_js_dist.extend(
    [
        {
            "relative_package_path": "async-{}.js".format(async_resource),
            "external_url": (
                "https://unpkg.com/{0}@{2}"
                "/{1}/async-{3}.js"
            ).format(package_name, __name__, __version__, async_resource),
            "namespace": package_name,
            "async": True,
        }
        for async_resource in async_resources
    ]
)

# Vendor chunks split out of the physical DashGlobe bundle for parallel download
# and long-term browser caching. Webpack loads these on demand; they are registered
# so Dash serves them from the component suite path.
_vendor_async_chunks = ("three", "h3", "globe-vendor")
_js_dist.extend(
    [
        {
            "relative_package_path": "async-{}.js".format(chunk_name),
            "namespace": package_name,
            "async": True,
        }
        for chunk_name in _vendor_async_chunks
    ]
)

_js_dist.extend(
    [
        {
            'relative_package_path': 'dash_globe.min.js',
    
            'namespace': package_name
        },
    ]
)

_css_dist = []


for _component in __all__:
    setattr(locals()[_component], '_js_dist', _js_dist)
    setattr(locals()[_component], '_css_dist', _css_dist)

from .globe import DashGlobe  # noqa: E402
from .colors import ring_color_interpolator  # noqa: E402
from .data import data_url, is_data_url  # noqa: E402
from .events import event_coords  # noqa: E402
from .materials import lambert_material, material_spec  # noqa: E402
from .presets import PRESETS  # noqa: E402

__all__ = [
    "DashGlobe",
    "PRESETS",
    "data_url",
    "is_data_url",
    "event_coords",
    "ring_color_interpolator",
    "material_spec",
    "lambert_material",
]
