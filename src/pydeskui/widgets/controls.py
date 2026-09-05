"""Native controls with explicit parenting and scoped appearance."""

import tkinter as tk
from tkinter import ttk

from ..scheduling import Scheduler
from ..theme import resolve_theme
from ._base import Owned


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
        theme=None,
        **ttk_options,
    ):
        self._validate(variant, size)
        self.variant, self._size = variant, size
        theme = resolve_theme(master, theme)
        ttk_options.setdefault("style", theme.name(f"{variant}.{size}.TButton"))
        super().__init__(master, text=text, command=command, **ttk_options)
        self._own(master, theme)
        self.bind("<Return>", lambda event: self.invoke())

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
        if "variant" in kwargs or "size" in kwargs:
            variant = kwargs.pop("variant", self.variant)
            size = kwargs.pop("size", self._size)
            self._validate(variant, size)
            kwargs["style"] = self.theme.name(f"{variant}.{size}.TButton")
            self.variant, self._size = variant, size
        return super().configure(cnf, **kwargs)

    config = configure

    def cget(self, key):
        if key in ("variant", "size"):
            return self._size if key == "size" else self.variant
        return super().cget(key)


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
        self._hint = tk.Label(self, text=placeholder, anchor="w", borderwidth=0, takefocus=False)
        self._hint.bind("<Button-1>", lambda event: self.focus_set())
        self._hint_trace = self.variable.trace_add("write", self._update_hint)
        self.bind("<FocusIn>", self._update_hint, add="+")
        self.bind("<FocusOut>", self._update_hint, add="+")
        self.bind("<Configure>", self._update_hint, add="+")
        self.state(["invalid"] if invalid else ["!invalid"])
        self._refresh_theme()

    def _update_hint(self, *args):
        if self.placeholder and not self.variable.get() and self.focus_get() is not self:
            self._hint.place(
                x=self.theme.px(11),
                rely=0.5,
                anchor="w",
                width=max(0, self.winfo_width() - self.theme.px(22)),
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
        theme=None,
        **ttk_options,
    ):
        if not isinstance(debounce_ms, int) or debounce_ms < 0:
            raise ValueError("debounce_ms must be a nonnegative integer")
        self.on_change, self.debounce_ms = on_change, debounce_ms
        self._pending = None
        super().__init__(master, textvariable=textvariable, theme=theme, **ttk_options)
        self._scheduler = Scheduler(self)
        self._trace = self.variable.trace_add("write", self._changed)
        self.bind("<Escape>", self._clear)

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
        return super().configure(cnf, **kwargs)

    config = configure

    def cget(self, key):
        if key in ("on_change", "debounce_ms"):
            return getattr(self, key)
        return super().cget(key)
