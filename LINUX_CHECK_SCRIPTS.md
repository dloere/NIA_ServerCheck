# 리눅스 서버 점검 스크립트 개발 메모

이 문서는 Codex가 이 폴더의 목적과 현재 구조를 즉시 이해하기 위한 인수인계용 요약이다.

목적
- 사내망 리눅스 서버 점검 스크립트를 외부에서 개발한 뒤, 내부로 옮겨 실행한다.
- 전체 점검을 오케스트레이션하는 상위 스크립트와, 기능별 하위 점검 스크립트로 분리한다.
- 특정 점검만 수정할 수 있도록 모듈형 구조를 유지한다.
- 현재는 Python 기반으로 완전 전환했으며, Bash 스크립트는 제거되었다.

대상 환경
- OS: Ubuntu 20.04.2 LTS
- PostgreSQL: 12.x (패키지: postgresql-12, client 12.14, postgresql-common 214ubuntu0.1)
- systemd 서비스: postgresql.service, postgresql@12-main.service (active)
- JVM 프로세스 확인: sudo jps -l 사용 (UI/엔진 모듈 점검)

현재 구조 (기준 경로: D:\Work\testScript)
- 최상단: LINUX_CHECK_SCRIPTS.md (이 문서)
- 하위 폴더: linux-checks
- linux-checks/check_runner.py : Python 일괄 점검 오케스트레이션 스크립트
- linux-checks/checks.conf : 점검 활성/비활성 설정
- linux-checks/build_pyinstaller.sh : PyInstaller 빌드 스크립트 (리눅스)
- linux-checks/checks/py_common.py : Python 공통 유틸
- linux-checks/checks/checks_summary.md : 각 점검 스크립트의 기능을 요약하며, 점검 스크립트 수정 시 반드시 함께 업데이트해야 합니다.
- linux-checks/checks/db_check.py : Python DB 점검
- linux-checks/checks/cron_check.py : Python cron 점검
- linux-checks/checks/ui_engine_check.py : Python UI/엔진 모듈 점검
- linux-checks/checks/resource_check.py : Python 리소스 점검

동작 개요
- check_runner.py 실행 시 checks.conf를 읽어 점검을 순차 실행한다.
- 각 점검 스크립트는 독립적으로 수정/교체 가능하다.
- 점검 스크립트는 표준 출력으로 요약을 출력하고, exit code로 상태를 표현한다.
- 로그는 check_runner.py 기준 경로의 history/<연도>/ 아래에 생성된다.
- UI/엔진 모듈 점검은 sudo jps -l 출력의 두 번째 컬럼(경로)을 개별 매칭한다.
- app-nia.jar가 존재하면 UI 정상 로그를 추가로 남긴다.
- 리소스 점검은 메모리/스왑/디스크 임계치 기반으로 WARN/FAIL 판단한다.

다음 작업 후보
- 점검 항목 확장 (10개 이상 예정)
- Python 단일 실행 파일 배포 시 리눅스에서 PyInstaller 빌드 필요
- PyInstaller 빌드 시 생성되는 check_runner.spec는 기본적으로 유지해도 무방 (불필요하면 수동 삭제)

# Gemini CLI의 역할 이해

LINUX_CHECK_SCRIPTS.md 문서를 바탕으로 저의 역할은 다음과 같습니다:

저는 Python 기반의 모듈식 리눅스 서버 점검 스크립트 시스템을 지원합니다. 저의 책임은 check_runner.py 오케스트레이션 스크립트가 checks.conf를 통해 구성된 다양한 개별 점검 스크립트(예: db_check.py, cron_check.py)를 순차적으로 실행하는 아키텍처를 이해하는 것을 포함합니다. 저는 이 스크립트들이 Ubuntu 20.04.2 LTS를 대상으로 하며, PostgreSQL 및 JVM 프로세스와 같은 특정 서비스를 점검하고, 요약을 출력하며, 로그를 생성한다는 것을 인지해야 합니다. 저의 궁극적인 목표는 새로운 점검 항목 추가 또는 PyInstaller 빌드 관리와 같은 작업을 포함하여 이 시스템의 개발, 유지보수 및 확장을 용이하게 하는 것입니다.