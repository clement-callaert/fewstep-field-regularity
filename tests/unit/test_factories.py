"""Unit tests for experiment factories."""

from __future__ import annotations

import pytest

from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    standard_gaussian,
)
from fewstep_regularities.experiments.factories import build_path, effective_m
from fewstep_regularities.paths.lipschitz_guided import LipschitzGuidedPath


def test_effective_m_anisotropic_not_one() -> None:
    tgt = anisotropic_gaussian(8, anisotropy=4.0)
    m = effective_m(tgt)
    assert abs(m - 1.0) > 1e-6
    assert m == pytest.approx(2.0, rel=1e-10)


def test_lipschitz_path_builds_for_anisotropic() -> None:
    src = standard_gaussian(4)
    tgt = anisotropic_gaussian(4, anisotropy=4.0)
    path = build_path({"name": "lipschitz_guided"}, src, tgt, src.dtype)
    assert isinstance(path, LipschitzGuidedPath)
    assert abs(path.m - 1.0) > 1e-6
