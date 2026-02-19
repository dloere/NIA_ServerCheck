import re
from typing import List, Tuple
from .py_common import run_cmd

def django_ems_check(sudo_prefix: List[str]) -> Tuple[int, str]:
    lines = ["[DJANGO_EMS] Django EMS 프로세스 점검 시작"]
    severity = 0 # 0=OK, 1=WARN, 2=FAIL

    # 1단계: 'python3 manage.py runserver' 프로세스 확인
    runserver_process_found = False
    rc, out = run_cmd(["ps", "aux"]) # 'sudo_prefix'는 일반적으로 ps aux에 필요하지 않으므로 사용하지 않음
    if rc != 0:
        lines.append(f"[DJANGO_EMS] 'ps aux' 명령어 실행 실패: {out.strip()} (FAIL)")
        return 2, "
".join(lines)

    for line in out.splitlines():
        # 'grep' 자체 프로세스 제외
        if "grep" in line:
            continue
        if "python3 manage.py runserver" in line:
            runserver_process_found = True
            lines.append(f"[DJANGO_EMS] 'python3 manage.py runserver' 프로세스 실행 확인: {line.strip()} (OK)")
            break

    if not runserver_process_found:
        lines.append("[DJANGO_EMS] 'python3 manage.py runserver' 프로세스가 실행 중이지 않습니다. (FAIL)")
        severity = max(severity, 2)

    # 2단계: 'python3 .*model.py' 프로세스 확인
    model_process_count = 0
    model_pattern = re.compile(r"python3 .*model\.py")
    
    # ps aux 결과를 다시 파싱하거나, 한 번의 호출로 처리 (여기서는 재사용)
    for line in out.splitlines():
        if "grep" in line:
            continue
        if model_pattern.search(line):
            model_process_count += 1
            # lines.append(f"[DJANGO_EMS] 모델 프로세스 실행 확인: {line.strip()}") # 너무 많은 로그 방지
    
    if model_process_count > 0:
        lines.append(f"[DJANGO_EMS] '{model_process_count}'개의 'python3 .*model.py' 프로세스 실행 중. (OK)")
    else:
        lines.append("[DJANGO_EMS] 'python3 .*model.py' 패턴의 프로세스가 실행 중이지 않습니다. (FAIL)")
        severity = max(severity, 2)
        
    if severity == 0:
        lines.append("[DJANGO_EMS] Django EMS 프로세스 점검 결과: OK")
    else:
        lines.append("[DJANGO_EMS] Django EMS 프로세스 점검 결과: FAIL")

    return severity, "
".join(lines)
