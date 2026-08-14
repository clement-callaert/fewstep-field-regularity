# Workshop target audit

Status: Target-selection gate, frozen on 2026-07-24.

Scope: Official conference pages, official workshop websites, and OpenReview
venue pages available on 2026-07-24. Missing rules are recorded as not yet
stated. They are not inferred from previous editions.

## Conference-level facts

NeurIPS 2026 workshops are intended for informal discussion of work in
progress and future directions. Workshops will be held on December 11 or 12
in Sydney and December 12 or 13 in Paris and Atlanta. The conference suggests
August 29, 2026 AoE for workshop contributions and requires workshop
accept/reject decisions by September 29, 2026 AoE.

Official sources:

- [NeurIPS 2026 workshop call](https://neurips.cc/Conferences/2026/CallForWorkshops)
- [NeurIPS 2026 dates](https://neurips.cc/Conferences/2026/Dates)
- [NeurIPS 2026 workshop proposals on OpenReview](https://openreview.net/group?id=NeurIPS.cc/2026/Workshop_Proposals)

The conference-level August 29 date is a suggested date. Each workshop call
controls its own deadline and rules.

## Ranked shortlist

### 1. Geometric Distributional Deep Learning

| field | verified information |
| --- | --- |
| Workshop | Geometric Distributional Deep Learning: Bridging Optimal Transport, Learning and Structured Data |
| Conference | NeurIPS 2026 |
| Date and place | December 12 or 13, 2026, Paris, France |
| Official URL | <https://gddl-neurips-2026.github.io/> |
| OpenReview | <https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/GDDL> |
| Submission deadline | August 29, 2026 AoE |
| Notification | September 29, 2026 AoE |
| Camera-ready or final program | Final program October 16, 2026 |
| Archival status | Non-archival, no official proceedings |
| Page limit | Short: 2 to 4 pages. Long: 5 to 9 pages. References excluded. |
| Anonymity | Anonymized, double-blind review |
| Template | NeurIPS 2026 template and instructions |
| Supplementary material | No separate supplementary-file rule stated. The call excludes references from the page limit but does not explicitly exclude an appendix. Recheck before submission. |
| Dual submission | Concurrent and subsequent submission explicitly allowed, subject to the other venue's policy |
| Work stage | Ongoing and unpublished work explicitly welcomed |

Fit: High. The paper uses exact Gaussian Wasserstein error, probability
distributions, generative flows, and a commuting eigenspace analysis. The
workshop explicitly covers computational optimal transport, generative
models, and learning with distributions. The project is less directly about
graphs, manifolds, or structured-data architectures, so the abstract must
lead with distributional transport and exact W2 rather than numerical
analysis alone.

Likely reviewer profile: Optimal transport, distributional learning,
generative modeling, Gaussian geometry, and applied mathematics.

Estimated acceptance fit: High for the short-paper track if the proof audit
passes and the four-page paper remains self-contained. The exact W2 audit and
controlled limitation result match the workshop's distributional focus. The
lack of manifold or structured-data experiments is a fit risk, not a
scientific defect.

Required paper changes:

1. Use a four-page short paper, excluding references.
2. Frame Gaussian W2 and probability-path ordering as the distributional
   contribution.
3. Explain the connection to computational OT without implying a new OT
   method.
4. Keep the complete mechanism and proposition in the main text.
5. Use the NeurIPS 2026 template and anonymize repository-identifying details.

### 2. AI for Stochastic Dynamics

| field | verified information |
| --- | --- |
| Workshop | AI for Stochastic Dynamics: From Theoretical Foundations to Scientific Applications |
| Conference | NeurIPS 2026 |
| Date and place | December 11 or 12, 2026, Sydney, Australia |
| Official URL | <https://eethanshi.github.io/stochastic-dynamics-2026/> |
| OpenReview | <https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/STODY> |
| Submission deadline | August 29, 2026 at 23:59 AoE |
| Notification | September 29, 2026 AoE |
| Camera-ready | October 9, 2026 |
| Archival status | Not stated on the current official CFP or OpenReview venue page |
| Page limit | Short: up to 4 pages. Regular: up to 8 pages. References and appendices excluded. |
| Anonymity | The current OpenReview submission is private to authors and venue readers during review, but the CFP does not explicitly state single- or double-blind review. Recheck before submission. |
| Template | Not stated on the current CFP |
| Supplementary material | Appendices are permitted outside the page limit. A separate supplementary-file policy is not stated. |
| Dual submission | Not stated on the current CFP |
| Work stage | Short papers explicitly include preliminary results, focused technical observations, negative findings, position statements, and open problems |

Fit: Very high intellectually. The call explicitly includes diffusion,
flow-based, and score-based generative models and brings together stochastic
analysis, numerical simulation, reliable algorithms, and systematic
evaluation. Its short-paper description matches the contribution exactly.

Likely reviewer profile: Stochastic analysis, numerical simulation,
scientific machine learning, diffusion and flow-based generative modeling,
probabilistic modeling, and dynamical systems.

Estimated acceptance fit: Very high on topic, conditional on the venue
confirming non-archival status and acceptable dual-submission policy. Those
unpublished rules prevent it from being the frozen primary target on
2026-07-24.

Required paper changes:

1. Lead with fixed-step integration and transported signed defects.
2. Clarify why a deterministic probability-flow ODE is relevant to a
   stochastic-dynamics audience.
3. Use the four-page short-paper track.
4. Obtain written or published confirmation of archival, anonymity, template,
   and dual-submission rules before switching the primary target.

### 3. Disease Reasoning, Experimentation, And Modeling

| field | verified information |
| --- | --- |
| Workshop | DREAM: Disease Reasoning, Experimentation, And Modeling |
| Conference | NeurIPS 2026 |
| Date and place | Date and location not yet stated on the current CFP |
| Official URL | <https://ai-dream-workshop.github.io/neurips2026/> |
| Submission deadline | Not yet stated |
| Notification | Not yet stated |
| Archival status | Non-archival |
| Page limit | Research papers: up to 8 pages. Open problems: 4 pages. Tiny papers: 1 to 2 pages. |
| Anonymity | Not yet stated |
| Template | Not yet stated |
| Supplementary material | Not yet stated |
| Dual submission | Not yet stated |
| Work stage | Tiny papers may lack results; open-problem submissions are welcomed |

Fit: Low to moderate. Neural ODEs, SDEs, and flow matching are in scope, but
the workshop centers disease modeling and AI scientists. The repository has
no biological target, disease application, or experimentally grounded
claim.

Likely reviewer profile: Biological generative modeling, cellular dynamics,
geometric methods, AI for science, and disease modeling.

Estimated acceptance fit: Low without adding an application that would exceed
the minimum-work constraint. It is retained only as evidence that the current
2026 landscape includes a generative-flow venue, not as an actionable target.

Required paper changes: A credible disease-modeling connection and biological
validation would be required. Those changes are not recommended.

## Recommendation

Freeze **Geometric Distributional Deep Learning** as the primary target. It
has the strongest combination of confirmed non-archival status, exact rules,
four-page format, optimal-transport readership, generative-modeling scope,
and permission for ongoing and concurrently submitted work.

Keep **AI for Stochastic Dynamics** as the preferred intellectual alternative.
Switch only if its official CFP confirms non-archival status, anonymity,
template, and dual-submission rules before the paper freeze. No scientific
experiment is needed to make that switch.

Do not target the NeurIPS main conference. Do not target DREAM without a
genuine disease-modeling contribution.

## Title ranking for the recommended target

1. **When Averaged Field Regularity Fails to Rank Few-Step Generative Paths**
2. **On the Limits of Regularity-Based Schedule Ranking in Generative Flows**
3. **Solver Defects and Path Rankings in Few-Step Gaussian Generative Flows**
4. **A Controlled Gaussian Study of Regularity and Few-Step Sampling Error**
5. **Averaged Field Regularity Does Not Determine Fixed-Step Generative ODE Error**

The first title is specific, readable, and compatible with a controlled
limitation paper. The fifth is mathematically accurate under stated
assumptions but reads more universally than the empirical scope unless the
subtitle or abstract narrows it immediately.

## Pre-submission rule check

Recheck the selected official CFP no later than one week before submission.
In particular, verify the assigned workshop day, template version,
supplementary policy, anonymization details, archival status, and
dual-submission policy. A missing rule must remain missing in the paper
checklist until the organizers publish or confirm it.
