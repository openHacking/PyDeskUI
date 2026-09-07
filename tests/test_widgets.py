import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk

import pytest

from pydeskui import (
    Button,
    DetailView,
    Dialog,
    Entry,
    FieldSpec,
    Form,
    Item,
    ItemList,
    NavigationItem,
    ProgressView,
    Scheduler,
    SearchEntry,
    SegmentedControl,
    Theme,
    TranslationContext,
)


@pytest.fixture
def root():
    tk.NoDefaultRoot()
    root = tk.Tk()
    root.geometry("600x500")
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    yield root
    root.update()
    root.destroy()
    assert not errors


def pump(root, seconds=0.1):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        root.update()
        time.sleep(0.005)


def test_import_no_root():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import pydeskui; import tkinter; assert tkinter._default_root is None",
        ],
        check=True,
    )


def test_parent_variables_and_native_options(root):
    parent = ttk.Frame(root)
    window = tk.Toplevel(root)
    value = tk.StringVar(master=root, value="hello")
    one, two = Entry(parent, textvariable=value), Entry(window, textvariable=value)
    assert one.winfo_parent() == str(parent)
    assert two.winfo_parent() == str(window)
    value.set("世界")
    assert one.get() == two.get() == "世界"
    one.destroy()
    value.set("retained")
    assert two.get() == "retained"
    with pytest.raises(tk.TclError):
        Entry(root, nonexistent_option=True)
    count = []
    button = Button(parent, command=lambda: count.append(1))
    button.invoke()
    button.state(["disabled"])
    button.invoke()
    assert count == [1]


def test_button_optional_icon_and_position(root):
    theme = Theme(root)
    button = Button(root, text="Home", icon="home", icon_position="left", theme=theme)
    button.pack()
    root.update()
    assert button.cget("icon") == "home"
    assert button.cget("icon_position") == "left"
    assert button.cget("image")
    button.configure(icon="settings", icon_position="right")
    assert button.cget("icon") == "settings"
    assert str(button.cget("compound")) == "right"
    button.configure(icon=None)
    assert not button.cget("image")
    with pytest.raises(ValueError):
        button.configure(icon_position="middle")


def test_navigation_item_selected_state(root):
    item = NavigationItem(root, text="Home", icon="home")
    assert not item.cget("selected")
    assert item.cget("variant") == "ghost"
    item.configure(selected=True)
    assert item.cget("selected")
    assert item.cget("variant") == "secondary"


def test_segmented_control_selection_keyboard_and_lifetime(root):
    value = tk.StringVar(master=root, value="enabled")
    changes = []
    control = SegmentedControl(
        root,
        values=(("all", "All"), ("enabled", "Enabled"), ("disabled", "Disabled")),
        variable=value,
        command=lambda: changes.append(value.get()),
    )
    control.pack()
    root.update()
    assert control.get() == "enabled"
    assert control.buttons[1].cget("variant") == "secondary"
    control.buttons[1].focus_force()
    control.buttons[1].event_generate("<Right>")
    root.update()
    assert control.get() == "disabled"
    assert changes == ["disabled"]
    control.set("all")
    assert changes == ["disabled"]
    with pytest.raises(ValueError):
        control.set("missing")
    control.destroy()
    value.set("enabled")


def test_pointer_focuses_entry_and_blank_click_blurs_it(root):
    theme = Theme(root)
    entry = Entry(root, theme=theme)
    entry.pack()
    root.update()
    entry.event_generate("<Button-1>", x=4, y=4)
    root.update()
    assert root.focus_get() is entry
    assert entry.instate(("focus",))
    assert not entry.instate(("user1",))
    root.event_generate("<ButtonPress-1>", x=500, y=450)
    root.update()
    assert root.focus_get() is not entry


def test_search_lifetime(root):
    value = tk.StringVar(master=root)
    changes = []
    entry = SearchEntry(root, textvariable=value, on_change=changes.append, debounce_ms=10)
    value.set("a")
    value.set("ab")
    pump(root)
    assert changes == ["ab"]
    entry._clear()
    pump(root)
    assert changes == ["ab", ""]
    value.set("pending")
    entry.destroy()
    pump(root)
    assert changes == ["ab", ""]
    assert not value.trace_info()


def test_theme_isolation_and_atomic_validation(root):
    plain = ttk.Style(root).lookup("TButton", "foreground")
    theme = Theme(root)
    second = Theme(root, mode="dark")
    button = Button(root, theme=theme)
    Entry(root, theme=second)
    theme.configure(mode="dark", accent="#ff0000")
    assert ttk.Style(root).lookup("TButton", "foreground") == plain
    with pytest.raises(ValueError):
        theme.configure(mode="light", accent="not-a-color")
    assert theme.mode == "dark"
    with pytest.raises(RuntimeError):
        theme.close()
    button.destroy()
    theme.close()


def test_form_list_and_progress(root):
    theme = Theme(root, translator=TranslationContext())
    form = Form(
        root,
        fields=[
            FieldSpec("text", "Text", "multiline", required=True),
            FieldSpec("count", "Count", "integer", default=2),
            FieldSpec("sort", "Sort", "boolean", default=False),
        ],
        theme=theme,
    )
    form.set_values({"text": "中文"})
    theme.configure(mode="dark")
    theme.translator.configure(locale="zh-CN")
    assert form.get_values() == {"text": "中文", "count": 2, "sort": False}
    form.set_values({"count": "x"})
    with pytest.raises(ValueError):
        form.get_values()
    changes = []
    items = ItemList(root, on_select=changes.append)
    items.set_items([Item("one", "First"), Item("two", "Second")])
    items.tree.selection_set("two")
    pump(root)
    items.set_items([Item("two", "Updated")])
    pump(root)
    assert changes == ["two"]
    with pytest.raises(ValueError):
        items.set_items([Item("x", "X"), Item("x", "Y")])
    assert items.selected_id() == "two"
    items.set_items([])
    assert changes == ["two", None]
    progress = ProgressView(root)
    progress.update_progress(None, "Working")
    progress.destroy()
    pump(root)


def test_scheduler_and_dialog(root):
    owner = ttk.Frame(root)
    scheduler = Scheduler(owner)
    calls = []
    handle = scheduler.call_later(10, lambda: calls.append(1))
    handle.cancel()
    handle.cancel()
    scheduler.call_later(10, lambda: calls.append(2))
    owner.destroy()
    pump(root)
    assert not calls
    dialog = Dialog(root, title="Title", message="Message", actions=[("ok", "OK")])
    dialog.show(calls.append)
    dialog._finish("ok")
    dialog._finish(None)
    assert calls == ["ok"]
    detail = DetailView(root)
    detail.set_content("Code", "<script>untrusted()</script>", "code")
    assert detail.text.cget("state") == "disabled"


def test_missing_parent_and_skill_fixtures(root):
    import importlib.util
    from pathlib import Path

    for constructor in (Button, Entry, Theme):
        with pytest.raises(TypeError):
            constructor(None)
    spec = importlib.util.spec_from_file_location(
        "skill_examples", Path(__file__).parents[1] / "skills/pydeskui/examples.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for panel in (
        module.embedded(root),
        module.cancellable(root),
        module.image_fallback(root, "missing.png"),
    ):
        panel.destroy()
    pump(root)
    assert TranslationContext("zh-CN").gettext("Run") == "运行"
    assert TranslationContext("missing").gettext("Run") == "Run"
