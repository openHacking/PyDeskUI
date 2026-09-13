"""Native Tk integration tests; require a window server (or Xvfb on Linux)."""

import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace

import pytest

from pydeskui.theme import Theme
from pydeskui.widgets.inputs import (
    Checkbox,
    Combobox,
    RadioGroup,
    Select,
    Slider,
    Spinbox,
    Switch,
    Textarea,
)


@pytest.fixture
def root():
    tk.NoDefaultRoot()
    window = tk.Tk()
    window.geometry("500x350+100+100")
    errors = []
    window.report_callback_exception = lambda *args: errors.append(args)
    window.update()
    yield window
    window.update()
    window.destroy()
    assert not errors


def show(root, widget):
    widget.pack()
    root.update()
    widget.focus_force()
    root.update()
    return widget


def key(widget, keysym, char="", state=0):
    return widget._popup_key(SimpleNamespace(keysym=keysym, char=char, state=state))


def test_import_has_no_default_root():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import pydeskui.widgets.inputs; import tkinter; assert tkinter._default_root is None",
        ],
        check=True,
    )


@pytest.mark.parametrize(
    "constructor",
    [
        Textarea,
        Checkbox,
        Switch,
        RadioGroup,
        Slider,
        Spinbox,
        Select,
        Combobox,
    ],
)
def test_explicit_master_and_theme_ownership(root, constructor):
    with pytest.raises(TypeError):
        constructor(None)
    theme = Theme(root)
    widget = constructor(root, theme=theme)
    assert widget.master is root
    assert widget in theme._widgets
    widget.destroy()
    assert widget not in theme._widgets
    theme.close()


def test_textarea_native_editing_and_theme(root):
    theme = Theme(root)
    text = Textarea(root, theme=theme, height=3)
    text.insert("1.0", "hello\n世界")
    text.edit_separator()
    text.insert("end", "!")
    text.edit_undo()
    assert text.get("1.0", "end-1c") == "hello\n世界"
    text.tag_add("custom", "1.0", "1.2")
    text.configure(state="disabled")
    text.insert("end", "ignored")
    theme.configure(mode="dark")
    assert text.get("1.0", "end-1c") == "hello\n世界"
    assert text.tag_ranges("custom")
    assert text.cget("state") == "disabled"
    custom = Textarea(root, theme=theme, background="#123456")
    theme.configure(mode="light")
    assert custom.cget("background") == "#123456"


@pytest.mark.parametrize("constructor", [Checkbox, Switch])
def test_checkbutton_native_values_command_disabled(root, constructor):
    var = tk.StringVar(root, "off")
    calls = []
    widget = constructor(
        root, variable=var, onvalue="on", offvalue="off", command=lambda: calls.append(var.get())
    )
    widget.invoke()
    assert var.get() == "on"
    widget.state(("disabled",))
    widget.invoke()
    assert calls == ["on"]
    widget.state(("!disabled",))
    widget.invoke()
    assert calls == ["on", "off"]
    widget.destroy()
    var.set("still alive")
    assert var.get() == "still alive"
    assert not var.trace_info()


def test_radio_group_native_selection_and_disabled(root):
    var = tk.StringVar(root, "a")
    calls = []
    group = RadioGroup(
        root,
        values=[("a", "First"), ("b", "Second")],
        variable=var,
        command=lambda: calls.append(var.get()),
    )
    group.buttons[1].invoke()
    assert group.get() == "b" and calls == ["b"]
    group.configure(state="disabled")
    group.buttons[0].invoke()
    assert group.get() == "b"
    group.state(("!disabled",))
    group.buttons[0].invoke()
    assert calls == ["b", "a"]
    group.set("b")
    assert group.buttons[1].instate(("selected",))


def test_slider_and_spinbox_native_options(root):
    number = tk.DoubleVar(root, 4)
    calls = []
    slider = Slider(root, variable=number, from_=1, to=10, command=calls.append)
    slider.set(8)
    assert number.get() == 8 and float(calls[-1]) == 8
    vertical = Slider(root, orient="vertical")
    assert "Vertical.TScale" in vertical.cget("style")
    vertical.configure(orient="horizontal")
    assert "Horizontal.TScale" in vertical.cget("style")
    var = tk.StringVar(root, "2")
    spin = Spinbox(
        root,
        textvariable=var,
        from_=0,
        to=8,
        increment=2,
        wrap=True,
        validate="key",
        validatecommand=(root.register(str.isdigit), "%P"),
    )
    spin.insert("end", "x")
    assert spin.get() == "2"
    spin.set("4")
    assert var.get() == "4"
    assert spin.cget("wrap")


@pytest.mark.parametrize(
    "constructor, option",
    [
        (Checkbox, "variable"),
        (Switch, "variable"),
        (RadioGroup, "variable"),
        (Slider, "variable"),
        (Spinbox, "textvariable"),
        (Select, "textvariable"),
        (Combobox, "textvariable"),
    ],
)
def test_foreign_variables_rejected(root, constructor, option):
    other = tk.Tcl()
    var = tk.StringVar(other)
    with pytest.raises(ValueError, match="different interpreter"):
        constructor(root, **{option: var})


@pytest.mark.parametrize("constructor", [Select, Combobox])
def test_popup_keyboard_commit_cancel_and_native_value_api(root, constructor):
    variable = tk.StringVar(root, "Beta")
    widget = show(root, constructor(root, values=("Alpha", "Beta", "Gamma"), textvariable=variable))
    selected = []
    widget.bind("<<ComboboxSelected>>", lambda event: selected.append(widget.get()))
    assert "TCombobox" not in widget.bindtags()
    widget.event_generate("<Down>")
    root.update()
    assert widget._popup is not None
    assert widget._listbox.curselection() == (1,)
    assert widget._listbox._rows[1][2].cget("text") == "✓"
    active_row = widget._listbox._rows[1][0]
    assert active_row.instate(("selected",))
    assert "select.option" in str(widget.theme.style.layout(active_row.cget("style")))
    active_image = widget.theme._images[widget.theme._image_key("select.option.active")]
    assert active_image.transparency_get(0, 0)
    assert widget._listbox._row_height >= widget.theme.px(28)
    widget._listbox.event_generate("<Down>")
    widget._listbox.event_generate("<Return>")
    root.update()
    assert variable.get() == "Gamma" and selected == ["Gamma"]
    assert widget._popup is None
    assert root.focus_get() is widget
    assert widget.current() == 2
    widget.open_popup()
    key(widget, "Home")
    key(widget, "Escape")
    root.update()
    assert widget.get() == "Gamma" and selected == ["Gamma"]
    widget.current(0)
    assert variable.get() == "Alpha"
    root.update()
    assert selected == ["Gamma"]


def test_type_matching_and_readonly(root):
    widget = show(root, Select(root, values=("Apple", "Apricot", "Banana", "世界")))
    widget.insert(0, "ignored")
    assert widget.get() == ""
    widget.configure(state="normal")
    widget.state(("!readonly",))
    assert widget.instate(("readonly",))
    widget.open_popup()
    key(widget, "b", "b")
    assert widget._listbox.curselection() == (2,)
    widget._typed_at = 0
    key(widget, "a", "a")
    key(widget, "a", "a")
    assert widget._listbox.curselection() == (1,)
    widget._typed_at = 0
    key(widget, "", "世")
    key(widget, "Return")
    assert widget.get() == "世界"


def test_editable_combobox_and_postcommand(root):
    widget = show(root, Combobox(root))
    widget.insert(0, "free text")
    assert widget.get() == "free text"
    widget.configure(postcommand=lambda: widget.configure(values=("fresh", "new")))
    widget.open_popup()
    assert widget._listbox.get(0, "end") == ("fresh", "new")
    key(widget, "Escape")
    assert widget.get() == "free text"


@pytest.mark.parametrize("method", ["configure", "state"])
def test_disabling_closes_popup_and_blocks_open(root, method):
    widget = show(root, Select(root, values=("a", "b")))
    widget.open_popup()
    if method == "configure":
        widget.configure(state="disabled")
    else:
        widget.state(("disabled",))
    assert widget._popup is None and root.grab_current() is None
    widget.open_popup()
    assert widget._popup is None and widget.get() == ""


def test_outside_focus_tab_and_grab_restoration(root):
    dialog = tk.Toplevel(root)
    widget = show(root, Select(dialog, values=("a", "b")))
    next_entry = ttk.Entry(dialog)
    next_entry.pack()
    root.update()
    dialog.grab_set()
    widget.open_popup()
    assert widget._popup is not None
    assert root.grab_current() is dialog
    assert widget.instate(("user2",))
    dialog.event_generate(
        "<ButtonPress-1>",
        x=-100,
        y=-100,
    )
    root.update()
    assert widget._popup is None and root.grab_current() is dialog
    assert not widget.instate(("user2",))
    assert root.focus_get() is not widget
    widget.open_popup()
    key(widget, "Tab")
    root.update()
    assert root.focus_get() is next_entry
    widget.open_popup()
    root.update()
    next_entry.focus_force()
    root.update()
    assert widget._popup is None
    assert root.focus_get() is next_entry
    widget.open_popup()
    widget.destroy()
    assert root.grab_current() is dialog
    dialog.destroy()


def test_popup_theme_isolation_and_lifetime(root):
    style = ttk.Style(root)
    baseline = style.configure("TCombobox")
    option = root.option_get("background", "Listbox")
    first, second = Theme(root), Theme(root, mode="dark")
    a = show(root, Select(root, theme=first, values=("a", "b")))
    b = show(root, Combobox(root, theme=second, values=("a", "b")))
    a.open_popup()
    before = a._listbox.cget("background")
    second.configure(mode="light")
    assert a._listbox.cget("background") == before
    first.configure(mode="dark")
    assert a._listbox.cget("background") != before
    assert style.configure("TCombobox") == baseline
    assert root.option_get("background", "Listbox") == option
    assert a.cget("style") != b.cget("style")
    popup_path = str(a._popup)
    a._schedule_focus_check()
    a.destroy()
    root.update()
    assert not int(root.tk.call("winfo", "exists", popup_path))
    assert a not in first._widgets
    assert a._focus_check is None
    # The native, globally configured popdown was never instantiated.
    assert not int(root.tk.call("winfo", "exists", str(b) + ".popdown"))


def test_popup_mouse_selection_and_empty_values(root):
    widget = show(root, Select(root, values=()))
    widget.open_popup()
    assert widget._popup is None
    widget.configure(values=("a", "b"))
    widget.open_popup()
    root.update()
    assert widget._popup.winfo_toplevel() is root
    assert widget._popup.winfo_rootx() >= root.winfo_rootx()
    assert widget._popup.winfo_rooty() >= root.winfo_rooty()
    assert (
        widget._popup.winfo_rootx() + widget._popup.winfo_width()
        <= root.winfo_rootx() + root.winfo_width()
    )
    popup_image = widget.theme._images[widget.theme._image_key("overlay.popup")]
    assert popup_image.transparency_get(0, 0)
    x, y, width, height = widget._listbox.choice_bbox(1)
    widget._choose_click(SimpleNamespace(x=x + 1, y=y + height // 2))
    assert widget.get() == "b" and widget._popup is None


def test_popup_first_visible_frame_has_final_row_layout(root):
    widget = show(root, Select(root, values=("One", "Two"), width=30))
    widget.current(0)
    root.update()
    widget.open_popup()
    listbox = widget._listbox
    check = listbox._rows[0][2]
    assert int(widget._popup.place_info()["width"]) == widget.winfo_width()
    assert int(listbox.cget("width")) == widget.winfo_width() - 8
    root.update_idletasks()
    first_visible_frame = (
        listbox.winfo_width(),
        listbox._content.winfo_width(),
        check.winfo_x(),
    )
    assert first_visible_frame[0] > 1
    assert first_visible_frame[1] == first_visible_frame[0]
    root.update()
    assert (
        listbox.winfo_width(),
        listbox._content.winfo_width(),
        check.winfo_x(),
    ) == first_visible_frame


def test_opening_press_is_not_treated_as_an_outside_click(root, monkeypatch):
    widget = show(root, Select(root, values=("JavaScript", "TypeScript")))
    refreshes = []
    monkeypatch.setattr(widget, "_refresh_theme", lambda: refreshes.append(True))
    monkeypatch.setattr(
        root,
        "update_idletasks",
        lambda: pytest.fail("opening a Select must not flush application-wide idle work"),
    )
    widget.open_popup()
    popup = widget._popup
    assert popup is not None

    # A real pointer press continues to the host binding installed by
    # open_popup(). Replaying that tail of the same event must leave the list
    # open; a genuinely external coordinate must still close it.
    result = widget._outside_click(
        SimpleNamespace(
            x_root=widget.winfo_rootx() + widget.winfo_width() // 2,
            y_root=widget.winfo_rooty() + widget.winfo_height() // 2,
        )
    )
    assert result is None
    assert widget._popup is popup
    assert refreshes == []

    widget._outside_click(SimpleNamespace(x_root=-10_000, y_root=-10_000))
    assert widget._popup is None


def test_popup_sizes_scrollbar_without_a_synchronous_layout_flush(root):
    widget = show(root, Select(root, values=tuple(range(20)), height=3, width=20))
    widget.open_popup()
    popup = widget._popup
    listbox = widget._listbox
    assert popup is not None and listbox is not None
    placed_width = int(popup.place_info()["width"])
    placed_height = int(popup.place_info()["height"])
    assert placed_width >= widget.winfo_width()
    assert placed_width <= root.winfo_width()
    assert placed_height == listbox.winfo_reqheight() + 8
    root.update_idletasks()
    assert popup.winfo_width() == placed_width
    assert popup.winfo_height() == placed_height


def test_popup_focus_waits_for_opening_pointer_dispatch(root):
    theme = Theme(root)
    widget = show(root, Select(root, theme=theme, values=("JavaScript", "TypeScript")))
    widget.focus_force()
    root.update()

    widget.open_popup()
    popup = widget._popup
    listbox = widget._listbox
    assert popup is not None and listbox is not None
    assert root.focus_get() is widget

    # Reproduce the host-level handler that runs after the Select's own
    # ButtonPress callback. It must still see the click as belonging to the
    # focused Select, not schedule a blur that immediately closes the list.
    theme._pointer_input(
        SimpleNamespace(
            widget=widget,
            x_root=widget.winfo_rootx() + 1,
            y_root=widget.winfo_rooty() + 1,
        )
    )
    root.update()
    assert widget._popup is popup
    assert root.focus_get() is listbox

    widget.close_popup()
    widget.open_popup()
    assert widget._popup_focus_job is not None
    widget.close_popup()
    root.update()
    assert widget._popup_focus_job is None


def test_select_opens_on_first_pointer_press(root):
    widget = show(root, Select(root, values=("JavaScript", "TypeScript")))
    widget.event_generate(
        "<ButtonPress-1>",
        x=widget.winfo_width() // 2,
        y=widget.winfo_height() // 2,
    )
    root.update()
    assert widget._popup is not None
    assert root.focus_get() is widget._listbox


def test_checkbox_uses_portable_checkmark_assets_and_refreshes(root):
    style = ttk.Style(root)
    native_layout = style.layout("TCheckbutton")
    theme = Theme(root)
    widget = show(root, Checkbox(root, theme=theme, text="Include archived"))
    layout = str(style.layout(widget.cget("style")))
    assert "inputs.checkbox.indicator" in layout
    assert "inputs.portable.Checkbutton.padding" in layout
    assert "inputs.portable.Checkbutton.label" in layout
    assert "Checkbutton.focus" not in layout
    assert style.layout("TCheckbutton") == native_layout

    off = theme._images[theme._image_key("inputs.checkbox.False.normal")]
    on = theme._images[theme._image_key("inputs.checkbox.True.normal")]
    assert off.width() == theme.px(28)
    assert off.height() == theme.px(22)
    assert off.get(theme.px(4), theme.px(4)) != on.get(theme.px(4), theme.px(4))
    assert off.transparency_get(off.width() - 1, 0)

    widget.event_generate("<space>")
    root.update()
    assert widget.instate(("selected",))
    before = on.get(theme.px(4), theme.px(4))
    theme.configure(mode="dark")
    refreshed = theme._images[theme._image_key("inputs.checkbox.True.normal")]
    assert refreshed.get(theme.px(4), theme.px(4)) != before


def test_switch_pill_assets_are_scoped_and_refresh(root):
    style = ttk.Style(root)
    native_layout = style.layout("TCheckbutton")
    theme = Theme(root)
    other = Theme(root)
    switch = show(root, Switch(root, theme=theme, text="Enable"))
    second = Switch(root, theme=other)
    off = theme._images[theme._image_key("inputs.switch.False.normal")]
    on = theme._images[theme._image_key("inputs.switch.True.normal")]
    x, y = theme.px(10), theme.px(10)
    assert off.get(x, y) != on.get(x, y)
    assert off.width() > off.height()
    assert off.transparency_get(0, 0)
    assert "inputs.switch.indicator" in str(style.layout(switch.cget("style")))
    assert "inputs.portable.Checkbutton.padding" in str(style.layout(switch.cget("style")))
    assert "inputs.portable.Checkbutton.label" in str(style.layout(switch.cget("style")))
    assert style.layout(switch.cget("style"))[0][0] == theme.name(
        theme._image_key("surface.card")
    )
    switch.event_generate("<space>")
    root.update()
    assert switch.instate(("selected",))
    before = on.get(x, y)
    other_before = other._images[other._image_key("inputs.switch.True.normal")].get(x, y)
    theme.configure(mode="dark")
    refreshed = theme._images[theme._image_key("inputs.switch.True.normal")]
    assert refreshed.get(x, y) != before
    assert on.get(x, y) == before
    for states in ((), ("selected",), ("active",), ("disabled",)):
        assert style.lookup(switch.cget("style"), "background", states) == theme.tokens["card"]
    assert other._images[other._image_key("inputs.switch.True.normal")].get(x, y) == other_before
    assert style.layout("TCheckbutton") == native_layout
    assert switch.cget("style") != second.cget("style")
    switch.destroy()
    theme.close()
    assert not theme._images


def test_combobox_custom_shell_and_host_theme_switch(root):
    theme = Theme(root)
    style = theme.style
    original_host = style.theme_use()
    baseline = style.layout("TCombobox")
    widget = show(root, Combobox(root, theme=theme, values=("One", "Two")))
    switch = Switch(root, theme=theme)
    assert "inputs.combo.field" in str(style.layout(widget.cget("style")))
    assert "inputs.combo.chevron.downarrow" in str(style.layout(widget.cget("style")))
    assert "inputs.portable.Combobox.padding" in str(style.layout(widget.cget("style")))
    assert "inputs.portable.Combobox.textarea" in str(style.layout(widget.cget("style")))
    assert style.layout("TCombobox") == baseline
    image = theme._images[theme._image_key("inputs.combo")]
    before = image.get(image.width() // 2, image.height() // 2)
    theme.configure(mode="dark", density="comfortable", radius=10)
    refreshed = theme._images[theme._image_key("inputs.combo")]
    assert refreshed.get(refreshed.width() // 2, refreshed.height() // 2) != before
    # Changing Tk's host theme rebuilds the private layouts without a native popup.
    alternative = next(name for name in style.theme_names() if name != original_host)
    try:
        style.theme_use(alternative)
        root.update()
        assert "inputs.combo.field" in str(style.layout(widget.cget("style")))
        assert "inputs.switch.indicator" in str(style.layout(switch.cget("style")))
        widget.open_popup()
        root.update()
        assert widget._listbox.cget("background") == theme.tokens["popover"]
        key(widget, "Return")
        assert widget.get() == "One"
    finally:
        style.theme_use(original_host)
        root.update()


def test_postcommand_can_destroy_owner_and_parent_cleanup(root):
    widget = show(root, Combobox(root, values=("One",)))
    widget.configure(postcommand=widget.destroy)
    widget.open_popup()
    assert not widget.winfo_exists()
    panel = ttk.Frame(root)
    panel.pack()
    other = show(root, Select(panel, values=("One",)))
    other.open_popup()
    popup = str(other._popup)
    panel.destroy()
    root.update()
    assert not int(root.tk.call("winfo", "exists", popup))
    assert root.grab_current() is None


def test_chevron_image_refresh_and_mouse_target(root):
    theme = Theme(root)
    widget = show(root, Combobox(root, theme=theme, values=("One", "Two")))
    image = theme._images[theme._image_key("inputs.combo.chevron.normal")]
    disabled = theme._images[theme._image_key("inputs.combo.chevron.disabled")]
    assert image.width() == image.height() == theme.px(16)
    assert image.transparency_get(0, 0)
    point = next(
        (x, y)
        for x in range(image.width())
        for y in range(image.height())
        if not image.transparency_get(x, y)
    )
    before = image.get(*point)
    assert disabled.get(*point) != before
    theme.configure(mode="dark")
    root.update()
    refreshed = theme._images[theme._image_key("inputs.combo.chevron.normal")]
    assert refreshed.get(*point) != before
    y = widget.winfo_height() // 2
    x = next(x for x in range(widget.winfo_width()) if "chevron.downarrow" in widget.identify(x, y))
    widget.event_generate("<Button-1>", x=x, y=y)
    root.update()
    assert widget._popup is not None
    assert widget.instate(("user2",))
    key(widget, "Escape")
    widget.state(("disabled",))
    widget.event_generate("<Button-1>", x=x, y=y)
    assert widget._popup is None


@pytest.mark.parametrize("constructor", [Textarea, Spinbox, Combobox, Select])
def test_native_font_tracks_theme_and_preserves_constructor_override(root, constructor):
    theme = Theme(root)
    widget = constructor(root, theme=theme)
    custom = constructor(root, theme=theme, font="TkFixedFont")
    assert str(widget.cget("font")) == str(theme.font)
    theme.configure(font_size=19)
    assert str(widget.cget("font")) == str(theme.font)
    assert theme.font.cget("size") == -theme.px(19)
    assert str(custom.cget("font")) == "TkFixedFont"


def test_spinbox_image_arrows_preserve_native_mouse_behavior(root):
    theme = Theme(root)
    calls = []
    widget = show(
        root,
        Spinbox(
            root,
            theme=theme,
            from_=0,
            to=4,
            increment=2,
            command=lambda: calls.append(widget.get()),
        ),
    )
    widget.set("2")
    layout = str(theme.style.layout(widget.cget("style")))
    assert ".uparrow" in layout and ".downarrow" in layout
    assert "inputs.portable.Spinbox.textarea" in layout
    assert theme.style.lookup(widget.cget("style"), "background") == theme.tokens["card"]

    def click(direction):
        point = next(
            (x, y)
            for x in range(widget.winfo_width())
            for y in range(widget.winfo_height())
                if direction + "arrow" in widget.identify(x, y)
        )
        widget.event_generate("<Button-1>", x=point[0], y=point[1])
        widget.event_generate("<ButtonRelease-1>", x=point[0], y=point[1])
        root.update()

    click("up")
    assert widget.get() == "4" and calls == ["4"]
    click("down")
    assert widget.get() == "2" and calls == ["4", "2"]
    theme.configure(mode="dark")
    assert theme.style.lookup(widget.cget("style"), "background") == theme.tokens["card"]
    widget.state(("disabled",))
    click("up")
    assert widget.get() == "2" and calls == ["4", "2"]
