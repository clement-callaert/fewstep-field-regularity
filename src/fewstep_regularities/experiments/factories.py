"""Hydra object factories for Phase 1 components."""

from __future__ import annotations

from typing import Any

import torch
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.distributions.gaussian import (
    Gaussian,
    anisotropic_gaussian,
    low_rank_gaussian,
    standard_gaussian,
)
from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField
from fewstep_regularities.fields.gaussian_ot_field import GaussianOTField
from fewstep_regularities.metrics.affine_gaussian import (
    AveragedSquaredLipschitzProxy,
    ExpectedSquaredJacobianNorm,
    JacobianTemporalVariation,
    LagrangianAcceleration,
    MaxSampledSpectralJacobianNorm,
    PathWeightedExpectedJacobianNorm,
    SpatialTemporalStiffness,
    TemporalFieldDerivativeNorm,
)
from fewstep_regularities.paths.gaussian_ot import GaussianOTPath
from fewstep_regularities.paths.linear import LinearPath
from fewstep_regularities.paths.lipschitz_guided import LipschitzGuidedPath
from fewstep_regularities.paths.variance_preserving import VariancePreservingTrigPath
from fewstep_regularities.solvers.euler import EulerSolver
from fewstep_regularities.solvers.heun import HeunSolver
from fewstep_regularities.solvers.rk4 import RK4Solver
from fewstep_regularities.utils.precision import resolve_dtype


def cfg_to_dict(cfg: DictConfig | dict[str, Any]) -> dict[str, Any]:
    """Convert OmegaConf node to a plain dict."""
    if isinstance(cfg, dict):
        return dict(cfg)
    container = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(container, dict):
        raise TypeError("config node must resolve to a mapping")
    return {str(k): v for k, v in container.items()}


def build_dtype(cfg: DictConfig) -> torch.dtype:
    """Resolve precision dtype from config."""
    name = str(OmegaConf.select(cfg, "precision.dtype", default="float64"))
    return resolve_dtype(name)


def build_device(cfg: DictConfig) -> torch.device:
    """Resolve compute device from config."""
    name = str(OmegaConf.select(cfg, "compute.device", default="cpu"))
    return torch.device(name)


def build_gaussian(
    dist_cfg: DictConfig | dict[str, Any],
    dim: int,
    dtype: torch.dtype,
    device: torch.device,
    generator: torch.Generator | None = None,
) -> Gaussian:
    """Build a Gaussian from a distribution config group."""
    data = cfg_to_dict(dist_cfg)
    name = str(data.get("name", data.get("kind", "")))
    if name in {"standard_gaussian", "gaussian"} and data.get("role") == "source":
        return standard_gaussian(dim, dtype=dtype, device=device)
    if name == "standard_gaussian":
        return standard_gaussian(dim, dtype=dtype, device=device)
    if name == "anisotropic_gaussian":
        return anisotropic_gaussian(
            dim,
            anisotropy=float(data.get("anisotropy", 4.0)),
            dtype=dtype,
            device=device,
        )
    if name == "low_rank_gaussian":
        return low_rank_gaussian(
            dim,
            rank=int(data.get("rank", 2)),
            noise_variance=float(data.get("noise_variance", 0.05)),
            dtype=dtype,
            device=device,
            generator=generator,
        )
    # Fallback by kind.
    kind = str(data.get("kind", ""))
    if kind == "gaussian" and data.get("role") == "source":
        return standard_gaussian(dim, dtype=dtype, device=device)
    raise ValueError(f"Unsupported distribution config: {name or kind}")


def effective_m(target: Gaussian) -> float:
    """Scalar variance ratio for Lipschitz-guided schedule.

    When the source is ``N(0, I)``, use the largest eigenvalue of the target
    covariance as the scalar ``M`` (stiffness-relevant). Geometric mean is
    unsuitable for anisotropic targets whose eigenvalues are reciprocal around
    1, because that mean is exactly 1 and the schedule is undefined.
    """
    ev = torch.linalg.eigvalsh(target.covariance())
    m = float(ev.max().item())
    if abs(m - 1.0) < 1e-12:
        ratio = float((ev.max() / ev.min().clamp(min=1e-32)).item())
        if abs(ratio - 1.0) < 1e-12:
            raise ValueError(
                "Cannot form Lipschitz-guided M: target covariance too close to I"
            )
        m = ratio
    return m


def build_path(
    path_cfg: DictConfig | dict[str, Any],
    source: Gaussian,
    target: Gaussian,
    dtype: torch.dtype,
) -> Any:
    """Build a probability path."""
    data = cfg_to_dict(path_cfg)
    name = str(data.get("name", data.get("schedule", "")))
    if name == "linear":
        return LinearPath(dtype=dtype)
    if name in {"variance_preserving", "variance_preserving_trig"}:
        return VariancePreservingTrigPath(dtype=dtype)
    if name == "lipschitz_guided":
        m = float(data.get("m", effective_m(target)))
        return LipschitzGuidedPath(m=m, dtype=dtype)
    if name == "gaussian_ot":
        return GaussianOTPath(source=source, target=target, dtype=dtype)
    raise ValueError(f"Unsupported path config: {name}")


def build_field(
    path_cfg: DictConfig | dict[str, Any],
    source: Gaussian,
    target: Gaussian,
    path: Any,
    dtype: torch.dtype,
) -> GaussianAffineField | GaussianOTField:
    """Build an exact velocity field for the path."""
    data = cfg_to_dict(path_cfg)
    name = str(data.get("name", data.get("schedule", "")))
    if name == "gaussian_ot":
        return GaussianOTField(source=source, target=target, dtype=dtype)
    return GaussianAffineField(
        source=source, target=target, schedule=path, dtype=dtype
    )


def build_solver(solver_cfg: DictConfig | dict[str, Any]) -> Any:
    """Build a fixed-step ODE solver."""
    data = cfg_to_dict(solver_cfg)
    name = str(data.get("name", ""))
    if name == "euler":
        return EulerSolver()
    if name == "heun":
        return HeunSolver()
    if name == "rk4":
        return RK4Solver()
    raise ValueError(f"Unsupported solver: {name}")


def build_evaluator(eval_cfg: DictConfig | dict[str, Any], dtype: torch.dtype) -> Any:
    """Build a distributional evaluator."""
    data = cfg_to_dict(eval_cfg)
    name = str(data.get("name", ""))
    if name == "gaussian_w2":
        return GaussianW2Evaluator(dtype=dtype)
    raise ValueError(f"Unsupported evaluator for Phase 1: {name}")


def build_metric(metric_cfg: DictConfig | dict[str, Any], dtype: torch.dtype) -> Any:
    """Build a regularity metric."""
    data = cfg_to_dict(metric_cfg)
    name = str(data.get("name", ""))
    n_time = int(data.get("n_time", 64))
    mapping = {
        "averaged_squared_lipschitz_proxy": AveragedSquaredLipschitzProxy,
        "max_sampled_spectral_jacobian_norm": MaxSampledSpectralJacobianNorm,
        "path_weighted_expected_jacobian_norm": PathWeightedExpectedJacobianNorm,
        "expected_squared_jacobian_norm": ExpectedSquaredJacobianNorm,
        "temporal_field_derivative_norm": TemporalFieldDerivativeNorm,
        "jacobian_temporal_variation": JacobianTemporalVariation,
        "lagrangian_acceleration": LagrangianAcceleration,
        "spatial_temporal_stiffness": SpatialTemporalStiffness,
    }
    if name not in mapping:
        raise ValueError(f"Unsupported metric: {name}")
    return mapping[name](n_time=n_time, dtype=dtype)
