from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .pack_builder import check_pack


@dataclass(frozen=True)
class QAChecks:
    audit_passed: bool
    evidence_lock_passed: bool
    manuscript_pdf_exists: bool
    latex_overfull_free: bool
    bibliography_count_ge_45: bool
    huang_cited_ge_2: bool
    required_tables_present: bool
    required_figures_present: bool
    pack_passed: bool


def _read_bibliography_count(bbl_path: Path) -> int | None:
    if not bbl_path.exists():
        return None
    bbl = bbl_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"\\begin\{thebibliography\}\{(\d+)\}", bbl)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _huang_cite_count(aux_path: Path) -> int:
    if not aux_path.exists():
        return 0
    aux = aux_path.read_text(encoding="utf-8", errors="ignore")
    return aux.count("huang2026tccn")


def run_qa(
    *,
    campaign_id: str,
    out_submission_dir: Path,
    out_manuscript_dir: Path,
    manuscript_root: Path,
    audit_recheck_json: Path,
    evidence_lock_json: Path,
) -> tuple[QAChecks, dict[str, object]]:
    # Audit gate.
    audit_passed = False
    if audit_recheck_json.exists():
        audit = json.loads(audit_recheck_json.read_text(encoding="utf-8"))
        summary = audit.get("summary", {})
        audit_passed = bool(summary.get("overall_pass", False))

    # Evidence gate.
    evidence_lock_passed = False
    if evidence_lock_json.exists():
        lock = json.loads(evidence_lock_json.read_text(encoding="utf-8"))
        evidence_lock_passed = bool(lock.get("passed", False))

    # Manuscript gates.
    pdf_path = out_manuscript_dir / "camera_ready" / "main.pdf"
    log_path = out_manuscript_dir / "camera_ready" / "main.log"
    bbl_path = out_manuscript_dir / "camera_ready" / "main.bbl"
    aux_path = out_manuscript_dir / "camera_ready" / "main.aux"

    manuscript_pdf_exists = pdf_path.exists()

    latex_overfull_free = False
    if log_path.exists():
        log_text = log_path.read_text(encoding="utf-8", errors="ignore")
        latex_overfull_free = "Overfull \\hbox" not in log_text

    bib_count = _read_bibliography_count(bbl_path)
    bibliography_count_ge_45 = bib_count is not None and bib_count >= 45

    huang_cited_ge_2 = _huang_cite_count(aux_path) >= 2

    required_tables = [
        manuscript_root / "generated" / "tables" / "tab_comm_params.tex",
        manuscript_root / "generated" / "tables" / "tab_tw_families.tex",
        manuscript_root / "generated" / "tables" / "tab_significance_summary.tex",
        manuscript_root / "generated" / "tables" / "tab_positioning_micro_vs_macro.tex",
    ]
    required_tables_present = all(p.exists() for p in required_tables)

    required_figures = [
        manuscript_root / "generated" / "figures" / "fig_conceptual_discretization.pdf",
    ]
    required_figures_present = all(p.exists() for p in required_figures)

    pack_path = out_submission_dir / f"TR_E_UPLOAD_PACK_{campaign_id}.zip"
    pack_check = check_pack(pack_path, campaign_id)
    pack_passed = bool(pack_check.get("passed", False))

    checks = QAChecks(
        audit_passed=audit_passed,
        evidence_lock_passed=evidence_lock_passed,
        manuscript_pdf_exists=manuscript_pdf_exists,
        latex_overfull_free=latex_overfull_free,
        bibliography_count_ge_45=bibliography_count_ge_45,
        huang_cited_ge_2=huang_cited_ge_2,
        required_tables_present=required_tables_present,
        required_figures_present=required_figures_present,
        pack_passed=pack_passed,
    )

    report = {
        "campaign_id": campaign_id,
        "checks": {
            "audit_passed": checks.audit_passed,
            "evidence_lock_passed": checks.evidence_lock_passed,
            "manuscript_pdf_exists": checks.manuscript_pdf_exists,
            "latex_overfull_free": checks.latex_overfull_free,
            "bibliography_count_ge_45": checks.bibliography_count_ge_45,
            "huang_cited_ge_2": checks.huang_cited_ge_2,
            "required_tables_present": checks.required_tables_present,
            "required_figures_present": checks.required_figures_present,
            "pack_passed": checks.pack_passed,
        },
        "bibliography": {"count": bib_count, "min_required": 45},
        "assets": {
            "required_tables": [p.as_posix() for p in required_tables],
            "required_figures": [p.as_posix() for p in required_figures],
        },
        "pack_check": pack_check,
    }

    report["passed"] = all(report["checks"].values())
    return checks, report
