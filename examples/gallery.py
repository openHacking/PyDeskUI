"""Interactive desktop workbench. Run after installing PyDeskUI."""

import pprint
import tkinter as tk
from tkinter import colorchooser, filedialog, font

from pydeskui import (
    Alert,
    Badge,
    Button,
    Card,
    Checkbox,
    Combobox,
    ContextMenu,
    DetailView,
    Dialog,
    DropdownMenu,
    EmptyState,
    Entry,
    FieldSpec,
    Form,
    Frame,
    Icon,
    Item,
    ItemList,
    Label,
    Popover,
    ProgressView,
    RadioGroup,
    Scheduler,
    ScrollArea,
    SegmentedControl,
    Select,
    Separator,
    Sheet,
    Sidebar,
    Skeleton,
    Slider,
    Spinbox,
    SplitPane,
    Switch,
    Table,
    Tabs,
    Textarea,
    Theme,
    Toast,
    Toolbar,
    Tooltip,
)

PAGES = [
    ("settings", "Settings", "设置"),
    ("resources", "Resource browser", "资源浏览"),
    ("tasks", "Task monitor", "任务监控"),
    ("buttons", "Buttons & badges", "按钮与标记"),
    ("inputs", "Inputs & selection", "输入与选择"),
    ("layout", "Layout & data", "布局与数据"),
    ("feedback", "Overlays & feedback", "浮层与反馈"),
]

SNIPPETS = {
    "settings": 'Form(root, fields=[FieldSpec("name", "Name", "text", required=True),\n    FieldSpec("sync", "Sync", "boolean", default=True)],\n    on_submit=print, theme=theme).pack(fill="x", padx=24, pady=24)',
    "resources": 'view = ItemList(root, theme=theme, on_select=print)\nview.set_items([Item("guide", "Getting started", "Documentation")])\nview.pack(fill="both", expand=True)',
    "tasks": 'progress = ProgressView(root, theme=theme, on_cancel=lambda: print("cancel"))\nprogress.pack(fill="x", padx=24, pady=24)\nprogress.update_progress(0.64, "64% — Processing files")',
    "buttons": 'Button(root, text="Create project", variant="primary", theme=theme).pack(padx=24, pady=24)\nButton(root, text="Cancel", variant="outline", theme=theme).pack()',
    "inputs": 'value = tk.StringVar(master=root)\nEntry(root, textvariable=value, placeholder="Search projects…", theme=theme).pack()\nSelect(root, values=("Personal", "Team"), theme=theme).pack()\nSwitch(root, text="Notifications", theme=theme).pack()',
    "layout": 'panes = SplitPane(root, theme=theme)\npanes.pack(fill="both", expand=True)\npanes.add(Card(panes, theme=theme), weight=1)\npanes.add(Card(panes, theme=theme), weight=2)',
    "feedback": 'button = Button(root, text="Actions", theme=theme)\nmenu = DropdownMenu(button, items=[("New project", lambda: print("new"))], theme=theme)\nbutton.configure(command=menu.show)\nbutton.pack(padx=24, pady=24)',
}


def _system_theme_mode(root):
    """Return the current macOS appearance without changing Tk's host theme."""
    if root.tk.call("tk", "windowingsystem") != "aqua":
        return "light"
    try:
        is_dark = root.tk.getboolean(root.tk.call("wm", "attributes", root._w, "-isdark"))
    except tk.TclError:
        return "light"
    return "dark" if is_dark else "light"


class Gallery(Frame):
    def __init__(self, root):
        self.locale = "en"
        self._texts = []
        self._styled = []
        self._fonts = {}
        self._label_style_specs = set()
        self._page_views = {}
        self._page_heights = {}
        self._height_job = None
        self._responsive_job = None
        self._responsive_width = None
        self._responsive_size = None
        self._resize_armed = False
        self.page = "settings"
        self.theme_visible = True
        self._default_family = font.nametofont("TkDefaultFont", root=root).actual("family")
        self._manual_theme = True
        theme = Theme(root, mode=_system_theme_mode(root))
        super().__init__(root, theme=theme)
        self.pack(fill="both", expand=True)
        root.title("PyDeskUI — Desktop component studio")
        root.geometry("1180x800")
        root.minsize(900, 640)
        self.scheduler = Scheduler(self)
        self._appearance_bindings = [
            (
                "<<DarkAqua>>",
                root.bind(
                    "<<DarkAqua>>",
                    lambda event: self._system_appearance_changed("dark"),
                    add="+",
                ),
            ),
            (
                "<<LightAqua>>",
                root.bind(
                    "<<LightAqua>>",
                    lambda event: self._system_appearance_changed("light"),
                    add="+",
                ),
            ),
        ]
        self._job = None
        self._progress = 0
        self._build_shell()
        # Prebuild each page while immediately unmapping the previous one.
        # Widget construction is cheap; keeping inactive pages mapped is what
        # makes Aqua's first geometry pass and later resizes expensive.
        for key, _, _ in PAGES:
            self.show_page(key)
        self.show_page("settings")
        self.bind("<Configure>", self._responsive, add="+")
        self.after_idle(self._arm_resize)
        self.after_idle(self._sync_system_theme)
        self._refresh_theme()

    def tr(self, en, zh):
        return zh if self.locale == "zh_CN" else en

    def text(self, parent, en, zh=None, *, role="body", muted=False, surface="card", **kw):
        label = Label(parent, theme=self.theme, text=self.tr(en, zh or en), **kw)
        self._texts.append((label, en, zh or en))
        self._styled.append((label, role, muted, surface))
        self._style_label(label, role, muted, surface)
        return label

    def button(self, parent, en, zh=None, **kw):
        b = Button(parent, theme=self.theme, text=self.tr(en, zh or en), **kw)
        self._texts.append((b, en, zh or en))
        return b

    def _style_label(self, label, role, muted, surface):
        self._configure_label_style(role, muted, surface)
        label.configure(style=self._label_style_name(role, muted, surface))

    def _label_style_name(self, role, muted, surface):
        return self.theme.name(f"Gallery.{role}.{int(muted)}.{surface}.TLabel")

    def _configure_label_style(self, role, muted, surface):
        if role not in self._fonts:
            self._fonts[role] = font.Font(self, font=self.theme.font)
        sizes = {"body": 13, "small": 12, "heading": 16, "title": 24, "brand": 15}
        self._fonts[role].configure(
            family=self.theme.font_family,
            size=-self.theme.px(sizes[role] * self.theme.font_size / 13),
            weight="bold" if role in ("heading", "title", "brand") else "normal",
        )
        self._label_style_specs.add((role, muted, surface))
        style = self._label_style_name(role, muted, surface)
        self.theme.surface_style(style, surface, label=True)
        self.theme.style.configure(
            style,
            font=self._fonts[role],
            background=self.theme.tokens[surface],
            foreground=self.theme.tokens["muted_foreground"]
            if muted
            else self.theme.tokens.get(surface + "_foreground", self.theme.tokens["foreground"]),
        )

    def _refresh_theme(self):
        if not hasattr(self, "nav"):
            return
        self._styled = [v for v in self._styled if v[0].winfo_exists()]
        for role, muted, surface in tuple(self._label_style_specs):
            self._configure_label_style(role, muted, surface)
        self.master.configure(background=self.theme.tokens["background"])
        self._nav_styles()
        self.mode_button.configure(
            text=self.tr("Dark mode", "深色模式")
            if self.theme.mode == "light"
            else self.tr("Light mode", "浅色模式")
        )
        if self.page in self._page_views:
            self._queue_page_height(self.page)

    def _nav_styles(self):
        name = self.theme.name("Nav.TButton")
        c = self.theme.tokens
        element = self.theme._element(
            "gallery.nav",
            [
                self.theme._tile("gallery.nav", c["sidebar"], c["sidebar"]),
                ("selected", self.theme._tile("gallery.nav.selected", c["card"], c["card"])),
            ],
        )
        self.theme.style.layout(
            name,
            [
                (
                    element,
                    {
                        "sticky": "nsew",
                        "children": [
                            (
                                self.theme.name("portable.Button.padding"),
                                {
                                    "sticky": "nsew",
                                    "children": [
                                        (
                                            self.theme.name("portable.Button.label"),
                                            {"sticky": "nsew"},
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        self.theme.style.configure(
            name,
            padding=(12, 9),
            anchor="w",
            font=self.theme.font,
            foreground=c["foreground"],
        )
        self.theme.style.map(name, foreground=[("focus", c["primary"])])
        for key, button in self.nav_buttons.items():
            button.configure(style=name)
            button.state(("selected",) if key == self.page else ("!selected",))

    def _build_shell(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        top = Frame(self, theme=self.theme, padding=(24, 18))
        top.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.text(top, "PyDeskUI", role="brand").pack(side="left")
        Badge(top, text="STUDIO", variant="secondary", theme=self.theme).pack(side="left", padx=12)
        self.text(top, "A considered desktop toolkit", "精心设计的桌面组件", muted=True).pack(
            side="left", padx=16
        )
        self.button(top, "Theme", "主题", command=self.toggle_panel, size="small").pack(
            side="right"
        )
        self.button(
            top, "中文 / EN", command=self.toggle_locale, variant="ghost", size="small"
        ).pack(side="right", padx=8)
        self.mode_button = self.button(
            top, "Dark mode", "深色模式", command=self.toggle_mode, variant="ghost", size="small"
        )
        self.mode_button.pack(side="right")
        self.nav = Sidebar(self, theme=self.theme, width=188, padding=(16, 22))
        self.nav.grid(row=1, column=0, sticky="nsew")
        self.nav.grid_propagate(False)
        self.text(
            self.nav, "WORKSPACE", "工作空间", role="small", muted=True, surface="sidebar"
        ).pack(anchor="w", padx=8, pady=(0, 14))
        self.nav_buttons = {}
        for i, (key, en, zh) in enumerate(PAGES):
            if i == 3:
                self.text(
                    self.nav, "COMPONENTS", "组件", role="small", muted=True, surface="sidebar"
                ).pack(anchor="w", padx=8, pady=(30, 14))
            b = self.button(
                self.nav, en, zh, variant="ghost", command=lambda k=key: self.show_page(k)
            )
            b.pack(fill="x", pady=3)
            self.nav_buttons[key] = b
        self.text(
            self.nav,
            "Built for focus.\nMade to be yours.",
            "专注于工作。\n自由定义风格。",
            role="small",
            muted=True,
            surface="sidebar",
        ).pack(side="bottom", anchor="w", padx=8, pady=16)
        self.viewport = ScrollArea(self, theme=self.theme, resize_debounce_ms=80)
        self.viewport.grid(row=1, column=1, sticky="nsew")
        self.viewport.canvas.configure(highlightthickness=0)
        self.pages_host = self.viewport.content
        self.pages_host.configure(padding=(28, 24))
        self.pages_host.columnconfigure(0, weight=1)
        # Page frames may stay mapped for fast switching. Keep their requests
        # from forcing the scroll content to the tallest cached page.
        self.pages_host.grid_propagate(False)
        self.body = self.pages_host
        self.theme_panel = Frame(self, theme=self.theme, width=248, padding=(20, 24))
        self.theme_panel.grid(row=1, column=2, sticky="nsew")
        self.theme_panel.grid_propagate(False)
        self._build_theme_panel()
        self.status = Frame(self, theme=self.theme, padding=(24, 8))
        self.status.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.text(
            self.status,
            "Native interaction. Your visual language.",
            "原生交互，自定义视觉语言。",
            role="small",
            muted=True,
        ).pack(side="left")
        self.text(
            self.status,
            "Tk / ttk  ·  Zero dependencies",
            "Tk / ttk  ·  零运行时依赖",
            role="small",
            muted=True,
        ).pack(side="right")

    def _build_theme_panel(self):
        p = self.theme_panel
        self.text(p, "Make it yours", "定义你的主题", role="heading").pack(anchor="w")
        self.text(
            p, "Changes apply everywhere.", "所有组件实时更新。", muted=True, role="small"
        ).pack(anchor="w", pady=(6, 24))
        for en, zh, values, value, key in (
            ("Density", "密度", ("compact", "default", "comfortable"), "default", "density"),
            ("Corner radius", "圆角", ("0", "4", "6", "8", "10", "12"), "6", "radius"),
            ("Text size", "字号", ("12", "13", "14", "16", "18"), "13", "font_size"),
        ):
            self.text(p, en, zh, role="small").pack(anchor="w", pady=(0, 6))
            box = Select(p, theme=self.theme, values=values, width=17)
            box.set(value)
            box.pack(fill="x", pady=(0, 18))
            box.bind("<<ComboboxSelected>>", lambda e, k=key, b=box: self.change_theme(k, b.get()))
            setattr(self, key + "_control", box)
        self.text(p, "Brand color", "品牌色", role="small").pack(anchor="w", pady=(0, 8))
        row = Frame(p, theme=self.theme)
        row.pack(fill="x", pady=(0, 18))
        self.button(
            row,
            "Neutral",
            "中性色",
            command=lambda: self.theme.configure(accent=None),
            size="small",
        ).pack(side="left")
        self.button(row, "Choose…", "选择…", command=self.choose_color, size="small").pack(
            side="right"
        )
        self.motion_var = tk.BooleanVar(master=self)
        self.contrast_var = tk.BooleanVar(master=self)
        Switch(
            p,
            text="Reduce motion",
            variable=self.motion_var,
            theme=self.theme,
            command=lambda: self.theme.configure(reduced_motion=self.motion_var.get()),
        ).pack(anchor="w", pady=6)
        Checkbox(
            p,
            text="High contrast",
            variable=self.contrast_var,
            theme=self.theme,
            command=lambda: self.theme.configure(
                contrast="high" if self.contrast_var.get() else "normal"
            ),
        ).pack(anchor="w", pady=6)
        Separator(p, theme=self.theme).pack(fill="x", pady=20)
        self.button(
            p, "Copy theme code", "复制主题配置", variant="primary", command=self.copy_theme
        ).pack(fill="x")
        self.button(p, "Save configuration…", "保存配置…", command=self.save_theme).pack(
            fill="x", pady=8
        )
        self.button(
            p, "Edit semantic tokens…", "编辑语义变量…", variant="ghost", command=self.edit_tokens
        ).pack(fill="x")
        self.button(
            p, "Reset defaults", "恢复默认", variant="ghost", command=self.reset_theme
        ).pack(fill="x")
        self.text(
            p,
            "Semantic tokens keep every\ncomponent in harmony.",
            "语义化主题变量，\n让所有组件保持一致。",
            muted=True,
            role="small",
        ).pack(anchor="w", pady=24)

    def change_theme(self, key, value):
        self.theme.configure(**{key: int(value) if key in ("radius", "font_size") else value})

    def choose_color(self):
        _, color = colorchooser.askcolor(
            parent=self.master, initialcolor=self.theme.tokens["primary"]
        )
        if color:
            self.theme.configure(accent=color)

    def toggle_mode(self):
        mode = "dark" if self.theme.mode == "light" else "light"
        self.theme.configure(mode=mode)

    def _system_appearance_changed(self, mode):
        if self.theme.mode != mode:
            self.theme.configure(mode=mode)

    def _sync_system_theme(self):
        mode = _system_theme_mode(self.master)
        if self.theme.mode != mode:
            self.theme.configure(mode=mode)

    def toggle_locale(self):
        self.locale = "zh_CN" if self.locale == "en" else "en"
        self.theme.translator.configure(locale=self.locale)
        self._texts = [v for v in self._texts if v[0].winfo_exists()]
        for widget, en, zh in self._texts:
            widget.configure(text=self.tr(en, zh))
        self._refresh_theme()

    def toggle_panel(self):
        self._manual_theme = not self.theme_visible
        self._set_panel(self._manual_theme)

    def _set_panel(self, visible):
        visible = bool(visible)
        if self.theme_visible == visible:
            return
        self.theme_visible = visible
        if visible:
            self.theme_panel.grid()
        else:
            self.theme_panel.grid_remove()

    def _responsive(self, event):
        if event.widget is self:
            size = (event.width, event.height)
            resized = self._responsive_size is not None and size != self._responsive_size
            self._responsive_size = size
            if self._resize_armed and resized:
                self._unmap_inactive_pages()
            self._responsive_width = event.width
            if self._responsive_job is None:
                self._responsive_job = self.after(24, self._apply_responsive)

    def _arm_resize(self):
        self._resize_armed = True

    def _apply_responsive(self):
        self._responsive_job = None
        width = self._responsive_width
        if width is not None:
            self._set_panel(width >= 1080 and self._manual_theme)
        if self.page in self._page_views:
            self._queue_page_height(self.page)

    def _unmap_inactive_pages(self):
        """During live resize, keep geometry work limited to the visible page."""
        for key, page in self._page_views.items():
            if key != self.page and page.winfo_ismapped():
                page.grid_remove()

    def reset_theme(self):
        self.theme.configure(
            mode=_system_theme_mode(self.master),
            accent=None,
            tokens={},
            radius=6,
            density="default",
            font_size=13,
            font_family=self._default_family,
            contrast="normal",
            reduced_motion=False,
        )
        for key, value in (("density", "default"), ("radius", "6"), ("font_size", "13")):
            getattr(self, key + "_control").set(value)
        self.motion_var.set(False)
        self.contrast_var.set(False)

    def edit_tokens(self):
        if hasattr(self, "token_sheet") and self.token_sheet.winfo_exists():
            self.token_sheet.destroy()
        sheet = self.token_sheet = Sheet(
            self, title=self.tr("Theme details", "主题详情"), size=380, theme=self.theme
        )
        bar = Frame(sheet.content, theme=self.theme, padding=16)
        bar.pack(side="bottom", fill="x")
        area = ScrollArea(sheet.content, theme=self.theme)
        area.pack(fill="both", expand=True)
        content = area.content
        content.configure(padding=16)
        self.text(content, "Font family", "字体").pack(anchor="w", pady=(0, 6))
        family = tk.StringVar(master=sheet, value=self.theme.font_family)
        Combobox(
            content, values=sorted(font.families(self)), textvariable=family, theme=self.theme
        ).pack(fill="x", pady=(0, 16))
        self.text(
            content,
            "Override only the colors you need.",
            "只覆盖需要自定义的颜色。",
            muted=True,
            wraplength=280,
        ).pack(anchor="w", pady=(0, 16))
        variables = {}
        for token in self.theme.tokens:
            self.text(content, token, role="small").pack(anchor="w", pady=(8, 4))
            variables[token] = tk.StringVar(
                master=sheet, value=self.theme._overrides.get(token, "")
            )
            Entry(
                content,
                textvariable=variables[token],
                placeholder=self.theme.tokens[token],
                theme=self.theme,
            ).pack(fill="x")
        error = self.text(bar, "", wraplength=300)
        error.pack(fill="x", pady=(0, 8))

        def apply():
            overrides = {k: v.get().strip() for k, v in variables.items() if v.get().strip()}
            try:
                self.theme.configure(tokens=overrides, font_family=family.get())
            except ValueError as exc:
                error.configure(text=str(exc))
            else:
                error.configure(text=self.tr("Theme updated", "主题已更新"))

        self.button(bar, "Apply theme", "应用主题", variant="primary", command=apply).pack(fill="x")
        sheet.show()

    def _theme_code(self):
        return (
            "from pydeskui import Theme\n\ntheme = Theme(root, **"
            + pprint.pformat(self.theme.export(), sort_dicts=False)
            + ")\n"
        )

    def copy(self, code):
        self.clipboard_clear()
        self.clipboard_append(code)
        self.notify(self.tr("Copied to clipboard", "已复制到剪贴板"))

    def copy_theme(self):
        self.copy(self._theme_code())

    def save_theme(self):
        path = filedialog.asksaveasfilename(
            parent=self.master,
            defaultextension=".py",
            initialfile="desktop_theme.py",
            filetypes=[("Python", "*.py")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as stream:
                stream.write(self._theme_code())
            self.notify(self.tr("Configuration saved", "配置已保存"))

    def notify(self, message):
        if hasattr(self, "toast") and self.toast.winfo_exists():
            self.toast.destroy()
        self.toast = Toast(self.master, text=message, theme=self.theme)
        self.toast.show()

    def card(self, title, subtitle=None, zh=None, zh_sub=None):
        card = Card(self.body, theme=self.theme, padding=20)
        card.pack(fill="x", pady=(0, 18))
        self.text(card, title, zh, role="heading").pack(anchor="w")
        if subtitle:
            self.text(card, subtitle, zh_sub, muted=True, wraplength=540).pack(
                anchor="w", pady=(6, 16)
            )
        return card

    def row(self, parent):
        row = Frame(parent, theme=self.theme)
        row.pack(fill="x", pady=(8, 4))
        return row

    def show_page(self, key):
        if self._job:
            self._job.cancel()
            self._job = None
        previous = self.page
        if key == previous and key in self._page_views:
            return
        self.page = key
        if previous in self.nav_buttons and previous != key:
            self.nav_buttons[previous].state(("!selected",))
        previous_page = self._page_views.get(previous)
        if previous_page is not None and previous != key:
            previous_page.grid_remove()
        self.nav_buttons[key].state(("selected",))
        if key in self._page_views:
            self.body = self._page_views[key]
            self.body.grid()
            self.body.tkraise()
            self._queue_page_height(key)
            self.viewport.canvas.yview_moveto(0)
            return
        self.body = Frame(self.pages_host, theme=self.theme)
        self._page_views[key] = self.body
        self.body.grid(row=0, column=0, sticky="nsew")
        self.body.tkraise()
        titles = {k: (en, zh) for k, en, zh in PAGES}
        heading = self.row(self.body)
        self.text(heading, *titles[key], role="title").pack(side="left")
        self.button(
            heading,
            "Copy example",
            "复制示例",
            variant="ghost",
            size="small",
            command=self.copy_example,
        ).pack(side="right")
        subtitles = {
            "settings": (
                "A quiet space to make things work your way.",
                "让工作方式，符合你的习惯。",
            ),
            "resources": (
                "Find what matters. Keep the details close.",
                "快速找到资源，就近查看详情。",
            ),
            "tasks": (
                "Clear progress, useful feedback, complete control.",
                "清晰的进度，有用的反馈，可控的任务。",
            ),
            "buttons": (
                "Purposeful actions, a consistent visual rhythm.",
                "清晰的操作层级，一致的视觉节奏。",
            ),
            "inputs": (
                "Native editing. Thoughtfully designed states.",
                "原生编辑能力，完整的交互状态。",
            ),
            "layout": ("Structure for real desktop workflows.", "为真实桌面工作流提供结构。"),
            "feedback": (
                "Keep people informed without breaking their flow.",
                "传递必要信息，保持工作连贯。",
            ),
        }
        self.text(self.body, *subtitles[key], muted=True, wraplength=560).pack(
            anchor="w", pady=(4, 24)
        )
        getattr(self, "page_" + key)()
        self._queue_page_height(key)
        self.viewport.canvas.yview_moveto(0)

    def _queue_page_height(self, key):
        if self._height_job is not None:
            self.after_cancel(self._height_job)
        self._height_job = self.after_idle(lambda: self._sync_page_height(key))

    def _sync_page_height(self, key):
        self._height_job = None
        page = self._page_views.get(key)
        if page is None or not page.winfo_exists():
            return
        height = max(1, page.winfo_reqheight())
        self._page_heights[key] = height
        if key != self.page:
            return
        if int(float(self.pages_host.cget("height"))) != height:
            self.pages_host.configure(height=height)
        self.viewport._queue_layout()

    def _sync_all_page_heights(self):
        for key, page in self._page_views.items():
            if page.winfo_exists():
                self._page_heights[key] = max(1, page.winfo_reqheight())
        self._sync_page_height(self.page)

    def copy_example(self):
        code = (
            "import tkinter as tk\nfrom pydeskui import *\n\nroot = tk.Tk()\n"
            "theme = Theme(root)\n" + SNIPPETS[self.page] + "\nroot.mainloop()\n"
        )
        self.copy(code)

    def page_settings(self):
        c = self.card(
            "Workspace profile",
            "Your workspace identity and defaults.",
            "工作空间资料",
            "管理工作空间的名称和默认设置。",
        )
        self.text(c, "Workspace name", "工作空间名称", role="small").pack(anchor="w", pady=(0, 6))
        Entry(
            c, theme=self.theme, textvariable=tk.StringVar(master=c, value="Design workspace")
        ).pack(fill="x")
        self.text(
            c,
            "Used in your sidebar and shared projects.",
            "显示在侧栏和共享项目中。",
            role="small",
            muted=True,
        ).pack(anchor="w", pady=(6, 18))
        row = self.row(c)
        row.columnconfigure((0, 1), weight=1, uniform="profile")
        for col, (en, zh, choices) in enumerate(
            (
                ("Visibility", "可见性", ("Private", "Team", "Public")),
                ("Default view", "默认视图", ("List", "Grid", "Details")),
            )
        ):
            field = Frame(row, theme=self.theme)
            field.grid(row=0, column=col, sticky="ew", padx=(0, 12) if col == 0 else (0, 0))
            self.text(field, en, zh, role="small").pack(anchor="w", pady=(0, 6))
            box = Select(field, theme=self.theme, values=choices, width=15)
            box.set(choices[0])
            box.pack(fill="x")
        Separator(c, theme=self.theme).pack(fill="x", pady=20)
        row = self.row(c)
        self.text(row, "Personal workspace", "个人工作空间", muted=True, role="small").pack(
            side="left"
        )
        self.button(
            row,
            "Save changes",
            "保存更改",
            variant="primary",
            command=lambda: self.notify(self.tr("Workspace updated", "工作空间已更新")),
        ).pack(side="right")
        c = self.card(
            "Preferences",
            "Small details that make work feel better.",
            "偏好设置",
            "让工作更舒适的小细节。",
        )
        for en, zh, desc, zh_desc in (
            (
                "Desktop notifications",
                "桌面通知",
                "Know when a background task finishes.",
                "后台任务完成时获得提示。",
            ),
            (
                "Restore your workspace",
                "恢复工作空间",
                "Pick up where you left off.",
                "下次打开时继续之前的工作。",
            ),
        ):
            row = self.row(c)
            switch = Switch(row, theme=self.theme, variable=tk.BooleanVar(master=row, value=True))
            switch.pack(side="right", padx=(16, 0))
            text = Frame(row, theme=self.theme)
            text.pack(side="left", fill="x", expand=True)
            self.text(text, en, zh).pack(anchor="w")
            self.text(text, desc, zh_desc, muted=True, role="small").pack(anchor="w", pady=(4, 12))
        self.text(
            self.body,
            "Changes stay in this demo. No account required.",
            "设置仅用于本地演示，无需账号。",
            muted=True,
            role="small",
        ).pack(anchor="w")

    def page_resources(self):
        c = self.card(
            "Project library",
            "Browse project files and notes.",
            "项目资源库",
            "浏览项目文件和笔记。",
        )
        detail = DetailView(c, theme=self.theme)
        items = [
            Item("guide", "Getting started", "Documentation"),
            Item("tokens", "Design tokens", "Theme reference"),
            Item("release", "Release checklist", "Project notes"),
            Item("assets", "Brand assets", "Resources"),
        ]
        view = ItemList(
            c,
            theme=self.theme,
            on_select=lambda key: detail.set_content(
                next((i.title for i in items if i.id == key), "Selection"),
                "A shared place for the details that matter.\n\nUse the arrow keys to browse. Theme changes preserve your selection.",
            ),
        )
        from pydeskui import SearchEntry

        search = SearchEntry(
            c,
            theme=self.theme,
            placeholder="Search resources…",
            on_change=lambda text: view.set_items(
                [i for i in items if text.lower() in i.title.lower()]
            ),
        )
        search.pack(fill="x", pady=(0, 16))
        view.set_items(items)
        view.tree.configure(height=5)
        view.pack(fill="x")
        detail.text.configure(height=9)
        detail.pack(fill="both", expand=True, pady=(20, 0))
        view.tree.selection_set("guide")
        ContextMenu(
            view.tree,
            items=[
                ("Open", lambda: self.notify("Opened resource")),
                ("Copy name", lambda: self.copy(view.selected_id() or "")),
            ],
            theme=self.theme,
        )

    def page_tasks(self):
        c = self.card(
            "Export workspace",
            "Prepare a local bundle of your project.",
            "导出工作空间",
            "将项目整理为本地资源包。",
        )
        row = self.row(c)
        Badge(row, text="READY", variant="secondary", theme=self.theme).pack(side="left")
        self.text(row, "24 files · Local destination", "24 个文件 · 本地目录", muted=True).pack(
            side="left", padx=12
        )
        self.progress = ProgressView(c, theme=self.theme, on_cancel=self.cancel_task)
        self.progress.pack(fill="x", pady=20)
        self.progress.update_progress(0, self.tr("Ready to export", "准备导出"))
        self.progress.cancel.state(["disabled"])
        self.button(c, "Start export", "开始导出", variant="primary", command=self.start_task).pack(
            anchor="e"
        )
        c = self.card(
            "Activity",
            "A readable record of the work in progress.",
            "任务记录",
            "清楚记录当前任务的运行情况。",
        )
        self.log = DetailView(c, theme=self.theme)
        self.log.text.configure(height=12)
        self.log.set_content("Session log", "Waiting for a task…", "code")
        self.log.pack(fill="both", expand=True)

    def start_task(self):
        if self._job:
            self._job.cancel()
        self._progress = 0
        self.progress.cancel.state(["!disabled"])
        self._tick_task()

    def _tick_task(self):
        self._progress = min(1, self._progress + 0.04)
        self.progress.update_progress(
            self._progress, f"{self._progress:.0%} — " + self.tr("Preparing files", "正在整理文件")
        )
        self.log.set_content(
            "Session log",
            "[ready] Workspace opened\n[scan] 24 files discovered\n"
            + f"[export] {round(24 * self._progress)} / 24 files",
            "code",
        )
        if self._progress < 1:
            self._job = self.scheduler.call_later(160, self._tick_task)
        else:
            self._job = None
            self.progress.update_progress(1, self.tr("Export complete", "导出完成"))
            self.progress.cancel.state(["disabled"])
            self.notify(self.tr("Workspace exported", "工作空间已导出"))

    def cancel_task(self):
        if self._job:
            self._job.cancel()
            self._job = None
        self.progress.update_progress(self._progress, self.tr("Canceled", "已取消"))
        self.progress.cancel.state(["disabled"])

    def page_buttons(self):
        c = self.card(
            "Action hierarchy",
            "A distinct treatment for each kind of action.",
            "操作层级",
            "不同操作采用不同视觉强度。",
        )
        for variants in (("primary", "secondary", "outline"), ("ghost", "destructive", "link")):
            row = self.row(c)
            for variant in variants:
                self.button(
                    row,
                    variant.title(),
                    variant=variant,
                    command=lambda v=variant: self.notify(v + " clicked"),
                ).pack(side="left", padx=(0, 12))
        c = self.card(
            "Sizes & states",
            "Keyboard focus is visible without changing layout.",
            "尺寸与状态",
            "键盘焦点清晰可见，不改变布局。",
        )
        row = self.row(c)
        for size in ("small", "medium", "large"):
            self.button(row, size.title(), size=size).pack(side="left", padx=(0, 12))
        row = self.row(c)
        for state in ("disabled", "focus", "pressed", "active"):
            b = self.button(row, state.title(), size="small")
            b.state([state])
            b.pack(side="left", padx=(0, 8))
        row = self.row(c)
        for variant in ("default", "secondary", "outline"):
            Badge(row, text=variant.title(), variant=variant, theme=self.theme).pack(
                side="left", padx=(0, 12)
            )
        row = self.row(c)
        for name in sorted(Icon._names):
            Icon(row, name=name, size=20, theme=self.theme).pack(side="left", padx=8)

    def page_inputs(self):
        c = self.card(
            "Text & selection",
            "Real variables, native editing and clear feedback.",
            "文本与选择",
            "保留变量绑定和原生编辑能力。",
        )
        entry = Entry(c, placeholder="Your project name", theme=self.theme)
        entry.pack(fill="x", pady=6)
        invalid = Entry(
            c,
            textvariable=tk.StringVar(master=c, value=""),
            placeholder="Required field",
            invalid=True,
            theme=self.theme,
        )
        invalid.pack(fill="x", pady=6)
        self.text(c, "Enter a project name to continue.", "请输入项目名称。", role="small").pack(
            anchor="w"
        )
        disabled = Entry(c, textvariable=tk.StringVar(master=c, value="Disabled"), theme=self.theme)
        disabled.state(["disabled"])
        disabled.pack(fill="x", pady=6)
        text = Textarea(c, theme=self.theme, height=3)
        text.insert("1.0", "A place for longer thoughts…")
        text.pack(fill="x", pady=8)
        row = self.row(c)
        box = Select(row, theme=self.theme, values=("Python", "TypeScript", "Swift"), width=18)
        box.set("Python")
        box.pack(side="left")
        Spinbox(row, theme=self.theme, from_=0, to=100, width=8).pack(side="left", padx=12)
        SegmentedControl(
            c,
            values=(("list", "List"), ("grid", "Grid"), ("details", "Details")),
            theme=self.theme,
        ).pack(fill="x", pady=8)
        row = self.row(c)
        Checkbox(row, text="Include archived", theme=self.theme).pack(side="left")
        Switch(row, text="Auto save", theme=self.theme).pack(side="right")
        RadioGroup(
            c, values=("Personal", "Team", "Organization"), orient="horizontal", theme=self.theme
        ).pack(anchor="w", pady=12)
        Slider(c, from_=0, to=100, theme=self.theme).pack(fill="x", pady=8)
        c = self.card(
            "Validated form",
            "Errors appear beside the fields they describe.",
            "表单验证",
            "错误提示显示在对应字段旁。",
        )
        Form(
            c,
            fields=[
                FieldSpec("name", "Name", "text", required=True),
                FieldSpec("count", "Count", "integer", default=2),
            ],
            on_submit=lambda values: self.notify(str(values)),
            theme=self.theme,
        ).pack(fill="x")

    def page_layout(self):
        c = self.card(
            "Data table",
            "Select rows, resize columns, and request sorting.",
            "数据表格",
            "选择行、调整列宽和请求排序。",
        )
        table = Table(c, columns=("Name", "Type", "Updated"), theme=self.theme, height=5)
        for column, width in (("Name", 220), ("Type", 140), ("Updated", 100)):
            table.column(column, width=width, minwidth=60)
        for i, row in enumerate(
            (
                ("Design system", "Workspace", "Today"),
                ("Components", "Library", "Today"),
                ("Documentation", "Collection", "Yesterday"),
            )
        ):
            table.insert("", "end", iid=str(i), values=row)
        table.pack(fill="x", pady=8)
        c = self.card(
            "Tabs & split panes",
            "Native navigation and adjustable workspace regions.",
            "标签与分栏",
            "原生导航与可调整的工作区域。",
        )
        tabs = Tabs(c, theme=self.theme)
        tabs.pack(fill="x", pady=8)
        a = Frame(tabs, theme=self.theme)
        a_content = Card(a, theme=self.theme, padding=16)
        a_content.pack(fill="x", pady=(8, 0))
        self.text(
            a_content, "Overview of the selected project.", "当前项目概览。"
        ).pack(anchor="w")
        tabs.add(a, text="Overview")
        b = Frame(tabs, theme=self.theme)
        b_content = Card(b, theme=self.theme, padding=16)
        b_content.pack(fill="x", pady=(8, 0))
        self.text(
            b_content, "Recent project activity appears here.", "项目近期活动。"
        ).pack(anchor="w")
        tabs.add(b, text="Activity")
        pane = SplitPane(c, theme=self.theme, height=150)
        pane.pack(fill="x", pady=16)
        from pydeskui import Tree

        tree = Tree(pane, theme=self.theme, height=4)
        tree.insert("", "end", iid="workspace", text="Workspace", open=True)
        tree.insert("workspace", "end", text="Documents")
        tree.insert("workspace", "end", text="Assets")
        pane.add(tree, weight=1)
        info = Frame(pane, theme=self.theme, padding=16)
        self.text(info, "Drag the divider", "拖动分隔条").pack(anchor="w")
        pane.add(info, weight=1)
        tools = Toolbar(c, theme=self.theme)
        tools.pack(fill="x")
        self.button(tools, "New item", "新建", size="small").pack(side="left")
        self.button(tools, "Archive", "归档", variant="ghost", size="small").pack(
            side="left", padx=8
        )

    def page_feedback(self):
        c = self.card(
            "Contextual actions",
            "Surfaces appear where the action begins.",
            "上下文操作",
            "浮层出现在操作发生的位置。",
        )
        row = self.row(c)
        action = self.button(row, "Open menu", "打开菜单")
        action.pack(side="left", padx=(0, 10))
        menu = DropdownMenu(
            action,
            items=[
                ("New project", lambda: self.notify("New project")),
                None,
                ("Duplicate", lambda: self.notify("Duplicated")),
            ],
            theme=self.theme,
        )
        action.configure(command=menu.show)
        anchor = self.button(row, "Popover", "弹出面板")
        anchor.pack(side="left", padx=(0, 10))
        popup = Popover(anchor, theme=self.theme)
        self.text(popup.content, "Quick settings", "快捷设置", role="heading").pack(
            padx=20, pady=12
        )
        Entry(popup.content, placeholder="Project name", theme=self.theme).pack(padx=20, pady=12)
        anchor.configure(command=popup.show)
        tip = self.button(row, "Hover for help", "悬停查看帮助", variant="ghost")
        tip.pack(side="left")
        Tooltip(tip, text="A little context, right when you need it.", theme=self.theme)
        row = self.row(c)
        self.button(row, "Open dialog", "打开对话框", command=self.open_dialog).pack(
            side="left", padx=(0, 10)
        )
        self.button(
            row,
            "Show toast",
            "显示通知",
            command=lambda: self.notify("Your changes have been saved."),
        ).pack(side="left", padx=(0, 10))
        sheet = Sheet(self.viewport, title="Project details", theme=self.theme)
        self.text(sheet.content, "An in-app inspector.", "应用内详情面板。").pack(padx=20, pady=20)
        self.button(row, "Open sheet", "打开侧面板", command=sheet.show).pack(side="left")
        # The sheet is owned by this page even though it overlays the viewport.
        c.bind(
            "<Destroy>",
            lambda e: sheet.destroy() if e.widget is c and sheet.winfo_exists() else None,
            add="+",
        )
        c = self.card(
            "Status & empty states",
            "Always explain what is happening and what comes next.",
            "状态与空内容",
            "解释当前状态以及下一步操作。",
        )
        Alert(
            c, title="All changes saved", message="Your workspace is up to date.", theme=self.theme
        ).pack(fill="x", pady=8)
        Alert(
            c,
            title="Connection unavailable",
            message="Check your connection and try again.",
            variant="destructive",
            theme=self.theme,
        ).pack(fill="x", pady=8)
        EmptyState(
            c,
            title="No results yet",
            message="Try another search or add your first item.",
            theme=self.theme,
        ).pack(fill="x", pady=8)
        Skeleton(c, lines=3, theme=self.theme).pack(fill="x", pady=12)

    def open_dialog(self):
        Dialog(
            self,
            title="Save changes?",
            message="Keep your latest workspace changes.",
            actions=[("save", "Save changes"), ("cancel", "Cancel")],
            default_action="save",
            cancel_action="cancel",
            theme=self.theme,
        ).show(lambda result: self.notify(str(result)))

    def _cleanup(self):
        for sequence, binding in self._appearance_bindings:
            if binding:
                self.master.unbind(sequence, binding)
        for job in (self._height_job, self._responsive_job):
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
        self.scheduler.close()


def main():
    root = tk.Tk()
    Gallery(root)
    root.mainloop()


if __name__ == "__main__":
    main()
