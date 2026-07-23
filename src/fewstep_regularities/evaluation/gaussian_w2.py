"""Exact Gaussian Wasserstein-2 distance (Bures)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import torch
from torch import Tensor

from fewstep_regularities.evaluation.base import EvaluationResult
from fewstep_regularities.paths.gaussian_ot import matrix_sqrt_psd
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_shape


def bures_distance_squared(cov_a: Tensor, cov_b: Tensor) -> Tensor:
    """Bures metric squared between covariances, Peyré (2.42).

    ``B(Σ_a, Σ_b)^2 = tr(Σ_a + Σ_b - 2 (Σ_a^{1/2} Σ_b Σ_a^{1/2})^{1/2})``.
    """
    assert_shape(cov_a, (None, None), "cov_a")
    assert_shape(cov_b, cov_a.shape, "cov_b")
    s_a = matrix_sqrt_psd(cov_a)
    mid = matrix_sqrt_psd(s_a @ cov_b @ s_a)
    return torch.trace(cov_a + cov_b - 2.0 * mid)


def gaussian_w2_squared(
    mean_a: Tensor,
    cov_a: Tensor,
    mean_b: Tensor,
    cov_b: Tensor,
) -> Tensor:
    """Exact ``W_2^2`` between Gaussians, Peyré (2.41).

    ``W_2^2 = ∥m_a - m_b∥^2 + B(Σ_a, Σ_b)^2``.
    """
    assert_shape(mean_a, (None,), "mean_a")
    assert_shape(mean_b, mean_a.shape, "mean_b")
    mean_term = torch.sum((mean_a - mean_b) ** 2)
    return mean_term + bures_distance_squared(cov_a, cov_b)


def gaussian_w2(
    mean_a: Tensor,
    cov_a: Tensor,
    mean_b: Tensor,
    cov_b: Tensor,
) -> Tensor:
    """Exact ``W_2`` between Gaussians."""
    return torch.sqrt(gaussian_w2_squared(mean_a, cov_a, mean_b, cov_b).clamp(min=0.0))


@dataclass
class GaussianW2Evaluator:
    """Exact Gaussian W2 evaluator.

    Prefer analytical ``(mean, covariance)`` inputs. Sample-based use estimates
    empirical moments and is marked non-exact in metadata.
    """

    name: str = "gaussian_w2"
    dtype: torch.dtype = DEFAULT_DTYPE

    def compute(
        self,
        samples: Tensor | Mapping[str, Tensor],
        reference: Tensor | Mapping[str, Tensor],
    ) -> EvaluationResult:
        """Compute exact or empirical-moment Gaussian W2.

        Args:
            samples: Either samples ``(n, d)`` or mapping with ``mean`` ``(d,)``
                and ``covariance`` ``(d, d)``.
            reference: Same formats as ``samples``.

        Returns:
            ``EvaluationResult`` with primary ``W_2`` scalar tensor.
        """
        mean_a, cov_a, exact_a = self._moments(samples, "samples")
        mean_b, cov_b, exact_b = self._moments(reference, "reference")
        is_exact = exact_a and exact_b
        w2 = gaussian_w2(mean_a, cov_a, mean_b, cov_b)
        mean_err = torch.linalg.vector_norm(mean_a - mean_b)
        cov_err = torch.linalg.matrix_norm(cov_a - cov_b, ord="fro")
        return EvaluationResult(
            primary=w2,
            uncertainty=None,
            auxiliaries={"mean_error": mean_err, "covariance_frobenius_error": cov_err},
            metadata={
                "estimator": "gaussian_bures_w2",
                "is_exact": is_exact,
                "formula": "Peyre (2.41)-(2.42)",
            },
        )

    def uncertainty(self, result: EvaluationResult) -> Tensor | None:
        """Exact W2 has no sampling uncertainty."""
        del result
        return None

    def metadata(self) -> Mapping[str, Any]:
        """Static evaluator documentation."""
        return {
            "name": self.name,
            "class": "exact_gaussian_w2",
            "reference": "Peyre and Cuturi (2019), eqs. (2.41)-(2.42)",
        }

    def _moments(
        self,
        data: Tensor | Mapping[str, Tensor],
        name: str,
    ) -> tuple[Tensor, Tensor, bool]:
        if isinstance(data, Mapping):
            mean = data["mean"]
            cov = data["covariance"]
            assert_dtype(mean, self.dtype, f"{name}.mean")
            assert_dtype(cov, self.dtype, f"{name}.covariance")
            return mean, cov, True
        assert_dtype(data, self.dtype, name)
        assert_shape(data, (None, None), name)
        mean = data.mean(dim=0)
        centered = data - mean.unsqueeze(0)
        cov = (centered.transpose(0, 1) @ centered) / max(data.shape[0] - 1, 1)
        return mean, cov, False
