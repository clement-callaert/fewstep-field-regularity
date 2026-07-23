"""Distributional evaluators."""

from fewstep_regularities.evaluation.base import EvaluationResult, Evaluator
from fewstep_regularities.evaluation.gaussian_w2 import (
    GaussianW2Evaluator,
    gaussian_w2,
    gaussian_w2_squared,
)

__all__ = [
    "EvaluationResult",
    "Evaluator",
    "GaussianW2Evaluator",
    "gaussian_w2",
    "gaussian_w2_squared",
]
