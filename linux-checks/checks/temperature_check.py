import os
from typing import Tuple, List

from .py_common import run_cmd


WARN_C = 80.0
FAIL_C = 90.0


def _read_sysfs_temps() -> List[Tuple[str, float]]:
    temps = []
    base = "/sys/class/thermal"
    if not os.path.isdir(base):
        return temps
    for name in sorted(os.listdir(base)):
        if not name.startswith("thermal_zone"):
            continue
        zone_path = os.path.join(base, name)
        temp_path = os.path.join(zone_path, "temp")
        type_path = os.path.join(zone_path, "type")
        if not os.path.isfile(temp_path):
            continue
        try:
            raw = open(temp_path, "r", encoding="utf-8").read().strip()
            if not raw:
                continue
            value = float(raw)
            if value > 1000.0:
                value = value / 1000.0
            label = name
            if os.path.isfile(type_path):
                t = open(type_path, "r", encoding="utf-8").read().strip()
                if t:
                    label = f"{name}:{t}"
            temps.append((label, value))
        except Exception:
            continue
    return temps


def _read_sensors() -> List[Tuple[str, float]]:
    temps = []
    rc, out = run_cmd(["sensors", "-u"])
    if rc != 0 or not out.strip():
        return temps

    current_chip = None
    current_label = None
    for raw in out.splitlines():
        line = raw.rstrip()
        if not line:
            current_label = None
            continue
        if not line.startswith(" ") and not line.startswith("\t"):
            current_chip = line.strip()
            current_label = None
            continue
        if line.startswith("  ") or line.startswith("\t"):
            if line.strip().endswith(":"):
                current_label = line.strip().rstrip(":")
                continue
            if "_input:" in line:
                try:
                    k, v = line.strip().split(":", 1)
                    value = float(v.strip())
                    label = current_label or k.replace("_input", "")
                    if current_chip:
                        label = f"{current_chip}:{label}"
                    temps.append((label, value))
                except Exception:
                    continue
    return temps


def temperature_check() -> Tuple[int, str]:
    lines = ["[TEMP] temperature check start"]
    severity = 0

    temps = _read_sysfs_temps()
    source = "sysfs"
    if not temps:
        temps = _read_sensors()
        source = "sensors"

    if not temps:
        lines.append("[TEMP] no temperature sensors found")
        lines.append("[TEMP] result: WARN")
        return 1, "\n".join(lines)

    lines.append(f"[TEMP] source={source}, count={len(temps)}")

    max_temp = None
    max_label = None
    for label, value in temps:
        lines.append(f"[TEMP] {label}={value:.1f}C")
        if max_temp is None or value > max_temp:
            max_temp = value
            max_label = label
        if value >= FAIL_C:
            severity = max(severity, 2)
        elif value >= WARN_C:
            severity = max(severity, 1)

    if max_temp is not None:
        lines.append(f"[TEMP] max={max_temp:.1f}C at {max_label}")

    if severity == 2:
        lines.append("[TEMP] result: FAIL")
    elif severity == 1:
        lines.append("[TEMP] result: WARN")
    else:
        lines.append("[TEMP] result: OK")

    return severity, "\n".join(lines)
