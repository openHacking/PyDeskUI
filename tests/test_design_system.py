"""Theme contracts that cannot be checked by screenshots alone."""

import importlib.util
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import pytest

from pydeskui import Button, Entry, Icon, Theme, check_runtime, load_image, load_svg
from pydeskui.theme import palette
from tests.test_widgets import pump


@pytest.fixture
def root():
    window = tk.Tk()
    errors = []
    window.report_callback_exception = lambda *args: errors.append(args)
    yield window
    window.update()
    window.destroy()
    assert not errors


def luminance(color):
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    return sum(v * w for v, w in zip(channels, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


@pytest.mark.parametrize("dark", [False, True])
def test_builtin_contrast(dark):
    c = palette(dark)
    for bg, fg in (
        ("background", "foreground"),
        ("card", "muted_foreground"),
        ("primary", "primary_foreground"),
        ("secondary", "secondary_foreground"),
        ("destructive", "destructive_foreground"),
    ):
        assert contrast(c[bg], c[fg]) >= 4.5, (bg, fg)
    assert contrast(c["card"], c["input"]) >= 3
    assert contrast(c["card"], c["ring"]) >= 3


def test_tk9_svg_resources(root, tmp_path):
    assert check_runtime(root).startswith("9.")
    source = tmp_path / "sample.svg"
    source.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="12" '
        'viewBox="0 0 24 12"><rect width="24" height="12" fill="#123456"/></svg>',
        encoding="utf-8",
    )
    image = load_svg(root, source, width=48)
    assert (image.width(), image.height()) == (48, 24)
    assert load_image(root, source, size=(24, 24)).width() == 24
    with pytest.raises(ValueError, match="mutually exclusive"):
        load_svg(root, source, width=24, height=24)
    icon = Icon(root, source=source, size=24)
    assert icon._icon_image.width() == icon.theme.px(24)
    icon.destroy()


def test_native_svg_theme_performance(root):
    started = time.perf_counter()
    theme = Theme(root)
    assert time.perf_counter() - started < 1.0
    started = time.perf_counter()
    buttons = [Button(root, theme=theme, text=str(index)) for index in range(100)]
    assert time.perf_counter() - started < 0.1
    started = time.perf_counter()
    theme.configure(mode="dark")
    assert time.perf_counter() - started < 0.25
    for button in buttons:
        button.destroy()
    theme.close()


def test_theme_validation_export_state_and_cache(root):
    theme = Theme(root)
    value = tk.StringVar(master=root, value="保留文字")
    entry = Entry(root, textvariable=value, theme=theme, placeholder="Placeholder")
    entry.pack()
    entry.selection_range(0, 2)
    entry.focus_force()
    button = Button(root, theme=theme, variant="primary")
    before = theme.export()
    for update in (
        {"density": "bad"},
        {"radius": -1},
        {"font_size": float("nan")},
        {"tokens": {"unknown": "red"}},
        {"tokens": {"primary": "invalid-color"}},
    ):
        with pytest.raises(ValueError):
            theme.configure(mode="dark", **update)
        assert theme.export() == before
    count = len(theme._images)
    for index in range(8):
        theme.configure(
            mode="dark" if index % 2 else "light",
            radius=index,
            tokens={"primary": "#334455"},
            density="comfortable",
        )
    assert entry.get() == "保留文字"
    assert entry.selection_present()
    assert count <= len(theme._images) <= count * 2
    assert theme.tokens["primary"] == "#334455"
    theme.configure(accent="#ffffff", tokens={})
    assert theme.tokens["primary_foreground"] == "#000000"
    copied = Theme(root, **theme.export())
    assert copied.tokens == theme.tokens
    if root.tk.call("tk", "windowingsystem") == "aqua":
        assert ttk.Style(root).theme_use() == "aqua"
    button.destroy()
    entry.destroy()
    copied.close()
    theme.close()


def test_host_theme_roundtrip_and_scoping(root):
    style = ttk.Style(root)
    original = style.theme_use()
    plain = style.lookup("TFrame", "background")
    one, two = Theme(root), Theme(root, mode="dark")
    a, b = Button(root, theme=one), Button(root, theme=two)
    a.pack()
    b.pack()
    try:
        style.theme_use("clam" if original != "clam" else "alt")
        pump(root, 0.05)
        one.configure(accent="#226633")
        style.theme_use(original)
        pump(root, 0.05)
        assert style.lookup("TFrame", "background") == plain
        assert (
            style.lookup(one.name("primary.medium.TButton"), "foreground")
            == one.tokens["primary_foreground"]
        )
        assert one.tokens != two.tokens
        assert one.name(f"entry.field.slot{one._active_slot}") in style.element_names()
    finally:
        style.theme_use(original)


def test_gallery_all_pages_and_theme_changes(root):
    spec = importlib.util.spec_from_file_location(
        "gallery", Path(__file__).parents[1] / "examples/gallery.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    gallery = module.Gallery(root)
    for mode in ("light", "dark"):
        gallery.theme.configure(mode=mode)
        for key, _, _ in module.PAGES:
            gallery.show_page(key)
            pump(root, 0.02)
            assert gallery.body.winfo_children()
    gallery.show_page("tasks")
    gallery.start_task()
    pump(root, 0.05)
    gallery.cancel_task()
    gallery.show_page("settings")
    gallery.toggle_locale()
    gallery.theme.configure(font_size=18)
    root.geometry("900x640")
    pump(root, 0.05)
    assert not gallery.theme_visible
    gallery.destroy()


def test_thousand_rows_and_responsive_progress(root):
    from pydeskui import Item, ItemList, ProgressView, Scheduler

    theme = Theme(root)
    view = ItemList(root, theme=theme)
    view.pack(fill="both", expand=True)
    view.set_items([Item(str(i), f"Resource {i}") for i in range(1000)])
    view.tree.selection_set("500")
    progress = ProgressView(root, theme=theme)
    progress.pack(fill="x")
    delivered = []
    scheduler = Scheduler(root)
    scheduler.call_later(1, lambda: delivered.append(True))
    for i in range(10):
        progress.update_progress(i / 10, "Processing")
        root.update()
    assert view.selected_id() == "500"
    assert len(view.tree.get_children()) == 1000
    assert delivered
    progress.destroy()
    scheduler.close()


def test_progress_paint_matches_value(root):
    from pydeskui import ProgressView

    progress = ProgressView(root)
    progress.pack(fill="x")
    root.update()
    progress.update_progress(0)
    paint = progress.bar._paint
    assert not paint.find_withtag("progress")
    progress.update_progress(0.5)
    half = paint.coords("progress")
    track = paint.coords("track")
    assert half[2] == pytest.approx((track[0] + track[2]) / 2)
    progress.update_progress(1)
    assert paint.coords("progress")[2] == pytest.approx(track[2])
    progress.update_progress(None)
    assert paint.coords("progress")[2] < track[2]
    progress.destroy()
