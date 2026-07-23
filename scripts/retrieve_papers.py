"""Retrieve papers from legal public sources and update papers/manifest.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PaperEntry:
    paper_id: str
    title: str
    authors: str
    year: int
    venue_or_status: str
    source_url: str
    pdf_url: str | None
    local_filename: str
    relevance: str
    formulas_or_results_needed: list[str]
    notes_path: str


CATALOG: list[PaperEntry] = [
    PaperEntry(
        paper_id="albergo2023stochastic_interpolants",
        title="Stochastic Interpolants: A Unifying Framework for Flows and Diffusions",
        authors="Michael S. Albergo, Nicholas M. Boffi, Eric Vanden-Eijnden",
        year=2023,
        venue_or_status="arXiv preprint",
        source_url="https://arxiv.org/abs/2303.08797",
        pdf_url="https://arxiv.org/pdf/2303.08797.pdf",
        local_filename="albergo2023stochastic_interpolants.pdf",
        relevance="Probability paths, interpolants, velocity fields.",
        formulas_or_results_needed=[
            "interpolant definition",
            "conditional and marginal velocity formulas",
        ],
        notes_path="notes/albergo2023stochastic_interpolants.md",
    ),
    PaperEntry(
        paper_id="lipschitz_guided_2025",
        title=(
            "Lipschitz-Guided Design of Interpolation Schedules in Generative Models"
        ),
        authors="Yifan Chen, Eric Vanden-Eijnden, Jiawei Xu",
        year=2025,
        venue_or_status="arXiv preprint",
        source_url="https://arxiv.org/abs/2509.01629",
        pdf_url="https://arxiv.org/pdf/2509.01629.pdf",
        local_filename="lipschitz_guided_2025.pdf",
        relevance="Baseline Lipschitz-guided schedule and regularity proxy.",
        formulas_or_results_needed=[
            "Lipschitz-guided schedule definition",
            "averaged squared Lipschitzness proxy",
            "transfer formula between schedules",
        ],
        notes_path="notes/lipschitz_guided_2025.md",
    ),
    PaperEntry(
        paper_id="lipman2023flow_matching",
        title="Flow Matching for Generative Modeling",
        authors="Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, Matt Le",
        year=2023,
        venue_or_status="ICLR 2023",
        source_url="https://arxiv.org/abs/2210.02747",
        pdf_url="https://arxiv.org/pdf/2210.02747.pdf",
        local_filename="lipman2023flow_matching.pdf",
        relevance="Flow matching paths and conditional vector fields.",
        formulas_or_results_needed=[
            "OT and VP conditional flows",
            "conditional velocity",
        ],
        notes_path="notes/lipman2023flow_matching.md",
    ),
    PaperEntry(
        paper_id="liu2022rectified_flow",
        title="Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow",
        authors="Xingchao Liu, Chengyue Gong, Qiang Liu",
        year=2022,
        venue_or_status="arXiv preprint / ICLR version search",
        source_url="https://arxiv.org/abs/2209.03003",
        pdf_url="https://arxiv.org/pdf/2209.03003.pdf",
        local_filename="liu2022rectified_flow.pdf",
        relevance="Rectified flow and linear interpolation path.",
        formulas_or_results_needed=[
            "rectified flow ODE",
            "marginal preserving properties",
        ],
        notes_path="notes/liu2022rectified_flow.md",
    ),
    PaperEntry(
        paper_id="tong2024conditional_flow_matching",
        title=(
            "Improving and Generalizing Flow-Based Generative Models with "
            "Minibatch Optimal Transport"
        ),
        authors="Alexander Tong, Kilian Fatras, Nikolay Malkin, et al.",
        year=2024,
        venue_or_status="TMLR / arXiv",
        source_url="https://arxiv.org/abs/2302.00482",
        pdf_url="https://arxiv.org/pdf/2302.00482.pdf",
        local_filename="tong2024conditional_flow_matching.pdf",
        relevance="Conditional flow matching and simulation-free dynamic OT couplings.",
        formulas_or_results_needed=[
            "OT-CFM objective",
            "coupling construction",
        ],
        notes_path="notes/tong2024conditional_flow_matching.md",
    ),
    PaperEntry(
        paper_id="peyre2019computational_ot",
        title="Computational Optimal Transport",
        authors="Gabriel Peyre, Marco Cuturi",
        year=2019,
        venue_or_status="Foundations and Trends in Machine Learning",
        source_url="https://arxiv.org/abs/1803.00567",
        pdf_url="https://arxiv.org/pdf/1803.00567.pdf",
        local_filename="peyre2019computational_ot.pdf",
        relevance="Gaussian W2, entropic OT, displacement interpolation references.",
        formulas_or_results_needed=[
            "Gaussian W2 closed form",
            "entropic OT definition",
        ],
        notes_path="notes/peyre2019computational_ot.md",
    ),
    PaperEntry(
        paper_id="hairer2008solving_odes_i",
        title="Solving Ordinary Differential Equations I: Nonstiff Problems",
        authors="Ernst Hairer, Syvert P. Norsett, Gerhard Wanner",
        year=2008,
        venue_or_status="Springer book",
        source_url="https://link.springer.com/book/10.1007/978-3-540-78862-1",
        pdf_url=None,
        local_filename="hairer2008solving_odes_i.pdf",
        relevance="ODE local error, order, and stability analysis.",
        formulas_or_results_needed=[
            "Euler/Heun/RK4 order conditions",
            "local truncation error",
        ],
        notes_path="notes/hairer2008solving_odes_i.md",
    ),
    PaperEntry(
        paper_id="bonneel2015sliced_wasserstein",
        title="Sliced and Radon Wasserstein Barycenters of Measures",
        authors="Nicolas Bonneel, Julien Rabin, Gabriel Peyre, Hanspeter Pfister",
        year=2015,
        venue_or_status="Journal of Mathematical Imaging and Vision",
        source_url="https://arxiv.org/abs/1308.2074",
        pdf_url="https://arxiv.org/pdf/1308.2074.pdf",
        local_filename="bonneel2015sliced_wasserstein.pdf",
        relevance="Sliced Wasserstein estimation.",
        formulas_or_results_needed=[
            "sliced Wasserstein definition",
            "projection estimator",
        ],
        notes_path="notes/bonneel2015sliced_wasserstein.md",
    ),
    PaperEntry(
        paper_id="yang2024consistency_flow_matching",
        title="Consistency Flow Matching: Defining Straight Flows with Velocity Consistency",
        authors=(
            "Ling Yang, Zixiang Zhang, Zhilong Zhang, Xingchao Liu, Minkai Xu, "
            "Wentao Zhang, Chenlin Meng, Stefano Ermon, Bin Cui"
        ),
        year=2024,
        venue_or_status="arXiv preprint",
        source_url="https://arxiv.org/abs/2407.02398",
        pdf_url="https://arxiv.org/pdf/2407.02398.pdf",
        local_filename="yang2024consistency_flow_matching.pdf",
        relevance="Few-step flow discretization error and straight-flow motivation.",
        formulas_or_results_needed=[
            "few-step Euler error discussion",
            "straight flow motivation",
        ],
        notes_path="notes/yang2024consistency_flow_matching.md",
    ),
    PaperEntry(
        paper_id="gmflow_2025",
        title="Gaussian Mixture Flow Matching Models",
        authors=(
            "Hansheng Chen, Kai Zhang, Hao Tan, Zexiang Xu, Fujun Luan, "
            "Leonidas Guibas, Gordon Wetzstein, Sai Bi"
        ),
        year=2025,
        venue_or_status="arXiv preprint",
        source_url="https://arxiv.org/abs/2504.05304",
        pdf_url="https://arxiv.org/pdf/2504.05304.pdf",
        local_filename="gmflow_2025.pdf",
        relevance="Gaussian mixture flow fields and few-step sampling issues.",
        formulas_or_results_needed=[
            "mixture velocity parameterization",
            "discretization error discussion for mixtures",
        ],
        notes_path="notes/gmflow_2025.md",
    ),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_pdf(url: str, dest: Path, timeout_s: float = 60.0) -> None:
    # Download from a public URL only.
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "fewstep-field-regularity/0.1 (research; legal arxiv fetch)"
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        data = response.read()
    if not data.startswith(b"%PDF"):
        msg = f"Downloaded content is not a PDF: {url}"
        raise RuntimeError(msg)
    dest.write_bytes(data)


def note_template(entry: PaperEntry) -> str:
    return f"""# {entry.title}

- paper_id: `{entry.paper_id}`
- authors: {entry.authors}
- year: {entry.year}
- source_url: {entry.source_url}
- local_filename: {entry.local_filename}

## Relevance

{entry.relevance}

## Formulas or results needed

{chr(10).join(f"- {item}" for item in entry.formulas_or_results_needed)}

## Notation differences

To be filled after reading the PDF.

## Assumptions to check

- smoothness
- bounded support
- absolute continuity
- non-degenerate covariance

## Project satisfies assumptions?

Unknown until formulas are extracted from the source.

## Replication status

not-started

## Extracted equations

Do not reconstruct proofs from memory. Extract only after the PDF is available.
"""


def build_manifest_record(
    entry: PaperEntry,
    access_date: str,
    status: str,
    checksum: str | None,
    error: str | None,
) -> dict[str, Any]:
    return {
        "paper_id": entry.paper_id,
        "title": entry.title,
        "authors": entry.authors,
        "year": entry.year,
        "venue_or_status": entry.venue_or_status,
        "source_url": entry.source_url,
        "pdf_url": entry.pdf_url,
        "access_date": access_date,
        "version_date": None,
        "local_filename": entry.local_filename,
        "sha256": checksum,
        "relevance": entry.relevance,
        "formulas_or_results_needed": entry.formulas_or_results_needed,
        "notation_differences": [],
        "replication_status": "not-started",
        "notes_path": entry.notes_path,
        "retrieval_status": status,
        "retrieval_error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Only write metadata and note stubs without downloading PDFs.",
    )
    args = parser.parse_args()

    root = repo_root()
    papers_dir = root / "papers"
    pdf_dir = papers_dir / "pdfs"
    notes_dir = papers_dir / "notes"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    access_date = datetime.now(UTC).date().isoformat()
    records: list[dict[str, Any]] = []

    for entry in CATALOG:
        note_path = papers_dir / entry.notes_path
        if not note_path.exists():
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(note_template(entry), encoding="utf-8")

        dest = pdf_dir / entry.local_filename
        checksum: str | None = None
        status = "missing"
        error: str | None = None

        if dest.is_file():
            checksum = sha256_file(dest)
            status = "present"
        elif args.skip_download or entry.pdf_url is None:
            status = "missing"
            error = (
                "No public PDF URL configured or download skipped. "
                "Do not reconstruct proofs from memory."
            )
        else:
            try:
                download_pdf(entry.pdf_url, dest)
                checksum = sha256_file(dest)
                status = "downloaded"
            except (urllib.error.URLError, TimeoutError, RuntimeError, OSError) as exc:
                status = "missing"
                error = str(exc)

        records.append(
            build_manifest_record(entry, access_date, status, checksum, error)
        )

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "policy": "Legal public sources only. No paywall bypass.",
        "papers": records,
        "catalog_source": [asdict(entry) for entry in CATALOG],
    }
    manifest_path = papers_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Wrote {manifest_path}")
    present = sum(
        1 for r in records if r["retrieval_status"] in {"present", "downloaded"}
    )
    print(f"Papers present or downloaded: {present}/{len(records)}")


if __name__ == "__main__":
    main()
