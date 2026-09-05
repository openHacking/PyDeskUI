"""Install a built wheel in a clean environment outside the checkout."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    wheels = sorted((Path(__file__).parents[1] / "dist").glob("*.whl"))
    if not wheels:
        raise SystemExit("Build a wheel first")
    with tempfile.TemporaryDirectory(prefix="pydeskui-wheel-") as directory:
        directory = Path(directory)
        venv = directory / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheels[-1])],
            check=True,
        )
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        code = (
            "import tkinter as tk; import pydeskui as ui; "
            "from importlib.resources import files; "
            "assert tk._default_root is None; "
            "assert all(hasattr(ui,n) for n in ui.__all__); "
            "assert files('pydeskui').joinpath('assets/icons/check.svg').is_file(); "
            "print('Installed wheel: exports, bundled icons, import isolation passed')"
        )
        subprocess.run([str(python), "-c", code], cwd=directory, env=environment, check=True)


if __name__ == "__main__":
    main()
