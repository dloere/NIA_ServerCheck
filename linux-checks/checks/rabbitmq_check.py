from typing import List, Tuple
from .py_common import run_cmd

def rabbitmq_check(sudo_prefix: List[str]) -> Tuple[int, str]:
    lines = ["[RABBITMQ] RabbitMQ 서비스 점검 시작"]
    severity = 0 # 0=OK, 1=WARN, 2=FAIL
    service_name = "rabbitmq-server"
    
    # 'sudo systemctl status rabbitmq-server' 명령어를 실행하여 서비스 상태를 가져옵니다.
    rc, out = run_cmd(sudo_prefix + ["systemctl", "status", service_name])
    
    if rc != 0:
        lines.append(f"[RABBITMQ] '{service_name}' 서비스 상태 확인 명령어 실행 실패 또는 서비스 비활성: {out.strip()} (FAIL)")
        # systemctl status는 서비스가 inactive/failed일 경우 3을 반환
        return 2, "
".join(lines)

    # 'Active: active (running)' 문자열이 출력에 포함되어 있는지 확인
    if "Active: active (running)" in out:
        lines.append(f"[RABBITMQ] '{service_name}' 서비스가 'active (running)' 상태입니다. (OK)")
    else:
        lines.append(f"[RABBITMQ] '{service_name}' 서비스가 'active (running)' 상태가 아닙니다. (FAIL)")
        lines.append(f"[RABBITMQ] 상태 정보:
{out.strip()}")
        severity = 2

    if severity == 0:
        lines.append("[RABBITMQ] RabbitMQ 서비스 점검 결과: OK")
    else:
        lines.append("[RABBITMQ] RabbitMQ 서비스 점검 결과: FAIL")

    return severity, "
".join(lines)
