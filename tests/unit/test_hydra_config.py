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
