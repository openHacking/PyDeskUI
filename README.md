# PyDeskUI

Professional tkinter/ttk components for **Python 3.13+ and Tcl/Tk 9**, with
zero third-party runtime dependencies. Version 0.2.0 uses Tk 9's native SVG
reader for scalable icons and compact control surfaces.

First check that Python is 3.13 or newer and is linked to Tk 9:

```sh
python -c "import tkinter as tk; r=tk.Tk(); print(r.tk.call('info','patchlevel')); r.destroy()"
```

From the repository root, create a virtual environment **only on first setup**,
then activate it (macOS/Linux, bash or zsh). If `.venv` already exists, skip the
creation command and start with `source .venv/bin/activate`:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install .
python examples/gallery.py
```

Tk 8.6 is rejected when a Theme or component is created. A virtual environment
inherits Tcl/Tk from its base interpreter; installing PyDeskUI cannot replace it.

```python
import tkinter as tk
from pydeskui import Button, Card, Entry, Label, Theme

root = tk.Tk()
theme = Theme(root, radius=6, density="default", font_size=13)
panel = Card(root, theme=theme)
panel.pack(fill="both", expand=True, padx=16, pady=16)
Label(panel, text="Project name", theme=theme).pack(anchor="w")
value = tk.StringVar(master=root, value="Hello")
Entry(panel, textvariable=value, placeholder="Untitled", theme=theme).pack(fill="x")
Button(panel, text="Clear", variant="secondary", theme=theme,
       command=lambda: value.set("")).pack(anchor="e", pady=8)
root.mainloop()
```

The caller owns the parent, domain state and event loop. All GUI operations run
on the Tk thread. Importing the library never creates a root. Themes use scoped
styles; widget destruction cancels owned work and retains caller variables.

The `pydeskui.widgets` export surface contains 38 components (excluding data
helpers and contexts):

| Group | Components |
|---|---|
| Existing controls and views | Button, Entry, SearchEntry, ItemList, DetailView, Form, ProgressView, Dialog |
| Structure and data | Frame, Label, Card, Separator, Badge, Icon, Sidebar, Toolbar, Tabs, SplitPane, ScrollArea, Table, Tree |
| Additional inputs | Textarea, Checkbox, RadioGroup, Switch, Select, Combobox, Slider, Spinbox |
| Overlays and feedback | Tooltip, Popover, DropdownMenu, ContextMenu, Alert, Toast, EmptyState, Skeleton, Sheet |

Supporting APIs include Item, FieldSpec, Theme, TranslationContext, Scheduler,
CancelHandle, `check_runtime`, `load_image`, `load_svg` and
`UnsupportedTkVersionError`. Tk 9 loads SVG, PNG and GIF directly. Bundled icons
are SVG source assets and are rendered at the active logical size.

Run `python examples/gallery.py` from the repository root to explore interactive
component compositions. The gallery is a demonstration, not a complete API or
platform/accessibility test. See the reference for all component contracts.

See [design system](docs/design-system.md),
[appearance decision](docs/adr/0002-professional-desktop-appearance.md),
[implemented API](docs/reference.md), [migration](docs/migration.md),
[design documents](docs/README.md), [contribution guide](CONTRIBUTING.md),
and [agent skill](skills/pydeskui/SKILL.md).

## Development

If `.venv` already exists, activate it; do not run `venv` over it again with a
different Python installation. This can leave interpreter links and
`pyvenv.cfg` inconsistent, causing `ensurepip` or `encodings` import failures.
If the environment is broken, first inspect `.venv/pyvenv.cfg` and its interpreter
links. To recreate it, deactivate it, move it to a backup location, create a new
`.venv` with the intended Tk-enabled interpreter, and reinstall dependencies.
Keep the backup for recovery; virtual environments are not portable after moving.
Use a Python installed at a stable location rather than under `/tmp`, since
removing the base interpreter also breaks its virtual environments.

Use the repository's `.venv` for development too, with Python 3.13+ and Tk 9. A venv
uses its base interpreter's Tcl/Tk installation; it does not install Tk itself.

After the initial setup above, activate the existing environment whenever you
open a new terminal (run these commands from the repository root):

```sh
source .venv/bin/activate
python -c "import sys; print(sys.executable)"
python -m tkinter
```

The interpreter path should be inside this project's `.venv`. Close the Tk test
window to continue. On Windows PowerShell, create the environment with
`python -m venv .venv` and activate it with `.\.venv\Scripts\Activate.ps1`.
Run `deactivate` to leave the environment. `.venv/` is ignored by Git; do not
commit or copy it between projects. Activation is optional if you call its
interpreter directly, for example `.venv/bin/python -m pytest` on macOS/Linux.

Install development dependencies into the activated environment, then verify:

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

Standalone Python builds must bundle Tcl/Tk 9 and link `_tkinter` against that
major version. `check_runtime(root)` reports the active version; PyDeskUI never
changes Tcl/Tk library paths at import time.

## Desktop studio

![PyDeskUI desktop studio](docs/images/studio-light.jpg)

Run `python examples/gallery.py` to explore the complete component collection,
three desktop scenes, and a live theme editor. See the [design system](docs/design-system.md).
