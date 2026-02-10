#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m pip install --user pyinstaller
python3 -m PyInstaller --onefile check_runner.py

# PyInstaller 산출물 정리 (spec/build는 필요 없으면 제거)
rm -f "$SCRIPT_DIR/check_runner.spec"
rm -rf "$SCRIPT_DIR/build"

echo "빌드 완료: $SCRIPT_DIR/dist/check_runner"
