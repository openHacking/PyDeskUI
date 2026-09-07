"""Native controls with explicit parenting and scoped appearance."""

import tkinter as tk
from functools import lru_cache
from importlib.resources import files
from tkinter import ttk

from ..scheduling import Scheduler
from ..theme import resolve_theme
from ._base import Owned


@lru_cache(maxsize=64)
def _icon_source(name):
    return files("pydeskui").joinpath("assets", "icons", f"{name}.svg").read_bytes()


class Button(Owned, ttk.Button):
    """A ttk button with no-argument command, variant and size options."""

    def __init__(
        self,
        master,
        *,
        text="",
        command=None,
        variant="default",
        size="medium",
        icon=None,
        icon_position="left",
        theme=None,
        **ttk_options,
    ):
        self._validate(variant, size)
        if icon_position not in ("left", "right"):
            raise ValueError("icon_position must be left or right")
        self.variant, self._size = variant, size
        self.icon, self.icon_position = icon, icon_position
        self._icon_image = None
        theme = resolve_theme(master, theme)
        ttk_options.setdefault("style", theme.name(f"{variant}.{size}.TButton"))
        if icon:
            ttk_options.setdefault("compound", icon_position)
        super().__init__(master, text=text, command=command, **ttk_options)
        self._own(master, theme)
        self.bind("<Return>", lambda event: self.invoke())
        self._refresh_theme()

    def _refresh_theme(self):
        if not self.icon:
            self._icon_image = None
            super().configure(image="")
            return
        data = _icon_source(self.icon)
        color = (
            self.theme.tokens["primary_foreground"]
            if self.variant == "primary"
            else self.theme.tokens["foreground"]
        )
        rgb = tuple(round(value / 257) for value in self.winfo_rgb(color))
        encoded = ("#%02x%02x%02x" % rgb).encode("ascii")
        data = data.replace(b"currentColor", encoded).replace(b"#000001", encoded)
        self._icon_image = self.theme.svg_icon(data, self.theme.px(18))
        super().configure(image=self._icon_image, compound=self.icon_position)

    @staticmethod
    def _validate(variant, size):
        if variant not in (
            "default",
            "primary",
            "text",
            "secondary",
            "outline",
            "ghost",
            "destructive",
            "link",
        ):
            raise ValueError("Invalid button variant")
        if size not in ("small", "medium", "large"):
            raise ValueError("Invalid button size")

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        refresh_icon = False
        if "variant" in kwargs or "size" in kwargs:
            variant = kwargs.pop("variant", self.variant)
            size = kwargs.pop("size", self._size)
            self._validate(variant, size)
            if (variant, size) != (self.variant, self._size):
                kwargs["style"] = self.theme.name(f"{variant}.{size}.TButton")
                refresh_icon = variant != self.variant
            self.variant, self._size = variant, size
        if "icon" in kwargs:
            icon = kwargs.pop("icon")
            refresh_icon = refresh_icon or icon != self.icon
            self.icon = icon
        if "icon_position" in kwargs:
            position = kwargs.pop("icon_position")
            if position not in ("left", "right"):
                raise ValueError("icon_position must be left or right")
            refresh_icon = refresh_icon or position != self.icon_position
            self.icon_position = position
        result = super().configure(cnf, **kwargs)
        if refresh_icon:
            self._refresh_theme()
        return result

    config = configure

    def cget(self, key):
        if key in ("variant", "size", "icon", "icon_position"):
            if key == "icon":
                return self.icon
            if key == "icon_position":
                return self.icon_position
            return self._size if key == "size" else self.variant
        return super().cget(key)


class NavigationItem(Button):
    """Consistent icon-and-label navigation row with an explicit selected state."""

    def __init__(self, master, *, selected=False, **options):
        self.selected = bool(selected)
        options.setdefault("variant", "secondary" if self.selected else "ghost")
        super().__init__(master, **options)

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        if "selected" in kwargs:
            selected = bool(kwargs.pop("selected"))
            if selected != self.selected:
                self.selected = selected
                kwargs["variant"] = "secondary" if selected else "ghost"
        return super().configure(cnf, **kwargs)

    config = configure

    def cget(self, key):
        if key == "selected":
            return self.selected
        return super().cget(key)


class SegmentedControl(Owned, ttk.Frame):
    """Compact single-selection control composed from themed buttons."""

    def __init__(
        self,
        master,
        *,
        values=(),
        variable=None,
        command=None,
        theme=None,
        **ttk_options,
    ):
        theme = resolve_theme(master, theme)
        if variable is not None and variable._tk is not master.tk:
            raise ValueError("Variable belongs to a different interpreter")
        options = tuple(values)
        if not options:
            raise ValueError("values must not be empty")
        normalized = []
        for option in options:
            value, label = option if isinstance(option, tuple) else (option, option)
            if not isinstance(value, str) or not value or not isinstance(label, str) or not label:
                raise ValueError("values must contain strings or nonempty (value, label) pairs")
            normalized.append((value, label))
        identifiers = [value for value, _label in normalized]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("values must be unique")
        ttk_options.setdefault("style", theme.name("TFrame"))
        super().__init__(master, **ttk_options)
        self._own(master, theme)
        self.values = tuple(normalized)
        self.variable = variable if variable is not None else tk.StringVar(master=master)
        self.command = command
        if self.variable.get() not in identifiers:
            self.variable.set(identifiers[0])
        self.buttons = []
        for index, (value, label) in enumerate(self.values):
            button = Button(
                self,
                text=label,
                command=lambda item=value: self.set(item, notify=True),
                variant="secondary" if value == self.variable.get() else "outline",
                theme=theme,
            )
            button.grid(row=0, column=index, sticky="ew")
            button.bind("<Left>", self._previous)
            button.bind("<Right>", self._next)
            self.columnconfigure(index, weight=1, uniform=f"segment-{id(self):x}")
            self.buttons.append(button)
        self._trace = self.variable.trace_add("write", self._sync)
        self._sync()

    def get(self):
        return self.variable.get()

    def set(self, value, *, notify=False):
        if value not in {identifier for identifier, _label in self.values}:
            raise ValueError(f"Unknown segment: {value!r}")
        changed = value != self.variable.get()
        self.variable.set(value)
        if changed and notify and self.command:
            self.command()

    def _move(self, step):
        identifiers = [value for value, _label in self.values]
        index = identifiers.index(self.variable.get())
        target = (index + step) % len(identifiers)
        self.set(identifiers[target], notify=True)
        self.buttons[target].focus_set()
        return "break"

    def _previous(self, _event):
        return self._move(-1)

    def _next(self, _event):
        return self._move(1)

    def _sync(self, *_args):
        selected = self.variable.get()
        for button, (value, _label) in zip(self.buttons, self.values):
            button.configure(variant="secondary" if value == selected else "outline")

    def _cleanup(self):
        self.variable.trace_remove("write", self._trace)


class Entry(Owned, ttk.Entry):
    """A native entry preserving a caller-owned StringVar and validation."""

    def __init__(
        self, master, *, textvariable=None, theme=None, placeholder="", invalid=False, **ttk_options
    ):
        theme = resolve_theme(master, theme)
        if textvariable is not None and textvariable._tk is not master.tk:
            raise ValueError("Variable belongs to a different interpreter")
        self.variable = textvariable if textvariable is not None else tk.StringVar(master=master)
        ttk_options.setdefault("style", theme.name("TEntry"))
        super().__init__(master, textvariable=self.variable, **ttk_options)
        self._own(master, theme)
        self.placeholder = placeholder
        self._leading_width = getattr(self, "_leading_width", 0)
        self._trailing_width = getattr(self, "_trailing_width", 0)
        self._hint = tk.Label(self, text=placeholder, anchor="w", borderwidth=0, takefocus=False)
        self._hint.bind("<Button-1>", lambda event: self.focus_set())
        self._hint_trace = self.variable.trace_add("write", self._update_hint)
        self.bind("<FocusIn>", self._update_hint, add="+")
        self.bind("<FocusOut>", self._update_hint, add="+")
        self.bind("<Configure>", self._update_hint, add="+")
        self.state(["invalid"] if invalid else ["!invalid"])
        self._refresh_theme()

    def _update_hint(self, *args):
        if self.placeholder and not self.variable.get():
            self._hint.place(
                x=self.theme.px(11) + self._leading_width,
                rely=0.5,
                anchor="w",
                width=max(
                    0,
                    self.winfo_width()
                    - self.theme.px(22)
                    - self._leading_width
                    - self._trailing_width,
                ),
            )
        else:
            self._hint.place_forget()

    def _refresh_theme(self):
        self._hint.configure(
            background=self.theme.tokens["card"],
            foreground=self.theme.tokens["muted_foreground"],
            font=self.theme.font,
        )
        self._update_hint()

    def _cleanup(self):
        self.variable.trace_remove("write", self._hint_trace)


class SearchEntry(Entry):
    """Debounced entry; Escape clears, destruction cancels pending delivery."""

    def __init__(
        self,
        master,
        *,
        textvariable=None,
        on_change=None,
        debounce_ms=150,
        search_icon=True,
        shortcut_hint="",
        theme=None,
        **ttk_options,
    ):
        if not isinstance(debounce_ms, int) or debounce_ms < 0:
            raise ValueError("debounce_ms must be a nonnegative integer")
        self.on_change, self.debounce_ms = on_change, debounce_ms
        self.search_icon, self.shortcut_hint = bool(search_icon), shortcut_hint
        self._leading_width = 24 if self.search_icon else 0
        self._trailing_width = 54 if shortcut_hint else 0
        self._pending = None
        super().__init__(master, textvariable=textvariable, theme=theme, **ttk_options)
        self._search_image = None
        self._search_label = tk.Label(self, borderwidth=0, takefocus=False)
        self._shortcut_label = tk.Label(
            self, text=shortcut_hint, borderwidth=0, takefocus=False, padx=self.theme.px(5)
        )
        self._search_label.bind("<Button-1>", lambda event: self.focus_set())
        self._shortcut_label.bind("<Button-1>", lambda event: self.focus_set())
        self._scheduler = Scheduler(self)
        self._trace = self.variable.trace_add("write", self._changed)
        self.bind("<Escape>", self._clear)
        self._refresh_theme()
        self._update_hint()

    def _refresh_theme(self):
        super()._refresh_theme()
        if not hasattr(self, "_search_label"):
            return
        for label in (self._search_label, self._shortcut_label):
            label.configure(
                background=self.theme.tokens["card"],
                foreground=self.theme.tokens["muted_foreground"],
                font=self.theme.font,
            )
        if self.search_icon:
            data = _icon_source("search")
            rgb = tuple(
                round(value / 257)
                for value in self.winfo_rgb(self.theme.tokens["muted_foreground"])
            )
            encoded = ("#%02x%02x%02x" % rgb).encode("ascii")
            self._search_image = self.theme.svg_icon(
                data.replace(b"currentColor", encoded).replace(b"#000001", encoded),
                self.theme.px(17),
            )
            self._search_label.configure(image=self._search_image)

    def _update_hint(self, *args):
        super()._update_hint(*args)
        if not hasattr(self, "_search_label"):
            return
        empty = not self.variable.get()
        if self.search_icon and empty:
            self._search_label.place(x=self.theme.px(10), rely=0.5, anchor="w")
        else:
            self._search_label.place_forget()
        if self.shortcut_hint and empty:
            self._shortcut_label.place(
                x=self.winfo_width() - self.theme.px(10), rely=0.5, anchor="e"
            )
        else:
            self._shortcut_label.place_forget()

    def _clear(self, event=None):
        if (
            not self.instate(("disabled",))
            and not self.instate(("readonly",))
            and self.variable.get()
        ):
            self.variable.set("")
        return "break"

    def _changed(self, *args):
        if self._pending:
            self._pending.cancel()
        self._pending = self._scheduler.call_later(self.debounce_ms, self._deliver)

    def _deliver(self):
        self._pending = None
        if self.on_change:
            self.on_change(self.variable.get())

    def _cleanup(self):
        self.variable.trace_remove("write", self._trace)
        self._scheduler.close()
        super()._cleanup()

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        delay = kwargs.pop("debounce_ms", self.debounce_ms)
        if not isinstance(delay, int) or delay < 0:
            raise ValueError("debounce_ms must be a nonnegative integer")
        self.debounce_ms = delay
        self.on_change = kwargs.pop("on_change", self.on_change)
        self.search_icon = kwargs.pop("search_icon", self.search_icon)
        self.shortcut_hint = kwargs.pop("shortcut_hint", self.shortcut_hint)
        return super().configure(cnf, **kwargs)

    config = configure

    def cget(self, key):
        if key in ("on_change", "debounce_ms", "search_icon", "shortcut_hint"):
            return getattr(self, key)
        return super().cget(key)
