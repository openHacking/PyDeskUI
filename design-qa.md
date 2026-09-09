# Design QA — shadcn-inspired collection components

## Visual truth and capture conditions

- Source Tabs: `/var/folders/t4/5jpgr2kj5ygcf_9jq59b0ykm0000gn/T/codex-clipboard-5b920621-7ab8-4374-9f29-b5f8c501c90f.png` (687×517).
- Source dark Tabs/Tree: `/var/folders/t4/5jpgr2kj5ygcf_9jq59b0ykm0000gn/T/codex-clipboard-f2d86f35-74d5-40f7-8f0d-88b804a1828a.png` (886×324).
- Source dark Table: `/var/folders/t4/5jpgr2kj5ygcf_9jq59b0ykm0000gn/T/codex-clipboard-18c0ba11-7c4f-471f-9ba0-8120118696d3.png` (896×381).
- Source Table: `/var/folders/t4/5jpgr2kj5ygcf_9jq59b0ykm0000gn/T/codex-clipboard-b4fc5324-a3c6-462f-b99d-7432f765ca8b.png` (781×629).
- Implementation captures: `/private/tmp/pydeskui-layout-top-final.png`, `/private/tmp/pydeskui-layout-bottom-final.png`, and `/private/tmp/pydeskui-layout-light-final.png` (all 1292×944 physical pixels).
- Comparison canvases: `/private/tmp/pydeskui-tabs-tree-comparison.png` and `/private/tmp/pydeskui-table-comparison.png`.
- Native macOS Gallery, default density, equivalent logical window size and identical Layout page content. Dark and light themes were both captured; the bottom capture uses the same dark window scrolled to the final content boundary.
- State coverage: Overview tab selected, Activity unselected, Workspace expanded, table populated and sortable, outer ScrollArea at top and bottom.

## Comparison history

1. The first implementation pass still inherited an Aqua heading layout that visually ignored the configured padding and left the heading cramped.
2. The heading was rebuilt from portable ttk elements so the configured 8px horizontal padding, density-dependent vertical padding, and left anchor are honored on macOS.
3. Tabs were reduced from the tall native Notebook treatment to a compact muted group with an independent selected surface. Gallery tab bodies were separated by 8px and placed on a Card.
4. The active Gallery page, rather than the tallest previously visited page, now owns the content height. A top-to-bottom capture confirms that the long Layout page can be continuously scrolled through Table and Tree regions.

## Surface review

- Fonts: existing application font family and semantic type scale retained; no accidental fallback or weight change found.
- Spacing: tab group is compact; tab-to-panel gap is 8px; table headings gain at least 8px horizontal padding; Tree disclosure indicator uses a 16px target with 6/8px side margins and 20px hierarchy indentation.
- Colors: muted, card, border, foreground, accent, and ring semantic tokens are used in both themes; no fixed light-only colors were introduced.
- Images/icons: existing built-in chevron and theme tile resources are reused; no runtime asset or dependency was added.
- Copy/content: Gallery labels and data remain unchanged, so the review isolates component behavior and visual hierarchy.
- Interaction: selected, hover, disabled, and keyboard-focus tab states are defined; native Ctrl-Tab and `<<NotebookTabChanged>>` behavior remain intact. Table headings remain caller-overridable.
- Scrolling: native scrollable children consume wheel input while they can move; at a directional boundary the event transfers to the containing ScrollArea. Nested ScrollAreas and value-changing controls remain isolated.

## Adversarial review

- P0: none.
- P1: none.
- P2: none.
- P3: native ttk text metrics keep the tab group slightly taller than the browser reference, and the heading separator is subtler on Aqua than the CSS reference. These are platform-rendering differences, not layout or interaction defects.

## Verification evidence

- Full test suite: 102 passed.
- Ruff: passed.
- mypy: passed.
- Sphinx with warnings as errors: passed.
- `git diff --check`: passed.
- Dark/light full-view and focused side-by-side comparisons: passed.

final result: passed

## Popover boundary pass — 2026-09-09

- Source visual truth: `/var/folders/t4/5jpgr2kj5ygcf_9jq59b0ykm0000gn/T/codex-clipboard-c2cd6064-0983-48c6-ae1b-8d0658c3858b.png` (301 × 307) shows the boundary disappearing on a white application surface; `/var/folders/t4/5jpgr2kj5ygcf_9jq59b0ykm0000gn/T/codex-clipboard-6bffd897-96d6-406b-a390-d53a9de2f31e.png` (519 × 371) establishes the existing DropdownMenu boundary treatment.
- Implementation evidence: `/private/tmp/pydeskui-popover-before.png`, `/private/tmp/pydeskui-popover-after.png`, and `/private/tmp/pydeskui-popover-dark-after.png`, all 640 × 420 physical pixels from the same 640 × 420 native Tk viewport, macOS Aqua, 1:1 capture; both light and dark fixed states were inspected.
- Focused comparison evidence: `/private/tmp/pydesktools-popover-comparison.png`; a full-page comparison was not useful because the requested change is confined to the popup edge and the supplied sources are cropped from different screens.
- Comparison history: the first capture showed square white content visually merging with the white host. Aqua did not apply the ttk frame style padding to child geometry, so the content covered the rounded tile edge. The fix applies DropdownMenu's proven external content inset in the shared attached-popup surface. The second capture shows the rounded one-pixel semantic border and corners continuously around Popover content.
- Fonts and copy: unchanged. Spacing: logical Popover content padding is preserved; the shared three-pixel surface inset only exposes the existing edge. Colors: existing `popover` and `border` tokens are retained in light and dark modes. Assets: no new image, icon, gradient, or dependency was introduced.
- Interaction: the focused overlay suite covers open/toggle, initial focus, outside click, Escape, Return dismissal, menu navigation, viewport clamping, and theme refresh.
- Aqua dismissal: Tk 9.0.4 reproduces upstream ticket `2ef5dd8036` (geometry-manager forget leaves stale pixels). The shared attached-popup path now lowers before an idle unmap and exposes only the vacated host rectangle. `/private/tmp/pydeskui-popover-hide-fixed.png` verifies underlying text repaints without pointer movement. In the full Gallery, 30 close cycles measured 0.258 ms median synchronous work and 6.069 ms median idle paint (0.438 ms and 7.040 ms maxima).
- Findings: no remaining P0, P1, or P2 issue. Cross-platform screenshots remain a P3 follow-up; the geometry regression is backend-independent and automated.

final result: passed
