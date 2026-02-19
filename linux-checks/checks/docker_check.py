from typing import List, Tuple
from .py_common import run_cmd

def docker_check(sudo_prefix: List[str]) -> Tuple[int, str]:
    lines = ["[DOCKER] Docker 컨테이너 점검 시작"]
    severity = 0 # 0=OK, 1=WARN, 2=FAIL

    # 'docker ps' 명령어를 실행하여 실행 중인 컨테이너 목록을 가져옵니다.
    # --format 옵션을 사용하여 CONTAINER ID, NAMES, STATUS만 가져오도록 합니다.
    # 이렇게 하면 파싱이 더 쉬워집니다.
    rc, out = run_cmd(sudo_prefix + ["docker", "ps", "--format", "{{.ID}}	{{.Names}}	{{.Status}}"])
    if rc != 0:
        lines.append(f"[DOCKER] 'docker ps' 명령어 실행 실패: {out.strip()} (FAIL)")
        return 2, "
".join(lines)

    # 헤더 라인 제거
    container_lines = out.strip().splitlines()
    if not container_lines:
        lines.append("[DOCKER] 실행 중인 Docker 컨테이너가 없습니다. (OK)")
        return 0, "
".join(lines)

    failed_containers = []
    for line in container_lines:
        parts = line.split('	')
        if len(parts) >= 3:
            container_id = parts[0]
            container_name = parts[1]
            container_status = parts[2]

            # STATUS가 'Up'으로 시작하는지 확인 (예: 'Up 3 months')
            if not container_status.startswith("Up"):
                failed_containers.append(f"이름: {container_name}, ID: {container_id}, 상태: {container_status}")

    if failed_containers:
        lines.append("[DOCKER] 비정상 상태의 Docker 컨테이너가 감지되었습니다: (FAIL)")
        for container_info in failed_containers:
            lines.append(f"[DOCKER]   - {container_info}")
        severity = 2
    else:
        lines.append("[DOCKER] 모든 Docker 컨테이너가 정상적으로 실행 중입니다. (OK)")

    if severity == 2:
        lines.append("[DOCKER] Docker 컨테이너 점검 결과: FAIL")
    else:
        lines.append("[DOCKER] Docker 컨테이너 점검 결과: OK")

    return severity, "
".join(lines)
