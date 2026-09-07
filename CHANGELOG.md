# Changelog

## 0.2.2

- Add semantic `Surface` roles and typography variants for application shells.
- Expose reusable display, title, section, muted, and body font styles through `Theme.fonts`.
- Add `CodeEditor` with line numbers and cursor status for structured-text tools.
- Add optional button icons, `NavigationItem`, and search icon/shortcut affordances.
- Normalize Aqua against Tk's 96-DPI baseline to prevent duplicate Retina scaling.
- Avoid Aqua's high-cost stretched SVG card surfaces, cache packaged icon sources,
  and keep inactive Gallery pages out of live geometry passes.

## Unreleased

## 0.2.1

- Add reusable `CommandPalette` and trusted-image `ImageCompareView` compound primitives.

## 0.2.0

- Restyled Tabs, Tree disclosure spacing and Table headings with compact
  shadcn-inspired hierarchy and density-aware metrics.
- Let native scrolling children hand wheel input to an enclosing ScrollArea when
  they have no overflow or reach a directional boundary.
- Sized the Gallery viewport from the active page so resized content remains scrollable.
- Coalesced responsive Gallery layout and reduced cached-page resize work.
- Added keyboard-aware focus-ring policies to Theme.
- Restyled choice and menu popups with rounded themed surfaces and cleaner rows.
- Dismissed interactive popups on focus loss without stealing the new focus.
- Require Python 3.13+ linked to Tcl/Tk 9.0+ and reject older Tk runtimes.
- Replace generated PNG control assets and multiresolution PNG icons with Tk 9
  native SVG loading and packaged SVG sources.
- Move high-volume Frame/Label surfaces to lightweight ttk elements, reducing
  Gallery theme traversal from about 155 seconds to about 13 seconds locally.
- Coalesce ScrollArea layout work and cache Gallery pages after first creation.
- Add `check_runtime`, `load_svg` and `UnsupportedTkVersionError`.
- Add semantic light/dark themes, density, radius, font, contrast and token configuration export.
- Replace inherited control chrome with scoped antialiased elements and opaque Aqua-compatible surfaces.
- Add the input, structure, data, overlay and feedback component collection.
- Keep selection lists and menus attached to their application window, synchronize
  native popup appearance with light/dark themes, and stack up to three Toasts in
  the application bottom-right corner by default. Select rows are fully laid out
  before the popup's first visible frame to avoid text and checkmark flicker;
  opening no longer flushes application-wide idle layout work.
- Add a desktop studio with three application scenes, component examples and live theme editing.
- Preserve variable ownership, native editing and caller-owned event loops; keep runtime dependencies empty.
- Add platform CI jobs, native integration tests and clean-wheel verification.

## 0.1.0

- Replace prototype controls with explicit-parent ttk components and owned scheduling.
- Add scoped themes, English/Chinese labels, forms, lists, progress and dialogs.
- Consolidate packaging, zero third-party core dependencies, typed exports and examples.
- Break 0.0.1 names; see the migration guide.
