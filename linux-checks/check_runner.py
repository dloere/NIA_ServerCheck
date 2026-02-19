#!/usr/bin/env python3
import os
import sys
from datetime import datetime


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log(line: str, path: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{now_ts()} {line}\n")


def load_checks_conf(path: str) -> dict:
    conf = {}
    if not os.path.isfile(path):
        return conf
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            conf[k.strip()] = v.strip()
    return conf


def is_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def run_check(name: str, func, all_log: str, fail_log: str) -> int:
    write_log(f"[RUN] {name}", all_log)
    rc, out = func()
    for line in out.splitlines():
        write_log(line, all_log)
    if rc == 0:
        write_log(f"[OK] {name}", all_log)
    elif rc == 1:
        write_log(f"[WARN] {name} (rc={rc})", all_log)
        for line in out.splitlines():
            write_log(line, fail_log)
    else:
        write_log(f"[FAIL] {name} (rc={rc})", all_log)
        for line in out.splitlines():
            write_log(line, fail_log)
    return rc


def main() -> int:
    if getattr(sys, "frozen", False):
        # PyInstaller onefile runs from a temp dir; use current working dir.
        root_dir = os.getcwd()
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__))
    conf_path = os.path.join(root_dir, "checks.conf")

    year_dir = datetime.now().strftime("%Y")
    ts = datetime.now().strftime("%Y%m%d%H%M")
    log_dir = os.path.join(root_dir, "history", year_dir)
    os.makedirs(log_dir, exist_ok=True)
    all_log = os.path.join(log_dir, f"checks_{ts}.log")
    fail_log = os.path.join(log_dir, f"checks_{ts}_fail.log")

    conf = load_checks_conf(conf_path)
    if not conf:
        write_log("[WARN] checks.conf 없음, 기본값 사용", all_log)

    # Allow local package imports from checks/
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    from checks.db_check import db_check
    from checks.cron_check import cron_check
    from checks.ui_engine_check import ui_engine_check
    from checks.resource_check import resource_check
from checks.temperature_check import temperature_check

    sudo_prefix = [] if is_root() else ["sudo"]

    write_log("[START] 일괄 점검 시작", all_log)

    if conf.get("DB_CHECK", "1") == "1":
        run_check("DB 점검", lambda: db_check(sudo_prefix), all_log, fail_log)
    else:
        write_log("[SKIP] DB 점검 비활성", all_log)

    if conf.get("CRON_CHECK", "1") == "1":
        run_check("CRON 점검", cron_check, all_log, fail_log)
    else:
        write_log("[SKIP] CRON 점검 비활성", all_log)

    if conf.get("UI_ENGINE_CHECK", "1") == "1":
        run_check("UI/엔진 모듈 점검", lambda: ui_engine_check(sudo_prefix), all_log, fail_log)
    else:
        write_log("[SKIP] UI/엔진 모듈 점검 비활성", all_log)

    if conf.get("RESOURCE_CHECK", "1") == "1":
        run_check("리소스 점검", resource_check, all_log, fail_log)
    else:
        write_log("[SKIP] 리소스 점검 비활성", all_log)

    if conf.get("TEMP_CHECK", "1") == "1":
        run_check("?? ???", temperature_check, all_log, fail_log)
    else:
        write_log("[SKIP] ?? ??? ?????", all_log)

    write_log("[END] 일괄 점검 종료", all_log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
