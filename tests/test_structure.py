"""Native integration checks; require a working Tk display."""

import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace

import pytest

from pydeskui.theme import Theme
from pydeskui.widgets import structure as s


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


def test_all_wrappers_native_styles_and_cleanup(root):
    theme = Theme(root)
    baseline = theme.style.configure("TFrame")
    widgets = [getattr(s, name)(root, theme=theme) for name in s.__all__]
    for widget in widgets:
        widget.pack()
    root.update()
    theme.configure(mode="dark")
    assert theme.style.configure("TFrame") == baseline
    for widget in widgets:
        assert widget in theme._widgets
        widget.destroy()
    root.update()
    assert not theme._widgets
    theme.close()


def test_tokens_and_custom_style_are_isolated(root):
    theme, other = Theme(root), Theme(root)
    theme.configure(
        tokens={
            "card": "#123456",
            "primary": "#654321",
            "primary_foreground": "#ffffff",
            "foreground": "#abcdef",
        }
    )
    card = s.Card(root, theme=theme)
    other_card = s.Card(root, theme=other)
    badge = s.Badge(root, text="Ready", theme=theme)
    icon = s.Icon(root, theme=theme)
    custom = s.Card(root, theme=theme, style="User.TFrame")
    assert theme.style.lookup(card.cget("style"), "background") == "#123456"
    assert other.style.lookup(other_card.cget("style"), "background") != "#123456"
    assert theme.style.lookup(badge.cget("style"), "background") == "#654321"
    theme.tokens["foreground"] = "#fedcba"
    theme._refresh()
    pixels = [
        icon._icon_image.get(x, y)
        for x in range(icon._icon_image.width())
        for y in range(icon._icon_image.height())
        if not icon._icon_image.transparency_get(x, y)
    ]
    assert pixels and (254, 220, 186) in pixels
    assert custom.cget("style") == "User.TFrame"


def test_native_collections_tabs_and_split(root):
    table = s.Table(root, columns=("name", "value"))
    table.insert("", "end", iid="row", values=("世界", 2))
    table.selection_set("row")
    assert table.selection() == ("row",)
    assert table.heading("name", "text") == "name"
    tree = s.Tree(root)
    tree.insert("", "end", iid="parent", text="Parent", open=True)
    tree.insert("parent", "end", iid="child", text="Child")
    assert tree.parent("child") == "parent"
    tabs = s.Tabs(root)
    first, second = s.Frame(tabs), s.Frame(tabs)
    tabs.add(first, text="First", underline=0)
    tabs.add(second, text="Second", underline=0)
    tabs.pack()
    root.update()
    changes = []
    tabs.bind("<<NotebookTabChanged>>", lambda _event: changes.append(tabs.select()))
    tabs.select(second)
    root.update()
    assert tabs.select() == str(second)
    assert changes[-1] == str(second)
    tabs.tab(second, state="disabled")
    assert tabs.tab(second, "state") == "disabled"
    for orient, key in (("horizontal", "Right"), ("vertical", "Down")):
        split = s.SplitPane(root, orient=orient)
        split.pack(fill="both", expand=True)
        split.add(s.Frame(split, width=100, height=100), weight=1)
        split.add(s.Frame(split, width=100, height=100), weight=1)
        root.update()
        before = split.sashpos(0)
        assert split._key(SimpleNamespace(keysym=key, state=0)) == "break"
        assert split.sashpos(0) > before
        split.destroy()


def test_scroll_layout_keyboard_and_validation(root):
    area = s.ScrollArea(root, horizontal=True)
    area.pack(fill="both", expand=True)
    s.Frame(area.content, width=1200, height=2000).pack()
    root.update()
    assert area.canvas.yview()[1] < 1
    assert area.canvas.xview()[1] < 1
    area.canvas.focus_force()
    area.canvas.event_generate("<Next>")
    root.update()
    assert area.canvas.yview()[0] > 0
    assert area._wheel(SimpleNamespace(num=5, state=1)) == "break"
    assert area.canvas.xview()[0] > 0
    children = root.winfo_children()
    for factory, options in (
        (s.Icon, {"name": "unknown"}),
        (s.Icon, {"size": float("nan")}),
        (s.Badge, {"variant": "unknown"}),
        (s.Table, {"columns": ("x", "x")}),
        (s.SplitPane, {"orient": "diagonal"}),
    ):
        with pytest.raises(ValueError):
            factory(root, **options)
    assert root.winfo_children() == children


def test_lightweight_card_refresh_and_host_theme(root):
    theme, other = Theme(root), Theme(root)
    card = s.Card(root, theme=theme)
    other_card = s.Card(root, theme=other)
    custom = s.Card(root, theme=theme, style="Caller.TFrame", padding=3)
    card.pack(fill="both", expand=True)
    s.Label(card, text="Card content").pack()
    root.update()
    element = theme.name("portable.Frame.border")
    assert theme.style.layout(card.cget("style"))[0][0] == element
    assert theme.style.lookup(card.cget("style"), "bordercolor") == theme.tokens["border"]
    theme.configure(tokens={"card": "#123456", "border": "#abcdef"})
    assert theme.style.lookup(card.cget("style"), "background") == "#123456"
    assert theme.style.lookup(card.cget("style"), "bordercolor") == "#abcdef"
    assert other_card.cget("style") != card.cget("style")
    assert custom.cget("style") == "Caller.TFrame"
    assert tuple(map(int, custom.cget("padding"))) == (3,)
    original = theme.style.theme_use()
    try:
        target = next(name for name in theme.style.theme_names() if name != original)
        theme.style.theme_use(target)
        root.update()
        assert theme.style.layout(card.cget("style"))[0][0] == element
    finally:
        theme.style.theme_use(original)
        root.update()


def test_scale_refresh_preserves_explicit_dimensions(root):
    theme = Theme(root)
    card = s.Card(root, theme=theme)
    toolbar = s.Toolbar(root, theme=theme)
    badge = s.Badge(root, theme=theme)
    explicit = s.Card(root, theme=theme, padding=7)
    icon = s.Icon(root, theme=theme, size=24)
    explicit_icon = s.Icon(root, theme=theme, size=24, width=37)
    area = s.ScrollArea(root, theme=theme)
    area.canvas.configure(width=333)
    split = s.SplitPane(root, theme=theme)
    old_scaling = root.tk.call("tk", "scaling")
    try:
        root.tk.call("tk", "scaling", 2 * (96 / 72))
        theme.configure()
        root.update()
        for widget, logical in ((card, 12), (toolbar, 6)):
            assert int(theme.style.lookup(widget.cget("style"), "padding")) == theme.px(logical)
        padding = theme.style.lookup(badge.cget("style"), "padding")
        assert tuple(map(int, root.tk.splitlist(padding))) == (theme.px(6), theme.px(2))
        assert tuple(map(int, explicit.cget("padding"))) == (7,)
        assert int(icon.cget("width")) == theme.px(24)
        assert int(explicit_icon.cget("width")) == 37
        assert int(explicit_icon.cget("height")) == theme.px(24)
        assert int(area.canvas.cget("width")) == 333
        assert int(area.canvas.cget("height")) == theme.px(180)
        assert int(theme.style.lookup(split.cget("style"), "sashwidth")) == theme.px(6)
        assert int(theme.style.lookup(area.yscrollbar.cget("style"), "width")) == theme.px(14)
    finally:
        root.tk.call("tk", "scaling", old_scaling)


def test_shadcn_inspired_collection_metrics_follow_density(root):
    theme = Theme(root)
    tabs = s.Tabs(root, theme=theme)
    table = s.Table(root, columns=("Name",), theme=theme)
    tree = s.Tree(root, theme=theme)
    style = theme.style
    for density, heading_y in (("compact", 8), ("default", 10), ("comfortable", 12)):
        theme.configure(density=density)
        heading_padding = root.tk.splitlist(
            style.lookup(theme.name("Treeview.Heading"), "padding")
        )
        assert tuple(map(int, heading_padding)) == (theme.px(8), theme.px(heading_y))
        assert str(style.lookup(theme.name("Treeview.Heading"), "anchor")) == "w"
        assert theme.name("portable.Treeheading.padding") in str(
            style.layout(theme.name("Treeview.Heading"))
        )
        assert int(style.lookup(theme.name("Treeview"), "indent")) == theme.px(20)
        item_layout = str(style.layout(theme.name("Treeview.Item")))
        assert "Treeitem.padding" in item_layout
        assert "Treeitem.image" in item_layout
        assert "Treeitem.text" in item_layout
        leading_key = f"slot{theme._render_slot}:spacer.tree.leading.indicator.{theme.px(6)}"
        gap_key = f"slot{theme._render_slot}:spacer.tree.gap.indicator.{theme.px(8)}"
        assert theme.name(leading_key) in item_layout
        assert theme._images[leading_key].width() == theme.px(6)
        assert theme.name(gap_key) in item_layout
        assert theme._images[gap_key].width() == theme.px(8)
        assert "Treeitem.indicator" in item_layout
        assert int(style.lookup(theme.name("Treeview.Item"), "indicatormargins")) == 0
        assert theme.name("notebook.tab.slot") in str(
            style.layout(theme.name("TNotebook.Tab"))
        )
    assert str(table.heading("Name", "anchor")) == "w"
    table.heading("Name", anchor="e")
    assert str(table.heading("Name", "anchor")) == "e"
    tabs.destroy()
    table.destroy()
    tree.destroy()
    theme.close()


def test_portable_scrollbar_layout_is_preserved(root):
    theme = Theme(root)
    names = [theme.name(f"{orient}.TScrollbar") for orient in ("Vertical", "Horizontal")]
    layouts = {name: theme.style.layout(name) for name in names}
    area = s.ScrollArea(root, horizontal=True, theme=theme)
    assert str(area.yscrollbar.cget("style")) == names[0]
    assert str(area.xscrollbar.cget("style")) == names[1]
    area._refresh_theme()
    for name in names:
        assert theme.style.layout(name) == layouts[name]


def test_table_sort_requests_leave_rows_and_selection_unchanged(root):
    calls = []
    table = s.Table(
        root,
        columns=("name", "value"),
        on_sort=lambda column, direction: calls.append((column, direction)),
    )
    table.heading("name", text="Display name")
    table.insert("", "end", iid="b", values=("B", 2))
    table.insert("", "end", iid="a", values=("A", 1))
    table.selection_set("b")
    # Exercise the registered native heading command, not just request_sort.
    command = table.heading("name", "command")
    root.tk.call(command)
    assert table.heading("name", "text") == "Display name ▲"
    root.tk.call(command)
    assert table.heading("name", "text") == "Display name ▼"
    table.request_sort("value")
    assert table.heading("name", "text") == "Display name"
    assert calls == [("name", "ascending"), ("name", "descending"), ("value", "ascending")]
    assert table.sort_column == "value"
    assert table.sort_direction == "ascending"
    assert table.get_children() == ("b", "a")
    assert table.selection() == ("b",)
    table.state(("disabled",))
    table.request_sort("value")
    assert len(calls) == 3
    with pytest.raises(ValueError):
        table.request_sort("missing")
    plain = s.Table(root, columns=("name",))
    plain.request_sort("name")
    assert plain.sort_direction == "ascending"


def test_gallery_sidebar_navigation(root, monkeypatch):
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "structure_gallery", Path(__file__).parents[1] / "examples/gallery.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.tk, "Tk", lambda: root)
    monkeypatch.setattr(root, "mainloop", lambda: None)
    module.main()
    root.update()
    shell = next(child for child in root.winfo_children() if isinstance(child, module.Gallery))
    assert isinstance(shell.nav, s.Sidebar)
    for key, button in list(shell.nav_buttons.items())[:2]:
        button.invoke()
        root.update()
        assert shell.page == key
        assert shell.body.winfo_children()


def _overflowing_area(master, **options):
    area = s.ScrollArea(master, **options)
    area.pack(side="left", fill="both", expand=True)
    body = s.Frame(area.content, width=1400, height=2200)
    body.pack()
    body.pack_propagate(False)
    return area, body


def test_wheel_over_dynamic_descendants_and_outside_scope(root):
    left, body = _overflowing_area(root, horizontal=True)
    right, other_body = _overflowing_area(root)
    outside = ttk.Label(root, text="Outside")
    outside.pack()
    root.update()
    # Descendants created after mapping require no explicit binding/tag setup.
    nested = s.Frame(body)
    nested.pack()
    label = s.Label(nested, text="Wheel here")
    entry = ttk.Entry(nested)
    label.pack()
    entry.pack()
    other_label = ttk.Label(other_body, text="Other area")
    other_label.pack()
    root.update()
    right_before = right.canvas.yview()
    for widget in (label, entry):
        left.canvas.yview_moveto(0)
        widget.event_generate("<MouseWheel>", delta=-1)
        root.update()
        assert left.canvas.yview()[0] > 0
        assert right.canvas.yview() == right_before
    left.canvas.xview_moveto(0)
    label.event_generate("<Shift-MouseWheel>", delta=-1)
    root.update()
    assert left.canvas.xview()[0] > 0
    left.canvas.yview_moveto(0)
    if root.tk.call("tk", "windowingsystem") != "aqua":
        label.event_generate("<Button-5>")
        root.update()
        assert left.canvas.yview()[0] > 0
    before = left.canvas.yview()
    outside.event_generate("<MouseWheel>", delta=-1)
    other_label.event_generate("<MouseWheel>", delta=-1)
    root.update()
    assert left.canvas.yview() == before
    assert right.canvas.yview()[0] > 0


@pytest.mark.parametrize("kind", ["text", "tree", "listbox"])
def test_overflowing_native_controls_keep_wheel_while_they_can_scroll(root, kind):
    area, body = _overflowing_area(root)
    if kind == "text":
        child = tk.Text(body, height=3)
        child.insert("1.0", "line\n" * 100)
    elif kind == "tree":
        child = ttk.Treeview(body, height=3)
        for index in range(100):
            child.insert("", "end", text=str(index))
    elif kind == "listbox":
        child = tk.Listbox(body, height=3)
        child.insert("end", *range(100))
    child.pack()
    root.update()
    before = area.canvas.yview()
    child.event_generate("<MouseWheel>", delta=-120)
    root.update()
    assert area.canvas.yview() == before
    assert child.yview()[0] > 0


@pytest.mark.parametrize("factory", [ttk.Combobox, ttk.Spinbox, ttk.Scale])
def test_value_controls_keep_wheel_isolated(root, factory):
    area, body = _overflowing_area(root)
    child = factory(body)
    child.pack()
    root.update()
    before = area.canvas.yview()
    child.event_generate("<MouseWheel>", delta=-120)
    root.update()
    assert area.canvas.yview() == before


@pytest.mark.parametrize("kind", ["text", "tree", "listbox", "canvas"])
def test_native_scroll_controls_chain_to_parent_without_room(root, kind):
    area, body = _overflowing_area(root)
    if kind == "text":
        child = tk.Text(body, height=3)
        child.insert("1.0", "short")
    elif kind == "tree":
        child = ttk.Treeview(body, height=3)
        child.insert("", "end", text="short")
    elif kind == "listbox":
        child = tk.Listbox(body, height=3)
        child.insert("end", "short")
    else:
        child = tk.Canvas(body, height=60, scrollregion=(0, 0, 300, 60))
    child.pack()
    root.update()
    event = SimpleNamespace(widget=child, delta=-120, state=0, num=None)
    assert area._subtree_wheel(event) == "break"
    assert area.canvas.yview()[0] > 0


def test_native_scroll_control_chains_at_directional_boundary(root):
    area, body = _overflowing_area(root)
    child = tk.Text(body, height=3)
    child.insert("1.0", "line\n" * 100)
    child.pack()
    root.update()
    down = SimpleNamespace(widget=child, delta=-120, state=0, num=None)
    up = SimpleNamespace(widget=child, delta=120, state=0, num=None)
    assert area._subtree_wheel(down) is None
    child.yview_moveto(1)
    assert area._subtree_wheel(down) == "break"
    outer_after_down = area.canvas.yview()[0]
    area.canvas.yview_moveto(0.5)
    child.yview_moveto(0)
    assert area._subtree_wheel(up) == "break"
    assert area.canvas.yview()[0] < 0.5
    assert outer_after_down > 0


def test_native_scroll_control_chains_shift_wheel_horizontally(root):
    area, body = _overflowing_area(root, horizontal=True)
    child = tk.Canvas(body, width=120, height=60, scrollregion=(0, 0, 1000, 60))
    child.pack()
    root.update()
    right = SimpleNamespace(widget=child, delta=-120, state=1, num=None)
    assert area._subtree_wheel(right) is None
    child.xview_moveto(1)
    assert area._subtree_wheel(right) == "break"
    assert area.canvas.xview()[0] > 0


def test_nested_scroll_area_owns_wheel_even_at_boundary(root):
    outer, body = _overflowing_area(root)
    inner = s.ScrollArea(body)
    inner.pack()
    inner.canvas.configure(width=200, height=100)
    inner_body = s.Frame(inner.content, width=200, height=1000)
    inner_body.pack()
    inner_body.pack_propagate(False)
    label = s.Label(inner_body, text="Inner area")
    label.pack()
    root.update()
    outer_before = outer.canvas.yview()
    label.event_generate("<MouseWheel>", delta=-1)
    root.update()
    assert inner.canvas.yview()[0] > 0
    assert outer.canvas.yview() == outer_before
    inner.canvas.yview_moveto(1)
    label.event_generate("<MouseWheel>", delta=-1)
    root.update()
    assert outer.canvas.yview() == outer_before


def test_wheel_bindings_cleaned_without_removing_other_handlers(root):
    calls = []
    external = root.bind("<MouseWheel>", lambda event: calls.append("external"), add="+")
    baseline = root.bind("<MouseWheel>")
    first = s.ScrollArea(root)
    second = s.ScrollArea(root)
    first_ids = tuple(first._wheel_bindings)
    second_ids = tuple(second._wheel_bindings)
    first.destroy()
    root.update()
    for sequence, binding in first_ids:
        assert binding not in root.bind(sequence)
        assert not root.tk.call("info", "commands", binding)
    for sequence, binding in second_ids:
        assert binding in root.bind(sequence)
    second.destroy()
    root.update()
    assert root.bind("<MouseWheel>").strip() == baseline.strip()
    root.event_generate("<MouseWheel>", delta=-1)
    assert calls == ["external"]
    root.unbind("<MouseWheel>", external)


def test_image_surfaces_and_card_border_refresh(root):
    theme = Theme(root)
    widgets = [
        (s.Frame(root, theme=theme), "card"),
        (s.Label(root, theme=theme, text="Label"), "card"),
        (s.Sidebar(root, theme=theme), "sidebar"),
        (s.Toolbar(root, theme=theme), "background"),
        (s.Badge(root, theme=theme, text="Badge"), "primary"),
        (s.Badge(root, theme=theme, variant="secondary"), "muted"),
    ]
    card = s.Card(root, theme=theme)
    custom = s.Sidebar(root, theme=theme, style="User.TFrame")
    for mode in ("light", "dark", "light"):
        theme.configure(mode=mode)
        root.update()
        for widget, token in widgets:
            layout = theme.style.layout(widget.cget("style"))
            expected = (
                theme.name("portable.Label.padding")
                if isinstance(widget, s.Label)
                else theme.name("portable.Frame.border")
            )
            assert layout[0][0] == expected
            assert theme.style.lookup(widget.cget("style"), "background") == theme.tokens[token]
        assert theme.style.layout(card.cget("style"))[0][0] == theme.name(
            "portable.Frame.border"
        )
        assert custom.cget("style") == "User.TFrame"


def test_aqua_logical_scale_one(root):
    if root.tk.call("tk", "windowingsystem") != "aqua":
        pytest.skip("Aqua baseline check")
    old = root.tk.call("tk", "scaling")
    try:
        root.tk.call("tk", "scaling", 1.0)
        theme = Theme(root)
        icon = s.Icon(root, size=20, theme=theme)
        assert theme.scale == pytest.approx(1, abs=0.01)
        assert int(icon.cget("width")) == 20
        assert theme.font.cget("size") == -13
    finally:
        root.tk.call("tk", "scaling", old)
