# Paper index

Papers are retrieved only from legal public sources such as arXiv, OpenReview,
journal author pages, and official proceedings. Do not bypass authentication
or paywalls.

Manifest file: [manifest.json](manifest.json)

Retrieval command:

```bash
python scripts/retrieve_papers.py
```

If a PDF cannot be accessed, the manifest records `retrieval_status: missing`
and proofs must not be reconstructed from memory.

## Required bibliographic fields

For every paper record:

- title
- authors
- year
- venue or review status
- source URL
- access date
- version date
- local filename
- SHA256 checksum
- relevance
- formulas or results needed
- notation differences
- replication status

## Initial catalog

| ID | Title | Source | Local PDF | Status |
| --- | --- | --- | --- | --- |
| albergo2023stochastic_interpolants | Stochastic Interpolants | arXiv:2303.08797 | pdfs/albergo2023stochastic_interpolants.pdf | see manifest |
| lipschitz_guided_2025 | Lipschitz-Guided Design of Interpolation Schedules | arXiv:2509.01629 | pdfs/lipschitz_guided_2025.pdf | see manifest |
| lipman2023flow_matching | Flow Matching for Generative Modeling | arXiv:2210.02747 | pdfs/lipman2023flow_matching.pdf | see manifest |
| liu2022rectified_flow | Rectified Flow | arXiv:2209.03003 | pdfs/liu2022rectified_flow.pdf | see manifest |
| tong2024conditional_flow_matching | Minibatch OT / Conditional Flow Matching | arXiv:2302.00482 | pdfs/tong2024conditional_flow_matching.pdf | see manifest |
| peyre2019computational_ot | Computational Optimal Transport | arXiv:1803.00567 | pdfs/peyre2019computational_ot.pdf | see manifest |
| hairer2008solving_odes_i | Solving ODEs I | Springer book page | n/a unless author-legal PDF | likely missing |
| bonneel2015sliced_wasserstein | Sliced and Radon Wasserstein Barycenters | arXiv:1308.2074 | pdfs/bonneel2015sliced_wasserstein.pdf | see manifest |
| yang2024consistency_flow_matching | Consistency Flow Matching | arXiv:2407.02398 | pdfs/yang2024consistency_flow_matching.pdf | see manifest |
| gmflow_2025 | Gaussian Mixture Flow Matching Models | arXiv:2504.05304 | pdfs/gmflow_2025.pdf | see manifest |

## Notes

Structured notes live under `notes/`. Proposition drafts live under
`notes/propositions/` and must use allowed proof statuses only.
