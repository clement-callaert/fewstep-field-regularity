"""Affine map and Gaussian moment propagation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from torch import Tensor

from fewstep_regularities.utils.precision import assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_shape


@dataclass(frozen=True)
class AffineMapResult:
    """Recovered endpoint map and solver accounting."""

    matrix: Tensor
    offset: Tensor
    actual_nfe: int
    n_steps: int
    wall_clock_s: float


def recover_affine_solver_map(
    field: Any,
    solver: Any,
    *,
    dim: int,
    dtype: torch.dtype,
    device: torch.device,
    requested_nfe: int,
) -> AffineMapResult:
    """Recover the numerical endpoint map from zero and basis probes."""
    if dim < 1:
        raise ValueError("dim must be positive")
    if requested_nfe < 1:
        raise ValueError("requested_nfe must be positive")
    probes = torch.cat(
        (
            torch.zeros((1, dim), dtype=dtype, device=device),
            torch.eye(dim, dtype=dtype, device=device),
        ),
        dim=0,
    )
    solved = solver.solve(field, probes, 0.0, 1.0, requested_nfe=requested_nfe)
    endpoint = solved.trajectory[-1]
    offset = endpoint[0]
    matrix = (endpoint[1:] - offset.unsqueeze(0)).T
    assert_shape(matrix, (dim, dim), "matrix")
    assert_shape(offset, (dim,), "offset")
    return AffineMapResult(
        matrix=matrix,
        offset=offset,
        actual_nfe=solved.actual_nfe,
        n_steps=solved.n_steps,
        wall_clock_s=solved.wall_clock_s,
    )


def propagate_gaussian_moments(
    affine_map: AffineMapResult,
    source_mean: Tensor,
    source_covariance: Tensor,
) -> tuple[Tensor, Tensor]:
    """Propagate Gaussian moments through an affine map."""
    if not source_mean.is_floating_point() or not source_covariance.is_floating_point():
        raise TypeError("Gaussian moments must have a floating dtype")
    assert_dtype(source_covariance, source_mean.dtype, "source_covariance")
    assert_dtype(affine_map.matrix, source_mean.dtype, "matrix")
    assert_dtype(affine_map.offset, source_mean.dtype, "offset")
    assert_device(source_covariance, source_mean.device, "source_covariance")
    assert_device(affine_map.matrix, source_mean.device, "matrix")
    assert_device(affine_map.offset, source_mean.device, "offset")
    assert_shape(source_mean, (None,), "source_mean")
    dim = source_mean.shape[0]
    assert_shape(source_covariance, (dim, dim), "source_covariance")
    assert_shape(affine_map.matrix, (dim, dim), "matrix")
    assert_shape(affine_map.offset, (dim,), "offset")
    mean = affine_map.matrix @ source_mean + affine_map.offset
    covariance = (
        affine_map.matrix @ source_covariance @ affine_map.matrix.transpose(0, 1)
    )
    covariance = 0.5 * (covariance + covariance.transpose(0, 1))
    return mean, covariance
