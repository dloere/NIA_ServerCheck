from typing import List, Tuple

from .py_common import run_cmd


def resource_check(sudo_prefix: List[str]) -> Tuple[int, str]:
    lines = ["[RESOURCE] 리소스 점검 시작"]
    severity = 0
    mem_warn = 85
    mem_fail = 90
    disk_warn = 85
    disk_fail = 90

    # 메모리 점검
    rc, out = run_cmd(sudo_prefix + ["free", "-m"])
    if rc != 0:
        lines.append("[RESOURCE] 메모리 정보 수집 실패: FAIL")
        return 2, "\n".join(lines)
    
    mem_total = mem_avail = None
    for line in out.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            mem_total = int(parts[1])
            mem_avail = int(parts[6])

    if mem_total is None or mem_avail is None:
        lines.append("[RESOURCE] 메모리 정보 파싱 실패: FAIL")
        severity = max(severity, 2)
    else:
        mem_used = mem_total - mem_avail
        mem_pct = (mem_used * 100) // mem_total
        if mem_pct >= mem_fail:
            lines.append(f"[RESOURCE] 메모리 사용률 {mem_pct}% (FAIL)")
            severity = max(severity, 2)
        elif mem_pct >= mem_warn:
            lines.append(f"[RESOURCE] 메모리 사용률 {mem_pct}% (WARN)")
            severity = max(severity, 1)
        else:
            lines.append(f"[RESOURCE] 메모리 사용률 {mem_pct}% (OK)")

    lines.append("[RESOURCE] 스왑 메모리 점검은 현재 비활성화되어 있습니다. (OK)")

    # 디스크 점검
    rc, out = run_cmd(sudo_prefix + ["df", "-P"])
    if rc != 0:
        lines.append("[RESOURCE] 디스크 정보 수집 실패: FAIL")
        severity = max(severity, 2)
    else:
        for line in out.splitlines():
            if line.startswith("Filesystem"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            fs, usep, mount = parts[0], parts[4], parts[5]
            usep_num = int(usep.rstrip("%"))
            if usep_num >= disk_fail:
                lines.append(f"[RESOURCE] 디스크 사용률 {usep} (FAIL) mount={mount} fs={fs}")
                severity = max(severity, 2)
            elif usep_num >= disk_warn:
                lines.append(f"[RESOURCE] 디스크 사용률 {usep} (WARN) mount={mount} fs={fs}")
                severity = max(severity, 1)
            else:
                lines.append(f"[RESOURCE] 디스크 사용률 {usep} (OK) mount={mount} fs={fs}")

    if severity == 2:
        lines.append("[RESOURCE] 리소스 점검 결과: FAIL")
    elif severity == 1:
        lines.append("[RESOURCE] 리소스 점검 결과: WARN")
    else:
        lines.append("[RESOURCE] 리소스 점검 결과: OK")
        
    return severity, "\n".join(lines)
