"""Monte Carlo regularity metrics for state-dependent mixture fields."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import torch
from torch import Tensor

from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.fields.mixture_affine import MixtureAffineField
from fewstep_regularities.metrics.affine_gaussian import (
    _frobenius_norm,
    _spectral_norm,
    integrate_time,
)
from fewstep_regularities.metrics.base import MetricResult
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_shape


def _as_mixture(field: VelocityField) -> MixtureAffineField:
    if isinstance(field, MixtureAffineField):
        return field
    raise TypeError("mixture MC metrics require MixtureAffineField")


def _mixture_times(
    mix: MixtureAffineField,
    times: Tensor | None,
    n_time: int,
    dtype: torch.dtype,
) -> Tensor:
    if times is None:
        return torch.linspace(0, 1, n_time, dtype=dtype, device=mix.target.device)
    assert_dtype(times, dtype, "times")
    assert_device(times, mix.target.device, "times")
    assert_shape(times, (None,), "times")
    return times


def _mixture_result(
    value: Tensor,
    name: str,
    *,
    n_time: int,
    n_samples: int,
    seed: int,
    quantity: str,
) -> MetricResult:
    return MetricResult(
        value=value,
        is_exact=False,
        estimator_name=name,
        n_samples=n_samples,
        uncertainty=None,
        metadata={
            "is_exact": False,
            "sampling_distribution": "marginal_gmm_at_t",
            "n_time": n_time,
            "n_samples": n_samples,
            "seed": seed,
            "quantity": quantity,
        },
    )


@dataclass
class MCPathWeightedExpectedJacobianNorm:
    """Path-distribution-weighted expected spectral Jacobian for mixtures."""

    name: str = "path_weighted_expected_jacobian_norm"
    n_time: int = 32
    n_samples: int = 128
    dtype: torch.dtype = DEFAULT_DTYPE
    seed: int = 0

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "spectral_2",
            "sampling_distribution": "marginal_gmm_at_t",
            "n_time": self.n_time,
            "n_samples": self.n_samples,
            "seed": self.seed,
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        mix = _as_mixture(field)
        times = _mixture_times(mix, times, self.n_time, self.dtype)
        gen = torch.Generator(device=mix.target.device)
        gen.manual_seed(self.seed)
        vals = []
        for t in times:
            x = mix.sample_marginal(t, self.n_samples, generator=gen)
            j = mix.jacobian(t, x)
            norms = torch.stack([_spectral_norm(j[i]) for i in range(j.shape[0])])
            vals.append(norms.mean())
        return MetricResult(
            value=integrate_time(torch.stack(vals), times),
            is_exact=False,
            estimator_name=self.name,
            n_samples=self.n_samples,
            uncertainty=None,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class MCExpectedSquaredJacobianNorm:
    """MC expected squared Frobenius Jacobian for mixtures."""

    name: str = "expected_squared_jacobian_norm"
    n_time: int = 32
    n_samples: int = 128
    dtype: torch.dtype = DEFAULT_DTYPE
    seed: int = 0

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "frobenius",
            "sampling_distribution": "marginal_gmm_at_t",
            "n_time": self.n_time,
            "n_samples": self.n_samples,
            "seed": self.seed,
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        mix = _as_mixture(field)
        times = _mixture_times(mix, times, self.n_time, self.dtype)
        gen = torch.Generator(device=mix.target.device)
        gen.manual_seed(self.seed)
        vals = []
        for t in times:
            x = mix.sample_marginal(t, self.n_samples, generator=gen)
            j = mix.jacobian(t, x)
            norms = torch.stack([_frobenius_norm(j[i]) ** 2 for i in range(j.shape[0])])
            vals.append(norms.mean())
        return MetricResult(
            value=integrate_time(torch.stack(vals), times),
            is_exact=False,
            estimator_name=self.name,
            n_samples=self.n_samples,
            metadata=dict(self.estimator_metadata()),
        )


@dataclass
class MCAveragedSquaredLipschitzProxy:
    """MC avg of squared spectral Jacobian norms for mixtures."""

    name: str = "averaged_squared_lipschitz_proxy"
    n_time: int = 32
    n_samples: int = 128
    dtype: torch.dtype = DEFAULT_DTYPE
    seed: int = 0

    def required_quantities(self) -> Sequence[str]:
        return ("jacobian",)

    def estimator_metadata(self) -> Mapping[str, Any]:
        return {
            "is_exact": False,
            "matrix_norm": "spectral_2",
            "sampling_distribution": "marginal_gmm_at_t",
            "n_time": self.n_time,
            "n_samples": self.n_samples,
            "note": "Sampled lower bound; not a global Lipschitz constant",
        }

    def compute(
        self,
        field: VelocityField,
        times: Tensor | None = None,
        states: Tensor | None = None,
    ) -> MetricResult:
        del states
        mix = _as_mixture(field)
        times = _mixture_times(mix, times, self.n_time, self.dtype)
        gen = torch.Generator(device=mix.target.device)
        gen.manual_seed(self.seed)
        vals = []
        for t in times:
            x = mix.sample_marginal(t, self.n_samples, generator=gen)
            j = mix.jacobian(t, x)
            norms = torch.stack([_spectral_norm(j[i]) ** 2 for i in range(j.shape[0])])
            vals.append(norms.mean())
        return MetricResult(
            value=integrate_time(torch.stack(vals), times),
            is_exact=False,
            estimator_name=self.name,
            n_samples=self.n_samples,
            metadata=dict(self.estimator_metadata()),
        )


def dispatch_metric_compute(
    metric: Any,
    field: VelocityField,
    times: Tensor | None = None,
    states: Tensor | None = None,
) -> MetricResult:
    """Route affine vs mixture metrics."""
    if isinstance(field, MixtureAffineField):
        name = str(getattr(metric, "name", ""))
        n_time = int(getattr(metric, "n_time", 32))
        n_samples = int(getattr(metric, "n_samples", 128))
        seed = int(getattr(metric, "seed", 0))
        dtype = getattr(metric, "dtype", DEFAULT_DTYPE)
        if name == "averaged_squared_lipschitz_proxy":
            return MCAveragedSquaredLipschitzProxy(
                n_time=n_time,
                n_samples=n_samples,
                dtype=dtype,
                seed=seed,
            ).compute(field, times=times, states=states)
        if name == "path_weighted_expected_jacobian_norm":
            return MCPathWeightedExpectedJacobianNorm(
                n_time=n_time,
                n_samples=n_samples,
                dtype=dtype,
                seed=seed,
            ).compute(field, times=times, states=states)
        if name == "expected_squared_jacobian_norm":
            return MCExpectedSquaredJacobianNorm(
                n_time=n_time,
                n_samples=n_samples,
                dtype=dtype,
                seed=seed,
            ).compute(field, times=times, states=states)
        if name == "max_sampled_spectral_jacobian_norm":
            mix = field
            use_times = _mixture_times(mix, times, n_time, dtype)
            gen = torch.Generator(device=mix.target.device)
            gen.manual_seed(seed)
            vals = []
            for t in use_times:
                x = mix.sample_marginal(t, n_samples, generator=gen)
                j = mix.jacobian(t, x)
                vals.append(
                    torch.stack([_spectral_norm(j[i]) for i in range(j.shape[0])]).max()
                )
            return MetricResult(
                value=torch.stack(vals).max(),
                is_exact=False,
                estimator_name=name,
                n_samples=n_samples,
                metadata={
                    "is_exact": False,
                    "sampling_distribution": "marginal_gmm_at_t",
                    "n_time": n_time,
                    "n_samples": n_samples,
                    "seed": seed,
                    "quantity": "sampled_max_spectral_jacobian_norm",
                },
            )
        if name == "temporal_field_derivative_norm":
            mix = field
            use_times = _mixture_times(mix, times, n_time, dtype)
            gen = torch.Generator(device=mix.target.device).manual_seed(seed)
            vals = []
            for t in use_times:
                x = mix.sample_marginal(t, n_samples, generator=gen)
                derivative = mix.time_derivative(t, x)
                if derivative is None:
                    raise RuntimeError("time_derivative unavailable")
                vals.append(torch.linalg.vector_norm(derivative, dim=1).mean())
            return _mixture_result(
                integrate_time(torch.stack(vals), use_times),
                name,
                n_time=n_time,
                n_samples=n_samples,
                seed=seed,
                quantity="expected_temporal_field_derivative_norm",
            )
        if name == "jacobian_temporal_variation":
            mix = field
            use_times = _mixture_times(mix, times, n_time, dtype)
            gen = torch.Generator(device=mix.target.device).manual_seed(seed)
            eps = torch.tensor(1e-6, dtype=dtype, device=mix.target.device)
            vals = []
            for t in use_times:
                x = mix.sample_marginal(t, n_samples, generator=gen)
                t_plus = (t + eps).clamp(max=1.0)
                t_minus = (t - eps).clamp(min=0.0)
                dt = (t_plus - t_minus).clamp(min=1e-12)
                delta = (mix.jacobian(t_plus, x) - mix.jacobian(t_minus, x)) / dt
                vals.append(torch.linalg.matrix_norm(delta, ord="fro").mean())
            return _mixture_result(
                integrate_time(torch.stack(vals), use_times),
                name,
                n_time=n_time,
                n_samples=n_samples,
                seed=seed,
                quantity="expected_jacobian_temporal_variation",
            )
        if name == "lagrangian_acceleration":
            mix = field
            use_times = _mixture_times(mix, times, n_time, dtype)
            gen = torch.Generator(device=mix.target.device).manual_seed(seed)
            vals = []
            for t in use_times:
                x = mix.sample_marginal(t, n_samples, generator=gen)
                velocity = mix.evaluate(t, x)
                jacobian = mix.jacobian(t, x)
                derivative = mix.time_derivative(t, x)
                if derivative is None:
                    raise RuntimeError("time_derivative unavailable")
                material = derivative + torch.bmm(
                    jacobian, velocity.unsqueeze(2)
                ).squeeze(2)
                vals.append(torch.linalg.vector_norm(material, dim=1).mean())
            return _mixture_result(
                integrate_time(torch.stack(vals), use_times),
                name,
                n_time=n_time,
                n_samples=n_samples,
                seed=seed,
                quantity="expected_lagrangian_acceleration",
            )
        if name == "spatial_temporal_stiffness":
            spatial_metric = MCAveragedSquaredLipschitzProxy(
                n_time=n_time, n_samples=n_samples, dtype=dtype, seed=seed
            )
            spatial = spatial_metric.compute(field, times=times, states=states)
            temporal_proxy = type(
                "_TemporalMetric",
                (),
                {
                    "name": "temporal_field_derivative_norm",
                    "n_time": n_time,
                    "n_samples": n_samples,
                    "dtype": dtype,
                    "seed": seed,
                },
            )()
            temporal = dispatch_metric_compute(
                temporal_proxy, field, times=times, states=states
            )
            weight = float(getattr(metric, "temporal_weight", 1.0))
            return MetricResult(
                value=spatial.value + weight * temporal.value,
                is_exact=False,
                estimator_name=name,
                n_samples=n_samples,
                uncertainty=None,
                metadata={
                    "is_exact": False,
                    "sampling_distribution": "marginal_gmm_at_t",
                    "n_time": n_time,
                    "n_samples": n_samples,
                    "seed": seed,
                    "quantity": "spatial_plus_weighted_temporal_stiffness",
                    "temporal_weight": weight,
                    "spatial": float(spatial.value.item()),
                    "temporal": float(temporal.value.item()),
                },
            )
    result: MetricResult = metric.compute(field, times=times, states=states)
    return result
