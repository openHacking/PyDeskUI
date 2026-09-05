"""Native inputs with explicit owners and independently styled choice popups.

Variables remain caller-owned. Commands on native controls keep tkinter's
signatures; choices emit ``<<ComboboxSelected>>`` only on user commitment.
"""

import time
import tkinter as tk
from tkinter import ttk

from ..resources import svg_photo
from ..theme import resolve_theme
from ._base import Owned

__all__ = [
    "Textarea",
    "Checkbox",
    "RadioGroup",
    "Switch",
    "Select",
    "Combobox",
    "Slider",
    "Spinbox",
]


def _variable(master, variable, factory, value):
    if variable is not None:
        if variable._tk is not master.tk:
            raise ValueError("Variable belongs to a different interpreter")
        return variable
    return factory(master=master, value=value)


def _color(theme, key, legacy):
    tokens = getattr(theme, "tokens", {})
    return tokens[key] if key in tokens else theme.colors[legacy]


def _portable(theme, source):
    """Copy a generic Clam element instead of inheriting Aqua's native drawing."""
    name = theme.name(f"inputs.portable.{source}")
    if name not in theme.style.element_names():
        theme.style.element_create(name, "from", "clam", source)
    return name


class Textarea(Owned, tk.Text):
    """Native multiline Text, including indices, undo, tags and validation state."""

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        self._custom_colors = set(options)
        options.setdefault("wrap", "word")
        options.setdefault("undo", True)
        super().__init__(master, **options)
        self._own(master, theme)
        self._refresh_theme()

    def _refresh_theme(self):
        theme = self.theme
        options = dict(
            background=_color(theme, "background", "surface"),
            foreground=_color(theme, "foreground", "text"),
            insertbackground=_color(theme, "foreground", "text"),
            selectbackground=_color(theme, "primary", "accent"),
            selectforeground=_color(theme, "primary_foreground", "surface"),
            highlightbackground=_color(theme, "input", "muted"),
            highlightcolor=_color(theme, "ring", "accent"),
            font=theme.font,
        )
        super().configure(**{k: v for k, v in options.items() if k not in self._custom_colors})


class Checkbox(Owned, ttk.Checkbutton):
    """Native checkbutton; ``variable``, on/off values and invoke are preserved."""

    def __init__(self, master, *, variable=None, theme=None, **options):
        theme = resolve_theme(master, theme)
        self.variable = _variable(master, variable, tk.StringVar, options.get("offvalue", "0"))
        options.setdefault("style", theme.name("TCheckbutton"))
        super().__init__(master, variable=self.variable, **options)
        self._own(master, theme)


class Switch(Checkbox):
    """Pill-and-thumb switch retaining native checkbutton interaction."""

    def __init__(self, master, *, theme=None, **options):
        theme = resolve_theme(master, theme)
        options.setdefault("style", theme.name("Switch.TCheckbutton"))
        super().__init__(master, theme=theme, **options)
        self._refresh_theme()

    def _refresh_theme(self):
        theme = self.theme
        c, style = theme.tokens, theme.style
        images = {}
        for selected in (False, True):
            for state in ("normal", "focus", "disabled"):
                track = c["primary"] if selected else c["input"]
                thumb = c["primary_foreground"] if selected else c["card"]
                if state == "disabled":
                    track, thumb = c["muted"], c["muted_foreground"]
                key = theme._image_key(f"inputs.switch.{selected}.{state}")
                width, height = theme.px(36), theme.px(20)
                data = _switch_svg(
                    width,
                    height,
                    theme.px(8),
                    track,
                    thumb,
                    c["ring"],
                    selected,
                    state == "focus",
                )
                if key in theme._images:
                    theme._images[key].configure(
                        data=data, format=("svg", "-scaletowidth", width + theme.px(8))
                    )
                else:
                    theme._images[key] = svg_photo(
                        theme.master, data, width=width + theme.px(8)
                    )
                images[selected, state] = theme._images[key]
        element = theme.name(f"inputs.switch.indicator.slot{theme._render_slot}")
        if element not in style.element_names():
            style.element_create(
                element,
                "image",
                images[False, "normal"],
                ("disabled", "selected", images[True, "disabled"]),
                ("disabled", images[False, "disabled"]),
                ("focus", "selected", images[True, "focus"]),
                ("focus", images[False, "focus"]),
                ("selected", images[True, "normal"]),
                sticky="",
            )
        name = theme.name("Switch.TCheckbutton")
        padding = _portable(theme, "Checkbutton.padding")
        label = _portable(theme, "Checkbutton.label")
        theme.surface_style(name, "card")
        style.layout(
            name,
            [
                (
                    theme.name(theme._image_key("surface.card")),
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                padding,
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (element, {"side": "left", "sticky": ""}),
                                        (label, {"side": "left", "sticky": "nsew"}),
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ],
        )
        style.configure(
            name,
            background=c["card"],
            foreground=c["foreground"],
            font=theme.font,
            padding=theme.px(2),
        )
        style.map(
            name,
            background=[("disabled", c["card"]), ("!disabled", c["card"])],
            foreground=[("disabled", c["muted_foreground"]), ("!disabled", c["foreground"])],
        )


def _switch_svg(width, height, gap, track, thumb, ring, selected, focused):
    """Return a compact switch asset for Tk 9's native SVG reader."""
    radius = height / 2
    inset = height / 10
    thumb_radius = radius - inset * 2
    thumb_x = width - radius if selected else radius
    focus = (
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" '
        f'rx="{radius - 1}" fill="none" stroke="{ring}" stroke-width="2"/>'
        if focused
        else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + gap}" height="{height}" '
        f'viewBox="0 0 {width + gap} {height}">{focus}'
        f'<rect x="{inset}" y="{inset}" width="{width - inset * 2}" '
        f'height="{height - inset * 2}" rx="{radius - inset}" fill="{track}"/>'
        f'<circle cx="{thumb_x}" cy="{radius}" r="{thumb_radius}" fill="{thumb}"/></svg>'
    )


def _chevron_svg(size, color, up=False):
    points = "6,15 12,9 18,15" if up else "6,9 12,15 18,9"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"><polyline points="{points}"/></svg>'
    )


class RadioGroup(Owned, ttk.Frame):
    """A group of native radios sharing a variable and no-argument command.

    ``values`` contains strings or ``(value, label)`` pairs. ``orient`` controls
    layout; each radio retains native focus traversal and invoke semantics.
    """

    def __init__(
        self,
        master,
        *,
        values=(),
        variable=None,
        command=None,
        orient="vertical",
        state="normal",
        theme=None,
        **options,
    ):
        if orient not in ("horizontal", "vertical"):
            raise ValueError("orient must be horizontal or vertical")
        if state not in ("normal", "disabled"):
            raise ValueError("state must be normal or disabled")
        theme = resolve_theme(master, theme)
        self.variable = _variable(master, variable, tk.StringVar, "")
        choices = [(v, v) if isinstance(v, str) else tuple(v) for v in values]
        if any(len(v) != 2 for v in choices):
            raise ValueError("values must contain strings or (value, label) pairs")
        options.setdefault("style", theme.name("TFrame"))
        super().__init__(master, **options)
        self._own(master, theme)
        self.buttons = []
        for index, (value, label) in enumerate(choices):
            button = ttk.Radiobutton(
                self,
                text=label,
                value=value,
                variable=self.variable,
                command=command,
                style=theme.name("TRadiobutton"),
            )
            button.grid(
                row=index if orient == "vertical" else 0,
                column=index if orient == "horizontal" else 0,
                sticky="w",
            )
            self.buttons.append(button)
        if state == "disabled":
            self.state(("disabled",))

    def state(self, statespec=None):
        result = super().state(statespec)
        if statespec is not None:
            for button in self.buttons:
                button.state(("disabled",) if self.instate(("disabled",)) else ("!disabled",))
        return result

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        if cnf == "state":
            return ("state", "state", "State", "normal", self.cget("state"))
        state = kwargs.pop("state", None)
        if state is not None and state not in ("normal", "disabled"):
            raise ValueError("state must be normal or disabled")
        result = super().configure(cnf, **kwargs)
        if state is not None:
            self.state(("disabled",) if state == "disabled" else ("!disabled",))
            return None
        return result

    config = configure

    def cget(self, key):
        if key == "state":
            return "disabled" if self.instate(("disabled",)) else "normal"
        return super().cget(key)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)


class Slider(Owned, ttk.Scale):  # type: ignore[misc]  # tkinter's two Scale.identify stubs conflict.
    """Native continuous scale; commands receive Tk's numeric string value."""

    def __init__(self, master, *, variable=None, theme=None, **options):
        theme = resolve_theme(master, theme)
        self.variable = _variable(master, variable, tk.DoubleVar, options.get("value", 0))
        self._scoped_style = "style" not in options
        orient = str(options.setdefault("orient", "horizontal")).capitalize()
        # Scale layouts are orientation-specific in ttk's native themes.
        options.setdefault("style", theme.name(f"{orient}.TScale"))
        super().__init__(master, variable=self.variable, **options)
        self._own(master, theme)

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        custom_style = "style" in kwargs
        if "orient" in kwargs and self._scoped_style and not custom_style:
            orient = str(kwargs["orient"]).capitalize()
            kwargs["style"] = self.theme.name(f"{orient}.TScale")
        result = super().configure(cnf, **kwargs)
        if custom_style:
            self._scoped_style = False
        return result

    config = configure


class Spinbox(Owned, ttk.Spinbox):
    """Native spinbox retaining ranges, values, wrapping and entry validation."""

    def __init__(self, master, *, textvariable=None, theme=None, **options):
        theme = resolve_theme(master, theme)
        self.variable = _variable(master, textvariable, tk.StringVar, "")
        self._custom_font = "font" in options
        options.setdefault("font", theme.font)
        options.setdefault("style", theme.name("TSpinbox"))
        super().__init__(master, textvariable=self.variable, **options)
        self._own(master, theme)
        self._refresh_theme()

    def _refresh_theme(self):
        theme = self.theme
        c, style = theme.tokens, theme.style
        field = theme._element(
            "inputs.spin.field",
            [
                theme._tile("inputs.spin", c["card"], c["input"]),
                ("disabled", theme._tile("inputs.spin.disabled", c["muted"], c["border"])),
                ("invalid", theme._tile("inputs.spin.invalid", c["card"], c["destructive"], 2)),
                ("focus", theme._tile("inputs.spin.focus", c["card"], c["ring"], 2)),
            ],
        )
        arrows = []
        for direction in ("up", "down"):
            images = {}
            for state, color in (("normal", c["foreground"]), ("disabled", c["muted_foreground"])):
                key = theme._image_key(f"inputs.spin.{direction}.{state}")
                size = theme.px(12)
                data = _chevron_svg(size, color, up=direction == "up")
                if key in theme._images:
                    theme._images[key].configure(
                        data=data, format=("svg", "-scaletowidth", size)
                    )
                else:
                    theme._images[key] = svg_photo(theme.master, data, width=size)
                images[state] = theme._images[key]
            element = theme.name(
                f"inputs.spin.slot{theme._render_slot}.{direction}arrow"
            )
            if element not in style.element_names():
                style.element_create(
                    element, "image", images["normal"], ("disabled", images["disabled"]), sticky=""
                )
            arrows.append(
                (element, {"side": "top" if direction == "up" else "bottom", "sticky": ""})
            )
        padding = _portable(theme, "Spinbox.padding")
        textarea = _portable(theme, "Spinbox.textarea")
        name = theme.name("TSpinbox")
        style.layout(
            name,
            [
                (
                    field,
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                padding,
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (
                                            "null",
                                            {"side": "right", "sticky": "", "children": arrows},
                                        ),
                                        (textarea, {"sticky": "nsew"}),
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ],
        )
        style.configure(
            name,
            padding=(theme.px(10), theme.px(3)),
            fieldbackground=c["card"],
            foreground=c["foreground"],
            selectbackground=c["primary"],
            selectforeground=c["primary_foreground"],
            insertcolor=c["foreground"],
            font=theme.font,
        )
        style.map(
            name,
            fieldbackground=[("disabled", c["muted"]), ("readonly", c["card"])],
            foreground=[("disabled", c["muted_foreground"]), ("!disabled", c["foreground"])],
        )
        if not self._custom_font:
            super().configure(font=theme.font)


class Combobox(Owned, ttk.Combobox):
    """Editable native entry/value API with a private, theme-scoped popup.

    Down/Up or Alt-Down opens the list, arrows/Home/End navigate, Return commits,
    Escape cancels, and Tab dismisses before normal focus traversal. Typing in
    the popup matches prefixes. ``postcommand`` runs immediately before opening.
    No global bindings, option database entries or native popdown are used.
    """

    def __init__(self, master, *, values=(), textvariable=None, theme=None, **options):
        theme = resolve_theme(master, theme)
        self.variable = _variable(master, textvariable, tk.StringVar, "")
        self._custom_font = "font" in options
        options.setdefault("font", theme.font)
        self._popup = None
        self._listbox = None
        self._previous_grab = None
        self._previous_grab_status = None
        self._focus_check = None
        self._prefix = ""
        self._typed_at = 0.0
        options.setdefault("style", theme.name("TCombobox"))
        super().__init__(master, values=values, textvariable=self.variable, **options)
        self._own(master, theme)
        self.bindtags(tuple("TEntry" if tag == "TCombobox" else tag for tag in self.bindtags()))
        self.bind("<Button-1>", self._click)
        self.bind("<Down>", self._open_key)
        self.bind("<Up>", self._open_key)
        self.bind("<Alt-Down>", self._open_key)
        self.bind("<F4>", self._toggle_key)
        self.bind("<Escape>", self._escape)
        self.bind("<KeyPress>", self._entry_key)
        self.bind("<Unmap>", lambda event: self.close_popup(restore_focus=False))
        self.bind("<FocusOut>", self._schedule_focus_check, add="+")
        self._refresh_theme()

    def _click(self, event):
        if self.instate(("disabled",)):
            return "break"
        if self.instate(("readonly",)) or "arrow" in self.identify(event.x, event.y):
            self._toggle_key(event)
            return "break"

    def _toggle_key(self, event=None):
        if self._popup is None:
            self.open_popup()
        else:
            self.close_popup()
        return "break"

    def _open_key(self, event=None):
        self.open_popup()
        return "break"

    def _escape(self, event=None):
        self.close_popup()
        return "break"

    def _entry_key(self, event):
        if self.instate(("readonly",)) and not self.instate(("disabled",)):
            if event.char and event.char.isprintable() and not event.state & 12:
                self.open_popup()
                self._match(event.char)
                return "break"

    def open_popup(self):
        """Open this widget's list unless disabled, already open or empty."""
        if self.instate(("disabled",)) or self._popup is not None:
            return
        command = self.cget("postcommand")
        if command:
            self.tk.call("uplevel", "#0", command)
        if not self.winfo_exists() or self.instate(("disabled",)):
            return
        values = self.cget("values")
        if not values:
            return
        popup = self._popup = tk.Toplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.transient(self.winfo_toplevel())
        self._prefix = ""
        self._previous_grab = self.grab_current()
        self._previous_grab_status = (
            self._previous_grab.grab_status() if self._previous_grab is not None else None
        )
        listbox = self._listbox = tk.Listbox(
            popup,
            exportselection=False,
            activestyle="dotbox",
            borderwidth=0,
            highlightthickness=0,
            height=max(1, min(len(values), int(self.cget("height")))),
            takefocus=True,
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(
            popup,
            command=listbox.yview,
            takefocus=False,
            style=self.theme.name("Vertical.TScrollbar"),
        )
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.insert("end", *values)
        self._refresh_theme()
        self._activate(max(0, self.current()))
        listbox.bind("<KeyPress>", self._popup_key)
        listbox.bind("<ButtonRelease-1>", self._choose_click)
        popup.bind("<ButtonPress-1>", self._outside_click, add="+")
        popup.bind("<FocusOut>", self._schedule_focus_check, add="+")
        popup.update_idletasks()
        width = min(self.winfo_screenwidth(), max(self.winfo_width(), popup.winfo_reqwidth()))
        height = min(self.winfo_screenheight(), popup.winfo_reqheight())
        x = max(0, min(self.winfo_rootx(), self.winfo_screenwidth() - width))
        y = self.winfo_rooty() + self.winfo_height()
        if y + height > self.winfo_screenheight():
            y = max(0, self.winfo_rooty() - height)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.deiconify()
        popup.lift()
        try:
            popup.grab_set()
            listbox.focus_force()
        except tk.TclError:
            self.close_popup(restore_focus=False)
            raise

    def _activate(self, index):
        if self._listbox is None or not self._listbox.size():
            return
        index = max(0, min(index, self._listbox.size() - 1))
        self._listbox.selection_clear(0, "end")
        self._listbox.selection_set(index)
        self._listbox.activate(index)
        self._listbox.see(index)

    def _popup_key(self, event):
        if self._listbox is None:
            return "break"
        if self.instate(("disabled",)):
            self.close_popup(restore_focus=False)
            return "break"
        key = event.keysym
        if key in ("Escape", "F4"):
            self.close_popup()
        elif key in ("Return", "KP_Enter", "space"):
            self._commit()
        elif key in ("Tab", "ISO_Left_Tab"):
            backward = key == "ISO_Left_Tab" or event.state & 1
            self.close_popup()
            target = self.tk_focusPrev() if backward else self.tk_focusNext()
            if target is not None:
                target.focus_set()
        elif key in ("Up", "Down", "Home", "End", "Prior", "Next"):
            current = self._listbox.index("active")
            index = {
                "Up": current - 1,
                "Down": current + 1,
                "Home": 0,
                "End": self._listbox.size() - 1,
                "Prior": current - int(self.cget("height")),
                "Next": current + int(self.cget("height")),
            }[key]
            self._activate(index)
        elif event.char and event.char.isprintable() and not event.state & 12:
            self._match(event.char)
        return "break"

    def _match(self, char):
        if self._listbox is None:
            return
        now = time.monotonic()
        self._prefix = (self._prefix if now - self._typed_at < 1 else "") + char.casefold()
        self._typed_at = now
        values = [str(v).casefold() for v in self._listbox.get(0, "end")]
        matches = [i for i, value in enumerate(values) if value.startswith(self._prefix)]
        if not matches:
            self._prefix = char.casefold()
            start = self._listbox.index("active") + 1
            matches = [
                i % len(values)
                for i in range(start, start + len(values))
                if values[i % len(values)].startswith(self._prefix)
            ]
        if matches:
            self._activate(matches[0])

    def _choose_click(self, event):
        if self._listbox is None:
            return "break"
        index = self._listbox.nearest(event.y)
        box = self._listbox.bbox(index)
        if (
            box
            and 0 <= event.x < self._listbox.winfo_width()
            and box[1] <= event.y < box[1] + box[3]
        ):
            self._activate(index)
            self._commit()
        return "break"

    def _commit(self):
        if self._listbox is None or self.instate(("disabled",)):
            self.close_popup(restore_focus=False)
            return
        selection = self._listbox.curselection()
        value = self._listbox.get(selection[0]) if selection else None
        self.close_popup()
        if value is not None:
            self.set(value)
            if self.winfo_exists():
                self.event_generate("<<ComboboxSelected>>", when="tail")

    def _outside_click(self, event):
        popup = self._popup
        if popup is not None and not (
            popup.winfo_rootx() <= event.x_root < popup.winfo_rootx() + popup.winfo_width()
            and popup.winfo_rooty() <= event.y_root < popup.winfo_rooty() + popup.winfo_height()
        ):
            self.close_popup()
            return "break"

    def _schedule_focus_check(self, event=None):
        if self._popup is not None and self._focus_check is None:
            self._focus_check = self.after_idle(self._check_focus)

    def _check_focus(self):
        self._focus_check = None
        focus = self.focus_get()
        if self._popup is not None and focus is not self:
            if focus is None or not str(focus).startswith(str(self._popup) + "."):
                self.close_popup(restore_focus=False)

    def close_popup(self, *, restore_focus=True):
        """Cancel the pending choice and release only this popup's local grab."""
        if self._focus_check is not None:
            self.after_cancel(self._focus_check)
            self._focus_check = None
        popup = self._popup
        if popup is None:
            return
        self._popup = self._listbox = None
        previous = self._previous_grab
        self._previous_grab = None
        try:
            owns_grab = popup.grab_current() is popup
            if owns_grab:
                popup.grab_release()
            popup.destroy()
            if owns_grab and previous is not None and previous.winfo_exists():
                if self._previous_grab_status == "global":
                    previous.grab_set_global()
                else:
                    previous.grab_set()
            if restore_focus and self.winfo_exists():
                self.focus_force()
        except tk.TclError:
            # Destruction may already have removed both owner and popup in Tcl.
            pass

    def _refresh_theme(self):
        theme = self.theme
        c, style = theme.tokens, theme.style
        normal = theme._tile("inputs.combo", c["card"], c["input"])
        focused = theme._tile("inputs.combo.focus", c["card"], c["ring"], 2)
        invalid = theme._tile("inputs.combo.invalid", c["card"], c["destructive"], 2)
        disabled = theme._tile("inputs.combo.disabled", c["muted"], c["border"])
        field = theme._element(
            "inputs.combo.field",
            [
                normal,
                ("disabled", disabled),
                ("invalid", invalid),
                ("focus", focused),
            ],
        )
        images = {}
        for state, color in (("normal", c["foreground"]), ("disabled", c["muted_foreground"])):
            key = theme._image_key(f"inputs.combo.chevron.{state}")
            size = theme.px(16)
            data = _chevron_svg(size, color)
            if key in theme._images:
                theme._images[key].configure(data=data, format=("svg", "-scaletowidth", size))
            else:
                theme._images[key] = svg_photo(theme.master, data, width=size)
            images[state] = theme._images[key]
        arrow = theme.name(f"inputs.combo.chevron.downarrow.slot{theme._render_slot}")
        if arrow not in style.element_names():
            style.element_create(
                arrow, "image", images["normal"], ("disabled", images["disabled"]), sticky=""
            )
        padding = _portable(theme, "Combobox.padding")
        textarea = _portable(theme, "Combobox.textarea")
        name = theme.name("TCombobox")
        style.layout(
            name,
            [
                (
                    field,
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                padding,
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (arrow, {"side": "right", "sticky": ""}),
                                        (textarea, {"sticky": "nsew"}),
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ],
        )
        base = {"compact": 28, "default": 32, "comfortable": 36}[theme.density]
        style.configure(
            name,
            padding=(theme.px(10), theme.px((base - 18) / 2)),
            fieldbackground=c["card"],
            foreground=c["foreground"],
            background=c["card"],
            borderwidth=0,
            font=theme.font,
            insertcolor=c["foreground"],
            selectbackground=c["primary"],
            selectforeground=c["primary_foreground"],
        )
        style.map(
            name,
            fieldbackground=[("disabled", c["muted"]), ("readonly", c["card"])],
            foreground=[("disabled", c["muted_foreground"])],
        )
        if not self._custom_font:
            super().configure(font=theme.font)
        if self._popup is not None and self._listbox is not None:
            self._popup.configure(background=c["border"], padx=theme.px(1), pady=theme.px(1))
            self._listbox.configure(
                background=_color(theme, "popover", "surface"),
                foreground=_color(theme, "popover_foreground", "text"),
                selectbackground=_color(theme, "accent", "accent"),
                selectforeground=_color(theme, "accent_foreground", "surface"),
                font=theme.font,
            )

    def configure(self, cnf=None, **kwargs):
        result = super().configure(cnf, **kwargs)
        if kwargs or isinstance(cnf, dict):
            self.close_popup(restore_focus=False)
        return result

    config = configure

    def state(self, statespec=None):
        result = super().state(statespec)
        if statespec is not None and self.instate(("disabled",)):
            self.close_popup(restore_focus=False)
        return result

    def destroy(self):
        self.close_popup(restore_focus=False)
        super().destroy()

    def _cleanup(self):
        self.close_popup(restore_focus=False)
        super()._cleanup()


class Select(Combobox):
    """Choice-only combobox: normal state remains readonly; disabled is native."""

    def __init__(self, master, *, theme=None, **options):
        if options.get("state", "normal") == "normal":
            options["state"] = "readonly"
        super().__init__(master, theme=theme, **options)

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        if kwargs.get("state") == "normal":
            kwargs["state"] = "readonly"
        return super().configure(cnf, **kwargs)

    config = configure

    def state(self, statespec=None):
        if statespec is not None:
            if isinstance(statespec, str):
                statespec = self.tk.splitlist(statespec)
            statespec = tuple(s for s in statespec if s != "!readonly") + ("readonly",)
        return super().state(statespec)
