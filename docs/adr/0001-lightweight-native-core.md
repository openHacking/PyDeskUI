# ADR 0001: Keep the native core lightweight and embeddable

> Design baseline: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

Status: accepted design direction; implementation pending. Date: 2026-09-03.

## Context

The prototype adds mandatory rendering dependencies even for a text button and violates ordinary tkinter parent/callback behavior. The library must serve arbitrary Python desktop applications, not just one tool host.

## Decision

Build on tkinter/ttk, require explicit parent ownership, preserve the application's event loop, and keep the core free of third-party runtime dependencies. Add reusable components only when a concrete application need exists. Keep image/SVG enhancement in optional adapters and business components outside the library.

## Alternatives considered

A mandatory themed framework would outsource more appearance work but introduce a runtime dependency and its compatibility policy. A Canvas-only toolkit would offer more drawing freedom but duplicate input, focus, accessibility and scaling behavior. A web-based renderer would change deployment and embedding costs substantially. None solves the immediate library contract problems better than a native core.

## Consequences

Native platform appearance may differ and advanced SVG/rounding effects are not guaranteed. The project must test Tk behavior and acknowledge accessibility limitations. Simple installation, ordinary tkinter usage and independent embedding take priority over pixel-identical styling.

## Revisit trigger

Revisit an optional adapter when a documented user task cannot be met adequately with ttk and prepared assets. Changing the core dependency policy requires a new ADR with measured installation, runtime and accessibility costs.
