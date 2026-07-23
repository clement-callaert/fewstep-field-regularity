# Claims ledger

No claim may be marked supported using a single run.
No paper text may state a stronger claim than this ledger.

Allowed statuses: `proposed`, `under-test`, `supported`, `contradicted`,
`inconclusive`, `withdrawn`.

| claim ID | proposed claim | claim type | required evidence | supporting artifacts | contradictory evidence | status | reviewer notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Lower averaged global Lipschitzness is associated with lower fixed-NFE Wasserstein error. | hypothesis | Stratified Spearman, nested IDs, multi-seed, multi-family | | | proposed | Registered in Phase 0. |
| H2 | Path-distribution-weighted local Jacobian metrics predict fixed-NFE error better than global worst-case metrics. | hypothesis | Held-out and leave-one-family-out correlation improvement vs baseline | | | proposed | Registered in Phase 0. |
| H3 | Temporal stiffness and Jacobian variation explain errors not captured by spatial Lipschitzness. | hypothesis | Residual analysis after controlling for spatial metrics | | | proposed | Registered in Phase 0. |
| H4 | Metric rankings may change across solvers and target geometries. | hypothesis | Reproducible ranking inversions across at least two families or solvers | | | proposed | Registered in Phase 0. |
| GATE | Decision gate conditions for continuing to a full paper. | process | See docs/DECISION_GATE.md | | | under-test | Gate registered before benchmark. |
