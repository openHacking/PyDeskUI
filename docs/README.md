# PyDeskUI design documentation

> Revised design: 2026-09-04; source audit: 2026-09-03 · Source revision: `e8e28e8` · Target design, not implemented behavior.

PyDeskUI will be an embeddable, lightweight tkinter/ttk component library for independent Python applications. These documents describe the replacement for the current prototype. They do not assert that the proposed API exists in version 0.0.1.

## Reading order

1. [Current implementation audit](audit.md): evidence, dependency decisions and verification limits.
2. [Architecture and ownership](architecture.md): modules, component selection and integration boundaries.
3. [Proposed public API](api.md): widget, theme, resource and lifetime contracts.
4. [Integration guide](integration.md): standalone and embedded application examples.
5. [Themes, internationalization and accessibility](internationalization.md).
6. [Documentation and Agent Skill specification](documentation-and-skills.md).
7. [Engineering and release policy](engineering.md).
8. [Migration, acceptance and review](roadmap.md).
9. [ADR 0001: lightweight native core](adr/0001-lightweight-native-core.md).

## Status and authority

The project owner accepted the direction on 2026-09-03. Interfaces are proposed and require implementation and conformance tests before release. `api.md` owns the public UI contract; `architecture.md` owns component boundaries. Changes to either require updating consumers and examples in the same change set.

English is the documentation source language. Built-in user-facing strings will support English and Simplified Chinese. PyDeskUI does not depend on PyDeskTools, a plugin host, a network service or an account.

Related public project: [PyDeskTools](https://github.com/openHacking/PyDeskTools). Its SDK, plugin protocol and business views belong to that project. Each repository must remain independently cloneable and releasable; local sibling checkouts are only a development convenience.

## Evidence convention

**Observed** means source inspection or a command executed against the recorded revision. **Proposed** means a decision in this design. **Unverified** means a required future runtime check. Source links use repository-relative paths; external references carry the access date 2026-09-03. No product code was changed during this documentation delivery.
