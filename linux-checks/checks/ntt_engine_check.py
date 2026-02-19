from typing import List, Tuple
from .py_common import run_cmd

def ntt_engine_check(sudo_prefix: List[str]) -> Tuple[int, str]:
    lines = ["[NTT_ENGINE] NTT Engine 유해 트래픽 관련 프로세스 점검 시작"]
    severity = 0 # 0=OK, 1=WARN, 2=FAIL
    koren_pid = None
    target_ip = "116.89.191.34"
    process_name = "koren_main.py"

    # 1단계: koren_main.py 프로세스 확인
    rc, out = run_cmd(["ps", "aux"])
    if rc != 0:
        lines.append(f"[NTT_ENGINE] 'ps aux' 명령어 실행 실패: {out.strip()} (FAIL)")
        return 2, "
".join(lines)

    for line in out.splitlines():
        if process_name in line and "python" in line and "grep" not in line:
            parts = line.split()
            try:
                koren_pid = int(parts[1]) # PID는 두 번째 컬럼
                lines.append(f"[NTT_ENGINE] '{process_name}' 프로세스 실행 확인. PID: {koren_pid} (OK)")
                break
            except ValueError:
                continue

    if koren_pid is None:
        lines.append(f"[NTT_ENGINE] '{process_name}' 프로세스가 실행 중이지 않습니다. (FAIL)")
        return 2, "
".join(lines)

    # 2단계: 비정상 소켓 연결 확인
    # 'sudo ss -tanp'를 사용하여 프로세스 ID와 함께 소켓 정보 확인
    rc, out = run_cmd(sudo_prefix + ["ss", "-tanp"])
    if rc != 0:
        lines.append(f"[NTT_ENGINE] 'sudo ss -tanp' 명령어 실행 실패: {out.strip()} (FAIL)")
        return 2, "
".join(lines)

    # koren_main.py 프로세스의 비정상 소켓 연결 확인
    # '116.89.191.34' IP 주소와 koren_pid를 모두 포함하는 라인 필터링
    abnormal_connections = []
    for line in out.splitlines():
        if target_ip in line and f"pid={koren_pid}" in line:
            abnormal_connections.append(line.strip())

    if abnormal_connections:
        lines.append(f"[NTT_ENGINE] '{process_name}' (PID: {koren_pid})에서 '{target_ip}'(으)로의 비정상적인 소켓 연결 감지: (FAIL)")
        for conn in abnormal_connections:
            lines.append(f"[NTT_ENGINE]   - {conn}")
        severity = max(severity, 2)
    else:
        lines.append(f"[NTT_ENGINE] '{process_name}' (PID: {koren_pid})에서 '{target_ip}'(으)로의 비정상적인 소켓 연결 없음. (OK)")


    if severity == 0:
        lines.append("[NTT_ENGINE] NTT Engine 점검 결과: OK")
    elif severity == 1:
        lines.append("[NTT_ENGINE] NTT Engine 점검 결과: WARN") # 현재는 WARN이 나올 수 있는 경로 없음
    else:
        lines.append("[NTT_ENGINE] NTT Engine 점검 결과: FAIL")

    return severity, "
".join(lines)
