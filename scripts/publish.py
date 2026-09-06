"""Validate, build, and publish the current PyDeskUI version to PyPI."""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_INIT = ROOT / "src" / "pydeskui" / "__init__.py"
CHANGELOG = ROOT / "CHANGELOG.md"
REPOSITORY_URLS = {
    "pypi": "https://upload.pypi.org/legacy/",
    "testpypi": "https://test.pypi.org/legacy/",
}


def fail(message: str) -> None:
    raise SystemExit(f"Release blocked: {message}")


def run(*command: str, env: dict[str, str] | None = None) -> None:
    print(f"\n+ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def capture(*command: str) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def project_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def package_version() -> str:
    match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        PACKAGE_INIT.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        fail(f"could not find __version__ in {PACKAGE_INIT.relative_to(ROOT)}")
    return match.group(1)


def check_release_metadata(version: str) -> None:
    package = package_version()
    if package != version:
        fail(f"pyproject.toml is {version}, but pydeskui.__version__ is {package}")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    heading = re.search(
        rf"^##\s+{re.escape(version)}(?:\s+\(([^)]*)\))?\s*$",
        changelog,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if heading is None:
        fail(f"CHANGELOG.md has no section for {version}")
    if heading.group(1) and "unreleased" in heading.group(1).lower():
        fail(f"CHANGELOG.md still marks {version} as unreleased")


def check_repository() -> None:
    if capture("git", "branch", "--show-current") != "main":
        fail("releases must run from the main branch")
    status = capture("git", "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        fail("the Git working tree is not clean; commit or stash changes first")


def check_dependencies() -> None:
    required = ("babel", "build", "keyring", "mypy", "ruff", "sphinx", "twine")
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        fail(
            "missing release dependencies "
            f"({', '.join(missing)}); run: python -m pip install -e '.[dev,docs]'"
        )


def upload_environment(repository: str) -> dict[str, str]:
    environment = dict(os.environ)
    environment.setdefault("TWINE_USERNAME", "__token__")
    environment["TWINE_NON_INTERACTIVE"] = "1"
    if environment.get("TWINE_PASSWORD"):
        return environment

    try:
        import keyring

        token = keyring.get_password(REPOSITORY_URLS[repository], "__token__")
    except Exception as error:  # pragma: no cover - depends on the OS credential backend
        fail(f"could not read the system keyring: {error}")
    if not token:
        fail(
            "no PyPI token found; configure it with: "
            f"keyring set {REPOSITORY_URLS[repository]} __token__"
        )
    environment["TWINE_PASSWORD"] = token
    return environment


def clean_build_directories() -> None:
    for directory in (ROOT / "build", ROOT / "dist"):
        if directory.exists():
            shutil.rmtree(directory)


def verify_source() -> None:
    run(sys.executable, "scripts/compile_catalogs.py")
    if capture("git", "status", "--porcelain=v1", "--untracked-files=all"):
        fail("source generation changed the working tree; review and commit it before publishing")
    run(sys.executable, "-m", "pytest")
    run(sys.executable, "-m", "ruff", "check", "src", "tests", "examples", "scripts")
    run(sys.executable, "-m", "mypy")
    run(sys.executable, "-m", "sphinx", "-W", "-b", "html", "docs", "build/docs")


def build_distributions() -> list[Path]:
    clean_build_directories()
    run(sys.executable, "-m", "build")
    distributions = sorted((ROOT / "dist").glob("*"))
    if len(distributions) != 2 or {path.suffix for path in distributions} != {".whl", ".gz"}:
        names = ", ".join(path.name for path in distributions) or "none"
        fail(f"expected one wheel and one source archive, found: {names}")
    run(sys.executable, "-m", "twine", "check", *(str(path) for path in distributions))
    run(sys.executable, "scripts/check_wheel.py")
    return distributions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        choices=tuple(REPOSITORY_URLS),
        default="pypi",
        help="package index to publish to (default: pypi)",
    )
    parser.add_argument("--dry-run", action="store_true", help="build and verify without uploading")
    parser.add_argument("--yes", action="store_true", help="upload without the final confirmation")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    check_dependencies()
    version = project_version()
    check_release_metadata(version)
    check_repository()
    environment = None if args.dry_run else upload_environment(args.repository)

    print(f"Preparing PyDeskUI {version} for {args.repository}.")
    verify_source()
    distributions = build_distributions()

    if args.dry_run:
        print(f"\nDry run passed for PyDeskUI {version}; nothing was uploaded.")
        return

    if not args.yes:
        answer = input(f"\nUpload PyDeskUI {version} to {args.repository}? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            raise SystemExit("Upload cancelled.")

    run(
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--repository",
        args.repository,
        *(str(path) for path in distributions),
        env=environment,
    )
    print(f"\nPublished PyDeskUI {version} to {args.repository}.")


if __name__ == "__main__":
    main()
