"""Distributional evaluator protocol."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from torch import Tensor


@dataclass(frozen=True)
class EvaluationResult:
    """Primary and auxiliary evaluation quantities.

    Attributes:
        primary: Primary scalar error (for example W2).
        uncertainty: Uncertainty for the primary estimate when available.
        auxiliaries: Secondary metrics such as mean or covariance error.
        metadata: Estimator name, regularization, sample sizes, etc.
    """

    primary: Tensor
    uncertainty: Tensor | None
    auxiliaries: Mapping[str, Tensor] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class Evaluator(Protocol):
    """Computes fixed-NFE distributional error and auxiliaries.

    Do not present entropic OT as exact W2.
    For Gaussian targets with analytical generated laws, prefer exact Gaussian W2.
    """

    @property
    def name(self) -> str:
        """Evaluator identifier."""
        ...

    def compute(
        self,
        samples: Tensor,
        reference: Tensor | Mapping[str, Tensor],
    ) -> EvaluationResult:
        """Compute the primary error and auxiliaries.

        Args:
            samples: Generated samples of shape ``(n, d)``, or analytical
                parameters packed by the concrete evaluator.
            reference: Reference samples of shape ``(m, d)`` or analytical
                moments / parameters.

        Returns:
            ``EvaluationResult`` with tensors on the sample device and dtype.

        Mathematical definition:
            Evaluator-specific distance or divergence.
        """
        ...

    def uncertainty(self, result: EvaluationResult) -> Tensor | None:
        """Return an uncertainty estimate for a prior result.

        Args:
            result: Previously computed evaluation result.

        Returns:
            Uncertainty tensor, or ``None`` if unavailable.
        """
        ...

    def metadata(self) -> Mapping[str, Any]:
        """Static evaluator documentation.

        Returns:
            Mapping with estimator class, regularization, and calibration notes.
        """
        ...
