"""No-command target placeholders for cloud runtimes not yet implemented."""

from __future__ import annotations

from dataclasses import dataclass

from folium_runtime.models import DownRequest, RuntimeResult, StartRequest


@dataclass(frozen=True)
class UnimplementedTarget:
    name: str

    def _result(self) -> RuntimeResult:
        return RuntimeResult(
            exit_code=2,
            notices=(f"Target '{self.name}' is configuration-only and has no runtime lifecycle implementation.",),
            errors=("No cloud, infrastructure, or lifecycle command was executed.",),
        )

    def status(self) -> RuntimeResult:
        return self._result()

    def start(self, request: StartRequest) -> RuntimeResult:
        return self._result()

    def down(self, request: DownRequest) -> RuntimeResult:
        return self._result()