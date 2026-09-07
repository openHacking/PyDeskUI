"""Semantic Tk 9 desktop themes with scoped SVG-backed ttk elements."""

import math
import tkinter as tk
import weakref
from collections import OrderedDict
from tkinter import font, ttk
from typing import Literal

from .i18n import TranslationContext
from .resources import check_runtime, svg_photo

_UNSET = object()


def palette(dark=False):
    values = (
        (
            "#171717",
            "#fafafa",
            "#202020",
            "#303030",
            "#858585",
            "#b3b3b3",
            "#fafafa",
            "#171717",
            "#f87171",
        )
        if dark
        else (
            "#fafafa",
            "#171717",
            "#ffffff",
            "#f4f4f5",
            "#8b8b94",
            "#64646e",
            "#18181b",
            "#fafafa",
            "#b91c1c",
        )
    )
    bg, fg, card, muted, border, subtle, primary, primary_fg, danger = values
    return dict(
        background=bg,
        foreground=fg,
        card=card,
        card_foreground=fg,
        popover=card,
        popover_foreground=fg,
        primary=primary,
        primary_foreground=primary_fg,
        secondary=muted,
        secondary_foreground=fg,
        muted=muted,
        muted_foreground=subtle,
        accent=muted,
        accent_foreground=fg,
        destructive=danger,
        destructive_foreground="#171717" if dark else "#ffffff",
        border=border,
        input=border,
        ring=fg,
        sidebar=muted,
        sidebar_foreground=fg,
        sidebar_primary=primary,
        sidebar_primary_foreground=primary_fg,
        sidebar_accent=card,
        sidebar_accent_foreground=fg,
        sidebar_border=border,
        sidebar_ring=fg,
    )


class Theme:
    """Scoped appearance; destroy themed widgets before closing.

    tokens replaces overrides ({} resets); accent=None resets branding.
    Sizes are logical pixels, without changing global Tk scaling.
    """

    def __init__(
        self,
        master,
        *,
        mode="light",
        accent=None,
        reduced_motion=False,
        translator=None,
        tokens=None,
        radius=6,
        density="default",
        font_family=None,
        font_size=13,
        contrast="normal",
        focus_ring="auto",
    ):
        if master is None or not isinstance(master, tk.Misc):
            raise TypeError("An explicit Tk master is required")
        check_runtime(master)
        self.master = master
        self.style = ttk.Style(master)
        self.prefix = f"PyDesk{id(self):x}"
        self.translator = translator or TranslationContext()
        self._widgets: weakref.WeakSet = weakref.WeakSet()
        self._closed = False
        self._images = {}
        self._svg_icons = OrderedDict()
        self._image_specs = {}
        self._active_slot = 1
        self._render_slot = 0
        self._surface_signatures = {}
        self._installed = set()
        self._installing = False
        self.mode, self.accent = "light", None
        self.radius: float = 6
        self.density = "default"
        self.font_size: float = 13
        self.contrast = "normal"
        self.focus_ring = "auto"
        self._keyboard_navigation = False
        self._input_bindings: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
        self.font_family = font.nametofont("TkDefaultFont", root=master).actual("family")
        self.reduced_motion = False
        self._overrides = {}
        self.font = font.Font(master, family=self.font_family, size=-13)
        self.fonts = {}
        self.configure(
            mode=mode,
            accent=accent,
            reduced_motion=reduced_motion,
            tokens=tokens or {},
            radius=radius,
            density=density,
            font_family=font_family or self.font_family,
            font_size=font_size,
            contrast=contrast,
            focus_ring=focus_ring,
        )
        self.translator._listeners.add(self._refresh)
        self._theme_binding = master.bind("<<ThemeChanged>>", self._host_changed, add="+")

    def configure(
        self,
        *,
        mode=None,
        accent=_UNSET,
        reduced_motion=None,
        tokens=None,
        radius=None,
        density=None,
        font_family=None,
        font_size=None,
        contrast=None,
        focus_ring=None,
    ):
        if self._closed:
            raise RuntimeError("Theme is closed")
        mode = self.mode if mode is None else mode
        accent = self.accent if accent is _UNSET else accent
        radius = self.radius if radius is None else radius
        density = self.density if density is None else density
        family = self.font_family if font_family is None else font_family
        size = self.font_size if font_size is None else font_size
        contrast = self.contrast if contrast is None else contrast
        focus_ring = self.focus_ring if focus_ring is None else focus_ring
        if mode not in ("light", "dark"):
            raise ValueError("mode must be light or dark")
        if density not in ("compact", "default", "comfortable"):
            raise ValueError("Invalid density")
        if contrast not in ("normal", "high"):
            raise ValueError("Invalid contrast")
        if focus_ring not in ("auto", "always", "never"):
            raise ValueError("focus_ring must be auto, always or never")
        if (
            not isinstance(radius, (int, float))
            or not math.isfinite(radius)
            or not 0 <= radius <= 12
        ):
            raise ValueError("radius must be between 0 and 12")
        if not isinstance(size, (int, float)) or not math.isfinite(size) or not 9 <= size <= 40:
            raise ValueError("font_size must be between 9 and 40")
        if not isinstance(family, str) or not family.strip():
            raise ValueError("font_family must be nonempty")
        overrides = dict(self._overrides if tokens is None else tokens)
        colors = palette(mode == "dark")
        if set(overrides) - set(colors):
            raise ValueError(f"Unknown theme tokens: {sorted(set(overrides) - set(colors))}")
        if accent is not None:
            rgb = self._rgb(accent)
            linear = [
                v / 3294.6 if v <= 10.31475 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in rgb
            ]
            luminance = sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))
            fg = "#000000" if luminance > 0.179 else "#ffffff"
            colors.update(
                primary=accent,
                ring=accent,
                sidebar_primary=accent,
                primary_foreground=fg,
                sidebar_primary_foreground=fg,
            )
        if contrast == "high":
            colors.update(
                border=colors["foreground"],
                input=colors["foreground"],
                muted_foreground=colors["foreground"],
            )
        colors.update(overrides)
        for color in colors.values():
            self._rgb(color)
        self.mode, self.accent, self.radius, self.density = mode, accent, radius, density
        self.font_family, self.font_size, self.contrast = family, size, contrast
        self.focus_ring = focus_ring
        self._overrides, self.tokens = overrides, colors
        if reduced_motion is not None:
            self.reduced_motion = bool(reduced_motion)
        self._apply_window_appearance(self.master.winfo_toplevel())
        for host in tuple(self._input_bindings):
            self._apply_window_appearance(host)
        # Tk reports its default 96-DPI logical scale as 4/3 on every supported
        # platform, including Aqua. Treating Aqua's baseline as 1.0 scaled all
        # dimensions and negative-pixel fonts a second time on Retina displays.
        baseline = 96 / 72
        self.scale = max(0.75, float(self.master.tk.call("tk", "scaling")) / baseline)
        self.font.configure(family=family, size=-self.px(size))
        specs: dict[str, tuple[float, Literal["normal", "bold"]]] = {
            "body": (size, "normal"),
            "muted": (size, "normal"),
            "section": (16, "bold"),
            "title": (28, "bold"),
            "display": (36, "bold"),
        }
        for name, (font_size, weight) in specs.items():
            themed = self.fonts.get(name)
            if themed is None:
                themed = font.Font(root=self.master)
                self.fonts[name] = themed
            themed.configure(family=family, size=-self.px(font_size), weight=weight)
        self.colors = dict(
            surface=colors["card"],
            text=colors["foreground"],
            muted=colors["muted_foreground"],
            danger=colors["destructive"],
            accent=colors["primary"],
        )
        self._render_slot = 1 - self._active_slot
        self._install()
        self._refresh()
        self._active_slot = self._render_slot
        self._apply_focus_visibility()

    def _focus_spec(self, image, *states):
        """Return a stable image state spec gated by the user1 visibility bit."""
        return (*states, "focus", "user1", image)

    def _input_focus_spec(self, image, *states):
        """Text inputs show their focus edge after pointer or keyboard focus."""
        if self.focus_ring == "never":
            return None
        return (*states, "focus", image)

    def _register_toplevel(self, widget):
        """Track pointer/keyboard modality without process-global bindings."""
        host = widget.winfo_toplevel()
        self._apply_window_appearance(host)
        if host in self._input_bindings:
            return
        bindings = []
        for sequence, callback in (
            ("<ButtonPress>", self._pointer_input),
            ("<KeyPress>", self._keyboard_input),
            ("<FocusIn>", self._focus_changed),
        ):
            bindings.append((sequence, host.bind(sequence, callback, add="+")))
        self._input_bindings[host] = bindings

    def _apply_window_appearance(self, host):
        """Keep native window chrome aligned with this theme's color mode."""
        try:
            appearance = self.mode
            if host.tk.call("tk", "windowingsystem") == "aqua":
                appearance = {"light": "aqua", "dark": "darkaqua"}[self.mode]
            host.wm_attributes("-appearance", appearance)
        except tk.TclError:
            # Tk 9 treats this as a no-op on Linux; tolerate older window
            # managers too so a custom runtime cannot break widget creation.
            pass

    def _pointer_input(self, event=None):
        self._set_keyboard_navigation(False)
        if event is None:
            return
        try:
            host = event.widget.winfo_toplevel()
            focused = host.focus_get()
            text_inputs = (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox, ttk.Spinbox)
            if focused is None or not isinstance(focused, text_inputs):
                return
            target = host.winfo_containing(event.x_root, event.y_root) or event.widget
            current = target
            while current is not None:
                if current is focused:
                    return
                current = getattr(current, "master", None)

            def blur_if_unchanged():
                try:
                    if host.focus_get() is focused:
                        host.focus_set()
                except tk.TclError:
                    pass

            host.after_idle(blur_if_unchanged)
        except tk.TclError:
            pass

    def _keyboard_input(self, event):
        if event.keysym in {
            "Tab",
            "ISO_Left_Tab",
            "Up",
            "Down",
            "Left",
            "Right",
            "Home",
            "End",
            "Prior",
            "Next",
            "Return",
            "KP_Enter",
            "space",
        }:
            self._set_keyboard_navigation(True)

    def _focus_changed(self, event=None):
        self._apply_focus_visibility()

    def _set_keyboard_navigation(self, enabled):
        enabled = bool(enabled)
        if self._keyboard_navigation != enabled:
            self._keyboard_navigation = enabled
            self._apply_focus_visibility()

    def _apply_focus_visibility(self):
        for widget in tuple(self._widgets):
            try:
                if isinstance(widget, ttk.Widget):
                    visible = self.focus_ring == "always" or (
                        self.focus_ring == "auto" and self._keyboard_navigation
                    )
                    # Bypass component state overrides: modality is visual state,
                    # not a request to propagate disabled/readonly semantics.
                    ttk.Widget.state(widget, ("user1",) if visible else ("!user1",))
                callback = getattr(widget, "_focus_visibility_changed", None)
                if callback is not None:
                    callback()
            except tk.TclError:
                pass

    def px(self, value):
        return max(1, round(value * self.scale))

    def _rgb(self, color):
        try:
            return tuple(round(v / 257) for v in self.master.winfo_rgb(color))
        except (tk.TclError, TypeError) as error:
            raise ValueError(f"Invalid color: {color!r}") from error

    def _tile(self, key, fill, border, stroke=1, radius=None):
        key = self._image_key(key)
        n = self.px(28)
        spec = (
            n,
            self.radius if radius is None else radius,
            fill,
            border,
            stroke,
        )
        if self._image_specs.get(key) == spec:
            return self._images[key]
        self._image_specs[key] = spec
        corner = min(n / 2, (self.radius if radius is None else radius) * self.scale)
        stroke_px = self.px(stroke)
        inset = stroke_px / 2
        extent = n - stroke_px
        data = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{n}" height="{n}" '
            f'viewBox="0 0 {n} {n}"><rect x="{inset}" y="{inset}" '
            f'width="{extent}" height="{extent}" rx="{corner}" fill="{fill}" '
            f'stroke="{border}" stroke-width="{stroke_px}"/></svg>'
        )
        if key in self._images:
            self._images[key].configure(data=data, format=("svg", "-scaletowidth", n))
        else:
            self._images[key] = svg_photo(self.master, data, width=n)
        return self._images[key]

    def _element(self, suffix, images):
        name = self.name(f"{suffix}.slot{self._render_slot}")
        if name not in self.style.element_names():
            self.style.element_create(
                name, "image", images[0], *images[1:], border=self.px(12), padding=0, sticky="nsew"
            )
        return name

    def _spacer_element(self, suffix, width):
        """Return a transparent, fixed-width layout element for native ttk parts."""
        key = self._image_key(f"spacer.{suffix}.{self.px(width)}")
        if key not in self._images:
            self._images[key] = tk.PhotoImage(
                master=self.master,
                width=self.px(width),
                height=1,
            )
        name = self.name(key)
        if name not in self.style.element_names():
            self.style.element_create(name, "image", self._images[key], sticky="")
        return name

    def popup_style(self):
        """Return the shared small rounded-surface style used by popup windows."""
        image = self._tile(
            "overlay.popup",
            self.tokens["popover"],
            self.tokens["border"],
            radius=self.radius,
        )
        element = self._element("overlay.popup", [image])
        name = self.name("Popup.TFrame")
        self.style.layout(name, [(element, {"sticky": "nsew"})])
        self.style.configure(
            name,
            padding=self.px(max(2, min(self.radius, 6) / 2)),
            background=self.tokens["popover"],
        )
        return name

    def menu_item_style(self):
        """Return the compact, left-aligned action-row style used by menus."""
        c = self.tokens
        radius = max(2, min(self.radius, 4))
        normal = self._tile("menu.item", c["popover"], c["popover"], radius=radius)
        active = self._tile("menu.item.active", c["accent"], c["accent"], radius=radius)
        pressed = self._tile("menu.item.pressed", c["accent"], c["foreground"], radius=radius)
        focus = self._tile("menu.item.focus", c["accent"], c["ring"], 1, radius=radius)
        disabled = self._tile("menu.item.disabled", c["popover"], c["popover"], radius=radius)
        states = [normal, ("disabled", disabled), ("pressed", pressed)]
        focus_spec = self._focus_spec(focus)
        if focus_spec is not None:
            states.append(focus_spec)
        states.append(("active", active))
        element = self._element("menu.item", states)
        name = self.name("MenuItem.TButton")
        self.style.layout(
            name,
            [
                (
                    element,
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                self.name("portable.Button.padding"),
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (
                                            self.name("portable.Button.label"),
                                            {"sticky": "nsew"},
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        row_height = {"compact": 26, "default": 28, "comfortable": 32}[self.density]
        vertical = max(2, round((self.px(row_height) - self.font.metrics("linespace")) / 2))
        self.style.configure(
            name,
            font=self.font,
            foreground=c["popover_foreground"],
            background=c["popover"],
            padding=(self.px(8), vertical),
            anchor="w",
            borderwidth=0,
        )
        self.style.map(name, foreground=[("disabled", c["muted_foreground"])])
        return name

    def select_option_style(self):
        """Return the rounded active-row surface used by Select popups."""
        c = self.tokens
        radius = max(2, min(self.radius, 4))
        normal = self._tile("select.option", c["popover"], c["popover"], radius=radius)
        active = self._tile("select.option.active", c["accent"], c["accent"], radius=radius)
        element = self._element("select.option", [normal, ("selected", active)])
        name = self.name("SelectOption.TFrame")
        self.style.layout(name, [(element, {"sticky": "nsew"})])
        self.style.configure(name, background=c["popover"], borderwidth=0)
        return name

    def _image_key(self, key):
        return f"slot{self._render_slot}:{key}"

    def svg_icon(self, data, width):
        """Return a shared immutable SVG photo for this interpreter and scale."""
        payload = data.encode("utf-8") if isinstance(data, str) else bytes(data)
        key = (payload, int(width))
        image = self._svg_icons.get(key)
        if image is not None:
            self._svg_icons.move_to_end(key)
            return image
        image = svg_photo(self.master, payload, width=width)
        self._svg_icons[key] = image
        if len(self._svg_icons) > 128:
            self._svg_icons.popitem(last=False)
        return image

    def _install(self):
        self._surface_signatures.clear()
        self._installing = True
        try:
            self._install_styles()
            self._installed.add(self.style.theme_use())
            self._active_host = self.style.theme_use()
        finally:
            self._installing = False

    def _install_styles(self):
        c, s = self.tokens, self.style
        for name in (
            "TFrame",
            "TLabel",
            "TCheckbutton",
            "TRadiobutton",
            "TScale",
            "TSpinbox",
            "TCombobox",
            "Treeview",
            "TNotebook",
            "TPanedwindow",
        ):
            s.configure(
                self.name(name),
                background=c["card"],
                foreground=c["foreground"],
                fieldbackground=c["card"],
                font=self.font,
                borderwidth=0,
            )
        s.configure(self.name("Danger.TLabel"), foreground=c["destructive"])
        for element in (
            "Button.border",
            "Button.label",
            "Button.padding",
            "Entry.field",
            "Entry.padding",
            "Entry.textarea",
        ):
            custom = self.name("portable." + element)
            if custom not in s.element_names():
                s.element_create(custom, "from", "clam", element)
        variants = dict(
            default=("card", "card_foreground", "input"),
            outline=("card", "card_foreground", "input"),
            primary=("primary", "primary_foreground", "primary"),
            secondary=("secondary", "secondary_foreground", "secondary"),
            destructive=("destructive", "destructive_foreground", "destructive"),
            ghost=("card", "card_foreground", "card"),
            text=("card", "card_foreground", "card"),
            link=("card", "primary", "card"),
        )
        base = {"compact": 28, "default": 32, "comfortable": 36}[self.density]
        for variant, (bg, fg, edge) in variants.items():
            normal = self._tile(variant, c[bg], c[edge])
            hover_bg = (
                c["accent"] if variant in ("default", "outline", "ghost", "text", "link") else c[bg]
            )
            hover = self._tile(variant + "hover", hover_bg, c["foreground"])
            pressed = self._tile(variant + "pressed", c[bg], c[fg], 2)
            focus = self._tile(variant + "focus", c[bg], c["ring"], 2)
            disabled = self._tile(variant + "disabled", c["muted"], c["muted"])
            button_states = [normal, ("disabled", disabled), ("pressed", pressed)]
            focus_spec = self._focus_spec(focus)
            if focus_spec is not None:
                button_states.append(focus_spec)
            button_states.append(("active", hover))
            button_element = self._element(variant + ".button", button_states)
            for size, delta in (("small", -4), ("medium", 0), ("large", 4)):
                name = self.name(f"{variant}.{size}.TButton")
                s.layout(
                    name,
                    [
                        (
                            button_element,
                            {
                                "sticky": "nsew",
                                "children": [
                                    (
                                        self.name("portable.Button.padding"),
                                        {
                                            "sticky": "nsew",
                                            "children": [
                                                (
                                                    self.name("portable.Button.label"),
                                                    {"sticky": "nsew"},
                                                )
                                            ],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                )
                pad = max(3, round((self.px(base + delta) - self.font.metrics("linespace")) / 2))
                s.configure(
                    name,
                    font=self.font,
                    foreground=c[fg],
                    background=c["card"],
                    padding=(self.px(12), pad),
                    anchor="center",
                    borderwidth=0,
                )
                s.map(name, foreground=[("disabled", c["muted_foreground"])])
        entry_states = [
            self._tile("entry", c["card"], c["input"]),
            ("disabled", self._tile("entrydisabled", c["muted"], c["border"])),
            ("invalid", self._tile("entryinvalid", c["card"], c["destructive"], 2)),
        ]
        focus_spec = self._input_focus_spec(self._tile("entryfocus", c["card"], c["ring"], 2))
        if focus_spec is not None:
            entry_states.append(focus_spec)
        entry_element = self._element("entry.field", entry_states)
        s.layout(
            self.name("TEntry"),
            [
                (
                    entry_element,
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                self.name("portable.Entry.padding"),
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (self.name("portable.Entry.textarea"), {"sticky": "nsew"})
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        s.configure(
            self.name("TEntry"),
            padding=(self.px(10), self.px((base - 18) / 2)),
            fieldbackground=c["card"],
            foreground=c["foreground"],
            insertcolor=c["foreground"],
            font=self.font,
            selectbackground=c["primary"],
            selectforeground=c["primary_foreground"],
        )
        s.map(
            self.name("TEntry"),
            fieldbackground=[("disabled", c["muted"])],
            foreground=[("disabled", c["muted_foreground"])],
        )
        # Portable elements are copied, never activate a different global theme.
        for suffix in (
            "TFrame",
            "TLabel",
            "TCheckbutton",
            "TRadiobutton",
            "Horizontal.TScale",
            "Vertical.TScale",
            "Horizontal.TProgressbar",
            "Vertical.TScrollbar",
            "Horizontal.TScrollbar",
            "TSpinbox",
            "TNotebook",
            "TNotebook.Tab",
            "Treeview.Heading",
        ):

            def copy_layout(layout):
                result = []
                for element, options in layout:
                    custom = self.name("portable." + element)
                    if custom not in s.element_names():
                        try:
                            s.element_create(custom, "from", "clam", element)
                        except tk.TclError:
                            custom = element
                    options = dict(options)
                    if "children" in options:
                        options["children"] = copy_layout(options["children"])
                    result.append((custom, options))
                return result

            try:
                portable = {
                    "TFrame": [("Frame.border", {"sticky": "nsew"})],
                    "TLabel": [
                        (
                            "Label.border",
                            {
                                "sticky": "nsew",
                                "children": [
                                    (
                                        "Label.padding",
                                        {
                                            "sticky": "nsew",
                                            "children": [("Label.label", {"sticky": "nsew"})],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                    "TCheckbutton": [
                        (
                            "Checkbutton.padding",
                            {
                                "sticky": "nsew",
                                "children": [
                                    ("Checkbutton.indicator", {"side": "left", "sticky": ""}),
                                    (
                                        "Checkbutton.focus",
                                        {
                                            "side": "left",
                                            "sticky": "w",
                                            "children": [("Checkbutton.label", {"sticky": "nsew"})],
                                        },
                                    ),
                                ],
                            },
                        )
                    ],
                    "TRadiobutton": [
                        (
                            "Radiobutton.padding",
                            {
                                "sticky": "nsew",
                                "children": [
                                    ("Radiobutton.indicator", {"side": "left", "sticky": ""}),
                                    (
                                        "Radiobutton.focus",
                                        {
                                            "side": "left",
                                            "sticky": "w",
                                            "children": [("Radiobutton.label", {"sticky": "nsew"})],
                                        },
                                    ),
                                ],
                            },
                        )
                    ],
                }
                if suffix.endswith("TScrollbar"):
                    orient = suffix.split(".")[0]
                    portable[suffix] = [
                        (
                            f"{orient}.Scrollbar.trough",
                            {
                                "sticky": "nsew",
                                "children": [(f"{orient}.Scrollbar.thumb", {"sticky": "nswe"})],
                            },
                        )
                    ]
                s.layout(self.name(suffix), copy_layout(portable.get(suffix, s.layout(suffix))))
            except tk.TclError:
                pass
            s.configure(
                self.name(suffix),
                background=c["primary"],
                foreground=c["foreground"],
                troughcolor=c["muted"],
                bordercolor=c["border"],
                lightcolor=c["primary"],
                darkcolor=c["primary"],
                arrowcolor=c["foreground"],
                font=self.font,
                borderwidth=0,
                indicatorsize=self.px(16),
                padding=self.px(2),
            )
        for suffix in ("TCheckbutton", "TRadiobutton"):
            s.configure(
                self.name(suffix),
                background=c["card"],
                indicatorbackground=c["card"],
                indicatorforeground=c["primary"],
                indicatormargin=(0, 0, self.px(8), 0),
            )
            s.map(
                self.name(suffix),
                indicatorbackground=[("selected", c["primary"])],
                indicatorforeground=[("selected", c["primary_foreground"])],
                foreground=[("disabled", c["muted_foreground"])],
            )
        progress_elements = []
        for role, token in (("trough", "muted"), ("pbar", "primary")):
            key = self._image_key("progress." + role)
            size = self.px(6)
            data = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
                f'viewBox="0 0 {size} {size}"><rect width="{size}" height="{size}" '
                f'rx="{size / 2}" fill="{c[token]}"/></svg>'
            )
            if key in self._images:
                self._images[key].configure(data=data, format=("svg", "-scaletowidth", size))
            else:
                self._images[key] = svg_photo(self.master, data, width=size)
            element = self.name(key)
            if element not in s.element_names():
                s.element_create(
                    element, "image", self._images[key], border=self.px(3), padding=0, sticky="nsew"
                )
            progress_elements.append(element)
        s.layout(
            self.name("TProgressbar"),
            [
                (
                    progress_elements[0],
                    {
                        "sticky": "nsew",
                        "children": [(progress_elements[1], {"side": "left", "sticky": "ns"})],
                    },
                )
            ],
        )
        s.configure(
            self.name("TProgressbar"),
            background=c["primary"],
            troughcolor=c["muted"],
            thickness=self.px(6),
            borderwidth=0,
        )
        s.configure(self.name("Treeview"), rowheight=self.px(base + 4), borderwidth=0)
        s.map(
            self.name("Treeview"),
            background=[("selected", c["secondary"])],
            foreground=[("selected", c["foreground"])],
        )
        heading_padding = self.name("portable.Treeheading.padding")
        if heading_padding not in s.element_names():
            s.element_create(heading_padding, "from", "clam", "Treeheading.padding")
        s.layout(
            self.name("Treeview.Heading"),
            [
                (
                    self.name("portable.Treeheading.cell"),
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                heading_padding,
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (
                                            self.name("portable.Treeheading.image"),
                                            {"side": "right", "sticky": ""},
                                        ),
                                        (
                                            self.name("portable.Treeheading.text"),
                                            {"sticky": "nsew"},
                                        ),
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        s.configure(
            self.name("Treeview.Heading"),
            background=c["card"],
            foreground=c["foreground"],
            bordercolor=c["border"],
            lightcolor=c["card"],
            darkcolor=c["card"],
            font=self.font,
            padding=(
                self.px(8),
                self.px({"compact": 8, "default": 10, "comfortable": 12}[self.density]),
            ),
            anchor="w",
            relief="flat",
        )
        # Aqua's disclosure element intentionally exposes no margin options.
        # Explicit transparent elements keep the native chevron while making
        # its spacing deterministic on every host theme.  Their names end in
        # "indicator" so ttk's native class binding includes the full padded
        # area in the expand/collapse hit target.
        tree_leading_space = self._spacer_element("tree.leading.indicator", 6)
        tree_indicator_gap = self._spacer_element("tree.gap.indicator", 8)
        s.layout(
            self.name("Treeview.Item"),
            [
                (
                    "Treeitem.padding",
                    {
                        "sticky": "nsew",
                        "children": [
                            (tree_leading_space, {"side": "left", "sticky": ""}),
                            ("Treeitem.indicator", {"side": "left", "sticky": ""}),
                            (tree_indicator_gap, {"side": "left", "sticky": ""}),
                            ("Treeitem.image", {"side": "left", "sticky": ""}),
                            ("Treeitem.text", {"side": "left", "sticky": ""}),
                        ],
                    },
                )
            ],
        )
        s.configure(self.name("Treeview.Item"), indicatormargins=0)
        s.configure(self.name("Treeview"), indent=self.px(20))
        # Keep high-volume frame/label surfaces on lightweight ttk elements.
        # SVG image elements are reserved for compact rounded controls.
        self.surface_style(self.name("TFrame"), "card")
        self.surface_style(self.name("TLabel"), "card", label=True)
        s.configure(self.name("TFrame"), background=c["card"])
        s.configure(self.name("TLabel"), background=c["card"], foreground=c["card_foreground"])
        for orient in ("Horizontal", "Vertical"):
            s.configure(
                self.name(orient + ".TScrollbar"),
                background=c["border"],
                troughcolor=c["card"],
                lightcolor=c["border"],
                darkcolor=c["border"],
                bordercolor=c["card"],
                arrowsize=self.px(10),
                width=self.px(10),
            )
        tab_normal = self._tile("notebook.tab", c["muted"], c["muted"], radius=8)
        tab_hover = self._tile("notebook.tab.hover", c["accent"], c["accent"], radius=8)
        tab_selected = self._tile("notebook.tab.selected", c["card"], c["border"], radius=8)
        tab_disabled = self._tile("notebook.tab.disabled", c["muted"], c["muted"], radius=8)
        tab_focus = self._tile("notebook.tab.focus", c["card"], c["ring"], 2, radius=8)
        tab_states = [
            tab_normal,
            ("disabled", tab_disabled),
        ]
        focus_spec = self._focus_spec(tab_focus, "selected")
        if focus_spec is not None:
            tab_states.append(focus_spec)
        tab_states.append(("selected", tab_selected))
        tab_states.append(("active", tab_hover))
        tab_element = self._element("notebook.tab", tab_states)
        s.layout(
            self.name("TNotebook.Tab"),
            [
                (
                    tab_element,
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                self.name("portable.Notebook.padding"),
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (
                                            self.name("portable.Notebook.label"),
                                            {"sticky": "nsew"},
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        tab_pad = self.px({"compact": 1, "default": 2, "comfortable": 4}[self.density])
        s.configure(
            self.name("TNotebook"),
            background=c["background"],
            bordercolor=c["background"],
            lightcolor=c["background"],
            darkcolor=c["background"],
            borderwidth=0,
            relief="flat",
            tabmargins=0,
        )
        s.configure(
            self.name("TNotebook.Tab"),
            background=c["muted"],
            foreground=c["muted_foreground"],
            padding=(self.px(10), tab_pad),
            font=self.font,
            borderwidth=0,
        )
        s.map(
            self.name("TNotebook.Tab"),
            foreground=[
                ("disabled", c["muted_foreground"]),
                ("selected", c["foreground"]),
                ("active", c["foreground"]),
            ],
        )

    def surface_style(self, name, token="card", *, label=False):
        signature = (
            self.style.theme_use(),
            self.tokens[token],
            self.tokens.get(token + "_foreground", self.tokens["foreground"]),
            self.font_family,
            self.font_size,
            self.scale,
            label,
        )
        if self._surface_signatures.get(name) == signature:
            return
        self._surface_signatures[name] = signature
        key = self._image_key("surface." + token)
        if key not in self._images:
            self._images[key] = tk.PhotoImage(master=self.master, width=2, height=2)
        image = self._images[key]
        image.put(self.tokens[token], to=(0, 0, 2, 2))
        element = self.name(key)
        if element not in self.style.element_names():
            self.style.element_create(element, "image", image, border=0, padding=0, sticky="nsew")
        if label:
            for part in ("Label.padding", "Label.label"):
                custom = self.name("portable." + part)
                if custom not in self.style.element_names():
                    self.style.element_create(custom, "from", "clam", part)
        if label:
            self.style.layout(
                name,
                [
                    (
                        self.name("portable.Label.padding"),
                        {
                            "sticky": "nsew",
                            "children": [(self.name("portable.Label.label"), {"sticky": "nsew"})],
                        },
                    )
                ],
            )
        else:
            border = self.name("portable.Frame.border")
            if border not in self.style.element_names():
                self.style.element_create(border, "from", "clam", "Frame.border")
            self.style.layout(name, [(border, {"sticky": "nsew"})])
        self.style.configure(
            name,
            background=self.tokens[token],
            foreground=self.tokens.get(token + "_foreground", self.tokens["foreground"]),
            font=self.font,
        )

    def rounded_surface_style(self, name, token="card", *, bordered=True, radius=None):
        """Install a scoped SVG-backed rounded surface for low-volume panels."""
        if self.master.tk.call("tk", "windowingsystem") == "aqua":
            # Stretching a nine-slice SVG across large native frames is very
            # expensive in Tk 9/Aqua (hundreds of milliseconds per remount).
            # Use the portable frame border there; other backends retain the
            # rounded SVG surface.
            self.surface_style(name, token)
            self.style.configure(
                name,
                background=self.tokens[token],
                bordercolor=self.tokens["border"] if bordered else self.tokens[token],
                borderwidth=self.px(1) if bordered else 0,
                relief="solid" if bordered else "flat",
            )
            return
        edge = self.tokens["border"] if bordered else self.tokens[token]
        image = self._tile(
            f"rounded-surface.{token}.{int(bordered)}",
            self.tokens[token],
            edge,
            radius=self.radius if radius is None else radius,
        )
        element = self._element(f"rounded-surface.{token}.{int(bordered)}", [image])
        self.style.layout(name, [(element, {"sticky": "nsew"})])
        self.style.configure(name, background=self.tokens[token], borderwidth=0, relief="flat")

    def _host_changed(self, event=None):
        if (
            not self._closed
            and not self._installing
            and self.style.theme_use() != self._active_host
        ):
            self._install()
            self._refresh()

    def name(self, suffix):
        return f"{self.prefix}.{suffix}"

    def _refresh(self):
        for widget in tuple(self._widgets):
            widget._refresh_theme()

    def export(self):
        return dict(
            mode=self.mode,
            accent=self.accent,
            tokens=dict(self._overrides),
            radius=self.radius,
            density=self.density,
            font_family=self.font_family,
            font_size=self.font_size,
            contrast=self.contrast,
            reduced_motion=self.reduced_motion,
            focus_ring=self.focus_ring,
        )

    def close(self):
        if self._closed:
            return
        if self._widgets:
            raise RuntimeError("Destroy theme widgets before closing the context")
        self.translator._listeners.discard(self._refresh)
        self.master.unbind("<<ThemeChanged>>", self._theme_binding)
        self._images.clear()
        self._svg_icons.clear()
        self.fonts.clear()
        self._image_specs.clear()
        self._surface_signatures.clear()
        for host, bindings in tuple(self._input_bindings.items()):
            for sequence, ident in bindings:
                try:
                    host.unbind(sequence, ident)
                except tk.TclError:
                    pass
        self._input_bindings.clear()
        self._closed = True


def resolve_theme(master, theme):
    if master is None or not isinstance(master, tk.Misc):
        raise TypeError("An explicit Tk master is required")
    if theme is None:
        root = master
        while root.master is not None:
            root = root.master
        theme = getattr(root, "_pydesk_theme", None)
        if theme is None or theme._closed:
            theme = Theme(root)
            setattr(root, "_pydesk_theme", theme)
    if theme._closed or theme.master.tk is not master.tk:
        raise ValueError("Theme must be open and belong to the same interpreter")
    return theme
