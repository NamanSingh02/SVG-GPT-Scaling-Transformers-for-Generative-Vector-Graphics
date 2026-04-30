#!/usr/bin/env python3
"""

Fixes GitHub "Invalid Notebook" rendering error caused by broken widget metadata:

    the 'state' key is missing from 'metadata.widgets'

How to use:
1. Change NOTEBOOK_PATH below to the full address/path of your notebook.
2. Run:

       python fix_notebook_widgets.py

Example NOTEBOOK_PATH on Mac:
    "/Users/naman/Projects/svg_gpt_scaling/notebooks/part1_svg_gpt_scaling.ipynb"

Important:
    This script does NOT create a backup.
    It directly modifies the notebook file.
"""

import sys
from pathlib import Path

try:
    import nbformat
except ImportError:
    print("Error: nbformat is not installed.")
    print("Install it with:")
    print("python -m pip install nbformat")
    sys.exit(1)


# -------------------------------------------------------------------
# EDIT THIS LINE ONLY
# Put the full address/path of your notebook here.
# -------------------------------------------------------------------
NOTEBOOK_PATH = "/Users/naman/path/to/YOUR_NOTEBOOK_NAME.ipynb"
# -------------------------------------------------------------------


def fix_notebook(notebook_path: Path) -> None:
    if not notebook_path.exists():
        raise FileNotFoundError(
            f"Notebook file not found:\n{notebook_path}\n\n"
            "Please edit NOTEBOOK_PATH in this script and put the correct notebook address."
        )

    if notebook_path.suffix != ".ipynb":
        raise ValueError("The file must be a .ipynb notebook file.")

    nb = nbformat.read(notebook_path, as_version=4)

    if "widgets" in nb.metadata:
        del nb.metadata["widgets"]
        print("Removed metadata.widgets")
    else:
        print("No metadata.widgets found. Nothing to remove.")

    nbformat.write(nb, notebook_path)
    print(f"Fixed notebook saved directly without backup: {notebook_path}")


def main() -> None:
    notebook_path = Path(NOTEBOOK_PATH).expanduser().resolve()

    try:
        fix_notebook(notebook_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
