# Tk 9 SVG implementation verification

Date: 2026-09-05. Environment: macOS arm64, CPython 3.13.12, Tcl/Tk 9.0.
This report covers the current working tree and retains all pre-existing edits.

## Implemented changes

- Python 3.13+ and Tk 9 runtime gate with a clear unsupported-version error.
- Tk 9 native SVG loading for public resources, bundled icons, rounded controls,
  Switch indicators and choice arrows; packaged icon PNG variants were removed.
- Lightweight Frame, Label and Card surfaces rather than stretchable images over
  large areas.
- Two bounded SVG state buffers so theme preparation does not mutate images that
  are currently displayed.
- ScrollArea Configure coalescing and unchanged-geometry suppression.
- Gallery pages created once, unmapped when inactive, and reused; redundant
  page-wide label restyling was replaced by shared role styles.

## Executed checks

| Check | Observed result |
|---|---|
| Full native test suite | 92 passed in 10.53 seconds |
| Theme construction | 7.91 ms in the recorded benchmark |
| Construct 100 Button instances | 1.20 ms |
| Theme switch, no mapped gallery | 1.16 ms median, 3.49 ms maximum across 20 switches |
| Gallery cached page switch | 65–191 ms across seven pages; mapping and native paint dominate |
| Gallery theme configuration | 8.94 ms before native repaint |
| Ruff / mypy / whitespace | Passed; mypy checked 13 source files |
| Sphinx HTML (`-W`) | Passed |
| Wheel and sdist | Built without package-discovery warnings; Twine passed |
| Clean wheel install | Passed; 0.2.0 exports and packaged SVG icon verified |

The earlier Python raster implementation measured about 398 ms for Theme
construction and 366 ms per theme switch. The functional Gallery traversal that
previously took about 155 seconds now completes in roughly 13 seconds in the
focused test. These measurements are local evidence, not universal platform
guarantees.

## Adversarial findings

1. Python pixel supersampling and PNG encoding blocked the Tk thread; the code and
   `_drawing` module were removed.
2. Stretchable image elements around every Frame and Label caused one Aqua redraw
   to take tens of seconds; high-volume surfaces now use ttk elements.
3. Configure callbacks could repeatedly write identical Canvas geometry;
   ScrollArea now performs at most one queued layout and compares signatures.
4. Updating visible PhotoImages one by one generated repeated invalidations;
   theme state resources now alternate between two fixed buffers.
5. Keeping every Gallery page mapped made theme repaint all pages; inactive pages
   are unmapped while their component state remains alive.

## Explicit limits

- Tk 9 converts SVG input into pixel-backed PhotoImage data. Assets are regenerated
  at the requested size/DPI; Tk does not retain a vector scene.
- Cached Gallery page mapping remains above the 50 ms aspirational target on some
  pages in this environment. Core component creation and theme configuration meet
  their budgets; further Gallery virtualization would trade away live examples.
- Windows and Linux were not executed in this local session. CI rejects runners
  whose Python is not linked to Tk 9; platform certification requires passing jobs.
- Physical Chinese IME sessions, screen readers and mixed-DPI monitor transitions
  were not certified in this run.
