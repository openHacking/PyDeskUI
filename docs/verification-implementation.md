# 0.1.0 implementation verification

Validated on macOS 26.5 arm64 with CPython 3.13.7 and Tk 8.6 on 2026-09-04.
This is the first component milestone; image conversion, animation and other
optional enhancements are not implemented.

## Executed checks

- Seven real-Tk component tests pass. Combined with the companion PyDeskTools
  integration suite, 38 tests pass in 73.67 seconds.
- Import creates no default root. Explicit parents, embedded frames/toplevels,
  external variables, independent themes, native keyboard invocation, form
  validation, item selection, progress cancellation, dialog lifetime and
  scheduler destruction are exercised by `tests/test_widgets.py`.
- Search traces and scheduled callbacks are removed on destruction. External
  variables remain usable. Invalid theme updates are rejected before mutation.
- The gallery and repository Skill fixtures use the 0.1 API. The Skill validator
  passes. The old drawing demonstration has been migrated to `Button`.
- Ruff and mypy pass; Sphinx builds with warnings treated as errors. Wheel and
  sdist metadata pass Twine validation. An isolated wheel installation outside
  the repository imports successfully and declares zero core runtime dependencies.

## Adversarial findings resolved

1. A public `size` attribute shadowed Tk's geometry method. Button now stores its
   semantic size privately; geometry and keyboard tests pass.
2. Theme styles could leak between component groups. Unique style scopes and
   interpreter ownership are tested with two themes in one interpreter.
3. Deferred search/progress callbacks could outlive widgets. Owned scheduling,
   trace removal and idempotent cleanup are exercised after destruction.
4. Dialog dismissal could leave stale focus/grab state. Completion and direct
   destruction both release owned resources.
5. Prototype imports could hide migration mistakes. Compatibility aliases were
   removed; examples and Skill fixtures import only the public 0.1 API.

## Measurement and limits

One local source-process sample: creating 100 buttons took 1.87 ms; assigning
1,000 list items took 2.70 ms; the slowest of ten theme switches took 0.16 ms.
These are samples, not performance guarantees.

CI is configured but has not been executed remotely. Windows, Linux, Intel Macs,
older macOS releases, a comprehensive scaling matrix and VoiceOver accessibility
have not been certified. Native Tk controls did not expose a complete control
tree in the desktop automation inspection, so no accessibility pass is claimed.
