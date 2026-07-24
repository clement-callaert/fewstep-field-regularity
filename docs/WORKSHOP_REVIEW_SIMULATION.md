# Workshop review simulation

Date: 2026-07-24. Reviewed draft: `paper/gddl2026/main.tex` at commit
`2d9d71a` (4 main pages, references on page 5). Three independent hostile
reviews were generated against the draft, each attacking correctness,
novelty, and relevance without deference to the repository documentation.
Objections are classified fatal / major / minor / invalid, and every valid
objection that fits the workshop scope is corrected in the revision listed
at the end.

---

## Review 1: Numerical-analysis reviewer

**Summary.** The paper shows that the time-averaged squared Jacobian of an
affine ODE field does not determine fixed-step Runge–Kutta endpoint error
ordering between two Gaussian probability paths, gives an exact modal
defect decomposition, and proves an elementary grid-aliasing proposition
for forward Euler.

**Strengths.** Everything is exactly computable and audited to 80 digits;
the telescoping transported-defect identity is stated correctly with no
hidden smallness assumptions; the proposition is honest about its
$N$-dependent construction; the claim discipline (bounds versus orderings)
is unusually clean for an ML venue.

**Weaknesses.** To a numerical analyst the headline is expected: local
truncation error depends on derivatives sampled at stage points, so no
unsigned time average of $\|A\|$ could be a ranking statistic. The
proposition is a one-line aliasing trick. The interesting content is the
benchmark discipline, not the mathematics.

**Correctness concerns.**
(a) The baseline $\mathcal{R}$ is computed by trapezoidal quadrature on 24
nodes; if quadrature error were comparable to metric margins, "inversions"
could be quadrature artifacts.
(b) Numerical modal factors can be negative at coarse Euler steps; the
$\wtwo$ reduction must use $|r_i|$.
(c) The Heun local coefficient sign convention should be stated
(exact-minus-method).

**Novelty concerns.** Backward error analysis and stage-sampling arguments
are classical (Hairer et al.); the proposition resembles known aliasing
examples. The paper must not imply a new numerical-analysis phenomenon.

**Relevance concerns.** Fine for a generative-modeling workshop; thin as
numerical analysis.

**Missing experiments.** An out-of-sample test of the solver-specific
proxy as a predictive criterion; a non-commuting Gaussian example.

**Score.** 6/10 (marginally above threshold). **Confidence.** 4/5.

**Classification of objections.**

| objection | class | disposition |
| --- | --- | --- |
| Quadrature error could produce spurious inversions (a) | major | Valid concern, resolved by diagnostic: recomputing all eight Phase 4 family metrics at n=2048 changes values by at most $3.6\times10^{-3}$ while every inversion-block metric margin is at least $0.62$; all orderings are unchanged. Recorded below; paper wording notes the closed-form smooth integrand. |
| Sign of modal factors (b) | minor | Already handled: code and the audited derivation use $\lvert r_i\rvert$ (see `docs/P4_P1_PROOF_AUDIT.md`); no paper change needed beyond the existing formula, which displays $\lvert r_i\rvert$. |
| Heun sign convention (c) | minor | Valid; the paper already states "exact minus method". No change needed. |
| Headline is classical / expected | major (novelty) | Partially valid; the paper's stated contribution is the exact controlled non-implication and benchmark, and Sections 1, 5, and 6 already disclaim a new numerical-analysis phenomenon. No further change. |
| Add out-of-sample proxy validation | invalid (scope) | Promoting the proxy is forbidden by the frozen claims; explicitly out of scope for this workshop paper. |
| Add non-commuting example | invalid (scope) | A new family after seeing results would violate the pre-registration discipline; noted as future work only. |

---

## Review 2: Diffusion / flow-matching reviewer

**Summary.** A controlled Gaussian study showing that the averaged
squared Lipschitz criterion for choosing probability paths does not
determine which path wins at fixed NFE under Euler/Heun/RK4, with a modal
explanation and a small pre-registered replication.

**Strengths.** Clear pipeline; equal-NFE accounting is done properly;
the low-rank solver–path flip (VP best for Euler, linear for Heun/RK4) is
a crisp, memorable observation; honest exclusion of mixture evidence.

**Weaknesses.** No learned model, no image or text experiment, so the
practical bite is unproven. The tested solvers are generic RK methods:
modern diffusion samplers (DPM-Solver, DPM-Solver++, DEIS) integrate the
linear part exactly and would be exact on these affine fields, so the
benchmark cannot say anything about the solvers practitioners actually
prefer. The comparison also fixes the time parameterization: the
Lipschitz-guided framework is mainly used to *optimize* schedules via its
transfer formula, not to rank two fixed paths, so the paper may be
attacking a use case the original authors do not advocate.

**Correctness concerns.** None found in the stated setting.

**Novelty concerns.** Align Your Steps already shows schedules must be
tuned per solver; the observation that a solver-independent criterion is
insufficient follows morally from that line of work.

**Relevance concerns.** Without a learned model the result is a
cautionary note, not a method.

**Missing experiments.** A small learned flow (even 2-D toy MLP); a
DPM-Solver-style exponential integrator column; schedule-transfer-
optimized paths rather than fixed linear/VP.

**Score.** 5/10 (borderline). **Confidence.** 4/5.

**Classification of objections.**

| objection | class | disposition |
| --- | --- | --- |
| Exponential integrators are exact on affine fields, so RK solvers are the wrong comparison | major | Valid as a scope boundary, not a flaw: the claim concerns generic fixed-stage RK discretization, and learned fields are not affine, so exact-linear integrators do not extend. **Corrected**: a limitation sentence now states this explicitly. |
| Fixed time parameterization; criterion is meant for schedule optimization via transfer formula | major | Valid as a scope boundary. **Corrected**: the paper now states it ranks two fixed paths at the identity parameterization and that reparameterization-based schedule optimization is a complementary use the result does not address. |
| No learned model / no practical demonstration | major (relevance) | Valid but explicitly out of the frozen scope; the paper already states no learned model is evaluated and demonstrates no application improvement. The workshop accepts controlled or preliminary studies. Not correctable without violating the scope freeze; left as a disclosed limitation. |
| Novelty follows from Align Your Steps | minor | Partially valid; the paper already credits solver-dependent schedules as established and claims only the exact non-implication and mechanism. No change. |
| Add learned-flow or exponential-integrator experiments | invalid (scope) | Expanding to a neural benchmark to answer a simulated reviewer is explicitly forbidden by the session constraints; recorded as future work. |

---

## Review 3: Optimal transport / distributional-learning reviewer

**Summary.** Using the closed-form Gaussian (Bures) $\wtwo$, the paper
demonstrates that an averaged Jacobian regularity functional does not
determine fixed-budget $\wtwo$ ordering of two Gaussian probability
paths, with exact modal accounting and a pre-registered second family.

**Strengths.** Exact distribution-level error metric rather than sample
estimates; correct use of the Gelbrich/Bures formula including the mean
term in the non-centered family; pre-registration of the external family
with frozen tolerances is exemplary for this community; artifact-level
provenance for every number.

**Weaknesses.** The OT content is standard (closed-form Gaussian
$\wtwo$); the geometry is limited to commuting covariances where
$\wtwo$ reduces to a per-mode computation, which is far from the general
Bures geometry; "external validation" is another Gaussian family, so the
external-ness is modest.

**Correctness concerns.**
(a) Why $\wtwo$ and not KL or another divergence? The choice should be
motivated since rankings could differ by metric.
(b) In the non-centered family the baseline $\mathcal{R}$ ignores $c(t)$
by definition; the paper should say this is a property of the registered
criterion, not an unfair handicap invented for the test.

**Novelty concerns.** The commuting reduction is elementary; the value is
the audit and the counterexample catalog, which is defensible for a
non-archival workshop.

**Relevance concerns.** Good fit for a distributional-learning workshop;
the paper should make the transport framing visible early.

**Missing experiments.** Non-commuting Gaussians (full Bures geometry);
a second divergence (e.g., KL, which is also closed-form for Gaussians).

**Score.** 6/10 (accept-leaning for a short-paper track).
**Confidence.** 3/5.

**Classification of objections.**

| objection | class | disposition |
| --- | --- | --- |
| Metric choice ($\wtwo$ vs KL) unmotivated (a) | minor | Valid. **Corrected**: the paper now notes $\wtwo$ is the exact, closed-form, distribution-level error used by the schedule-design literature and native to the workshop's transport focus. Testing a second divergence is future work, not added post hoc. |
| $\mathcal{R}$ ignores $c(t)$; fairness should be stated (b) | minor | Valid and pre-registered: the frozen external-validation plan recorded before execution that this is a property of the registered baseline definition. **Corrected**: the paper's Section 2 already states "$\mathcal{R}$ ignores $c(t)$"; a clause now marks it as the criterion's own definition. |
| Commuting-only geometry | minor | Already disclosed in limitations; no change. |
| External family is still Gaussian | minor | Wording in the paper is "pre-registered", and the claim scope is "tested systems"; no change. |
| Add non-commuting / KL experiments | invalid (scope) | New post-hoc families are barred by the pre-registration discipline; recorded as future work. |

---

## Quadrature diagnostic (recorded for objection R1-a)

Post-hoc diagnostic, run 2026-07-24, not a registered artifact and not
cited numerically in the paper. Recomputing the averaged-regularity
metric for all eight Phase 4 (family, dimension, path) combinations at
`n_time` 24 versus 2048:

| family | dim | path | n=24 | n=2048 | abs. diff |
| --- | --- | --- | ---: | ---: | ---: |
| anisotropic | 2/8 | linear | 0.97263691 | 0.97229634 | 3.41e-04 |
| anisotropic | 2/8 | vp | 0.19236078 | 0.19227006 | 9.07e-05 |
| low-rank | 2 | linear | 1.24489803 | 1.24553069 | 6.33e-04 |
| low-rank | 2 | vp | 0.62545352 | 0.62546110 | 7.58e-06 |
| low-rank | 8 | linear | 2.94765233 | 2.94410414 | 3.55e-03 |
| low-rank | 8 | vp | 4.72952064 | 4.73054400 | 1.02e-03 |

Every metric ordering is unchanged; the maximum quadrature drift
(3.55e-03) is at least two orders of magnitude below every
inversion-block metric margin (minimum 0.62). The anisotropic values are
dimension-independent because the spectral norm depends only on the
extreme eigenvalue rule.

## Summary of dispositions

- Fatal objections: none.
- Major objections corrected in the draft: exponential-integrator scope
  boundary; time-reparameterization scope boundary.
- Major objections valid but out of the frozen scope (left disclosed, not
  corrected by new experiments): no learned model; classical flavor of
  the mechanism.
- Minor objections corrected: $\wtwo$ motivation; $\mathcal{R}$-ignores-
  $c(t)$ framing.
- Invalid / out-of-scope requests (recorded as future work only):
  out-of-sample proxy validation, non-commuting families, KL comparison,
  learned-flow experiments, exponential-integrator columns.

## Revision plan

1. **Done in this revision** (see `paper/gddl2026/main.tex`):
   add the exponential-integrator and reparameterization scope sentences
   to Section 7; add the $\wtwo$ motivation clause to Section 2; mark
   "$\mathcal{R}$ ignores $c(t)$" as a property of the registered
   criterion; keep the four-page budget after edits.
2. **Before submission (no new science):** swap in the official NeurIPS
   2026 style file when published and re-verify the page count; recheck
   the GDDL CFP rules one week before the deadline; final anonymization
   pass.
3. **Explicit future work (not for this paper):** out-of-sample
   evaluation of solver-specific proxies, non-commuting Gaussian
   geometry, KL-based orderings, and any learned-model benchmark. Each
   would require a new pre-registered plan.
