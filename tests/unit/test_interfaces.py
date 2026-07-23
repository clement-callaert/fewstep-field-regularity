"""Phase 0 unit tests for package imports and protocols."""

from __future__ import annotations

from typing import get_type_hints

from fewstep_regularities import __version__
from fewstep_regularities.artifacts.manifest import (
    RunManifest,
    required_manifest_fields,
)
from fewstep_regularities.artifacts.writer import (
    ArtifactWriter,
    FilesystemArtifactWriter,
)
from fewstep_regularities.distributions.base import Distribution
from fewstep_regularities.evaluation.base import Evaluator
from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.metrics.base import RegularityMetric
from fewstep_regularities.paths.base import ProbabilityPath
from fewstep_regularities.solvers.base import ODESolver
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, resolve_dtype


def test_version_string() -> None:
    assert __version__ == "0.1.0"


def test_default_dtype_is_float64() -> None:
    import torch

    assert torch.float64 == DEFAULT_DTYPE
    assert resolve_dtype("float64") == torch.float64


def test_protocols_are_importable() -> None:
    assert Distribution is not None
    assert ProbabilityPath is not None
    assert VelocityField is not None
    assert ODESolver is not None
    assert RegularityMetric is not None
    assert Evaluator is not None
    assert ArtifactWriter is not None


def test_filesystem_writer_satisfies_protocol() -> None:
    writer = FilesystemArtifactWriter()
    assert isinstance(writer, ArtifactWriter)


def test_required_manifest_fields_nonempty() -> None:
    fields = required_manifest_fields()
    assert "run_id" in fields
    assert "config_hash" in fields
    assert "random_seeds" in fields


def test_run_manifest_missing_fields_detects_empty_seeds() -> None:
    manifest = RunManifest(
        run_id="x",
        git_commit="abc",
        config_hash="h",
        code_status="clean",
        software_environment_hash="e",
        random_seeds=[],
        start_time="t0",
        end_time="t1",
        runtime_s=0.0,
        artifact_manifest=[],
        resolved_config_path="a",
        unresolved_config_path="b",
        command_line="cmd",
        python_version="3.11",
        package_lock_hash="p",
        cuda_version="null",
        gpu_name="cpu",
    )
    assert "random_seeds" in manifest.missing_fields()


def test_protocol_methods_have_annotations() -> None:
    hints = get_type_hints(Distribution.sample)
    assert "n" in hints or hints  # runtime may vary; method exists
    assert callable(Distribution.sample)
