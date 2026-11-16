"""Regression tests for the B3 verifier and the pre-write boundary."""

from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path

import pytest

from bonus import swarm_verified
from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.schemas import Budget
from lab8.trace import Trace


def test_c002_verifies_before_refund(public_db):
    result = swarm_verified.run_claim("C-002", seed=55, store_path=str(public_db))
    assert (result.status, result.proposal_amount, result.refund_effects) == ("denied", 0, [])
    assert result.run_id == "R-swarm_verified-C-002-s55"
    events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
    assert [event["payload"] for event in events if event["kind"] == "verifier_override"] == [
        {"fields": ["delay_days"]}
    ]
    with closing(connect(public_db)) as conn:
        assert get_refund(conn, "C-002") is None


def test_verifier_repairs_status_damage_and_delay_in_one_round(public_db):
    trusted = {
        "delay_days": 2, "status": "in_transit", "damage_verified": False,
        "paid_vnd": 120_000, "shipping_fee_vnd": 20_000,
    }
    candidate = dict(trusted, delay_days=8, status="delivered", damage_verified=True)
    budget = Budget()
    trace = Trace("B3-verifier-contract")
    with closing(connect(public_db)) as conn:
        assert swarm_verified.verified_quote(conn, budget, trace, candidate, trusted) == 0
    assert budget.tool_calls == 2
    assert trace.events == [
        {"kind": "verifier_override", "payload": {"fields": ["delay_days", "status", "damage_verified"]}}
    ]


def test_verified_swarm_resumes_after_commit_without_refunding_twice(public_db):
    with pytest.raises(InjectedCrash):
        swarm_verified.run_claim(
            "C-012", seed=55, store_path=str(public_db), crash_at="after_effect_before_checkpoint"
        )
    result = swarm_verified.run_claim("C-012", seed=55, store_path=str(public_db))
    assert result.status == "resolved"
    assert len(result.refund_effects) == 1
    with closing(connect(public_db)) as conn:
        assert get_refund(conn, "C-012")["amount_vnd"] == 35_000
        assert committed_audit_count(conn, "C-012") == 1
