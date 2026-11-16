"""Shape B — one ReAct agent.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from contextlib import closing
from typing import Any

from lab8 import durability, mock_llm
from lab8.db import connect
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))
    order_scope = {}
    order = {}

    def choose(*actions: tuple[str, dict[str, Any]]) -> dict[str, Any]:
        tool_names = ", ".join(name for name, _ in actions)
        response = mock_llm.complete(
            budget, seed=seed, purpose="react", prompt=f"Choose a read tool: {tool_names}"
        )
        # MockLLM returns a seeded digest for ReAct. Map it to the available actions.
        digest = response.split(":", 1)[1]
        name, args = actions[int(digest, 16) % len(actions)]
        trace.add("react_action", {"tool": name})
        return {"tool": name, "args": args}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        nonlocal order_scope, order
        last_tool = observation.get("last_tool")
        if last_tool is None:
            return choose(("get_claim_view", {"claim_id": claim_id}))

        result = observation["last_result"]
        if last_tool == "get_claim_view":
            if not result["found"]:
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            if not result["order_id"]:
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
            order_scope = {"order_id": result["order_id"], "principal_id": result["principal_id"]}
            return choose(("lookup_order", order_scope))

        if last_tool == "lookup_order":
            if not result["visible"]:
                return {"final": {"status": "escalated", "error_reason": result["reason"]}}
            order = result["order"]
            return choose(
                ("compute_compensation", {"order": order}),
                ("lookup_refund_history", order_scope),
            )

        if last_tool == "lookup_refund_history":
            trace.add("refund_history", {"refunded_vnd": result.get("refunded_vnd")})
            return choose(("compute_compensation", {"order": order}))

        # compute_compensation supplied the quote in the last tool observation.
        return {"final": {}}

    with closing(connect(store_path)) as conn:
        react = run_react(conn, budget, observation={}, decide=decide, max_steps=8, worker=True)
        final = react["final"]
        status = final.get("status")
        error_reason = final.get("error_reason")
        proposal = 0

        if status is None:
            quote = react["observation"]["last_result"]
            proposal = quote["amount_vnd"]
            trace.add("compute_compensation", {"amount_vnd": proposal})
            if proposal <= 0:
                status = "denied"
                error_reason = quote["reason"]
            else:
                # Send the full quote. The host applies approval and prior refunds.
                outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
                trace.add("issue_refund", {"ok": outcome["ok"], "reason": outcome["reason"]})
                if outcome["ok"]:
                    status = "resolved"
                else:
                    status = "failed" if outcome["conflict"] else "denied"
                    error_reason = outcome["reason"]

        trace.add("decision", {"status": status, "proposal_amount": proposal})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )
