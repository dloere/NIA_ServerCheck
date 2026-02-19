import subprocess
from typing import List, Tuple


def run_cmd(args: List[str]) -> Tuple[int, str]:
    try:
        p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return p.returncode, p.stdout
    except FileNotFoundError:
        return 127, f"command not found: {args[0]}"
