# Migration, acceptance and adversarial review

> Revised design: 2026-09-04; source audit: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

## Ordered implementation

| Stage | Deliverable | Exit evidence |
|---|---|---|
| UI-0: engineering foundation | Correct package identity and imports, one build configuration, source/wheel tests, provenance inventory | Wheel/sdist install outside checkout; library imports without opening GUI |
| UI-1: embedding contracts | Button, Entry, SearchEntry, Theme, parent and lifetime fixes | Standalone and embedded tests; no implicit roots; keyboard and disabled behavior |
| UI-2: application primitives | ItemList, DetailView, Form, ProgressView, Dialog, ImageView and ImageSelection driven by downstream scenarios | Independent gallery plus PyDeskTools manager/form integration |
| UI-3: international release | en/zh_CN, resources, platform matrix, API docs and Skill | GUI/platform evidence, executable documentation examples, Skill fixture results |
| UI-4: optional enhancements | images/SVG extras only where justified | Core stays dependency-free; adapter-specific platform and memory checks |

PyDeskTools consumes a released compatible UI version at each integration milestone. Editable sibling installs are acceptable for local development, but no absolute path dependency enters distribution metadata.

## Migration map

| Prototype pattern | Replacement |
|---|---|
| `from button import ...` | Imports through installed `pydeskui` public exports |
| DeskButton callback receives Event | Button command takes no argument; use explicit bind for event listeners |
| Entry owns an implicit global variable | Explicit parent and caller-owned StringVar supported |
| Fixed colors/font in each widget | Scoped Theme and named system fonts |
| Unconditional SVG dependency | Native image first, optional adapter on demand |
| Tutorials inside runtime namespace | Guarded examples outside the distribution |

No backward compatibility layer is required for prototype 0.0.1. Document the break and show a before/after example for each public replacement. Do not label the new library production-ready until release gates pass.

## Acceptance scenarios

1. Install core with no third-party runtime dependency; instantiate Button and Entry in a Tk-enabled environment.
2. Place components in a caller's Frame and Toplevel; assert `winfo_parent()` and verify no extra root.
3. Supply two StringVars, change them externally, submit/clear independently and preserve values through theme/locale changes.
4. Enter/leave buttons rapidly; destroy a parent mid-animation; verify no stale Tcl commands or live callbacks.
5. Operate every component by keyboard, test disabled states and return focus after closing dialogs.
6. Run long-list/progress updates while moving/resizing the window; measure GUI-thread responsiveness.
7. Test missing optional dependencies without breaking basic import; retain image lifetime and release resources after destruction.
8. Exercise English, Chinese, long labels, IME and scaling; record unsupported accessibility cases honestly.

## Adversarial review

| Attack on the design | Resolution in this baseline | Required future evidence |
|---|---|---|
| A "lightweight" core still imports a renderer transitively | Optional imports live only in explicit adapters | Inspect wheel dependency graph and import trace |
| Themes mutate a consumer's existing ttk styles | Context-prefixed styles; no bare style writes | Two contexts plus a plain ttk form in the same interpreter |
| Parent is explicit but StringVar/image still chooses default root | Require explicit masters for all Tk resources | Frame/Toplevel tests with default-root behavior disabled |
| Canceled animations still update a destroyed widget | Track owner handles, coalesce and discard stale callbacks | Stress test repeated create/destroy during transitions |
| Agent examples invent future interfaces | Separate design from released docs; version-matched Skill | Execute all released examples and Skill fixtures |

## Revised image acceptance

Verify preview fit/zoom/scroll, correct original-pixel region coordinates after scaling, keyboard adjustment and Escape, repeated image replacement and destruction, two independent Tk containers and no mandatory Pillow import. Test host-normalized large images against documented resource limits. Capture acquisition, compression and clipboard/history tests belong to the consuming application.

## Documentation-delivery evidence

See [verification report](verification.md) for checks executed on the final documentation. Runtime gates above are not reported as completed by this document-only change.
