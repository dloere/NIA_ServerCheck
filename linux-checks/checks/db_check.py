from py_common import run_cmd


def db_check(sudo_prefix: list[str]) -> tuple[int, str]:
    lines = ["[DB] PostgreSQL 점검 시작"]
    db_port = "6544"
    service_name = "postgresql"

    rc, out = run_cmd(sudo_prefix + ["netstat", "-tulnp"])
    if rc != 0:
        lines.append(f"[DB] netstat 실행 실패: {out.strip()}")
        return 2, "\n".join(lines)
    if f":{db_port} " in out:
        lines.append(f"[DB] 포트 {db_port} 리스닝 확인: OK")
    else:
        lines.append(f"[DB] 포트 {db_port} 리스닝 확인: FAIL")
        return 2, "\n".join(lines)

    rc, _ = run_cmd(sudo_prefix + ["systemctl", "is-active", "--quiet", service_name])
    if rc == 0:
        lines.append("[DB] systemctl active: OK")
    else:
        lines.append("[DB] systemctl active: FAIL")
        rc2, out2 = run_cmd(sudo_prefix + ["systemctl", "status", service_name, "--no-pager", "-l"])
        if rc2 == 0 and out2.strip():
            lines.append(out2.rstrip())
        return 2, "\n".join(lines)

    rc, _ = run_cmd(sudo_prefix + ["systemctl", "is-enabled", "--quiet", service_name])
    if rc == 0:
        lines.append("[DB] systemctl enabled: OK")
        lines.append("[DB] PostgreSQL 점검 완료")
        return 0, "\n".join(lines)
    else:
        lines.append("[DB] systemctl enabled: WARN (부팅 자동시작 아님)")
        lines.append("[DB] PostgreSQL 점검 완료")
        return 1, "\n".join(lines)
