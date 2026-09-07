# Public reference

This reference targets 0.2.x, Python 3.13+ and Tk 9. Widgets require a positional `master`,
use normal `pack`/`grid` for inline widgets, and execute callbacks on the Tk thread.
Popups use `show()`/`hide()`; Sheet manages its own placement. Invalid enum
values raise `ValueError`; unknown native options raise `tkinter.TclError`.
Callback exceptions go to the application's `report_callback_exception`.

All 39 components are exported from `pydeskui.widgets`; supporting contexts
and resources are exported from `pydeskui`. Check top-level component re-exports
against the installed revision.

## Behavior and keyboard contracts

- **Button:** no-argument command, variants `default/primary/secondary/outline/ghost/destructive/link/text`, sizes
  `small/medium/large`. `configure`/`cget` expose variant and size. Disabled buttons
  do not invoke. Space and Return activate a focused button.
- **Entry:** native get/insert/delete, validation and external StringVar ownership.
- **SearchEntry:** debounced `on_change(text)`; Escape clears once; destruction
  removes its trace and pending callback. `debounce_ms` is a nonnegative integer.
- **SegmentedControl:** compact single selection over string values or `(value, label)`
  pairs. `get()`/`set(value)` manage selection; Left/Right moves and commits.
- **ItemList:** `set_items(Sequence[Item])` preserves selection by ID, rejects
  duplicates before mutation, and emits `on_select(id | None)` only on change.
  Arrow keys use native Treeview selection. Initial implementation is intended
  for collections of up to 1000 visible items.
- **DetailView:** `set_content(title, body, format="text")` accepts text/code only;
  readonly selectable text is never evaluated. Use bounded previews for large data.
- **Form:** unique FieldSpec IDs; kinds text/multiline/integer/boolean/choice.
  `get_values()` validates required/type/choice and raises ValueError on errors.
  `set_values(dict)` updates only supplied fields; `set_errors(dict)` displays
  application errors. Tab leaves a multiline input; Shift-Tab moves backward.
- **ProgressView:** `update_progress(None, message)` is indeterminate; a finite
  0–1 value is determinate. `on_cancel` only signals intent to the application.
- **Dialog:** actions are `(id, label)` pairs; `show(on_result)` returns immediately.
  An action returns its ID; Escape/window close returns None. Focus/grab return
  to the invoker. Each instance may be shown once.

## Contexts and resources

`Theme(master, ...)` uses scoped styles and a configurable font based on
TkDefaultFont. Its full appearance signature is documented below. Invalid changes are rejected
before mutation. `close()` requires all themed widgets to be destroyed.
`TranslationContext.configure(locale=...)` refreshes library-owned labels without
translating consumer strings. Supported built-in catalogs: English and zh_CN.

`Scheduler(owner).call_later(delay_ms, callback)` returns an idempotent cancel
handle. Closing/destroying the owner cancels pending callbacks. This is not a
thread dispatcher. `check_runtime(master)` verifies Tk 9. `load_image` supports
SVG, PNG and GIF; `load_svg(master, resource, width=None, height=None, scale=None)`
uses Tk 9's native reader. Callers retain returned PhotoImages.

Run the repository’s `examples/gallery.py` for the interactive gallery. It demonstrates selected
compositions; the API inventory below is the component reference.


## Professional desktop theme

```text
Theme(master, *, mode="light", accent=None, reduced_motion=False,
      translator=None, tokens=None, radius=6, density="default",
      font_family=None, font_size=13, contrast="normal", focus_ring="auto")
```

`radius` accepts finite numbers from 0 through 12; `font_size` accepts finite
numbers from 9 through 40. `density` is `compact`, `default`, or `comfortable`;
`contrast` is `normal` or `high`. The default font family comes from TkDefaultFont.
`focus_ring` is `auto`, `always`, or `never`; auto shows the ring for keyboard
navigation without adding a pointer-focus outline.
See [design system](../../docs/design-system.md) for all underscore-style token keys.

`configure(...)` refreshes registered widgets. Omitted values retain their
settings; `tokens=None` retains overrides, while a supplied mapping **replaces**
all previous overrides. `tokens={}` clears them. `accent=None` resets branding.
Overrides are applied after mode, accent and high-contrast adjustments.

`export()` returns a Python dictionary of constructor-compatible appearance
settings, including only explicit token overrides. It does not include master
or translator. Use `Theme(other_master, **theme.export())` for a separate context.
`theme.tokens` contains the resolved palette; update through `configure()`.
`px(value)` converts logical dimensions to at least one physical pixel using
Tk scaling without modifying the interpreter's global scaling.

## Structure and data components

All 39 components listed here and above are available from `pydeskui.widgets`.
For example, `from pydeskui.widgets import Tree` uses the component export surface.

All constructors below take positional `master` and optional keyword `theme`.
Native options and methods remain available unless noted.

| Component | Constructor additions and public API |
|---|---|
| Frame | ttk.Frame container; caller manages child geometry. |
| Label | ttk.Label, including `text`, `textvariable`, `image`, `underline`. |
| Card | Frame surface with default padding 12 and a fixed logical corner radius of 10. Parent children directly to it. |
| Sidebar | Sidebar-colored Frame container; application supplies navigation controls. |
| Toolbar | Background-colored Frame container with default padding 6. |
| Separator | `orient="horizontal"` or `"vertical"`; non-focusable by default. |
| Badge | `variant="default"`: `default`, `primary`, `secondary`, `outline`; native label options. |
| Icon | `name="check", size=20, color=None`; `set_icon(name)`. Decorative Canvas paths, not an SVG loader. |
| Tabs | Compact rounded ttk.Notebook; `add`, `tab`, `select`, `forget`; `<<NotebookTabChanged>>`. Parent pages to the notebook. |
| SplitPane | `orient="horizontal"`; ttk.Panedwindow `add`, `insert`, `forget`, `pane`, `sashpos`. |
| ScrollArea | `horizontal=False`, `resize_debounce_ms=0`; parent children to `.content`. Exposes `.canvas`, `.xscrollbar`, `.yscrollbar`. |
| Tree | ttk.Treeview with `show="tree"`, a 20px logical indent and spaced disclosure indicators; native `insert`, `item`, selection and scrolling APIs. |
| Table | `columns=(), on_sort=None`; defaults to padded, left-aligned headings. `request_sort(column)` updates the indicator and calls `on_sort(column, direction)`. |

Icon names are `plus`, `minus`, `check`, `x`, `menu`, `search`,
`chevron-left`, `chevron-right`, `chevron-up`, and `chevron-down`.
Pair icons with visible text or a labeled control.

Table column IDs must be unique nonempty strings not starting with `#`.
Sort direction is `ascending` or `descending`; repeated requests toggle it.
The application reorders rows: Table only signals intent. Use
`<<TreeviewSelect>>` for native Table/Tree selection notifications.

Tabs enables native traversal. SplitPane adds arrow-key sash adjustment,
Shift-arrows for finer adjustment, Home/End to select a sash and Return to cycle
sashes. ScrollArea handles wheel events on its viewport/content and keyboard
scrolling on its canvas. Scrollable native descendants keep a gesture while they
can move, then hand it to the parent at a boundary; nested ScrollAreas and value
controls retain their own wheel handling.

## Inputs

| Component | Constructor additions and public API |
|---|---|
| Entry | `textvariable=None, placeholder="", invalid=False`; native editing/validation. Set invalid state with `state(["invalid"])`. Placeholder is a visual hint, not the value or a replacement for a label. |
| Textarea | tk.Text with word wrapping and undo enabled by default; native indices, `get`, `insert`, `delete`, tags and disabled state. No StringVar interface. |
| Checkbox | `variable=None`; native checkbutton `command`, `onvalue`, `offvalue`, `invoke`. |
| Switch | Checkbox subclass with the same native checkbutton behavior and options. |
| RadioGroup | `values=(), variable=None, command=None, orient="vertical", state="normal"`; values are strings or `(value, label)` pairs. `get()`, `set(value)`, `.buttons`. |
| Combobox | `values=(), textvariable=None`; editable ttk entry/value API with its own themed popup. `get`, `set`, `current`, `open_popup()`, `close_popup(restore_focus=True)`. |
| Select | Combobox with readonly selection; setting state to `normal` retains readonly behavior. |
| Slider | `variable=None`; native ttk.Scale ranges, `get`, `set`, and `command(value)`. |
| Spinbox | `textvariable=None`; native ttk.Spinbox ranges, values, wrapping and entry validation. |

Checkbox, Switch, RadioGroup and Spinbox commands retain native no-argument
signatures. Slider commands receive Tk's numeric **string**. These are not
uniform `on_change(value)` callbacks. Variable changes follow native semantics.

Combobox/Select emit `<<ComboboxSelected>>` on user commitment; programmatic
`set()` does not emit it. `postcommand` runs before opening the popup. Arrow keys
open/navigate, Return commits, Escape cancels, and Tab dismisses and traverses.
Popup typing matches prefixes; it is not a filtering/data-fetch API.
Caller-supplied variables must belong to the same interpreter and remain
caller-owned after destruction.

## Overlays and feedback

These constructors take positional `master` and optional keyword `theme`.

| Component | Constructor additions and public API |
|---|---|
| Popover | Put children in `.content`; `show(anchor=None, x=None, y=None)`, `hide()`, `.is_open`. Coordinates are screen coordinates. |
| Tooltip | `text="", delay_ms=500`; hover help attached to master; `set_text(text)` and popup show/hide methods. Does not take focus. |
| DropdownMenu | `items=()` of `(label, command)` pairs or `None` separators; `add_item(label, command=None, disabled=False)` returns a Button; `add_separator()`. The surface is constrained to the owner's application window. |
| ContextMenu | In-window DropdownMenu attached to master for right click and Shift-F10, plus macOS Control-click handling. |
| Toast | `text="", duration_ms=3000`; `show(text=None, duration_ms=None, anchor=None, x=None, y=None)`. The default is an in-window bottom-right stack; zero duration persists until hidden. |
| Alert | `title="", message="", variant="default", action_text=None, command=None, dismissible=False, on_dismiss=None`; `set_content(title=None, message=None)`, `dismiss()`. |
| EmptyState | Alert API with default title `"No items"`. |
| Skeleton | `lines=3, width=240, line_height=12, gap=8`; static Canvas placeholder bars, including when reduced motion is enabled. |
| Sheet | `side="right", size=320, title="", on_close=None`; `.content`, `show(focus=None)`, `hide()`, `.is_open`. |

Arguments following master are keyword-only in these APIs. Alert variants are
`default` and `destructive`. Alert action commands and dismissal callbacks take
no arguments; `dismiss()` destroys the alert and invokes `on_dismiss` once.
Plain destruction does not represent a dismissal callback.

Interactive popovers/menus dismiss on Escape or outside clicks observed in their
host windows, restore prior focus when possible and do not grab input. Menu
commands take no arguments and run after hiding. Up/Down, Home/End and Tab move
among enabled menu items. Tooltip and Toast are noninteractive notifications.

Select lists, DropdownMenu and ContextMenu are attached to their owning native
window. Screen-coordinate requests are translated and clamped to the client area,
and surfaces near the bottom edge open above their anchor when possible. Toasts
without explicit placement stack upward from the bottom-right (16-pixel edge,
8-pixel gap), keep at most three visible, and hide the oldest on overflow.
Re-showing a toast makes it newest; explicitly positioned toasts do not join the stack.

Sheet is an application-internal edge panel, not an OS modal sheet. Supported
sides are `left`, `right`, `top`, `bottom`; positive integer `size` is in logical
pixels and clamped to its parent. Add children to `.content`; do not pack/grid
the Sheet itself. `show(focus=widget)` requires a descendant. `on_close()` runs
once per visible-to-hidden transition, not on destruction. These overlays are
separate from the existing one-shot `Dialog.show(on_result)` contract.

Keyboard bindings described here are implemented behavior, not evidence of
screen-reader compatibility, accessibility conformance or platform certification.
