"""Declarative field layout without application-schema or plugin knowledge."""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Any, Literal

from ..theme import resolve_theme
from ._base import Owned
from .controls import Button, Entry
from .inputs import Checkbox, Select, Textarea


@dataclass(frozen=True)
class FieldSpec:
    id: str
    label: str
    kind: Literal["text", "multiline", "integer", "boolean", "choice"]
    required: bool = False
    default: object = None
    choices: tuple[str, ...] = ()


class Form(Owned, ttk.Frame):
    """Form layout and required/type/choice checks; errors are visible text."""

    def __init__(self, master, *, fields, on_submit=None, theme=None):
        self.fields = tuple(fields)
        ids = [field.id for field in self.fields]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError("Field IDs must be unique nonempty strings")
        if any(
            f.kind not in ("text", "multiline", "integer", "boolean", "choice") for f in self.fields
        ):
            raise ValueError("Unknown field kind")
        theme = resolve_theme(master, theme)
        super().__init__(master, style=theme.name("TFrame"))
        self._own(master, theme)
        self.on_submit = on_submit
        self.controls: dict[str, Any] = {}
        self.variables = {}
        self.errors = {}
        self._error_values = {}
        for index, field in enumerate(self.fields):
            ttk.Label(self, text=field.label, style=theme.name("TLabel")).grid(
                row=index * 3, column=0, sticky="w", pady=(16, 6)
            )
            control: tk.Widget
            if field.kind == "multiline":
                control = Textarea(self, theme=theme, width=60, height=5, undo=True, wrap="word")
                control.bind("<Tab>", self._next_focus)
                control.bind("<Shift-Tab>", self._previous_focus)
                self.rowconfigure(index * 3 + 1, weight=1)
            else:
                var = tk.StringVar(master=self)
                self.variables[field.id] = var
                if field.kind == "boolean":
                    control = Checkbox(
                        self,
                        variable=var,
                        onvalue="true",
                        offvalue="false",
                        theme=theme,
                    )
                elif field.kind == "choice":
                    control = Select(
                        self,
                        textvariable=var,
                        values=field.choices,
                        state="readonly",
                        theme=theme,
                    )
                else:
                    control = Entry(self, textvariable=var, theme=theme)
            control.grid(row=index * 3 + 1, column=0, sticky="nsew")
            self.controls[field.id] = control
            label = ttk.Label(self, style=theme.name("Danger.TLabel"))
            label.grid(row=index * 3 + 2, column=0, sticky="w", pady=(4, 0))
            label.grid_remove()
            self.errors[field.id] = label
        self.submit_button = Button(self, command=self._submit, theme=theme, variant="primary")
        if on_submit:
            self.submit_button.grid(row=len(self.fields) * 3, column=0, sticky="e", pady=8)
        self.columnconfigure(0, weight=1)
        self.set_values({f.id: f.default for f in self.fields})
        self._refresh_theme()

    @staticmethod
    def _next_focus(event):
        event.widget.tk_focusNext().focus_set()
        return "break"

    @staticmethod
    def _previous_focus(event):
        event.widget.tk_focusPrev().focus_set()
        return "break"

    def _refresh_theme(self):
        self.submit_button.configure(text=self._t("Run"))
        for field in self.fields:
            if field.kind == "multiline":
                self.controls[field.id].configure(
                    background=self.theme.colors["surface"],
                    foreground=self.theme.colors["text"],
                    insertbackground=self.theme.colors["text"],
                )

    def get_values(self):
        result = {}
        errors = {}
        for field in self.fields:
            value = (
                self.controls[field.id].get("1.0", "end-1c")
                if field.kind == "multiline"
                else self.variables[field.id].get()
            )
            if field.required and value == "":
                errors[field.id] = self._t("Required")
            elif field.kind == "integer" and value != "":
                try:
                    value = int(value)
                except ValueError:
                    errors[field.id] = self._t("Enter an integer")
            elif field.kind == "boolean":
                value = value == "true"
            elif field.kind == "choice" and value not in field.choices and value != "":
                errors[field.id] = self._t("Choose a listed value")
            result[field.id] = value
        self.set_errors(errors)
        if errors:
            raise ValueError("Invalid form values")
        return result

    def set_values(self, values):
        unknown = set(values) - set(self.controls)
        if unknown:
            raise ValueError(f"Unknown fields: {sorted(unknown)}")
        for field in self.fields:
            if field.id not in values:
                continue
            value = values[field.id]
            if field.kind == "multiline":
                control = self.controls[field.id]
                control.delete("1.0", "end")
                control.insert("1.0", "" if value is None else str(value))
            else:
                self.variables[field.id].set(
                    ("true" if value else "false")
                    if field.kind == "boolean"
                    else ""
                    if value is None
                    else str(value)
                )

    def set_errors(self, errors):
        if set(errors) - set(self.errors):
            raise ValueError("Unknown field in errors")
        self._error_values = dict(errors)
        for identifier, label in self.errors.items():
            message = errors.get(identifier, "")
            label.configure(text=message)
            if message:
                label.grid()
            else:
                label.grid_remove()
            control = self.controls[identifier]
            if hasattr(control, "state"):
                control.state(["invalid"] if message else ["!invalid"])

    def _submit(self):
        try:
            values = self.get_values()
        except ValueError:
            return
        if self.on_submit:
            self.on_submit(values)
