# Changelog

## 0.2.0 (unreleased)

- Require Python 3.13+ linked to Tcl/Tk 9.0+ and reject older Tk runtimes.
- Replace generated PNG control assets and multiresolution PNG icons with Tk 9
  native SVG loading and packaged SVG sources.
- Move high-volume Frame/Label surfaces to lightweight ttk elements, reducing
  Gallery theme traversal from about 155 seconds to about 13 seconds locally.
- Coalesce ScrollArea layout work and cache Gallery pages after first creation.
- Add `check_runtime`, `load_svg` and `UnsupportedTkVersionError`.

## 0.1.0

- Replace prototype controls with explicit-parent ttk components and owned scheduling.
- Add scoped themes, English/Chinese labels, forms, lists, progress and dialogs.
- Consolidate packaging, zero third-party core dependencies, typed exports and examples.
- Break 0.0.1 names; see the migration guide.

## Unreleased — desktop design system

- Add semantic light/dark themes, density, radius, font, contrast and token configuration export.
- Replace inherited control chrome with scoped antialiased elements and opaque Aqua-compatible surfaces.
- Add the input, structure, data, overlay and feedback component collection.
- Add a desktop studio with three application scenes, component examples and live theme editing.
- Preserve variable ownership, native editing and caller-owned event loops; keep runtime dependencies empty.
- Add platform CI jobs, native integration tests and clean-wheel verification.
