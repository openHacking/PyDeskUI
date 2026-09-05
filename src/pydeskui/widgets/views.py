"""Small collection, detail, progress and nonblocking dialog primitives."""

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from ..scheduling import Scheduler
from ..theme import resolve_theme
from ._base import Owned
from .controls import Button


@dataclass(frozen=True)
class Item:
    id: str
    title: str
    subtitle: str = ""


class _AutoScrollbar(ttk.Scrollbar):
    def set(self, first, last):
        super().set(first, last)
        if float(first) <= 0 and float(last) >= 1:
            self.grid_remove()
        else:
            self.grid()


class ItemList(Owned, ttk.Frame):
    """Single-selection Treeview wrapper with stable string IDs."""

    def __init__(self, master, *, on_select=None, theme=None):
        theme = resolve_theme(master, theme)
        super().__init__(master, style=theme.name("TFrame"))
        self._own(master, theme)
        self.on_select = on_select
        self._selected = None
        self.tree = ttk.Treeview(
            self,
            columns=("subtitle",),
            show="tree",
            selectmode="browse",
            style=theme.name("Treeview"),
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = _AutoScrollbar(
            self, command=self.tree.yview, style=theme.name("Vertical.TScrollbar")
        )
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)
        self.empty = ttk.Label(self, style=theme.name("TLabel"))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._changed)
        self._refresh_theme()
        self.set_items([])

    def _refresh_theme(self):
        self.empty.configure(text=self._t("No items"))

    def selected_id(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _changed(self, event=None):
        selected = self.selected_id()
        if selected != self._selected:
            self._selected = selected
            if self.on_select:
                self.on_select(selected)

    def set_items(self, items):
        items = tuple(items)
        ids = [item.id for item in items]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError("Item IDs must be unique nonempty strings")
        selected = self.selected_id()
        old = set(self.tree.get_children())
        for identifier in old - set(ids):
            self.tree.delete(identifier)
        for index, item in enumerate(items):
            label = item.title + (f" — {item.subtitle}" if item.subtitle else "")
            if item.id in old:
                self.tree.item(item.id, text=label)
                self.tree.move(item.id, "", index)
            else:
                self.tree.insert("", index, iid=item.id, text=label)
        if selected is not None and selected in ids:
            self.tree.selection_set(selected)
        if items:
            self.empty.grid_remove()
        else:
            self.empty.grid(row=1, column=0, sticky="w")
        self._changed()


class DetailView(Owned, ttk.Frame):
    """Readonly scrollable text/code; content is never evaluated."""

    def __init__(self, master, *, theme=None):
        theme = resolve_theme(master, theme)
        super().__init__(master, style=theme.name("TFrame"))
        self._own(master, theme)
        self.title = ttk.Label(self, style=theme.name("TLabel"))
        self.title.grid(row=0, column=0, sticky="w")
        self.text = tk.Text(
            self,
            wrap="word",
            state="disabled",
            width=60,
            height=14,
            borderwidth=0,
            highlightthickness=0,
            padx=12,
            pady=12,
        )
        self.text.grid(row=1, column=0, sticky="nsew")
        horizontal = _AutoScrollbar(
            self,
            orient="horizontal",
            command=self.text.xview,
            style=theme.name("Horizontal.TScrollbar"),
        )
        self.horizontal = horizontal
        horizontal.grid(row=2, column=0, sticky="ew")
        horizontal.grid_remove()
        self.text.configure(xscrollcommand=horizontal.set)
        scroll = _AutoScrollbar(
            self, command=self.text.yview, style=theme.name("Vertical.TScrollbar")
        )
        scroll.grid(row=1, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scroll.set)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._format = "text"
        self._refresh_theme()

    def _refresh_theme(self):
        self.text.configure(
            background=self.theme.colors["surface"],
            foreground=self.theme.colors["text"],
            insertbackground=self.theme.colors["text"],
            font="TkFixedFont" if self._format == "code" else self.theme.font,
        )

    def set_content(self, title, body, format="text"):
        if format not in ("text", "code"):
            raise ValueError("format must be text or code")
        self._format = format
        if format == "code":
            self.horizontal.grid()
        else:
            self.horizontal.grid_remove()
        self.title.configure(text=title)
        self.text.configure(state="normal", wrap="none" if format == "code" else "word")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", body)
        self.text.configure(state="disabled")
        self._refresh_theme()


class _Progressbar(ttk.Progressbar):
    """Native progress value/API with a deterministic noninteractive paint layer."""

    def __init__(self, master, *, theme, **options):
        self.theme = theme
        super().__init__(master, **options)
        self._paint = tk.Canvas(
            self, height=theme.px(6), borderwidth=0, highlightthickness=0, takefocus=False
        )
        self._paint.place(x=0, y=0, relwidth=1, relheight=1)
        self._paint.bind("<Configure>", self._draw)
        self._refresh_theme()

    def configure(self, cnf=None, **options):
        result = super().configure(cnf, **options)
        if hasattr(self, "_paint"):
            self._draw()
        return result

    config = configure

    def step(self, amount=1):
        super().step(amount)
        self._draw()

    def _refresh_theme(self):
        self._paint.configure(background=self.theme.tokens["card"])
        self._draw()

    def _draw(self, event=None):
        paint = self._paint
        width, height = paint.winfo_width(), paint.winfo_height()
        if width < 2 or height < 2:
            return
        paint.delete("all")
        stroke = min(height, self.theme.px(6))
        left, right, y = stroke / 2, max(stroke / 2, width - stroke / 2), height / 2
        paint.create_line(
            left,
            y,
            right,
            y,
            width=stroke,
            capstyle="round",
            fill=self.theme.tokens["muted"],
            tags="track",
        )
        maximum = float(self.cget("maximum")) or 1
        fraction = min(1, max(0, float(self.cget("value")) / maximum))
        if str(self.cget("mode")) == "indeterminate":
            start = left + fraction * (right - left) * 0.78
            end = min(right, start + (right - left) * 0.22)
        elif fraction:
            start, end = left, max(left + 0.01, left + (right - left) * fraction)
        else:
            return
        paint.create_line(
            start,
            y,
            end,
            y,
            width=stroke,
            capstyle="round",
            fill=self.theme.tokens["primary"],
            tags="progress",
        )


class ProgressView(Owned, ttk.Frame):
    """Determinate or indeterminate progress with optional cancellation."""

    def __init__(self, master, *, on_cancel=None, theme=None):
        theme = resolve_theme(master, theme)
        super().__init__(master, style=theme.name("TFrame"))
        self._own(master, theme)
        self.label = ttk.Label(self, style=theme.name("TLabel"))
        self.label.pack(fill="x")
        self.bar = _Progressbar(self, theme=theme, maximum=1, style=theme.name("TProgressbar"))
        self.bar.pack(fill="x", pady=(8, 12))
        self.cancel = Button(self, command=on_cancel, theme=theme)
        if on_cancel:
            self.cancel.pack(anchor="e")
        self.scheduler = Scheduler(self)
        self._tick = None
        self._refresh_theme()

    def _refresh_theme(self):
        self.cancel.configure(text=self._t("Cancel"))
        self.bar._refresh_theme()
        if self.theme.reduced_motion and self._tick:
            self._tick.cancel()
            self._tick = None

    def update_progress(self, value=None, message=""):
        if value is not None and (not math.isfinite(value) or not 0 <= value <= 1):
            raise ValueError("Progress must be None or between 0 and 1")
        if self._tick:
            self._tick.cancel()
        self.label.configure(text=message)
        self.bar.configure(
            mode="indeterminate" if value is None else "determinate",
            value=0 if value is None else value,
        )
        if value is None and not self.theme.reduced_motion:
            self._animate()

    def _animate(self):
        self.bar.step(0.02)
        self._tick = self.scheduler.call_later(40, self._animate)

    def _cleanup(self):
        self.scheduler.close()


class Dialog(Owned, tk.Toplevel):
    """Nonblocking modal dialog; actions are (stable_id, visible_label) pairs."""

    def __init__(
        self,
        master,
        *,
        title,
        message,
        actions,
        theme=None,
        default_action=None,
        cancel_action=None,
    ):
        actions = tuple(actions)
        if len({action[0] for action in actions}) != len(actions):
            raise ValueError("Action IDs must be unique")
        ids = {action[0] for action in actions}
        if default_action is not None and default_action not in ids:
            raise ValueError("Unknown default action")
        if cancel_action is not None and cancel_action not in ids:
            raise ValueError("Unknown cancel action")
        self.default_action, self.cancel_action = default_action, cancel_action
        theme = resolve_theme(master, theme)
        super().__init__(master)
        self.withdraw()
        self._own(master, theme)
        self.title(title)
        self.transient(master.winfo_toplevel())
        self._callback = None
        self._finished = False
        self._invoker = master.focus_get()
        self._previous_grab = master.grab_current()
        ttk.Label(self, text=message, wraplength=480, padding=16, style=theme.name("TLabel")).pack(
            fill="both", expand=True
        )
        row = ttk.Frame(self, style=theme.name("TFrame"))
        row.pack(fill="x", padx=16, pady=12)
        self._buttons = []
        for identifier, label in actions:
            button = Button(
                row,
                text=label,
                command=lambda i=identifier: self._finish(i),
                theme=theme,
                variant="primary" if identifier == default_action else "outline",
            )
            button.pack(side="right", padx=4)
            self._buttons.append(button)
        self.protocol("WM_DELETE_WINDOW", lambda: self._finish(self.cancel_action))
        self.bind("<Escape>", lambda event: self._finish(self.cancel_action))
        self.bind("<Return>", self._return_action)
        self._refresh_theme()

    def _return_action(self, event):
        if isinstance(event.widget, Button):
            return None
        if self.default_action is not None:
            self._finish(self.default_action)
        return "break"

    def _refresh_theme(self):
        self.configure(background=self.theme.tokens["card"])

    def show(self, on_result):
        if self._finished or self._callback is not None:
            raise RuntimeError("Dialog may only be shown once")
        self._callback = on_result
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.deiconify()
        self.grab_set()
        (self._buttons[0] if self._buttons else self).focus_set()

    def _finish(self, result):
        if self._finished:
            return
        self._finished = True
        callback, self._callback = self._callback, None
        self.destroy()
        if callback:
            callback(result)

    def _cleanup(self):
        callback = self._callback if not self._finished else None
        self._callback = None
        self._finished = True
        try:
            if self._previous_grab and self._previous_grab.winfo_exists():
                self._previous_grab.grab_set()
            if self._invoker and self._invoker.winfo_exists():
                self._invoker.focus_set()
        except tk.TclError:
            pass
        if callback:
            callback(None)
