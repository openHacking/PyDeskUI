# Engineering and release policy

> Revised design: 2026-09-04; source audit: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

## Packaging

Retain the `src` layout and setuptools backend. Make `pyproject.toml` the sole source for project metadata, dependency ranges, extras and build configuration. Remove duplicate setup.py metadata and the manually frozen requirements file during implementation. Use a modern setuptools floor compatible with SPDX license metadata; select the exact tested floor in the packaging change, not by copying an obsolete minimum.

Declare Python >=3.13 and require a Python interpreter linked to Tcl/Tk 9. Include only library modules, SVG icons and compiled translation catalogs in wheels. Tutorials, business demos and unrelated artwork stay outside the installed package. Library dependencies use tested ranges; a developer lock file can reproduce contributor environments without constraining downstream users to exact versions.

Suggested tooling: uv for contributor environment management; standard `pip install -e .`, `python -m build` and `twine check` remain documented alternatives where relevant. Ruff handles lint/format, mypy checks the public typed surface, pytest covers behavior. No runtime dependency on these tools.

## Repository health

Future engineering changes add or revise CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, issue/PR templates and release instructions. Use English, give reproducible bug-report fields (OS, architecture, Python, Tcl/Tk, package version), and publish a private security reporting route through GitHub rather than inventing an unmonitored email address.

Contributions use the existing MIT terms; document sign-off/provenance expectations. Maintain a third-party notices inventory, including assets and copied snippets. Do not relicense historical contributions or promise complete rights clearance from this design alone.

## CI and publication

| Gate | Checks |
|---|---|
| Pull request | Ruff, mypy, pure-logic tests, wheel/sdist build, metadata check, install from outside source checkout |
| GUI integration | Tk-enabled Python, parenting, variables, callbacks, destruction and native events; Linux Xvfb can cover a subset |
| Release candidate | Supported OS/Python matrix, optional-extra installation, manual accessibility/scaling checks, dependency/license audit |
| Tagged release | Reproducible artifacts, release notes, PyPI Trusted Publishing, static versioned docs and source provenance |

Do not publish from pull requests or grant them release secrets. Pin action revisions and use minimum workflow permissions. Prefer OIDC Trusted Publishing over a long-lived PyPI token. Public distribution claims must match the matrix that actually passed. [PyPA publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/), accessed 2026-09-03.

## Versioning and compatibility

The Tk 9/SVG line starts at 0.2.0. Breaking pre-1.0 API changes increment the minor version; patch releases preserve contracts. At 1.0 adopt normal semantic versioning. Declare a supported API rather than promising all internal modules are stable. Support a deprecation window only after the public API stabilizes; the prototype does not justify retaining broken aliases.

Test Python 3.13 and 3.14 only with `_tkinter` linked to Tk 9. A Python version alone does not prove compatibility, so CI must assert the runtime Tk patch level before GUI tests. Tk 8.6 is unsupported and receives a clear runtime error. Do not add an arbitrary Python upper bound without an observed incompatibility.

## Performance budget proposal

Core installs with zero third-party runtime packages. Responsiveness targets are: warm theme switching below 50 ms, page switching below 50 ms once created, 100 Button construction below 20 ms, and no repeated Configure mutations for a stable ScrollArea size. Record cold first-window paint separately because it includes operating-system window startup.

## Current versus target commands

The existing README contains historical setup.py workflows and remains historical except for the new design link. During implementation, replace those instructions atomically with tested commands and remove obsolete demos. [PyPA pyproject guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), accessed 2026-09-03, is the packaging reference.
