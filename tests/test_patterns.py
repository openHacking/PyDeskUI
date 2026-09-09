import tkinter as tk

import pytest

from pydeskui import CodeEditor, CommandPalette, ImageCompareView, Item, Theme


@pytest.fixture
def root():
    tk.NoDefaultRoot()
    window = tk.Tk()
    window.geometry("600x500")
    yield window
    window.destroy()


def test_command_palette_uses_stable_result_ids(root):
    selected = []
    palette = CommandPalette(root, on_select=selected.append, theme=Theme(root))
    palette.results.set_items([Item("plugin:command", "Command", "Plugin")])
    palette.results.tree.selection_set("plugin:command")
    palette._accept(None)
    assert selected == ["plugin:command"]


def test_image_compare_retains_host_images(root):
    view = ImageCompareView(root, theme=Theme(root))
    before = tk.PhotoImage(master=root, width=1, height=1)
    after = tk.PhotoImage(master=root, width=1, height=1)
    view.set_images(before, after)
    assert view._images == (before, after)
    view.clear()
    assert view._images == ()


def test_code_editor_tracks_lines_and_delegates_text_api(root):
    editor = CodeEditor(root, theme=Theme(root))
    editor.pack(fill="both", expand=True)
    editor.insert("1.0", "one\ntwo")
    root.update()
    assert editor.get("1.0", "end-1c") == "one\ntwo"
    assert editor.gutter.get("1.0", "end-1c") == "1\n2"
    assert editor.status.cget("text").startswith("Ln ")


def test_embedded_editors_keep_thin_focus_and_visible_footer(root):
    theme = Theme(root)
    editor = CodeEditor(root, bordered=False, theme=theme)
    editor.pack(fill="both", expand=True)
    editor.insert("1.0", "long line " * 100 + "\n" + "\n".join(map(str, range(100))))
    root.update()
    assert editor.horizontal.winfo_ismapped()
    assert editor.vertical.winfo_ismapped()
    assert editor.status.winfo_ismapped()
    for mode in ("dark", "light"):
        theme.configure(mode=mode)
        root.update()
        assert int(editor.text.cget("highlightthickness")) == theme.px(1)
        assert editor.text.cget("highlightbackground") == theme.tokens["background"]
        assert editor.gutter.cget("spacing1") == editor.text.cget("spacing1")
    editor.text.yview_moveto(0.5)
    root.update()
    assert abs(editor.text.yview()[0] - editor.gutter.yview()[0]) < 0.02
