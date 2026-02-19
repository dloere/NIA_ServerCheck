import os
import time
from typing import Tuple

from .py_common import run_cmd


def _read_proc_stat() -> Tuple[int, int, int, int, int]:
    with open("/proc/stat", "r", encoding="utf-8") as f:
        first = f.readline().strip()
    parts = first.split()
    if len(parts) < 9 or parts[0] != "cpu":
        raise ValueError("unexpected /proc/stat format")

    user = int(parts[1]) + int(parts[2])  # user + nice
    system = int(parts[3]) + int(parts[6]) + int(parts[7])  # system + irq + softirq
    idle = int(parts[4])
    iowait = int(parts[5])
    steal = int(parts[8])
    total = sum(int(x) for x in parts[1:])
    return total, user, system, idle + iowait, iowait + steal


def _read_loadavg() -> Tuple[float, float, float, int]:
    with open("/proc/loadavg", "r", encoding="utf-8") as f:
        raw = f.read().strip()
    parts = raw.split()
    if len(parts) < 4:
        raise ValueError("unexpected /proc/loadavg format")
    l1 = float(parts[0])
    l5 = float(parts[1])
    l15 = float(parts[2])
    runq = int(parts[3].split("/")[0])
    return l1, l5, l15, runq


def cpu_check() -> Tuple[int, str]:
    lines = ["[CPU] CPU check start"]
    severity = 0  # 0=OK, 1=WARN, 2=FAIL

    try:
        t0, u0, s0, i0, ws0 = _read_proc_stat()
        time.sleep(1.0)
        t1, u1, s1, i1, ws1 = _read_proc_stat()
    except Exception as e:  # pragma: no cover
        lines.append(f"[CPU] failed to collect /proc/stat: {e}")
        return 2, "\n".join(lines)

    total_delta = t1 - t0
    if total_delta <= 0:
        lines.append("[CPU] invalid cpu delta from /proc/stat")
        return 2, "\n".join(lines)

    user_pct = ((u1 - u0) * 100.0) / total_delta
    system_pct = ((s1 - s0) * 100.0) / total_delta
    idle_pct = ((i1 - i0) * 100.0) / total_delta
    iowait_steal_pct = ((ws1 - ws0) * 100.0) / total_delta
    used_pct = 100.0 - idle_pct

    lines.append(
        "[CPU] usage {:.1f}% (user {:.1f}% / system {:.1f}% / idle {:.1f}% / iowait+steal {:.1f}%)".format(
            used_pct, user_pct, system_pct, idle_pct, iowait_steal_pct
        )
    )

    if used_pct >= 95.0:
        lines.append("[CPU] total usage too high: FAIL")
        severity = max(severity, 2)
    elif used_pct >= 85.0:
        lines.append("[CPU] total usage high: WARN")
        severity = max(severity, 1)

    try:
        l1, l5, l15, runq = _read_loadavg()
    except Exception as e:  # pragma: no cover
        lines.append(f"[CPU] failed to collect /proc/loadavg: {e}")
        return 2, "\n".join(lines)

    cpu_count = os.cpu_count() or 1
    r1 = l1 / cpu_count
    r5 = l5 / cpu_count
    r15 = l15 / cpu_count
    lines.append(
        "[CPU] load avg 1/5/15m = {:.2f}/{:.2f}/{:.2f}, cores={}, ratio={:.2f}/{:.2f}/{:.2f}".format(
            l1, l5, l15, cpu_count, r1, r5, r15
        )
    )

    if r1 >= 2.0 or r5 >= 1.5:
        lines.append("[CPU] sustained load ratio high: FAIL")
        severity = max(severity, 2)
    elif r1 >= 1.2 or r5 >= 1.0:
        lines.append("[CPU] load ratio elevated: WARN")
        severity = max(severity, 1)

    lines.append(f"[CPU] run queue={runq} (runnable tasks)")
    if runq > (cpu_count * 2):
        lines.append("[CPU] run queue indicates bottleneck: FAIL")
        severity = max(severity, 2)
    elif runq > cpu_count:
        lines.append("[CPU] run queue above core count: WARN")
        severity = max(severity, 1)

    rc, out = run_cmd(["ps", "-eo", "pid,comm,%cpu", "--sort=-%cpu"])
    if rc == 0 and out.strip():
        lines.append("[CPU] top cpu processes")
        for row in out.splitlines()[1:6]:
            lines.append(f"[CPU] {row.strip()}")
    else:
        lines.append("[CPU] failed to collect top cpu processes")
        severity = max(severity, 1)

    if severity == 2:
        lines.append("[CPU] result: FAIL")
    elif severity == 1:
        lines.append("[CPU] result: WARN")
    else:
        lines.append("[CPU] result: OK")

    return severity, "\n".join(lines)
