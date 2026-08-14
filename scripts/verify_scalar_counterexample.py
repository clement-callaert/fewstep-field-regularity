"""Command-line verification of the scalar Gaussian counterexample."""

from __future__ import annotations

import json

from fewstep_regularities.analysis.scalar_gaussian_counterexample import (
    certify,
    float64_crosscheck,
    high_precision_crosscheck,
    linear_heun_endpoint_factor,
    linear_heun_step_factors,
    linear_regularity,
    vp_regularity,
)


def main() -> None:
    result = certify(dps=40)
    payload = {
        "linear_regularity": linear_regularity(),
        "vp_regularity": vp_regularity(),
        "linear_heun_steps": [str(v) for v in linear_heun_step_factors()],
        "linear_heun_factor": str(linear_heun_endpoint_factor()),
        "linear_w2": str(result.linear_w2),
        "vp_rational_upper": str(result.vp_rational_upper),
        "vp_integer_certificate": [result.vp_integer_left, result.vp_integer_right],
        "vp_factor_interval_crosscheck": list(result.vp_factor_interval),
        "vp_w2_interval_crosscheck": list(result.vp_w2_interval),
        "mpmath_version": result.mpmath_version,
        "ranking_inverted": result.ranking_inverted,
        "float64": float64_crosscheck(),
        "mpmath_80digit": high_precision_crosscheck(dps=80),
        "software": result.software,
    }
    print(json.dumps(payload, indent=2))
    if not result.ranking_inverted:
        raise SystemExit("certification failed")


if __name__ == "__main__":
    main()
