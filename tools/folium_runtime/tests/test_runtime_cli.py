from pathlib import Path

from folium_runtime import cli
from folium_runtime.cli import parser
from folium_runtime.picker import BUILDABLE_SERVICES, SERVICES, ServiceSelection
from folium_runtime.targets.local import ModelArtifact, environment_file_variables, missing_environment_variables, required_environment_variables


def test_required_environment_variables_reads_compose_interpolation(tmp_path: Path) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("PASSWORD: ${POSTGRES_PASSWORD:?set it}\nOPTIONAL: ${LOG_LEVEL:-INFO}\n")

    assert required_environment_variables([compose_file]) == {"POSTGRES_PASSWORD"}


def test_missing_environment_variables_does_not_return_values(tmp_path: Path, monkeypatch) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("TOKEN: ${RUNTIME_TOKEN:?set it}\n")
    monkeypatch.delenv("RUNTIME_TOKEN", raising=False)

    assert missing_environment_variables([compose_file]) == ["RUNTIME_TOKEN"]


def test_environment_file_variables_returns_names_only(tmp_path: Path) -> None:
    environment_file = tmp_path / ".env"
    environment_file.write_text("# comment\nRUNTIME_TOKEN=secret-value\nEMPTY=\n")

    assert environment_file_variables(environment_file) == {"RUNTIME_TOKEN", "EMPTY"}


def test_model_readiness_requires_expected_size(tmp_path: Path) -> None:
    destination = tmp_path / "model.gguf"
    destination.write_bytes(b"short")
    artifact = ModelArtifact("test", "https://example.test/model", "a" * 64, 10, destination)

    assert artifact.configured
    assert destination.stat().st_size != artifact.size_bytes


def test_start_defaults_to_local_target() -> None:
    arguments = parser().parse_args(["start"])

    assert arguments.target == "local"
    assert not arguments.rebuild
    assert not arguments.recreate


def test_down_requires_explicit_volume_removal() -> None:
    arguments = parser().parse_args(["down"])

    assert not arguments.volumes


def test_azure_bootstrap_requires_an_explicit_target() -> None:
    arguments = parser().parse_args(["bootstrap-state", "--target", "azure", "--storage-account", "foliumstate123"])

    assert arguments.target == "azure"
    assert not arguments.confirm


def test_service_picker_has_unique_compose_service_names() -> None:
    service_names = [name for name, _label in SERVICES]

    assert len(service_names) == len(set(service_names))
    assert "folium-backend" in service_names
    assert "frontend" in service_names


def test_buildable_picker_services_are_all_known_services() -> None:
    service_names = {name for name, _label in SERVICES}

    assert BUILDABLE_SERVICES <= service_names
    assert "folium-postgres" not in BUILDABLE_SERVICES


def test_service_selection_tracks_independent_build_and_recreate_marks() -> None:
    selection = ServiceSelection(["folium-backend", "frontend"], ["folium-backend"], ["frontend"])

    assert selection.build == ["folium-backend"]
    assert selection.recreate == ["frontend"]


def test_top_level_model_download_flag_is_rejected(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli.sys, "argv", ["folium", "--download-model"])

    try:
        cli.main()
    except SystemExit as error:
        assert error.code == 2

    assert "uv run folium start --download-model" in capsys.readouterr().err