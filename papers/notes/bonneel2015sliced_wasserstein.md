# Sliced and Radon Wasserstein Barycenters of Measures

- paper_id: `bonneel2015sliced_wasserstein`
- authors: Nicolas Bonneel, Julien Rabin, Gabriel Peyre, Hanspeter Pfister
- year: 2015
- source_url: https://hal.archives-ouvertes.fr/hal-00881872
- pdf_url: https://perso.liris.cnrs.fr/nicolas.bonneel/WassersteinSliced-JMIV.pdf
- local_filename: bonneel2015sliced_wasserstein.pdf
- access_date: 2026-07-23
- sha256: see papers/manifest.json

## Retrieval note

The previous catalog URL `arXiv:1308.2074` pointed to a different paper
(gravitational-wave detectors). The correct public PDF is the author copy
linked above (HAL hal-00881872).

## Relevance

Sliced Wasserstein distance and Monte Carlo projection estimator used for
empirical distributional error when exact W2 is unavailable.

## Formulas or results needed

- sliced Wasserstein definition
- projection estimator
- 1-D Wasserstein closed form via sorting / quantile matching

## Notation differences

- Paper uses `WR` for 1-D Wasserstein and `SWRd` for sliced W2 on `Rd`.
- Project uses `projected_w2` for one direction and `sliced_wasserstein` for
  the Monte Carlo average over directions.
- Paper normalizes the sphere measure so `integral_{S^{d-1}} dθ = 1`.

## Assumptions to check

- input measures are probability measures on `Rd`
- for equal-weight discrete clouds, 1-D W2 uses sorted projections
- Monte Carlo estimator replaces the sphere integral by a finite set `Θ`

## Project satisfies assumptions?

Yes for empirical equal-weight samples. Unequal weights need weighted 1-D OT
(not used in Phase 2 calibration defaults).

## Replication status

formulas-extracted-phase2

## Extracted equations

Source: local PDF pages 7-8 (section 4.1).

Sliced Wasserstein distance (30)-(31):

`SW_{Rd}(μ_1, μ_2)^2 = W_{Ω_d}(R μ_1, R μ_2)^2`

`= ∫_{S^{d-1}} W_R(P_θ♯ μ_1, P_θ♯ μ_2)^2 dθ`

with `dθ` the uniform probability measure on the unit sphere.

Finite-direction Monte Carlo estimator (page 8, energy `E_Θ`):

`(1/|Θ|) ∑_{θ ∈ Θ} W_R(P_θ♯ μ_1, P_θ♯ μ_2)^2`

For equal-weight discrete measures, 1-D `W_R` between projected samples uses
sorting / quantile matching (section 2.3, cumulative inverse formulas (16)-(18);
Lagrangian discrete case uses sorted projections as in Theorem 1).

Do not present sliced Wasserstein as exact `W_2` on `Rd`.
