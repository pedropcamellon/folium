"""Available runtime target adapters."""

from folium_runtime.targets.base import RuntimeTarget
from folium_runtime.targets.local import LocalComposeTarget
from folium_runtime.targets.stub import UnimplementedTarget


def registry() -> dict[str, RuntimeTarget]:
    return {
        "local": LocalComposeTarget(),
        "azure": UnimplementedTarget("azure"),
        "aws": UnimplementedTarget("aws"),
    }