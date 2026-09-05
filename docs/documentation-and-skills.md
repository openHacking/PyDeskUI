# Documentation and Agent Skill specification

> Revised design: 2026-09-04; source audit: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

## Documentation system

Adopt Sphinx with MyST Markdown and autodoc when the public API is implemented. Tooling belongs to the docs dependency group, never the runtime requirements. Publish versioned static documentation from tagged releases using GitHub Pages. This delivery supplies design Markdown only; it does not add a working Sphinx build or publish a website.

Organize future user docs by tutorials (first window, embedding), how-to guides (theme, resources, tasks), API reference (every public export) and explanations (lifetime, threading, architecture). Keep migration guides and an explicit support matrix available from each version's landing page.

Every public object documents its signature, parameters/defaults, return values, exceptions, thread/lifetime constraints, keyboard behavior, minimal example and version introduced. Examples must execute against the matching release in CI. API reference generation must not import modules with GUI side effects. Design docs remain separate from released API docs and retain their status labels.

## Agent Skill artifact

The target artifact is `skills/pydeskui/SKILL.md` with compact references and tested examples. It is a repository-distributed instruction package for coding agents, not a runtime application plugin, a cloud API or an automatic installation into a user's agent environment. This document specifies it; no installable Skill is published before the API exists.

The Skill must include:

- YAML frontmatter with stable name `pydeskui` and a precise description: use for integrating or modifying PyDeskUI-based tkinter interfaces.
- A compatibility table tying Skill release to PyDeskUI API versions, and instructions to inspect the installed version before selecting examples.
- A short workflow: identify parent/event-loop ownership; choose the smallest component; check public signatures; implement; validate keyboard/lifetime behavior.
- References to the same version's API and examples, using packaged relative resources so the Skill is usable offline.
- Troubleshooting for missing Tk, invalid master, optional dependencies, callback signatures and main-thread work.
- Instructions to read project-local rules and preserve the consumer's architecture. Never run installers, network calls or create roots as a hidden side effect of consulting the Skill.

## Positive and negative examples

| Task | Correct guidance | Failure to prevent |
|---|---|---|
| Add a search field to a frame | Require caller's master and a normal on_change callback | Create an extra Tk root or nested mainloop |
| Add an icon | Prefer a prepared PNG; opt into SVG deliberately | Add lxml/Pillow/tksvg to every installation |
| Load large data | Application queue/executor; update on GUI thread | Call widgets from the worker thread |
| Build plugin manager | Compose PyDeskUI primitives in the application | Add plugin installation logic to the UI library |
| Use unavailable API | Report the version mismatch and point to migration | Invent a method because a design document mentions it |

## Skill acceptance

A future Skill release passes five fixture tasks: a standalone window, embedded panel, shared StringVar, cancellable progress panel and optional-image fallback. Validate code against the release, inspect that the artifact contains no credentials or private sibling-repository links, and verify every reference exists in the artifact. Add a sixth future fixture for image preview/selection once implemented, checking original-pixel coordinates and no capture/clipboard business logic in the library. A documentation version bump alone must not advertise new widget functionality.

## Maintenance

API changes update type hints, reference text, examples and Skill fixtures together. A maintainer owns final terminology and translation consistency. Generated reference pages do not replace hand-authored behavior contracts. Stale references are a release failure, not an issue deferred until after publishing.
