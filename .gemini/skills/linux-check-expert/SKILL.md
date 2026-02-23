---
name: linux-check-expert
description: 리눅스 서버 점검 스크립트(Python 기반)의 개발, 유지보수 및 확장을 위한 전문 지침입니다. 점검 스크립트 수정, 신규 점검 추가, 빌드 관리 시 이 스킬을 활성화하세요.
---

# 리눅스 점검 스크립트 전문가 지침

이 스킬은 `linux-checks` 프로젝트의 모듈형 구조와 개발 원칙을 준수하도록 설계되었습니다.

## 1. 프로젝트 구조 이해
- **오케스트레이터:** `linux-checks/check_runner.py` (전체 점검 제어)
- **설정:** `linux-checks/checks.conf` (점검 활성/비활성 관리)
- **공통 모듈:** `linux-checks/checks/py_common.py` (유틸리티 및 공통 함수)
- **개별 점검:** `linux-checks/checks/` 디렉토리 내의 `*_check.py` 파일들
- **문서화:** `linux-checks/checks/checks_summary.md` (각 점검 스크립트 기능 요약)

## 2. 개발 및 수정 원칙
- **모듈화:** 모든 점검은 독립적인 Python 파일로 구성하며, `check_runner.py`에 의해 호출됩니다.
- **공통 로직 사용:** 새로운 점검을 만들 때 `py_common.py`에 정의된 함수를 최대한 활용하여 코드 중복을 피합니다.
- **상태 코드:** 점검 스크립트는 `exit code`를 통해 상태를 표현하며, 표준 출력(stdout)으로 요약 정보를 제공해야 합니다.
- **문서 동기화:** 점검 스크립트를 추가하거나 수정할 경우, 반드시 `linux-checks/checks/checks_summary.md` 파일도 함께 업데이트하여 최신 상태를 유지합니다.
- **로그 관리:** 로그는 `check_runner.py` 실행 경로의 `history/<연도>/` 디렉토리에 생성되는 규칙을 따릅니다.

## 3. 대상 환경 (Target Environment)
- **OS:** Ubuntu 20.04.2 LTS
- **DB:** PostgreSQL 12.x
- **Services:** systemd 기반 서비스 (postgresql 등)
- **JVM:** `sudo jps -l`을 통한 프로세스 및 경로 매칭 점검

## 4. 빌드 및 배포
- **PyInstaller:** 리눅스 환경에서 단일 실행 파일로 배포할 때 `build_pyinstaller.sh`를 사용합니다.
- **Spec 파일:** `check_runner.spec` 파일은 기본적으로 유지하되 필요한 경우에만 수정합니다.

## 5. 작업 절차
1.  **분석:** 수정하려는 점검 항목이 `checks.conf` 및 `checks_summary.md`에 어떻게 정의되어 있는지 확인합니다.
2.  **구현:** `py_common.py`를 활용하여 점검 로직을 작성합니다.
3.  **검증:** (가능한 경우) 로직의 유효성을 검토하고 기존 스타일과 일치하는지 확인합니다.
4.  **문서화:** `checks_summary.md`를 업데이트합니다.
