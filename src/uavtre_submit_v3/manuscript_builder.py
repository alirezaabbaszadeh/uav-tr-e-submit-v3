from __future__ import annotations

import subprocess
from pathlib import Path


def ensure_anonymous_wrapper(manuscript_root: Path) -> Path:
    """Create main_anonymous.tex if missing."""

    wrapper = manuscript_root / "main_anonymous.tex"
    if wrapper.exists():
        return wrapper

    wrapper.write_text(
        "% Auto-generated wrapper for anonymous build.\n"
        "% Do not include author identifiers in this wrapper.\n"
        "\\def\\ANON{1}\\input{main.tex}\n",
        encoding="utf-8",
    )
    return wrapper


def compile_manuscript(*, repo_root: Path, manuscript_root: Path, outdir: Path, variant: str) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)

    if variant not in {"anonymous", "camera_ready"}:
        raise ValueError(f"unknown variant: {variant}")

    if variant == "anonymous":
        main_tex = ensure_anonymous_wrapper(manuscript_root)
    else:
        main_tex = manuscript_root / "main.tex"

    if not main_tex.exists():
        raise FileNotFoundError(main_tex)

    cmd = [
        "latexmk",
        "-pdf",
        "-g",
        "-cd",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={outdir.resolve().as_posix()}",
        main_tex.relative_to(repo_root).as_posix(),
    ]

    proc = subprocess.run(cmd, cwd=repo_root, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        log = outdir / "latexmk_submit_v3.log"
        log.write_text((proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8")
        raise RuntimeError(f"latexmk failed for {variant} (see {log.as_posix()})")

    # Normalize to main.pdf.
    pdf = outdir / "main.pdf"
    if pdf.exists():
        return pdf

    candidates = list(outdir.glob("*.pdf"))
    if candidates:
        candidates[0].replace(pdf)

    if not pdf.exists():
        raise FileNotFoundError(pdf)

    return pdf
