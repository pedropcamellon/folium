"""Runtime target extension contract."""

from __future__ import annotations

from typing import Protocol

from folium_runtime.models import DownRequest, RuntimeResult, StartRequest


class RuntimeTarget(Protocol):
    name: str

    def status(self) -> RuntimeResult: ...

    def start(self, request: StartRequest) -> RuntimeResult: ...

    def down(self, request: DownRequest) -> RuntimeResult: ...