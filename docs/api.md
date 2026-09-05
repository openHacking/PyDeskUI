# Public API design record

> Revised design: 2026-09-04; source audit: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

The implemented public reference is [reference.md](reference.md). This design
record is retained for historical context; PyDeskUI 0.2 requires Python 3.13+
linked to Tk 9.

## Common widget rules

Every widget requires positional `master`. Standard tkinter geometry methods remain available; do not mix `pack` and `grid` within the same parent. Native ttk options pass through after PyDeskUI-specific options are consumed. Unknown options raise the normal Tk error instead of being silently ignored.

`configure()` updates documented options; `cget()` reads them. Unsupported enum values and inconsistent constructor arguments raise `ValueError`. Native state APIs retain their ttk meanings. User callbacks run on the GUI thread and exceptions are forwarded to the application's `report_callback_exception`; the library does not swallow them.

| Export | Proposed signature / members | Contract |
|---|---|---|
| `Button` | `Button(master, *, text="", command=None, variant="default", size="medium", theme=None, **ttk_options)` | `command: Callable[[], None]`; variants default/primary/text; sizes small/medium/large; supports disabled, focus and `invoke()` |
| `Entry` | `Entry(master, *, textvariable=None, theme=None, **ttk_options)` | Standard get/insert/delete and ttk validation; preserve externally supplied StringVar |
| `SearchEntry` | `SearchEntry(master, *, textvariable=None, on_change=None, debounce_ms=150, theme=None, **ttk_options)` | `on_change(text: str)` after debounce; Escape clears; clearing produces one change; destroy cancels pending change |
| `ItemList` | `ItemList(master, *, on_select=None, theme=None)`; `set_items(items)`, `selected_id()` | Items have stable string `id`, `title`, optional `subtitle`; `on_select(id: str \| None)`; single selection; preserve selection by ID |
| `DetailView` | `DetailView(master, *, theme=None)`; `set_content(title, body, format="text")` | Formats text/code only; content is data, never evaluated; readonly scrollable body |
| `Form` | `Form(master, *, fields, on_submit=None, theme=None)`; `get_values()`, `set_values(values)`, `set_errors(errors)` | FieldSpec sequence; submit receives dictionary; owns labels and layout, not business schema execution |
| `ProgressView` | `ProgressView(master, *, on_cancel=None, theme=None)`; `update_progress(value=None, message="")` | None = indeterminate; 0.0–1.0 = determinate; caller chooses cancellation availability |
| `Dialog` | `Dialog(master, *, title, message, actions, theme=None)`; `show(on_result)` | Nonblocking application callback with action ID; closing returns None; returns focus to invoker |

`FieldSpec` is a frozen dataclass: `id: str`, `label: str`, `kind: Literal["text", "multiline", "integer", "boolean", "choice"]`, `required: bool = False`, `default: object = None`, `choices: tuple[str, ...] = ()`. IDs must be unique in a Form. Built-in form checks only required/type/choice constraints; applications set additional errors. It does not import the PyDeskTools SDK.

`Item` is a frozen dataclass with `id: str`, `title: str`, `subtitle: str = ""`. Duplicate IDs are rejected before changing the collection. Empty items clear selection and display a localizable empty state. Selection change notifications are emitted only when the selected ID changes.

## Image preview and rectangular selection

Proposed exports `ImageView(master, *, theme=None)` and `ImageSelection(master, *, on_select=None, theme=None)` add generic raster interaction. `ImageView.set_image(image)` takes a Tk PhotoImage owned by the same interpreter, retains it, and exposes `fit()`, `set_zoom(scale)` and scrollbar-based panning. Validate finite positive zoom and bound resized-image allocation. Core zoom uses Tk-native operations; higher-quality resampling can be supplied by the application without adding a mandatory imaging dependency.

`ImageSelection` adds rectangular drag selection, keyboard-adjustable selection and Escape cancellation. Its `on_select` receives `(x, y, width, height)` in original image pixels or None, independent of displayed zoom/scroll. Clamp to image bounds; reject empty rectangles; expose the selected dimensions as text. Coordinate mapping and accessibility are component tests. Neither widget captures the screen, reads the clipboard, compresses files or owns screenshot permissions. `clear()` and `destroy()` release images and owned bindings. Host applications normalize incoming previews to PNG and enforce decoding/resource limits before construction.

## Theme API

`Theme(master, *, mode="light", accent=None, reduced_motion=False, translator=None)` creates a scoped context. `mode` is light or dark; system theme detection is an application/platform-adapter responsibility. Methods: `configure(mode=..., accent=..., reduced_motion=...)`, `close()`.

A widget's `theme=None` selects the interpreter's default PyDeskUI light context. Explicit Theme contexts allow two independently themed sections. Context style names include a unique context prefix and never modify bare `TButton` or `TEntry`. Closing a context with live widgets raises `RuntimeError`; destroy widgets first. Tk native surfaces such as OS file dialogs may not follow custom colors.

Tokens cover semantic colors (surface/text/muted/accent/danger/focus), spacing, control sizes and named fonts. Token overrides are validated before applying a style update; invalid colors must not partially modify a context.

## Resource API

`load_image(master, resource, *, size=None)` accepts a filesystem `Path` or an
`importlib.resources` Traversable and loads SVG, PNG or GIF through Tk 9.
`load_svg(master, resource, *, width=None, height=None, scale=None)` exposes the
native SVG sizing controls. The sizing options are mutually exclusive. Returned
PhotoImages must be retained by their consumer.

## Scheduling API

`Scheduler(owner)` has `call_later(delay_ms, callback) -> CancelHandle` and `close()`. `CancelHandle.cancel()` is idempotent. Both creation and cancellation occur on the GUI thread. Destroying owner closes its scheduler. The scheduler provides lifetime ownership, not cross-thread dispatch.

## Internationalization API

`TranslationContext(locale="en", translations=None)` provides `gettext(message)` and `ngettext(singular, plural, n)`. A Theme receives this context as `translator`; applications supply their own business text already translated. No API calls `gettext.install()` or `locale.setlocale()`.

## Example: component behavior

```python
# Proposed API; requires the future 0.1 implementation and a Tk-enabled Python.
import tkinter as tk
from pydeskui import Button, Entry, Theme

root = tk.Tk()
theme = Theme(root, mode="light")
value = tk.StringVar(master=root, value="Hello")
Entry(root, textvariable=value, theme=theme).grid(row=0, column=0)
Button(root, text="Clear", command=lambda: value.set(""), theme=theme).grid(row=0, column=1)
root.mainloop()
```

## Compatibility

Map `DeskButton` to Button and `DeskInput` to Entry with a migration guide; do not preserve silently broken semantics. `TxRoundedButton` remains a retired experiment rather than a promised replacement API. Do not add a fictitious `TxButton` alias simply to conceal a consumer import error. Application and library changes land through released versions or explicit editable development installs.
