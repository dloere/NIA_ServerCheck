# checks 폴더 Python 파일 기능 요약

이 문서는 `linux-checks/checks` 폴더 내 Python 스크립트들의 기능을 요약합니다. 각 점검 스크립트가 수정되거나 추가될 경우 이 문서도 함께 업데이트해야 합니다.

## cpu_check.py
CPU 사용률, 로드 평균, 실행 큐를 점검합니다. `/proc/stat` 및 `/proc/loadavg`에서 데이터를 읽어 CPU 사용률 (사용자, 시스템, 유휴, iowait+steal), 1분/5분/15분 로드 평균, 그리고 실행 가능한 태스크 수를 계산합니다. 임계치를 초과할 경우 경고(WARN) 또는 실패(FAIL)를 반환합니다. CPU를 많이 사용하는 상위 5개 프로세스 정보도 수집합니다.

## cron_check.py
Cron 작업 점검을 수행합니다. 현재는 "아직 구현되지 않음" 상태이며 항상 OK를 반환합니다.

## db_check.py
PostgreSQL 데이터베이스의 상태를 점검합니다. PostgreSQL 서비스가 특정 포트(6544)에서 리스닝 중인지, `systemctl`을 통해 서비스가 활성화(active)되어 있는지, 그리고 부팅 시 자동 시작(enabled)되는지 확인합니다. 서비스가 활성화되지 않았거나 포트가 리스닝하지 않으면 실패(FAIL), 자동 시작이 비활성화되어 있으면 경고(WARN)를 반환합니다.

## resource_check.py
시스템의 메모리 및 디스크 사용량을 점검합니다. `free -m` 명령어를 사용하여 메모리 사용률을 확인하고, `df -P` 명령어를 사용하여 각 마운트 지점의 디스크 사용률을 확인합니다. 스왑 메모리 점검은 현재 비활성화되어 있습니다. 설정된 임계치(예: 메모리 85%/90%, 디스크 85%/90%)를 초과할 경우 경고(WARN) 또는 실패(FAIL)를 반환합니다.

## temperature_check.py
시스템 온도를 점검합니다. `/sys/class/thermal` 또는 `sensors` 명령어를 통해 온도 센서 데이터를 수집하여 현재 온도를 보고하고, 설정된 임계치(WARN_C, FAIL_C)를 초과하는 온도가 감지되면 경고(WARN) 또는 실패(FAIL)를 반환합니다.

## ui_engine_check.py
UI 및 엔진 모듈의 실행 상태를 점검합니다. `sudo jps -l` 명령어를 사용하여 현재 실행 중인 Java 프로세스(jar 파일) 목록을 가져옵니다. 미리 정의된 `expected` jar 파일 목록과 비교하여 모든 필수 모듈이 실행 중인지 확인합니다. 누락된 모듈이 있을 경우 실패(FAIL)를 반환합니다. 특히 `app-nia.jar`의 실행 여부를 확인하여 UI 모듈의 정상 작동 여부를 보고합니다.

## ntt_engine_check.py
NTT Engine 유해 트래픽 관련 프로세스 점검을 수행합니다. `ps aux` 명령어를 통해 `python koren_main.py` 프로세스의 실행 여부와 PID를 확인합니다. 프로세스가 실행 중인 경우, 해당 PID로 `sudo ss -tanp` 명령어를 실행하여 `116.89.191.34` IP 주소로의 비정상적인 소켓 연결이 있는지 검증합니다. `koren_main.py` 프로세스가 실행 중이 아니거나 비정상적인 소켓 연결이 감지되면 실패(FAIL)를 반환합니다.

## docker_check.py
Docker 컨테이너의 실행 상태를 점검합니다. `docker ps` 명령어를 사용하여 모든 실행 중인 컨테이너의 상태를 확인합니다. 'Up' 상태가 아닌 컨테이너가 하나라도 발견되면 해당 컨테이너의 이름, ID, 상태를 보고하고 실패(FAIL)를 반환합니다. 모든 컨테이너가 정상적으로 'Up' 상태이면 성공(OK)을 반환합니다.

## django_ems_check.py
Django EMS 관련 프로세스의 실행 상태를 점검합니다. 다음 두 가지 유형의 프로세스를 확인합니다:
1.  `python3 manage.py runserver`: Django 웹 서버 프로세스가 실행 중인지 확인합니다.
2.  `python3 .*model.py`: 'model.py' 패턴을 가진 Python 스크립트 프로세스가 하나 이상 실행 중인지 확인합니다.
두 가지 프로세스 유형 중 하나라도 실행 중이지 않으면 실패(FAIL)를 반환합니다.

## chatbot_check.py
챗봇 서비스의 실행 상태를 점검합니다. `sudo ss -lptn` 명령어를 사용하여 8001 포트에서 `python` 프로세스가 리스닝 중인지 확인합니다. 8001 포트에서 `python` 프로세스가 정상적으로 리스닝 중이지 않으면 실패(FAIL)를 반환합니다.

## rabbitmq_check.py
RabbitMQ 메시징 서비스의 실행 상태를 점검합니다. `sudo systemctl status rabbitmq-server` 명령어를 사용하여 서비스가 'active (running)' 상태인지 확인합니다. 서비스가 정상적으로 실행 중이지 않으면 실패(FAIL)를 반환합니다.