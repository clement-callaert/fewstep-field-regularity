# Phase 4 literature audit

Status: Source verified for the listed sections. Novelty assessment remains
under review.

Scope: Primary sources relevant to affine ODE propagation, local truncation
error, schedule design, solver dependence, Gaussian interpolation, and
Gaussian Wasserstein distance. No conclusion relies on an abstract alone.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`

Literature is interpretive context, not registered evidence. Post-hoc
diagnostics remain post-hoc. Dimension 8 mixture output and dirty Phase 3
artifacts are excluded from decision claims.

## Source records

### Classical ODE and linear systems

J. C. Butcher, "Coefficients for the study of Runge-Kutta integration
processes," *Journal of the Australian Mathematical Society* 3, 185-201
(1963), [DOI](https://doi.org/10.1017/S1446788700027932). Section 2 introduces
the rooted-tree coefficient machinery for Runge-Kutta order conditions. The
paper notes that a non-autonomous problem can be made autonomous by adding
time as a state variable. This supplies source machinery for solver order,
but the affine non-autonomous expressions in the mathematical analysis are
original expansions.

E. Hairer, S. P. Norsett, and G. Wanner, *Solving Ordinary Differential
Equations I*, second revised edition, Springer (1993, corrected printing
2008), [DOI](https://doi.org/10.1007/978-3-540-78862-1). Chapter II, Sections
2 and 3 treat Runge-Kutta order conditions and error estimation. Chapter II,
Section 3, Theorem 3.4 gives the standard implication from local order to
global order under smoothness and stability assumptions. It provides proof
machinery, not the solver-specific constants asserted here.

E. Hairer, C. Lubich, and G. Wanner, *Geometric Numerical Integration*,
second edition, Springer (2006),
[DOI](https://doi.org/10.1007/3-540-30666-8). Chapter IX, Sections 1 through
3 develop modified equations and backward error analysis for one-step
methods. This weakens any novelty claim based only on interpreting a
discrete solver through another differential equation. It does not order the
two Gaussian paths studied here.

C. F. Van Loan, "Computing integrals involving the matrix exponential,"
*IEEE Transactions on Automatic Control* 23(3), 395-404 (1978),
[DOI](https://doi.org/10.1109/TAC.1978.1101743). Theorem 1 and the block
matrix constructions in Sections II and III show how matrix exponentials
encode integrals for constant linear systems. This is relevant exact
discretization machinery. Our \(A(t)\) is time dependent, but commuting.

### Generative paths, schedules, and solvers

Y. Lipman, R. T. Q. Chen, H. Ben-Hamu, M. Nickel, and M. Le, "Flow Matching
for Generative Modeling," ICLR 2023, arXiv version 2 dated 2023-02-15,
[paper](https://arxiv.org/abs/2210.02747). Sections 3 and 4 define conditional
probability paths and Gaussian paths. This establishes that Gaussian
probability paths and their vector fields are known machinery. It does not
establish the fixed-NFE ordering result.

M. Albergo, N. M. Boffi, and E. Vanden-Eijnden, "Stochastic Interpolants: A
Unifying Framework for Flows and Diffusions," *JMLR* 26(209), 1-80 (2025),
[paper](https://jmlr.org/papers/v26/23-1605.html). Section 2, especially the
interpolant definition and transport equations, supplies the source framework
for \(X_t=\alpha X_0+\sigma X_1\). The Gaussian affine specialization here is
an original calculation from those standard identities.

C. Lu et al., "DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic
Model Sampling in Around 10 Steps," NeurIPS 2022, arXiv version 3 dated
2022-10-17, [paper](https://arxiv.org/abs/2206.00927). Section 3, Proposition
3.1 gives an exact solution representation after a log-SNR change of
variables. Section 3.2 derives high-order solvers by Taylor expansion.
Appendix D gives convergence results. It shows that exact treatment of a
linear component and the chosen time variable matter.

C. Lu et al., "DPM-Solver++: Fast Solver for Guided Sampling of Diffusion
Probabilistic Models," arXiv version 3 dated 2023-03-10,
[paper](https://arxiv.org/abs/2211.01095). Section 3 reports that higher order
solvers can be less stable under strong guidance. Section 4.1, Proposition
4.1 and equations 8 and 9 derive an exact linear contribution and
solver-dependent Taylor approximation. This is direct prior evidence that
solver order alone does not determine practical sampling quality. It weakens
novelty of a broad solver-dependence claim.

Q. Zhang and Y. Chen, "Fast Sampling of Diffusion Models with Exponential
Integrator," arXiv version 3 dated 2023-04-10,
[paper](https://arxiv.org/abs/2204.13902). Sections 3.1 and 3.2 split the
diffusion ODE into an analytically integrated linear term and an approximated
nonlinear term. This supplies related proof machinery and weakens novelty of
exact linear propagation as a contribution.

A. Sabour, S. Fidler, and K. Kreis, "Align Your Steps: Optimizing Sampling
Schedules in Diffusion Models," ICML 2024, arXiv version 2 dated 2024-06-05,
[paper](https://arxiv.org/abs/2404.14507). Sections 3 and 4 derive and test
schedules specific to the solver, trained model, and data distribution. This
substantially weakens novelty of the qualitative claim that a preferred
schedule can depend on the solver. It does not give the present commuting
Gaussian error decomposition.

T. Karras, M. Aittala, T. Aila, and S. Laine, "Elucidating the Design Space
of Diffusion-Based Generative Models," NeurIPS 2022,
[paper](https://arxiv.org/abs/2206.00364). Section 3 separates the ODE solver,
time steps, and noise schedule as sampler design choices. Equations 4 through
6 and Algorithm 1 specify the deterministic sampler. This is prior evidence
that schedule and discretization should be studied jointly.

"Lipschitz-Guided Design of Interpolation Schedules in Generative Models,"
arXiv version 1 dated 2025-09-01,
[paper](https://arxiv.org/abs/2509.01629). Sections 3.1 and 3.2, including
Proposition 3.1, propose averaged squared drift Lipschitzness as a numerical
schedule criterion and give a schedule transfer formula. Sections 3.3 through
3.5 analyze Gaussian and mixture targets. Section 4 uses fixed-step RK4 in
experiments. This is the nearest overlap. It motivates the baseline but does
not state that its ordering determines fixed-NFE error across Euler, Heun,
and RK4. The Phase 4 result should therefore be framed as a limitation under
tested affine Gaussian settings, not as a refutation of the paper.

### Wasserstein error

M. Gelbrich, "On a Formula for the L2 Wasserstein Metric between Measures on
Euclidean and Hilbert Spaces," *Mathematische Nachrichten* 147, 185-203
(1990), manuscript received 1988-08-22,
[DOI](https://doi.org/10.1002/mana.19901470121). The finite-dimensional
Gaussian and elliptically contoured formula in the main theorem supplies the
exact moment-based W2 identity. The commuting simplification in the Phase 4
analysis is original algebra. It is not an empirical estimate.

## Overlap assessment

Observation: Prior work already treats Gaussian interpolation, exact linear
terms, modified equations, schedule optimization, and solver-specific
schedules.

Interpretation: A broad novelty claim about solver dependence is not
defensible. The narrower contribution that survives review is a controlled
commuting Gaussian decomposition showing why averaged Jacobian regularity
does not determine fixed-grid W2 error. The minimal proposition is elementary
and should be treated as explanatory, not as a major theorem.

The search did not locate a source stating the exact P4-P1 construction or
the exact tested Euler, Heun, and RK4 inversion pattern. Absence from this
audit is not proof of novelty. Citation coverage and the proposition still
need expert review.

## Unresolved literature questions

- Check whether numerical-analysis work on oscillatory coefficients contains
  the same grid-aliasing construction.
- Check whether schedule optimization papers after September 2025 give a
  direct averaged-Lipschitz counterexample.
- Obtain page-level confirmation for every theorem label before publication.
- Decide whether solver-specific schedule optimization fully subsumes the
  empirical part of P4-C2.
