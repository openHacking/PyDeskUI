# ADR 0002: Own professional desktop appearance, preserve Tk contracts

Status: accepted for interaction/design direction; rendering details superseded
by ADR 0003. Date: 2026-09-04.

## Context

The lightweight core decision in ADR 0001 established explicit parents, ordinary
Tk integration and zero third-party runtime dependencies. Default host-theme
appearance alone does not supply the semantic surfaces, consistent control
spacing and configurable colors needed by the current desktop components.

## Decision

Own component appearance through semantic theme tokens, scoped ttk styles,
image-backed button/entry elements and limited Tk Canvas drawing. Preserve native
editing, selection, variables and callback contracts wherever components wrap
Tk/ttk. Keep application state, windows and the event loop with the caller.

This refines ADR 0001's appearance tradeoff: platform-native visuals are not the
priority for library-owned surfaces. Its dependency and embedding decisions
remain in force. The implementation uses only the Python standard library and
Tcl/Tk and does not activate a different global ttk theme.

Expose explicit light/dark modes, branding, color overrides, radius, density,
font settings, contrast and reduced motion through Theme. Export settings as a
Python dictionary. Configuring tokens replaces the override mapping, rather than
silently accumulating stale values. See the [design system](../design-system.md)
for accepted values and the [reference](../reference.md) for component APIs.

## Alternatives considered

- Host-theme styling alone preserves more OS visual variation but limits control
  over the current semantic appearance requirements.
- A mandatory third-party theme or rendering framework changes the zero-runtime-
  dependency contract.
- A Canvas-only toolkit requires reimplementing native text editing, selection
  and focus behavior across the whole component set.

The selected approach confines custom drawing to appearance and small decorative
surfaces while retaining native controls and methods for interaction. Choice
popups and nonmodal overlays use owned Tk windows/panels with explicit lifecycle
and dismissal behavior.

## Consequences

The library must maintain generated images, scoped styles, focus handling and
popup cleanup. Appearance is deliberately controlled but not guaranteed to be
pixel-identical across operating systems. Custom tokens can produce poor
contrast; high-contrast mode is an adjustment, not a conformance assertion.

Native callback signatures remain unchanged: commands may take no arguments,
Slider receives a numeric string, and selection uses existing virtual events.
Applications sort Table rows themselves. Decorative icons, static skeletons
and the current checkbutton-based Switch do not imply a complete custom renderer.

## Validation boundary

This decision records implementation choices, not platform or accessibility
test results. Verify keyboard behavior, focus restoration, scaling and lifecycle
in the intended deployment. No full-platform or screen-reader certification is
claimed. Future rendering or dependency changes require their own rationale and
measured evidence.
