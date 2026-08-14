"""Tests for continuous spectral regularity versus the 24-node trapezoid."""

from __future__ import annotations

import math

import pytest
import torch

from fewstep_regularities.analysis.continuous_regularity import (
    continuous_regularity,
    regularity_report,
    trapezoidal_regularity,
)
from fewstep_regularities.analysis.scalar_gaussian_counterexample import (
    linear_regularity,
    vp_regularity,
)
from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    low_rank_gaussian,
)
from fewstep_regularities.experiments.workshop_external_validation import (
    frozen_target_eigenvalues,
)

NONCENTERED_R_TARGETS = {
    "linear_R": 1.093536901895,
    "linear_R24": 1.093850806380,
    "vp_R": 0.342354218861,
    "vp_R24": 0.342535902815,
}
NONCENTERED_R_TOL = 1.0e-12


def _low_rank_eigs(dim: int) -> list[float]:
    generator = torch.Generator().manual_seed(271828)
    gaussian = low_rank_gaussian(
        dim, rank=2, noise_variance=0.05, dtype=torch.float64, generator=generator
    )
    return torch.linalg.eigvalsh(gaussian.covariance()).tolist()


@pytest.mark.analytical
def test_scalar_continuous_r_matches_closed_form() -> None:
    lin, lin_err = continuous_regularity("linear", [4.0])
    vp, vp_err = continuous_regularity("variance_preserving", [4.0])
    assert lin_err < 1e-10
    assert vp_err < 1e-8
    assert lin == pytest.approx(linear_regularity(), rel=0.0, abs=1e-12)
    assert vp == pytest.approx(vp_regularity(), rel=0.0, abs=1e-12)


@pytest.mark.analytical
def test_anisotropic_eigenvalues_and_shared_spectral_r() -> None:
    eigs2 = torch.linalg.eigvalsh(
        anisotropic_gaussian(2, anisotropy=4.0, dtype=torch.float64).covariance()
    ).tolist()
    eigs8 = torch.linalg.eigvalsh(
        anisotropic_gaussian(8, anisotropy=4.0, dtype=torch.float64).covariance()
    ).tolist()
    assert eigs2 == pytest.approx([0.5, 2.0])
    assert min(eigs8) == pytest.approx(0.5)
    assert max(eigs8) == pytest.approx(2.0)
    r2, _ = continuous_regularity("linear", eigs2)
    r8, _ = continuous_regularity("linear", eigs8)
    assert r2 == pytest.approx(r8, rel=0.0, abs=1e-12)


@pytest.mark.analytical
def test_r_ordering_agrees_with_r24_on_headline_geometries() -> None:
    geometries = {
        "scalar4": [4.0],
        "aniso2": torch.linalg.eigvalsh(
            anisotropic_gaussian(2, anisotropy=4.0, dtype=torch.float64).covariance()
        ).tolist(),
        "lowrank2": _low_rank_eigs(2),
        "lowrank8": _low_rank_eigs(8),
    }
    for name, eigs in geometries.items():
        lin = regularity_report("linear", eigs)
        vp = regularity_report("variance_preserving", eigs)
        sign_r = math.copysign(1.0, float(lin["R"]) - float(vp["R"]))
        sign_24 = math.copysign(1.0, float(lin["R24"]) - float(vp["R24"]))
        assert sign_r == sign_24, name
        assert abs(sign_r) == 1.0
        for count in (24, 48, 96, 192):
            trap = lin["trapezoidal"][count]
            assert math.isfinite(trap)


@pytest.mark.analytical
def test_low_rank_d2_covariance_is_seed_deterministic() -> None:
    cov_a = low_rank_gaussian(
        2,
        rank=2,
        noise_variance=0.05,
        dtype=torch.float64,
        generator=torch.Generator().manual_seed(271828),
    ).covariance()
    cov_b = low_rank_gaussian(
        2,
        rank=2,
        noise_variance=0.05,
        dtype=torch.float64,
        generator=torch.Generator().manual_seed(271828),
    ).covariance()
    assert torch.equal(cov_a, cov_b)
    eigs = torch.linalg.eigvalsh(cov_a)
    assert torch.all(eigs > 0)
    assert trapezoidal_regularity("linear", eigs.tolist(), 24) > 0


@pytest.mark.analytical
def test_low_rank_d8_regularity_ordering_is_opposite_to_scalar() -> None:
    eigs = _low_rank_eigs(8)
    lin, _ = continuous_regularity("linear", eigs)
    vp, _ = continuous_regularity("variance_preserving", eigs)
    assert lin < vp
    assert linear_regularity() > vp_regularity()


@pytest.mark.analytical
def test_noncentered_r_versus_rhat24_matches_published_targets() -> None:
    eigs2 = frozen_target_eigenvalues(2, torch.float64, torch.device("cpu")).tolist()
    eigs8 = frozen_target_eigenvalues(8, torch.float64, torch.device("cpu")).tolist()
    assert max(eigs2) / min(eigs2) == pytest.approx(6.0, rel=0.0, abs=1e-12)
    lin = regularity_report("linear", eigs2)
    vp = regularity_report("variance_preserving", eigs2)
    values = {
        "linear_R": float(lin["R"]),
        "linear_R24": float(lin["R24"]),
        "vp_R": float(vp["R"]),
        "vp_R24": float(vp["R24"]),
    }
    for name, expected in NONCENTERED_R_TARGETS.items():
        assert values[name] == pytest.approx(
            expected, rel=0.0, abs=NONCENTERED_R_TOL
        ), name
    lin8, _ = continuous_regularity("linear", eigs8)
    assert lin8 == pytest.approx(values["linear_R"], rel=0.0, abs=NONCENTERED_R_TOL)
