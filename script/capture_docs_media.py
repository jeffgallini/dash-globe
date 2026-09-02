"""Capture PNG (and optional GIF) media from the local usage gallery for docs/README."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "docs" / "assets" / "examples"

EXAMPLES = [
    {
        "id": "basic-example-globe",
        "slug": "basic-points",
        "title": "Basic Points",
        "wait": 5,
        "gif": False,
    },
    {
        "id": "random-arcs-example-globe",
        "slug": "random-arcs",
        "title": "Random Arcs",
        "wait": 5,
        "gif": True,
    },
    {
        "id": "choropleth-countries-globe",
        "slug": "choropleth",
        "title": "Choropleth Countries",
        "wait": 6,
        "gif": False,
    },
    {
        "id": "large-dataset-globe",
        "slug": "large-dataset",
        "title": "Large Dataset via data_url",
        "wait": 8,
        "gif": True,
    },
    {
        "id": "airline-routes-globe",
        "slug": "airline-routes",
        "title": "Airline Routes",
        "wait": 6,
        "gif": False,
    },
    {
        "id": "day-night-cycle-globe",
        "slug": "day-night-cycle",
        "title": "Day Night Cycle",
        "wait": 6,
        "gif": True,
    },
    {
        "id": "clouds-globe",
        "slug": "clouds",
        "title": "Clouds",
        "wait": 6,
        "gif": True,
    },
    {
        "id": "situation-room-globe",
        "slug": "situation-room",
        "title": "Situation Room",
        "wait": 7,
        "gif": False,
    },
]


def _chrome(headless: bool = True) -> webdriver.Chrome:
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    os.environ["PATH"] = os.pathsep.join(
        part for part in path_parts if "Documents\\R" not in part and "Documents/R" not in part
    )
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,980")
    options.add_argument("--disk-cache-size=1")
    return webdriver.Chrome(options=options)


def _save_gif(frames: list[bytes], path: Path, duration_ms: int = 180) -> None:
    try:
        from PIL import Image
        import io
    except ImportError as exc:
        raise RuntimeError("Pillow is required to write GIF media. pip install pillow") from exc

    images = [Image.open(io.BytesIO(frame)).convert("RGB") for frame in frames]
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )


def capture_example(driver: webdriver.Chrome, example: dict, base_url: str) -> None:
    globe_id = example["id"]
    slug = example["slug"]
    wait = WebDriverWait(driver, 40)

    driver.get(f"{base_url}/#examples")
    time.sleep(1.0)
    button = wait.until(EC.presence_of_element_located((By.ID, f"{globe_id}-run-button")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
    time.sleep(0.4)
    button.click()

    mount = wait.until(EC.presence_of_element_located((By.ID, f"{globe_id}-mount")))
    wait.until(lambda d: len(mount.find_elements(By.TAG_NAME, "canvas")) > 0)
    time.sleep(example["wait"])

    png_path = ASSETS_DIR / f"{slug}.png"
    mount.screenshot(str(png_path))
    print(f"wrote {png_path.relative_to(ROOT)}")

    if example.get("gif"):
        frames = []
        for _ in range(10):
            frames.append(mount.screenshot_as_png)
            time.sleep(0.35)
        gif_path = ASSETS_DIR / f"{slug}.gif"
        _save_gif(frames, gif_path)
        print(f"wrote {gif_path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8050")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--only", nargs="*", help="Optional slug filters")
    args = parser.parse_args()

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    selected = EXAMPLES
    if args.only:
        wanted = set(args.only)
        selected = [example for example in EXAMPLES if example["slug"] in wanted]

    driver = _chrome(headless=not args.headed)
    try:
        driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
        for example in selected:
            print(f"capturing {example['title']}...")
            capture_example(driver, example, args.base_url.rstrip("/"))
        # Hero shot: reuse large-dataset or choropleth if present.
        hero_src = ASSETS_DIR / "large-dataset.png"
        if not hero_src.exists():
            hero_src = ASSETS_DIR / "choropleth.png"
        if hero_src.exists():
            hero_dst = ASSETS_DIR / "hero.png"
            hero_dst.write_bytes(hero_src.read_bytes())
            print(f"wrote {hero_dst.relative_to(ROOT)}")
    finally:
        driver.quit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
