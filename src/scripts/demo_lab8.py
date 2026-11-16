"""Run the ProblemSolver Lab 8 demo against temporary SQLite stores."""

from __future__ import annotations

import argparse
import time
from contextlib import chdir, closing
from pathlib import Path
from tempfile import TemporaryDirectory

from bonus.swarm_verified import run_claim as run_verified_swarm
from lab8 import benchmark
from lab8.app import PUBLIC_CLAIMS, PUBLIC_WORLD, prepare_store, run_shape
from lab8.config_loader import repo_path
from lab8.console import utf8_stdio
from lab8.crash_test import run_suite
from lab8.db import connect, load_json, load_jsonl
from lab8.demo.buggy_workflow import main as show_unsafe_refund
from lab8.durability import InjectedCrash
from lab8.handoff import ALLOWED_FIELDS
from lab8.metrics import ledger_snapshot, trial_pass

BASELINE_SHAPES = ("workflow", "single", "orchestrator", "swarm")
SECTIONS = ("shapes", "handoff", "policy", "crash", "benchmark", "bonus")


def verify(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def vnd(amount: int | float) -> str:
    return f"{amount:,}".replace(",", ".")


def live_claim(labels: dict, shape: str, claim_id: str, seed: int = 11, *, expected_miss: str | None = None):
    store = Path("stores") / f"{shape}-{claim_id}-{seed}.sqlite"
    prepare_store(store)
    started_at = time.time()
    result = (
        run_verified_swarm(claim_id, seed=seed, store_path=str(store))
        if shape == "swarm_verified"
        else run_shape(shape, claim_id, seed=seed, store_path=str(store))
    )
    with closing(connect(store)) as conn:
        snap = ledger_snapshot(conn, claim_id)
        passed, reason = trial_pass(result.as_dict(), labels[claim_id], conn, started_at=started_at)
    verify(
        (passed, reason) == ((False, expected_miss) if expected_miss else (True, "ok")),
        f"Kết quả không khớp kịch bản: {shape}, {claim_id}",
    )
    print(
        f"{shape:14} {claim_id} seed {seed:<2} {result.status:<10} "
        f"quote {vnd(result.proposal_amount):>7} | ledger {vnd(snap['refund_vnd']):>7} VND | "
        f"model={result.model_calls} | committed={snap['committed_audit_count']} | "
        f"policy_denied={snap['policy_denied']}"
    )
    return result


def show_shapes(labels: dict) -> None:
    print("1. Bốn kiến trúc xử lý cùng đơn trễ đủ điều kiện")
    for shape in BASELINE_SHAPES:
        result = live_claim(labels, shape, "C-001")
        if shape == "single":
            events = load_json(result.trace_path)["events"]
            tools = [event["payload"]["tool"] for event in events if event["kind"] == "react_action"]
            print("  ReAct chọn công cụ đọc: " + " → ".join(tools))


def show_handoff(labels: dict) -> None:
    print("2. Handoff và trace an toàn trên C-010")
    result = live_claim(labels, "orchestrator", "C-010")
    events = load_json(result.trace_path)["events"]
    handoffs = [event["payload"] for event in events if event["kind"] == "handoff"]
    verify(len(handoffs) == 1, "Cần đúng một handoff")
    handoff = handoffs[0]
    verify(
        set(handoff) <= ALLOWED_FIELDS and handoff["allowed_tools"] == ["lookup_order"],
        "Handoff vượt quyền hoặc có trường ngoài allowlist",
    )
    print(f"  Quyền: {handoff['principal_scope']} | công cụ: {', '.join(handoff['allowed_tools'])}")
    print("  Trường handoff: " + ", ".join(sorted(handoff)))
    print(f"  Kiểm tra trace và ledger theo nhãn public: OK | {result.run_id}")


def show_policy(labels: dict) -> None:
    print("3. Phê duyệt và trần hoàn theo đơn")
    for claim_id in ("C-007", "C-013", "C-014"):
        result = live_claim(labels, "workflow", claim_id)
        if result.error_reason:
            print("  Lý do: " + result.error_reason)


def show_crash() -> None:
    print("4. Phản ví dụ và khôi phục C-012 trên cùng SQLite")
    show_unsafe_refund()
    claim_id = "C-012"
    store = Path("stores") / "workflow-crash.sqlite"
    prepare_store(store)

    def state(label: str, expected_checkpoint: int) -> None:
        with closing(connect(store)) as conn:
            snap = ledger_snapshot(conn, claim_id)
            checkpoints = conn.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'",
                (claim_id,),
            ).fetchone()[0]
        verify(
            (snap["refund_count"], snap["committed_audit_count"], snap["refund_vnd"], checkpoints)
            == (1, 1, 35_000, expected_checkpoint),
            "Refund, audit hoặc checkpoint không đúng",
        )
        print(f"  {label}: refund=1 | refund_committed=1 | checkpoint={checkpoints} | 35.000 VND")

    try:
        run_shape("workflow", claim_id, seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")
    except InjectedCrash as exc:
        print("  Crash mô phỏng: " + str(exc))
    else:
        raise RuntimeError("Không xảy ra crash như kịch bản")
    state("Ngay sau crash", 0)
    result = run_shape("workflow", claim_id, seed=11, store_path=str(store))
    verify(result.status == "resolved", "Workflow chưa khôi phục")
    state("Chạy lại cùng SQLite", 1)
    crash = run_suite(Path("suite"))
    verify(crash["crash_safety"] == "20/20", "Crash suite chưa đạt")
    print("  Crash suite chạy trực tiếp: " + crash["crash_safety"])


def show_benchmark(claims: list[dict], live: bool) -> None:
    print("5. Benchmark public và lý do chọn Workflow")
    stored = load_json(repo_path("reports", "benchmark.json"))
    report = stored
    if live:
        report = benchmark.run_benchmark(
            world=load_json(PUBLIC_WORLD),
            claims=claims,
            shapes=list(BASELINE_SHAPES),
            seeds=stored["controlled_variables"]["seeds"],
        )
        verify(report == stored, "Benchmark chạy lại khác báo cáo đã nộp")
        print("  Chạy lại khớp JSON đã lưu.")
    else:
        print("  Đọc số liệu từ reports/benchmark.json.")
    print(benchmark.render_table(report))


def show_bonus(labels: dict) -> None:
    print("6. C-002 và bonus B3: ticket 5 ngày, đơn 2 ngày, ngưỡng 3 ngày")
    for shape in ("workflow", "swarm", "swarm_verified"):
        live_claim(labels, shape, "C-002", 55, expected_miss="status resolved != denied" if shape == "swarm" else None)
    events = load_json(Path("traces") / "R-swarm_verified-C-002-s55.json")["events"]
    corrections = [event["payload"]["fields"] for event in events if event["kind"] == "verifier_override"]
    verify(corrections == [["delay_days"]], "Verifier không ghi đúng một lần sửa delay_days")
    print("  verifier_override: " + ", ".join(corrections[0]))
    for suite in ("public", "adversarial"):
        report = load_json(repo_path("reports", f"bonus_b3_{suite}.json"))
        baseline = report["by_shape"]["swarm"]
        variant = report["by_shape"]["swarm_verified"]
        audit = report["b3"]["by_shape"]["swarm_verified"]
        print(
            f"  Báo cáo {suite}: Swarm {baseline['successes']}/{baseline['trials']} → "
            f"verified {variant['successes']}/{variant['trials']}; sửa dữ kiện={audit['verifier_overrides']}; "
            f"secret={audit['secret_leak_count']}, PII={audit['pii_leak_count']}, "
            f"approval bypass={audit['approval_bypass_count']}"
        )


def main() -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--section", choices=("all", *SECTIONS), default="all")
    parser.add_argument("--live-benchmark", action="store_true", help="Rerun CP5 and compare with the saved JSON")
    args = parser.parse_args()
    claims = load_jsonl(PUBLIC_CLAIMS)
    labels = {claim["claim_id"]: claim["expected"] for claim in claims}
    actions = {
        "shapes": lambda: show_shapes(labels),
        "handoff": lambda: show_handoff(labels),
        "policy": lambda: show_policy(labels),
        "crash": show_crash,
        "benchmark": lambda: show_benchmark(claims, args.live_benchmark),
        "bonus": lambda: show_bonus(labels),
    }
    with TemporaryDirectory(prefix="logix-demo-", ignore_cleanup_errors=True) as scratch, chdir(scratch):
        for section in SECTIONS if args.section == "all" else (args.section,):
            actions[section]()
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
