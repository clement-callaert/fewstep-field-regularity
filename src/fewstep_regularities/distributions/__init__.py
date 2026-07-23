"""Probability distributions used as sources and targets."""

from fewstep_regularities.distributions.base import Distribution, Moments
from fewstep_regularities.distributions.gaussian import (
    Gaussian,
    anisotropic_gaussian,
    low_rank_gaussian,
    standard_gaussian,
)
from fewstep_regularities.distributions.gaussian_mixture import (
    GaussianMixture,
    eight_mode_gmm,
    imbalanced_gmm,
    two_mode_gmm,
)

__all__ = [
    "Distribution",
    "Gaussian",
    "GaussianMixture",
    "Moments",
    "anisotropic_gaussian",
    "eight_mode_gmm",
    "imbalanced_gmm",
    "low_rank_gaussian",
    "standard_gaussian",
    "two_mode_gmm",
]
