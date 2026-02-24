#!/usr/bin/env bash
set -euo pipefail

CAMPAIGN_ID="${1:-journal_v3_full_20260219_000231}"
EVIDENCE_ROOT="${2:-/home/ali/code/UAV/uav_tr_e_project/outputs/campaigns}"
AUDIT_JSON="${3:-/home/ali/code/UAV/uav_tr_e_project/outputs/audit/journal_readiness_${CAMPAIGN_ID}.json}"

PYTHONPATH=src python -m uavtre_submit_v3.run \
  --campaign-id "$CAMPAIGN_ID" \
  --evidence-root "$EVIDENCE_ROOT" \
  --audit-json "$AUDIT_JSON" \
  --mode full \
  --pdf-variant camera_ready
