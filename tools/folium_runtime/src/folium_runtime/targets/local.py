"""Safe, local-only lifecycle commands for the documented Folium Compose stack."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import tomllib

from folium_runtime import picker, ui
from folium_runtime.models import DownRequest, RuntimeResult, StartRequest

ROOT = Path(__file__).resolve().parents[5]
COMPOSE_COMMAND = ["docker", "compose"]
TARGETS = ("local", "azure", "aws")
LOCAL_ENDPOINTS = (
    ("Frontend", "http://localhost:3000"),
    ("Backend API", "http://localhost:8000"),
    ("Backend health", "http://localhost:8000/health"),
    ("Backend API docs", "http://localhost:8000/docs"),
    ("Summarization health", "http://localhost:8002/health"),
    ("Temporal UI", "http://localhost:8233"),
    ("MinIO console", "http://localhost:9001"),
    ("Grafana", "http://localhost:3002"),
)
REQUIRED_ENV_PATTERN = re.compile(r"\$\{([A-Z][A-Z0-9_]*):\?[^}]*\}")
STORAGE_ACCOUNT_PATTERN = re.compile(r"^[a-z0-9]{3,24}$")


@dataclass(frozen=True)
class ModelArtifact:
    name: str
    url: str
    sha256: str
    size_bytes: int
    destination: Path

    @property
    def configured(self) -> bool:
        return bool(self.url and self.sha256 and self.size_bytes > 0)


def run(command: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=check)


def required_environment_variables(compose_files: list[Path]) -> set[str]:
    required: set[str] = set()
    for compose_file in compose_files:
        required.update(REQUIRED_ENV_PATTERN.findall(compose_file.read_text()))
    return required


def environment_file_variables(environment_file: Path) -> set[str]:
    if not environment_file.is_file():
        return set()
    return {
        line.split("=", maxsplit=1)[0].strip()
        for line in environment_file.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }


def missing_environment_variables(compose_files: list[Path]) -> list[str]:
    configured_names = set(os.environ) | environment_file_variables(ROOT / ".env")
    return sorted(name for name in required_environment_variables(compose_files) if name not in configured_names)


def compose_files() -> list[Path]:
    return [
        ROOT / "backend/docker-compose.yml",
        ROOT / "services/temporal/docker-compose.infra.yml",
    ]


def load_artifact() -> ModelArtifact:
    manifest_path = Path(__file__).parents[1] / "model-artifact.toml"
    contents = tomllib.loads(manifest_path.read_text())
    artifact = contents["artifact"]
    return ModelArtifact(
        name=str(artifact["name"]),
        url=str(artifact["url"]),
        sha256=str(artifact["sha256"]),
        size_bytes=int(artifact["size_bytes"]),
        destination=ROOT / str(artifact["destination"]),
    )


def docker_preflight() -> list[str]:
    problems: list[str] = []
    if shutil.which("docker") is None:
        return ["Docker is not installed. Install Docker Desktop, then rerun this command."]
    daemon = run(["docker", "info"])
    if daemon.returncode:
        return ["Docker is installed but the daemon is unavailable. Start Docker Desktop, then rerun this command."]
    missing = missing_environment_variables(compose_files())
    if missing:
        problems.append(f"Missing required environment variables: {', '.join(missing)}. Set them in root .env.")
    config = run([*COMPOSE_COMMAND, "config", "-q"])
    if config.returncode:
        problems.append("Docker Compose configuration is invalid. Run `docker compose config -q` for details.")
    return problems


def describe_model(artifact: ModelArtifact) -> str:
    if not artifact.configured:
        return (
            f"No verified model artifact is configured. Expected model path: {artifact.destination}. "
            "Set the URL, SHA-256, and size in tools/folium_runtime/src/folium_runtime/model-artifact.toml before using --download-model."
        )
    return f"Model path: {artifact.destination} ({artifact.size_bytes / 1_000_000_000:.2f} GB)."


def model_ready(artifact: ModelArtifact) -> bool:
    return artifact.destination.is_file() and artifact.destination.stat().st_size == artifact.size_bytes


def download_model(artifact: ModelArtifact) -> int:
    if not artifact.configured:
        print(describe_model(artifact), file=sys.stderr)
        return 2
    free_bytes = shutil.disk_usage(artifact.destination.parent).free
    if free_bytes < artifact.size_bytes:
        print(f"Insufficient disk space for {artifact.size_bytes} bytes at {artifact.destination.parent}.", file=sys.stderr)
        return 2
    artifact.destination.parent.mkdir(parents=True, exist_ok=True)
    partial = artifact.destination.with_suffix(f"{artifact.destination.suffix}.part")
    existing_bytes = partial.stat().st_size if partial.exists() else 0
    request = urllib.request.Request(artifact.url, headers={"Range": f"bytes={existing_bytes}-"} if existing_bytes else {})
    try:
        with urllib.request.urlopen(request) as response, partial.open("ab" if existing_bytes else "wb") as output:
            shutil.copyfileobj(response, output)
    except OSError as error:
        print(f"Model download failed: {error}", file=sys.stderr)
        return 1
    with partial.open("rb") as downloaded_file:
        digest = hashlib.file_digest(downloaded_file, "sha256").hexdigest()
    if partial.stat().st_size != artifact.size_bytes or digest != artifact.sha256:
        print("Downloaded model failed size or SHA-256 verification; retaining partial file for a resumable retry.", file=sys.stderr)
        return 1
    partial.replace(artifact.destination)
    print(f"Verified model downloaded to {artifact.destination}.")
    return 0


def print_endpoints() -> None:
    ui.endpoints(LOCAL_ENDPOINTS)


def status() -> int:
    artifact = load_artifact()
    problems = docker_preflight()
    for problem in problems:
        ui.error(problem)
    ui.notice("Model ready." if model_ready(artifact) else describe_model(artifact))
    if shutil.which("docker"):
        services = run([*COMPOSE_COMMAND, "ps", "--format", "{{.Service}}\t{{.State}}"])
        if services.returncode == 0:
            ui.services(services.stdout)
    return 1 if problems else 0


def start(
    target: str,
    rebuild: bool,
    recreate: bool,
    download: bool,
    services: list[str] | None = None,
    build_services: list[str] | None = None,
    recreate_services: list[str] | None = None,
) -> int:
    if target != "local":
        ui.notice(f"Target '{target}' only selects configuration guidance; it will not deploy cloud infrastructure.")
    problems = docker_preflight()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    artifact = load_artifact()
    if not model_ready(artifact):
        if download:
            result = download_model(artifact)
            if result:
                return result
        elif os.environ.get("SUMMARIZATION_PROVIDER", "local") == "local":
            print(f"{describe_model(artifact)}\nNext command: uv run folium start --download-model", file=sys.stderr)
            return 2
        else:
            ui.notice("Local model is unavailable; starting the configured non-local summarization provider.")
    selected_services = services or []
    build_targets = selected_services if rebuild else build_services or []
    recreate_targets = selected_services if recreate else recreate_services or []
    if build_targets:
        result = run([*COMPOSE_COMMAND, "build", *build_targets])
        if result.returncode:
            print(result.stderr, file=sys.stderr)
            return result.returncode
    regular_targets = [service for service in selected_services if service not in recreate_targets]
    commands = []
    if regular_targets or not selected_services:
        commands.append([*COMPOSE_COMMAND, "up", "--detach", *regular_targets])
    if recreate_targets:
        commands.append([*COMPOSE_COMMAND, "up", "--detach", "--force-recreate", *recreate_targets])
    for command in commands:
        result = run(command)
        if result.returncode:
            print(result.stderr, file=sys.stderr)
            return result.returncode
    print_endpoints()
    return 0


def down(volumes: bool) -> int:
    command = [*COMPOSE_COMMAND, "down"]
    if volumes:
        command.append("--volumes")
    result = run(command)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def bootstrap_state(args: argparse.Namespace) -> int:
    if args.target != "azure":
        print("bootstrap-state supports only --target azure.", file=sys.stderr)
        return 2
    if not args.confirm:
        print("Refusing cloud mutation. Rerun with --confirm after reviewing the resource-group, account, and container names.", file=sys.stderr)
        return 2
    if not STORAGE_ACCOUNT_PATTERN.fullmatch(args.storage_account):
        print("Storage account names must contain 3-24 lowercase letters or digits.", file=sys.stderr)
        return 2
    account = run(["az", "account", "show", "--query", "id", "--output", "tsv"])
    if account.returncode or not account.stdout.strip():
        print("Azure CLI has no active subscription. Run `az login` and `az account set --subscription <id>`.", file=sys.stderr)
        return 2
    group = run(["az", "group", "show", "--name", args.resource_group])
    tags = "managed-by=folium-runtime-runner"
    if group.returncode:
        commands = [
            ["az", "group", "create", "--name", args.resource_group, "--location", args.location, "--tags", tags],
            ["az", "storage", "account", "create", "--name", args.storage_account, "--resource-group", args.resource_group, "--location", args.location, "--sku", "Standard_LRS", "--tags", tags],
        ]
    else:
        ownership = run(["az", "group", "show", "--name", args.resource_group, "--query", "tags.managed-by", "--output", "tsv"])
        if ownership.stdout.strip() != "folium-runtime-runner":
            print("Existing resource group is not managed by Folium; refusing to mutate it.", file=sys.stderr)
            return 2
        storage_ownership = run(["az", "storage", "account", "show", "--name", args.storage_account, "--resource-group", args.resource_group, "--query", "tags.managed-by", "--output", "tsv"])
        if storage_ownership.returncode or storage_ownership.stdout.strip() != "folium-runtime-runner":
            print("Existing storage account is not managed by Folium; refusing to mutate it.", file=sys.stderr)
            return 2
        commands = []
    for command in commands:
        result = run(command)
        if result.returncode:
            print(result.stderr, file=sys.stderr)
            return result.returncode
    container = run(["az", "storage", "container", "create", "--name", args.container, "--account-name", args.storage_account, "--auth-mode", "login", "--public-access", "off"])
    if container.returncode:
        print(container.stderr, file=sys.stderr)
        return container.returncode
    print(f'resource_group_name = "{args.resource_group}"\nstorage_account_name = "{args.storage_account}"\ncontainer_name = "{args.container}"\nkey = "folium.tfstate"')
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run and inspect Folium's local Docker Compose runtime.")
    subcommands = result.add_subparsers(dest="command")
    start_parser = subcommands.add_parser("start", help="Start the documented local stack.")
    start_parser.add_argument("--target", choices=TARGETS, default="local")
    start_parser.add_argument("--rebuild", action="store_true")
    start_parser.add_argument("--recreate", action="store_true")
    start_parser.add_argument("--download-model", action="store_true")
    subcommands.add_parser("status", help="Report runtime state without changing it.")
    down_parser = subcommands.add_parser("down", help="Stop Folium Compose services without removing volumes.")
    down_parser.add_argument("--volumes", action="store_true", help="Also remove Compose volumes and their data.")
    bootstrap_parser = subcommands.add_parser("bootstrap-state", help="Create Azure Terraform state storage only.")
    bootstrap_parser.add_argument("--target", required=True, choices=TARGETS)
    bootstrap_parser.add_argument("--confirm", action="store_true")
    bootstrap_parser.add_argument("--resource-group", default="rg-folium-tfstate")
    bootstrap_parser.add_argument("--storage-account", required=True)
    bootstrap_parser.add_argument("--container", default="tfstate")
    bootstrap_parser.add_argument("--location", default="eastus")
    return result


def main() -> None:
    arguments = sys.argv[1:]
    if arguments and arguments[0] == "--download-model":
        arguments = ["start", "--download-model", *arguments[1:]]
    if not arguments:
        ui.banner()
        selection = picker.select_services()
        if selection is None:
            ui.notice("Cancelled.")
            return
        if not selection.services:
            ui.notice("No services selected.")
            return
        raise SystemExit(start("local", False, False, False, selection.services, selection.build, selection.recreate))
    args = parser().parse_args(arguments)
    if args.command != "bootstrap-state" or args.confirm:
        ui.banner()
    if args.command == "status":
        code = status()
    elif args.command == "down":
        code = down(args.volumes)
    elif args.command == "bootstrap-state":
        code = bootstrap_state(args)
    else:
        code = start(args.target, args.rebuild, args.recreate, args.download_model)
    raise SystemExit(code)


class LocalComposeTarget:
    """Docker Compose-backed local runtime target."""

    name = "local"

    def status(self) -> RuntimeResult:
        return RuntimeResult(exit_code=status())

    def start(self, request: StartRequest) -> RuntimeResult:
        return RuntimeResult(
            exit_code=start(
                "local",
                bool(request.services and request.build_services == frozenset(request.services)),
                bool(request.services and request.recreate_services == frozenset(request.services)),
                request.download_model,
                list(request.services),
                list(request.build_services),
                list(request.recreate_services),
            )
        )

    def down(self, request: DownRequest) -> RuntimeResult:
        return RuntimeResult(exit_code=down(request.volumes))