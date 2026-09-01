"""Argument parsing and terminal edge for the Folium runtime tool."""

from __future__ import annotations

import argparse
import sys

from folium_runtime import picker, ui
from folium_runtime.models import DownRequest, RuntimeResult, StartRequest
from folium_runtime.targets import registry
from folium_runtime.targets.local import (
    bootstrap_state as bootstrap_azure_state,
    service_states,
)

TARGETS = ("local", "azure", "aws")


def render(result: RuntimeResult) -> int:
    for notice in result.notices:
        ui.notice(notice)
    for error in result.errors:
        ui.error(error)
    if result.endpoints:
        ui.endpoints(result.endpoints)
    if result.services:
        ui.services("\n".join("\t".join(row) for row in result.services))
    return result.exit_code


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run and inspect Folium runtime targets.")
    commands = result.add_subparsers(dest="command")
    start_command = commands.add_parser("start", help="Start a selected runtime target.")
    start_command.add_argument("--target", choices=TARGETS, default="local")
    start_command.add_argument("--rebuild", action="store_true")
    start_command.add_argument("--recreate", action="store_true")
    start_command.add_argument("--download-model", action="store_true")
    commands.add_parser("status", help="Report target state without changing it.")
    down_command = commands.add_parser("down", help="Stop local Compose services without removing volumes.")
    down_command.add_argument("--target", choices=TARGETS, default="local")
    down_command.add_argument("--volumes", action="store_true")
    bootstrap = commands.add_parser("bootstrap-state", help="Create Azure Terraform state storage only.")
    bootstrap.add_argument("--target", required=True, choices=TARGETS)
    bootstrap.add_argument("--confirm", action="store_true")
    bootstrap.add_argument("--resource-group", default="rg-folium-tfstate")
    bootstrap.add_argument("--storage-account", required=True)
    bootstrap.add_argument("--container", default="tfstate")
    bootstrap.add_argument("--location", default="eastus")
    return result


def main() -> None:
    arguments = sys.argv[1:]
    if arguments and arguments[0] == "--download-model":
        print(
            "Model download is a start action. Use: uv run folium start --download-model",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if not arguments:
        ui.banner()
        selection = picker.select_services(service_states())
        if selection is None:
            ui.notice("Cancelled.")
            return
        request = StartRequest(
            services=tuple(selection.services),
            build_services=frozenset(selection.build),
            recreate_services=frozenset(selection.recreate),
            tail_logs=True,
        )
        raise SystemExit(render(registry()["local"].start(request)))
    args = parser().parse_args(arguments)
    if args.command != "bootstrap-state" or args.confirm:
        ui.banner()
    if args.command == "bootstrap-state":
        raise SystemExit(bootstrap_azure_state(args))
    target = registry()[getattr(args, "target", "local")]
    if args.command == "status":
        raise SystemExit(render(target.status()))
    if args.command == "down":
        raise SystemExit(render(target.down(DownRequest(args.volumes))))
    request = StartRequest(
        build_services=frozenset() if not args.rebuild else frozenset(picker.BUILDABLE_SERVICES),
        recreate_services=frozenset() if not args.recreate else frozenset(picker.SERVICES[index][0] for index in range(len(picker.SERVICES))),
        download_model=args.download_model,
    )
    raise SystemExit(render(target.start(request)))