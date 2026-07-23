"""Exact Gaussian mixture distributions."""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor

from fewstep_regularities.distributions.base import Moments
from fewstep_regularities.distributions.gaussian import Gaussian, _symmetrize
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_finite, assert_shape


def _cpu() -> torch.device:
    return torch.device("cpu")


@dataclass
class GaussianMixture:
    """Finite Gaussian mixture ``∑_k π_k N(μ_k, Σ_k)``.

    Attributes:
        weights: Shape ``(K,)``, positive and summing to 1.
        means: Shape ``(K, d)``.
        covs: Shape ``(K, d, d)``, each SPD.
    """

    weights: Tensor
    means: Tensor
    covs: Tensor
    _dtype: torch.dtype = DEFAULT_DTYPE
    _device: torch.device = field(default_factory=_cpu)

    def __post_init__(self) -> None:
        assert_dtype(self.weights, self._dtype, "weights")
        assert_dtype(self.means, self._dtype, "means")
        assert_dtype(self.covs, self._dtype, "covs")
        assert_device(self.weights, self._device, "weights")
        assert_device(self.means, self._device, "means")
        assert_device(self.covs, self._device, "covs")
        self.covs = _symmetrize(self.covs)
        assert_shape(self.weights, (None,), "weights")
        k = int(self.weights.shape[0])
        if k < 1:
            raise ValueError("mixture needs at least one component")
        assert_shape(self.means, (k, None), "means")
        d = int(self.means.shape[1])
        assert_shape(self.covs, (k, d, d), "covs")
        if torch.any(self.weights <= 0):
            raise ValueError("weights must be positive")
        weight_sum = float(self.weights.sum().item())
        if abs(weight_sum - 1.0) > 1e-10:
            raise ValueError(f"weights must sum to 1, got {weight_sum}")
        for i in range(k):
            torch.linalg.cholesky(self.covs[i])

    @property
    def n_components(self) -> int:
        """Number of mixture components ``K``."""
        return int(self.weights.shape[0])

    @property
    def dim(self) -> int:
        """Ambient dimension ``d``."""
        return int(self.means.shape[1])

    @property
    def dtype(self) -> torch.dtype:
        """Tensor dtype."""
        return self._dtype

    @property
    def device(self) -> torch.device:
        """Tensor device."""
        return self._device

    def component(self, index: int) -> Gaussian:
        """Return component ``index`` as a ``Gaussian``."""
        if index < 0 or index >= self.n_components:
            raise IndexError("component index out of range")
        return Gaussian(
            mean_vec=self.means[index],
            cov=self.covs[index],
            _dtype=self._dtype,
            _device=self._device,
        )

    def sample(self, n: int, generator: torch.Generator | None = None) -> Tensor:
        """Draw i.i.d. samples of shape ``(n, d)``.

        Mathematical definition:
            sample component ``k ~ Categorical(π)``, then ``x ~ N(μ_k, Σ_k)``.
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return torch.empty(0, self.dim, dtype=self._dtype, device=self._device)
        # Sample component indices.
        idx = torch.multinomial(self.weights, n, replacement=True, generator=generator)
        eps = torch.randn(
            n, self.dim, dtype=self._dtype, device=self._device, generator=generator
        )
        out = torch.empty(n, self.dim, dtype=self._dtype, device=self._device)
        for k in range(self.n_components):
            mask = idx == k
            if not bool(mask.any()):
                continue
            chol = torch.linalg.cholesky(self.covs[k])
            out[mask] = self.means[k].unsqueeze(0) + eps[mask] @ chol.transpose(0, 1)
        return out

    def component_log_probs(self, x: Tensor) -> Tensor:
        """Per-component log densities of shape ``(n, K)``.

        Mathematical definition:
            ``log N(x; μ_k, Σ_k)`` for each ``k``.
        """
        assert_dtype(x, self._dtype, "x")
        assert_device(x, self._device, "x")
        assert_shape(x, (None, self.dim), "x")
        n = int(x.shape[0])
        logs = torch.empty(n, self.n_components, dtype=self._dtype, device=self._device)
        for k in range(self.n_components):
            logs[:, k] = self.component(k).log_prob(x)
        return logs

    def responsibilities(self, x: Tensor) -> Tensor:
        """Posterior component weights of shape ``(n, K)``.

        Mathematical definition:
            ``r_k(x) = softmax_k(log π_k + log N_k(x))``.
        """
        log_comp = self.component_log_probs(x)
        log_joint = log_comp + torch.log(self.weights).unsqueeze(0)
        return torch.softmax(log_joint, dim=1)

    def log_prob(self, x: Tensor) -> Tensor:
        """Log density of shape ``(n,)``.

        Mathematical definition:
            ``log ∑_k π_k N(x; μ_k, Σ_k)`` via stable log-sum-exp.
        """
        log_comp = self.component_log_probs(x)
        log_joint = log_comp + torch.log(self.weights).unsqueeze(0)
        return torch.logsumexp(log_joint, dim=1)

    def score(self, x: Tensor) -> Tensor:
        """Score ``∇ log p(x)`` of shape ``(n, d)``.

        Mathematical definition:
            ``∑_k r_k(x) (-Σ_k^{-1}(x - μ_k))`` with stable responsibilities.
        """
        assert_dtype(x, self._dtype, "x")
        assert_device(x, self._device, "x")
        assert_shape(x, (None, self.dim), "x")
        resp = self.responsibilities(x)
        score = torch.zeros_like(x)
        for k in range(self.n_components):
            s_k = self.component(k).score(x)
            score = score + resp[:, k : k + 1] * s_k
        assert_finite(score, "mixture score")
        return score

    def mean(self) -> Tensor:
        """Exact mean ``∑_k π_k μ_k`` of shape ``(d,)``."""
        return torch.sum(self.weights.unsqueeze(1) * self.means, dim=0)

    def covariance(self) -> Tensor:
        """Exact covariance of shape ``(d, d)``.

        Mathematical definition:
            ``∑_k π_k (Σ_k + μ_k μ_k^T) - m m^T``.
        """
        m = self.mean()
        second = torch.zeros(self.dim, self.dim, dtype=self._dtype, device=self._device)
        for k in range(self.n_components):
            mu = self.means[k]
            second = second + self.weights[k] * (self.covs[k] + torch.outer(mu, mu))
        return _symmetrize(second - torch.outer(m, m))

    def analytical_moments(self) -> Moments:
        """Exact analytical moments."""
        return Moments(mean=self.mean(), covariance=self.covariance())


def _normalize_weights(raw: Tensor) -> Tensor:
    """Normalize positive weights to sum to one."""
    if torch.any(raw <= 0):
        raise ValueError("raw weights must be positive")
    return raw / raw.sum()


def two_mode_gmm(
    dim: int,
    separation: float = 2.0,
    component_std: float = 0.5,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
) -> GaussianMixture:
    """Equal-weight two-mode mixture on the first axis."""
    if dim < 1:
        raise ValueError("dim must be positive")
    if separation <= 0 or component_std <= 0:
        raise ValueError("separation and component_std must be positive")
    dev = device or torch.device("cpu")
    means = torch.zeros(2, dim, dtype=dtype, device=dev)
    means[0, 0] = -separation
    means[1, 0] = separation
    cov = (component_std**2) * torch.eye(dim, dtype=dtype, device=dev)
    covs = torch.stack([cov, cov], dim=0)
    weights = torch.tensor([0.5, 0.5], dtype=dtype, device=dev)
    return GaussianMixture(
        weights=weights, means=means, covs=covs, _dtype=dtype, _device=dev
    )


def eight_mode_gmm(
    dim: int,
    radius: float = 2.0,
    component_std: float = 0.35,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
) -> GaussianMixture:
    """Equal-weight eight-mode mixture on a circle in the first two coords.

    For ``dim == 1``, uses eight points on the line. For ``dim >= 2``, places
    modes on a circle in the ``(e_0, e_1)`` plane and zeros elsewhere.
    """
    if dim < 1:
        raise ValueError("dim must be positive")
    if radius <= 0 or component_std <= 0:
        raise ValueError("radius and component_std must be positive")
    dev = device or torch.device("cpu")
    k = 8
    means = torch.zeros(k, dim, dtype=dtype, device=dev)
    angles = torch.linspace(0, 2 * torch.pi, k + 1, dtype=dtype, device=dev)[:-1]
    if dim == 1:
        means[:, 0] = radius * torch.cos(angles)
    else:
        means[:, 0] = radius * torch.cos(angles)
        means[:, 1] = radius * torch.sin(angles)
    cov = (component_std**2) * torch.eye(dim, dtype=dtype, device=dev)
    covs = cov.unsqueeze(0).expand(k, dim, dim).clone()
    weights = torch.full((k,), 1.0 / k, dtype=dtype, device=dev)
    return GaussianMixture(
        weights=weights, means=means, covs=covs, _dtype=dtype, _device=dev
    )


def imbalanced_gmm(
    dim: int,
    weight_ratio: float = 9.0,
    separation: float = 2.0,
    component_std: float = 0.5,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
) -> GaussianMixture:
    """Two-mode mixture with weight ratio ``weight_ratio : 1``."""
    if weight_ratio <= 0:
        raise ValueError("weight_ratio must be positive")
    mix = two_mode_gmm(
        dim,
        separation=separation,
        component_std=component_std,
        dtype=dtype,
        device=device,
    )
    raw = torch.tensor([weight_ratio, 1.0], dtype=dtype, device=mix.device)
    weights = _normalize_weights(raw)
    return GaussianMixture(
        weights=weights,
        means=mix.means,
        covs=mix.covs,
        _dtype=dtype,
        _device=mix.device,
    )
