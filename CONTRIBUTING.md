# Contributing

Follow the [README environment setup](README.md#development) first. From the
repository root, create `.venv` once with `python -m venv .venv` and run
`source .venv/bin/activate` in each new macOS/Linux terminal. Python 3.11+ with
Tk is supported; the README also includes Windows activation instructions.
If `.venv` already exists, skip creation and only activate it. Do not overwrite
an existing environment using a different Python installation.

With that environment active, install `python -m pip install -e '.[dev,docs]'`,
then run Ruff, mypy, pytest, `python -m build` and
`python -m twine check dist/*`. Run GUI tests on a real desktop or Linux Xvfb.
Compile gettext catalogs with `scripts/compile_catalogs.py`.

Keep explicit-parent, zero-core-dependency and lifetime contracts. New primitives
need an independent example and a real consumer. Update type hints, reference,
Skill fixtures and migration notes with API changes. Do not import GUI demos.

Reports should include OS/architecture, Python/Tcl/Tk versions, package version,
minimal code and expected/actual behavior. Avoid sharing private input or secrets.
Contributions use MIT; use `git commit -s` to certify provenance and list copied
code/assets and their licenses. Maintainers review behavior, ownership and tests.
