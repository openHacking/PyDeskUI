"""Overlay lifecycle and interaction regression tests (requires a Tk display)."""

import tkinter as tk
from types import SimpleNamespace

import pytest

from pydeskui import Theme
from pydeskui.widgets.controls import Button, Entry
from pydeskui.widgets.overlays import (
    Alert,
    ContextMenu,
    DropdownMenu,
    EmptyState,
    Popover,
    Sheet,
    Skeleton,
    Toast,
    Tooltip,
    _clamp_geometry,
)
from pydeskui.widgets.views import Dialog


@pytest.fixture
def root():
    tk.NoDefaultRoot()
    root = tk.Tk()
    root.geometry("600x400+100+100")
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    root.update()
    yield root
    root.destroy()
    assert not errors


@pytest.mark.parametrize("bounds", [(0, 0, 800, 600), (-800, -100, 800, 600)])
def test_geometry(bounds):
    left, top, width, height = bounds
    for x, y, w, h in [
        (9999, 9999, 100, 50),
        (-9999, -9999, 100, 50),
        (0, 0, 2000, 2000),
        (0, 0, 0, 0),
    ]:
        x, y, w, h = _clamp_geometry(x, y, w, h, bounds)
        assert left <= x < x + w <= left + width
        assert top <= y < y + h <= top + height


@pytest.mark.parametrize(
    "constructor",
    [Tooltip, Popover, DropdownMenu, ContextMenu, Alert, Toast, EmptyState, Skeleton, Sheet],
)
def test_explicit_master(constructor):
    with pytest.raises(TypeError):
        constructor(None)


def test_popup_dismissal_and_focus(root):
    entry = Entry(root)
    entry.pack()
    root.update()
    entry.focus_force()
    root.update()
    existing = root.bind("<ButtonPress>", lambda event: None, add="+")
    popup = Popover(root)
    variable = tk.StringVar(root)
    field = Entry(popup.content, theme=popup.theme, placeholder="Type here", textvariable=variable)
    field.pack()
    popup.show(x=100000, y=100000)
    root.update()
    assert popup.is_open
    assert popup.winfo_rootx() + popup.winfo_width() <= root.winfo_vrootwidth()
    popup._outside(SimpleNamespace(widget=field))
    assert popup.is_open
    entry.focus_force()
    popup._outside(SimpleNamespace(widget=entry))
    root.update()
    assert not popup.is_open
    assert str(root.tk.call("focus", "-lastfor", root)) == str(entry)
    assert existing in root.bind("<ButtonPress>")
    popup.show()
    root.update()
    popup.focus_force()
    root.update()
    popup.event_generate("<Escape>")
    root.update()
    assert not popup.is_open
    popup.show()
    popup.destroy()
    root.update()
    assert not variable.trace_info()
    assert str(root.tk.call("focus", "-lastfor", root)) == str(entry)
    assert existing in root.bind("<ButtonPress>")


def test_popup_focus_loss_dismisses_without_stealing_focus(root):
    first = Entry(root)
    first.pack()
    target = Entry(root)
    target.pack()
    popup = Popover(first)
    field = Entry(popup.content, theme=popup.theme)
    field.pack()
    first.focus_force()
    root.update()
    popup.show()
    root.update()
    target.focus_force()
    popup._check_focus()
    root.update()
    assert not popup.is_open
    assert root.focus_get() is target


def test_popover_is_attached_toggles_and_optionally_closes_on_return(root):
    theme = Theme(root)
    owner = Button(root, text="Options", theme=theme)
    owner.pack()
    popover = Popover(owner, theme=theme, close_on_return=True)
    field = Entry(popover.content, theme=theme)
    field.pack()
    owner.configure(command=lambda: popover.toggle(focus=field))
    root.update()

    owner.invoke()
    root.update()
    assert popover.is_open
    assert popover.winfo_toplevel() is root
    assert root.focus_get() is field
    inset = theme.px(max(2, min(theme.radius, 6) / 2))
    assert int(popover.content.pack_info()["padx"]) == inset
    assert int(popover.content.pack_info()["pady"]) == inset
    popover._outside(SimpleNamespace(widget=owner))
    assert popover.is_open
    owner.invoke()
    assert not popover.is_open

    # Reopening before Aqua's deferred unmap runs must cancel the stale work.
    owner.invoke()
    assert popover.is_open
    root.update_idletasks()
    assert popover.is_open
    assert popover.place_info()
    owner.invoke()
    popover.hide()
    root.update_idletasks()
    assert not popover.place_info()

    owner.invoke()
    root.update()
    root.event_generate("<Return>")
    root.update()
    assert not popover.is_open

    owner.invoke()
    root.update()
    root.event_generate("<ButtonPress-1>", x=500, y=300)
    root.update()
    assert not popover.is_open
    popover.destroy()
    owner.destroy()
    theme.close()


def test_timer_cleanup_and_no_focus(root):
    owner = tk.Frame(root)
    owner.pack()
    entry = Entry(root)
    entry.pack()
    root.update()
    entry.focus_force()
    root.update()
    tip = Tooltip(owner, text="Help", delay_ms=10000)
    toast = Toast(owner, text="Saved", duration_ms=10000)
    tip.show()
    toast.show()
    root.update()
    assert root.focus_get() is entry
    old_timer = next(iter(toast._timers))
    toast.show(text="Again")
    assert old_timer not in root.tk.call("after", "info")
    tip.hide()
    tip._schedule()
    timers = tip._timers | toast._timers
    theme = tip.theme
    owner.destroy()
    root.update()
    assert not timers.intersection(root.tk.call("after", "info"))
    assert tip not in theme._widgets and toast not in theme._widgets


def test_toast_timeout(root):
    toast = Toast(root, duration_ms=1)
    toast.show()
    done = tk.BooleanVar(root, False)
    root.after(30, done.set, True)
    root.wait_variable(done)
    assert not toast.is_open
    assert not toast._timers
    toast.show(duration_ms=0)
    assert toast.is_open and not toast._timers


def test_menu_commands_navigation_and_binding_cleanup(root):
    owner = tk.Frame(root)
    owner.pack()
    calls = []
    menu = DropdownMenu(owner, items=[("One", lambda: calls.append(menu.is_open)), None])
    disabled = menu.add_item("Disabled", disabled=True)
    last = menu.add_item("Last")
    menu.show()
    root.update()
    menu.items[0].focus_force()
    root.update()
    menu.event_generate("<Down>")
    root.update()
    assert root.focus_get() is last
    menu._move(1)
    root.update()
    assert root.focus_get() is menu.items[0]
    disabled.invoke()
    assert not calls
    menu.items[0].invoke()
    assert calls == [False]
    context = ContextMenu(owner, items=[("Action", lambda: None)])
    existing = owner.bind("<Button-3>", lambda e: None, add="+")
    owner.event_generate("<Button-3>", x=2, y=2)
    root.update()
    assert context.is_open
    context.destroy()
    assert existing in owner.bind("<Button-3>")
    assert not menu._dismiss_bindings


def test_menu_button_click_stays_open_and_focuses_first_item(root):
    owner = Button(root, text="Open menu")
    owner.pack()
    menu = DropdownMenu(owner, items=[("One", lambda: None), ("Two", lambda: None)])
    owner.configure(command=menu.show)
    root.update()

    owner.event_generate("<ButtonPress-1>", x=4, y=4)
    owner.event_generate("<ButtonRelease-1>", x=4, y=4)
    root.update()

    assert menu.is_open
    assert menu.winfo_ismapped()
    assert root.focus_get() is menu.items[0]
    assert menu.items[0].cget("style") == owner.theme.name("MenuItem.TButton")
    assert str(owner.theme.style.lookup(menu.items[0].cget("style"), "anchor")) == "w"
    assert menu.winfo_rooty() >= owner.winfo_rooty() + owner.winfo_height() + owner.theme.px(4)


def test_attached_menu_stays_inside_host_and_has_transparent_corners(root):
    owner = tk.Frame(root)
    owner.place(x=580, y=380, width=20, height=20)
    menu = DropdownMenu(owner, items=[("A wide menu item", lambda: None)])
    menu.show(x=-10000, y=10000)
    root.update()
    assert menu.winfo_toplevel() is root
    assert root.winfo_rootx() <= menu.winfo_rootx()
    assert root.winfo_rooty() <= menu.winfo_rooty()
    assert menu.winfo_rootx() + menu.winfo_width() <= root.winfo_rootx() + root.winfo_width()
    assert menu.winfo_rooty() + menu.winfo_height() <= root.winfo_rooty() + root.winfo_height()
    image = menu.theme._images[menu.theme._image_key("overlay.popup")]
    assert image.transparency_get(0, 0)


def test_native_toplevel_appearance_tracks_theme(root):
    theme = Theme(root, mode="light")
    owner = tk.Frame(root)
    owner.pack()
    popover = Popover(owner, theme=theme)
    tooltip = Tooltip(owner, theme=theme)
    dialog = Dialog(
        root,
        title="Confirm",
        message="Continue?",
        actions=(("ok", "OK"),),
        theme=theme,
    )

    def expected(mode):
        if root.tk.call("tk", "windowingsystem") == "aqua":
            return {"light": "aqua", "dark": "darkaqua"}[mode]
        return mode

    for mode in ("light", "dark"):
        theme.configure(mode=mode)
        for window in (root, tooltip, dialog):
            assert window.wm_attributes("-appearance") == expected(mode)
        assert popover.winfo_toplevel() is root
        assert popover.content.cget("background") == theme.tokens["popover"]
        assert tooltip.label.cget("foreground") == theme.tokens["popover_foreground"]
    for window in (popover, tooltip, dialog):
        window.destroy()
    owner.destroy()
    theme.close()


def test_toast_default_stack_limit_reflow_and_explicit_position(root):
    toasts = [Toast(root, text=str(index), duration_ms=0) for index in range(4)]
    for toast in toasts:
        toast.show()
        root.update()
    assert not toasts[0].is_open
    assert [toast.is_open for toast in toasts[1:]] == [True, True, True]
    assert toasts[1].winfo_y() < toasts[2].winfo_y() < toasts[3].winfo_y()
    assert (
        toasts[3].winfo_x() + toasts[3].winfo_width()
        == root.winfo_width() - toasts[3].theme.px(16)
    )
    old_y = toasts[3].winfo_y()
    toasts[2].hide()
    root.update()
    assert toasts[3].winfo_y() == old_y
    assert toasts[1].winfo_y() < toasts[3].winfo_y()
    toasts[1].show(text="newest")
    root.update()
    assert toasts[1].winfo_y() > toasts[3].winfo_y()
    explicit = Toast(root, text="anchored", duration_ms=0)
    explicit.show(anchor=toasts[3])
    root.update()
    assert explicit.is_open
    assert explicit.winfo_toplevel() is root
    assert explicit.winfo_rootx() + explicit.winfo_width() <= root.winfo_rootx() + root.winfo_width()
    for toast in (*toasts, explicit):
        toast.destroy()


def test_sheet_is_internal_resizes_restores_and_dismisses(root):
    panel = tk.Frame(root, width=200, height=150)
    panel.pack_propagate(False)
    panel.pack()
    entry = Entry(root)
    entry.pack()
    root.update()
    entry.focus_force()
    root.update()
    calls = []
    sheet = Sheet(panel, side="right", size=500, on_close=lambda: calls.append(1))
    field = Entry(sheet.content)
    field.pack()
    sheet.show(focus=field)
    root.update()
    assert sheet.winfo_toplevel() is root
    assert sheet.winfo_width() <= panel.winfo_width()
    panel.configure(width=120)
    root.update()
    assert sheet.winfo_width() <= 120
    sheet._outside(SimpleNamespace(widget=field))
    assert sheet.is_open
    sheet._escape()
    sheet.hide()
    root.update()
    assert calls == [1]
    assert str(root.tk.call("focus", "-lastfor", root)) == str(entry)
    assert not sheet.winfo_ismapped()
    sheet.destroy()


def test_theme_refresh_static_skeleton_and_alert_actions(root):
    theme = Theme(
        root,
        reduced_motion=True,
        tokens=dict(
            background="#101010",
            foreground="#eeeeee",
            popover="#202020",
            popover_foreground="#dddddd",
            border="#555555",
            muted="#333333",
            destructive="#ff0000",
        ),
    )
    before = theme.style.lookup("TButton", "background")
    called = []
    alert = Alert(
        root,
        title="Error",
        variant="destructive",
        dismissible=True,
        on_dismiss=lambda: called.append("dismiss"),
        theme=theme,
        action_text="Retry",
        command=lambda: called.append("retry"),
    )
    empty = EmptyState(root, theme=theme)
    skeleton = Skeleton(root, lines=4, theme=theme)
    tip = Tooltip(root, text="Help", theme=theme)
    assert alert.title_label.cget("foreground") == "#ff0000"
    assert len(skeleton.find_withtag("skeleton")) == 4
    assert not tip._timers
    theme.configure(mode="dark", tokens={**theme.export()["tokens"], "popover": "#123456"})
    assert tip.label.cget("background") == "#123456"
    assert theme.style.lookup("TButton", "background") == before
    alert.action.invoke()
    alert.dismiss()
    alert.dismiss()
    assert called == ["retry", "dismiss"]
    for widget in (empty, skeleton, tip):
        widget.destroy()
    theme.close()
