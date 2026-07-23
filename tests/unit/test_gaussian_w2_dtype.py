"""Unit tests for Gaussian W2 dtype policy."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator


def test_w2_rejects_silent_dtype_cast() -> None:
    ev = GaussianW2Evaluator(dtype=torch.float64)
    mean = torch.zeros(2, dtype=torch.float32)
    cov = torch.eye(2, dtype=torch.float32)
    with pytest.raises(TypeError, match="dtype"):
        ev.compute(
            {"mean": mean, "covariance": cov},
            {"mean": mean, "covariance": cov},
        )
