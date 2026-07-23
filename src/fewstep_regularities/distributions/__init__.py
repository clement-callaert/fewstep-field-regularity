"""Probability distributions used as sources and targets."""

from fewstep_regularities.distributions.base import Distribution, Moments
from fewstep_regularities.distributions.gaussian import (
    Gaussian,
    anisotropic_gaussian,
    low_rank_gaussian,
    standard_gaussian,
)

__all__ = [
    "Distribution",
    "Gaussian",
    "Moments",
    "anisotropic_gaussian",
    "low_rank_gaussian",
    "standard_gaussian",
]
