"""Velocity field protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from torch import Tensor


@runtime_checkable
class VelocityField(Protocol):
    """Time-dependent velocity field ``v(t, x)``.

    Exact fields are allowed only after derivation and source checks in
    docs/MATHEMATICAL_NOTES.md.
    """

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        """Evaluate the velocity field.

        Args:
            t: Times of shape ``(n,)`` or ``(n, 1)``.
            x: States of shape ``(n, d)``.

        Returns:
            Velocities of shape ``(n, d)``, same dtype and device as ``x``.

        Mathematical definition:
            ``v(t, x)`` for the registered path and distributions.

        References:
            Implementation-specific. Cite source equations in notes.
        """
        ...

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        """Evaluate the spatial Jacobian.

        Args:
            t: Times of shape ``(n,)`` or ``(n, 1)``.
            x: States of shape ``(n, d)``.

        Returns:
            Jacobians of shape ``(n, d, d)``, same dtype and device as ``x``.

        Mathematical definition:
            ``J(t, x) = D_x v(t, x)``.
        """
        ...

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Evaluate ``partial_t v`` when available.

        Args:
            t: Times of shape ``(n,)`` or ``(n, 1)``.
            x: States of shape ``(n, d)``.

        Returns:
            Time derivatives of shape ``(n, d)``, or ``None`` if unavailable.

        Mathematical definition:
            ``partial_t v(t, x)`` at fixed ``x``.
        """
        ...
