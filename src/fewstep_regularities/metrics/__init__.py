"""Regularity metrics."""

from fewstep_regularities.metrics.affine_gaussian import (
    AveragedSquaredLipschitzProxy,
    ExpectedSquaredJacobianNorm,
    JacobianTemporalVariation,
    LagrangianAcceleration,
    MaxSampledSpectralJacobianNorm,
    PathWeightedExpectedJacobianNorm,
    SpatialTemporalStiffness,
    TemporalFieldDerivativeNorm,
)
from fewstep_regularities.metrics.base import MetricResult, RegularityMetric

__all__ = [
    "AveragedSquaredLipschitzProxy",
    "ExpectedSquaredJacobianNorm",
    "JacobianTemporalVariation",
    "LagrangianAcceleration",
    "MaxSampledSpectralJacobianNorm",
    "MetricResult",
    "PathWeightedExpectedJacobianNorm",
    "RegularityMetric",
    "SpatialTemporalStiffness",
    "TemporalFieldDerivativeNorm",
]
