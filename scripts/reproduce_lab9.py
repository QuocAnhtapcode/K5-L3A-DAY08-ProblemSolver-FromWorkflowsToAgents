"""Rebuild Lab 9 submission evidence; every expected negative is checked explicitly.

Run at repository root with .venv/Scripts/python.exe scripts/reproduce_lab9.py.
Reports are produced by their owning modules, never patched by this script.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def main():
    # Native Windows consoles can default to cp1252; child modules emit UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    log = []

    def run(module, *args, expected=0, contains=None):
        command = [sys.executable, "-m", module, *args]
        title = "python -m " + " ".join([module, *args])
        print(f"\n$ {title}", flush=True)
        result = subprocess.run(command, cwd=SRC, env={**os.environ, "PYTHONUTF8": "1"},
                                capture_output=True, text=True, encoding="utf-8")
        output = result.stdout + result.stderr
        print(output, end="", flush=True)
        log.append(f"$ {title}\n{output}process exit {result.returncode}\n")
        if result.returncode != expected or (contains and contains not in output):
            raise RuntimeError(f"{title}: expected exit {expected}, got {result.returncode}")
        clean = "\n".join(line.rstrip() for line in "\n".join(log).splitlines())
        (SRC / "reports/lab9_validation.log").write_text(clean + "\n", encoding="utf-8")

    if sys.argv[1:] == ["--finalize"]:
        # Refresh only document rendering after a documentation fix; retain the
        # full measured validation log instead of rerunning unchanged agents.
        previous = SRC / "reports/lab9_validation.log"
        log.append(previous.read_text(encoding="utf-8").rstrip())
        if "process exit 1" not in log[0] or "mutation score 3/3" not in log[0]:
            raise RuntimeError("No completed evaluation log to finalize; run the full command first")
        run("lab9.evidence")
        print("\nLab 9 evidence finalization PASS.")
        return

    run("lab9.smoke")
    run("lab9.evalset", "--build", "--check")
    run("lab9.evalset", "--v2", "--build")
    run("pytest", "-q")
    run("pytest", "-q", "-m", "student", "-o", "addopts=")
    run("lab9.judge", "--csv", "data/eval/judge_tone_public.csv", "--audit", "5")
    run("lab9.judge", "--csv", "data/eval/judge_helpful_public.csv", "--audit", "5", expected=1,
        contains="FAIL floors")
    for spec, suffix in (("config/metric_spec.yaml", "v1"), ("config/metric_spec_v2.yaml", "v2")):
        base = f"reports/baseline_{suffix}.json"
        run("lab9.eval", "--shape", "swarm", "--spec", spec, "--out", base)
        run("lab9.gate", "--pr", base, "--baseline", base, "--spec", spec, "--base-spec", spec)
        for shape in ("fixed", "seeded_regression"):
            path = f"reports/eval_{shape}.json" if suffix == "v1" else f"reports/eval_{shape}_v2.json"
            run("lab9.eval", "--shape", shape, "--spec", spec, "--out", path)
            run("lab9.gate", "--pr", path, "--baseline", base, "--spec", spec, "--base-spec", spec,
                expected=int(shape == "seeded_regression"),
                contains="pass_rate" if shape == "seeded_regression" else "exit 0")
        if suffix == "v1":
            run("lab9.ci_check", "--pr", base, "--baseline", base, "--spec", spec)
    run("lab9.mutation", "--detect")
    spec, base = "config/metric_spec_v2.yaml", "reports/baseline_v2.json"
    run("lab9.mutation", "--spec", spec, "--aa", "66,77,88,99,110")
    run("lab9.mutation", "--spec", spec, "--baseline", base, "--base-spec", spec,
        contains="mutation score 3/3")
    run("lab9.eval", "--shape", "slice_regression", "--spec", spec, "--out", "reports/eval_slice_regression.json")
    run("lab9.traps", "--pr", "reports/eval_slice_regression.json", "--baseline", base, "--spec", spec)
    for trap in ("evaluator_errors_as_nan", "dropped_failing_rows", "cherry_picked_seeds", "loosened_spec"):
        trap_spec = f"reports/traps/{trap}.spec.yaml" if trap == "loosened_spec" else spec
        run("lab9.gate", "--pr", f"reports/traps/{trap}.json", "--baseline", base,
            "--spec", trap_spec, "--base-spec", spec, expected=1, contains="INTEGRITY")
    run("lab9.evidence")
    print("\nLab 9 reproduction PASS; see src/reports/lab9_validation.log.")


if __name__ == "__main__":
    main()
