"""Structural checks for the restructured arXiv manuscript."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "arxiv" / "main.tex"

SEARCH_PHRASES = (
    "flow matching",
    "stochastic interpolants",
    "few-step sampling",
    "sampling schedule",
    "schedule design",
    "Jacobian",
    "Wasserstein-2",
    "Heun",
    "Runge–Kutta",
    "NFE",
    "flow-matching marginal",
    "score-based probability-flow",
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
    r"\\section{Definitions and standing assumptions}",
    r"\\section{Certified scalar Gaussian ranking inversion}",
    r"\\section{Solver-specific local error}",
    r"\\section{Grid-aware impossibility}",
    r"\\section{Finite Gaussian enumeration}",
    r"\\section{Related work}",
    r"\\section{Limitations}",
    r"\\section{Conclusion}",
)

APPENDIX_SECTIONS = (
    r"\\section\{Proof of Proposition~\\ref\{prop:scalar\}\}",
    r"\\section\{Solver formulas and local truncation expansions\}",
    r"\\section\{Class~S embedding of the grid-aware fields\}",
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
        r"\\section\{Introduction\}(.*?)\\section\{Definitions and standing assumptions\}",
        text,
        flags=re.S,
    )
    if match is None:
        raise ValueError("missing introduction")
    return match.group(1)


def body_floats(body: str) -> tuple[int, int]:
    figures = len(re.findall(r"\\begin\{figure\}", body))
    tables = len(re.findall(r"\\begin\{table\}", body))
    return figures, tables


FORBIDDEN_PHRASES = (
    r"regularity integral $\cR$ and Gaussian $\wtwo$ are available in closed form",
    "a Lipschitz constant of the marginal field",
    "every fixed-stage Runge--Kutta method samples",
    "pre-specified $36$-block",
    "on the same block",
    "would contradict",
    "complete census",
    "they prove no universal",
    "prove no universal ranking",
    "without a proved universal",
)


def abstract_word_count(abstract: str) -> int:
    return len(strip_tex(abstract).split())


def forbidden_phrase_hits(text: str) -> list[str]:
    return [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]


def custom_macros_in_abstract(abstract: str) -> list[str]:
    hits = []
    for macro in (r"\cR", r"\Rhat", r"\wtwo", r"\nBlocks", r"\citet"):
        if macro in abstract:
            hits.append(macro)
    return hits


def thirty_six_without_restriction(text: str) -> list[str]:
    """Return 36-of-36 claims whose window lacks a finite-enumeration fence."""
    pattern = re.compile(r"\$?36\$?\s+of\s+\$?36\$?")
    bad: list[str] = []
    for match in pattern.finditer(text):
        window = text[max(0, match.start() - 500) : match.end() + 500]
        collapsed = re.sub(r"\s+", " ", window).lower()
        has_four = (
            "four candidate" in collapsed
            or "four paths" in collapsed
            or "four specified" in collapsed
            or "four schedules" in collapsed
        )
        has_fence = (
            "tested block" in collapsed
            or "finite enumeration" in collapsed
            or "finite-census" in collapsed
            or "finite census" in collapsed
            or "does not imply" in collapsed
            or "not a global" in collapsed
        )
        if not (has_four and has_fence):
            bad.append(collapsed[:180])
    return bad


def not_shared_without_eigenvalue_hypothesis(text: str) -> list[str]:
    """Return 'not a shared' claims that omit distinct eigenvalues."""
    pattern = re.compile(r"not a (Class~S )?shared")
    bad: list[str] = []
    for match in pattern.finditer(text):
        window = text[max(0, match.start() - 350) : match.end() + 350]
        collapsed = re.sub(r"\s+", " ", window).lower()
        if "distinct" not in collapsed or "eigenvalue" not in collapsed:
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
    shared = not_shared_without_eigenvalue_hypothesis(text)
    if shared:
        errors.append(f"not-shared without eigenvalue hypothesis: {shared[0]}")
    abstract = abstract_text(text)
    n_words = abstract_word_count(abstract)
    if n_words < 150 or n_words > 280:
        errors.append(f"abstract word count {n_words} outside 150-280")
    if len(strip_tex(abstract)) > 1920:
        errors.append("abstract exceeds 1920 characters")
    forbidden = forbidden_phrase_hits(text)
    if forbidden:
        errors.append(f"forbidden phrasing: {forbidden[0]}")
    hits = custom_macros_in_abstract(abstract)
    if hits:
        errors.append(f"abstract custom macros: {hits}")
    n_fig, n_tab = body_floats(body)
    if n_fig > 4 or n_tab > 3:
        errors.append(f"body floats figures={n_fig} tables={n_tab}")
    if body.rfind(r"\section{Limitations}") > body.rfind(r"\section{Conclusion}"):
        errors.append("Limitations must precede Conclusion")
    if errors:
        raise SystemExit("structure check failed:\n  " + "\n  ".join(errors))
    print("structure checks passed")


if __name__ == "__main__":
    main()
