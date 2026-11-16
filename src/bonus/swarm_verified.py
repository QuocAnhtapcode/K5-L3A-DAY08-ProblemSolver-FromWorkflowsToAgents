"""Swarm with a code verifier between the tentative quote and the host write."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import Any

from lab8 import durability
from lab8.db import connect
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "swarm_verified"
QUOTE_FIELDS = ("delay_days", "status", "damage_verified")


def verified_quote(
    conn: sqlite3.Connection,
    budget: Budget,
    trace: Trace,
    candidate: dict[str, Any],
    trusted_order: dict[str, Any],
) -> int:
    """Quote the candidate once and repair it at most once using the scoped order."""
    budget.add_tool(tool_cost())
    proposal = compute_compensation(conn, candidate)["amount_vnd"]
    changed_fields = [field for field in QUOTE_FIELDS if candidate.get(field) != trusted_order[field]]
    if changed_fields:
        trace.add("verifier_override", {"fields": changed_fields})
        budget.add_tool(tool_cost())
        proposal = compute_compensation(conn, trusted_order)["amount_vnd"]
    return proposal


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    with closing(connect(store_path)) as conn:
        def done(status: str, *, proposal: int = 0, reason: str | None = None) -> RunResult:
            trace.add("decision", {"status": status, "proposal_amount": proposal})
            return finish(
                conn,
                shape=SHAPE,
                claim_id=claim_id,
                seed=seed,
                status=status,
                proposal_amount=proposal,
                budget=budget,
                trace=trace,
                error_reason=reason,
            )

        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim["found"]:
            return done("failed", reason="unknown_claim")

        ticket = claim["ticket"]
        complete(budget, seed=seed, purpose="peer", prompt=ticket)
        parsed_delay = parse_delay_days(ticket)
        complete(budget, seed=seed, purpose="parse", prompt=ticket)
        if not claim["order_id"]:
            complete(budget, seed=seed, purpose="draft", prompt="needs_info")
            return done("needs_info", reason="missing_order_id")

        handoff = make_handoff(
            request_id=f"REQ-{claim_id}",
            claim_id=claim_id,
            task="check_applicable_policy",
            facts={},
            allowed_tools=["lookup_order", "lookup_policy"],
        )
        trace.add("handoff", handoff)
        tools = run_readonly_investigators(conn, budget, handoff, claim["principal_id"])["tools"]
        order_view = tools["lookup_order"]
        trace.add("investigator", {"order_visible": order_view["visible"], "policy_count": len(tools["lookup_policy"]["policies"])})
        if not order_view["visible"]:
            complete(budget, seed=seed, purpose="draft", prompt="escalated")
            return done("escalated", reason=order_view["reason"])

        trusted_order = order_view["order"]
        candidate = dict(trusted_order)
        # Reproduce the reference Swarm's tentative evidence choice for the comparison.
        if seed % 5 == 0 and parsed_delay is not None:
            candidate["delay_days"] = parsed_delay

        proposal = verified_quote(conn, budget, trace, candidate, trusted_order)
        trace.add("quote", {"amount_vnd": proposal})
        complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
        if proposal == 0:
            return done("denied", reason="no_entitlement")

        outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        if outcome["ok"]:
            return done("resolved", proposal=proposal)
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal=proposal, reason=outcome["reason"])
