"""Typed requests and results for runtime target operations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StartRequest:
    services: tuple[str, ...] = ()
    build_services: frozenset[str] = frozenset()
    recreate_services: frozenset[str] = frozenset()
    download_model: bool = False
    tail_logs: bool = False


@dataclass(frozen=True)
class DownRequest:
    volumes: bool = False


@dataclass(frozen=True)
class RuntimeResult:
    exit_code: int = 0
    notices: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    endpoints: tuple[tuple[str, str], ...] = ()
    services: tuple[tuple[str, str], ...] = ()

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0