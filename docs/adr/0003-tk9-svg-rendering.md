# ADR 0003: Require Tk 9 and use native SVG rendering

Status: accepted. Date: 2026-09-05. Supersedes the runtime and raster-rendering
parts of ADR 0001 and ADR 0002.

## Context

The first professional theme implementation generated antialiased PNG data in
Python for every rounded state. Profiling measured roughly 398 ms to construct a
Theme and 366 ms to switch it. Wrapping every Frame and Label in a stretchable
image element also made a full Aqua redraw take tens of seconds in the Gallery.
The cost came from rendering architecture rather than ordinary Tk widget creation.

## Decision

PyDeskUI 0.2 requires Python 3.13+ linked to Tcl/Tk 9.0+. Theme and component
construction rejects older Tk versions through `check_runtime`.

Bundled icons are SVG source files. Tk 9 reads SVG directly into PhotoImage at
the requested size or `tk::svgFmt` DPI scale. Compact rounded controls and
indicators may use SVG-backed ttk image elements. High-volume Frame and Label
surfaces use lightweight scoped ttk elements and semantic colors. Native Entry,
Text, Treeview, selection, variables, focus and keyboard behavior remain intact.

SVG photos are cached per Theme and interpreter with a 128-entry bound. Theme
updates mutate the fixed state images in place and retain scoped style names.
ScrollArea coalesces Configure events and skips unchanged geometry. Gallery pages
are created once and reused.

## Consequences

Tk 8.6 and its Python distributions are unsupported. SVG is parsed by Tk and
then displayed as pixel-backed PhotoImage data; it is regenerated at the target
scale rather than retained as a vector scene. External SVG files are limited to
Tk 9's supported SVG subset. No SVG or image package is added at runtime.

Cold operating-system window creation is recorded separately from steady-state
component timing. Platform claims require a Tk 9 test run on that platform.
