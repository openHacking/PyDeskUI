"""Reusable compound views for command-driven desktop tools."""

import tkinter as tk
from tkinter import font as tkfont

from .widgets import Frame, ItemList, Label, Popover, SearchEntry, Textarea
from .widgets.views import _AutoScrollbar


class CodeEditor(Frame):
    """Small code editing surface with line numbers and a cursor status row."""

    def __init__(self, master, *, readonly=False, line_numbers=True, bordered=True, theme=None, **options):
        super().__init__(master, theme=theme, **options)
        self._readonly = bool(readonly)
        self._bordered = bool(bordered)
        self._gutter_lines = 0
        self._line_numbers = bool(line_numbers)
        self.code_font = tkfont.Font(self, font="TkFixedFont")
        self.code_font.configure(size=-self.theme.px(self.theme.font_size))
        self.body = Frame(self, theme=self.theme)
        self.body.pack(fill="both", expand=True)
        self.gutter = tk.Text(
            self.body,
            width=4,
            state="disabled",
            takefocus=False,
            borderwidth=0,
            highlightthickness=0,
            padx=self.theme.px(8),
            pady=self.theme.px(10),
            spacing1=self.theme.px(1),
            spacing3=self.theme.px(1),
            font=self.code_font,
        )
        if self._line_numbers:
            self.gutter.grid(row=0, column=0, sticky="ns")
        self.text = Textarea(
            self.body,
            wrap="none",
            bordered=bordered,
            borderwidth=0,
            highlightthickness=self.theme.px(1),
            font=self.code_font,
            padx=self.theme.px(12),
            pady=self.theme.px(10),
            spacing1=self.theme.px(1),
            spacing3=self.theme.px(1),
            theme=self.theme,
        )
        self.text.grid(row=0, column=1, sticky="nsew")
        self.vertical = _AutoScrollbar(self.body, orient="vertical", command=self.text.yview,
                                      style=self.theme.name("Vertical.TScrollbar"))
        self.vertical.grid(row=0, column=2, sticky="ns")
        self.horizontal = _AutoScrollbar(self.body, orient="horizontal", command=self.text.xview,
                                        style=self.theme.name("Horizontal.TScrollbar"))
        self.horizontal.grid(row=1, column=1, sticky="ew")
        self.text.configure(yscrollcommand=self._scroll_changed, xscrollcommand=self.horizontal.set)
        self.body.rowconfigure(0, weight=1)
        self.body.columnconfigure(1, weight=1)
        self.status_bar = Frame(self, theme=self.theme)
        self.status_bar.pack(side="bottom", fill="x", before=self.body, pady=(6, 0))
        self.status = Label(self.status_bar, variant="muted", theme=self.theme)
        self.status.pack(side="left")
        self.text.bind("<KeyRelease>", self._update_chrome, add="+")
        self.text.bind("<ButtonRelease>", self._update_chrome, add="+")
        self.text.bind("<<Modified>>", self._update_chrome, add="+")
        self.text.bind("<MouseWheel>", self._sync_scroll, add="+")
        if self._readonly:
            self.text.configure(state="disabled")
        self._refresh_theme()
        self._update_chrome()

    def _refresh_theme(self):
        self.code_font.configure(size=-self.theme.px(self.theme.font_size))
        self.gutter.configure(
            background=self.theme.tokens["muted"],
            foreground=self.theme.tokens["muted_foreground"],
        )

    def _scroll_changed(self, first, last):
        self.vertical.set(first, last)
        self.gutter.yview_moveto(first)

    def _sync_scroll(self, event=None):
        self.after_idle(lambda: self.gutter.yview_moveto(self.text.yview()[0]))

    def _update_chrome(self, event=None):
        try:
            lines = max(1, int(self.text.index("end-1c").split(".")[0]))
            current_line, current_column = map(int, self.text.index("insert").split("."))
            if lines != self._gutter_lines:
                self.gutter.configure(state="normal")
                self.gutter.delete("1.0", "end")
                self.gutter.insert("1.0", "\n".join(map(str, range(1, lines + 1))))
                self.gutter.configure(state="disabled")
                self._gutter_lines = lines
            self.status.configure(text=f"Ln {current_line}, Col {current_column + 1}")
            self.text.edit_modified(False)
        except tk.TclError:
            pass

    def get(self, *args):
        return self.text.get(*args)

    def delete(self, *args):
        self.text.delete(*args)
        self._update_chrome()

    def insert(self, *args):
        self.text.insert(*args)
        self._update_chrome()

    def focus_set(self):
        return self.text.focus_set()


class CommandPalette(Popover):
    """Keyboard-friendly search popover with a stable-ID result list."""

    def __init__(self, master, *, title="Quick search", on_search=None, on_select=None, theme=None):
        super().__init__(master, theme=theme)
        self.title_label = Label(self.content, text=title, theme=self.theme)
        self.title_label.pack(anchor="w")
        self.search = SearchEntry(self.content, on_change=on_search, theme=self.theme)
        self.search.pack(fill="x", pady=(8, 6))
        self.results = ItemList(self.content, on_select=on_select, theme=self.theme)
        self.results.pack(fill="both", expand=True)
        self.search.bind("<Down>", self._focus_first, add="+")
        self.results.tree.bind("<Return>", self._accept, add="+")

    def _focus_first(self, _event):
        children = self.results.tree.get_children()
        if children:
            self.results.tree.selection_set(children[0])
            self.results.tree.focus(children[0])
            self.results.tree.focus_set()
        return "break"

    def _accept(self, _event):
        selected = self.results.selected_id()
        if selected and self.results.on_select:
            self.results.on_select(selected)
        return "break"

    def show(self, *, anchor=None, x=None, y=None, focus=None):
        return super().show(
            anchor=anchor,
            x=x,
            y=y,
            focus=self.search if focus is None else focus,
        )


class ImageCompareView(Frame):
    """Before/after images supplied by a trusted host adapter.

    ``overlay`` remains a presentation hint on Tk/Aqua and uses the stable
    two-pane view. Native clipped canvases reproducibly crash Tk 9 on macOS,
    so the component preserves process safety instead of copying image data.
    """

    def __init__(
        self,
        master,
        *,
        before_title="Before",
        after_title="After",
        mode="side-by-side",
        position=0.5,
        theme=None,
    ):
        if mode not in ("side-by-side", "overlay"):
            raise ValueError("mode must be side-by-side or overlay")
        if not 0 <= position <= 1:
            raise ValueError("position must be between 0 and 1")
        super().__init__(master, theme=theme)
        self.mode, self.position = mode, float(position)
        self.before = Label(self, text=before_title, theme=self.theme)
        self.after_label = Label(self, text=after_title, theme=self.theme)
        self.before.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self.after_label.pack(side="left", fill="both", expand=True, padx=(4, 0))
        self._images: tuple[tk.PhotoImage, ...] = ()

    def set_images(self, before_image: tk.PhotoImage, after_image: tk.PhotoImage):
        self.before.configure(image=before_image, text="")
        self.after_label.configure(image=after_image, text="")
        self._images = (before_image, after_image)

    def clear(self, *, before_text="Before", after_text="After"):
        self.before.configure(image="", text=before_text)
        self.after_label.configure(image="", text=after_text)
        self._images = ()
