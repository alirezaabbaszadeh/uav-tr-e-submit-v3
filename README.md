# uav-tr-e-submit-v3

Greenfield, manuscript-focused TR-E/Q1 submission pipeline that **does not rerun solvers**.

This repo reads a single **locked evidence campaign** (CSV/JSON artifacts) and regenerates:
- manuscript tables/figures
- camera-ready + anonymous PDFs
- a TR-E portal upload pack ZIP

## Prebuilt PDF (GitHub Releases)
The manuscript PDF and submission pack ZIP are **not committed** to git (they are generated outputs).

Download them from GitHub Releases (latest tag):
- `main.pdf`
- `TR_E_UPLOAD_PACK_journal_v3_full_20260219_000231.zip`
- `source_journal_v3_full_20260219_000231.zip`
- `FINAL_QA_REPORT_journal_v3_full_20260219_000231.json`

## Evidence (immutable input)
Default evidence source used in our lab setup:
- `/home/ali/code/UAV/uav_tr_e_project/outputs/campaigns/journal_v3_full_20260219_000231`

Required campaign metadata files:
- `CAMPAIGN_MANIFEST.json`, `RUN_PLAN.json`, `ENV_SNAPSHOT.json`, `COMMAND_LOG.csv`

Audit JSON (must be overall_pass=true):
- `/home/ali/code/UAV/uav_tr_e_project/outputs/audit/journal_readiness_journal_v3_full_20260219_000231.json`

## Quick start
1) Install deps (optional if already installed):
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-lock.txt
```

2) Run full pipeline:
```bash
PYTHONPATH=src python -m uavtre_submit_v3.run \
  --campaign-id journal_v3_full_20260219_000231 \
  --evidence-root /home/ali/code/UAV/uav_tr_e_project/outputs/campaigns \
  --audit-json /home/ali/code/UAV/uav_tr_e_project/outputs/audit/journal_readiness_journal_v3_full_20260219_000231.json \
  --mode full \
  --pdf-variant camera_ready
```

Outputs:
- `out/manuscript/camera_ready/main.pdf`
- `out/manuscript/anonymous/main.pdf`
- `out/submission/TR_E_UPLOAD_PACK_journal_v3_full_20260219_000231.zip`

## Notes
- Target journal: Transportation Research Part E.
- Positioning: routing-level (fleet logistics) vs trajectory-level DRL micro-control; cites Huang et al. (IEEE TCCN 2026).
- Heavy inputs/outputs are gitignored.
