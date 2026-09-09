"""Dependency-free overlays with explicit ownership and local styling.

Popup coordinates are screen coordinates. Menus accept (label, command) pairs
or None separators. Sheet is a Frame: pack/grid content into ``sheet.content``
and call show()/hide() instead of managing the sheet itself.
"""

import tkinter as tk
import weakref
from functools import partial
from tkinter import ttk
from typing import Any, cast

from ..theme import resolve_theme
from ._base import Owned
from .controls import Button

__all__ = [
    "Tooltip",
    "Popover",
    "DropdownMenu",
    "ContextMenu",
    "Alert",
    "Toast",
    "EmptyState",
    "Skeleton",
    "Sheet",
]


def _color(theme, token):
    return theme.tokens[token]


def _clamp_geometry(x, y, width, height, bounds):
    """Clamp a rectangle to (left, top, width, height), including its size."""
    left, top, available_width, available_height = bounds
    width = max(1, min(int(width), max(1, available_width)))
    height = max(1, min(int(height), max(1, available_height)))
    x = max(left, min(int(x), left + available_width - width))
    y = max(top, min(int(y), top + available_height - height))
    return x, y, width, height


def _within(widget, ancestor):
    while widget is not None:
        if widget is ancestor:
            return True
        widget = getattr(widget, "master", None)
    return False


def _restore(widget):
    try:
        if widget is not None and widget.winfo_exists() and widget.winfo_viewable():
            widget.focus_set()
    except tk.TclError:
        pass


def _delay(value):
    if not isinstance(value, int) or value < 0:
        raise ValueError("Delay must be a nonnegative integer")
    return value


class _Dismissal:
    """Scoped additive bindings; never bind_all/unbind_all or grab input."""

    def _init_dismissal(self):
        self._dismiss_bindings = []
        self._previous_focus = None
        self._focus_check = None
        self.is_open = False

    def _arm(self):
        widget = cast(Any, self)
        host = widget.master.winfo_toplevel()
        for target in dict.fromkeys((host, widget.winfo_toplevel())):
            bindings = [
                ("<ButtonPress>", self._outside),
                ("<Escape>", self._escape),
                ("<FocusOut>", self._focus_out),
            ]
            if getattr(self, "close_on_return", False):
                bindings.append(("<Return>", self._return))
            for sequence, callback in bindings:
                ident = target.bind(sequence, callback, add="+")
                self._dismiss_bindings.append((target, sequence, ident))

    def _disarm(self):
        widget = cast(Any, self)
        if self._focus_check is not None:
            try:
                widget.after_cancel(self._focus_check)
            except tk.TclError:
                pass
            self._focus_check = None
        for target, sequence, ident in self._dismiss_bindings:
            try:
                target.unbind(sequence, ident)
            except tk.TclError:
                pass
        self._dismiss_bindings.clear()

    def _outside(self, event):
        owner = getattr(self, "_owner", None)
        if (
            owner is not None
            and owner is not owner.winfo_toplevel()
            and _within(event.widget, owner)
        ):
            return
        if self.is_open and not _within(event.widget, self):
            cast(Any, self).hide(restore_focus=False)

    def _focus_out(self, event=None):
        if self.is_open and self._focus_check is None:
            widget = cast(Any, self)
            self._focus_check = widget.after_idle(self._check_focus)

    def _check_focus(self):
        self._focus_check = None
        widget = cast(Any, self)
        focus = widget.focus_get()
        if self.is_open and (focus is None or not _within(focus, self)):
            widget.hide(restore_focus=False)

    def _escape(self, event=None):
        if self.is_open:
            cast(Any, self).hide()
            return "break"

    def _return(self, event=None):
        widget = cast(Any, self)
        focus = widget.focus_get()
        if self.is_open and (focus is self or _within(focus, self)):
            widget.hide()
            return "break"


class _Popup(_Dismissal, Owned, tk.Toplevel):
    def __init__(self, master, *, theme=None, interactive=True):
        theme = resolve_theme(master, theme)
        self._init_dismissal()
        self._timers = set()
        self._interactive = interactive
        super().__init__(master, takefocus=interactive)
        self.withdraw()
        self.overrideredirect(True)
        self.transient(master.winfo_toplevel())
        self._own(master, theme)
        self._surface = ttk.Frame(self)
        self._surface.pack(fill="both", expand=True)
        self.content = tk.Frame(self._surface)
        self.content.pack(fill="both", expand=True)
        self._owner_binding = master.bind("<Destroy>", self._owner_destroyed, add="+")
        self._refresh_theme()

    def _owner_destroyed(self, event):
        if event.widget is self.master:
            self.destroy()

    def _later(self, delay, callback):
        def deliver():
            self._timers.discard(ident)
            callback()

        ident = self.after(delay, deliver)
        self._timers.add(ident)
        return ident

    def _cancel_timers(self):
        for ident in self._timers:
            try:
                self.after_cancel(ident)
            except tk.TclError:
                pass
        self._timers.clear()

    def show(self, *, anchor=None, x=None, y=None):
        """Show below anchor or at screen x/y; interactive popups take focus."""
        anchor = self.master if anchor is None else anchor
        if anchor.tk is not self.tk:
            raise ValueError("Anchor belongs to another interpreter")
        self.update_idletasks()
        if x is None:
            x = anchor.winfo_rootx()
        if y is None:
            y = anchor.winfo_rooty() + anchor.winfo_height()
        bounds = (
            self.winfo_vrootx(),
            self.winfo_vrooty(),
            self.winfo_vrootwidth(),
            self.winfo_vrootheight(),
        )
        x, y, width, height = _clamp_geometry(
            x, y, self.winfo_reqwidth(), self.winfo_reqheight(), bounds
        )
        # Explicit +negative offsets denote absolute negative screen coordinates.
        self.geometry(f"{width}x{height}+{x}+{y}")
        if not self.is_open and self._interactive:
            self._previous_focus = self.focus_get() or self.master.focus_lastfor()
            self._arm()
        self.is_open = True
        self.deiconify()
        self.lift()
        if self._interactive:
            self.focus_set()
        return self

    def hide(self, *, restore_focus=True):
        """Dismiss and cancel pending work. Safe to call repeatedly."""
        was_open = self.is_open
        self.is_open = False
        self._cancel_timers()
        self._disarm()
        self.withdraw()
        if was_open and self._interactive and restore_focus:
            _restore(self._previous_focus)
        self._previous_focus = None

    def destroy(self):
        # Restore before Tk destroys the focused native window.
        if self.winfo_exists():
            self.hide()
            super().destroy()

    def _cleanup(self):
        self._cancel_timers()
        self._disarm()
        try:
            self.master.unbind("<Destroy>", self._owner_binding)
        except tk.TclError:
            pass
        if self.is_open and self._interactive:
            _restore(self._previous_focus)
        self.is_open = False

    def _refresh_theme(self):
        theme = self.theme
        self.configure(background=_color(theme, "background"))
        self._surface.configure(style=theme.popup_style())
        self.content.configure(background=_color(self.theme, "popover"))
        if hasattr(self, "label"):
            self.label.configure(
                background=_color(self.theme, "popover"),
                foreground=_color(self.theme, "popover_foreground"),
                font=self.theme.font,
            )


class _AttachedPopup(_Dismissal, Owned, ttk.Frame):
    """Popup surface stacked inside the owner's native application window."""

    def __init__(self, master, *, theme=None, interactive=True):
        owner = master
        theme = resolve_theme(owner, theme)
        self._init_dismissal()
        self._timers = set()
        self._interactive = interactive
        self._owner = owner
        self._owner_is_destroying = False
        host = owner.winfo_toplevel()
        super().__init__(host, takefocus=interactive, style=theme.popup_style())
        self._aqua_deferred_unmap = self.tk.call("tk", "windowingsystem") == "aqua"
        self._own(owner, theme)
        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True)
        self._owner_binding = owner.bind("<Destroy>", self._owner_destroyed, add="+")
        self._refresh_theme()

    def _owner_destroyed(self, event):
        if event.widget is self._owner:
            self._owner_is_destroying = True
            self.destroy()

    def _check_focus(self):
        self._focus_check = None
        focus = self.focus_get()
        if self.is_open and focus is not self._owner and (
            focus is None or not _within(focus, self)
        ):
            self.hide(restore_focus=False)

    def _later(self, delay, callback):
        def deliver():
            self._timers.discard(ident)
            callback()

        ident = self.after(delay, deliver)
        self._timers.add(ident)
        return ident

    def _when_idle(self, callback):
        def deliver():
            self._timers.discard(ident)
            callback()

        ident = self.after_idle(deliver)
        self._timers.add(ident)
        return ident

    def _cancel_timers(self):
        for ident in self._timers:
            try:
                self.after_cancel(ident)
            except tk.TclError:
                pass
        self._timers.clear()

    def show(self, *, anchor=None, x=None, y=None):
        """Show inside the owner window; x/y remain screen coordinates."""
        anchor = self._owner if anchor is None else anchor
        if anchor.tk is not self.tk:
            raise ValueError("Anchor belongs to another interpreter")
        # Cancel Aqua's deferred unmap when a popup is reopened in the same
        # event turn. This keeps rapid toggles free of flashes and stale work.
        self._cancel_timers()
        host = self.master
        host.update_idletasks()
        self.update_idletasks()
        width = min(max(1, host.winfo_width()), self.winfo_reqwidth())
        height = min(max(1, host.winfo_height()), self.winfo_reqheight())
        host_x, host_y = host.winfo_rootx(), host.winfo_rooty()
        explicit_y = y is not None
        if x is None:
            x = anchor.winfo_rootx()
        if y is None:
            y = (
                anchor.winfo_rooty()
                + anchor.winfo_height()
                + self.theme.px(getattr(self, "_anchor_gap", 0))
            )
        relative_x, relative_y = x - host_x, y - host_y
        if not explicit_y and relative_y + height > host.winfo_height():
            relative_y = anchor.winfo_rooty() - host_y - height
        relative_x, relative_y, width, height = _clamp_geometry(
            relative_x,
            relative_y,
            width,
            height,
            (0, 0, host.winfo_width(), host.winfo_height()),
        )
        if not self.is_open and self._interactive:
            self._previous_focus = self.focus_get() or self._owner.focus_lastfor()
            self._arm()
        self.is_open = True
        self.place(x=relative_x, y=relative_y, width=width, height=height)
        self.lift()
        if self._interactive:
            self._when_idle(self._finish_show)
        return self

    def _finish_show(self):
        if not self.is_open:
            return
        try:
            self.lift()
            # A placed popup's descendants are not necessarily viewable until
            # geometry settles on Aqua.
            self.update_idletasks()
            self._focus_initial()
        except tk.TclError:
            self.hide(restore_focus=False)

    def _focus_initial(self):
        self.focus_force()

    def hide(self, *, restore_focus=True):
        was_open = self.is_open
        if not was_open:
            # In particular, do not cancel Aqua's already queued lower-then-
            # unmap sequence. Repeated hide() calls must remain idempotent.
            return
        self.is_open = False
        self._cancel_timers()
        self._disarm()
        if was_open and self._aqua_deferred_unmap:
            # Tk 9 Aqua fails to expose the area vacated by pack/place forget
            # (Tk ticket 2ef5dd8036). Lowering first lets AppKit repaint only
            # the intersecting siblings. Unmap after that paint has completed;
            # a local host expose also repairs any uncovered parent background.
            x, y = self.winfo_x(), self.winfo_y()
            width, height = self.winfo_width(), self.winfo_height()
            self.lower()
            self._when_idle(partial(self._finish_hide, x, y, width, height))
        else:
            self.place_forget()
        if was_open and self._interactive and restore_focus:
            _restore(self._previous_focus)
        self._previous_focus = None

    def _finish_hide(self, x, y, width, height):
        if self.is_open:
            return
        self.place_forget()
        try:
            self.master.event_generate(
                "<Expose>", x=x, y=y, width=width, height=height, count=0
            )
        except tk.TclError:
            pass

    def destroy(self):
        if self.winfo_exists():
            self.hide()
            super().destroy()

    def _cleanup(self):
        self._cancel_timers()
        self._disarm()
        if not self._owner_is_destroying:
            try:
                self._owner.unbind("<Destroy>", self._owner_binding)
            except tk.TclError:
                pass
        if self.is_open and self._interactive:
            _restore(self._previous_focus)
        self.is_open = False

    def _refresh_theme(self):
        self.configure(style=self.theme.popup_style())
        self.content.configure(background=_color(self.theme, "popover"))
        # Tk child geometry does not honor a ttk frame style's padding on every
        # backend (notably Aqua). Keep the content inset from the rounded tile so
        # its border and transparent corners remain visible.
        inset = self.theme.px(max(2, min(self.theme.radius, 6) / 2))
        self.content.pack_configure(padx=inset, pady=inset)


class Popover(_AttachedPopup):
    """Viewport-bounded interactive popup with predictable light dismissal."""

    def __init__(self, master, *, padding=16, close_on_return=False, theme=None):
        self.close_on_return = bool(close_on_return)
        self._initial_focus = None
        self._anchor_gap = 4
        super().__init__(master, theme=theme)
        self.content.configure(padx=self.theme.px(padding), pady=self.theme.px(padding))

    def show(self, *, anchor=None, x=None, y=None, focus=None):
        if focus is not None and not _within(focus, self):
            raise ValueError("Initial focus must belong to the popover")
        self._initial_focus = focus
        super().show(anchor=anchor, x=x, y=y)
        return self

    def toggle(self, **kwargs):
        if self.is_open:
            self.hide()
        else:
            self.show(**kwargs)
        return self

    def _focus_initial(self):
        target = self._initial_focus
        if target is not None and target.winfo_exists() and target.winfo_viewable():
            target.focus_force()
        else:
            self.focus_force()


class Tooltip(_Popup):
    """Hover help attached to master. show()/hide() also work explicitly."""

    def __init__(self, master, *, text="", delay_ms=500, theme=None):
        self.delay_ms = _delay(delay_ms)
        self._anchor_bindings = []
        super().__init__(master, theme=theme, interactive=False)
        self.label = tk.Label(
            self.content, text=text, padx=8, pady=4, wraplength=self.theme.px(320)
        )
        self.label.pack()
        for sequence, callback in (
            ("<Enter>", self._schedule),
            ("<Leave>", lambda e: self.hide()),
            ("<ButtonPress>", lambda e: self.hide()),
        ):
            ident = master.bind(sequence, callback, add="+")
            self._anchor_bindings.append((sequence, ident))
        self._refresh_theme()

    def set_text(self, text):
        self.label.configure(text=text)

    def _schedule(self, event=None):
        self._cancel_timers()
        self._later(self.delay_ms, self.show)

    def _cleanup(self):
        for sequence, ident in self._anchor_bindings:
            try:
                self.master.unbind(sequence, ident)
            except tk.TclError:
                pass
        super()._cleanup()


class DropdownMenu(_AttachedPopup):
    """Menu of (label, no-argument command) pairs and None separators.

    add_item returns a Button supporting state(["disabled"]). Keyboard Up/Down,
    Home/End and Tab traverse enabled items; Return/Space invoke the selection.
    """

    def __init__(self, master, *, items=(), theme=None):
        self.items = []
        self._separators = []
        self._anchor_gap = 4
        super().__init__(master, theme=theme)
        for item in items:
            if item is None:
                self.add_separator()
            else:
                self.add_item(*item)
        for key, step in (("<Down>", 1), ("<Up>", -1), ("<Tab>", 1), ("<Shift-Tab>", -1)):
            self.bind(key, partial(self._move, step), add="+")
        self.bind("<Home>", lambda e: self._edge(False), add="+")
        self.bind("<End>", lambda e: self._edge(True), add="+")

    def add_item(self, label, command=None, *, disabled=False):
        def invoke():
            self.hide()
            if command is not None:
                command()

        button = Button(
            self.content,
            text=label,
            command=invoke,
            theme=self.theme,
            variant="ghost",
            style=self.theme.menu_item_style(),
        )
        button.pack(fill="x", pady=1)
        for key, step in (
            ("<Down>", 1),
            ("<Up>", -1),
            ("<Tab>", 1),
            ("<Shift-Tab>", -1),
        ):
            button.bind(key, partial(self._move, step), add="+")
        button.bind("<Home>", lambda e: self._edge(False), add="+")
        button.bind("<End>", lambda e: self._edge(True), add="+")
        if disabled:
            button.state(["disabled"])
        self.items.append(button)
        return button

    def add_separator(self):
        separator = tk.Frame(self.content, height=1, background=_color(self.theme, "border"))
        separator.pack(fill="x", pady=3)
        self._separators.append(separator)
        return separator

    def _enabled(self):
        return [
            button
            for button in self.items
            if button.winfo_exists() and not button.instate(["disabled"])
        ]

    def _move(self, step, event=None):
        enabled = self._enabled()
        if enabled:
            current = self.focus_get()
            index = enabled.index(current) if current in enabled else (-1 if step > 0 else 0)
            enabled[(index + step) % len(enabled)].focus_set()
        return "break"

    def _edge(self, last):
        enabled = self._enabled()
        if enabled:
            enabled[-1 if last else 0].focus_set()
        return "break"

    def show(self, **kwargs):
        super().show(**kwargs)
        return self

    def _focus_initial(self):
        enabled = self._enabled()
        if enabled:
            enabled[0].focus_force()

    def _refresh_theme(self):
        super()._refresh_theme()
        self.theme.menu_item_style()
        for separator in self._separators:
            separator.configure(background=_color(self.theme, "border"))


class ContextMenu(DropdownMenu):
    """Dropdown bound to right click, macOS Control-click, and Shift-F10."""

    def __init__(self, master, *, items=(), theme=None):
        self._context_bindings = []
        self._context_owner = master
        super().__init__(master, items=items, theme=theme)
        sequences = ["<Button-3>", "<Shift-F10>"]
        if self.tk.call("tk", "windowingsystem") == "aqua":
            sequences += ["<Button-2>", "<Control-Button-1>"]
        for sequence in sequences:
            ident = master.bind(sequence, self._request, add="+")
            self._context_bindings.append((sequence, ident))

    def _request(self, event):
        if event.type == tk.EventType.KeyPress:
            self._later(0, self.show)
        else:
            self._later(0, lambda: self.show(x=event.x_root, y=event.y_root))
        return "break"

    def _cleanup(self):
        for sequence, ident in self._context_bindings:
            try:
                self._context_owner.unbind(sequence, ident)
            except tk.TclError:
                pass
        super()._cleanup()


_toast_stacks: weakref.WeakKeyDictionary[Any, list[Any]] = weakref.WeakKeyDictionary()


class Toast(_AttachedPopup):
    """Non-focusing in-app notification; defaults to a bottom-right stack."""

    def __init__(self, master, *, text="", duration_ms=3000, theme=None):
        self.duration_ms = _delay(duration_ms)
        super().__init__(master, theme=theme, interactive=False)
        self.label = tk.Label(
            self.content, text=text, padx=12, pady=8, wraplength=self.theme.px(360)
        )
        self.label.pack()
        self._stacked = False
        self._resize_job = None
        self._host_resize_binding = self.master.bind(
            "<Configure>", self._host_resized, add="+"
        )
        self._refresh_theme()

    def show(self, *, text=None, duration_ms=None, anchor=None, x=None, y=None):
        delay = self.duration_ms if duration_ms is None else _delay(duration_ms)
        if text is not None:
            self.label.configure(text=text)
        self._cancel_timers()
        explicit = anchor is not None or x is not None or y is not None
        if explicit:
            was_stacked = self._stacked
            self._leave_stack()
            if was_stacked:
                self._reflow_host(self.master)
            super().show(anchor=anchor, x=x, y=y)
        else:
            stack = _toast_stacks.setdefault(self.master, [])
            if self in stack:
                stack.remove(self)
            stack.append(self)
            self._stacked = True
            self.is_open = True
            while len(stack) > 3:
                stack[0].hide(restore_focus=False)
            self._reflow_stack()
        if delay:
            self._later(delay, self.hide)
        return self

    def hide(self, *, restore_focus=True):
        host = self.master
        self._leave_stack()
        super().hide(restore_focus=restore_focus)
        self._reflow_host(host)

    def _leave_stack(self):
        stack = _toast_stacks.get(self.master)
        if stack is not None and self in stack:
            stack.remove(self)
            if not stack:
                _toast_stacks.pop(self.master, None)
        self._stacked = False

    def _host_resized(self, event):
        if event.widget is self.master and self._stacked and self._resize_job is None:
            self._resize_job = self.after_idle(self._resize_reflow)

    def _resize_reflow(self):
        self._resize_job = None
        if self._stacked:
            self._reflow_stack()

    def _reflow_stack(self):
        self._reflow_host(self.master)

    @staticmethod
    def _reflow_host(host):
        stack = _toast_stacks.get(host, [])
        stack[:] = [
            toast
            for toast in stack
            if toast.winfo_exists() and toast.is_open and toast._stacked
        ]
        if not stack:
            _toast_stacks.pop(host, None)
            return
        host.update_idletasks()
        margin = stack[-1].theme.px(16)
        gap = stack[-1].theme.px(8)
        available_width = max(1, host.winfo_width() - 2 * margin)
        bottom = max(0, host.winfo_height() - margin)
        positions = {}
        for toast in reversed(stack):
            toast.label.configure(
                wraplength=max(1, min(toast.theme.px(360), available_width - toast.theme.px(24)))
            )
            toast.update_idletasks()
            width = min(available_width, toast.winfo_reqwidth())
            height = min(max(1, host.winfo_height()), toast.winfo_reqheight())
            y = max(0, bottom - height)
            positions[toast] = (max(0, host.winfo_width() - margin - width), y, width, height)
            bottom = y - gap
        for toast in stack:
            x, y, width, height = positions[toast]
            toast.place(x=x, y=y, width=width, height=height)
            toast.lift()

    def _refresh_theme(self):
        super()._refresh_theme()
        if hasattr(self, "label"):
            self.label.configure(
                background=_color(self.theme, "popover"),
                foreground=_color(self.theme, "popover_foreground"),
                font=self.theme.font,
            )
        if getattr(self, "_stacked", False):
            self._reflow_stack()

    def _cleanup(self):
        host = self.master
        self._leave_stack()
        if self._resize_job is not None:
            try:
                self.after_cancel(self._resize_job)
            except tk.TclError:
                pass
            self._resize_job = None
        try:
            host.unbind("<Configure>", self._host_resize_binding)
        except tk.TclError:
            pass
        super()._cleanup()
        self._reflow_host(host)


class Alert(Owned, tk.Frame):
    """Inline message with optional action and dismiss button.

    dismiss() destroys the alert and calls on_dismiss once. set_content updates
    its title/message. Variants: default, destructive.
    """

    def __init__(
        self,
        master,
        *,
        title="",
        message="",
        variant="default",
        action_text=None,
        command=None,
        dismissible=False,
        on_dismiss=None,
        theme=None,
        **options,
    ):
        if variant not in ("default", "destructive"):
            raise ValueError("variant must be default or destructive")
        theme = resolve_theme(master, theme)
        self.variant, self.on_dismiss = variant, on_dismiss
        self._dismissed = False
        super().__init__(master, **options)
        self._own(master, theme)
        self.title_label = tk.Label(self, text=title, anchor="w", justify="left")
        self.title_label.pack(fill="x", padx=12, pady=(8, 0))
        self.message_label = tk.Label(
            self, text=message, anchor="w", justify="left", wraplength=self.theme.px(400)
        )
        self.message_label.pack(fill="x", padx=12, pady=(0, 8))
        self.action = None
        if action_text is not None:
            self.action = Button(self, text=action_text, command=command, theme=theme)
            self.action.pack(side="left", padx=8, pady=4)
        self.close_button = None
        if dismissible:
            self.close_button = Button(self, text="Dismiss", command=self.dismiss, theme=theme)
            self.close_button.pack(side="right", padx=8, pady=4)
        self._refresh_theme()

    def set_content(self, *, title=None, message=None):
        if title is not None:
            self.title_label.configure(text=title)
        if message is not None:
            self.message_label.configure(text=message)

    def dismiss(self):
        if self._dismissed:
            return
        self._dismissed = True
        callback = self.on_dismiss
        self.destroy()
        if callback is not None:
            callback()

    def _refresh_theme(self):
        background = _color(self.theme, "background")
        foreground = _color(
            self.theme, "destructive" if self.variant == "destructive" else "foreground"
        )
        self.configure(
            background=background,
            highlightthickness=1,
            highlightbackground=_color(self.theme, "border"),
        )
        for label in (self.title_label, self.message_label):
            label.configure(background=background, foreground=foreground, font=self.theme.font)


class EmptyState(Alert):
    """Inline empty-result title/message and optional action, using Alert's API."""

    def __init__(self, master, *, title="No items", message="", theme=None, **options):
        super().__init__(master, title=title, message=message, theme=theme, **options)


class Skeleton(Owned, tk.Canvas):
    """Static placeholder bars (also static with reduced_motion enabled)."""

    def __init__(self, master, *, lines=3, width=240, line_height=12, gap=8, theme=None, **options):
        if not isinstance(lines, int) or lines < 1 or line_height < 1 or gap < 0:
            raise ValueError("lines/line_height must be positive; gap must be nonnegative")
        theme = resolve_theme(master, theme)
        self.lines, self.line_height, self.gap = lines, line_height, gap
        self._logical_width = width
        options.setdefault("highlightthickness", 0)
        super().__init__(
            master,
            width=width,
            height=lines * line_height + (lines - 1) * gap,
            takefocus=False,
            **options,
        )
        self._own(master, theme)
        self.bind("<Configure>", self._draw, add="+")
        self._refresh_theme()

    def _draw(self, event=None):
        self.delete("skeleton")
        width = event.width if event is not None else self.winfo_width()
        if width <= 1:
            width = int(self.cget("width"))
        for index in range(self.lines):
            line_height = self.theme.px(self.line_height)
            gap = self.theme.px(self.gap) if self.gap else 0
            y = index * (line_height + gap)
            end = width * (0.65 if index == self.lines - 1 else 1)
            self.create_rectangle(
                0,
                y,
                end,
                y + line_height,
                width=0,
                fill=_color(self.theme, "muted"),
                tags="skeleton",
            )

    def _refresh_theme(self):
        gap = self.theme.px(self.gap) if self.gap else 0
        self.configure(
            background=_color(self.theme, "background"),
            width=self.theme.px(self._logical_width),
            height=self.lines * self.theme.px(self.line_height) + (self.lines - 1) * gap,
        )
        self._draw()


class Sheet(_Dismissal, Owned, tk.Frame):
    """Application-internal edge panel. Add children to .content.

    show(focus=widget) optionally selects initial focus; hide restores it.
    side is left/right/top/bottom; size is logical pixels, clamped to the parent.
    on_close runs once per visible-to-hidden transition.
    """

    def __init__(self, master, *, side="right", size=320, title="", on_close=None, theme=None):
        if side not in ("left", "right", "top", "bottom"):
            raise ValueError("Invalid sheet side")
        if not isinstance(size, int) or size < 1:
            raise ValueError("size must be a positive integer")
        theme = resolve_theme(master, theme)
        self._init_dismissal()
        self.side, self._size, self.on_close = side, size, on_close
        super().__init__(master, takefocus=True)
        self._own(master, theme)
        self.heading = tk.Label(self, text=title, anchor="w")
        self.heading.pack(fill="x", padx=12, pady=8)
        self.close_button = Button(self, text="Close", command=self.hide, theme=theme)
        self.close_button.pack(side="bottom", anchor="e", padx=8, pady=8)
        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True, padx=12, pady=4)
        self._resize_binding = master.bind("<Configure>", self._resize, add="+")
        self._refresh_theme()

    def _resize(self, event=None):
        if not self.is_open or (event is not None and event.widget is not self.master):
            return
        horizontal = self.side in ("left", "right")
        extent = self.master.winfo_width() if horizontal else self.master.winfo_height()
        size = min(self.theme.px(self._size), max(1, extent))
        self.place_forget()
        if horizontal:
            self.place(
                relx=1 if self.side == "right" else 0,
                y=0,
                anchor="ne" if self.side == "right" else "nw",
                width=size,
                relheight=1,
            )
        else:
            self.place(
                x=0,
                rely=1 if self.side == "bottom" else 0,
                anchor="sw" if self.side == "bottom" else "nw",
                relwidth=1,
                height=size,
            )
        self.lift()

    def show(self, *, focus=None):
        if focus is not None and not _within(focus, self):
            raise ValueError("Focus widget must belong to the sheet")
        self.master.update_idletasks()
        if not self.is_open:
            self._previous_focus = self.focus_get() or self.master.focus_lastfor()
            self._arm()
        self.is_open = True
        self._resize()
        (self.close_button if focus is None else focus).focus_set()
        return self

    def hide(self):
        if not self.is_open:
            return
        self.is_open = False
        self.place_forget()
        self._disarm()
        previous, self._previous_focus = self._previous_focus, None
        _restore(previous)
        if self.on_close is not None:
            self.on_close()

    def _cleanup(self):
        self._disarm()
        try:
            self.master.unbind("<Configure>", self._resize_binding)
        except tk.TclError:
            pass
        if self.is_open:
            _restore(self._previous_focus)
        self.is_open = False

    def _refresh_theme(self):
        background = _color(self.theme, "background")
        self.configure(
            background=background,
            highlightthickness=1,
            highlightbackground=_color(self.theme, "border"),
        )
        self.content.configure(background=background)
        self.heading.configure(
            background=background, foreground=_color(self.theme, "foreground"), font=self.theme.font
        )
        if self.is_open:
            self._resize()
