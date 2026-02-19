from typing import List, Tuple
from .py_common import run_cmd

def chatbot_check(sudo_prefix: List[str]) -> Tuple[int, str]:
    lines = ["[CHATBOT] 챗봇 서비스 점검 시작"]
    severity = 0 # 0=OK, 1=WARN, 2=FAIL
    target_port = "8001"
    process_name = "python"

    # 'sudo ss -lptn' 명령어를 실행하여 리스닝 중인 소켓 정보를 가져옵니다.
    rc, out = run_cmd(sudo_prefix + ["ss", "-lptn"])
    if rc != 0:
        lines.append(f"[CHATBOT] 'sudo ss -lptn' 명령어 실행 실패: {out.strip()} (FAIL)")
        return 2, "
".join(lines)

    found_chatbot_process = False
    for line in out.splitlines():
        # 8001 포트와 python 프로세스가 동시에 존재하는 라인 확인
        if f":{target_port}" in line and f'"{process_name}"' in line:
            lines.append(f"[CHATBOT] 8001 포트에서 챗봇(python) 프로세스 리스닝 확인: {line.strip()} (OK)")
            found_chatbot_process = True
            break

    if not found_chatbot_process:
        lines.append(f"[CHATBOT] 8001 포트에서 챗봇(python) 프로세스가 리스닝 중이지 않습니다. (FAIL)")
        severity = 2

    if severity == 0:
        lines.append("[CHATBOT] 챗봇 서비스 점검 결과: OK")
    else:
        lines.append("[CHATBOT] 챗봇 서비스 점검 결과: FAIL")

    return severity, "
".join(lines)
