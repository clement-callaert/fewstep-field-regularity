# Claims ledger

No claim may be marked supported using a single run.
No paper text may state a stronger claim than this ledger.

Allowed statuses: `proposed`, `under-test`, `supported`, `contradicted`,
`inconclusive`, `withdrawn`.

| claim ID | proposed claim | claim type | required evidence | supporting artifacts | contradictory evidence | status | reviewer notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Lower averaged global Lipschitzness is associated with lower fixed-NFE Wasserstein error. | hypothesis | Stratified Spearman, nested IDs, multi-seed, multi-family | phase3_gate_analysis_final_audit_2026-07-23-v2:correlations | Opposite signs across Gaussian and mixture family strata | inconclusive | One registered gate run. Sampling unit is configuration; seeds are nested. |
| H2 | Path-distribution-weighted local Jacobian metrics predict fixed-NFE error better than global worst-case metrics. | hypothesis | Held-out and leave-one-family-out correlation improvement vs baseline | | phase3_gate_analysis_final_audit_2026-07-23-v2:correlations | contradicted | No registered alternative reaches the improvement threshold. |
| H3 | Temporal stiffness and Jacobian variation explain errors not captured by spatial Lipschitzness. | hypothesis | Residual analysis after controlling for spatial metrics | | phase3_gate_analysis_final_audit_2026-07-23-v2:correlations | inconclusive | The temporal residual association is small and positive, but no support threshold was registered for it. |
| H4 | Metric rankings may change across solvers and target geometries. | hypothesis | Reproducible ranking inversions across at least two families or solvers | phase3_gate_analysis_final_audit_2026-07-23-v2:inversions; phase3_gate_analysis_final_audit_2026-07-23-v2:interactions | Euler-specific evidence triggers pivot rule 8 | under-test | Condition 2 holds after uncalibrated dimension 8 mixture blocks are excluded. One registered gate run cannot mark the claim supported. |
| GATE | Decision gate conditions for continuing to a full paper. | process | See docs/DECISION_GATE.md | phase3_gate_analysis_final_audit_2026-07-23-v2:decision | Superseded analysis outputs contained reporting defects and uncalibrated mixture evidence | under-test | Continue to Phase 4 review only. Do not start Phase 5 before human review. |
| P4-C1 | The baseline regularity ordering does not determine the fixed-NFE path ordering in the tested exact Gaussian configurations. | Phase 4 empirical claim | Clean reproduction, precision audit, and a limited mathematical explanation | | Dirty-code Phase 3 observations only | under-test | Run 1 is configured but has not been launched. |
| P4-C2 | The preferred path depends on the solver in the tested low-rank Gaussian configurations. | Phase 4 empirical claim | Clean reproduction at both dimensions and all registered NFE budgets, followed by precision checks | | Dirty-code Phase 3 observations only | under-test | One clean run will not be sufficient to mark this supported. |
| P4-C3 | A solver-specific local error quantity explains the observed path preference better than the averaged regularity baseline. | Phase 4 explanatory claim | Derived quantity, source audit, numerical checks, and out-of-sample validation | | No Phase 4 diagnostic run | proposed | Any diagnostic designed from Phase 3 remains post-hoc. |
| P4-P1 | A minimal affine proposition establishes non-implication between averaged regularity ordering and fixed-step numerical error ordering. | proposition | Explicit assumptions, complete derivation or construction, counterexample search, numerical checks, and expert review | | No proposition has been stated | proposed | Final status must remain needs expert review in the mathematical analysis until manual approval. |
