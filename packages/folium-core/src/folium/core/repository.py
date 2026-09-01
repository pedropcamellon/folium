"""Repository-level primitives shared by Folium development tools."""

from __future__ import annotations

from pathlib import Path

ROOT_MARKERS = ("pyproject.toml", "docker-compose.yml")
PROJECT_DIRECTORY_NAME = "folium"


def find_repository_root(start: Path) -> Path:
    """Find the Folium repository root containing all required marker files."""
    candidate = start.resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if directory.name.casefold() == PROJECT_DIRECTORY_NAME and all(
            (directory / marker).is_file() for marker in ROOT_MARKERS
        ):
            return directory
    marker_list = ", ".join(ROOT_MARKERS)
    raise FileNotFoundError(
        f"Could not find a Folium repository root above {start}; expected directory name "
        f"'{PROJECT_DIRECTORY_NAME}' with: {marker_list}."
    )
