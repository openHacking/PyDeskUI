# Contributing

PyDeskUI development requires Python 3.13+ linked to Tcl/Tk 9. A virtual
environment inherits Tcl/Tk from its base interpreter; it does not install or
replace Tk. Standalone Python builds must bundle Tcl/Tk 9 and link `_tkinter`
against that major version.

## Development setup

From the repository root, create `.venv` once and activate it on macOS/Linux:

```sh
python -m venv .venv
source .venv/bin/activate
python -c "import sys; print(sys.executable)"
python -m tkinter
```

The interpreter path should be inside this project's `.venv`. Close the Tk test
window to continue. In each new terminal, activate the existing environment
instead of creating it again. On Windows PowerShell, activate it with
`.\.venv\Scripts\Activate.ps1`. Run `deactivate` to leave the environment.

Do not overwrite an existing environment using a different Python installation.
Doing so can leave interpreter links and `pyvenv.cfg` inconsistent, causing
`ensurepip` or `encodings` import failures. If the environment is broken, inspect
`.venv/pyvenv.cfg` and its interpreter links first. To recreate it, deactivate
it, move it to a backup location, create a new `.venv` with the intended
Tk-enabled interpreter, and reinstall dependencies. Keep the backup for
recovery; virtual environments are not portable after moving. Use a Python
installed at a stable location rather than under `/tmp`.

The `.venv/` directory is ignored by Git; do not commit or copy it between
projects. Activation is optional when calling its interpreter directly, for
example `.venv/bin/python -m pytest` on macOS/Linux.

## Install and verify

Install development dependencies into the activated environment, then run the
project checks:

```sh
python -m pip install -e '.[dev,docs]'
python scripts/compile_catalogs.py
python -m pytest
ruff check .
mypy
python -m build
python -m twine check dist/*
sphinx-build -W -b html docs build/docs
```

Run GUI tests on a real desktop or Linux Xvfb. `check_runtime(root)` reports the
active Tcl/Tk version; PyDeskUI never changes Tcl/Tk library paths at import
time.

## Publishing a release

The release script uses `build`, `twine`, and the system keyring installed by
the `dev` dependency set. Install them with:

```sh
python -m pip install -e '.[dev,docs]'
```

Create a project-scoped API token in PyPI, then store it once in the system
keyring. Paste the token, including its `pypi-` prefix, at the hidden prompt:

```sh
keyring set https://upload.pypi.org/legacy/ __token__
```

Do not put the token in this repository or pass it as a command-line argument.
As an alternative for temporary or automated environments, Twine accepts the
`TWINE_USERNAME=__token__` and `TWINE_PASSWORD` environment variables.

Before publishing, update the version in `pyproject.toml` and
`src/pydeskui/__init__.py`, finalize the matching `CHANGELOG.md` section, and
commit the release so the `main` working tree is clean. Then publish with:

```sh
python scripts/publish.py --yes
```

The script verifies release metadata and the clean branch, runs the test,
lint, type, documentation, package, and clean-wheel checks, removes stale local
build artifacts, rebuilds the wheel and source archive, and uploads only those
fresh artifacts. Omit `--yes` for a final confirmation, or use `--dry-run` to
run every check without uploading. TestPyPI is available with
`--repository testpypi`; configure its separate token with
`keyring set https://test.pypi.org/legacy/ __token__`.

## Contribution expectations

Keep explicit-parent, zero-core-dependency and lifetime contracts. New primitives
need an independent example and a real consumer. Update type hints, reference,
Skill fixtures and migration notes with API changes. Do not import GUI demos.

Reports should include OS/architecture, Python/Tcl/Tk versions, package version,
minimal code and expected/actual behavior. Avoid sharing private input or secrets.
Contributions use MIT; use `git commit -s` to certify provenance and list copied
code/assets and their licenses. Maintainers review behavior, ownership and tests.
