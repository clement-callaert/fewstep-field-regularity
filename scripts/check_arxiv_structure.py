"""Structural checks T2--T13 for the restructured arXiv manuscript."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "arxiv" / "main.tex"

SEARCH_PHRASES = (
    "flow matching",
    "stochastic interpolants",
    "probability flow ODE",
    "few-step sampling",
    "sampling schedule",
    "schedule design",
    "Lipschitz constant",
    "Jacobian norm",
    "Wasserstein-2 distance",
    "Heun method",
    "Runge–Kutta",
    "number of function evaluations (NFE)",
)

BODY_FORBIDDEN = (
    "outputs/",
    ".json",
    ".py",
    "sha256",
    "commit",
    "scripts/",
    "pip install",
    "pytest",
)

REQUIRED_SECTIONS = (
    r"\\section{Introduction}",
    r"\\section{Background}",
    r"\\subsection{Gaussian interpolants and the marginal velocity field}",
    r"\\subsection{Solvers, evaluation budget, and endpoint error}",
    r"\\subsection{The averaged squared Jacobian criterion}",
    r"\\section{Method}",
    r"\\subsection{The variance-path invariant and the Cauchy--Schwarz bound}",
    r"\\subsection{A certified one-dimensional counterexample}",
    r"\\subsection{What the unsigned average discards}",
    r"\\subsection{Three regimes: comparator, in-family objective, unconstrained minimiser}",
    r"\\section{Experiments}",
    r"\\subsection{Setup}",
    r"\\subsection{Statistical treatment and what the counts mean}",
    r"\\subsection{R as a pairwise comparator: linear versus VP}",
    r"\\subsection{R as an in-family objective: VP versus the scalar log-covariance schedule}",
    r"\\subsection{The unconstrained R-minimiser}",
    r"\\subsection{Where the inversions live: a sweep over target variance}",
    r"\\subsection{Robustness to the random geometry}",
    r"\\subsection{Numerical validity controls}",
    r"\\section{Related work}",
    r"\\section{Conclusion}",
    r"\\section{Limitations}",
)

APPENDIX_SECTIONS = (
    r"\\section\{Proof of Proposition~\\ref\{prop:scalar\}\}",
    r"\\section\{Solver formulas and local truncation expansions\}",
    r"\\section\{Grid-aware Euler construction\}",
    r"\\section\{Full block tables\}",
    r"\\section\{Non-centered structural stress test\}",
    r"\\section\{Quadrature, precision, and interval procedures\}",
    r"\\section\{Robustness grids\}",
    r"\\section\{Reproducibility, artifacts, and provenance\}",
)


def body_and_appendix(text: str) -> tuple[str, str]:
    match = re.search(r"\\appendix", text)
    if match is None:
        raise ValueError("missing \\appendix")
    return text[: match.start()], text[match.start() :]


def abstract_text(text: str) -> str:
    match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, flags=re.S
    )
    if match is None:
        raise ValueError("missing abstract")
    return match.group(1)


def strip_tex(source: str) -> str:
    source = re.sub(r"%.*", "", source)
    source = source.replace("~", " ")
    source = source.replace("\\,", " ")
    source = source.replace("\\ ", " ")
    source = source.replace("--", "–")
    source = re.sub(r"\\[a-zA-Z]+\{", " ", source)
    source = re.sub(r"\\[a-zA-Z]+", " ", source)
    source = re.sub(r"[{}$]", "", source)
    source = re.sub(r"\s+", " ", source)
    return source.strip()


def intro_text(text: str) -> str:
    match = re.search(
        r"\\section\{Introduction\}(.*?)\\section\{Background\}", text, flags=re.S
    )
    if match is None:
        raise ValueError("missing introduction")
    return match.group(1)


def body_floats(body: str) -> tuple[int, int]:
    figures = len(re.findall(r"\\begin\{figure\}", body))
    tables = len(re.findall(r"\\begin\{table\}", body))
    return figures, tables


def custom_macros_in_abstract(abstract: str) -> list[str]:
    hits = []
    for macro in (r"\cR", r"\Rhat", r"\wtwo", r"\nBlocks", r"\citet"):
        if macro in abstract:
            hits.append(macro)
    return hits


def thirty_six_without_restriction(text: str) -> list[str]:
    """Return occurrences of 36 of 36 whose nearby window lacks the restriction."""
    pattern = re.compile(r"\$?36\$?\s+of\s+\$?36\$?")
    bad: list[str] = []
    for match in pattern.finditer(text):
        window = text[max(0, match.start() - 400) : match.end() + 400]
        collapsed = re.sub(r"\s+", " ", window)
        if "not a shared" not in collapsed or "interpolant" not in collapsed:
            bad.append(collapsed[:180])
    return bad


def main() -> None:
    text = TEX.read_text(encoding="utf-8")
    body, appendix = body_and_appendix(text)
    errors: list[str] = []
    for token in BODY_FORBIDDEN:
        if token in body:
            errors.append(f"body contains {token!r}")
    bad = thirty_six_without_restriction(text)
    if bad:
        errors.append(f"36 of 36 without restriction: {bad[0]}")
    abstract = abstract_text(text)
    if len(strip_tex(abstract)) > 1920:
        errors.append("abstract exceeds 1920 characters")
    hits = custom_macros_in_abstract(abstract)
    if hits:
        errors.append(f"abstract custom macros: {hits}")
    n_fig, n_tab = body_floats(body)
    if n_fig > 4 or n_tab > 3:
        errors.append(f"body floats figures={n_fig} tables={n_tab}")
    if errors:
        raise SystemExit("structure check failed:\n  " + "\n  ".join(errors))
    print("structure checks passed")


if __name__ == "__main__":
    main()
