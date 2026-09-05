"""Offline, import-safe fixtures for PyDeskUI 0.2.x."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from pydeskui import (
    Button,
    Entry,
    ProgressView,
    Scheduler,
    load_image,
)


def embedded(parent):
    panel = ttk.Frame(parent)
    value = tk.StringVar(master=panel, value="Shared")
    Entry(panel, textvariable=value).pack()
    Entry(panel, textvariable=value).pack()
    Button(panel, text="Clear", command=lambda: value.set("")).pack()
    return panel


def cancellable(parent):
    panel = ttk.Frame(parent)
    scheduler = Scheduler(panel)
    handle = scheduler.call_later(1000, lambda: progress.update_progress(1, "Done"))
    progress = ProgressView(panel, on_cancel=handle.cancel)
    progress.pack()
    progress.update_progress(None, "Working")
    return panel


def image_fallback(parent, path):
    label = ttk.Label(parent, text="Image unavailable")
    try:
        image = load_image(parent, Path(path))
        label.configure(image=image)
        label.image = image
    except (OSError, ValueError):
        pass
    return label


def main():
    root = tk.Tk()
    embedded(root).pack()
    cancellable(root).pack()
    image_fallback(root, "missing.png").pack()
    root.mainloop()


if __name__ == "__main__":
    main()
