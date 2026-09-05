# Integration guide

These instructions describe the implemented 0.2.x API.

## Prerequisites and installation

Use Python 3.13 or newer linked to Tcl/Tk 9. `python -m tkinter` verifies that a
GUI can open; `check_runtime(root)` verifies the required Tk major version. A
virtual environment inherits `_tkinter` from its base Python and cannot upgrade
Tk 8.6 by installing a package from pip.

Install with `python -m pip install pydeskui`. SVG support is built into Tk 9 and
does not require an extra. Installation alone does not change themes or create windows.

## Standalone application

```python
import tkinter as tk
from pydeskui import Button, Entry

def main():
    root = tk.Tk()
    root.title("Example")
    value = tk.StringVar(master=root)
    Entry(root, textvariable=value).pack(fill="x", padx=12, pady=12)
    Button(root, text="Close", command=root.destroy).pack(pady=12)
    root.mainloop()

if __name__ == "__main__":
    main()
```

## Embed in an existing application

```python
# The caller supplies a parent and owns the event loop.
import tkinter as tk
from tkinter import ttk
from pydeskui import Button, Entry

def build_search_panel(parent, on_search):
    panel = ttk.Frame(parent)
    value = tk.StringVar(master=panel)
    Entry(panel, textvariable=value).grid(row=0, column=0, sticky="ew")
    Button(panel, text="Search", command=lambda: on_search(value.get())).grid(row=0, column=1)
    panel.columnconfigure(0, weight=1)
    return panel
```

The caller places the returned panel. This function creates neither `Tk()` nor `mainloop()`. Application state, translations and error reporting remain outside the component library.

## Long tasks

A GUI callback enqueues work to an application-owned executor and returns immediately. Workers put plain Python data into a queue. The Tk-owning thread schedules a polling callback and applies completed results to widgets. Closing a panel cancels its poller, marks pending results stale and prevents updates to destroyed widgets. Thread cancellation is cooperative; do not block window close waiting indefinitely on a worker.

For untrusted or CPU-heavy extensions, use an application-level process design such as PyDeskTools. PyDeskUI does not supply a plugin runner or claim it can terminate arbitrary Python threads.

## Configuration and resources

Create StringVar with an explicit master, retain image references, and use `importlib.resources` for bundled files. Avoid paths based on the current working directory. Fonts derive from Tk named system fonts; application-level font overrides are optional.

## Troubleshooting

| Symptom | Check |
|---|---|
| Missing `_tkinter` | Python was built without Tk support; choose a Tk-enabled Python distribution |
| No display / TclError | GUI tests need a desktop session or an explicitly configured test display |
| Image disappears | Preserve its handle for the displayed widget lifetime |
| Application freezes | Move computation/I/O out of GUI callbacks |
| Widget attaches to wrong window | Verify explicit parent and variable/image masters |
| `UnsupportedTkVersionError` | Select or build Python with `_tkinter` linked to Tk 9 |
| SVG fails to load | Check that the file uses Tk 9's supported SVG element/attribute subset |

Report exact OS, architecture, Python, Tcl and Tk versions with platform-specific failures.
