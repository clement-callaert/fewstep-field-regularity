"""Regularity metric protocol."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from torch import Tensor

from fewstep_regularities.fields.base import VelocityField


@dataclass(frozen=True)
class MetricResult:
    """Scalar regularity estimate with estimator metadata.

    Attributes:
        value: Estimated metric value (scalar tensor).
        is_exact: True only for closed-form quantities, never for sampled bounds.
        estimator_name: Name of the estimator or exact formula.
        n_samples: Sample budget used by the estimator, if any.
        uncertainty: Optional uncertainty estimate.
        metadata: Additional estimator details.
    """

    value: Tensor
    is_exact: bool
    estimator_name: str
    n_samples: int | None = None
    uncertainty: Tensor | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class RegularityMetric(Protocol):
    """Field regularity metric.

    Do not call a sampled lower bound a global Lipschitz constant.
    Prefer names such as sampled maximum Jacobian norm.
    """

    @property
    def name(self) -> str:
        """Metric identifier."""
        ...

    def required_quantities(self) -> Sequence[str]:
        """Names of quantities required from the field and path.

        Returns:
            Sequence such as ``(\"jacobian\", \"time_derivative\")``.
        """
        ...

    def estimator_metadata(self) -> Mapping[str, Any]:
        """Return static estimator documentation.

        Returns:
            Mapping describing definition, sampling distribution, time
            weighting, matrix norm, approximation method, tolerances.
        """
        ...

    def compute(
        self,
        field: VelocityField,
        times: Tensor,
        states: Tensor,
    ) -> MetricResult:
        """Estimate the regularity metric along a path sample.

        Args:
            field: Velocity field.
            times: Times of shape ``(m,)`` or ``(m, 1)``.
            states: States of shape ``(m, n, d)`` or ``(n, d)``.

        Returns:
            ``MetricResult`` with value dtype matching inputs.

        Mathematical definition:
            Metric-specific. Document exact vs estimator status.
        """
        ...
