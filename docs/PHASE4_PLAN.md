# Phase 4 plan

Status: Active. Run 1 completed and passed its reproduction checks.

Scope: Explain the surviving Phase 3 ranking inversions in the anisotropic
Gaussian and low-rank Gaussian families. This plan does not authorize Phase 5,
a full Cartesian benchmark, new target families, or decisive use of dimension
8 mixture results.

Artifact IDs used:

- `phase3_gate_registered_2026-07-23-v1:gate_results`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:inversions`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:interactions`

The Phase 3 artifacts have dirty-code provenance. They are comparison inputs
only. They are not release-ready sources.

## Research questions

The primary question is why an averaged field regularity metric can order two
probability paths oppositely from their fixed-NFE Gaussian Wasserstein error.

The secondary question is why the preferred path can change between Euler,
Heun, and RK4 under equal NFE.

Phase 4 seeks a mathematical mechanism or a rigorous negative conclusion. It
does not seek another correlation result.

## Analysis classes

The clean Gaussian reproduction is a pre-specified Phase 4 check. It tests
P4-C1 and P4-C2 on the Phase 3 Gaussian grid without changing the registered
Phase 3 gate.

The following analyses are post-hoc diagnostics:

- material derivative norms
- temporal variation of the affine matrix
- solver-specific local error proxies
- mean and covariance error decomposition
- eigenvalue-wise propagation error
- time-local contributions to endpoint error

These diagnostics will remain labeled post-hoc. They will not be added to the
registered hypothesis list or used to claim predictive superiority on the
same configurations that motivated them.

## Observation and interpretation

The audited Phase 3 observation is that stable baseline ranking inversions
occur in both exact Gaussian families. In the low-rank Gaussian family,
variance-preserving is preferred for Euler, while linear is preferred for
Heun and RK4 at dimensions 2 and 8 and NFE 8, 16, and 32.

The possible explanation based on solver order is an interpretation. It is
not yet a derivation, proposition, or supported claim.

Gaussian Wasserstein distance in this scope is computed from analytically
propagated Gaussian moments. The baseline time integral uses numerical
quadrature and is not called a symbolic exact quantity.

## Clean-code gate

No scientific run may start until all of these conditions hold:

1. Review every current tracked and untracked source change.
2. Preserve superseded and invalidated analyses.
3. Commit the reviewed Phase 3 code and Phase 4 planning files.
4. Confirm `git status --short` is empty.
5. Record the full Git commit in the session log.
6. Run the full CPU test suite.
7. Run Ruff lint and format checks.
8. Run MyPy.
9. Run pre-commit on all files.
10. Confirm that the Phase 4 runner rejects dirty release-ready runs.
11. Resolve the Phase 4 Hydra config and verify every listed input.

The clean-code gate passed at commit `083dbf9a14e73f3211daf9851909160467b8c3ee`.
Run 1 was executed from that clean commit. Later analysis code must pass the
same gate from a new clean commit before Run 2.

## Run 1: clean Gaussian reproduction

Configuration:
[`configs/experiment/phase4_gaussian_reproduction.yaml`](../configs/experiment/phase4_gaussian_reproduction.yaml)

Artifact policy:
[`configs/artifact_policy/phase4_release_ready.yaml`](../configs/artifact_policy/phase4_release_ready.yaml)

Run ID: `phase4_gaussian_reproduction_2026-07-24-v1`

The exact grid is:

- families: anisotropic Gaussian and low-rank Gaussian
- dimensions: 2 and 8
- paths: linear and variance-preserving
- solvers: Euler, Heun, and RK4
- NFE: 8, 16, and 32
- dtype: float64
- device: CPU
- target geometry seed: 271828

This gives 72 endpoint configurations. Gaussian endpoint error has no particle
or projection estimator. The baseline metric uses 24 time points and the
registered estimator budget field of 128, even though the affine Gaussian
calculation does not require state sampling.

Equal NFE means:

| solver | evaluations per step | steps at NFE 8, 16, 32 |
| --- | ---: | --- |
| Euler | 1 | 8, 16, 32 |
| Heun | 2 | 4, 8, 16 |
| RK4 | 4 | 2, 4, 8 |

The run must save the numerical affine map, propagated mean, propagated
covariance, exact Gaussian Wasserstein value, actual NFE, condition number,
covariance eigenvalue range, source hashes, and complete run provenance.

### Runtime decision

The larger Phase 3 run completed in 68.394967 seconds on the recorded CPU
environment and included mixture sampling plus 17,568 joined rows. The
focused reproduction has 72 deterministic endpoint configurations.

The conservative estimate is under 10 minutes. The hard stop is 45 minutes.
This is expected to satisfy the required limit. The runner must stop before
launch if its resolved configuration differs from the 72 configurations
listed above.

### Validation and stop rule

After the run:

1. Validate the manifest and every checksum.
2. Confirm clean Git provenance and release-ready status.
3. Confirm covariance symmetry and positive semidefiniteness.
4. Confirm exact endpoint target moments for the continuous affine flow.
5. Confirm requested NFE equals actual NFE.
6. Compare each Gaussian row with the exact Phase 3 input row.
7. Record inversion margins and reproduction tolerances.
8. Update the session log.
9. Stop before Run 2.

If a decisive inversion does not reproduce, stop Phase 4 and investigate.

## Mathematical workstream

The analysis will use
[`docs/PHASE4_MATHEMATICAL_ANALYSIS.md`](PHASE4_MATHEMATICAL_ANALYSIS.md).
For an affine field

\[
b(t,x)=A(t)x+c(t),
\]

the document will define the time-dependent matrix \(A(t)\), vector \(c(t)\),
state transition matrix, exact mean and covariance dynamics, and each
fixed-step solver map. It will separate standard identities, source-verified
steps, original derivations, and numerical checks.

The Euler material derivative target is

\[
\partial_t b(t,x)+J(t,x)b(t,x)
=\left(A'(t)+A(t)^2\right)x
+c'(t)+A(t)c(t),
\]

where \(J(t,x)=A(t)\). This displayed identity is a derivation target and is
not assigned theorem status here.

Heun and RK4 expressions will be derived only after checking an authoritative
numerical ODE source. Candidate source machinery includes the standard
Runge-Kutta order conditions and local truncation analysis in
[Hairer, Norsett, and Wanner, Solving Ordinary Differential Equations I](https://doi.org/10.1007/978-3-540-78862-1).
The exact section and equation remain to be recorded in the literature audit.

Allowed derivation statuses are sketch, partially verified, source verified,
symbolically checked, numerically checked, needs expert review.

## Minimal proposition attempt

P4-P1 starts as proposed. The first target is a scalar or diagonal commuting
affine system with a defined grid and endpoint error. The proposed
non-implication will be pursued only if it remains connected to the Gaussian
experiments.

The work must include a counterexample search, endpoint and singular checks,
and numerical verification. Any resulting statement remains needs expert
review. No statement will be called proved without manual approval.

## Later focused runs

Runs 2 through 6 are authorized by the user's request to execute all of Phase
4. Each still requires review of the preceding validated artifacts.

| run | purpose | expected limit | hard stop |
| --- | --- | ---: | ---: |
| 2 | high-accuracy reference for decisive rows | 30 minutes | 45 minutes |
| 3 | affine mean, covariance, matrix, and eigenvalue decomposition | 40 minutes | 60 minutes |
| 4 | solver-specific local error diagnostics | 45 minutes | 60 minutes |
| 5 | precision, NFE 64 and 128, and small perturbations | 60 minutes | 90 minutes |
| 6 | final focused validation from an immutable config | 90 minutes | 120 minutes |

No run may add mixtures, dimension 32, or a Cartesian expansion before the
Gaussian mechanism is understood.

## Precision audit plan

For decisive rows, compare float64 results against high-accuracy reference
integration and a small higher-precision CPU calculation. Record:

- inversion margin
- reference error
- precision sensitivity
- affine map condition number
- minimum covariance eigenvalue
- maximum covariance eigenvalue
- matrix square-root residual
- endpoint moment residual

An inversion is unstable if its margin is comparable to the numerical
reference error.

## Literature audit plan

Only primary sources will be used. The audit will read full relevant sections
on non-autonomous affine ODE error, Euler, Heun, RK4, modified equations, time
reparameterization, diffusion and flow schedules, solver-dependent sampling,
Gaussian flow matching, linear-system discretization, and Wasserstein error
under affine maps.

The existing affine Gaussian field construction is related to
[Stochastic Interpolants](https://arxiv.org/abs/2303.08797). Existing schedule
notes refer to
[Lipschitz-guided schedules](https://arxiv.org/abs/2509.01629). These links do
not establish novelty or overlap. Exact sections, assumptions, version dates,
and proof machinery remain to be audited in
[`docs/PHASE4_LITERATURE_AUDIT.md`](PHASE4_LITERATURE_AUDIT.md).

## Claims

The planned Phase 4 entries are:

| claim ID | initial status |
| --- | --- |
| P4-C1 | under-test |
| P4-C2 | under-test |
| P4-C3 | proposed |
| P4-P1 | proposed |

One clean run cannot mark a new claim supported. H1 and H3 remain
inconclusive. H2 remains contradicted. H4 remains under-test.

## Exclusions and invalidated outputs

- Dimension 8 mixture evidence is excluded from every decisive Phase 4 claim.
- Gaussian mixtures are excluded from Run 1.
- NFE 64 and 128 are excluded from Run 1.
- Dimension 32 is excluded.
- Superseded Phase 3 analyses remain preserved.
- The first Phase 3 sensitivity and interaction artifacts remain invalidated.
- Corrected intermediate analyses remain superseded by the final audit.
- Dirty Phase 3 artifacts are not release-ready table or figure sources.

## Unresolved questions

1. Does the clean commit reproduce every decisive Gaussian inversion?
2. Which affine matrix or covariance eigendirection controls the strongest
   inversion?
3. Does the same derived term explain both geometry families?
4. Why does Euler prefer variance-preserving in the low-rank family while
   Heun and RK4 prefer linear?
5. Are the smallest RK4 margins larger than higher-precision numerical error?
6. Can a minimal proposition be stated without artificial assumptions?
7. Is the mechanism already established in numerical ODE or diffusion
   schedule literature?
8. Can the final limited claim survive at least two solvers or geometries?
