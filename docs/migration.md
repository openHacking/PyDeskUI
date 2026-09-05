# Migrating to 0.2

Version 0.2 requires Python 3.13+ linked to Tk 9. Applications using 0.1 on
Tk 8.6 must change their Python distribution or rebuild Python against Tk 9.

| Before | After |
|---|---|
| `from button import DeskButton` | `from pydeskui import Button` |
| `DeskButton(command=lambda event: ...)` | `Button(parent, command=lambda: ...)` |
| `DeskInput(root)` ignoring its parent | `Entry(parent, textvariable=caller_variable)` |
| `TxRoundedButton(...)` | `Button(parent, ...)` using native focus and disabled state |
| `type="primary", size="middle"` | `variant="primary", size="medium"` |
| global hard-coded colors | explicit `Theme(parent)` |
| runtime namespace tutorials | guarded `examples/gallery.py` |
| prepared PNG icon variants | one SVG source loaded by Tk 9 at the requested size |

No `TxButton`, `DeskButton` or `DeskInput` aliases are exported. Screenshots,
plugin schemas and filesystem business operations belong to the application.

`MissingOptionalDependencyError` is removed. Use `check_runtime(root)` to verify
Tk 9, `load_svg()` for explicit SVG resources, and
`UnsupportedTkVersionError` for a runtime compatibility diagnostic.
