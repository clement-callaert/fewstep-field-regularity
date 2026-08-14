# Q&A defense

Answers are for a hostile but technical interview. Keep them short.
Do not broaden the claim.

## 1. Does this refute Lipschitz-guided schedule design?

No. Chen, Vanden-Eijnden, and Xu propose averaged squared Lipschitzness
as a schedule-design criterion, including a transfer formula for
optimizing schedules. The present study ranks two fixed paths, linear
and trigonometric VP, at the identity time parameterization, under
generic Runge-Kutta solvers. A quantity can appear in an informative
upper bound without being tight enough to order two methods at a small
equal NFE. The result is a limitation of that scalar as a pairwise
ranking statistic in tested commuting Gaussian flows. It is not a
refutation of regularity-guided design.

## 2. Why should regularity ever be expected to predict discretization error?

Classical one-step theory bounds local and global error by Lipschitz
and smoothness constants of the field (Hairer, Norsett, Wanner).
Averaged squared Jacobian magnitude is a natural scalar proxy for that
roughness. The expectation is therefore reasonable as a bound
heuristic. The extra, unsupported step is that the same scalar should
completely order pairwise fixed-budget endpoint errors. The Gaussian
laboratory isolates that extra step.

## 3. Why use spectral norm rather than Frobenius norm?

Chen et al. Def. 3.2 uses $\|\nabla b_t\|_2$, the operator 2-norm.
The baseline is implemented with `torch.linalg.matrix_norm(..., ord=2)`.
Frobenius is a different metric, used elsewhere in the repository as an
alternative, not as the registered baseline. Changing the matrix norm
would be a different criterion and a different test.

## 4. Why does the expectation disappear in the affine case?

For $b(t,x)=A(t)x+c(t)$, the spatial Jacobian is $A(t)$, independent of
$x$. Therefore
$\mathbb{E}[\|\nabla_x b(t,X_t)\|_2^2]=\|A(t)\|_2^2$.
The path measure still exists; it simply does not enter the integrand.
This is a property of affine fields, not a handicap invented for the
test. In the non-centered family, $\mathcal{R}$ also ignores $c(t)$ by
definition.

## 5. Why compare equal NFE instead of equal step count?

NFE is the computational budget in generative sampling: each field
evaluation is the expensive call. Heun uses two evaluations per step,
RK4 four. Equal step count would give RK4 four times the field budget
of Euler. The code requires `requested_nfe % evals_per_step == 0`.
The tradeoff is explicit: a higher-order solver receives fewer, more
informative steps at the same evaluation budget.

## 6. Is 14 out of 36 statistically meaningful?

No, not as a population frequency. The 36 blocks are a focused,
pre-specified grid, not a random sample from a larger universe of
paths, solvers, or dimensions. Fourteen inversions are a catalog of
disagreements inside that grid. They are enough to refute a universal
ranking implication inside the tested systems. They are not an estimate
of how often inversions occur elsewhere. The same warning applies to
11 of 18 in the non-centered family.

## 7. Why $\mathrm{W}_2$ rather than KL?

Gaussian $\mathrm{W}_2$ is closed-form (Gelbrich), matches the
schedule-design literature's distributional error, and is native to a
transport view of generative paths. KL is also closed-form for
Gaussians, but it was not the registered primary outcome. Rankings
could differ under another divergence. That is an open comparison, not
a hidden result. Reported values are $\mathrm{W}_2$, not $\mathrm{W}_2^2$.

## 8. Why use commuting Gaussians?

They give exact fields, exact endpoint laws, exact Gelbrich $\mathrm{W}_2$,
and an eigenmode decomposition with no training or sampling estimator.
Commuting covariances are a restriction: $\mathrm{W}_2$ reduces to a
sum over modes. Non-commuting Gaussians would require the full Bures
geometry and were not part of the frozen grid. The restriction is
disclosed, not accidental.

## 9. Does the scalar counterexample explain the observed Gaussian inversions?

No. Proposition 1 is a grid-aware Euler aliasing construction. The
oscillatory field is chosen after $N$. The Gaussian inversions are
explained by solver-stage sampling and transported signed defects on
the actual linear and VP coefficients. The proposition shows logical
non-implication. It is not claimed as the mechanism of every inversion.

## 10. What happens with exponential integrators?

DPM-Solver, DPM-Solver++, and DEIS integrate a linear part exactly.
On these affine fields they are exact, so both paths have zero
discretization error and the ranking question is vacuous. Learned
fields are not affine, so exact-linear integrators do not make the
question disappear in practice. The study concerns generic fixed-stage
Runge-Kutta methods.

## 11. Why exclude the mixture experiments?

Dimension-8 mixture blocks failed estimator calibration. Uncalibrated
sampling estimators are not allowed to support a ranking claim. The
claims ledger and workshop paper both exclude mixture evidence. No
mixture number appears in the talk as a result.

## 12. Is solver-dependent schedule quality already known?

Yes. Align Your Steps optimizes schedules per solver, model, and
dataset. EDM separates schedule from discretization. Solver dependence
is not the novelty claim. What is new here, relative to that
literature, is an exact commuting-Gaussian ranking non-implication for
the averaged-regularity scalar, with a modal identity and a
grid-aware Euler proposition. Search absence does not prove novelty.

## 13. What is genuinely new?

A controlled, closed-form demonstration that averaged squared Jacobian
ordering need not determine fixed-NFE Gaussian $\mathrm{W}_2$ ordering
on commuting affine flows, together with an exact transported-defect
identity and a quantified Euler non-implication. The contribution is
the limitation of a scalar ranking statistic in an audited laboratory.
It is not a new sampler, not a new numerical-analysis phenomenon, and
not a universal schedule rule.

## 14. Why is a low-dimensional exact benchmark relevant to learned models?

Learned fields mix approximation error, training noise, and
discretization error. If a ranking claim already fails when those
noises are absent, it is not entitled to be treated as automatic in
learned systems. The benchmark does not show that the same inversions
occur for neural fields. It shows which claim deserves a later test
there. Exact small models are for discovery of claims, not for
replacing image experiments.

## 15. How could this be extended to non-commuting covariances?

Keep Gaussian endpoints but drop simultaneous diagonalizability.
The field remains affine, Gelbrich $\mathrm{W}_2$ remains closed-form,
and the numerical map can still be recovered from $d+1$ probes.
The modal product identity is lost. One would track matrix one-step
maps and transported defects in $\mathrm{GL}(d)$. That family was not
run, and adding it after seeing results would violate the
pre-registration discipline used here.

## 16. How might the question change for a CTMC generator?

Replace $b_t(x)$ by a rate matrix $Q_t(x,y)$. Endpoint error is then
error of a discrete distribution after a finite jump approximation.
The analogue of averaged Jacobian regularity would be some reduced
scalar of $Q_t$, for example a Lipschitz constant of rates, a spectral
gap, or an averaged holding-rate roughness. The same logical gap
applies: a scalar appearing in a bound need not order two generators
at a fixed simulation budget. That is a research question, not a
corollary of the ODE study.

## 17. What is the analogue of NFE in a discrete rate model?

The honest analogue is the number of generator or rate evaluations, or
the number of simulated jumps, depending on the scheme: uniformization
steps, thinning proposals, tau-leaping stages, or Gillespie steps.
The point is equal computational budget, not equal number of time
bins. I do not claim that the Gaussian NFE table transfers numerically
to any of those schemes.

## 18. Which part of the result might transfer to the PhD topic, and which part definitely does not?

What may transfer is the research discipline: path or rate schedule,
dynamical field or generator, discretization scheme, and budget are a
joint design; unsigned averages discard signed sampled defects; exact
small models can falsify ranking claims before learned systems are
blamed. What definitely does not transfer is the commuting Gaussian
theorem, the 14-of-36 catalog, the VP-versus-linear preference, or
Proposition 1. Those are statements about affine ODEs. A CTMC
factorization trap is a different mathematical object and would need
its own exact laboratory.
