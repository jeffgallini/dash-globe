import json
from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.resolve()
package = json.loads((here / "package.json").read_text(encoding="utf-8"))
long_description = (here / "README.md").read_text(encoding="utf-8")

distribution_name = package["name"]
package_name = distribution_name.replace(" ", "_").replace("-", "_")

setup(
    name=distribution_name,
    version=package["version"],
    author="Jeff Gallini",
    author_email="gallinij@gmail.com",
    url="https://github.com/jeffgallini/dash-globe",
    project_urls={
        "Source": "https://github.com/jeffgallini/dash-globe",
        "Issues": "https://github.com/jeffgallini/dash-globe/issues",
    },
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    package_data={
        package_name: [
            "*.js",
            "*.js.map",
            "*.txt",
            "metadata.json",
            "package-info.json",
        ]
    },
    license=package["license"],
    license_files=("LICENSE",),
    description=package.get("description", package_name),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["dash>=2"],
    python_requires=">=3.8",
    keywords=["dash", "plotly", "globe", "react-globe.gl", "data visualization"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Dash",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
