# Third-party notices and provenance

New 0.1 modules are original project implementation under MIT. The core wheel
contains no third-party runtime Python distribution. tkinter and Tcl/Tk are supplied
by the consumer's Python distribution and retain their licenses.

The packaged line icons are selected from the Lucide icon library because its
2px outline geometry matches PyDeskUI's desktop visual language. Lucide Icons and
Contributors copyright 2026; distributed under the ISC License. Upstream source and
license: https://github.com/lucide-icons/lucide

Historical `demo/` artwork is excluded from the wheel. Its historical origin is
recorded in the audit; retaining it in source does not assert new rights clearance.
Removed tutorial/Stack Overflow-derived prototype implementations are not shipped
in the replacement runtime.

Build/documentation/test dependencies retain upstream licenses and are not runtime
requirements. Record their resolved versions in `requirements-dev.lock`.
