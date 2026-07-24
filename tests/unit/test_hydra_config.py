"""Hydra config composition tests."""

from __future__ import annotations

from pathlib import Path

from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf


def test_smoke_config_resolves() -> None:
    root = Path(__file__).resolve().parents[2]
    raw = OmegaConf.load(root / "configs" / "config.yaml")
    assert raw.hydra.job.chdir is False
    config_dir = str(root / "configs")
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(config_name="config", overrides=["experiment=smoke"])
    assert cfg.precision.dtype == "float64"
    assert cfg.experiment.mode == "dry_run"
    assert cfg.artifact_policy.release_ready is False
    assert list(cfg.experiment.hypotheses) == ["H1", "H2", "H3", "H4"]
    text = OmegaConf.to_yaml(cfg, resolve=True)
    assert "averaged_squared_lipschitz_proxy" in text


def test_phase2_smoke_selects_mixture_safe_defaults() -> None:
    root = Path(__file__).resolve().parents[2]
    config_dir = str(root / "configs")
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(config_name="config", overrides=["experiment=phase2_smoke"])
    assert cfg.distribution.name == "two_mode_gmm"
    assert cfg.evaluator.name == "sliced_wasserstein"


def test_phase3_gate_config_is_registered_and_float64() -> None:
    root = Path(__file__).resolve().parents[2]
    config_dir = str(root / "configs")
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(config_name="config", overrides=["experiment=phase3_gate"])
    assert cfg.experiment.mode == "gate_benchmark"
    assert cfg.experiment.gate_version == "2026-07-23-v1"
    assert list(cfg.experiment.seeds) == list(range(10))
    assert cfg.precision.dtype == "float64"
    assert "gaussian_ot" not in list(cfg.experiment.path_names)


def test_phase4_gaussian_reproduction_config_is_focused() -> None:
    root = Path(__file__).resolve().parents[2]
    config_dir = str(root / "configs")
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(
            config_name="config",
            overrides=[
                "experiment=phase4_gaussian_reproduction",
                "artifact_policy=phase4_release_ready",
            ],
        )
    assert cfg.experiment.mode == "phase4_gaussian_reproduction"
    assert cfg.precision.dtype == "float64"
    assert cfg.compute.device == "cpu"
    assert cfg.artifact_policy.release_ready is True
    assert [item.name for item in cfg.experiment.targets] == [
        "anisotropic_gaussian",
        "low_rank_gaussian",
    ]
    assert [item.name for item in cfg.experiment.paths] == [
        "linear",
        "variance_preserving",
    ]
    assert [item.name for item in cfg.experiment.solvers] == [
        "euler",
        "heun",
        "rk4",
    ]
    assert list(cfg.experiment.dimensions) == [2, 8]
    assert list(cfg.experiment.nfe_budgets) == [8, 16, 32]
    assert cfg.experiment.expected_counts.endpoint_configurations == 72


def test_phase4_affine_audit_configs_resolve() -> None:
    root = Path(__file__).resolve().parents[2]
    config_dir = str(root / "configs")
    experiments = {
        "phase4_precision": "precision",
        "phase4_decomposition": "decomposition",
        "phase4_diagnostics": "diagnostics",
        "phase4_robustness": "robustness",
        "phase4_final_validation": "final_validation",
    }
    for experiment, audit_kind in experiments.items():
        with initialize_config_dir(version_base=None, config_dir=config_dir):
            cfg = compose(
                config_name="config",
                overrides=[
                    f"experiment={experiment}",
                    "artifact_policy=phase4_release_ready",
                ],
            )
        assert cfg.experiment.mode == "phase4_affine_audit"
        assert cfg.experiment.audit_kind == audit_kind
        assert cfg.precision.dtype == "float64"
        assert cfg.compute.device == "cpu"
        assert cfg.artifact_policy.release_ready is True
        assert cfg.experiment.runtime.hard_stop_minutes <= 120
