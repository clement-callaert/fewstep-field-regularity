"""Regularity metrics for affine Gaussian fields."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import torch
from torch import Tensor

from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField
from fewstep_regularities.fields.gaussian_ot_field import GaussianOTField
from fewstep_regularities.metrics.base import MetricResult
from fewstep_regularities.utils.precision import DEFAULT_DTYPE

AffineField = GaussianAffineField | GaussianOTField


def _as_affine(field: VelocityField) -> AffineField:
    if isinstance(field, (GaussianAffineField, GaussianOTField)):
        return field
    raise TypeError("Phase 1 metrics require GaussianAffineField or GaussianOTField")


def _spectral_norm(matrix: Tensor) -> Tensor:
    """Operator 2-norm of a square matrix."""
    out: Tensor = torch.linalg.matrix_norm(matrix, ord=2)
    return out


def _frobenius_norm(matrix: Tensor) -> Tensor:
    """Frobenius norm."""
    out: Tensor = torch.linalg.matrix_norm(matrix, ord="fro")
    return out


def integrate_time(values: Tensor, times: Tensor) -> Tensor:
    return torch.trapz(values, times)


def _default_times(n_time: int, dtype: torch.dtype) -> Tensor:
    return torch.linspace(0, 1, n_time, dtype=dtype)


@dataclass
class AveragedSquaredLipschitzProxy:
    """Avg-Lip² proxy for affine fields (Def 3.2). Not a global Lipschitz constant.

    Uses exact spectral Jacobians on a time grid and a trapezoidal integral.
    """

    name: str = "averaged_squared_lipschitz_proxy"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "spectral_2",
            "time_weighting": "uniform_trapezoid",
            "sampling_distribution": "none_state_independent",
            "definition": "Lipschitz-guided Def 3.2 / eq. (3.4)",
            "n_time": self.n_time,
            "note": "Exact spectral Jacobian at grid times; trapezoidal time integral",
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        vals = torch.stack([_spectral_norm(affine.jacobian_matrix(t)) ** 2 for t in times])
        return MetricResult(
            value=integrate_time(vals, times),
            is_exact=False,
            estimator_name=self.name,
            n_samples=None,
            uncertainty=None,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class MaxSampledSpectralJacobianNorm:
    """Grid-maximum spectral Jacobian norm (sampled lower bound)."""

    name: str = "max_sampled_spectral_jacobian_norm"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "spectral_2",
            "time_weighting": "uniform_grid_max",
            "n_time": self.n_time,
            "note": "Grid maximum; not a certified global Lipschitz constant",
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        vals = torch.stack([_spectral_norm(affine.jacobian_matrix(t)) for t in times])
        return MetricResult(
            value=vals.max(),
            is_exact=False,
            estimator_name=self.name,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class PathWeightedExpectedJacobianNorm:
    """Time-averaged spectral Jacobian norm for affine fields."""

    name: str = "path_weighted_expected_jacobian_norm"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "spectral_2",
            "time_weighting": "uniform_trapezoid",
            "n_time": self.n_time,
            "note": "Time average of spectral Jacobian; not path-distribution reweighted",
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        vals = torch.stack([_spectral_norm(affine.jacobian_matrix(t)) for t in times])
        return MetricResult(
            value=integrate_time(vals, times),
            is_exact=False,
            estimator_name=self.name,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class ExpectedSquaredJacobianNorm:
    """Time-averaged squared Frobenius Jacobian norm."""

    name: str = "expected_squared_jacobian_norm"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "frobenius",
            "time_weighting": "uniform_trapezoid",
            "n_time": self.n_time,
            "note": "Exact Frobenius Jacobian at grid times; trapezoidal time integral",
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        vals = torch.stack(
            [_frobenius_norm(affine.jacobian_matrix(t)) ** 2 for t in times]
        )
        return MetricResult(
            value=integrate_time(vals, times),
            is_exact=False,
            estimator_name=self.name,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class TemporalFieldDerivativeNorm:
    """FD temporal derivative norm along the marginal mean path."""

    name: str = "temporal_field_derivative_norm"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE
    fd_eps: float = 1e-6

    def required_quantities(self) -> Sequence[str]:
        return ("time_derivative",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "approximation": "finite_difference",
            "fd_eps": self.fd_eps,
            "sampling_distribution": "marginal_mean_path",
            "n_time": self.n_time,
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        vals = []
        for t in times:
            x = affine.mean_t(t).unsqueeze(0)
            dt = affine.time_derivative(t, x)
            if dt is None:
                raise RuntimeError("time_derivative unavailable")
            vals.append(torch.linalg.vector_norm(dt[0]))
        return MetricResult(
            value=integrate_time(torch.stack(vals), times),
            is_exact=False,
            estimator_name=self.name,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class JacobianTemporalVariation:
    """Mean forward-difference Jacobian variation on a time grid."""

    name: str = "jacobian_temporal_variation"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "approximation": "forward_difference_on_grid",
            "matrix_norm": "frobenius",
            "n_time": self.n_time,
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        js = [affine.jacobian_matrix(t) for t in times]
        vals = []
        for i in range(len(times) - 1):
            dt = times[i + 1] - times[i]
            vals.append(_frobenius_norm(js[i + 1] - js[i]) / dt)
        return MetricResult(
            value=torch.stack(vals).mean(),
            is_exact=False,
            estimator_name=self.name,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class LagrangianAcceleration:
    """∥∂_t v + J v∥ along the marginal mean path."""

    name: str = "lagrangian_acceleration"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE

    def required_quantities(self) -> Sequence[str]:
        return ("evaluate", "jacobian", "time_derivative")

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "definition": "∥∂_t v + J v∥ at marginal mean path",
            "n_time": self.n_time,
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        affine = _as_affine(field)
        times = times if times is not None else _default_times(self.n_time, self.dtype)
        vals = []
        for t in times:
            x = affine.mean_t(t).unsqueeze(0)
            v = affine.evaluate(t, x)
            j = affine.jacobian(t, x)[0]
            dt = affine.time_derivative(t, x)
            if dt is None:
                raise RuntimeError("time_derivative unavailable")
            vals.append(torch.linalg.vector_norm(dt[0] + j @ v[0]))
        return MetricResult(
            value=integrate_time(torch.stack(vals), times),
            is_exact=False,
            estimator_name=self.name,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class SpatialTemporalStiffness:
    """Combined avg-Lip² plus temporal derivative energy."""

    name: str = "spatial_temporal_stiffness"
    n_time: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE
    temporal_weight: float = 1.0

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian", "time_derivative")

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "combination": "A2 + w * temporal_field_derivative_norm",
            "temporal_weight": self.temporal_weight,
            "n_time": self.n_time,
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        a2 = AveragedSquaredLipschitzProxy(n_time=self.n_time, dtype=self.dtype).compute(
            field, times=times, states=states
        )
        temp = TemporalFieldDerivativeNorm(n_time=self.n_time, dtype=self.dtype).compute(
            field, times=times, states=states
        )
        return MetricResult(
            value=a2.value + self.temporal_weight * temp.value,
            is_exact=False,
            estimator_name=self.name,
            metadata={
                **dict(self.estimator_metadata()),
                "a2": float(a2.value.item()),
                "temporal": float(temp.value.item()),
            },
        )
