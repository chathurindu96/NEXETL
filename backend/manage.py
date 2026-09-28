"""Command-line entry point for NEXETL Django development tasks."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    """Run a Django management command with the local source tree available."""
    source_root = Path(__file__).resolve().parent / "src"
    sys.path.insert(0, str(source_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexetl.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
