"""Tk 9 image resources, including its native SVG reader."""

from __future__ import annotations

import math
import tkinter as tk
from pathlib import Path
from typing import Any, cast


class UnsupportedTkVersionError(RuntimeError):
    """Raised when PyDeskUI is attached to a pre-Tk 9 interpreter."""


def check_runtime(master: tk.Misc) -> str:
    """Return the Tk patch level or reject an interpreter older than Tk 9."""
    if master is None or not isinstance(master, tk.Misc):
        raise TypeError("An explicit Tk master is required")
    try:
        version = str(master.tk.call("package", "require", "Tk"))
        supported = int(master.tk.call("package", "vcompare", version, "9.0")) >= 0
    except tk.TclError as error:
        raise UnsupportedTkVersionError("PyDeskUI requires Tcl/Tk 9.0 or newer") from error
    if not supported:
        raise UnsupportedTkVersionError(
            f"PyDeskUI requires Tcl/Tk 9.0 or newer; this interpreter provides Tk {version}"
        )
    return version


def _read_resource(resource) -> bytes:
    if isinstance(resource, Path):
        return resource.read_bytes()
    if hasattr(resource, "read_bytes") and not isinstance(resource, (str, bytes, bytearray)):
        return resource.read_bytes()
    raise TypeError("resource must be a pathlib.Path or Traversable")


def _positive(value, name):
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return value


def svg_photo(master: tk.Misc, data: bytes | str, *, width=None, height=None, scale=None):
    """Create a Tk 9 PhotoImage from trusted SVG bytes or text."""
    check_runtime(master)
    selected = sum(value is not None for value in (width, height, scale))
    if selected > 1:
        raise ValueError("width, height and scale are mutually exclusive")
    if width is not None:
        image_format = ("svg", "-scaletowidth", round(_positive(width, "width")))
    elif height is not None:
        image_format = ("svg", "-scaletoheight", round(_positive(height, "height")))
    elif scale is not None:
        image_format = ("svg", "-scale", _positive(scale, "scale"))
    else:
        image_format = master.tk.call("set", "tk::svgFmt")
    return tk.PhotoImage(master=master, data=data, format=cast(Any, image_format))


def load_svg(master: tk.Misc, resource, *, width=None, height=None, scale=None) -> tk.PhotoImage:
    """Load an SVG resource with Tk 9's native, DPI-aware SVG reader."""
    data = _read_resource(resource)
    if b"<svg" not in data[:1024].lower():
        raise ValueError("resource is not SVG data")
    return svg_photo(master, data, width=width, height=height, scale=scale)


def load_image(master: tk.Misc, resource, *, size=None) -> tk.PhotoImage:
    """Load SVG, PNG or GIF data; SVG scaling preserves its aspect ratio."""
    check_runtime(master)
    data = _read_resource(resource)
    if b"<svg" in data[:1024].lower():
        if size is None:
            return svg_photo(master, data)
        width, height = tuple(size)
        _positive(width, "size width")
        _positive(height, "size height")
        image = svg_photo(master, data, width=width)
        if image.height() > round(height):
            image = svg_photo(master, data, height=height)
        return image
    if not data.startswith((b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a")):
        raise ValueError("resource must contain SVG, PNG or GIF data")
    image = tk.PhotoImage(master=master, data=data)
    if size is not None and tuple(size) != (image.width(), image.height()):
        raise ValueError("PNG/GIF resources must already have the requested size")
    return image
