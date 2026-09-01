import subprocess

import pytest
from folium_runtime import cli
from folium_runtime.models import RuntimeResult, StartRequest
from folium_runtime.picker import ServiceSelection
from folium_runtime.targets import local, registry


def test_folium_runs_picker_selection_on_local_target(monkeypatch) -> None:
    requests: list[StartRequest] = []

    class LocalTarget:
        def start(self, request: StartRequest) -> RuntimeResult:
            requests.append(request)
            return RuntimeResult()

    monkeypatch.setattr(cli.sys, "argv", ["folium"])
    monkeypatch.setattr(cli.ui, "banner", lambda: None)
    monkeypatch.setattr(cli, "service_states", lambda: {"frontend": "running"})
    picker_states: list[dict[str, str]] = []

    def select_services(states: dict[str, str]) -> ServiceSelection:
        picker_states.append(states)
        return ServiceSelection(["frontend"], [], [])

    monkeypatch.setattr(cli.picker, "select_services", select_services)
    monkeypatch.setattr(cli, "registry", lambda: {"local": LocalTarget()})

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 0
    assert picker_states == [{"frontend": "running"}]
    assert requests == [StartRequest(services=("frontend",), tail_logs=True)]


def test_local_target_runs_selected_services(monkeypatch) -> None:
    commands: list[tuple[list[str], bool]] = []

    def fake_run(
        command: list[str], *, check: bool = False, stream: bool = False
    ) -> subprocess.CompletedProcess[str]:
        commands.append((command, stream))
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(local, "docker_preflight", list)
    monkeypatch.setattr(local, "model_ready", lambda artifact: True)
    monkeypatch.setattr(local, "print_endpoints", lambda: None)
    monkeypatch.setattr(local, "run", fake_run)

    result = registry()["local"].start(
        StartRequest(services=("frontend",), tail_logs=True)
    )

    assert result.succeeded
    assert commands == [
        (["docker", "compose", "ps", "--status", "running", "--services"], False),
        (["docker", "compose", "up", "--detach", "frontend"], True),
        (["docker", "compose", "logs", "--follow", "--tail", "100", "frontend"], True),
    ]


def test_local_target_attaches_to_selected_running_services(monkeypatch) -> None:
    commands: list[tuple[list[str], bool]] = []

    def fake_run(
        command: list[str], *, check: bool = False, stream: bool = False
    ) -> subprocess.CompletedProcess[str]:
        commands.append((command, stream))
        return subprocess.CompletedProcess(command, 0, stdout="frontend\n")

    monkeypatch.setattr(local, "docker_preflight", list)
    monkeypatch.setattr(local, "model_ready", lambda artifact: True)
    monkeypatch.setattr(local, "print_endpoints", lambda: None)
    monkeypatch.setattr(local, "run", fake_run)

    result = registry()["local"].start(
        StartRequest(services=("frontend",), tail_logs=True)
    )

    assert result.succeeded
    assert commands == [
        (["docker", "compose", "ps", "--status", "running", "--services"], False),
        (["docker", "compose", "logs", "--follow", "--tail", "100", "frontend"], True),
    ]


def test_registry_selects_the_local_target() -> None:
    assert registry()["local"].name == "local"


@pytest.mark.parametrize("target_name", ["azure", "aws"])
def test_cloud_targets_do_not_execute_lifecycle_commands(target_name: str) -> None:
    result = registry()[target_name].start(StartRequest())

    assert result.exit_code == 2
    assert result.errors == (
        "No cloud, infrastructure, or lifecycle command was executed.",
    )
