from typing import Tuple

from .py_common import run_cmd


def resource_check() -> Tuple[int, str]:
    lines = ["[RESOURCE] 리소스 점검 시작"]
    mem_warn = 85
    mem_fail = 90
    # swap check disabled for now
    # swap_warn = 50
    # swap_fail = 80
    disk_warn = 85
    disk_fail = 90

    rc, out = run_cmd(["free", "-m"])
    if rc != 0:
        lines.append("[RESOURCE] 메모리 정보 수집 실패: FAIL")
        return 2, "\n".join(lines)
    mem_total = mem_avail = None
    swap_total = swap_used = None
    for line in out.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            mem_total = int(parts[1])
            mem_avail = int(parts[6])
        if line.startswith("Swap:"):
            parts = line.split()
            swap_total = int(parts[1])
            swap_used = int(parts[2])

    mem_rc = 0
    if mem_total is None or mem_avail is None:
        lines.append("[RESOURCE] 메모리 정보 수집 실패: FAIL")
        mem_rc = 2
    else:
        mem_used = mem_total - mem_avail
        mem_pct = (mem_used * 100) // mem_total
        if mem_pct >= mem_fail:
            lines.append(f"[RESOURCE] 메모리 사용률 {mem_pct}% (FAIL)")
            mem_rc = 2
        elif mem_pct >= mem_warn:
            lines.append(f"[RESOURCE] 메모리 사용률 {mem_pct}% (WARN)")
            mem_rc = 1
        else:
            lines.append(f"[RESOURCE] 메모리 사용률 {mem_pct}% (OK)")

    # 스왑 메모리 점검은 현재 보류 중이므로 비활성화합니다.
    # 관련 변수 (swap_total, swap_used, swap_warn, swap_fail) 및 로직은 제거됩니다.
    swap_rc = 0
    lines.append("[RESOURCE] 스왑 메모리 점검은 현재 비활성화되어 있습니다. (OK)")


    rc, out = run_cmd(["df", "-P"])
    if rc != 0:
        lines.append("[RESOURCE] 디스크 정보 수집 실패: FAIL")
        disk_rc = 2
    else:
        disk_rc = 0
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
                disk_rc = 2
            elif usep_num >= disk_warn:
                lines.append(f"[RESOURCE] 디스크 사용률 {usep} (WARN) mount={mount} fs={fs}")
                if disk_rc < 1:
                    disk_rc = 1
            else:
                lines.append(f"[RESOURCE] 디스크 사용률 {usep} (OK) mount={mount} fs={fs}")

    if mem_rc == 2 or disk_rc == 2:
        lines.append("[RESOURCE] 리소스 점검 결과: FAIL")
        return 2, "\n".join(lines)
    if mem_rc == 1 or disk_rc == 1:
        lines.append("[RESOURCE] 리소스 점검 결과: WARN")
        return 1, "\n".join(lines)
    lines.append("[RESOURCE] 리소스 점검 결과: OK")
    return 0, "\n".join(lines)
