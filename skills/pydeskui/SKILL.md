---
name: pydeskui
description: Integrate or modify PyDeskUI-based tkinter interfaces using explicit parent, scoped theme and widget lifetime contracts.
---

Read project-local rules and inspect `importlib.metadata.version("pydeskui")`
before choosing an example. This skill targets PyDeskUI **0.2.x**; prototype
0.0.1 names are incompatible. For other minor versions inspect their reference.

The application owns Tk(), mainloop(), business state, executors and translations.
When embedding, require the caller's parent and return the panel; do not create
another root. Use Toplevel for additional windows. All widget operations occur
on the Tk thread. Worker results reach it through an application-owned queue.

Use the smallest primitive matching the scenario. Read [reference](reference.md)
for supported signatures and [examples](examples.py) for standalone, embedding,
shared variables, cancellable progress and native-image fallback fixtures.
Never infer released functionality from an architectural proposal. Image selection
widgets require Python 3.13+ linked to Tk 9. SVG icons and resource loading are
part of the core runtime.

Use explicit masters for variables/images; retain displayed images. Themes cannot
cross interpreters. Destroy owners to cancel scheduling, and close a theme only
after its widgets. Preserve externally supplied variables during cleanup.
Plugin installation, schema execution and domain-specific controls stay outside
PyDeskUI. Add business views by composition.

If `_tkinter`, Tk 9 or a display is absent, report the environment requirement; do not
silently install packages or start a root. Consulting this skill has no network,
installer or GUI side effects. Verify keyboard behavior and destruction with
pending callbacks against the installed API before completing an integration.


For professional desktop composition, use the 38 components listed in the
reference, including structure/data views, additional native inputs and owned
overlays. Import public names from `pydeskui` or `pydeskui.widgets`; inspect the
installed exports when working across revisions. Item and FieldSpec are data
helpers, not widgets. Do not infer complete gallery coverage from the API list.

Pass an explicit shared Theme to each component that needs it. Theme uses
underscore token keys; `radius` is 0–12 (default 6), `density` is
compact/default/comfortable, and `font_size` is 9–40 (default 13).
`configure(tokens=mapping)` replaces overrides; `{}` clears them and `None`
retains them. `accent=None` clears branding. `export()` returns a Python dict of
appearance settings, without master or translator. Card currently has its own
fixed radius of 10. Do not modify global Tk scaling or the host ttk theme to
apply PyDeskUI appearance.

Preserve native callback signatures: Checkbox/Switch/RadioGroup/Spinbox commands
take no arguments, Slider receives a numeric string, and Combobox/Select use
`<<ComboboxSelected>>` for user commitment. Do not invent a universal on_change
API. Table's `on_sort(column, direction)` requests application-owned row ordering.
Use `.content` for ScrollArea, Popover and Sheet children. Show/hide overlays;
do not pack/grid Sheet itself. Keep existing Dialog's one-shot result callback.

Zero third-party runtime dependencies remain a requirement. Describe actual
bindings and state behavior without claiming verified accessibility, full
platform coverage or identical appearance. Skeleton is static and Switch uses
native checkbutton interaction. Validate the installed application behavior;
report only checks actually performed.
