# Third-party notices and provenance

New 0.1 modules are original project implementation under MIT. The core wheel
contains no third-party runtime Python distribution or copied artwork. tkinter and
Tcl/Tk are supplied by the consumer's Python distribution and retain their licenses.

Historical `demo/` and artwork under `src/pydeskui/assets/` are excluded from the
wheel. Their historical origin is recorded in the audit; retaining them in source
does not assert new rights clearance. Removed tutorial/Stack Overflow-derived
prototype implementations are not shipped in the replacement runtime.

Build/documentation/test dependencies retain upstream licenses and are not runtime
requirements. Record their resolved versions in `requirements-dev.lock`.
