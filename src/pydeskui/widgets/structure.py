"""Native structural widgets; all accept an explicit master and optional theme.

ttk options and methods remain available. Composite ScrollArea exposes ``content``
for children and ``canvas``, ``xscrollbar`` and ``yscrollbar`` for native control.
No bind_all handlers, implicit roots, image packages, or unscoped style writes.
Built-in dimensions use theme.px and refresh with the theme. Explicit native
dimensions/padding remain caller-owned pixels (text widths remain characters).
"""

import math
import tkinter as tk
from functools import partial
from importlib.resources import files
from tkinter import ttk

from ..resources import svg_photo
from ..theme import resolve_theme
from ._base import Owned

__all__ = [
    "Frame",
    "Label",
    "Card",
    "Separator",
    "Badge",
    "Icon",
    "Sidebar",
    "Toolbar",
    "Tabs",
    "SplitPane",
    "ScrollArea",
    "Table",
    "Tree",
]


def _color(theme, token):
    tokens = getattr(theme, "tokens", {})
    if token in tokens:
        return tokens[token]
    legacy = getattr(theme, "colors", {})
    key = {
        "background": "surface",
        "foreground": "text",
        "card": "surface",
        "card_foreground": "text",
        "muted": "surface",
        "muted_foreground": "muted",
        "border": "muted",
        "primary": "accent",
        "primary_foreground": "surface",
        "accent": "surface",
        "accent_foreground": "text",
        "sidebar": "surface",
        "sidebar_foreground": "text",
    }[token]
    return legacy.get(key, "#ffffff" if key == "surface" else "#17202a")


def _px(theme, value):
    return theme.px(value) if hasattr(theme, "px") else max(1, round(value))


def _oriented_style(theme, suffix, orient):
    """Scrollbar/paned layouts are orientation-specific in native ttk themes."""
    name = theme.name(f"{orient.title()}.{suffix}")
    try:
        theme.style.layout(name)
    except tk.TclError:
        theme.style.layout(name, theme.style.layout(f"{orient.title()}.{suffix}"))
    return name


def _orientation(orient):
    if orient not in ("horizontal", "vertical"):
        raise ValueError("orient must be horizontal or vertical")
    return orient


class Frame(Owned, ttk.Frame):
    """Native container. Child geometry is controlled entirely by the caller."""

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        options.setdefault("style", theme.name("TFrame"))
        super().__init__(master, **options)
        self._own(master, theme)


class Label(Owned, ttk.Label):
    """Native text/image label, including textvariable and underline support."""

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        options.setdefault("style", theme.name("TLabel"))
        super().__init__(master, **options)
        self._own(master, theme)


class _Surface(Frame):
    _role = "card"
    _padding = 12

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        self._role_style = f"{type(self).__name__}.{theme.name('TFrame')}"
        options.setdefault("style", self._role_style)
        super().__init__(master, theme=theme, **options)
        self._refresh_theme()

    def _refresh_theme(self):
        if hasattr(self.theme, "surface_style"):
            self.theme.surface_style(self._role_style, self._role)
        self.theme.style.configure(
            self._role_style,
            background=_color(self.theme, self._role),
            bordercolor=_color(self.theme, "border"),
            padding=_px(self.theme, self._padding),
        )


class Card(_Surface):
    """Lightweight bordered content card.

    Place children directly inside the frame; explicit padding/style options
    override the defaults. Images are retained and refreshed by the theme.
    """

    def __init__(self, master, *, theme=None, **options):
        options.setdefault("borderwidth", 0)
        options.setdefault("relief", "flat")
        super().__init__(master, theme=theme, **options)

    def _refresh_theme(self):
        super()._refresh_theme()
        theme = self.theme
        theme.style.configure(
            self._role_style,
            borderwidth=_px(theme, 1),
            bordercolor=_color(theme, "border"),
            relief="solid",
        )


class Sidebar(_Surface):
    """Sidebar-colored container for caller-supplied native navigation controls."""

    _role = "sidebar"


class Toolbar(_Surface):
    """Compact container for native buttons; their normal focus traversal remains."""

    _role = "background"
    _padding = 6


class Separator(Owned, ttk.Separator):
    """Non-focusable native horizontal or vertical separator."""

    def __init__(self, master, *, orient="horizontal", theme=None, **options):
        _orientation(orient)
        theme = resolve_theme(master, theme)
        self._role_style = theme.name("TSeparator")
        options.setdefault("style", self._role_style)
        options.setdefault("takefocus", False)
        super().__init__(master, orient=orient, **options)
        self._own(master, theme)
        self._refresh_theme()

    def _refresh_theme(self):
        self.theme.style.configure(self._role_style, background=_color(self.theme, "border"))


class Badge(Label):
    """Text badge. variant is default, secondary, outline, or primary."""

    def __init__(self, master, *, variant="default", theme=None, **options):
        if variant not in ("default", "secondary", "outline", "primary"):
            raise ValueError("Invalid badge variant")
        self.variant = variant
        theme = resolve_theme(master, theme)
        self._role_style = f"Badge.{variant}.{theme.name('TLabel')}"
        options.setdefault("style", self._role_style)
        super().__init__(master, theme=theme, **options)
        self._refresh_theme()

    def _refresh_theme(self):
        bg, fg = {
            "default": ("primary", "primary_foreground"),
            "primary": ("primary", "primary_foreground"),
            "secondary": ("muted", "muted_foreground"),
            "outline": ("background", "foreground"),
        }[self.variant]
        if hasattr(self.theme, "surface_style"):
            self.theme.surface_style(self._role_style, bg, label=True)
        self.theme.style.configure(
            self._role_style,
            background=_color(self.theme, bg),
            foreground=_color(self.theme, fg),
            font=self.theme.font,
            bordercolor=_color(self.theme, "border"),
            relief="solid" if self.variant == "outline" else "flat",
            borderwidth=_px(self.theme, 1) if self.variant == "outline" else 0,
            padding=(_px(self.theme, 6), _px(self.theme, 2)),
        )


class Icon(Owned, tk.Canvas):
    """Decorative SVG icon; pair it with visible text or an accessible button.

    Names: plus, minus, check, x, menu, search, chevron-left/right/up/down.
    ``set_icon(name)`` changes the drawing. Canvas options remain available.
    """

    _names = frozenset(
        {
            "plus",
            "minus",
            "check",
            "x",
            "menu",
            "search",
            "chevron-left",
            "chevron-right",
            "chevron-up",
            "chevron-down",
        }
    )

    def __init__(
        self, master, *, name=None, source=None, size=20, color=None, theme=None, **options
    ):
        if name is not None and source is not None:
            raise ValueError("name and source are mutually exclusive")
        name = "check" if name is None and source is None else name
        if name is not None:
            self._validate_name(name)
        if not isinstance(size, (int, float)) or not math.isfinite(size) or size <= 0:
            raise ValueError("size must be a positive finite number")
        theme = resolve_theme(master, theme)
        self.icon_name, self.icon_source, self.icon_color = name, source, color
        self._icon_image: tk.PhotoImage | None = None
        self._canvas_item = None
        self._logical_size = size
        self._scaled_dimensions = {
            key: _px(theme, size) for key in ("width", "height") if key not in options
        }
        self._auto_background = "background" not in options and "bg" not in options
        options.setdefault("width", _px(theme, size))
        options.setdefault("height", _px(theme, size))
        options.setdefault("highlightthickness", 0)
        options.setdefault("borderwidth", 0)
        options.setdefault("takefocus", False)
        super().__init__(master, **options)
        self._own(master, theme)
        self.bind("<Configure>", self._draw, add="+")
        self._refresh_theme()

    @classmethod
    def _validate_name(cls, name):
        if name not in cls._names:
            raise ValueError(f"Unknown icon: {name!r}")

    def set_icon(self, name):
        self._validate_name(name)
        self.icon_name = name
        self.icon_source = None
        self._image_signature = None
        self._draw()

    def set_source(self, source):
        if source is None or not hasattr(source, "read_bytes"):
            raise TypeError("source must be a pathlib.Path or Traversable")
        self.icon_name = None
        self.icon_source = source
        self._image_signature = None
        self._draw()

    def _refresh_theme(self):
        for key, previous in tuple(self._scaled_dimensions.items()):
            if float(self.cget(key)) != previous:
                del self._scaled_dimensions[key]
                continue
            value = _px(self.theme, self._logical_size)
            self.configure(**{key: value})
            self._scaled_dimensions[key] = value
        if self._auto_background:
            self.configure(background=_color(self.theme, "background"))
        self._draw()

    def _draw(self, event=None):
        width, height = float(self.winfo_width()), float(self.winfo_height())
        if width <= 1:
            width = float(self.cget("width"))
        if height <= 1:
            height = float(self.cget("height"))
        color = self.icon_color or _color(self.theme, "foreground")
        pixels = max(1, round(min(width, height)))
        rgb = tuple(round(v / 257) for v in self.winfo_rgb(color))
        source_key = self.icon_name or str(self.icon_source)
        signature = (source_key, pixels, rgb)
        if getattr(self, "_image_signature", None) != signature:
            self._image_signature = signature
            asset = (
                files("pydeskui").joinpath("assets", "icons", f"{self.icon_name}.svg")
                if self.icon_name
                else self.icon_source
            )
            if asset is None or not hasattr(asset, "read_bytes"):
                raise TypeError("source must be a pathlib.Path or Traversable")
            data = asset.read_bytes()
            encoded_color = ("#%02x%02x%02x" % rgb).encode("ascii")
            data = data.replace(b"currentColor", encoded_color).replace(b"#000001", encoded_color)
            if hasattr(self.theme, "svg_icon"):
                self._icon_image = self.theme.svg_icon(data, pixels)
            else:
                self._icon_image = svg_photo(self, data, width=pixels)
        if self._canvas_item is None:
            self._canvas_item = self.create_image(
                width / 2, height / 2, image=self._icon_image, tags="pydeskui-icon"
            )
        else:
            self.coords(self._canvas_item, width / 2, height / 2)
            self.itemconfigure(self._canvas_item, image=self._icon_image)

    def _cleanup(self):
        self._icon_image = None
        self._canvas_item = None


class Tabs(Owned, ttk.Notebook):
    """Native add/tab/select/forget API; Ctrl-Tab and underlined mnemonics enabled.

    Parent each tab's content directly to this notebook for mnemonic traversal.
    Listen to the native <<NotebookTabChanged>> event for selection changes.
    """

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        options.setdefault("style", theme.name("TNotebook"))
        super().__init__(master, **options)
        self._own(master, theme)
        self.enable_traversal()


class SplitPane(Owned, ttk.Panedwindow):
    """Native add/insert/forget/pane/sashpos API, plus keyboard sash adjustment.

    Focus the pane and use arrows (10px), Shift-arrows (1px). Home/End select
    the first/last sash; Return cycles the active sash. Tab exits normally.
    """

    def __init__(self, master, *, orient="horizontal", theme=None, **options):
        _orientation(orient)
        theme = resolve_theme(master, theme)
        self._native_style = "style" not in options
        if "style" not in options:
            options["style"] = _oriented_style(theme, "TPanedwindow", orient)
        options.setdefault("takefocus", True)
        super().__init__(master, orient=orient, **options)
        self._own(master, theme)
        self._active_sash = 0
        for key in ("Left", "Right", "Up", "Down", "Home", "End", "Return"):
            self.bind(f"<{key}>", self._key, add="+")
        self._refresh_theme()

    def _refresh_theme(self):
        if self._native_style:
            style = _oriented_style(self.theme, "TPanedwindow", str(self.cget("orient")))
            self.theme.style.configure(
                style, background=_color(self.theme, "background"), sashwidth=_px(self.theme, 6)
            )

    def _key(self, event):
        count = len(self.panes()) - 1
        if count < 1 or self.instate(("disabled",)):
            return None
        self._active_sash = min(self._active_sash, count - 1)
        key = event.keysym
        if key in ("Home", "End", "Return"):
            self._active_sash = {
                "Home": 0,
                "End": count - 1,
                "Return": (self._active_sash + 1) % count,
            }[key]
        else:
            keys = ("Left", "Right") if str(self.cget("orient")) == "horizontal" else ("Up", "Down")
            if key not in keys:
                return None
            delta = _px(self.theme, 1 if event.state & 1 else 10) * (-1 if key == keys[0] else 1)
            self.sashpos(self._active_sash, self.sashpos(self._active_sash) + delta)
        return "break"


class ScrollArea(Frame):
    """Scrollable child container with native bars and a keyboard-focusable canvas.

    Parent widgets to ``content``. ``horizontal=False`` fits content to viewport
    width; True allows its requested width to overflow. Arrow/Page/Home/End work
    on the viewport. Wheels over ordinary descendants scroll this area; native
    scrollable controls and nested ScrollAreas retain their own wheel handling.
    Per-instance toplevel bindings are removed on destruction.
    """

    def __init__(self, master, *, horizontal=False, theme=None, **options):
        self._wheel_bindings = []
        self._layout_job = None
        self._layout_signature = None
        super().__init__(master, theme=theme, **options)
        self.horizontal = bool(horizontal)
        self.canvas = tk.Canvas(
            self,
            highlightthickness=_px(self.theme, 1),
            borderwidth=0,
            takefocus=True,
            width=_px(self.theme, 240),
            height=_px(self.theme, 180),
        )
        self._canvas_defaults = {
            key: (logical, _px(self.theme, logical))
            for key, logical in (("width", 240), ("height", 180), ("highlightthickness", 1))
        }
        self.content = Frame(self.canvas, theme=self.theme)
        self._window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.yscrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            style=_oriented_style(self.theme, "TScrollbar", "vertical"),
        )
        self.xscrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.canvas.xview,
            style=_oriented_style(self.theme, "TScrollbar", "horizontal"),
        )
        self.canvas.configure(yscrollcommand=self._set_y, xscrollcommand=self.xscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.yscrollbar.grid(row=0, column=1, sticky="ns")
        if self.horizontal:
            self.xscrollbar.grid(row=1, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas.bind("<Configure>", self._queue_layout, add="+")
        self.content.bind("<Configure>", self._queue_layout, add="+")
        self._wheel_toplevel = self.winfo_toplevel()
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            binding = self._wheel_toplevel.bind(sequence, self._subtree_wheel, add="+")
            self._wheel_bindings.append((sequence, binding))
        self.canvas.bind("<Button-1>", lambda event: self.canvas.focus_set(), add="+")
        self.canvas.bind("<KeyPress>", self._key, add="+")
        self._refresh_theme()

    def _refresh_theme(self):
        for key, (logical, previous) in tuple(self._canvas_defaults.items()):
            if float(self.canvas.cget(key)) != previous:
                del self._canvas_defaults[key]
                continue
            value = _px(self.theme, logical)
            self.canvas.configure(**{key: value})
            self._canvas_defaults[key] = (logical, value)
        for orient, bar in (("vertical", self.yscrollbar), ("horizontal", self.xscrollbar)):
            style = _oriented_style(self.theme, "TScrollbar", orient)
            self.theme.style.configure(style, width=_px(self.theme, 14))
        self.canvas.configure(
            background=_color(self.theme, "background"),
            highlightbackground=_color(self.theme, "border"),
            highlightcolor=_color(self.theme, "primary"),
        )
        self._queue_layout()

    def _set_y(self, first, last):
        self.yscrollbar.set(first, last)
        visible = not (float(first) <= 0 and float(last) >= 1)
        if getattr(self, "_y_visible", None) != visible:
            self._y_visible = visible
            if visible:
                self.yscrollbar.grid()
            else:
                self.yscrollbar.grid_remove()

    def _queue_layout(self, event=None):
        if self._layout_job is None:
            self._layout_job = self.after_idle(self._layout)

    def _layout(self, event=None):
        self._layout_job = None
        inset = 2 * (
            float(self.canvas.cget("highlightthickness")) + float(self.canvas.cget("borderwidth"))
        )
        width = max(1, self.canvas.winfo_width() - inset)
        if self.horizontal:
            width = max(width, self.content.winfo_reqwidth())
        height = max(self.content.winfo_reqheight(), self.canvas.winfo_height() - inset, 1)
        signature = (width, height)
        if signature == self._layout_signature:
            return
        self._layout_signature = signature
        self.canvas.itemconfigure(self._window, width=width, height=height)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def _wheel(self, event):
        if getattr(event, "num", None) in (4, 5):
            units = -3 if event.num == 4 else 3
        else:
            delta = event.delta
            if not delta:
                return None
            aqua = self.tk.call("tk", "windowingsystem") == "aqua"
            units = -int(delta) if aqua else -int(math.copysign(max(1, abs(delta) // 120), delta))
        horizontal = bool(event.state & 1) and self.horizontal
        view = self.canvas.xview if horizontal else self.canvas.yview
        before = view()
        view("scroll", units, "units")
        return "break" if view() != before else None

    def _subtree_wheel(self, event):
        # The toplevel bindtag follows each widget's instance and native class
        # bindings. New descendants therefore work without polling or retagging.
        widget = event.widget
        while isinstance(widget, tk.Misc):
            if widget is self.canvas or widget is self.content:
                return self._wheel(event)
            if widget is self or isinstance(widget, ScrollArea):
                return None
            if widget.winfo_class() in {
                "Text",
                "Treeview",
                "Listbox",
                "Canvas",
                "Scrollbar",
                "TScrollbar",
                "Spinbox",
                "TSpinbox",
                "TCombobox",
                "Scale",
                "TScale",
            }:
                return None
            widget = widget.master
        return None

    def _cleanup(self):
        if self._layout_job is not None:
            try:
                self.after_cancel(self._layout_job)
            except tk.TclError:
                pass
            self._layout_job = None
        for sequence, binding in self._wheel_bindings:
            try:
                self._wheel_toplevel.unbind(sequence, binding)
            except tk.TclError:
                # The owning toplevel may itself be in the middle of destruction.
                pass
        self._wheel_bindings.clear()

    def _key(self, event):
        key = event.keysym
        if key in ("Home", "End"):
            self.canvas.yview_moveto(0 if key == "Home" else 1)
        elif key in ("Up", "Down", "Prior", "Next"):
            self.canvas.yview_scroll(
                -1 if key in ("Up", "Prior") else 1,
                "pages" if key in ("Prior", "Next") else "units",
            )
        elif key in ("Left", "Right") and self.horizontal:
            self.canvas.xview_scroll(-1 if key == "Left" else 1, "units")
        else:
            return None
        return "break"


class Tree(Owned, ttk.Treeview):
    """Native hierarchical view with insert/item/selection and xview/yview APIs.

    Native arrows, expansion, multi-selection, focus and virtual events survive.
    Supply text on each node for meaningful labels; attach scrollbars as needed.
    """

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        options.setdefault("style", theme.name("Treeview"))
        options.setdefault("show", "tree")
        super().__init__(master, **options)
        self._own(master, theme)


class Table(Tree):
    """Native flat Treeview: columns are IDs, headings initially use those IDs.

    Use heading/column to customize, insert('', 'end', values=...) for rows, and
    <<TreeviewSelect>> for changes. Standard selection and scrolling APIs apply.
    Clicking a heading calls on_sort(column, direction), where direction is
    'ascending' or 'descending'. Repeated clicks toggle; a new column starts
    ascending. Rows are never reordered internally. request_sort(column) offers
    the same action for keyboard-accessible controls or application menus.
    """

    def __init__(self, master, *, columns=(), on_sort=None, theme=None, **options):
        columns = tuple(columns)
        if any(not isinstance(c, str) or not c or c.startswith("#") for c in columns):
            raise ValueError("Column IDs must be nonempty strings not starting with #")
        if len(set(columns)) != len(columns):
            raise ValueError("Column IDs must be unique")
        if on_sort is not None and not callable(on_sort):
            raise TypeError("on_sort must be callable or None")
        self.on_sort = on_sort
        self.sort_column = None
        self.sort_direction = None
        self._sort_heading = None
        options.setdefault("show", "headings")
        super().__init__(master, columns=columns, theme=theme, **options)
        for column in columns:
            self.heading(column, text=column, command=partial(self.request_sort, column))

    def request_sort(self, column):
        """Request sorting and update the indicator without mutating row data."""
        if column not in self.cget("columns"):
            raise ValueError(f"Unknown column: {column!r}")
        if self.instate(("disabled",)):
            return
        direction = (
            "descending"
            if self.sort_column == column and self.sort_direction == "ascending"
            else "ascending"
        )
        if self._sort_heading is not None:
            old_column, original, rendered = self._sort_heading
            if old_column in self.cget("columns") and self.heading(old_column, "text") == rendered:
                self.heading(old_column, text=original)
        original = self.heading(column, "text")
        rendered = f"{original} {'▲' if direction == 'ascending' else '▼'}"
        self.heading(column, text=rendered)
        self._sort_heading = (column, original, rendered)
        self.sort_column, self.sort_direction = column, direction
        if self.on_sort is not None:
            self.on_sort(column, direction)
