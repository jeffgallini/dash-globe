from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "dash_globe"
PACKAGE_JSON_PATH = PACKAGE_ROOT / "package.json"
PACKAGE_INFO_PATH = PACKAGE_ROOT / "dash_globe" / "package-info.json"
PROJECT_TOML_PATH = PACKAGE_ROOT / "Project.toml"

PROJECT_TOML_VERSION_PATTERN = re.compile(r'(?m)^version\s*=\s*"(?P<version>[^"]+)"\s*$')
SEMVER_PATTERN = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _read_project_toml_version() -> str:
    project_toml = PROJECT_TOML_PATH.read_text(encoding="utf-8")
    match = PROJECT_TOML_VERSION_PATTERN.search(project_toml)
    if match is None:
        raise RuntimeError(f"Could not find a version entry in {PROJECT_TOML_PATH}")
    return match.group("version")


def _write_project_toml_version(version: str) -> None:
    project_toml = PROJECT_TOML_PATH.read_text(encoding="utf-8")
    updated = PROJECT_TOML_VERSION_PATTERN.sub(f'version = "{version}"', project_toml, count=1)
    PROJECT_TOML_PATH.write_text(updated, encoding="utf-8")


def read_version() -> str:
    package_json_version = _load_json(PACKAGE_JSON_PATH)["version"]
    package_info_version = _load_json(PACKAGE_INFO_PATH)["version"]
    project_toml_version = _read_project_toml_version()

    versions = {package_json_version, package_info_version, project_toml_version}
    if len(versions) != 1:
        raise RuntimeError(
            "Version metadata is out of sync across package.json, package-info.json, "
            f"and Project.toml: {sorted(versions)}"
        )

    return package_json_version


def write_version(version: str) -> str:
    if SEMVER_PATTERN.fullmatch(version) is None:
        raise ValueError(f"Expected a semantic version in X.Y.Z form, got {version!r}")

    package_json = _load_json(PACKAGE_JSON_PATH)
    package_json["version"] = version
    _write_json(PACKAGE_JSON_PATH, package_json)

    package_info = _load_json(PACKAGE_INFO_PATH)
    package_info["version"] = version
    _write_json(PACKAGE_INFO_PATH, package_info)

    _write_project_toml_version(version)
    return version


def bump_version(part: str) -> str:
    match = SEMVER_PATTERN.fullmatch(read_version())
    if match is None:
        raise RuntimeError("Current version must be in X.Y.Z form before it can be bumped")

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Unsupported bump target: {part}")

    return write_version(f"{major}.{minor}.{patch}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the dash_globe release version")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("current", help="Print the current version")
    subparsers.add_parser("check", help="Validate that all release metadata files are in sync")

    set_parser = subparsers.add_parser("set", help="Write an explicit version")
    set_parser.add_argument("version")

    bump_parser = subparsers.add_parser("bump", help="Increment a semantic version part")
    bump_parser.add_argument("part", choices=("major", "minor", "patch"))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "current":
            print(read_version())
        elif args.command == "check":
            print(read_version())
        elif args.command == "set":
            print(write_version(args.version))
        elif args.command == "bump":
            print(bump_version(args.part))
        else:
            parser.error(f"Unsupported command: {args.command}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
