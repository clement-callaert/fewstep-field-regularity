"""Exact Gaussian distributions."""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor

from fewstep_regularities.distributions.base import Moments
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_finite, assert_shape


def _symmetrize(matrix: Tensor) -> Tensor:
    """Return a symmetric copy of a square matrix."""
    return 0.5 * (matrix + matrix.transpose(-1, -2))


def _cpu() -> torch.device:
    return torch.device("cpu")


@dataclass
class Gaussian:
    """Full-covariance Gaussian ``N(mean, covariance)``.

    Attributes:
        mean_vec: Shape ``(d,)``.
        cov: Shape ``(d, d)``, symmetric positive definite.
        _dtype: Tensor dtype (default float64).
        _device: Tensor device.
    """

    mean_vec: Tensor
    cov: Tensor
    _dtype: torch.dtype = DEFAULT_DTYPE
    _device: torch.device = field(default_factory=_cpu)

    def __post_init__(self) -> None:
        assert_dtype(self.mean_vec, self._dtype, "mean")
        assert_dtype(self.cov, self._dtype, "covariance")
        assert_device(self.mean_vec, self._device, "mean")
        assert_device(self.cov, self._device, "covariance")
        self.cov = _symmetrize(self.cov)
        assert_shape(self.mean_vec, (None,), "mean")
        d = int(self.mean_vec.shape[0])
        assert_shape(self.cov, (d, d), "covariance")
        # Check positive definite via Cholesky.
        torch.linalg.cholesky(self.cov)

    @property
    def dim(self) -> int:
        """Ambient dimension ``d``."""
        return int(self.mean_vec.shape[0])

    @property
    def dtype(self) -> torch.dtype:
        """Tensor dtype."""
        return self._dtype

    @property
    def device(self) -> torch.device:
        """Tensor device."""
        return self._device

    def sample(self, n: int, generator: torch.Generator | None = None) -> Tensor:
        """Draw i.i.d. samples of shape ``(n, d)``.

        Mathematical definition:
            ``x ~ N(m, Σ)``.
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        eps = torch.randn(
            n,
            self.dim,
            dtype=self._dtype,
            device=self._device,
            generator=generator,
        )
        chol = torch.linalg.cholesky(self.cov)
        samples: Tensor = self.mean_vec.unsqueeze(0) + eps @ chol.transpose(0, 1)
        return samples

    def log_prob(self, x: Tensor) -> Tensor:
        """Log density of shape ``(n,)``.

        Mathematical definition:
            ``log N(x; m, Σ)``.
        """
        assert_dtype(x, self._dtype, "x")
        assert_device(x, self._device, "x")
        assert_shape(x, (None, self.dim), "x")
        delta = x - self.mean_vec.unsqueeze(0)
        chol = torch.linalg.cholesky(self.cov)
        # Solve L y = delta^T.
        y = torch.linalg.solve_triangular(chol, delta.transpose(0, 1), upper=False)
        mahal = torch.sum(y * y, dim=0)
        log_det = 2.0 * torch.sum(torch.log(torch.diag(chol)))
        d = float(self.dim)
        log_two_pi = torch.log(
            torch.tensor(2.0 * torch.pi, dtype=self._dtype, device=self._device)
        )
        return -0.5 * (mahal + log_det + d * log_two_pi)

    def score(self, x: Tensor) -> Tensor:
        """Score ``∇ log p(x)`` of shape ``(n, d)``.

        Mathematical definition:
            ``s(x) = -Σ^{-1} (x - m)``.
        """
        assert_dtype(x, self._dtype, "x")
        assert_device(x, self._device, "x")
        assert_shape(x, (None, self.dim), "x")
        delta = x - self.mean_vec.unsqueeze(0)
        # Solve Σ s^T = -(x-m)^T via Cholesky.
        chol = torch.linalg.cholesky(self.cov)
        sol = torch.cholesky_solve(delta.transpose(0, 1), chol)
        out = -sol.transpose(0, 1)
        assert_finite(out, "score")
        return out

    def mean(self) -> Tensor:
        """Exact mean of shape ``(d,)``."""
        return self.mean_vec

    def covariance(self) -> Tensor:
        """Exact covariance of shape ``(d, d)``."""
        return self.cov

    def analytical_moments(self) -> Moments:
        """Exact analytical moments."""
        return Moments(mean=self.mean_vec, covariance=self.cov)


def standard_gaussian(
    dim: int,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
) -> Gaussian:
    """Standard Gaussian ``N(0, I_d)``."""
    if dim < 1:
        raise ValueError("dim must be positive")
    dev = device or torch.device("cpu")
    mean = torch.zeros(dim, dtype=dtype, device=dev)
    cov = torch.eye(dim, dtype=dtype, device=dev)
    return Gaussian(mean_vec=mean, cov=cov, _dtype=dtype, _device=dev)


def anisotropic_gaussian(
    dim: int,
    anisotropy: float = 4.0,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
) -> Gaussian:
    """Diagonal Gaussian with geometric anisotropy.

    Eigenvalues form a geometric sequence from ``1/sqrt(a)`` to ``sqrt(a)``
    where ``a`` is ``anisotropy``, so the condition number is ``a``.
    """
    if dim < 1:
        raise ValueError("dim must be positive")
    if anisotropy <= 0:
        raise ValueError("anisotropy must be positive")
    dev = device or torch.device("cpu")
    if dim == 1:
        ev = torch.tensor([1.0], dtype=dtype, device=dev)
    else:
        log_min = -0.5 * torch.log(torch.tensor(anisotropy, dtype=dtype, device=dev))
        log_max = 0.5 * torch.log(torch.tensor(anisotropy, dtype=dtype, device=dev))
        ev = torch.exp(torch.linspace(log_min, log_max, dim, dtype=dtype, device=dev))
    mean = torch.zeros(dim, dtype=dtype, device=dev)
    cov = torch.diag(ev)
    return Gaussian(mean_vec=mean, cov=cov, _dtype=dtype, _device=dev)


def low_rank_gaussian(
    dim: int,
    rank: int = 2,
    noise_variance: float = 0.05,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
    generator: torch.Generator | None = None,
) -> Gaussian:
    """Gaussian with covariance ``F F^T + noise_variance I``.

    ``F`` has shape ``(d, rank)`` with i.i.d. standard normal entries.
    """
    if dim < 1:
        raise ValueError("dim must be positive")
    if rank < 1 or rank > dim:
        raise ValueError("rank must be in 1..dim")
    if noise_variance <= 0:
        raise ValueError("noise_variance must be positive")
    dev = device or torch.device("cpu")
    factor = torch.randn(dim, rank, dtype=dtype, device=dev, generator=generator)
    cov = factor @ factor.transpose(0, 1) + noise_variance * torch.eye(
        dim, dtype=dtype, device=dev
    )
    mean = torch.zeros(dim, dtype=dtype, device=dev)
    return Gaussian(mean_vec=mean, cov=cov, _dtype=dtype, _device=dev)
