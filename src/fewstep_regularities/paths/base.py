"""Probability path protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from torch import Tensor


@runtime_checkable
class ProbabilityPath(Protocol):
    """Scalar-schedule probability path between source and target.

    Paths are classified in docs/MATHEMATICAL_NOTES.md as:
    independent coupling, deterministic transport, Gaussian OT, or
    schedule reparameterization. Do not label a path as optimal transport
    unless the coupling and displacement interpolation are valid.
    """

    def alpha(self, t: Tensor) -> Tensor:
        """Mean schedule coefficient.

        Args:
            t: Times of shape ``(...)``, values in ``[0, 1]``.

        Returns:
            ``alpha(t)`` broadcastable to ``t``, same dtype and device.

        Mathematical definition:
            Path-specific. Often ``E[x_t | x_0, x_1]`` uses ``alpha(t)``.

        References:
            See path notes after source verification.
        """
        ...

    def sigma(self, t: Tensor) -> Tensor:
        """Noise or residual schedule coefficient.

        Args:
            t: Times of shape ``(...)``, values in ``[0, 1]``.

        Returns:
            ``sigma(t)`` broadcastable to ``t``, same dtype and device.

        Mathematical definition:
            Path-specific residual scale.

        References:
            See path notes after source verification.
        """
        ...

    def alpha_derivative(self, t: Tensor) -> Tensor:
        """Time derivative of ``alpha``.

        Args:
            t: Times of shape ``(...)``.

        Returns:
            ``d alpha / dt`` broadcastable to ``t``, same dtype and device.
        """
        ...

    def sigma_derivative(self, t: Tensor) -> Tensor:
        """Time derivative of ``sigma``.

        Args:
            t: Times of shape ``(...)``.

        Returns:
            ``d sigma / dt`` broadcastable to ``t``, same dtype and device.
        """
        ...

    def marginal_sample(
        self,
        t: Tensor,
        x0: Tensor,
        x1: Tensor,
        noise: Tensor | None = None,
    ) -> Tensor:
        """Sample the path marginal or conditional bridge.

        Args:
            t: Times of shape ``(n,)`` or ``(n, 1)``.
            x0: Source samples of shape ``(n, d)``.
            x1: Target samples of shape ``(n, d)``.
            noise: Optional noise of shape ``(n, d)``.

        Returns:
            Samples ``x_t`` of shape ``(n, d)``, same dtype and device as inputs.

        Mathematical definition:
            Path-specific bridge. Document coupling type in the implementation.
        """
        ...

    def conditional_velocity(
        self,
        t: Tensor,
        x: Tensor,
        x0: Tensor,
        x1: Tensor,
    ) -> Tensor:
        """Conditional velocity given endpoints.

        Args:
            t: Times of shape ``(n,)`` or ``(n, 1)``.
            x: States of shape ``(n, d)``.
            x0: Source samples of shape ``(n, d)``.
            x1: Target samples of shape ``(n, d)``.

        Returns:
            Conditional velocities of shape ``(n, d)``.

        Mathematical definition:
            ``u_t(x | x_0, x_1)`` for the chosen path.
        """
        ...

    def marginal_velocity(
        self,
        t: Tensor,
        x: Tensor,
    ) -> Tensor | None:
        """Marginal velocity when an exact formula is available.

        Args:
            t: Times of shape ``(n,)`` or ``(n, 1)``.
            x: States of shape ``(n, d)``.

        Returns:
            Marginal velocities of shape ``(n, d)``, or ``None`` if unavailable.

        Mathematical definition:
            ``u_t(x) = E[u_t(x | x_0, x_1) | x_t = x]`` when closed form exists.
        """
        ...
