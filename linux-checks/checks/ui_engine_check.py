from py_common import run_cmd


def ui_engine_check(sudo_prefix: list[str]) -> tuple[int, str]:
    lines = ["[UI/ENGINE] UI/엔진 모듈 점검 시작"]
    expected = [
        "/home/codej8888/server/lib/com.nia.ai.per.ap-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.data.linkage.ip.equip-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.engine-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.data.linkage-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.data.linkage.ip.alarm-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ping.alarm.preprocessor-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ai.performance.result-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.rca.cluster.preprocessor-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ai.performance.send-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ai.traffic.preprocessor-0.0.1-SNAPSHOT.jar",
        "./app-nia.jar",
        "/home/codej8888/server/lib/com.nia.ip.sdn.data.linkage.ai-1.0-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ip.sdn.linkage-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.alarm.ip.preprocessor-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ems.linkage-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.data.linkage.ai-1.0-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ip.sdn.syslog.preprocessor-1.0-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.data.linkage.ip.perf-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.alarm.preprocessor-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.alarm.simulator-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ip.sdn.syslog.linkage-0.0.1-SNAPSHOT.jar",
        "/home/codej8888/server/lib/com.nia.ip.sdn.sflow.linkage-0.0.1-SNAPSHOT.jar",
    ]

    rc, out = run_cmd(sudo_prefix + ["jps", "-l"])
    if rc != 0 or not out.strip():
        lines.append("[UI/ENGINE] sudo jps -l 출력 없음: FAIL")
        return 2, "\n".join(lines)

    present = set()
    for line in out.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            present.add(parts[1].strip())

    missing = [jar for jar in expected if jar not in present]
    if missing:
        lines.append("[UI/ENGINE] 실행되지 않은 jar 발견: FAIL")
        for jar in missing:
            lines.append(f"[UI/ENGINE] 미실행: {jar}")
        return 2, "\n".join(lines)

    lines.append("[UI/ENGINE] 모든 대상 jar 실행 확인: OK")
    if "./app-nia.jar" in present:
        lines.append("[UI/ENGINE] UI 모듈(app-nia.jar) 정상 실행: OK")
    return 0, "\n".join(lines)
