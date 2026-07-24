"""Regression test for equal-NFE accounting in the gate grid."""

from __future__ import annotations

from pathlib import Path

from hydra import compose, initialize_config_dir

from fewstep_regularities.experiments.factories import build_solver


def test_registered_gate_nfe_is_exact_for_every_solver() -> None:
    root = Path(__file__).resolve().parents[2]
    with initialize_config_dir(
        version_base=None,
        config_dir=str(root / "configs"),
    ):
        cfg = compose(config_name="config", overrides=["experiment=phase3_gate"])
    for solver_name in cfg.experiment.solver_names:
        solver = build_solver({"name": str(solver_name)})
        for nfe in cfg.experiment.nfe_budgets:
            assert int(nfe) % solver.evals_per_step == 0
