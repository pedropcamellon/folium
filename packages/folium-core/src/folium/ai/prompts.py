"""Prompt asset loading primitives."""

from pathlib import Path


def load_prompt(path: Path) -> str:
    """Load a versioned Markdown prompt asset."""
    return path.read_text(encoding="utf-8").strip()