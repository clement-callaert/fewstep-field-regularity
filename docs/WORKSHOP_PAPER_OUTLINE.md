# Exact four-page workshop paper outline

Status: Proposed outline. Paper drafting has not started.

Target: NeurIPS 2026 Geometric Distributional Deep Learning short-paper
track, four main pages excluding references.

Title: **When Averaged Field Regularity Fails to Rank Few-Step Generative
Paths**

The page budget assumes the NeurIPS 2026 two-column template. The main text
must be self-contained. No core result or proposition is deferred to an
appendix.

## Page 1

### Abstract, about 150 words

- Practical issue: choosing probability paths for few-step generation.
- Attractive assumption: lower averaged Jacobian regularity should rank paths
  by fixed-budget error.
- Setting: exact commuting Gaussian probability flows and exact Gaussian W2.
- Result: fourteen clean-code ranking inversions.
- Mechanism: solver stage sampling and transported signed defects.
- Scope: controlled limitation, not a new sampler or universal negative
  result.

### 1. Introduction, about 0.65 page

- Motivate fixed-NFE path and solver selection.
- Distinguish controlling an error bound from determining empirical ordering.
- State the narrow literature gap relative to regularity-guided schedules and
  solver-specific schedule optimization.
- End with at most three contributions:
  1. controlled exact-W2 inversion benchmark;
  2. commuting eigenmode and transported-defect explanation;
  3. grid-aware Euler non-implication construction, conditional on proof
     verification.

### Figure 1, about 0.25 page

Conceptual two-path diagram: one averaged score per path, fixed solver nodes,
and the opposite endpoint-error ordering. Caption labels it conceptual, not
experimental.

## Page 2

### 2. Gaussian paths and regularity criterion, about 0.45 page

- Define \(X_t=\alpha X_0+\sigma X_1\), \(Q(t)\), and
  \(A(t)=Q'(t)Q(t)^{-1}/2\).
- Define the averaged squared Jacobian baseline.
- State Gaussian W2 and the centered commuting reduction.
- Give only the linear and variance-preserving path definitions needed later.

### 3. Why the ranking need not agree, about 0.55 page

- Diagonalize into \(x_i'=a_i(t)x_i\).
- Show exact modal factor
  \(\sqrt{q_i(t_{n+1})/q_i(t_n)}\).
- State that Euler, Heun, and RK4 use different stage-dependent numerical
  factors at equal NFE.
- Display the transported signed-defect identity.
- Explain the information omitted by an unsigned time average: stages,
  derivatives, signs, cancellation, and endpoint transport.

### Figure 2, about 0.25 page

Compact strongest-inversion plot plus an honest summary of all fourteen
inversion blocks. Use release-ready artifacts only. Avoid a correlation axis
that implies predictive validation.

## Page 3

### 4. Controlled benchmark, about 0.35 page

- Families: anisotropic and low-rank Gaussian.
- Dimensions: 2 and 8.
- Paths: linear and variance-preserving.
- Solvers: Euler, Heun, RK4.
- Primary NFE: 8, 16, 32; robustness at 64 and 128.
- Exact propagated Gaussian moments and Gaussian W2.
- Define an inversion and equal-NFE accounting.
- Separate pre-specified reproduction from post-hoc diagnostics.

### 5. Results, about 0.65 page

- State all fourteen reproduced inversions.
- Give the strongest comparison as a small table.
- Report strongest and smallest margins with artifact IDs.
- Report the 80-digit precision comparison.
- Describe low-rank solver-path interaction.
- Briefly report perturbation and high-NFE robustness.
- State explicitly that mixtures do not support the conclusions.

### Figure 3, about 0.3 page

Dominant eigenmode and transported signed local defects for the strongest
comparison. The caption states that the decomposition is exact while any
solver-specific aggregate is post-hoc.

## Page 4

### 6. Minimal non-implication construction, about 0.3 page

Include only if P4-P1 is verified.

- Quantify over \(L>0\) and integer \(N\geq1\).
- Define \(a_0\), \(\epsilon_N\), and \(a_1\).
- Give the same-endpoint, strict-regularity, and Euler-exact equalities in one
  compact proposition and proof.
- State that \(a_1\) depends on the grid and is not the mechanism asserted for
  every Gaussian inversion.

If withdrawn, replace this subsection with a short scope statement and give
more space to limitations.

### 7. Related work and distinction, about 0.28 page

- Flow Matching and Stochastic Interpolants for Gaussian paths.
- Lipschitz-guided schedule design for the baseline.
- Align Your Steps, DPM-Solver, DPM-Solver++, DEIS, and EDM for
  solver-specific schedules or integration.
- Classical Runge-Kutta error and backward error analysis.
- State that solver dependence is not the contribution.

### Figure 4, about 0.22 page

Low-rank path preference across Euler, Heun, and RK4 versus NFE, with equal
NFE made visible. If space is tight, move this figure to the supplement and
retain the interaction as a compact table. The first three figures have
priority.

### 8. Limitations and conclusion, about 0.35 page

- Gaussian analytical and commuting setting.
- Two paths and three solvers only.
- No learned field, image, or video experiment.
- No universal predictor.
- Post-hoc status of the solver-specific proxy.
- Literature-search absence does not prove novelty.
- Conclude only that averaged regularity alone does not determine the tested
  fixed-budget ordering.

## References and appendix

References do not count toward the target page limit. The workshop CFP does
not yet explicitly exclude an appendix for the short track, so do not rely on
appendix space until that rule is confirmed.

If permitted, the appendix may contain:

- full Gaussian derivations;
- full inversion table;
- complete P4-P1 proof audit;
- precision and reconstruction checks;
- configuration tables and artifact hashes;
- extended literature comparison.

## Space and figure rules

- Maximum four main figures.
- If four figures make the derivation unreadable, use three.
- Every experimental figure must have a provenance sidecar.
- Each numerical sentence must name an artifact in source or caption.
- No post-hoc proxy correlation plot in the main paper.
- No main-text claim may depend on supplementary material.
