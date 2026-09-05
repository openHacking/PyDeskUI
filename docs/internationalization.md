# Themes, internationalization and accessibility

> Revised design: 2026-09-04; source audit: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

## Language model

Documentation, code identifiers and contributor-facing diagnostics use English. Built-in end-user labels support `en` and `zh_CN` using gettext catalogs in the `pydeskui` domain. Applications decide the locale and pass a translation context. Locale fallback is exact locale, language, then English. Missing translations show the source English message, never a blank label.

Consumer text is already translated by the consumer. The library must not treat arbitrary text as a message key. Use named placeholders and `ngettext` for plural messages; avoid concatenating fragments whose word order varies by language. Locale changes occur on the GUI thread and update library-owned labels without resetting field values or selection.

Language tags exposed by applications can use BCP 47 (for example `zh-CN`); the adapter maps them to gettext catalog names. Do not change the process-wide C locale. Timestamp/number formatting belongs to application services; the UI primitive displays their results.

## Appearance

Offer light/dark themes with named system fonts and semantic tokens. Use ttk semantics first, including disabled, focus, selected, invalid and active states. Do not copy global ttk styles. Background/foreground animation is optional and respects reduced motion. Make focus indicators visible rather than expressing focus with color alone.

Layout uses natural widget sizing and stretch weights, with sensible minimum sizes instead of fixed window dimensions. Test 100%, 150% and 200% scaling, monitor changes where supported, long German-like labels and CJK input. Avoid manually changing global `tk scaling` inside library components.

## Accessibility contract and limitations

Keyboard navigation is a release requirement: Tab/Shift+Tab traversal, Space/Return activation according to widget role, arrow-key selection, Escape dismissal and focus return from dialogs. Do not steal focus during progress updates. Labels identify fields and errors remain visible as text.

Use native dialogs when their platform behavior is preferable. OS screen-reader integration and complex-script shaping vary with Tcl/Tk and platform builds; do not claim universal accessibility compliance from widget choice alone. RTL layouts and screen-reader compatibility remain explicitly unverified until recorded manual tests exist.

## Acceptance matrix

| Area | Required evidence |
|---|---|
| Translation | All built-in visible messages extracted; en/zh_CN catalogs compile; missing-key fallback |
| Text expansion | Pseudolocalized strings at 2x length do not hide controls |
| Input | Chinese IME composition, non-ASCII paste, mixed-direction text and Unicode filenames |
| Keyboard | Every action operable without a mouse; stable focus after dialogs |
| Theme | Light/dark/reduced motion, simultaneous independent contexts, no unrelated ttk changes |
| Scaling | 100/150/200% screen captures and interactive inspection on supported targets |
| Assistive technology | Explicit results for VoiceOver, Narrator and Linux accessibility tooling; unsupported cases documented |

Internationalization tests must include plugin-host compositions in downstream integration tests, while this repository tests primitives independently.
