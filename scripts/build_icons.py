"""Rebuild bundled SVG icons. Standard library only; no GUI is opened."""

from pathlib import Path

PATHS = {
    "plus": ((3, 12, 21, 12), (12, 3, 12, 21)),
    "minus": ((3, 12, 21, 12),),
    "check": ((4, 12, 9, 17, 20, 6),),
    "x": ((5, 5, 19, 19), (5, 19, 19, 5)),
    "menu": ((3, 5, 21, 5), (3, 12, 21, 12), (3, 19, 21, 19)),
    "chevron-left": ((15, 5, 8, 12, 15, 19),),
    "chevron-right": ((9, 5, 16, 12, 9, 19),),
    "chevron-up": ((5, 15, 12, 8, 19, 15),),
    "chevron-down": ((5, 9, 12, 16, 19, 9),),
    "search": ((15, 15, 21, 21),),
}


def icon_svg(name, paths):
    geometry = []
    if name == "search":
        geometry.append('<circle cx="10" cy="10" r="7"/>')
    for path in paths:
        points = " ".join(f"{path[i]},{path[i + 1]}" for i in range(0, len(path), 2))
        geometry.append(f'<polyline points="{points}"/>')
    shapes = "".join(geometry)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="#000001" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{shapes}</svg>\n'
    )


def main():
    destination = Path(__file__).parents[1] / "src/pydeskui/assets/icons"
    destination.mkdir(parents=True, exist_ok=True)
    for old in destination.glob("*.png"):
        old.unlink()
    for name, paths in PATHS.items():
        (destination / f"{name}.svg").write_text(icon_svg(name, paths), encoding="utf-8")


if __name__ == "__main__":
    main()
