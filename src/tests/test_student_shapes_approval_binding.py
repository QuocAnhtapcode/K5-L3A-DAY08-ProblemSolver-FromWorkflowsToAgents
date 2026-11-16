"""End-to-end check of the host's claim-bound approval across the student shapes."""

from __future__ import annotations

import json
from contextlib import closing

import pytest

from lab8.db import connect
from lab8.shapes import SHAPES


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_student_shape_rejects_another_claims_approval_on_retry(public_db, shape):
    with closing(connect(public_db)) as conn:
        conn.execute(
            """
            UPDATE claims
            SET approval_id = (SELECT approval_id FROM claims WHERE claim_id = 'C-014')
            WHERE claim_id = 'C-001'
            """
        )
        ledger_before = conn.execute("SELECT COUNT(*) FROM refund_ledger").fetchone()[0]
        conn.commit()

    for _ in range(2):
        result = SHAPES[shape]("C-001", seed=11, store_path=str(public_db))
        assert result.status == "denied"
        assert result.proposal_amount == 35_000
        assert result.error_reason == "approval_claim_mismatch"
        assert result.refund_effects == []
        assert result.committed_audit_count == 0

    with closing(connect(public_db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger").fetchone()[0] == ledger_before
        denials = conn.execute(
            """
            SELECT details_json FROM audit_events
            WHERE claim_id = 'C-001' AND event_type = 'policy_denied'
            """
        ).fetchall()
    assert [json.loads(row["details_json"])["reason"] for row in denials] == ["approval_claim_mismatch"]
