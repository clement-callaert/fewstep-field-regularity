# P4-P1 proof audit

Status: Proof verified after independent adversarial review.

Date: 2026-07-24.

## Audited proposition

For every real \(L>0\) and every integer \(N\geq 1\), let \(h=1/N\) and let
forward Euler use the fixed left-endpoint grid
\(t_n=nh\), \(n=0,\ldots,N-1\), on \([0,1]\). Then there exist two
\(C^\infty\) scalar linear non-autonomous fields

\[
f_k(t,x)=a_k(t)x,\qquad k\in\{0,1\},
\]

such that, for the initial-value problems

\[
x'(t)=f_k(t,x(t)),\qquad x(0)=1,
\]

all of the following hold:

1. the exact endpoints agree and equal \(\exp(L)\);
2. the averaged squared spatial Jacobian of \(f_1\) is strictly larger than
   that of \(f_0\);
3. the fixed-grid forward Euler endpoint for \(f_1\) is exact;
4. the fixed-grid forward Euler endpoint for \(f_0\) has strictly positive
   absolute error.

Consequently, larger averaged squared Jacobian does not imply larger
fixed-grid forward Euler endpoint error under these assumptions.

The quantifiers matter. The field \(a_1\) depends on \(N\). This is not a
claim about refining one fixed oscillatory ODE, and it is not a uniform
counterexample over all grids or solvers.

## Definitions

Fix \(L>0\) and \(N\in\mathbb{N}\). Define

\[
h=\frac1N,\qquad t_n=\frac nN,
\]

\[
\epsilon_N=N\left\{\exp(L/N)-1\right\}-L,
\]

\[
a_0(t)=L,\qquad
a_{1,N}(t)=L+\epsilon_N\cos(2\pi Nt).
\]

Both coefficients and both fields are real analytic on \(\mathbb{R}\).
Below, \(a_1\) abbreviates \(a_{1,N}\); the subscript is suppressed only for
readability.
For a scalar field \(f(t,x)=a(t)x\), the spatial Jacobian is
\(\partial_x f(t,x)=a(t)\), independent of \(x\).

## Formal proof

### Same exact endpoint

The solution of \(x'=a(t)x\), \(x(0)=1\), is

\[
x(t)=\exp\left(\int_0^t a(s)\,ds\right).
\]

For \(a_0\),

\[
\int_0^1 a_0(t)\,dt=L.
\]

For \(a_1\),

\[
\int_0^1a_1(t)\,dt
=L+\epsilon_N\int_0^1\cos(2\pi Nt)\,dt
=L+\epsilon_N\frac{\sin(2\pi N)}{2\pi N}
=L,
\]

because \(N\) is an integer. Thus both exact endpoints equal \(\exp(L)\).

### Strict averaged squared Jacobian ordering

Using integer-period orthogonality,

\[
\begin{aligned}
\int_0^1 a_1(t)^2\,dt
&=L^2
+2L\epsilon_N\int_0^1\cos(2\pi Nt)\,dt
+\epsilon_N^2\int_0^1\cos^2(2\pi Nt)\,dt\\
&=L^2+\frac{\epsilon_N^2}{2}.
\end{aligned}
\]

Also,

\[
\int_0^1a_0(t)^2\,dt=L^2.
\]

It remains to show \(\epsilon_N>0\). Let \(z=L/N>0\). The strict inequality
\(\exp(z)>1+z\) gives

\[
N\{\exp(L/N)-1\}>N(L/N)=L.
\]

Therefore \(\epsilon_N>0\), so

\[
\int_0^1a_1(t)^2\,dt>
\int_0^1a_0(t)^2\,dt.
\]

### Euler is exact for \(a_1\)

Forward Euler at the left endpoint updates

\[
x_{n+1}=\{1+h\,a_1(t_n)\}x_n.
\]

At every left node,

\[
\cos(2\pi Nt_n)=\cos(2\pi n)=1,
\]

so

\[
\begin{aligned}
1+h\,a_1(t_n)
&=1+\frac{L+\epsilon_N}{N}\\
&=1+\frac{N\{\exp(L/N)-1\}}{N}\\
&=\exp(L/N).
\end{aligned}
\]

Every one-step factor is therefore positive, and the endpoint is

\[
x_N=\prod_{n=0}^{N-1}\exp(L/N)=\exp(L).
\]

### Euler has positive error for \(a_0\)

For the constant field,

\[
x_N^{(0)}=(1+L/N)^N.
\]

Since \(L/N>0\) and \(\log(1+z)<z\) for \(z>0\),

\[
N\log(1+L/N)<L.
\]

Exponentiating gives

\[
(1+L/N)^N<\exp(L).
\]

Thus the absolute endpoint error

\[
\exp(L)-(1+L/N)^N
\]

is strictly positive. Every Euler factor for \(a_0\) is also positive because
\(1+L/N>1\).

This completes the proposition.

## Edge cases and asymptotics

### \(N=1\)

The construction gives

\[
\epsilon_1=\exp(L)-1-L>0,
\qquad
a_1(t)=L+\epsilon_1\cos(2\pi t).
\]

The single left Euler factor is

\[
1+a_1(0)=1+L+\epsilon_1=\exp(L).
\]

The exact integral of the cosine over \([0,1]\) is zero. All four conclusions
hold without a special case.

### Small positive \(L\)

Taylor expansion at fixed \(N\) gives

\[
\epsilon_N
=N\left\{\frac{L}{N}+\frac{L^2}{2N^2}
+O(L^3/N^3)\right\}-L
=\frac{L^2}{2N}+O(L^3/N^2).
\]

For every \(L>0\), however small, the exact exponential inequality above
gives strict positivity. At \(L=0\), \(\epsilon_N=0\), the regularity ordering
is not strict, and the proposition deliberately excludes that case.

### \(N\to\infty\) with fixed \(L\)

\[
\epsilon_N=\frac{L^2}{2N}+\frac{L^3}{6N^2}+O(N^{-3}),
\]

so

\[
\int_0^1a_1^2-\int_0^1a_0^2
=\frac{\epsilon_N^2}{2}
=\frac{L^4}{8N^2}+O(N^{-3}).
\]

The strict metric gap tends to zero. The coefficient \(a_1\) also changes
with \(N\): its amplitude tends to zero while its frequency tends to
infinity. In particular, this limit is not the convergence analysis of Euler
for one fixed coefficient. The first derivative amplitude
\(2\pi N\epsilon_N\) approaches \(\pi L^2\), while higher derivative
amplitudes need not remain bounded. The coefficient may also be negative
between nodes for some \(L,N\); the proposition assumes smoothness, not a
nonnegative drift. This is a grid-aliasing construction.

## Role of left-endpoint sampling and grid awareness

The proof uses the identity
\(\cos(2\pi Nt_n)=1\) at the left Euler nodes. A shifted grid, right-endpoint
method, midpoint method, or multistage Runge-Kutta method samples different
phases and is not covered. The oscillation frequency and amplitude are chosen
after \(N\) is fixed. The construction therefore establishes a logical
non-implication for fixed-grid left Euler, not a mechanism for all Gaussian
inversions and not a practical schedule design.

## Audit of associated identities

### Euler local coefficient

For \(x'=a(t)x\), assume \(a\in C^3\) for the displayed \(O(h^4)\)
remainders below. The leading coefficients require only the corresponding
lower derivatives with little-o remainders. The tested linear,
variance-preserving, and P4-P1 coefficients are analytic. Then

\[
x''=(a'+a^2)x.
\]

The exact one-step factor is

\[
1+ha+\frac{h^2}{2}(a'+a^2)+O(h^3),
\]

while Euler uses \(1+ha\). Thus the leading
**exact-minus-Euler** local coefficient is

\[
\frac12(a'+a^2).
\]

The sign convention must accompany the formula.

### Heun local coefficient

Explicit trapezoidal Heun has scalar factor

\[
r_H=1+\frac h2\{a(t)+a(t+h)+h\,a(t+h)a(t)\}.
\]

Expanding \(a(t+h)\) at \(t\) gives

\[
r_H
=1+ha+\frac{h^2}{2}(a'+a^2)
+h^3\left(\frac14a''+\frac12aa'\right)+O(h^4).
\]

The exact factor is

\[
1+ha+\frac{h^2}{2}(a'+a^2)
+\frac{h^3}{6}(a''+3aa'+a^3)+O(h^4).
\]

Subtracting method from exact cancels the \(aa'\) term and gives the leading
**exact-minus-Heun** coefficient

\[
-\frac1{12}a''+\frac16a^3.
\]

### Transported signed-defect identity

For arbitrary scalars \(r_0,\ldots,r_{S-1}\) and
\(e_0,\ldots,e_{S-1}\),

\[
\prod_{j=0}^{S-1}r_j-\prod_{j=0}^{S-1}e_j
=\sum_{i=0}^{S-1}(r_i-e_i)
\left(\prod_{j<i}r_j\right)
\left(\prod_{j>i}e_j\right).
\]

This follows by inserting the mixed products

\[
P_i=\left(\prod_{j<i}r_j\right)
\left(\prod_{j\geq i}e_j\right),
\]

for which \(P_0=\prod_j e_j\),
\(P_S=\prod_j r_j\), and

\[
P_{i+1}-P_i
=(r_i-e_i)
\left(\prod_{j<i}r_j\right)
\left(\prod_{j>i}e_j\right).
\]

Summing over \(i\) telescopes. The identity is exact and requires no
small-step, positivity, or smoothness assumption.

### Commuting Gaussian W2 reduction

In the centered commuting setting, diagonalize the target covariance as
\(\Sigma_1=U\operatorname{diag}(\lambda_i)U^\mathsf{T}\), with
\(\lambda_i>0\). Starting from covariance \(I\), a diagonal numerical
endpoint map with modal factors \(r_i\) produces covariance eigenvalues
\(r_i^2\). The Gaussian W2 formula then reduces modewise to

\[
W_2^2
=\sum_i\left(\sqrt{r_i^2}-\sqrt{\lambda_i}\right)^2
=\sum_i\left(|r_i|-\sqrt{\lambda_i}\right)^2.
\]

The absolute value is essential if a numerical factor is negative. This is
an exact algebraic reduction of the Gaussian covariance formula, up to the
floating-point evaluation used in artifacts. The transported identity is an
identity for signed factor error. Relating its sign directly to a W2 modal
discrepancy additionally requires controlling the sign of \(r_i\); the W2
formula itself remains valid without that condition because it uses
\(\lvert r_i\rvert\).

## Literature-equivalence search

The search used combinations of “Euler,” “oscillatory coefficient,”
“fixed grid,” “aliasing,” “resonance,” “periodic coefficient,” and
“Runge-Kutta.” It also revisited the primary numerical-analysis sources
already read for the Phase 4 literature audit:

- Butcher (1963) for Runge-Kutta order machinery;
- Hairer, Norsett, and Wanner (1993/2008), Chapter II, for local and global
  Runge-Kutta error;
- Hairer, Lubich, and Wanner (2006), Chapter IX, for modified equations and
  backward error analysis.

The search found broad prior treatment of oscillatory error, sampling
aliasing, phase error, and resonance, but no verified primary source with the
same \(N\)-dependent cosine coefficient, equal exact endpoint, strict
averaged-square ordering, and Euler-exact calibration. Search absence does
not establish novelty. The proposition should be described as an elementary
grid-aliasing construction and an original proposition under the stated
assumptions, not as a new numerical-analysis phenomenon.

## Formal proof versus numerical checks

The proposition is established by the inequalities and identities above.
The repository test
`tests/analytical/test_affine_flow_analysis.py::test_euler_nonimplication_construction`
checks one representative case only. It is regression evidence, not part of
the proof.

The Euler and Heun expansions, transported-defect identity, and commuting W2
reduction have both algebraic derivations and numerical checks. Numerical
agreement does not establish the identities.

## Independent adversarial review

An independently prompted numerical-analysis reviewer attempted to invalidate
the proposition and associated identities without trusting the existing
tests or prose.

No fatal or major flaw was found. The reviewer independently verified:

1. the quantifiers, exact endpoints, and strict metric ordering;
2. positivity of \(\epsilon_N\) and every Euler factor;
3. the \(N=1\), small-positive-\(L\), and large-\(N\) cases;
4. the exact-minus-Euler and exact-minus-Heun coefficients and their signs;
5. the earlier-numerical, later-exact orientation of the telescoping identity;
6. the commuting centered Gaussian W2 reduction with \(\lvert r_i\rvert\).

Valid minor objections and resolutions:

| objection | classification | resolution |
| --- | --- | --- |
| General \(C^3\) path assumptions do not automatically justify every displayed \(O(h^4)\) remainder for the derived scalar coefficient. | minor | The audit now states the extra \(a\in C^3\) assumption for those remainders. The tested coefficients and P4-P1 are analytic. |
| Grid dependence was present in \(\epsilon_N\) but hidden in the notation \(a_1\). | minor | The coefficient is now defined as \(a_{1,N}\), with any later abbreviation stated explicitly. |
| W2 depends on \(\lvert r_i\rvert\), whereas the transported identity concerns signed factor error. | minor | The distinction is now explicit. No positivity assumption is added to the algebraic identity. |
| The coefficient can be negative between nodes and can have non-uniform higher derivatives as \(N\) grows. | minor, artificiality | These facts are disclosed. The proposition claims smoothness and logical non-implication only. |
| The construction resembles familiar grid resonance or aliasing. | minor, literature | The paper will not claim a new numerical-analysis phenomenon or infer novelty from search absence. |

Rejected objections included possible failures of epsilon positivity, \(N=1\),
small \(L\), Euler-factor positivity, the Heun sign, the \(aa'\) cancellation,
and telescoping orientation. Direct calculation resolves each one above.

## Final status

**Proof verified.**

The proposition is valid for the stated grid-aware left-endpoint Euler
setting. It is suitable for a short main-text proposition if its artificial
and \(N\)-dependent construction is stated. It is not a mechanism claimed for
all Gaussian inversions and not a major theorem.
