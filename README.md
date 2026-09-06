# PyDeskUI

Professional tkinter/ttk components for **Python 3.13+ and Tcl/Tk 9**, with
zero third-party runtime dependencies. Version 0.2.0 uses Tk 9's native SVG
reader for scalable icons and compact control surfaces.

## Desktop studio

| Light | Dark |
|---|---|
| ![PyDeskUI desktop studio in light mode](https://raw.githubusercontent.com/openHacking/PyDeskUI/main/docs/images/studio-light.jpg) | ![PyDeskUI desktop studio in dark mode](https://raw.githubusercontent.com/openHacking/PyDeskUI/main/docs/images/studio-dark.jpg) |

The gallery includes the complete component collection, three desktop scenes,
and a live theme editor. From a repository checkout, run
`python examples/gallery.py` to explore it. The gallery is a demonstration, not
a complete API or platform/accessibility test.

## Installation

Install PyDeskUI from PyPI:

```sh
python -m pip install pydeskui
```

Check that Python is 3.13 or newer and is linked to Tk 9:

```sh
python -c "import tkinter as tk; r=tk.Tk(); print(r.tk.call('info','patchlevel')); r.destroy()"
```

Tk 8.6 is rejected when a Theme or component is created. A virtual environment
inherits Tcl/Tk from its base interpreter; installing PyDeskUI cannot replace it.

## Quick start

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

Themes default to keyboard-aware focus rings: pointer interaction stays visually
quiet while Tab and arrow-key navigation remains visible. Set `focus_ring` to
`"always"` or `"never"` when an application needs an explicit policy.

Supporting APIs include Item, FieldSpec, Theme, TranslationContext, Scheduler,
CancelHandle, `check_runtime`, `load_image`, `load_svg` and
`UnsupportedTkVersionError`. Tk 9 loads SVG, PNG and GIF directly. Bundled icons
are SVG source assets and are rendered at the active logical size.

## Documentation

See the [design system](https://github.com/openHacking/PyDeskUI/blob/main/docs/design-system.md),
[appearance decision](https://github.com/openHacking/PyDeskUI/blob/main/docs/adr/0002-professional-desktop-appearance.md),
[implemented API](https://github.com/openHacking/PyDeskUI/blob/main/docs/reference.md),
[migration guide](https://github.com/openHacking/PyDeskUI/blob/main/docs/migration.md),
[design documents](https://github.com/openHacking/PyDeskUI/blob/main/docs/README.md),
and [agent skill](https://github.com/openHacking/PyDeskUI/blob/main/skills/pydeskui/SKILL.md).

## Contributing

Development setup, testing, and release checks are documented in the
[contribution guide](https://github.com/openHacking/PyDeskUI/blob/main/CONTRIBUTING.md).

## Support

If PyDeskUI is useful to you, you can support its development on
[Buy Me a Coffee](https://buymeacoffee.com/openhacking).
