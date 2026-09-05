"""Compile maintained gettext source catalogs (requires Babel, docs-only tooling)."""

from pathlib import Path

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

root = Path(__file__).resolve().parents[1]
for source in (root / "locales").glob("*/LC_MESSAGES/*.po"):
    destination = (
        root / "src/pydeskui/locales" / source.relative_to(root / "locales").with_suffix(".mo")
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as stream:
        catalog = read_po(stream)
    with destination.open("wb") as stream:
        write_mo(stream, catalog)
