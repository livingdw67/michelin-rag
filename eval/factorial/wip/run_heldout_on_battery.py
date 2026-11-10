"""Answer the 300 held-out questions with qwen3, a battery charge at a time.

For a laptop that can only charge while it's switched off. Run this until it stops at the battery floor, shut down and
charge, then run it again: each run picks up where the last one stopped. Questions go in a seeded order stratified by
(type, company), so at any stopping point the finished questions keep the mix of the full 300. They run in chunks through
eval.factorial.deferred. Local model only, nothing is billed. Ollama must be running.

    python -u eval/factorial/wip/run_heldout_on_battery.py [--floor 20]

Exit 0 when all 300 have an outcome, 4 at the battery floor, 2 after repeated failures.
"""
import ctypes
import json
import os
import random
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RESULTS = REPO / "eval" / "factorial" / "results"
OUT = "pending_local_r2_heldout.jsonl"
PENDING = RESULTS / OUT
LOG = RESULTS / "local_r2_heldout.log"
ORDER = RESULTS / "local_r2_heldout_order.json"
# Percent; 20 leaves the laptop usable and stops before low-battery GPU throttling. Keep any lower floor above the
# Windows critical level (hibernate at 2% here), so a run ends cleanly instead of being cut off.
FLOOR = int(sys.argv[sys.argv.index("--floor") + 1]) if "--floor" in sys.argv else 20
CHUNK = 20
SEED = 20261109
ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001


class PowerStatus(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte), ("BatteryLifePercent", ctypes.c_ubyte),
                ("SystemStatusFlag", ctypes.c_ubyte), ("BatteryLifeTime", ctypes.c_ulong),
                ("BatteryFullLifeTime", ctypes.c_ulong)]


def percent():
    s = PowerStatus()
    ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
    return s.BatteryLifePercent


def stratified_order():
    """Systematic sample within each (type, company) cell, so any prefix keeps each cell's share of the 300."""
    held = set(json.loads((REPO / "eval" / "factorial" / "split.json").read_text(encoding="utf-8"))["heldout"])
    cells = defaultdict(list)
    for line in (REPO / "eval" / "factorial" / "questions.jsonl").read_text(encoding="utf-8").splitlines():
        q = json.loads(line)
        if q["id"] in held:
            cells[(q["type"], q["company"])].append(q["id"])
    rng = random.Random(SEED)
    keyed = []
    for key in sorted(cells):
        ids = sorted(cells[key])
        rng.shuffle(ids)
        offset = rng.random()
        keyed += [((i + offset) / len(ids), qid) for i, qid in enumerate(ids)]
    return [qid for _, qid in sorted(keyed)]


def finished():
    """Questions with a scored outcome (same rule as deferred.answer: errors other than a runaway are retried)."""
    done = set()
    if PENDING.exists():
        for line in PENDING.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row["status"] != "error" or row.get("error", "").startswith("LengthFinishReasonError"):
                done.add(row["id"])
    return done


def say(message):
    print(time.strftime("%H:%M:%S"), message, f"(battery {percent()}%)", flush=True)


def main():
    order = stratified_order()
    ORDER.write_text(json.dumps({"seed": SEED, "stratified_by": ["type", "company"], "order": order}, indent=0),
                     encoding="utf-8")
    env = {**os.environ, "LLM_PROFILE": "local", "CHAT_MODEL": "qwen3-8b-12k", "REWRITE_MODEL": "qwen3-8b-12k",
           "LLM_REASONING_EFFORT": "none", "PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(REPO)}
    python = str(REPO / ".venv" / "Scripts" / "python.exe")
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)  # no idle sleep during the run
    failures = 0
    while True:
        done = finished()
        todo = [q for q in order if q not in done]
        if not todo:
            say(f"finished: all {len(order)} held-out questions have an outcome")
            return 0
        if percent() <= FLOOR:
            say(f"battery floor reached: {len(done)}/{len(order)} done. Shut down, charge, and run this again")
            return 4
        chunk = todo[:CHUNK]
        say(f"{len(done)}/{len(order)} done, next {len(chunk)}")
        cmd = [python, "-u", "-m", "eval.factorial.deferred", "answer", "--only", ",".join(chunk), "--workers", "2",
               "--out", OUT]
        with open(LOG, "a", encoding="utf-8") as log:
            proc = subprocess.Popen(cmd, cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT)
            while proc.poll() is None:
                time.sleep(10)
                if percent() <= FLOOR:
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
                    proc.wait()
                    break
        if percent() > FLOOR and len(finished()) == len(done):  # a whole chunk with no progress: a crash or Ollama is down
            failures += 1
            if failures >= 3:
                say(f"stopped after repeated failures: {len(done)}/{len(order)} done, is Ollama running? See {LOG}")
                return 2


if __name__ == "__main__":
    sys.exit(main())
