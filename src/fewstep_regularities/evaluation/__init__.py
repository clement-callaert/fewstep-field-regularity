"""Distributional evaluators."""

from fewstep_regularities.evaluation.base import EvaluationResult, Evaluator
from fewstep_regularities.evaluation.gaussian_w2 import (
    GaussianW2Evaluator,
    gaussian_w2,
    gaussian_w2_squared,
)
from fewstep_regularities.evaluation.projected_sliced import (
    DiscreteOTEvaluator,
    EntropicOTEvaluator,
    ProjectedW2Evaluator,
    SlicedWassersteinEvaluator,
)

__all__ = [
    "DiscreteOTEvaluator",
    "EntropicOTEvaluator",
    "EvaluationResult",
    "Evaluator",
    "GaussianW2Evaluator",
    "ProjectedW2Evaluator",
    "SlicedWassersteinEvaluator",
    "gaussian_w2",
    "gaussian_w2_squared",
]
