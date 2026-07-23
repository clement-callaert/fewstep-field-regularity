"""Core distribution protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import torch
from torch import Tensor


@dataclass(frozen=True)
class Moments:
    """Exact first and second moments when available.

    Attributes:
        mean: Shape ``(d,)``, dtype matches the distribution default.
        covariance: Shape ``(d, d)``, dtype matches the distribution default.
    """

    mean: Tensor
    covariance: Tensor


@runtime_checkable
class Distribution(Protocol):
    """Probability distribution interface for sources and targets.

    Implementations must use the configured default dtype (float64 for
    analytical experiments) and must not silently cast precision.
    """

    @property
    def dim(self) -> int:
        """Ambient dimension ``d``."""
        ...

    @property
    def dtype(self) -> torch.dtype:
        """Tensor dtype used by this distribution."""
        ...

    @property
    def device(self) -> torch.device:
        """Device used by this distribution."""
        ...

    def sample(self, n: int, generator: torch.Generator | None = None) -> Tensor:
        """Draw i.i.d. samples.

        Args:
            n: Number of samples.
            generator: Optional PyTorch RNG.

        Returns:
            Samples of shape ``(n, d)``, dtype and device of this distribution.

        Mathematical definition:
            ``x ~ p``.

        References:
            Implementation-specific. See docs/MATHEMATICAL_NOTES.md.
        """
        ...

    def log_prob(self, x: Tensor) -> Tensor:
        """Evaluate log density.

        Args:
            x: Points of shape ``(n, d)``, dtype and device of this distribution.

        Returns:
            Log densities of shape ``(n,)``, same dtype and device.

        Mathematical definition:
            ``log p(x)``.

        References:
            Implementation-specific.
        """
        ...

    def score(self, x: Tensor) -> Tensor:
        """Evaluate score function ``grad_x log p(x)``.

        Args:
            x: Points of shape ``(n, d)``, dtype and device of this distribution.

        Returns:
            Scores of shape ``(n, d)``, same dtype and device.

        Mathematical definition:
            ``s(x) = nabla_x log p(x)``.

        References:
            Implementation-specific. Mixture scores must use stable log-sum-exp.
        """
        ...

    def mean(self) -> Tensor:
        """Return the exact mean vector.

        Returns:
            Mean of shape ``(d,)``, dtype and device of this distribution.

        Mathematical definition:
            ``E[x]``.
        """
        ...

    def covariance(self) -> Tensor:
        """Return the exact covariance matrix.

        Returns:
            Covariance of shape ``(d, d)``, dtype and device of this distribution.

        Mathematical definition:
            ``Cov(x) = E[(x - m)(x - m)^T]``.
        """
        ...

    def analytical_moments(self) -> Moments:
        """Return exact analytical moments.

        Returns:
            ``Moments`` with mean ``(d,)`` and covariance ``(d, d)``.
        """
        ...
