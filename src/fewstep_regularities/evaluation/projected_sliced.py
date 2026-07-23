"""Projected, sliced, entropic, and discrete Wasserstein evaluators."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from scipy.optimize import linprog
from torch import Tensor

from fewstep_regularities.evaluation.base import EvaluationResult
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_shape


def _as_samples(x: Tensor | Mapping[str, Tensor], name: str) -> Tensor:
    if isinstance(x, Mapping):
        if "samples" not in x:
            raise TypeError(f"{name} mapping must contain 'samples'")
        return x["samples"]
    return x


def projected_w2_squared_1d(u: Tensor, v: Tensor) -> Tensor:
    """Exact 1-D W2 squared for equal-weight empirical measures.

    Args:
        u: Projections of shape ``(n,)``.
        v: Projections of shape ``(m,)``.

    Mathematical definition:
        ``∫_0^1 |F_u^{-1}(q) - F_v^{-1}(q)|² dq``. For ``n = m``, this is
        ``(1/n) ∑_i (u_{(i)} - v_{(i)})²``.
    """
    assert_dtype(v, u.dtype, "v")
    assert_device(v, u.device, "v")
    assert_shape(u, (None,), "u")
    assert_shape(v, (None,), "v")
    if u.numel() == 0 or v.numel() == 0:
        raise ValueError("empirical measures must be non-empty")
    us = torch.sort(u).values
    vs = torch.sort(v).values
    if us.shape[0] == vs.shape[0]:
        return torch.mean((us - vs) ** 2)

    # Integrate the two empirical quantile step functions exactly by walking
    # through their combined CDF breakpoints.
    n = int(us.shape[0])
    m = int(vs.shape[0])
    i = 0
    j = 0
    q = 0.0
    total = torch.zeros((), dtype=u.dtype, device=u.device)
    while i < n and j < m:
        q_next = min((i + 1) / n, (j + 1) / m)
        total = total + (q_next - q) * (us[i] - vs[j]) ** 2
        q = q_next
        if q >= (i + 1) / n:
            i += 1
        if q >= (j + 1) / m:
            j += 1
    return total


def random_directions(
    n_proj: int,
    dim: int,
    dtype: torch.dtype,
    device: torch.device,
    generator: torch.Generator | None = None,
) -> Tensor:
    """Sample unit directions of shape ``(n_proj, dim)``."""
    if n_proj < 1:
        raise ValueError("n_proj must be positive")
    if dim < 1:
        raise ValueError("dim must be positive")
    raw = torch.randn(n_proj, dim, dtype=dtype, device=device, generator=generator)
    norms = torch.linalg.vector_norm(raw, dim=1, keepdim=True).clamp(min=1e-32)
    out: Tensor = raw / norms
    return out


@dataclass
class ProjectedW2Evaluator:
    """Projected empirical W2 estimator.

    The primary is the square root of the mean squared 1-D empirical W2 over
    the sampled directions.
    """

    n_projections: int = 1
    dtype: torch.dtype = DEFAULT_DTYPE
    seed: int | None = 0
    name: str = "projected_w2"

    def metadata(self) -> Mapping[str, Any]:
        return {
            "estimator": self.name,
            "is_exact_w2": False,
            "n_projections": self.n_projections,
            "definition": "sqrt(mean exact empirical 1D W2 squared)",
        }

    def uncertainty(self, result: EvaluationResult) -> Tensor | None:
        return result.uncertainty

    def compute(
        self,
        samples: Tensor,
        reference: Tensor | Mapping[str, Tensor],
    ) -> EvaluationResult:
        x = _as_samples(samples, "samples")
        y = _as_samples(reference, "reference")
        assert_dtype(x, self.dtype, "samples")
        assert_dtype(y, self.dtype, "reference")
        assert_device(y, x.device, "reference")
        assert_shape(x, (None, None), "samples")
        assert_shape(y, (None, x.shape[1]), "reference")
        if x.shape[0] == 0 or y.shape[0] == 0:
            raise ValueError("sample sets must be non-empty")
        gen = None
        if self.seed is not None:
            gen = torch.Generator(device=x.device)
            gen.manual_seed(int(self.seed))
        dirs = random_directions(
            self.n_projections, int(x.shape[1]), self.dtype, x.device, gen
        )
        vals = []
        for i in range(self.n_projections):
            vals.append(projected_w2_squared_1d(x @ dirs[i], y @ dirs[i]))
        stacked = torch.stack(vals)
        mean_sq = stacked.mean()
        primary = torch.sqrt(mean_sq.clamp(min=0.0))
        unc = None
        if self.n_projections > 1:
            se_mean_sq = stacked.std(unbiased=True) / (float(self.n_projections) ** 0.5)
            if float(mean_sq.item()) == 0.0:
                unc = torch.zeros_like(mean_sq)
            else:
                unc = se_mean_sq / (2.0 * torch.sqrt(mean_sq))
        return EvaluationResult(
            primary=primary,
            uncertainty=unc,
            auxiliaries={"mean_projected_w2_sq": mean_sq},
            metadata={
                **dict(self.metadata()),
                "n_samples": int(x.shape[0]),
                "n_reference": int(y.shape[0]),
                "seed": self.seed,
            },
        )


@dataclass
class SlicedWassersteinEvaluator:
    """Monte Carlo sliced Wasserstein estimator (Bonneel eqs. 30-31).

    Not exact W2 on Rd.
    """

    n_projections: int = 128
    dtype: torch.dtype = DEFAULT_DTYPE
    seed: int | None = 0
    name: str = "sliced_wasserstein"

    def metadata(self) -> Mapping[str, Any]:
        return {
            "estimator": self.name,
            "is_exact_w2": False,
            "n_projections": self.n_projections,
            "definition": "Bonneel (30)-(31): sqrt(MC mean of 1D W2 squared)",
            "reference": "papers/notes/bonneel2015sliced_wasserstein.md",
        }

    def uncertainty(self, result: EvaluationResult) -> Tensor | None:
        return result.uncertainty

    def compute(
        self,
        samples: Tensor,
        reference: Tensor | Mapping[str, Tensor],
    ) -> EvaluationResult:
        # Reuse projected evaluator with many directions.
        proj = ProjectedW2Evaluator(
            n_projections=self.n_projections,
            dtype=self.dtype,
            seed=self.seed,
            name=self.name,
        )
        result = proj.compute(samples, reference)
        meta = dict(result.metadata)
        meta.update(dict(self.metadata()))
        return EvaluationResult(
            primary=result.primary,
            uncertainty=result.uncertainty,
            auxiliaries=result.auxiliaries,
            metadata=meta,
        )


def _pairwise_sq_dists(x: Tensor, y: Tensor) -> Tensor:
    """Squared pairwise distances of shape ``(n, m)``."""
    # ||x||^2 + ||y||^2 - 2 x y^T
    x2 = torch.sum(x * x, dim=1, keepdim=True)
    y2 = torch.sum(y * y, dim=1, keepdim=True).transpose(0, 1)
    return (x2 + y2 - 2.0 * (x @ y.transpose(0, 1))).clamp(min=0.0)


@dataclass
class EntropicOTEvaluator:
    """Sinkhorn entropic OT cost with reported epsilon (Peyré 4.2).

    Returns ``sqrt`` of the transport cost ``⟨P, C⟩`` where ``C_ij = ||xi-yj||^2``.
    Do not present as exact W2.
    """

    epsilon: float = 0.05
    max_iter: int = 10000
    tol: float = 1e-5
    dtype: torch.dtype = DEFAULT_DTYPE
    name: str = "entropic_ot"

    def metadata(self) -> Mapping[str, Any]:
        return {
            "estimator": self.name,
            "is_exact_w2": False,
            "epsilon": self.epsilon,
            "definition": "Peyré (4.2) Sinkhorn; primary is sqrt(<P,C>)",
            "reference": "papers/notes/peyre2019computational_ot.md",
        }

    def uncertainty(self, result: EvaluationResult) -> Tensor | None:
        return result.uncertainty

    def compute(
        self,
        samples: Tensor,
        reference: Tensor | Mapping[str, Tensor],
    ) -> EvaluationResult:
        x = _as_samples(samples, "samples")
        y = _as_samples(reference, "reference")
        assert_dtype(x, self.dtype, "samples")
        assert_dtype(y, self.dtype, "reference")
        assert_device(y, x.device, "reference")
        assert_shape(x, (None, None), "samples")
        assert_shape(y, (None, x.shape[1]), "reference")
        if self.epsilon <= 0:
            raise ValueError("epsilon must be positive")
        n = int(x.shape[0])
        m = int(y.shape[0])
        if n == 0 or m == 0:
            raise ValueError("sample sets must be non-empty")
        if self.max_iter < 1:
            raise ValueError("max_iter must be positive")
        if self.tol <= 0:
            raise ValueError("tol must be positive")
        a = torch.full((n,), 1.0 / n, dtype=self.dtype, device=x.device)
        b = torch.full((m,), 1.0 / m, dtype=self.dtype, device=x.device)
        cost = _pairwise_sq_dists(x, y)
        # Log-domain Sinkhorn (Peyré 4.35-4.36 style).
        log_k = -cost / self.epsilon
        f = torch.zeros(n, dtype=self.dtype, device=x.device)
        g = torch.zeros(m, dtype=self.dtype, device=x.device)
        log_a = torch.log(a)
        log_b = torch.log(b)
        converged = False
        row_residual = torch.tensor(float("inf"), dtype=self.dtype, device=x.device)
        col_residual = torch.tensor(float("inf"), dtype=self.dtype, device=x.device)
        iterations = 0
        for iteration in range(1, self.max_iter + 1):
            # softmin over j: f_i = eps log a_i - eps logsumexp_j (log K_ij + g_j/eps)
            f = self.epsilon * (
                log_a - torch.logsumexp(log_k + g.unsqueeze(0) / self.epsilon, dim=1)
            )
            g = self.epsilon * (
                log_b
                - torch.logsumexp(
                    log_k.transpose(0, 1) + f.unsqueeze(0) / self.epsilon, dim=1
                )
            )
            log_p = (
                log_k + f.unsqueeze(1) / self.epsilon + g.unsqueeze(0) / self.epsilon
            )
            row_sums = torch.exp(torch.logsumexp(log_p, dim=1))
            col_sums = torch.exp(torch.logsumexp(log_p, dim=0))
            row_residual = torch.max(torch.abs(row_sums - a))
            col_residual = torch.max(torch.abs(col_sums - b))
            iterations = iteration
            if max(row_residual.item(), col_residual.item()) <= self.tol:
                converged = True
                break
        if not converged:
            raise RuntimeError(
                "entropic OT did not converge: "
                f"iterations={iterations}, row_residual={row_residual.item():.3e}, "
                f"col_residual={col_residual.item():.3e}, tol={self.tol:.3e}"
            )

        p = torch.exp(log_p)
        transport_cost = torch.sum(p * cost)
        entropy = -torch.sum(p * (log_p - 1.0))
        regularized_objective = transport_cost - self.epsilon * entropy
        primary = torch.sqrt(transport_cost.clamp(min=0.0))
        return EvaluationResult(
            primary=primary,
            uncertainty=None,
            auxiliaries={
                "transport_cost": transport_cost,
                "entropy": entropy,
                "regularized_objective": regularized_objective,
                "epsilon": torch.tensor(
                    self.epsilon, dtype=self.dtype, device=x.device
                ),
                "row_marginal_residual": row_residual,
                "column_marginal_residual": col_residual,
            },
            metadata={
                **dict(self.metadata()),
                "n_samples": n,
                "n_reference": m,
                "max_iter": self.max_iter,
                "iterations": iterations,
                "converged": converged,
                "primary_quantity": "sqrt_transport_component",
            },
        )


@dataclass
class DiscreteOTEvaluator:
    """Exact empirical W2 for small equal-weight sample sets via linprog.

    Cost is squared Euclidean. Primary value is ``W_2 = sqrt(⟨P*, C⟩)``.
    Restricted to ``n, m <= max_points``.
    """

    max_points: int = 64
    dtype: torch.dtype = DEFAULT_DTYPE
    name: str = "discrete_ot"

    def metadata(self) -> Mapping[str, Any]:
        return {
            "estimator": self.name,
            "is_exact_w2": False,
            "is_exact_empirical_w2": True,
            "scope": "finite equal-weight empirical measures",
            "max_points": self.max_points,
            "definition": "Kantorovich LP with C_ij=||xi-yj||^2",
            "reference": "papers/notes/peyre2019computational_ot.md",
        }

    def uncertainty(self, result: EvaluationResult) -> Tensor | None:
        return result.uncertainty

    def compute(
        self,
        samples: Tensor,
        reference: Tensor | Mapping[str, Tensor],
    ) -> EvaluationResult:
        x = _as_samples(samples, "samples")
        y = _as_samples(reference, "reference")
        assert_dtype(x, self.dtype, "samples")
        assert_dtype(y, self.dtype, "reference")
        assert_device(y, x.device, "reference")
        assert_shape(x, (None, None), "samples")
        assert_shape(y, (None, x.shape[1]), "reference")
        n = int(x.shape[0])
        m = int(y.shape[0])
        if n == 0 or m == 0:
            raise ValueError("sample sets must be non-empty")
        if n > self.max_points or m > self.max_points:
            raise ValueError(
                f"discrete OT limited to max_points={self.max_points}, got n={n}, m={m}"
            )
        cost = _pairwise_sq_dists(x, y).detach().cpu().numpy().astype(np.float64)
        # Variables P_ij flattened row-major. Marginals a=1/n, b=1/m.
        c_vec = cost.reshape(-1)
        a_eq = []
        b_eq = []
        # Row sums.
        for i in range(n):
            row = np.zeros(n * m)
            row[i * m : (i + 1) * m] = 1.0
            a_eq.append(row)
            b_eq.append(1.0 / n)
        # Column sums (drop last for redundancy).
        for j in range(m - 1):
            col = np.zeros(n * m)
            col[j::m] = 1.0
            a_eq.append(col)
            b_eq.append(1.0 / m)
        bounds = [(0.0, None)] * (n * m)
        result = linprog(
            c_vec,
            A_eq=np.asarray(a_eq),
            b_eq=np.asarray(b_eq),
            bounds=bounds,
            method="highs",
        )
        if not result.success:
            raise RuntimeError(f"discrete OT failed: {result.message}")
        transport_cost = float(result.fun)
        primary = torch.tensor(transport_cost**0.5, dtype=self.dtype, device=x.device)
        return EvaluationResult(
            primary=primary,
            uncertainty=None,
            auxiliaries={
                "transport_cost": torch.tensor(
                    transport_cost, dtype=self.dtype, device=x.device
                )
            },
            metadata={
                **dict(self.metadata()),
                "n_samples": n,
                "n_reference": m,
                "solver": "scipy.linprog.highs",
            },
        )
