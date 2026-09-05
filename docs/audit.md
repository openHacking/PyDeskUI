# Current implementation audit

> Design baseline: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

## Executive finding

The repository contains useful visual experiments, but its packaging and widget contracts are not ready for general library use. Modernization should establish predictable tkinter behavior before adding decorative effects. Replacing tkinter or introducing a web renderer would contradict the lightweight embedding objective without addressing the existing correctness defects.

## Baseline and method

Observed: latest local commit `e8e28e8`, dated 2023-08-24; project metadata version 0.0.1; Python requirement >=3.7. All 24 Python files parsed with Python 3.14.3. Parsing reported invalid escape sequence warnings in the validation tutorial. It did not execute imports, instantiate widgets or prove runtime correctness.

The local interpreter fails `import tkinter` with `ModuleNotFoundError: No module named '_tkinter'`. GUI tests and visual measurements were not run. The top-level tests directory contains only an empty initializer; tutorial/demo files are not an effective regression suite.

## Findings

| ID / priority | Evidence | Impact | Proposed correction and acceptance |
|---|---|---|---|
| UI-01 / P1 | [button.py](../src/pydeskui/button.py), `DeskButton.__init__`, calls `Frame.__init__(self)` without the caller's parent | Widget can attach to a default root instead of the requested container | Require `master`; test nested Frame and Toplevel ownership without creating another root |
| UI-02 / P1 | [input.py](../src/pydeskui/input.py) ignores parent and supplied options; constructs an implicit-master `StringVar` | Embedding, externally owned variables and normal Entry configuration fail | Delegate parent/options to ttk.Entry and bind provided variable; test two independent inputs |
| UI-03 / P1 | [button.py](../src/pydeskui/button.py) binds mouse events directly to `command` and uses a Label as a button | Nonstandard callback arguments; no equivalent keyboard/disabled semantics | Build on ttk.Button; command takes no arguments; verify Space, Return, disabled and focus behavior |
| UI-04 / P1 | `transition` and `update_label` share mutable animation state and do not retain/cancel `after` identifiers | Hover bursts overlap; callbacks can outlive widgets; SVG recreated per frame | Owner-scoped cancellable scheduling, elapsed-time interpolation and cached images; stress destruction mid-animation |
| UI-05 / P1 | [pyproject.toml](../pyproject.toml), [setup.py](../setup.py), [requirements.txt](../requirements.txt) repeat metadata and dependency policy | Different installation paths can produce different environments | One metadata source; wheel and sdist installation tests with `pip check` |
| UI-06 / P2 | [svg_image.py](../src/pydeskui/common/svg_image.py) imported unconditionally by button module | Even text-only buttons require SVG dependencies | Lazy optional adapter; prove importing and using core widgets without any third-party package |
| UI-07 / P2 | SVG helper opens files without a context manager and accepts file-or-XML ambiguity | Resource leaks and unclear input contract | Separate explicit resource/file APIs; bounded trusted asset processing; reject invalid assets predictably |
| UI-08 / P2 | [demo.py](../src/pydeskui/demo.py) and tutorial modules create roots at import time; demo uses bare sibling imports | Discovery/documentation tooling can start GUI loops or fail after installation | Move tutorials outside the distributed library; use guarded entrypoints |
| UI-09 / P2 | README/setup metadata references old `TKinter-UI` URL; old `setup.py install/develop` instructions | Broken onboarding and duplicated project identity | Correct URLs and build/install instructions during engineering phase; this delivery only adds navigation |
| UI-10 / P2 | `list.py` and package initializer are empty; fonts/colors are hard-coded | No coherent public surface; portability and theme limitations | Export only implemented public names; theme tokens and system named fonts |

P1 means blocks a reliable release or core contract; P2 means important maintainability/usability work. No evidence currently supports labeling this a production-ready library.

## Dependency disposition

| Existing dependency | Observed usage | Target disposition |
|---|---|---|
| lxml==4.7.1 | SVG root recoloring and serialization | Remove from core. Do not implement a general SVG engine; prefer prepared trusted assets or an optional renderer |
| Pillow==9.0.1 | ImageGrab in a drawing demo, no import in core source | Remove from core; optional `images` extra for future image conversion/resizing; demo declares its own needs |
| tksvg==0.7.1 | SVGImage adapter | Experimental optional `svg` extra only after platform/wheel validation; no mandatory substitute dependency |
| setuptools>=61 | Build backend | Retain as build-time dependency, raise the floor when adopting current license metadata; not a runtime dependency |
| tkinter/Tcl/Tk | Base GUI stack | Explicit system prerequisite for library consumers; installer responsibility for applications |

Exact old pins are neither a security assessment nor proof of exploitability. Before implementation, resolve supported releases in disposable environments, record current advisories, wheel availability, licenses and transitive costs, then choose tested ranges. Do not silently upgrade all packages as a substitute for deciding whether they are needed.

Python 3.7 reached end of life in 2023; Python 3.11 is a compatibility floor with a finite remaining support window. Test 3.11–3.14 and review the floor before Python 3.11's scheduled 2027 end of life. [Python version status](https://devguide.python.org/versions/), accessed 2026-09-03.

## Source and asset provenance

Several widgets cite Stack Overflow and tutorial websites. Attribution in comments does not by itself establish redistribution compatibility with MIT. Inventory copied snippets, icons, fonts and demo artwork; record origin/license and replace or obtain permission for material that cannot be cleanly redistributed. Keep original copyright notices. No legal conclusion about individual snippets was established in this audit.

## Verification still required

Install wheel and sdist in clean environments; exercise GUI contracts on three platforms; inspect wheel contents for tutorial leakage; measure import cost and distribution size; audit supported dependency resolutions. The proposed roadmap specifies gates rather than claiming these checks passed.
